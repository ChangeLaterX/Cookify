"""
Security Headers Middleware for FastAPI.
Implements comprehensive security headers to protect against common web vulnerabilities.
"""
import logging
from typing import Dict, Optional, List
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from core.config import settings

logger = logging.getLogger(__name__)


class SecurityHeadersConfig:
    """Configuration class for security headers."""
    
    def __init__(self):
        # Basic security headers - always applied
        self.x_content_type_options = "nosniff"
        self.x_frame_options = "DENY"
        self.x_xss_protection = "1; mode=block"
        self.referrer_policy = "strict-origin-when-cross-origin"
        
        # HSTS - only in production or when explicitly enabled
        self.hsts_max_age = 31536000  # 1 year
        self.hsts_include_subdomains = True
        self.hsts_preload = False  # Can be enabled per environment
        
        # Content Security Policy - configurable per environment
        self.csp_directives = self._get_csp_directives()
        
        # Additional security headers
        self.permissions_policy = self._get_permissions_policy()
        
    def _get_csp_directives(self) -> Dict[str, str]:
        """Get Content Security Policy directives based on environment."""
        if settings.is_development:
            # More permissive CSP for development, including Swagger UI CDN resources
            return {
                "default-src": "'self'",
                "script-src": "'self' 'unsafe-inline' 'unsafe-eval' localhost:* 127.0.0.1:* https://unpkg.com https://cdn.jsdelivr.net",
                "style-src": "'self' 'unsafe-inline' fonts.googleapis.com https://unpkg.com https://cdn.jsdelivr.net",
                "font-src": "'self' fonts.gstatic.com https://unpkg.com https://cdn.jsdelivr.net",
                "img-src": "'self' data: blob: https:",
                "connect-src": "'self' localhost:* 127.0.0.1:* ws: wss:",
                "frame-ancestors": "'none'",
                "base-uri": "'self'",
                "form-action": "'self'"
            }
        else:
            # Strict CSP for production
            return {
                "default-src": "'self'",
                "script-src": "'self'",
                "style-src": "'self' 'unsafe-inline'",  # Allow inline styles for better UX
                "font-src": "'self'",
                "img-src": "'self' data: blob:",
                "connect-src": "'self'",
                "frame-ancestors": "'none'",
                "base-uri": "'self'",
                "form-action": "'self'",
                "upgrade-insecure-requests": ""
            }
    
    def _get_permissions_policy(self) -> str:
        """Get Permissions Policy header value."""
        # Disable potentially dangerous features
        policies = [
            "camera=()",
            "microphone=()",
            "geolocation=()",
            "payment=()",
            "usb=()",
            "magnetometer=()",
            "gyroscope=()",
            "accelerometer=()",
            "ambient-light-sensor=()",
            "autoplay=()",
            "encrypted-media=()",
            "fullscreen=(self)",
            "picture-in-picture=()"
        ]
        return ", ".join(policies)
    
    def get_hsts_header(self) -> Optional[str]:
        """Get HSTS header value if applicable."""
        if not settings.is_production:
            # Don't set HSTS in development to avoid browser issues
            return None
            
        hsts_value = f"max-age={self.hsts_max_age}"
        if self.hsts_include_subdomains:
            hsts_value += "; includeSubDomains"
        if self.hsts_preload:
            hsts_value += "; preload"
        return hsts_value
    
    def get_csp_header(self) -> str:
        """Get Content Security Policy header value."""
        directives = []
        for directive, value in self.csp_directives.items():
            if value:
                directives.append(f"{directive} {value}")
            else:
                directives.append(directive)
        return "; ".join(directives)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add comprehensive security headers to all responses.
    
    Implements protection against:
    - XSS attacks
    - Clickjacking
    - MIME type sniffing
    - Man-in-the-middle attacks (HSTS)
    - Various other web vulnerabilities
    """
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.config = SecurityHeadersConfig()
        self._log_config()
    
    def _log_config(self) -> None:
        """Log the security headers configuration."""
        logger.info("Security Headers Middleware initialized")
        logger.info(f"Environment: {'development' if settings.is_development else 'production'}")
        logger.info(f"HSTS enabled: {self.config.get_hsts_header() is not None}")
        logger.debug(f"CSP directives: {len(self.config.csp_directives)} configured")
    
    async def dispatch(self, request: Request, call_next) -> Response:
        """Process request and add security headers to response."""
        try:
            # Process the request
            response = await call_next(request)
            
            # Add security headers
            self._add_security_headers(response)
            
            return response
        except Exception as e:
            logger.error(f"Error in SecurityHeadersMiddleware: {e}")
            logger.error(f"Error type: {type(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise
    
    def _add_security_headers(self, response: Response) -> None:
        """Add all security headers to the response."""
        try:
            # Basic security headers
            response.headers["X-Content-Type-Options"] = self.config.x_content_type_options
            response.headers["X-Frame-Options"] = self.config.x_frame_options
            response.headers["X-XSS-Protection"] = self.config.x_xss_protection
            response.headers["Referrer-Policy"] = self.config.referrer_policy
            
            # Content Security Policy
            response.headers["Content-Security-Policy"] = self.config.get_csp_header()
            
            # Permissions Policy
            response.headers["Permissions-Policy"] = self.config.permissions_policy
            
            # HSTS (only in production)
            hsts_header = self.config.get_hsts_header()
            if hsts_header:
                response.headers["Strict-Transport-Security"] = hsts_header
            
            # Additional security headers
            response.headers["X-Permitted-Cross-Domain-Policies"] = "none"
            response.headers["Cross-Origin-Embedder-Policy"] = "require-corp"
            response.headers["Cross-Origin-Opener-Policy"] = "same-origin"
            response.headers["Cross-Origin-Resource-Policy"] = "cross-origin"
            
            # Remove server information safely
            if "Server" in response.headers:
                del response.headers["Server"]
        except Exception as e:
            logger.error(f"Error adding security headers: {e}")
            logger.error(f"Response type: {type(response)}")
            logger.error(f"Response headers type: {type(response.headers)}")
            logger.error(f"Available headers: {list(response.headers.keys())}")
            # Don't re-raise the exception to avoid breaking the response
            logger.warning("Continuing without some security headers due to error")


class CustomSecurityHeadersConfig(SecurityHeadersConfig):
    """
    Extended security configuration that can be customized per environment.
    """
    
    def __init__(
        self,
        custom_csp: Optional[Dict[str, str]] = None,
        enable_hsts_preload: bool = False,
        custom_frame_options: Optional[str] = None,
        additional_headers: Optional[Dict[str, str]] = None
    ):
        super().__init__()
        
        # Override CSP if provided
        if custom_csp:
            self.csp_directives.update(custom_csp)
        
        # Enable HSTS preload if requested
        self.hsts_preload = enable_hsts_preload
        
        # Override frame options if provided
        if custom_frame_options:
            self.x_frame_options = custom_frame_options
        
        # Store additional headers
        self.additional_headers = additional_headers or {}
    
    def get_additional_headers(self) -> Dict[str, str]:
        """Get any additional custom headers."""
        return self.additional_headers


def create_security_headers_middleware(
    custom_config: Optional[CustomSecurityHeadersConfig] = None
):
    """
    Factory function to create security headers middleware with optional custom config.
    
    For custom configuration, you would need to create a custom middleware class.
    This is a placeholder for future extensibility.
    
    Returns:
        SecurityHeadersMiddleware class ready for FastAPI
    """
    # For now, return the standard middleware class
    # Custom configuration can be implemented by subclassing SecurityHeadersMiddleware
    return SecurityHeadersMiddleware


# Export for easy importing
__all__ = [
    "SecurityHeadersMiddleware",
    "SecurityHeadersConfig", 
    "CustomSecurityHeadersConfig",
    "create_security_headers_middleware"
]
