from app.services.redis import RedisService


class RedisIdempotencyService:
    PREFIX = "ledgerflow:idempotency"

    def __init__(self, redis_service: RedisService) -> None:
        self.redis_service = redis_service

    def _build_key(self, idempotency_key: str) -> str:
        return f"{self.PREFIX}:{idempotency_key}"

    async def acquire(
        self,
        idempotency_key: str,
        ttl_seconds: int = 30,
    ) -> bool:
        key = self._build_key(idempotency_key)

        return await self.redis_service.set_if_not_exists(
            key=key,
            value="processing",
            ttl_seconds=ttl_seconds,
        )

    async def release(self, idempotency_key: str) -> None:
        key = self._build_key(idempotency_key)
        await self.redis_service.delete(key)