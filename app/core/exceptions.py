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

class WalletNotFoundError(Exception):
    pass

class InsufficientBalanceError(Exception):
    pass


class SameWalletTransferError(Exception):
    pass

class CurrencyMismatchError(Exception):
    pass