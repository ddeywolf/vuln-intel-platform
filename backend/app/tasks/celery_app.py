"""Celery application configuration with Beat schedule."""

from celery import Celery
from celery.schedules import crontab

from app.config import get_settings

settings = get_settings()

celery_app = Celery(
    "vuln_intel",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=["app.tasks.ingestion_tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    worker_prefetch_multiplier=1,
    task_acks_late=True,
)

# ── Celery Beat schedule ───────────────────────────────────────────────────────
celery_app.conf.beat_schedule = {
    # NVD: every 2 hours
    "sync-nvd": {
        "task": "app.tasks.ingestion_tasks.sync_nvd",
        "schedule": crontab(minute=0, hour="*/2"),
    },
    # GitHub Advisories: every hour
    "sync-github-advisories": {
        "task": "app.tasks.ingestion_tasks.sync_github_advisories",
        "schedule": crontab(minute=15),
    },
    # OSV: every 4 hours
    "sync-osv": {
        "task": "app.tasks.ingestion_tasks.sync_osv",
        "schedule": crontab(minute=30, hour="*/4"),
    },
    # CISA KEV: daily at 06:00 UTC
    "sync-cisa-kev": {
        "task": "app.tasks.ingestion_tasks.sync_cisa_kev",
        "schedule": crontab(minute=0, hour=6),
    },
    # EPSS: daily at 07:00 UTC
    "sync-epss": {
        "task": "app.tasks.ingestion_tasks.sync_epss",
        "schedule": crontab(minute=0, hour=7),
    },
    # Alert evaluation: every 15 minutes
    "check-alerts": {
        "task": "app.tasks.ingestion_tasks.check_alerts",
        "schedule": crontab(minute="*/15"),
    },
}
