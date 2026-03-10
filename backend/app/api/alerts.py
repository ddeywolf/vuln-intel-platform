"""Alert configuration API endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.alert import AlertCreate, AlertResponse, AlertUpdate
from app.services.alert_service import AlertService
from app.utils.pagination import PaginatedResponse, PaginationParams

router = APIRouter()


@router.get("", response_model=PaginatedResponse[AlertResponse])
async def list_alerts(
    db: Annotated[AsyncSession, Depends(get_db)],
    pagination: Annotated[PaginationParams, Depends()],
):
    """Return a paginated list of alert rules."""
    service = AlertService(db)
    return await service.list(pagination)


@router.post("", response_model=AlertResponse, status_code=status.HTTP_201_CREATED)
async def create_alert(
    payload: AlertCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Create a new alert rule."""
    service = AlertService(db)
    return await service.create(payload)


@router.get("/{alert_id}", response_model=AlertResponse)
async def get_alert(
    alert_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Return an alert rule by ID."""
    service = AlertService(db)
    alert = await service.get(alert_id)
    if alert is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alert not found")
    return alert


@router.patch("/{alert_id}", response_model=AlertResponse)
async def update_alert(
    alert_id: int,
    payload: AlertUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Partially update an alert rule."""
    service = AlertService(db)
    alert = await service.update(alert_id, payload)
    if alert is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alert not found")
    return alert


@router.delete("/{alert_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_alert(
    alert_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Delete an alert rule."""
    service = AlertService(db)
    deleted = await service.delete(alert_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alert not found")
