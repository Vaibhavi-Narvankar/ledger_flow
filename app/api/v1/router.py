from fastapi import APIRouter
from app.api.v1.endpoints import user,health,wallet


api_router = APIRouter()

api_router.include_router(health.router)
api_router.include_router(user.router)
api_router.include_router(wallet.router)