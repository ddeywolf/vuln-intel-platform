"""CISA Known Exploited Vulnerabilities (KEV) catalog ingestion."""

import logging
from datetime import UTC, datetime
from typing import Any

import httpx

from app.schemas.vulnerability import VulnerabilityCreate, VulnerabilityUpdate

logger = logging.getLogger(__name__)

CISA_KEV_URL = "https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json"


def parse(entry: dict[str, Any]) -> VulnerabilityCreate:
    """Normalise a CISA KEV entry into VulnerabilityCreate."""
    cve_id: str = entry.get("cveID", "UNKNOWN")

    def _parse_dt(s: str | None) -> datetime | None:
        if not s:
            return None
        try:
            return datetime.strptime(s, "%Y-%m-%d").replace(tzinfo=UTC)
        except ValueError:
            return None

    return VulnerabilityCreate(
        cve_id=cve_id,
        source="cisa",
        description=entry.get("shortDescription"),
        severity=None,  # CISA KEV doesn't include CVSS severity
        exploit_available=True,
        cisa_kev=True,
        cisa_kev_date_added=_parse_dt(entry.get("dateAdded")),
    )


async def fetch() -> list[dict[str, Any]]:
    """Download and return the CISA KEV JSON catalog."""
    async with httpx.AsyncClient(timeout=60) as client:
        try:
            resp = await client.get(CISA_KEV_URL)
            resp.raise_for_status()
            data = resp.json()
        except httpx.HTTPError as exc:
            logger.error("CISA KEV fetch failed: %s", exc)
            return []

    entries: list[dict[str, Any]] = data.get("vulnerabilities", [])
    logger.info("CISA KEV: fetched %d entries", len(entries))
    return entries


async def sync(db_session) -> int:
    """Fetch CISA KEV data and upsert into the database."""
    from app.services.vulnerability_service import VulnerabilityService

    raw_items = await fetch()
    service = VulnerabilityService(db_session)
    count = 0
    for item in raw_items:
        try:
            payload = parse(item)
            existing = await service.get_by_cve_id(payload.cve_id)
            if existing:
                # Only update KEV-specific fields on existing records
                await service.update(
                    payload.cve_id,
                    VulnerabilityUpdate(
                        exploit_available=True,
                        cisa_kev=True,
                        cisa_kev_date_added=payload.cisa_kev_date_added,
                    ),
                )
            else:
                await service.create(payload)
            count += 1
        except Exception as exc:
            logger.warning("CISA KEV: failed to upsert %s: %s", item.get("cveID"), exc)
    logger.info("CISA KEV: processed %d entries", count)
    return count
