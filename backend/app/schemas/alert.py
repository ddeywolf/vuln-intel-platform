"""Pydantic schemas for alert request/response validation."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class AlertBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    criteria: dict[str, Any] = Field(default_factory=dict)
    severity_threshold: str | None = Field(
        None, pattern="^(CRITICAL|HIGH|MEDIUM|LOW)$"
    )
    notification_channel: str = Field(
        default="email",
        pattern="^(email|slack|webhook|pagerduty)$",
    )
    notification_target: str | None = None
    is_active: bool = True


class AlertCreate(AlertBase):
    pass


class AlertUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    criteria: dict[str, Any] | None = None
    severity_threshold: str | None = None
    notification_channel: str | None = None
    notification_target: str | None = None
    is_active: bool | None = None


class AlertResponse(AlertBase):
    id: int
    last_triggered_at: datetime | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
