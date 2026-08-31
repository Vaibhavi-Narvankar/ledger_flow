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



@router.get(
    "/user/{user_id}",
    response_model=list[WalletResponse],
)
async def get_user_wallets(
    user_id: int,
    db: AsyncSession = Depends(get_db),
) -> list[WalletResponse]:
    service = WalletService(db)
    return await service.get_user_wallets(user_id)

@router.get(
    "/{wallet_id}",
    response_model=WalletResponse,
)
async def get_wallet(
    wallet_id: int,
    db: AsyncSession = Depends(get_db),
) -> WalletResponse:
    service = WalletService(db)
    return await service.get_wallet(wallet_id)

@router.delete(
    "/{wallet_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_wallet(
    wallet_id: int,
    db: AsyncSession = Depends(get_db),
) -> None:
    service = WalletService(db)
    await service.delete_wallet(wallet_id)