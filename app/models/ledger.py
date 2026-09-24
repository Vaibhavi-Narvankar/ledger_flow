from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING
from sqlalchemy import CheckConstraint
from sqlalchemy import DateTime, ForeignKey, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.transaction import Transaction
    from app.models.wallet import Wallet


class LedgerEntry(Base):
    __tablename__ = "ledger_entries"

    id: Mapped[int] = mapped_column(primary_key=True)

    transaction_id: Mapped[int] = mapped_column(
        ForeignKey("transactions.id"),
        nullable=False,
        index=True,
    )

    wallet_id: Mapped[int] = mapped_column(
        ForeignKey("wallets.id"),
        nullable=False,
        index=True,
    )

    entry_type: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
    )

    amount: Mapped[Decimal] = mapped_column(
        Numeric(20, 8),
        nullable=False,
    )

    __table_args__ = (
        CheckConstraint(
            "entry_type IN ('DEBIT', 'CREDIT')",
            name="ledger_entry_type_check",
        ),
        CheckConstraint(
            "amount > 0",
            name="ledger_entry_amount_positive",
        ),
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    transaction: Mapped["Transaction"] = relationship(
        back_populates="ledger_entries",
    )

    wallet: Mapped["Wallet"] = relationship(
        back_populates="ledger_entries",
    )