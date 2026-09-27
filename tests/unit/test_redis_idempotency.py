from unittest.mock import AsyncMock

import pytest

from app.services.redis_idempotency import RedisIdempotencyService


@pytest.mark.asyncio
async def test_acquire_idempotency_key() -> None:
    redis_service = AsyncMock()
    redis_service.set_if_not_exists.return_value = True

    service = RedisIdempotencyService(redis_service)

    result = await service.acquire(
        "transfer-123",
        ttl_seconds=30,
    )

    assert result is True

    redis_service.set_if_not_exists.assert_awaited_once_with(
        key="ledgerflow:idempotency:transfer-123",
        value="processing",
        ttl_seconds=30,
    )


@pytest.mark.asyncio
async def test_acquire_existing_idempotency_key() -> None:
    redis_service = AsyncMock()
    redis_service.set_if_not_exists.return_value = False

    service = RedisIdempotencyService(redis_service)

    result = await service.acquire("transfer-123")

    assert result is False

    redis_service.set_if_not_exists.assert_awaited_once_with(
        key="ledgerflow:idempotency:transfer-123",
        value="processing",
        ttl_seconds=30,
    )


@pytest.mark.asyncio
async def test_release_idempotency_key() -> None:
    redis_service = AsyncMock()

    service = RedisIdempotencyService(redis_service)

    await service.release("transfer-123")

    redis_service.delete.assert_awaited_once_with(
        "ledgerflow:idempotency:transfer-123",
    )