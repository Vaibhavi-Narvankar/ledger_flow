class AppException(Exception):
    """Base exception for application-level errors."""


class UserAlreadyExistsError(AppException):
    """Raised when attempting to create a duplicate user."""

class UserNotFoundError(AppException):
    """Raised when the requested user does not exist."""


class WalletAlreadyExistsError(AppException):
    """Raised when a user already has a wallet for a currency."""


class WalletNotFoundError(AppException):
    """Raised when the requested wallet does not exist."""


class UnsupportedCurrencyError(AppException):
    """Raised when the requested currency is not supported."""

class InsufficientBalanceError(AppException):
    """Raised when a wallet does not have sufficient funds."""


class SameWalletTransferError(AppException):
    """Raised when sender and receiver wallets are the same."""


class CurrencyMismatchError(AppException):
    """Raised when sender and receiver currencies do not match."""

class IdempotencyConflictError(AppException):
    """Raised when an idempotency key is reused for a different request."""

class TransactionNotFoundError(AppException):
    """Raised when a transaction does not exist."""

class InvalidTransactionStatusTransitionError(AppException):
    pass

class RedisUnavailableError(AppException):
    """Raised when Redis is unavailable."""