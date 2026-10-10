import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
import json
from unittest.mock import AsyncMock, MagicMock
from app.workers.event_consumer_worker import handle_message
from app.models.processed_event import ProcessedEvent
from app.services.event_consumer import EventConsumer


@pytest.mark.asyncio
async def test_process_message_records_new_event(test_engine) -> None:
    session_factory = async_sessionmaker(
        bind=test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    consumer = EventConsumer(session_factory)

    processed = await consumer.process_message(
        message_id="test-message-001",
        event_type="DepositCompleted",
        payload={"transaction_id": 100},
    )

    assert processed is True

    async with session_factory() as db:
        result = await db.execute(
            select(ProcessedEvent).where(
                ProcessedEvent.message_id == "test-message-001"
            )
        )
        event = result.scalar_one()

        assert event.event_type == "DepositCompleted"
        assert event.processed_at is not None



@pytest.mark.asyncio
async def test_rejects_empty_message_id(test_engine) -> None:
    session_factory = async_sessionmaker(
        bind=test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    consumer = EventConsumer(session_factory)

    with pytest.raises(ValueError, match="message_id must not be empty"):
        await consumer.process_message(
            message_id=" ",
            event_type="DepositCompleted",
            payload={"transaction_id": 100},
        )


@pytest.mark.asyncio
async def test_rejects_empty_event_type(test_engine) -> None:
    session_factory = async_sessionmaker(
        bind=test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    consumer = EventConsumer(session_factory)

    with pytest.raises(ValueError, match="event_type must not be empty"):
        await consumer.process_message(
            message_id="test-message-003",
            event_type=" ",
            payload={"transaction_id": 100},
        )

@pytest.mark.asyncio
async def test_duplicate_message_is_not_processed_again(test_engine) -> None:
    session_factory = async_sessionmaker(
        bind=test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    consumer = EventConsumer(session_factory)

    message_id = "test-message-002"

    first_result = await consumer.process_message(
        message_id=message_id,
        event_type="TransferCompleted",
        payload={"transaction_id": 200},
    )

    second_result = await consumer.process_message(
        message_id=message_id,
        event_type="TransferCompleted",
        payload={"transaction_id": 200},
    )

    assert first_result is True
    assert second_result is False

    async with session_factory() as db:
        result = await db.execute(
            select(ProcessedEvent).where(
                ProcessedEvent.message_id == message_id
            )
        )
        events = result.scalars().all()

        assert len(events) == 1


@pytest.mark.asyncio

async def test_database_failure_is_raised() -> None:
    session = MagicMock()
    session.execute = AsyncMock(
        side_effect=RuntimeError("Simulated database failure")
    )
    session.rollback = AsyncMock()
    session_context = MagicMock()
    session_context.__aenter__ = AsyncMock(return_value=session)
    session_context.__aexit__ = AsyncMock(return_value=False)
    session_factory = MagicMock(return_value=session_context)
    consumer = EventConsumer(session_factory)
    with pytest.raises(RuntimeError, match="Simulated database failure"):
        await consumer.process_message(
            message_id="database-failure-test-001",
            event_type="TestEvent",
            payload={"test": True},
        )
    session.rollback.assert_awaited_once()



@pytest.mark.asyncio
async def test_database_failure_at_retry_limit_dead_letters_message() -> None:
    message = MagicMock()

    message.body = json.dumps({"test": True}).encode()
    message.message_id = "retry-limit-test-001"
    message.type = "TestEvent"
    message.headers = {"x-retry-count": 2}

    message.ack = AsyncMock()
    message.nack = AsyncMock()
    message.reject = AsyncMock()

    consumer = MagicMock()
    consumer.process_message = AsyncMock(
        side_effect=RuntimeError("Simulated database failure")
    )

    await handle_message(message, consumer)

    message.reject.assert_awaited_once_with(requeue=False)
    message.ack.assert_not_awaited()
    message.nack.assert_not_awaited()


@pytest.mark.asyncio
async def test_database_failure_schedules_retry() -> None:
    message = MagicMock()

    message.body = json.dumps({"test": True}).encode()
    message.message_id = "database-failure-test-002"
    message.type = "TestEvent"
    message.headers = {}
    message.content_type = "application/json"

    message.ack = AsyncMock()
    message.nack = AsyncMock()
    message.reject = AsyncMock()

    message.channel.default_exchange.publish = AsyncMock()

    consumer = MagicMock()
    consumer.process_message = AsyncMock(
        side_effect=RuntimeError("Simulated database failure")
    )

    await handle_message(message, consumer)

    message.channel.default_exchange.publish.assert_awaited_once()

    publish_call = message.channel.default_exchange.publish.await_args

    retry_message = publish_call.args[0]

    assert publish_call.kwargs["routing_key"] == "ledgerflow.events.retry"
    assert retry_message.headers["x-retry-count"] == 1
    assert retry_message.message_id == "database-failure-test-002"

    message.ack.assert_awaited_once()
    message.nack.assert_not_awaited()
    message.reject.assert_not_awaited()

@pytest.mark.asyncio
async def test_malformed_message_is_rejected_without_retry() -> None:
    message = MagicMock()

    message.body = b"{invalid-json"
    message.message_id = "malformed-message-001"
    message.type = "TestEvent"

    message.ack = AsyncMock()
    message.nack = AsyncMock()
    message.reject = AsyncMock()

    consumer = MagicMock()
    consumer.process_message = AsyncMock()

    await handle_message(message, consumer)

    message.reject.assert_awaited_once_with(requeue=False)
    message.ack.assert_not_awaited()
    message.nack.assert_not_awaited()
    consumer.process_message.assert_not_awaited()

