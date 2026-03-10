"""Business logic for alert rule CRUD operations."""

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.alert import Alert
from app.schemas.alert import AlertCreate, AlertUpdate
from app.utils.pagination import PaginatedResponse, PaginationParams


class AlertService:
    """Service class encapsulating alert rule business logic."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def list(self, pagination: PaginationParams) -> PaginatedResponse[Alert]:
        """Return a paginated list of alert rules."""
        count_result = await self.db.execute(select(func.count()).select_from(Alert))
        total = count_result.scalar_one()

        result = await self.db.execute(
            select(Alert)
            .order_by(Alert.created_at.desc())
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

    async def get(self, alert_id: int) -> Alert | None:
        """Return an alert rule by primary key."""
        result = await self.db.execute(select(Alert).where(Alert.id == alert_id))
        return result.scalar_one_or_none()

    async def create(self, payload: AlertCreate) -> Alert:
        """Create a new alert rule."""
        alert = Alert(**payload.model_dump())
        self.db.add(alert)
        await self.db.flush()
        await self.db.refresh(alert)
        return alert

    async def update(self, alert_id: int, payload: AlertUpdate) -> Alert | None:
        """Partially update an alert rule."""
        alert = await self.get(alert_id)
        if alert is None:
            return None
        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(alert, field, value)
        await self.db.flush()
        await self.db.refresh(alert)
        return alert

    async def delete(self, alert_id: int) -> bool:
        """Delete an alert rule. Returns True if deleted."""
        alert = await self.get(alert_id)
        if alert is None:
            return False
        await self.db.delete(alert)
        return True
