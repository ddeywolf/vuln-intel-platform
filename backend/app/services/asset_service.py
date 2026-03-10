"""Business logic for asset CRUD operations."""

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.asset import Asset
from app.schemas.asset import AssetCreate, AssetUpdate
from app.utils.pagination import PaginatedResponse, PaginationParams


class AssetService:
    """Service class encapsulating asset business logic."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def list(self, pagination: PaginationParams) -> PaginatedResponse[Asset]:
        """Return a paginated list of assets."""
        count_result = await self.db.execute(select(func.count()).select_from(Asset))
        total = count_result.scalar_one()

        result = await self.db.execute(
            select(Asset)
            .order_by(Asset.name)
            .offset(pagination.offset)
            .limit(pagination.page_size)
        )
        items = result.scalars().all()
        return PaginatedResponse(
            items=list(items),
            total=total,
            page=pagination.page,
            page_size=pagination.page_size,
        )

    async def get(self, asset_id: int) -> Asset | None:
        """Return an asset by primary key."""
        result = await self.db.execute(select(Asset).where(Asset.id == asset_id))
        return result.scalar_one_or_none()

    async def create(self, payload: AssetCreate) -> Asset:
        """Create a new asset record."""
        asset = Asset(**payload.model_dump())
        self.db.add(asset)
        await self.db.flush()
        await self.db.refresh(asset)
        return asset

    async def update(self, asset_id: int, payload: AssetUpdate) -> Asset | None:
        """Partially update an asset."""
        asset = await self.get(asset_id)
        if asset is None:
            return None
        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(asset, field, value)
        await self.db.flush()
        await self.db.refresh(asset)
        return asset

    async def delete(self, asset_id: int) -> bool:
        """Delete an asset. Returns True if deleted."""
        asset = await self.get(asset_id)
        if asset is None:
            return False
        await self.db.delete(asset)
        return True
