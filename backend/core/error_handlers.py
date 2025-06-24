"""
Global error handlers for the FastAPI application.
"""

import logging
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from core.config import settings


# Function to get request ID
def get_request_id(request: Request) -> str:
    """Get request ID from request state."""
    return getattr(request.state, "request_id", "unknown")


from core.exceptions import (
    AuthenticationError,
    AuthorizationError,
    ValidationError,
    RateLimitError,
    DatabaseError,
)

logger = logging.getLogger(__name__)


def setup_error_handlers(app: FastAPI) -> None:
    """Setup global error handlers for the application."""

    # Log that error handlers are being configured
    logger.info("Configuring error handlers")

    @app.exception_handler(AuthenticationError)
    async def authentication_error_handler(request: Request, exc: AuthenticationError):
        """Handle authentication errors."""
        request_id = get_request_id(request)
        logger.warning(f"Authentication error (Request ID: {request_id}): {exc.detail}")

        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": "authentication_error",
                "message": exc.detail,
                "request_id": request_id,
                "status_code": exc.status_code,
            },
            headers=exc.headers,
        )

    @app.exception_handler(AuthorizationError)
    async def authorization_error_handler(request: Request, exc: AuthorizationError):
        """Handle authorization errors."""
        request_id = get_request_id(request)
        logger.warning(f"Authorization error (Request ID: {request_id}): {exc.detail}")

        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": "authorization_error",
                "message": exc.detail,
                "request_id": request_id,
                "status_code": exc.status_code,
            },
        )

    @app.exception_handler(RateLimitError)
    async def rate_limit_error_handler(request: Request, exc: RateLimitError):
        """Handle rate limiting errors."""
        request_id = get_request_id(request)
        logger.warning(f"Rate limit exceeded (Request ID: {request_id}): {exc.detail}")

        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": "rate_limit_exceeded",
                "message": exc.detail,
                "request_id": request_id,
                "status_code": exc.status_code,
            },
            headers={"Retry-After": str(settings.HTTP_RETRY_AFTER_DEFAULT)},
        )

    @app.exception_handler(ValidationError)
    async def validation_error_handler(request: Request, exc: ValidationError):
        """Handle validation errors."""
        request_id = get_request_id(request)
        logger.warning(f"Validation error (Request ID: {request_id}): {exc.detail}")

        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": "validation_error",
                "message": exc.detail,
                "request_id": request_id,
                "status_code": exc.status_code,
            },
        )

    @app.exception_handler(DatabaseError)
    async def database_error_handler(request: Request, exc: DatabaseError):
        """Handle database errors."""
        request_id = get_request_id(request)
        logger.error(f"Database error (Request ID: {request_id}): {exc.detail}")

        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": "database_error",
                "message": exc.detail,
                "request_id": request_id,
                "status_code": exc.status_code,
            },
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        """Handle HTTP exceptions."""
        request_id = get_request_id(request)
        logger.warning(
            f"HTTP {exc.status_code} error (Request ID: {request_id}): {exc.detail}"
        )

        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": "http_error",
                "message": exc.detail,
                "request_id": request_id,
                "status_code": exc.status_code,
            },
            headers=getattr(exc, "headers", None),
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ):
        """Handle request validation errors."""
        request_id = get_request_id(request)
        logger.warning(f"Validation error (Request ID: {request_id}): {str(exc)}")

        return JSONResponse(
            status_code=settings.HTTP_UNPROCESSABLE_ENTITY,
            content={
                "error": "validation_error",
                "message": exc.errors(),
                "request_id": request_id,
                "status_code": settings.HTTP_UNPROCESSABLE_ENTITY,
            },
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        """Handle all uncaught exceptions."""
        request_id = get_request_id(request)
        logger.exception(f"Unhandled exception (Request ID: {request_id}): {str(exc)}")

        return JSONResponse(
            status_code=settings.HTTP_INTERNAL_SERVER_ERROR,
            content={
                "error": "internal_server_error",
                "message": "An unexpected error occurred. Please try again later.",
                "request_id": request_id,
                "status_code": settings.HTTP_INTERNAL_SERVER_ERROR,
            },
        )

    logger.info("Error handlers configured successfully")
