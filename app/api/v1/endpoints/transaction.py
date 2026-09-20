from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.schemas.transaction import TransferCreate, TransactionResponse
from app.services.transaction import TransactionService


router = APIRouter(
    prefix="/transactions",
    tags=["Transactions"],
)


@router.post(
    "/transfers",
    response_model=TransactionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_transfer(
    data: TransferCreate,
    db: AsyncSession = Depends(get_db),
) -> TransactionResponse:

    service = TransactionService(db)

    return await service.create_transfer(data)