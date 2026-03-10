"""Pydantic schemas for asset request/response validation."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class AssetBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    vendor: str | None = None
    version: str | None = None
    asset_type: str = Field(
        default="application",
        pattern="^(application|os|library|firmware|network|hardware)$",
    )
    cpe: str | None = None
    description: str | None = None
    tags: list[str] | None = None
    extra: dict[str, Any] | None = None


class AssetCreate(AssetBase):
    pass


class AssetUpdate(BaseModel):
    name: str | None = None
    vendor: str | None = None
    version: str | None = None
    asset_type: str | None = None
    cpe: str | None = None
    description: str | None = None
    tags: list[str] | None = None
    extra: dict[str, Any] | None = None


class AssetResponse(AssetBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
