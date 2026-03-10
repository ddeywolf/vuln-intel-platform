"""OSV.dev (Open Source Vulnerabilities) REST API ingestion."""

import logging
from datetime import UTC, datetime
from typing import Any

import httpx

from app.schemas.vulnerability import VulnerabilityCreate

logger = logging.getLogger(__name__)

OSV_API_BASE = "https://api.osv.dev/v1"


def parse(advisory: dict[str, Any]) -> VulnerabilityCreate | None:
    """Normalise an OSV advisory record into VulnerabilityCreate."""
    osv_id: str = advisory.get("id", "UNKNOWN")

    # Extract CVE alias if present
    cve_id = osv_id
    for alias in advisory.get("aliases", []):
        if alias.startswith("CVE-"):
            cve_id = alias
            break

    severity_raw = advisory.get("database_specific", {}).get("severity", "")
    severity_map = {"CRITICAL": "CRITICAL", "HIGH": "HIGH", "MODERATE": "MEDIUM", "LOW": "LOW"}
    severity = severity_map.get(severity_raw.upper())

    # Extract CVSS score from severity block
    cvss_score: float | None = None
    cvss_vector: str | None = None
    for s in advisory.get("severity", []):
        if s.get("type") in ("CVSS_V3", "CVSS_V2"):
            cvss_vector = s.get("score")
            break

    references = [
        {"url": ref.get("url"), "type": ref.get("type")}
        for ref in advisory.get("references", [])
    ]

    affected_products = []
    for aff in advisory.get("affected", []):
        pkg = aff.get("package", {})
        affected_products.append(
            {
                "package": pkg.get("name"),
                "ecosystem": pkg.get("ecosystem"),
                "versions": aff.get("versions", []),
            }
        )

    def _parse_dt(s: str | None) -> datetime | None:
        if not s:
            return None
        try:
            return datetime.fromisoformat(s.rstrip("Z")).replace(tzinfo=UTC)
        except ValueError:
            return None

    summary = advisory.get("summary") or advisory.get("details", "")[:500]

    return VulnerabilityCreate(
        cve_id=cve_id,
        source="osv",
        description=summary,
        severity=severity,
        cvss_score=cvss_score,
        cvss_vector=cvss_vector,
        references=references,
        affected_products=affected_products,
        published_date=_parse_dt(advisory.get("published")),
        modified_date=_parse_dt(advisory.get("modified")),
    )


async def fetch(ecosystem: str | None = None, page_size: int = 1000) -> list[dict[str, Any]]:
    """Fetch vulnerabilities from OSV.dev. Optionally filter by ecosystem."""
    url = f"{OSV_API_BASE}/vulns"
    params: dict[str, Any] = {"page_size": page_size}
    if ecosystem:
        params["ecosystem"] = ecosystem

    all_items: list[dict[str, Any]] = []
    page_token: str | None = None

    async with httpx.AsyncClient(timeout=60) as client:
        for _ in range(20):  # max 20 pages per run
            if page_token:
                params["page_token"] = page_token
            try:
                resp = await client.get(url, params=params)
                resp.raise_for_status()
                data = resp.json()
            except httpx.HTTPError as exc:
                logger.error("OSV fetch failed: %s", exc)
                break

            all_items.extend(data.get("vulns", []))
            page_token = data.get("next_page_token")
            if not page_token:
                break

    logger.info("OSV: fetched %d records", len(all_items))
    return all_items


async def sync(db_session, ecosystem: str | None = None) -> int:
    """Fetch, parse, and upsert OSV vulnerability records."""
    from app.services.vulnerability_service import VulnerabilityService

    raw_items = await fetch(ecosystem=ecosystem)
    service = VulnerabilityService(db_session)
    count = 0
    for item in raw_items:
        try:
            payload = parse(item)
            if payload:
                await service.upsert(payload)
                count += 1
        except Exception as exc:
            logger.warning("OSV: failed to upsert %s: %s", item.get("id"), exc)
    logger.info("OSV: upserted %d records", count)
    return count
