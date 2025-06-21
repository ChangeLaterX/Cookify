"""
Main FastAPI application with enhanced architecture.
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from typing import Any

# Core imports
from core.config import settings
from core.logging import setup_logging
# Middleware imports
from middleware.auth_middleware import AuthContextMiddleware
from middleware.rate_limiting import AuthRateLimitMiddleware
from middleware.ocr_rate_limiting import OCRRateLimitMiddleware
from middleware.security_headers import SecurityHeadersMiddleware

# Validation framework
from shared.utils.validation_env import load_validation_config, get_validation_settings

# Domain routers
from domains.auth.routes import router as auth_router
from domains.ingredients.routes import router as ingredients_router
from domains.ocr.routes import router as receipt_router
from domains.health.routes import router as health_router
from domains.update.routes import router as update_router

# Setup logging first
setup_logging()
from core.logging import get_logger
logger = get_logger("main")

if settings.DEBUG:
    logger.info(f"DEBUG MODE ENABLED: {settings.DEBUG}")

def create_application() -> FastAPI:
    """Create and configure the FastAPI application."""
    
    # Create FastAPI app
    application = FastAPI(
        title=settings.APP_NAME,
        debug=settings.DEBUG,
        description="",
        version=settings.VERSION,
        docs_url=settings.DOCS_URL,
        redoc_url=settings.REDOC_URL,
        openapi_url="/openapi.json" if settings.DOCS_URL else None,
    )
    
    # Setup error handlers
    from core.error_handlers import setup_error_handlers
    setup_error_handlers(application)
    
    # Add CORS middleware (should be early in the stack)
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
        allow_methods=settings.CORS_ALLOW_METHODS,
        allow_headers=settings.CORS_ALLOW_HEADERS,
    )
    
    # Add security headers middleware (should be first for all responses)
    if settings.SECURITY_HEADERS_ENABLED:
        application.add_middleware(SecurityHeadersMiddleware)
    
    # Add OCR rate limiting middleware (resource-intensive operations)
    application.add_middleware(OCRRateLimitMiddleware)
    
    # Add auth context middleware
    application.add_middleware(AuthContextMiddleware)
    
    # Add rate limiting for authentication endpoints
    application.add_middleware(AuthRateLimitMiddleware)
    
    # Include routers
    application.include_router(auth_router, prefix="/api")
    application.include_router(ingredients_router, prefix="/api")
    application.include_router(receipt_router, prefix="/api")
    application.include_router(health_router, prefix="/api")
    application.include_router(update_router, prefix="/api")
    
    # Add startup and shutdown events
    application.add_event_handler("startup", on_startup)
    application.add_event_handler("shutdown", on_shutdown)
    
    logger.info(f"FastAPI application created - {settings.APP_NAME} v{settings.VERSION}")
    return application


async def on_startup() -> None:
    """Application startup handler."""
    logger.info("Application startup initiated")
    
    # Initialize validation framework
    load_validation_config()
    
    # Run startup scripts (ingredient cache, etc.)
    try:
        from domains.update.ingredient_cache import initialize_ingredient_cache
        cache_success = await initialize_ingredient_cache()
        if cache_success:
            logger.info("✅ Ingredient cache initialized successfully")
        else:
            logger.warning("⚠️ Ingredient cache initialization failed - check logs for details")
    except Exception as e:
        logger.error(f"❌ Error initializing ingredient cache: {str(e)}")
    
    logger.info(f"Debug mode: {settings.DEBUG}")
    logger.info(f"CORS origins: {settings.CORS_ORIGINS}")
    logger.info(f"Cache enabled: {settings.ENABLE_USER_CACHE}")
    logger.info(f"Security headers enabled: {settings.SECURITY_HEADERS_ENABLED}")
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
    """Root endpoint for basic application info."""
    return {
        "message": f"{settings.APP_NAME} is running",
        "status": "healthy",
        "version": settings.VERSION,
        "docs": settings.DOCS_URL,
        "debug": settings.DEBUG,
        "health_check": "/api/health",
        "quick_health": "/api/health/quick"
    }


if __name__ == "__main__":
    import uvicorn
    from core.config import settings

    uvicorn.run(
        app, 
        host=settings.SERVER_HOST, 
        port=settings.SERVER_PORT,
        log_level=settings.LOG_LEVEL.lower(),
        access_log=settings.ENABLE_ACCESS_LOG
    )
