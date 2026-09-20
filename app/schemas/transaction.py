from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field


class TransferCreate(BaseModel):
    sender_wallet_id: int = Field(gt=0)
    receiver_wallet_id: int = Field(gt=0)
    amount: Decimal = Field(gt=0)

class DepositCreate(BaseModel):
    wallet_id: int = Field(gt=0)
    amount: Decimal = Field(gt=0)


class TransactionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    sender_wallet_id: int | None
    receiver_wallet_id: int | None
    amount: Decimal
    currency: str
    transaction_type: str
    status: str
    created_at: datetime