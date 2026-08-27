class AppException(Exception):
    """Base exception for application-level errors."""


class UserAlreadyExistsError(AppException):
    """Raised when attempting to create a duplicate user."""