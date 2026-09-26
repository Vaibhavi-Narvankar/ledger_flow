from app.core.enums import (
    TRANSACTION_STATUS_TRANSITIONS,
    TransactionStatus,
)
from app.core.exceptions import (
    InvalidTransactionStatusTransitionError,
)
from app.models.transaction import Transaction


class TransactionStateService:

    @staticmethod
    def transition(
        transaction: Transaction,
        new_status: TransactionStatus,
    ) -> None:
        current_status = TransactionStatus(transaction.status)

        allowed_statuses = TRANSACTION_STATUS_TRANSITIONS.get(
            current_status,
            set(),
        )

        if new_status not in allowed_statuses:
            raise InvalidTransactionStatusTransitionError(
                f"Invalid transaction status transition: "
                f"{current_status.value} -> {new_status.value}"
            )

        transaction.status = new_status.value