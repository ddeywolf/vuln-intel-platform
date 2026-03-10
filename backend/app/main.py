"""FastAPI application entry point."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.database import engine
from app.elasticsearch_client import close_es, init_es
from app.api.router import api_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application startup and shutdown events."""
    # Startup
    logger.info("Starting Vulnerability Intelligence Platform...")
    try:
        await init_es()
        logger.info("Elasticsearch connected.")
    except Exception as exc:
        logger.warning("Elasticsearch unavailable at startup: %s", exc)

    yield

    # Shutdown
    logger.info("Shutting down...")
    await close_es()
    await engine.dispose()


def create_application() -> FastAPI:
    """Factory function to create and configure the FastAPI application."""
    application = FastAPI(
        title="Vulnerability Intelligence Platform",
        description=(
            "Aggregate, analyze, and act on security vulnerability data "
            "from NVD, GitHub Advisories, OSV, CISA KEV, and EPSS."
        ),
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    # ── CORS ─────────────────────────────────────────────────────────────────
    application.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Routes ────────────────────────────────────────────────────────────────
    application.include_router(api_router, prefix="/api/v1")

    @application.get("/health", tags=["health"])
    async def health_check():
        return {"status": "ok", "version": "1.0.0"}

    return application


app = create_application()
