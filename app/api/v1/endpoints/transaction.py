from typing import Annotated
from datetime import datetime
from fastapi import APIRouter, Depends, Header, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.transaction import (
    DepositCreate,
    TransactionResponse,
    TransactionHistoryResponse,
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

@router.get(
    "/wallet/{wallet_id}",
    response_model=TransactionHistoryResponse,
    status_code=status.HTTP_200_OK,
)
async def get_wallet_transactions(
    wallet_id: int,
    page: Annotated[
        int,
        Query(ge=1),
    ] = 1,
    page_size: Annotated[
        int,
        Query(ge=1, le=100),
    ] = 20,
    transaction_type: TransactionType | None = None,
    transaction_status: Annotated[
        TransactionStatus | None,
        Query(alias="status"),
    ] = None,
    currency: Annotated[
        str | None,
        Query(min_length=3, max_length=3),
    ] = None,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    db: AsyncSession = Depends(get_db),
) -> TransactionHistoryResponse:

    service = TransactionService(db)

    return await service.get_wallet_transactions(
        wallet_id=wallet_id,
        transaction_type=(
            transaction_type.value
            if transaction_type is not None
            else None
        ),
        status=(
            transaction_status.value
            if transaction_status is not None
            else None
        ),
        currency=(
            currency.upper()
            if currency is not None
            else None
        ),
        start_date=start_date,
        end_date=end_date,
        page=page,
        page_size=page_size,
    )

@router.get(
    "/{transaction_id}",
    response_model=TransactionResponse,
    status_code=status.HTTP_200_OK,
)
async def get_transaction(
    transaction_id: int,
    db: AsyncSession = Depends(get_db),
) -> TransactionResponse:

    service = TransactionService(db)

    return await service.get_transaction(
        transaction_id=transaction_id,
    )

