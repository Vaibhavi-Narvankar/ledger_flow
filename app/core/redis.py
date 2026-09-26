from redis.asyncio import Redis

from app.core.config import get_settings


def create_redis_client() -> Redis:
    settings = get_settings()

    return Redis(
        host=settings.redis_host,
        port=settings.redis_port,
        db=settings.redis_db,
        decode_responses=True,
    )


redis_client = create_redis_client()