from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.wallet import Wallet

if TYPE_CHECKING:
    from app.models.ledger import LedgerEntry


class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(primary_key=True)

    sender_wallet_id: Mapped[int | None] = mapped_column(
        ForeignKey("wallets.id"),
        nullable=True,
        index=True,
    )

    receiver_wallet_id: Mapped[int | None] = mapped_column(
        ForeignKey("wallets.id"),
        nullable=True,
        index=True,
    )

    amount: Mapped[Decimal] = mapped_column(
        Numeric(precision=20, scale=8),
        nullable=False,
    )

    currency: Mapped[str] = mapped_column(
        String(3),
        nullable=False,
    )

    transaction_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    sender_wallet: Mapped["Wallet | None"] = relationship(
        foreign_keys=[sender_wallet_id],
        back_populates="sent_transactions",
    )

    receiver_wallet: Mapped["Wallet | None"] = relationship(
        foreign_keys=[receiver_wallet_id],
        back_populates="received_transactions",
    )

    ledger_entries: Mapped[list["LedgerEntry"]] = relationship(
        back_populates="transaction",
    )