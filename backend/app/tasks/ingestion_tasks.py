"""Celery scheduled ingestion tasks."""

import asyncio
import logging

from app.tasks.celery_app import celery_app

logger = logging.getLogger(__name__)


def _run(coro):
    """Execute an async coroutine in a new event loop (Celery worker context)."""
    return asyncio.get_event_loop().run_until_complete(coro)


async def _get_db_session():
    """Create and return a new async database session for use in tasks."""
    from app.database import AsyncSessionLocal

    return AsyncSessionLocal()


@celery_app.task(name="app.tasks.ingestion_tasks.sync_nvd", bind=True, max_retries=3)
def sync_nvd(self, days_back: int = 1):
    """Ingest recent CVEs from the NVD 2.0 API."""
    from app.ingestion import nvd

    async def _run_sync():
        session = await _get_db_session()
        async with session:
            count = await nvd.sync(session, days_back=days_back)
            await session.commit()
            return count

    try:
        count = _run(_run_sync())
        logger.info("sync_nvd: upserted %d records", count)
        return {"status": "ok", "count": count}
    except Exception as exc:
        logger.error("sync_nvd failed: %s", exc)
        raise self.retry(exc=exc, countdown=300)


@celery_app.task(name="app.tasks.ingestion_tasks.sync_github_advisories", bind=True, max_retries=3)
def sync_github_advisories(self):
    """Ingest advisories from the GitHub Advisory Database."""
    from app.ingestion import github_advisories

    async def _run_sync():
        session = await _get_db_session()
        async with session:
            count = await github_advisories.sync(session)
            await session.commit()
            return count

    try:
        count = _run(_run_sync())
        logger.info("sync_github_advisories: upserted %d records", count)
        return {"status": "ok", "count": count}
    except Exception as exc:
        logger.error("sync_github_advisories failed: %s", exc)
        raise self.retry(exc=exc, countdown=300)


@celery_app.task(name="app.tasks.ingestion_tasks.sync_osv", bind=True, max_retries=3)
def sync_osv(self):
    """Ingest vulnerabilities from OSV.dev."""
    from app.ingestion import osv

    async def _run_sync():
        session = await _get_db_session()
        async with session:
            count = await osv.sync(session)
            await session.commit()
            return count

    try:
        count = _run(_run_sync())
        logger.info("sync_osv: upserted %d records", count)
        return {"status": "ok", "count": count}
    except Exception as exc:
        logger.error("sync_osv failed: %s", exc)
        raise self.retry(exc=exc, countdown=300)


@celery_app.task(name="app.tasks.ingestion_tasks.sync_cisa_kev", bind=True, max_retries=3)
def sync_cisa_kev(self):
    """Ingest the CISA Known Exploited Vulnerabilities catalog."""
    from app.ingestion import cisa_kev

    async def _run_sync():
        session = await _get_db_session()
        async with session:
            count = await cisa_kev.sync(session)
            await session.commit()
            return count

    try:
        count = _run(_run_sync())
        logger.info("sync_cisa_kev: processed %d records", count)
        return {"status": "ok", "count": count}
    except Exception as exc:
        logger.error("sync_cisa_kev failed: %s", exc)
        raise self.retry(exc=exc, countdown=300)


@celery_app.task(name="app.tasks.ingestion_tasks.sync_epss", bind=True, max_retries=3)
def sync_epss(self):
    """Update EPSS scores for all known vulnerabilities."""
    from app.ingestion import epss

    async def _run_sync():
        session = await _get_db_session()
        async with session:
            count = await epss.sync(session)
            await session.commit()
            return count

    try:
        count = _run(_run_sync())
        logger.info("sync_epss: updated %d scores", count)
        return {"status": "ok", "count": count}
    except Exception as exc:
        logger.error("sync_epss failed: %s", exc)
        raise self.retry(exc=exc, countdown=300)


@celery_app.task(name="app.tasks.ingestion_tasks.check_alerts", bind=True)
def check_alerts(self):
    """Evaluate active alert rules against recently ingested data."""
    logger.info("check_alerts: alert evaluation task triggered (placeholder)")
    # TODO: implement alert matching logic against vulnerability data
    return {"status": "ok", "alerts_checked": 0}
