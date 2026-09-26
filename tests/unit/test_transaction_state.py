import pytest

from app.core.enums import TransactionStatus
from app.core.exceptions import InvalidTransactionStatusTransitionError
from app.models.transaction import Transaction
from app.services.transaction_state import TransactionStateService


def test_pending_to_completed() -> None:
    transaction = Transaction(
        status=TransactionStatus.PENDING.value,
    )

    TransactionStateService.transition(
        transaction,
        TransactionStatus.COMPLETED,
    )

    assert transaction.status == TransactionStatus.COMPLETED.value


def test_pending_to_failed() -> None:
    transaction = Transaction(
        status=TransactionStatus.PENDING.value,
    )

    TransactionStateService.transition(
        transaction,
        TransactionStatus.FAILED,
    )

    assert transaction.status == TransactionStatus.FAILED.value


@pytest.mark.parametrize(
    "current_status,new_status",
    [
        (TransactionStatus.COMPLETED, TransactionStatus.FAILED),
        (TransactionStatus.COMPLETED, TransactionStatus.PENDING),
        (TransactionStatus.FAILED, TransactionStatus.COMPLETED),
        (TransactionStatus.FAILED, TransactionStatus.PENDING),
    ],
)
def test_invalid_transaction_status_transition(
    current_status: TransactionStatus,
    new_status: TransactionStatus,
) -> None:
    transaction = Transaction(
        status=current_status.value,
    )

    with pytest.raises(InvalidTransactionStatusTransitionError):
        TransactionStateService.transition(
            transaction,
            new_status,
        )