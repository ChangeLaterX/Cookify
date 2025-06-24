"""
Custom exceptions for the application.
"""

from fastapi import HTTPException, status
from typing import Any, Dict, Optional


class DatabaseError(HTTPException):
    """Custom exception for database errors."""

    def __init__(
        self, detail: str, status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    ):
        super().__init__(status_code=status_code, detail=detail)


class NotFoundError(HTTPException):
    """Custom exception for not found errors."""

    def __init__(self, resource: str, identifier: str):
        detail = f"{resource} with ID '{identifier}' not found"
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


class ValidationError(HTTPException):
    """Custom exception for validation errors."""

    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=detail
        )


class AuthenticationError(HTTPException):
    """Custom exception for authentication errors."""

    def __init__(self, detail: str = "Authentication required"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )


class AuthorizationError(HTTPException):
    """Custom exception for authorization errors."""

    def __init__(self, detail: str = "Insufficient permissions"):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)


class TokenExpiredError(AuthenticationError):
    """Exception raised when JWT token is expired."""

    def __init__(self, detail: str = "Token has expired"):
        super().__init__(detail=detail)


class InvalidTokenError(AuthenticationError):
    """Exception raised when JWT token is invalid."""

    def __init__(self, detail: str = "Invalid token"):
        super().__init__(detail=detail)


class EmailNotVerifiedError(AuthorizationError):
    """Exception raised when email is not verified."""

    def __init__(self, detail: str = "Email verification required"):
        super().__init__(detail=detail)


class RateLimitError(HTTPException):
    """Exception raised when rate limit is exceeded."""

    def __init__(self, detail: str = "Rate limit exceeded"):
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=detail,
        )


class UserAlreadyExistsError(HTTPException):
    """Exception raised when trying to create a user that already exists."""

    def __init__(self, detail: str = "User already exists"):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail,
        )


class InsufficientPermissionsError(AuthorizationError):
    """Exception raised when user lacks required permissions."""

    def __init__(self, required_permissions: list):
        detail = f"Required permissions: {', '.join(required_permissions)}"
        super().__init__(detail=detail)
