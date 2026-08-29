from fastapi import APIRouter
from app.api.v1.endpoints import user
from app.api.v1.endpoints.health import health
from app.api.v1.endpoints.wallet import router as wallet_router


api_router = APIRouter()

api_router.include_router(health.router)
api_router.include_router(user.router)
router.include_router(wallet_router)