from typing import Annotated

from fastapi import APIRouter, Depends, Header, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.transaction import (
    DepositCreate,
    TransactionResponse,
    TransferCreate,
)
from app.services.transaction import TransactionService


router = APIRouter(
    prefix="/transactions",
    tags=["Transactions"],
)


@router.post(
    "/deposits",
    response_model=TransactionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_deposit(
    data: DepositCreate,
    idempotency_key: Annotated[
        str,
        Header(
            alias="Idempotency-Key",
            min_length=1,
            max_length=64,
        ),
    ],
    db: AsyncSession = Depends(get_db),
) -> TransactionResponse:
    service = TransactionService(db)

    return await service.create_deposit(
        data=data,
        idempotency_key=idempotency_key,
    )


@router.post(
    "/transfers",
    response_model=TransactionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_transfer(
    data: TransferCreate,
    idempotency_key: Annotated[
        str,
        Header(
            alias="Idempotency-Key",
            min_length=1,
            max_length=64,
        ),
    ],
    db: AsyncSession = Depends(get_db),
) -> TransactionResponse:
    service = TransactionService(db)

    return await service.create_transfer(
        data=data,
        idempotency_key=idempotency_key,
    )