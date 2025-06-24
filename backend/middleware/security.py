"""
Security Dependencies for FastAPI.
Provides authentication dependencies for protected routes.
"""

import logging
from typing import Optional
from uuid import UUID

from core.config import settings
from domains.auth.schemas import AuthUser
from domains.auth.services import AuthenticationError
from domains.auth.services import get_current_user as get_user_from_token
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

logger = logging.getLogger(__name__)

# Security scheme for bearer token
security = HTTPBearer()
optional_security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> AuthUser:
    """
    FastAPI dependency to get current authenticated user.

    Validates JWT token and returns user data.

    Args:
        credentials: Bearer token from Authorization header

    Returns:
        AuthUser with user and profile data

    Raises:
        HTTPException: 401 if token is invalid or user not found
    """
    try:
        token = credentials.credentials
        logger.debug(f"Validating token for authentication")

        # Get user from token via service
        user = await get_user_from_token(token)

        if not user.is_active:
            logger.warning(f"Inactive user attempted access: {user.id}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "error": "Account is inactive",
                    "error_code": "ACCOUNT_INACTIVE",
                },
                headers={"WWW-Authenticate": "Bearer"},
            )

        logger.debug(f"User authenticated successfully: {user.id}")
        return user

    except AuthenticationError as e:
        logger.warning(f"Authentication failed: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": e.message, "error_code": e.error_code},
            headers={"WWW-Authenticate": "Bearer"},
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in authentication: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Authentication service error",
                "error_code": "SERVICE_ERROR",
            },
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(optional_security),
) -> Optional[AuthUser]:
    """
    FastAPI dependency to optionally get current authenticated user.

    Returns user data if valid token is provided, None otherwise.
    Useful for endpoints that can show different content for authenticated users.

    Args:
        credentials: Optional bearer token from Authorization header

    Returns:
        AuthUser if authenticated, None otherwise
    """
    if credentials is None:
        logger.debug("No authentication credentials provided")
        return None

    try:
        token = credentials.credentials
        logger.debug(f"Validating optional token")

        # Get user from token via service
        user = await get_user_from_token(token)

        if not user.is_active:
            logger.debug(f"Inactive user in optional auth: {user.id}")
            return None

        logger.debug(f"Optional user authenticated: {user.id}")
        return user

    except AuthenticationError as e:
        logger.debug(f"Optional authentication failed: {e.message}")
        return None
    except Exception as e:
        logger.warning(f"Error in optional authentication: {str(e)}")
        return None


async def require_verified_user(
    current_user: AuthUser = Depends(get_current_user),
) -> AuthUser:
    """
    FastAPI dependency that requires a verified user.

    Args:
        current_user: Current authenticated user

    Returns:
        AuthUser if verified

    Raises:
        HTTPException: 403 if user is not verified
    """
    if not current_user.is_verified:
        logger.warning(f"Unverified user attempted access: {current_user.id}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error": "Email verification required",
                "error_code": "EMAIL_NOT_VERIFIED",
            },
        )

    return current_user


async def admin_required(
    current_user: AuthUser = Depends(get_current_user),
) -> AuthUser:
    """
    FastAPI dependency that requires admin privileges.

    Args:
        current_user: Current authenticated user

    Returns:
        AuthUser if admin

    Raises:
        HTTPException: 403 if user is not admin
    """
    if not current_user.is_super_admin:
        logger.warning(f"Non-admin user attempted admin access: {current_user.id}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error": "Admin privileges required",
                "error_code": "INSUFFICIENT_PRIVILEGES",
            },
        )

    return current_user


async def get_user_id(current_user: AuthUser = Depends(get_current_user)) -> UUID:
    """
    FastAPI dependency to get just the current user ID.

    Useful when you only need the user ID for database queries.

    Args:
        current_user: Current authenticated user

    Returns:
        UUID of current user
    """
    return current_user.id


async def get_optional_user_id(
    current_user: Optional[AuthUser] = Depends(get_optional_user),
) -> Optional[UUID]:
    """
    FastAPI dependency to optionally get current user ID.

    Args:
        current_user: Optional current authenticated user

    Returns:
        UUID of current user if authenticated, None otherwise
    """
    return current_user.id if current_user else None


# Security utility functions
def extract_token_from_header(authorization: str) -> str:
    """
    Extract JWT token from Authorization header.

    Args:
        authorization: Authorization header value

    Returns:
        JWT token string

    Raises:
        ValueError: If header format is invalid
    """
    if not authorization.startswith("Bearer "):
        raise ValueError("Invalid authorization header format")

    return authorization[
        settings.MIDDLEWARE_BEARER_PREFIX_LENGTH :
    ]  # Remove "Bearer " prefix


def validate_token_format(token: str) -> bool:
    """
    Basic validation of JWT token format.

    Args:
        token: JWT token string

    Returns:
        True if format looks valid, False otherwise
    """
    if not token:
        return False

    # JWT tokens should have 3 parts separated by dots
    parts = token.split(".")
    return len(parts) == settings.MIDDLEWARE_JWT_PARTS_COUNT and all(
        part for part in parts
    )


# Export dependencies and utilities
__all__ = [
    "get_current_user",
    "get_optional_user",
    "require_verified_user",
    "admin_required",
    "get_user_id",
    "get_optional_user_id",
    "extract_token_from_header",
    "validate_token_format",
    "security",
    "optional_security",
]
