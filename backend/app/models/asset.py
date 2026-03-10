"""SQLAlchemy model for asset/software inventory records."""

from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy import JSON
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.database import Base


class Asset(Base):
    """Represents a software asset in the inventory."""

    __tablename__ = "assets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # ── Identity ──────────────────────────────────────────────────────────
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    vendor: Mapped[str | None] = mapped_column(String(255), nullable=True)
    version: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # ── Classification ────────────────────────────────────────────────────
    asset_type: Mapped[str] = mapped_column(
        String(50), nullable=False, default="application"
    )  # application, os, library, firmware

    # ── CPE / identifiers ────────────────────────────────────────────────
    cpe: Mapped[str | None] = mapped_column(String(500), nullable=True, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # ── Metadata ─────────────────────────────────────────────────────────
    tags: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)
    extra: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)

    # ── Audit ─────────────────────────────────────────────────────────────
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    def __repr__(self) -> str:
        return f"<Asset(name={self.name!r}, type={self.asset_type!r}, version={self.version!r})>"
