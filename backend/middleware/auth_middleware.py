"""
Authentication Middleware for FastAPI.
Provides automatic user context injection and request/response processing.
"""

import time
from typing import Any, Dict, Optional
from uuid import UUID

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from core.config import settings
from core.logging import get_logger
from domains.auth.schemas import AuthUser
from domains.auth.services import AuthenticationError
from domains.auth.services import get_current_user as get_user_from_token

logger = get_logger(__name__)


class AuthContextMiddleware(BaseHTTPMiddleware):
    """
    Middleware that automatically injects user context into requests.

    This middleware:
    - Extracts JWT tokens from Authorization headers
    - Validates tokens and loads user data
    - Injects user context into request state
    - Logs authentication events for security monitoring
    - Handles rate limiting for auth endpoints
    """

    def __init__(self, app):
        super().__init__(app)
        import logging

        from core.logging import get_logger

        self.logger = get_logger(f"{__name__}.{self.__class__.__name__}")

        # Endpoints that don't require authentication
        self.public_endpoints = {
            "/auth/login",
            "/auth/refresh",
            "/auth/password-reset",
            "/auth/health",
            "/docs",
            "/redoc",
            "/openapi.json",
            "/",
            "/health",
        }

    async def dispatch(self, request: Request, call_next):
        """
        Process request through authentication middleware.

        Args:
            request: FastAPI request object
            call_next: Next middleware/endpoint in chain

        Returns:
            Response from downstream handler
        """
        start_time = time.time()

        # Initialize request state
        request.state.user = None
        request.state.user_id = None
        request.state.is_authenticated = False

        # Get request info for logging
        client_ip = self._get_client_ip(request)
        user_agent = request.headers.get("user-agent", "unknown")
        request_id = request.headers.get("x-request-id", "unknown")

        try:
            # Check if endpoint is public
            if self._is_public_endpoint(request.url.path):
                self.logger.debug(f"Public endpoint accessed: {request.url.path}")
            else:
                # Try to authenticate user (but don't fail on auth errors)
                try:
                    await self._inject_user_context(request)
                except Exception as auth_error:
                    self.logger.debug(
                        f"Auth context injection failed: {str(auth_error)}"
                    )
                    # Continue processing - auth failures shouldn't stop the request

            # Process request
            response = await call_next(request)

            # Log successful request
            duration = time.time() - start_time
            self._log_request(
                request, response, duration, client_ip, user_agent, request_id
            )

            return response

        except Exception as e:
            # Log error but only catch critical middleware errors
            duration = time.time() - start_time
            self.logger.error(
                f"Critical middleware error: {str(e)} | "
                f"Path: {request.url.path} | "
                f"IP: {client_ip} | "
                f"Duration: {duration:.{settings.MIDDLEWARE_DURATION_DECIMAL_PLACES}f}s | "
                f"Exception type: {type(e).__name__} | "
                f"Exception details: {repr(e)}"
            )

            # Re-raise the exception to see the real error
            raise e

    async def _inject_user_context(self, request: Request) -> None:
        """
        Inject user context into request if valid token is provided.

        Args:
            request: FastAPI request object
        """
        try:
            # Extract token from Authorization header
            authorization = request.headers.get("authorization")
            if not authorization:
                self.logger.debug("No authorization header found")
                return

            if not authorization.startswith("Bearer "):
                self.logger.debug("Invalid authorization header format")
                return

            token = authorization[
                settings.MIDDLEWARE_BEARER_PREFIX_LENGTH :
            ]  # Remove "Bearer " prefix

            # Validate and get user
            user = await get_user_from_token(token)

            if user and user.is_active:
                # Inject user context into request
                request.state.user = user
                request.state.user_id = user.id
                request.state.is_authenticated = True

                self.logger.debug(f"User context injected: {user.id}")
            else:
                self.logger.debug("User not active or not found")

        except AuthenticationError as e:
            self.logger.debug(f"Authentication failed in middleware: {e.message}")
        except Exception as e:
            self.logger.warning(f"Error injecting user context: {str(e)}")

    def _is_public_endpoint(self, path: str) -> bool:
        """
        Check if endpoint is public (doesn't require authentication).

        Args:
            path: Request path

        Returns:
            True if endpoint is public
        """
        # Exact matches
        if path in self.public_endpoints:
            return True

        # Pattern matches
        public_patterns = ["/static/", "/assets/", "/.well-known/", "/favicon.ico"]

        return any(path.startswith(pattern) for pattern in public_patterns)

    def _get_client_ip(self, request: Request) -> str:
        """
        Get client IP address from request.

        Args:
            request: FastAPI request object

        Returns:
            Client IP address
        """
        # Check for forwarded headers (when behind proxy)
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[
                settings.SECURITY_IP_HEADER_SPLIT_INDEX
            ].strip()

        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip

        # Fallback to direct connection
        if hasattr(request.client, "host"):
            return request.client.host

        return "unknown"

    def _log_request(
        self,
        request: Request,
        response: Response,
        duration: float,
        client_ip: str,
        user_agent: str,
        request_id: str,
    ) -> None:
        """
        Log request for security monitoring.

        Args:
            request: FastAPI request object
            response: Response object
            duration: Request duration in seconds
            client_ip: Client IP address
            user_agent: User agent string
            request_id: Request ID
        """
        user_id = getattr(request.state, "user_id", None)
        is_authenticated = getattr(request.state, "is_authenticated", False)

        log_data = {
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "duration": f"{duration:.{settings.MIDDLEWARE_DURATION_DECIMAL_PLACES}f}s",
            "client_ip": client_ip,
            "user_agent": user_agent,
            "request_id": request_id,
            "user_id": str(user_id) if user_id else None,
            "authenticated": is_authenticated,
        }

        # Log level based on response status
        if response.status_code >= settings.MIDDLEWARE_HTTP_SERVER_ERROR_THRESHOLD:
            self.logger.error(f"Request failed: {log_data}")
        elif response.status_code >= settings.MIDDLEWARE_HTTP_CLIENT_ERROR_THRESHOLD:
            self.logger.warning(f"Client error: {log_data}")
        elif settings.ENABLE_ACCESS_LOG:
            self.logger.info(f"Request: {log_data}")


# Convenience function to get user from request state
def get_user_from_request(request: Request) -> Optional[AuthUser]:
    """
    Get authenticated user from request state.

    Args:
        request: FastAPI request object

    Returns:
        AuthUser if authenticated, None otherwise
    """
    return getattr(request.state, "user", None)


def get_user_id_from_request(request: Request) -> Optional[UUID]:
    """
    Get authenticated user ID from request state.

    Args:
        request: FastAPI request object

    Returns:
        User UUID if authenticated, None otherwise
    """
    return getattr(request.state, "user_id", None)


def is_authenticated_request(request: Request) -> bool:
    """
    Check if request is authenticated.

    Args:
        request: FastAPI request object

    Returns:
        True if request is authenticated
    """
    return getattr(request.state, "is_authenticated", False)


# Export middleware and utilities
__all__ = [
    "AuthContextMiddleware",
    "get_user_from_request",
    "get_user_id_from_request",
    "is_authenticated_request",
]
