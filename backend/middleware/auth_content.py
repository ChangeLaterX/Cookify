"""
Enhanced middleware configuration for FastAPI application.
"""
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.sessions import SessionMiddleware
from core.config import settings
from domains.auth.context import AuthContextMiddleware

logger: logging.Logger = logging.getLogger(__name__)


def setup_middleware(app: FastAPI) -> None:
    """
    Configure all middleware for the FastAPI application.
    Middleware is applied in reverse order (last added is executed first).
    """
    
    # 1. Trusted Host Middleware (security layer - first to execute)
    if settings.enable_trusted_host_middleware and settings.trusted_hosts:
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=settings.trusted_hosts
        )
        logger.info(f"Enabled TrustedHostMiddleware with hosts: {settings.trusted_hosts}")
    
    # 2. CORS Middleware (for cross-origin requests)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_safe,
        allow_credentials=settings.cors_allow_credentials,
        allow_methods=settings.cors_allow_methods,
        allow_headers=settings.cors_allow_headers,
    )
    logger.info(f"Enabled CORSMiddleware with origins: {settings.cors_origins_safe}")
    
    # 3. Session Middleware (for OAuth flows and session management)
    app.add_middleware(
        SessionMiddleware,
        secret_key=settings.session_secret_key,
        https_only=settings.session_https_only_safe,
        same_site=settings.session_same_site
    )
    logger.info("Enabled SessionMiddleware with secure settings")
    
    # 4. Auth Context Middleware (authentication context management)
    app.add_middleware(AuthContextMiddleware)
    logger.info("Enabled AuthContextMiddleware")
    
    logger.info("All middleware configured successfully")
