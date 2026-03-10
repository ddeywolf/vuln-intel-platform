"""SQLAlchemy model for alert/notification rule records."""

from datetime import datetime
from typing import Any

from sqlalchemy import Boolean, DateTime, Integer, String, Text
from sqlalchemy import JSON
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.database import Base


class Alert(Base):
    """Represents a configurable alert rule."""

    __tablename__ = "alerts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # ── Identity ──────────────────────────────────────────────────────────
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # ── Criteria ─────────────────────────────────────────────────────────
    # JSON object describing filter conditions, e.g.:
    # {"severity": ["CRITICAL", "HIGH"], "keywords": ["apache"], "sources": ["nvd"]}
    criteria: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    severity_threshold: Mapped[str | None] = mapped_column(
        String(20), nullable=True
    )  # minimum severity: CRITICAL, HIGH, MEDIUM, LOW

    # ── Notification ──────────────────────────────────────────────────────
    notification_channel: Mapped[str] = mapped_column(
        String(50), nullable=False, default="email"
    )  # email, slack, webhook, pagerduty
    notification_target: Mapped[str | None] = mapped_column(
        String(500), nullable=True
    )  # email address, webhook URL, etc.

    # ── State ─────────────────────────────────────────────────────────────
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)
    last_triggered_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # ── Audit ─────────────────────────────────────────────────────────────
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    def __repr__(self) -> str:
        return f"<Alert(name={self.name!r}, active={self.is_active!r})>"
