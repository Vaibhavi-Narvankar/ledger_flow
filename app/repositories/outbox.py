from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.outbox_event import OutboxEvent


class OutboxRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(
        self,
        *,
        event_type: str,
        aggregate_type: str,
        aggregate_id: int,
        payload: dict[str, Any],
    ) -> OutboxEvent:
        event = OutboxEvent(
            event_type=event_type,
            aggregate_type=aggregate_type,
            aggregate_id=aggregate_id,
            payload=payload,
        )

        self.db.add(event)
        await self.db.flush()

        return event

    async def get_pending(
        self,
        *,
        limit: int = 100,
    ) -> list[OutboxEvent]:
        result = await self.db.execute(
            select(OutboxEvent)
            .where(OutboxEvent.status == "PENDING")
            .order_by(OutboxEvent.created_at, OutboxEvent.id)
            .limit(limit)
            .with_for_update(skip_locked=True)
        )

        return list(result.scalars().all())

    async def mark_published(
        self,
        event: OutboxEvent,
    ) -> None:
        event.status = "PUBLISHED"
        event.published_at = datetime.now(timezone.utc)

        await self.db.flush()