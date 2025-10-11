"""Custom exceptions for Backend API."""


class BackendAPIException(Exception):
    """Base exception for Backend API."""

    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class AuthenticationException(BackendAPIException):
    """Authentication failure exception."""

    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, status_code=401)


class AuthorizationException(BackendAPIException):
    """Authorization failure exception."""

    def __init__(self, message: str = "Not authorized to access this resource"):
        super().__init__(message, status_code=403)
