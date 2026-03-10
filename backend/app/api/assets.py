"""Asset management API endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.asset import AssetCreate, AssetResponse, AssetUpdate
from app.services.asset_service import AssetService
from app.utils.pagination import PaginatedResponse, PaginationParams

router = APIRouter()


@router.get("", response_model=PaginatedResponse[AssetResponse])
async def list_assets(
    db: Annotated[AsyncSession, Depends(get_db)],
    pagination: Annotated[PaginationParams, Depends()],
):
    """Return a paginated list of assets."""
    service = AssetService(db)
    return await service.list(pagination)


@router.post("", response_model=AssetResponse, status_code=status.HTTP_201_CREATED)
async def create_asset(
    payload: AssetCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Create a new asset record."""
    service = AssetService(db)
    return await service.create(payload)


@router.get("/{asset_id}", response_model=AssetResponse)
async def get_asset(
    asset_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Return an asset by ID."""
    service = AssetService(db)
    asset = await service.get(asset_id)
    if asset is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Asset not found")
    return asset


@router.patch("/{asset_id}", response_model=AssetResponse)
async def update_asset(
    asset_id: int,
    payload: AssetUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Partially update an asset."""
    service = AssetService(db)
    asset = await service.update(asset_id, payload)
    if asset is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Asset not found")
    return asset


@router.delete("/{asset_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_asset(
    asset_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Delete an asset."""
    service = AssetService(db)
    deleted = await service.delete(asset_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Asset not found")
