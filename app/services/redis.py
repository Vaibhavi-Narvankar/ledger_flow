from redis.exceptions import RedisError
from redis.asyncio import Redis
from app.core.exceptions import RedisUnavailableError


class RedisService:
    def __init__(self, client: Redis) -> None:
        self.client = client

    async def set_if_not_exists(
        self,
        key: str,
        value: str,
        ttl_seconds: int,
    ) -> bool:
        try:
            result = await self.client.set(
                key,
                value,
                ex=ttl_seconds,
                nx=True,
            )
        except RedisError as exc:
            raise RedisUnavailableError(
                "Redis is currently unavailable"
            ) from exc

        return result is True

    async def delete(self, key: str) -> None:
        try:
            await self.client.delete(key)
        except RedisError as exc:
            raise RedisUnavailableError(
                "Redis is currently unavailable"
            ) from exc