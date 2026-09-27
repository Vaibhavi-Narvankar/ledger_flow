from unittest.mock import AsyncMock

import pytest

from app.services.redis import RedisService


@pytest.mark.asyncio
async def test_set_if_not_exists_success() -> None:
    redis_client = AsyncMock()
    redis_client.set.return_value = True

    service = RedisService(redis_client)

    result = await service.set_if_not_exists(
        key="test:key",
        value="1",
        ttl_seconds=30,
    )

    assert result is True

    redis_client.set.assert_awaited_once_with(
        "test:key",
        "1",
        ex=30,
        nx=True,
    )


@pytest.mark.asyncio
async def test_set_if_not_exists_when_key_exists() -> None:
    redis_client = AsyncMock()
    redis_client.set.return_value = None

    service = RedisService(redis_client)

    result = await service.set_if_not_exists(
        key="test:key",
        value="1",
        ttl_seconds=30,
    )

    assert result is False

    redis_client.set.assert_awaited_once_with(
        "test:key",
        "1",
        ex=30,
        nx=True,
    )


@pytest.mark.asyncio
async def test_delete() -> None:
    redis_client = AsyncMock()

    service = RedisService(redis_client)

    await service.delete("test:key")

    redis_client.delete.assert_awaited_once_with("test:key")