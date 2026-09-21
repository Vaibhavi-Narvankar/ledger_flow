from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.enums import (
    LedgerEntryType,
    TransactionStatus,
    TransactionType,
)
from app.core.exceptions import (
    CurrencyMismatchError,
    IdempotencyConflictError,
    InsufficientBalanceError,
    SameWalletTransferError,
    WalletNotFoundError,
)
from app.models.ledger import LedgerEntry
from app.models.transaction import Transaction
from app.repositories.ledger import LedgerRepository
from app.repositories.transaction import TransactionRepository
from app.repositories.wallet import WalletRepository
from app.schemas.transaction import (
    DepositCreate,
    TransactionResponse,
    TransferCreate,
)


class TransactionService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.wallet_repository = WalletRepository(db)
        self.transaction_repository = TransactionRepository(db)
        self.ledger_repository = LedgerRepository(db)

    def _validate_deposit_idempotency(
        self,
        transaction: Transaction,
        data: DepositCreate,
    ) -> None:
        if (
            transaction.transaction_type != TransactionType.DEPOSIT.value
            or transaction.sender_wallet_id is not None
            or transaction.receiver_wallet_id != data.wallet_id
            or transaction.amount != data.amount
        ):
            raise IdempotencyConflictError(
                "Idempotency key was already used for a different request"
            )

    def _validate_transfer_idempotency(
        self,
        transaction: Transaction,
        data: TransferCreate,
    ) -> None:
        if (
            transaction.transaction_type != TransactionType.TRANSFER.value
            or transaction.sender_wallet_id != data.sender_wallet_id
            or transaction.receiver_wallet_id != data.receiver_wallet_id
            or transaction.amount != data.amount
        ):
            raise IdempotencyConflictError(
                "Idempotency key was already used for a different request"
            )

    async def create_deposit(
        self,
        data: DepositCreate,
        idempotency_key: str,
    ) -> TransactionResponse:

        idempotency_key = idempotency_key.strip()


        existing_transaction = (
            await self.transaction_repository.get_by_idempotency_key(
                idempotency_key
            )
        )

        if existing_transaction is not None:
            self._validate_deposit_idempotency(
                existing_transaction,
                data,
            )

            return TransactionResponse.model_validate(
                existing_transaction
            )


        wallet = await self.wallet_repository.get_by_id_for_update(
            data.wallet_id
        )

        if wallet is None:
            raise WalletNotFoundError(
                f"Wallet {data.wallet_id} not found"
            )


        try:
            transaction = Transaction(
                sender_wallet_id=None,
                receiver_wallet_id=wallet.id,
                amount=data.amount,
                currency=wallet.currency,
                transaction_type=TransactionType.DEPOSIT.value,
                status=TransactionStatus.COMPLETED.value,
                idempotency_key=idempotency_key,
            )

            transaction = await self.transaction_repository.create(
                transaction
            )

            wallet.balance += data.amount

            ledger_entry = LedgerEntry(
                transaction_id=transaction.id,
                wallet_id=wallet.id,
                entry_type=LedgerEntryType.CREDIT.value,
                amount=data.amount,
            )

            await self.ledger_repository.create(
                ledger_entry
            )

            await self.db.commit()

        except IntegrityError as exc:
            await self.db.rollback()

            # Concurrent request with the same idempotency key
            if getattr(exc.orig, "sqlstate", None) == "23505":

                existing_transaction = (
                    await self.transaction_repository.get_by_idempotency_key(
                        idempotency_key
                    )
                )

                if existing_transaction is not None:
                    self._validate_deposit_idempotency(
                        existing_transaction,
                        data,
                    )

                    return TransactionResponse.model_validate(
                        existing_transaction
                    )

            raise

        except Exception:
            await self.db.rollback()
            raise


        return TransactionResponse.model_validate(
            transaction
        )

    async def create_transfer(
        self,
        data: TransferCreate,
        idempotency_key: str,
    ) -> TransactionResponse:

        idempotency_key = idempotency_key.strip()

        existing_transaction = (
            await self.transaction_repository.get_by_idempotency_key(
                idempotency_key
            )
        )

        if existing_transaction is not None:
            self._validate_transfer_idempotency(
                existing_transaction,
                data,
            )

            return TransactionResponse.model_validate(
                existing_transaction
            )

        if data.sender_wallet_id == data.receiver_wallet_id:
            raise SameWalletTransferError(
                "Sender and receiver wallets must be different"
            )

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


        if data.sender_wallet_id == first_wallet.id:
            sender_wallet = first_wallet
            receiver_wallet = second_wallet
        else:
            sender_wallet = second_wallet
            receiver_wallet = first_wallet

        if sender_wallet.currency != receiver_wallet.currency:
            raise CurrencyMismatchError(
                "Sender and receiver wallets must use the same currency"
            )


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
                idempotency_key=idempotency_key,
            )

            transaction = await self.transaction_repository.create(
                transaction
            )

            sender_wallet.balance -= data.amount
            receiver_wallet.balance += data.amount

            debit_entry = LedgerEntry(
                transaction_id=transaction.id,
                wallet_id=sender_wallet.id,
                entry_type=LedgerEntryType.DEBIT.value,
                amount=data.amount,
            )

            credit_entry = LedgerEntry(
                transaction_id=transaction.id,
                wallet_id=receiver_wallet.id,
                entry_type=LedgerEntryType.CREDIT.value,
                amount=data.amount,
            )

            await self.ledger_repository.create(
                debit_entry
            )

            await self.ledger_repository.create(
                credit_entry
            )

            await self.db.commit()

        except IntegrityError as exc:
            await self.db.rollback()

            # Concurrent request with same idempotency key
            if getattr(exc.orig, "sqlstate", None) == "23505":

                existing_transaction = (
                    await self.transaction_repository.get_by_idempotency_key(
                        idempotency_key
                    )
                )

                if existing_transaction is not None:
                    self._validate_transfer_idempotency(
                        existing_transaction,
                        data,
                    )

                    return TransactionResponse.model_validate(
                        existing_transaction
                    )

            raise

        except Exception:
            await self.db.rollback()
            raise

        return TransactionResponse.model_validate(
            transaction
        )