"""
Authentication context management using contextvars.
"""
import logging
from contextvars import ContextVar
from typing import Optional
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from domains.auth.schemas import User

logger: logging.Logger = logging.getLogger(__name__)

# Context variable to store current user
current_user_context: ContextVar[Optional[User]] = ContextVar('current_user', default=None)
current_request_context: ContextVar[Optional[Request]] = ContextVar('current_request', default=None)


class AuthContextMiddleware(BaseHTTPMiddleware):
    """Middleware to manage authentication context for each request."""
    
    async def dispatch(self, request: Request, call_next) -> Response:
        """Process request and set up auth context."""
        # Reset context for each request
        current_user_context.set(None)
        current_request_context.set(request)
        
        try:
            response: Response = await call_next(request)
            return response
        finally:
            # Clean up context after request
            current_user_context.set(None)
            current_request_context.set(None)


def get_current_user_from_context() -> Optional[User]:
    """Get current user from context."""
    return current_user_context.get()


def set_current_user_in_context(user: Optional[User]) -> None:
    """Set current user in context."""
    current_user_context.set(user)
    if user:
        logger.debug(f"Set user {user.email} in context")
    else:
        logger.debug("Cleared user from context")


def get_current_request_from_context() -> Optional[Request]:
    """Get current request from context."""
    return current_request_context.get()


def has_user_in_context() -> bool:
    """Check if there's a user in the current context."""
    return current_user_context.get() is not None
