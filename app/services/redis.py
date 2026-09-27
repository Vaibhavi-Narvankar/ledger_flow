from redis.asyncio import Redis

from app.core.redis import redis_client


class RedisService:
    def __init__(self, client: Redis) -> None:
        self.client = client

    async def set_if_not_exists(
        self,
        key: str,
        value: str,
        ttl_seconds: int,
    ) -> bool:
        result = await self.client.set(
            key,
            value,
            ex=ttl_seconds,
            nx=True,
        )
        return result is True

    async def delete(self, key: str) -> None:
        await self.client.delete(key)

redis_service = RedisService(redis_client)