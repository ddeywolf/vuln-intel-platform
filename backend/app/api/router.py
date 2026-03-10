"""Main API router aggregating all sub-routers."""

from fastapi import APIRouter

from app.api import vulnerabilities, assets, alerts, dashboard, auth

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(
    vulnerabilities.router, prefix="/vulnerabilities", tags=["Vulnerabilities"]
)
api_router.include_router(assets.router, prefix="/assets", tags=["Assets"])
api_router.include_router(alerts.router, prefix="/alerts", tags=["Alerts"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])
