"""Dashboard stats and analytics API endpoints."""

from typing import Any, Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.vulnerability import Vulnerability
from app.models.asset import Asset
from app.models.alert import Alert

router = APIRouter()


@router.get("/stats", response_model=dict[str, Any])
async def get_dashboard_stats(
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Return aggregate statistics for the dashboard."""
    # Total vulnerability count
    total_vulns_result = await db.execute(select(func.count()).select_from(Vulnerability))
    total_vulns = total_vulns_result.scalar_one()

    # Counts by severity
    severity_result = await db.execute(
        select(Vulnerability.severity, func.count().label("count"))
        .group_by(Vulnerability.severity)
    )
    severity_counts: dict[str, int] = {
        row.severity or "UNKNOWN": row.count for row in severity_result.all()
    }

    # Critical and high shortcuts
    critical_count = severity_counts.get("CRITICAL", 0)
    high_count = severity_counts.get("HIGH", 0)

    # CISA KEV count
    kev_result = await db.execute(
        select(func.count()).select_from(Vulnerability).where(Vulnerability.cisa_kev.is_(True))
    )
    kev_count = kev_result.scalar_one()

    # Exploit available count
    exploit_result = await db.execute(
        select(func.count())
        .select_from(Vulnerability)
        .where(Vulnerability.exploit_available.is_(True))
    )
    exploit_count = exploit_result.scalar_one()

    # Total assets
    asset_result = await db.execute(select(func.count()).select_from(Asset))
    asset_count = asset_result.scalar_one()

    # Active alerts
    alert_result = await db.execute(
        select(func.count()).select_from(Alert).where(Alert.is_active.is_(True))
    )
    active_alerts = alert_result.scalar_one()

    # Counts by source
    source_result = await db.execute(
        select(Vulnerability.source, func.count().label("count")).group_by(Vulnerability.source)
    )
    source_counts: dict[str, int] = {row.source: row.count for row in source_result.all()}

    # Recent 5 vulnerabilities
    recent_result = await db.execute(
        select(Vulnerability)
        .order_by(Vulnerability.published_date.desc().nullslast())
        .limit(5)
    )
    recent_vulns = recent_result.scalars().all()

    return {
        "total_vulnerabilities": total_vulns,
        "critical_count": critical_count,
        "high_count": high_count,
        "cisa_kev_count": kev_count,
        "exploit_available_count": exploit_count,
        "assets_monitored": asset_count,
        "active_alerts": active_alerts,
        "severity_distribution": severity_counts,
        "source_distribution": source_counts,
        "recent_vulnerabilities": [
            {
                "id": v.id,
                "cve_id": v.cve_id,
                "description": (v.description or "")[:200],
                "severity": v.severity,
                "cvss_score": v.cvss_score,
                "published_date": v.published_date,
                "cisa_kev": v.cisa_kev,
            }
            for v in recent_vulns
        ],
    }
