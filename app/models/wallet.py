from datetime import datetime
from decimal import Decimal
from sqlalchemy import DateTime, ForeignKey, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base
from typing import TYPE_CHECKING
from sqlalchemy import CheckConstraint
from sqlalchemy import UniqueConstraint

if TYPE_CHECKING:
    from app.models.user import User

if TYPE_CHECKING:
    from app.models.transaction import Transaction

if TYPE_CHECKING:
    from app.models.ledger import LedgerEntry


class Wallet(Base):
    __tablename__ = "wallets"

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    currency: Mapped[str] = mapped_column(
        String(3),
        nullable=False,
    )


    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "currency",
            name="uq_wallets_user_id_currency",
        ),
        CheckConstraint(
            "char_length(currency) = 3",
            name="currency_length",
        ),
    )

    sent_transactions: Mapped[list["Transaction"]] = relationship(
        foreign_keys="Transaction.sender_wallet_id",
        back_populates="sender_wallet",
    )

    received_transactions: Mapped[list["Transaction"]] = relationship(
        foreign_keys="Transaction.receiver_wallet_id",
        back_populates="receiver_wallet",
    )

    balance: Mapped[Decimal] = mapped_column(
        Numeric(precision=20, scale=8),
        nullable=False,
        default=Decimal("0"),
        server_default="0",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    user: Mapped["User"] = relationship(
        back_populates="wallets",
    )

    ledger_entries: Mapped[list["LedgerEntry"]] = relationship(
        back_populates="wallet",
    )