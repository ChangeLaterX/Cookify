"""
Global error handlers for the FastAPI application.
"""
import logging
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from middleware.request_id import get_request_id

from core.exceptions import (
    AuthenticationError,
    AuthorizationError,
    ValidationError,
    RateLimitError,
    DatabaseError
)

logger = logging.getLogger(__name__)


def setup_error_handlers(app: FastAPI) -> None:
    """Setup global error handlers for the application."""
    
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
                "status_code": exc.status_code
            },
            headers=exc.headers
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
                "status_code": exc.status_code
            }
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
                "status_code": exc.status_code
            },
            headers={"Retry-After": "60"}
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
                "status_code": exc.status_code
            }
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
                "message": "A database error occurred. Please try again later.",
                "request_id": request_id,
                "status_code": exc.status_code
            }
        )
    
    @app.exception_handler(RequestValidationError)
    async def request_validation_error_handler(request: Request, exc: RequestValidationError):
        """Handle FastAPI request validation errors."""
        request_id = get_request_id(request)
        logger.warning(f"Request validation error (Request ID: {request_id}): {exc.errors()}")
        
        return JSONResponse(
            status_code=422,
            content={
                "error": "request_validation_error",
                "message": "Request validation failed",
                "details": exc.errors(),
                "request_id": request_id,
                "status_code": 422
            }
        )
    
    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        """Handle general HTTP exceptions."""
        request_id = get_request_id(request)
        
        if exc.status_code >= 500:
            logger.error(f"HTTP {exc.status_code} error (Request ID: {request_id}): {exc.detail}")
        else:
            logger.warning(f"HTTP {exc.status_code} error (Request ID: {request_id}): {exc.detail}")
        
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": "http_error",
                "message": exc.detail,
                "request_id": request_id,
                "status_code": exc.status_code
            }
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """Handle unexpected exceptions."""
        request_id = get_request_id(request)
        logger.exception(f"Unhandled exception (Request ID: {request_id}): {str(exc)}")
        
        return JSONResponse(
            status_code=500,
            content={
                "error": "internal_server_error",
                "message": "An unexpected error occurred. Please try again later.",
                "request_id": request_id,
                "status_code": 500
            }
        )
    
    logger.info("Error handlers configured successfully")
