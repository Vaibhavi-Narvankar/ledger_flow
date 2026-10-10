import json
from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.models.outbox_event import OutboxEvent
from app.services.outbox_publisher import OutboxPublisher


@pytest.mark.asyncio
async def test_publish_pending_event(test_engine) -> None:
    session_factory = async_sessionmaker(
        bind=test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    # Isolate this test from events created by other tests.
    async with session_factory() as db:
        await db.execute(delete(OutboxEvent))
        await db.commit()

        event = OutboxEvent(
            event_type="TestEvent",
            aggregate_type="transaction",
            aggregate_id=999,
            payload={
                "event_type": "TestEvent",
                "transaction_id": 999,
            },
        )
        db.add(event)
        await db.commit()
        event_id = event.id

    channel = MagicMock()
    channel.default_exchange.publish = AsyncMock()

    rabbitmq = MagicMock()
    rabbitmq.channel = channel

    publisher = OutboxPublisher(
        rabbitmq,
        session_factory=session_factory,
    )

    published_count = await publisher.publish_pending()

    assert published_count == 1
    channel.default_exchange.publish.assert_awaited_once()

    message = channel.default_exchange.publish.await_args.args[0]
    assert json.loads(message.body) == {
        "event_type": "TestEvent",
        "transaction_id": 999,
    }

    async with session_factory() as db:
        result = await db.execute(
            select(OutboxEvent).where(OutboxEvent.id == event_id)
        )
        stored_event = result.scalar_one()

        assert stored_event.status == "PUBLISHED"
        assert stored_event.published_at is not None


@pytest.mark.asyncio
async def test_publish_failure_keeps_event_pending(test_engine) -> None:
    session_factory = async_sessionmaker(
        bind=test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    # Isolate this test from events created by other tests.
    async with session_factory() as db:
        await db.execute(delete(OutboxEvent))
        await db.commit()

        event = OutboxEvent(
            event_type="TestFailureEvent",
            aggregate_type="transaction",
            aggregate_id=1000,
            payload={
                "event_type": "TestFailureEvent",
                "transaction_id": 1000,
            },
        )
        db.add(event)
        await db.commit()
        event_id = event.id

    channel = MagicMock()
    channel.default_exchange.publish = AsyncMock(
        side_effect=RuntimeError("Simulated RabbitMQ failure")
    )

    rabbitmq = MagicMock()
    rabbitmq.channel = channel

    publisher = OutboxPublisher(
        rabbitmq,
        session_factory=session_factory,
    )

    with pytest.raises(RuntimeError, match="Simulated RabbitMQ failure"):
        await publisher.publish_pending()

    async with session_factory() as db:
        result = await db.execute(
            select(OutboxEvent).where(OutboxEvent.id == event_id)
        )
        stored_event = result.scalar_one()

        assert stored_event.status == "PENDING"
        assert stored_event.published_at is None