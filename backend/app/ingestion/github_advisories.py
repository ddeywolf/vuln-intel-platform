"""GitHub Advisory Database ingestion via the GraphQL API."""

import logging
from datetime import UTC, datetime
from typing import Any

import httpx

from app.config import get_settings
from app.schemas.vulnerability import VulnerabilityCreate

logger = logging.getLogger(__name__)
settings = get_settings()

GITHUB_GRAPHQL_URL = "https://api.github.com/graphql"

ADVISORIES_QUERY = """
query($cursor: String) {
  securityAdvisories(first: 100, after: $cursor, orderBy: {field: UPDATED_AT, direction: DESC}) {
    pageInfo {
      hasNextPage
      endCursor
    }
    nodes {
      ghsaId
      summary
      description
      severity
      cvss {
        score
        vectorString
      }
      publishedAt
      updatedAt
      references {
        url
      }
      vulnerabilities(first: 10) {
        nodes {
          package {
            name
            ecosystem
          }
          vulnerableVersionRange
        }
      }
      identifiers {
        type
        value
      }
    }
  }
}
"""


def parse(advisory: dict[str, Any]) -> VulnerabilityCreate | None:
    """Normalise a GitHub advisory node into VulnerabilityCreate."""
    ghsa_id: str = advisory.get("ghsaId", "")

    # Prefer CVE identifier if available
    cve_id = ghsa_id
    for ident in advisory.get("identifiers", []):
        if ident.get("type") == "CVE":
            cve_id = ident["value"]
            break

    severity_raw = advisory.get("severity", "UNKNOWN")
    severity_map = {
        "CRITICAL": "CRITICAL",
        "HIGH": "HIGH",
        "MODERATE": "MEDIUM",
        "LOW": "LOW",
    }
    severity = severity_map.get(severity_raw.upper())

    cvss = advisory.get("cvss") or {}
    cvss_score: float | None = cvss.get("score")
    cvss_vector: str | None = cvss.get("vectorString")

    references = [{"url": ref["url"]} for ref in advisory.get("references", []) if ref.get("url")]

    affected_products = [
        {
            "package": v["package"]["name"],
            "ecosystem": v["package"]["ecosystem"],
            "vulnerable_range": v.get("vulnerableVersionRange"),
        }
        for v in advisory.get("vulnerabilities", {}).get("nodes", [])
    ]

    def _parse_dt(s: str | None) -> datetime | None:
        if not s:
            return None
        try:
            return datetime.fromisoformat(s.rstrip("Z")).replace(tzinfo=UTC)
        except ValueError:
            return None

    return VulnerabilityCreate(
        cve_id=cve_id,
        source="github",
        description=advisory.get("summary") or advisory.get("description"),
        severity=severity,
        cvss_score=cvss_score,
        cvss_vector=cvss_vector,
        references=references,
        affected_products=affected_products,
        published_date=_parse_dt(advisory.get("publishedAt")),
        modified_date=_parse_dt(advisory.get("updatedAt")),
    )


async def fetch(max_pages: int = 5) -> list[dict[str, Any]]:
    """Fetch security advisories from GitHub GraphQL API."""
    if not settings.github_token:
        logger.warning("GITHUB_TOKEN not set — skipping GitHub Advisory ingestion")
        return []

    headers = {
        "Authorization": f"bearer {settings.github_token}",
        "Content-Type": "application/json",
    }

    all_advisories: list[dict[str, Any]] = []
    cursor: str | None = None
    pages = 0

    async with httpx.AsyncClient(timeout=60) as client:
        while pages < max_pages:
            variables: dict[str, Any] = {"cursor": cursor}
            try:
                resp = await client.post(
                    GITHUB_GRAPHQL_URL,
                    json={"query": ADVISORIES_QUERY, "variables": variables},
                    headers=headers,
                )
                resp.raise_for_status()
                data = resp.json()
            except httpx.HTTPError as exc:
                logger.error("GitHub Advisory fetch failed: %s", exc)
                break

            page_data = data.get("data", {}).get("securityAdvisories", {})
            nodes = page_data.get("nodes", [])
            all_advisories.extend(nodes)

            page_info = page_data.get("pageInfo", {})
            if not page_info.get("hasNextPage"):
                break
            cursor = page_info.get("endCursor")
            pages += 1

    logger.info("GitHub: fetched %d advisories", len(all_advisories))
    return all_advisories


async def sync(db_session, max_pages: int = 5) -> int:
    """Fetch, parse, and upsert GitHub Advisory records."""
    from app.services.vulnerability_service import VulnerabilityService

    raw_items = await fetch(max_pages=max_pages)
    service = VulnerabilityService(db_session)
    count = 0
    for item in raw_items:
        try:
            payload = parse(item)
            if payload:
                await service.upsert(payload)
                count += 1
        except Exception as exc:
            logger.warning("GitHub: failed to upsert %s: %s", item.get("ghsaId"), exc)
    logger.info("GitHub: upserted %d records", count)
    return count
