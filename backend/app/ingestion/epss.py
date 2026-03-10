"""EPSS (Exploit Prediction Scoring System) score ingestion."""

import csv
import io
import logging
from typing import Any

import httpx

from app.schemas.vulnerability import VulnerabilityUpdate

logger = logging.getLogger(__name__)

# FIRST.org provides daily EPSS CSV files
EPSS_CSV_URL = "https://epss.cyentia.com/epss_scores-current.csv.gz"
EPSS_FALLBACK_URL = "https://api.first.org/data/v1/epss"


async def fetch() -> list[dict[str, Any]]:
    """Download and parse the current EPSS scores CSV."""
    import gzip

    async with httpx.AsyncClient(timeout=120) as client:
        try:
            resp = await client.get(EPSS_CSV_URL)
            resp.raise_for_status()
            raw = gzip.decompress(resp.content).decode("utf-8")
        except Exception as exc:
            logger.warning("EPSS gzip CSV fetch failed (%s), trying REST fallback", exc)
            return await _fetch_rest()

    scores: list[dict[str, Any]] = []
    reader = csv.DictReader(io.StringIO(raw))
    for row in reader:
        cve_id = row.get("cve")
        epss = row.get("epss")
        percentile = row.get("percentile")
        if cve_id and epss:
            try:
                scores.append(
                    {
                        "cve_id": cve_id,
                        "epss_score": float(epss),
                        "epss_percentile": float(percentile) if percentile else None,
                    }
                )
            except ValueError:
                pass

    logger.info("EPSS: parsed %d scores from CSV", len(scores))
    return scores


async def _fetch_rest(limit: int = 10000) -> list[dict[str, Any]]:
    """Fallback: fetch EPSS scores via the FIRST.org REST API."""
    url = EPSS_FALLBACK_URL
    params: dict[str, Any] = {"limit": limit, "offset": 0}
    all_data: list[dict[str, Any]] = []
    async with httpx.AsyncClient(timeout=60) as client:
        while True:
            try:
                resp = await client.get(url, params=params)
                resp.raise_for_status()
                data = resp.json()
            except httpx.HTTPError as exc:
                logger.error("EPSS REST fallback failed: %s", exc)
                break
            items = data.get("data", [])
            all_data.extend(items)
            total = data.get("total", 0)
            params["offset"] += limit
            if params["offset"] >= total:
                break
    return [
        {
            "cve_id": item.get("cve"),
            "epss_score": float(item.get("epss", 0)),
            "epss_percentile": float(item.get("percentile", 0)),
        }
        for item in all_data
        if item.get("cve")
    ]


async def sync(db_session) -> int:
    """Update EPSS scores for all known vulnerabilities."""
    from app.services.vulnerability_service import VulnerabilityService

    scores = await fetch()
    service = VulnerabilityService(db_session)
    count = 0
    for entry in scores:
        cve_id = entry.get("cve_id")
        if not cve_id:
            continue
        existing = await service.get_by_cve_id(cve_id)
        if existing:
            await service.update(
                cve_id,
                VulnerabilityUpdate(
                    epss_score=entry.get("epss_score"),
                    epss_percentile=entry.get("epss_percentile"),
                ),
            )
            count += 1
    logger.info("EPSS: updated %d vulnerability scores", count)
    return count
