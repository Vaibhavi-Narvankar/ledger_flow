from enum import StrEnum


class TransactionType(StrEnum):
    TRANSFER = "TRANSFER"
    DEPOSIT = "DEPOSIT"
    WITHDRAWAL = "WITHDRAWAL"


class TransactionStatus(StrEnum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class LedgerEntryType(StrEnum):
    DEBIT = "DEBIT"
    CREDIT = "CREDIT"

TRANSACTION_STATUS_TRANSITIONS: dict[
    TransactionStatus,
    set[TransactionStatus],
] = {
    TransactionStatus.PENDING: {
        TransactionStatus.COMPLETED,
        TransactionStatus.FAILED,
    },
    TransactionStatus.COMPLETED: set(),
    TransactionStatus.FAILED: set(),
}