from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.enums import TransactionStatus, TransactionType
from app.core.exceptions import (
    InsufficientBalanceError,
    SameWalletTransferError,
    WalletNotFoundError,
    CurrencyMismatchError,
)
from app.models.ledger import LedgerEntry
from app.models.transaction import Transaction
from app.repositories.ledger import LedgerRepository
from app.repositories.transaction import TransactionRepository
from app.repositories.wallet import WalletRepository
from app.schemas.transaction import TransferCreate, TransactionResponse


class TransactionService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.wallet_repository = WalletRepository(db)
        self.transaction_repository = TransactionRepository(db)
        self.ledger_repository = LedgerRepository(db)

    async def create_transfer(
        self,
        data: TransferCreate,
    ) -> TransactionResponse:

        if data.sender_wallet_id == data.receiver_wallet_id:
            raise SameWalletTransferError(
                "Sender and receiver wallets must be different"
            )

        # Always lock wallets in deterministic order.
        first_wallet_id = min(
            data.sender_wallet_id,
            data.receiver_wallet_id,
        )
        second_wallet_id = max(
            data.sender_wallet_id,
            data.receiver_wallet_id,
        )

        first_wallet = await self.wallet_repository.get_by_id_for_update(
            first_wallet_id
        )

        if first_wallet is None:
            raise WalletNotFoundError(
                f"Wallet {first_wallet_id} not found"
            )

        second_wallet = await self.wallet_repository.get_by_id_for_update(
            second_wallet_id
        )

        if second_wallet is None:
            raise WalletNotFoundError(
                f"Wallet {second_wallet_id} not found"
            )

        # Map the locked wallets back to their actual roles.
        if data.sender_wallet_id == first_wallet.id:
            sender_wallet = first_wallet
            receiver_wallet = second_wallet
        else:
            sender_wallet = second_wallet
            receiver_wallet = first_wallet

        # Currency must match.
        if sender_wallet.currency != receiver_wallet.currency:
            raise CurrencyMismatchError(
                "Sender and receiver wallets must use the same currency"
            )

        # Balance check happens while sender wallet is locked.
        if sender_wallet.balance < data.amount:
            raise InsufficientBalanceError(
                "Insufficient wallet balance"
            )

        try:
            transaction = Transaction(
                sender_wallet_id=sender_wallet.id,
                receiver_wallet_id=receiver_wallet.id,
                amount=data.amount,
                currency=sender_wallet.currency,
                transaction_type=TransactionType.TRANSFER.value,
                status=TransactionStatus.COMPLETED.value,
            )

            transaction = await self.transaction_repository.create(
                transaction
            )

            # Update balances.
            sender_wallet.balance -= data.amount
            receiver_wallet.balance += data.amount

            # Ledger debit.
            debit_entry = LedgerEntry(
                transaction_id=transaction.id,
                wallet_id=sender_wallet.id,
                entry_type="DEBIT",
                amount=data.amount,
            )

            # Ledger credit.
            credit_entry = LedgerEntry(
                transaction_id=transaction.id,
                wallet_id=receiver_wallet.id,
                entry_type="CREDIT",
                amount=data.amount,
            )

            await self.ledger_repository.create(debit_entry)
            await self.ledger_repository.create(credit_entry)

            await self.db.commit()

        except Exception:
            await self.db.rollback()
            raise

        return TransactionResponse.model_validate(transaction)