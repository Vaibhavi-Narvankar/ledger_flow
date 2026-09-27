from fastapi import Request
from app.services.redis import RedisService


def get_redis_service(request: Request) -> RedisService:
    return RedisService(request.app.state.redis)