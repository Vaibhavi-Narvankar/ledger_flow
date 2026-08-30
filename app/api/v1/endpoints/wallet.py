from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.wallet import (WalletCreate,WalletResponse)
from app.core.database import get_db
from app.services.wallet import WalletService

router = APIRouter(prefix="/wallets", tags=["Wallets"])

@router.post(
    "",
    response_model=WalletResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_wallet(
   data:WalletCreate,
   db: AsyncSession = Depends(get_db),
) -> WalletResponse:
     service = WalletService(db)
     return await service.create_wallet(data)