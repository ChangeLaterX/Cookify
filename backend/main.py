"""
Main FastAPI application with enhanced architecture.
"""
from fastapi import FastAPI, Request
import logging
from typing import Any, Dict

# Core imports
from core.config import settings
from core.logging import setup_logging
from middleware.auth_content import setup_middleware
from middleware.request_id import RequestIDMiddleware
from middleware.rate_limit import RateLimitMiddleware

# Validation framework
from shared.utils.validation_env import load_validation_config, get_validation_settings

# Domain routers
from domains.auth.router import router as auth_router

# Setup logging first
setup_logging()
logger: logging.Logger = logging.getLogger("app.main")


def create_application() -> FastAPI:
    """Create and configure the FastAPI application."""
    
    # Create FastAPI app
    application = FastAPI(
        title=settings.app_name,
        debug=settings.debug,
        description="Enhanced Meal Planning API with professional authentication system",
        version=settings.version,
        docs_url=settings.docs_url,
        redoc_url=settings.redoc_url,
        openapi_url="/openapi.json" if settings.docs_url else None,
    )
    
    # Setup error handlers
    from core.error_handlers import setup_error_handlers
    setup_error_handlers(application)
    
    # Add request ID middleware (early in chain)
    application.add_middleware(RequestIDMiddleware)
    
    # Add rate limiting (only in production or if enabled)
    if not settings.debug:
        application.add_middleware(
            RateLimitMiddleware,
            requests_per_minute=100,
            burst_requests=20,
            burst_window_seconds=10
        )
    
    # Setup other middleware
    setup_middleware(application)
    
    # Include routers
    application.include_router(auth_router, prefix="/api")
    
    # Add startup and shutdown events
    application.add_event_handler("startup", on_startup)
    application.add_event_handler("shutdown", on_shutdown)
    
    logger.info(f"FastAPI application created - {settings.app_name} v{settings.version}")
    return application


async def on_startup() -> None:
    """Application startup handler."""
    logger.info("Application startup initiated")
    
    # Initialize validation framework
    load_validation_config()
    
    logger.info(f"Debug mode: {settings.debug}")
    logger.info(f"CORS origins: {settings.cors_origins}")
    logger.info(f"Cache enabled: {settings.enable_user_cache}")
    logger.info("Application startup completed")


async def on_shutdown() -> None:
    """Application shutdown handler."""
    logger.info("Application shutdown initiated")
    # Cleanup tasks here if needed
    logger.info("Application shutdown completed")


# Create the application
app: FastAPI = create_application()


@app.get("/")
async def root() -> dict[str, Any]:
    """Root endpoint for health check."""
    return {
        "message": f"{settings.app_name} is running",
        "status": "healthy",
        "version": settings.version,
        "docs": settings.docs_url,
        "debug": settings.debug
    }


@app.get("/health")
async def health_check(request: Request) -> dict[str, Any]:
    """Enhanced health check endpoint with system information."""

    cache_stats: dict[str, Any] | None = None
    if settings.enable_user_cache:
        try:
            from domains.auth.cache import user_cache
            cache_stats = await user_cache.stats()
        except ImportError:
            cache_stats = {"error": "Cache module not available"}
        except Exception as e:
            cache_stats = {"error": f"Cache unavailable: {str(e)}"}

    return {
        "status": "healthy",
        "app": settings.app_name,
        "version": settings.version,
        "timestamp": "2025-05-27T10:00:00Z",
        "system": {
            "debug": settings.debug,
            "cache_enabled": settings.enable_user_cache,
            "cache_stats": cache_stats,
        },
        "validation": get_validation_settings(),
        "endpoints": {
            "auth": "/api/auth",
            "docs": settings.docs_url,
            "redoc": settings.redoc_url,
        },
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
