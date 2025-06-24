"""
Simple Security Headers Middleware for testing.
"""

import logging

from core.config import settings
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class SimpleSecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Simple middleware to test security headers."""

    def __init__(self, app):
        super().__init__(app)
        logger.info("Simple Security Headers Middleware initialized")

    async def dispatch(self, request: Request, call_next) -> Response:
        """Add basic security headers."""
        response = await call_next(request)

        # Add only the basic required headers from Issue 2
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = settings.MIDDLEWARE_XSS_PROTECTION_MODE
        response.headers["Content-Security-Policy"] = "default-src 'self'"

        return response
