from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class LedgerEntryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    transaction_id: int
    wallet_id: int
    entry_type: str
    amount: Decimal
    created_at: datetime