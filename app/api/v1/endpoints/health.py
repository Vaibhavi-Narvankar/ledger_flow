from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from fastapi import APIRouter, Depends, Request


router = APIRouter()


@router.get("/health")
async def health_check():
    return {"status": "healthy"}


@router.get("/health/db")
async def database_health_check(
    db: AsyncSession = Depends(get_db),
):
    await db.execute(text("SELECT 1"))

    return {
        "status": "healthy",
        "database": "connected",
    }

@router.get("/redis")
async def redis_health(request: Request):
    await request.app.state.redis.ping()

    return {
        "status": "ok",
        "redis": "connected",
    }