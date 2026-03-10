"""NVD (NIST) CVE feed ingestion via the NVD 2.0 REST API."""

import logging
from datetime import UTC, datetime, timedelta
from typing import Any

import httpx

from app.config import get_settings
from app.schemas.vulnerability import VulnerabilityCreate

logger = logging.getLogger(__name__)
settings = get_settings()

NVD_API_BASE = "https://services.nvd.nist.gov/rest/json/cves/2.0"
PAGE_SIZE = 2000


def _map_severity(metrics: dict[str, Any]) -> tuple[str | None, float | None, str | None]:
    """Extract severity label, CVSS score, and vector from the metrics block."""
    # Prefer CVSSv3.1 > CVSSv3.0 > CVSSv2
    for key in ("cvssMetricV31", "cvssMetricV30"):
        entries = metrics.get(key, [])
        if entries:
            cvss = entries[0].get("cvssData", {})
            return (
                cvss.get("baseSeverity"),
                cvss.get("baseScore"),
                cvss.get("vectorString"),
            )
    entries = metrics.get("cvssMetricV2", [])
    if entries:
        cvss = entries[0].get("cvssData", {})
        score = cvss.get("baseScore")
        severity = entries[0].get("baseSeverity")
        return severity, score, cvss.get("vectorString")
    return None, None, None


def parse(raw: dict[str, Any]) -> VulnerabilityCreate:
    """Normalise a single NVD CVE item into a VulnerabilityCreate schema."""
    vuln = raw.get("cve", {})
    cve_id: str = vuln.get("id", "UNKNOWN")

    descriptions = vuln.get("descriptions", [])
    description = next(
        (d["value"] for d in descriptions if d.get("lang") == "en"), None
    )

    metrics = vuln.get("metrics", {})
    severity, cvss_score, cvss_vector = _map_severity(metrics)

    references = [
        {"url": ref.get("url"), "source": ref.get("source")}
        for ref in vuln.get("references", [])
    ]

    configurations = vuln.get("configurations", [])
    affected_products = []
    for config in configurations:
        for node in config.get("nodes", []):
            for match in node.get("cpeMatch", []):
                affected_products.append(match.get("criteria"))

    published_str = vuln.get("published")
    modified_str = vuln.get("lastModified")

    def _parse_dt(s: str | None) -> datetime | None:
        if not s:
            return None
        try:
            return datetime.fromisoformat(s.rstrip("Z")).replace(tzinfo=UTC)
        except ValueError:
            return None

    return VulnerabilityCreate(
        cve_id=cve_id,
        source="nvd",
        description=description,
        severity=severity,
        cvss_score=cvss_score,
        cvss_vector=cvss_vector,
        references=references,
        affected_products=affected_products,
        published_date=_parse_dt(published_str),
        modified_date=_parse_dt(modified_str),
    )


async def fetch(days_back: int = 1) -> list[dict[str, Any]]:
    """Fetch recent CVEs from the NVD 2.0 API."""
    now = datetime.now(UTC)
    start = now - timedelta(days=days_back)
    params: dict[str, Any] = {
        "pubStartDate": start.strftime("%Y-%m-%dT%H:%M:%S.000"),
        "pubEndDate": now.strftime("%Y-%m-%dT%H:%M:%S.000"),
        "resultsPerPage": PAGE_SIZE,
        "startIndex": 0,
    }
    headers = {}
    if settings.nvd_api_key:
        headers["apiKey"] = settings.nvd_api_key

    all_items: list[dict[str, Any]] = []
    async with httpx.AsyncClient(timeout=60) as client:
        while True:
            try:
                resp = await client.get(NVD_API_BASE, params=params, headers=headers)
                resp.raise_for_status()
                data = resp.json()
            except httpx.HTTPError as exc:
                logger.error("NVD fetch failed: %s", exc)
                break

            vulnerabilities = data.get("vulnerabilities", [])
            all_items.extend(vulnerabilities)
            total = data.get("totalResults", 0)
            start_index = params["startIndex"] + PAGE_SIZE
            if start_index >= total:
                break
            params["startIndex"] = start_index
            logger.debug("NVD: fetched %d/%d", len(all_items), total)

    logger.info("NVD: fetched %d CVE records", len(all_items))
    return all_items


async def sync(db_session, days_back: int = 1) -> int:
    """Fetch, parse, and upsert NVD CVE records. Returns count of upserted records."""
    from app.services.vulnerability_service import VulnerabilityService

    raw_items = await fetch(days_back=days_back)
    service = VulnerabilityService(db_session)
    count = 0
    for item in raw_items:
        try:
            payload = parse(item)
            await service.upsert(payload)
            count += 1
        except Exception as exc:
            logger.warning("NVD: failed to upsert %s: %s", item.get("cve", {}).get("id"), exc)
    logger.info("NVD: upserted %d records", count)
    return count
