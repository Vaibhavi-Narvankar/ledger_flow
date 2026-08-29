from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field


class WalletCreate(BaseModel):
    user_id: int = Field(gt=0)
    currency: str = Field(min_length=3, max_length=3)


class WalletResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    currency: str
    balance: Decimal
    created_at: datetime
    updated_at: datetime