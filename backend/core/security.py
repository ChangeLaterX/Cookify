"""
Security utilities and helpers.
"""
import hashlib
import secrets
from typing import Optional
from passlib.context import CryptContext
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Request
from core.config import settings

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class ConfigurableHTTPBearer(HTTPBearer):
    """Enhanced HTTP Bearer security with configurable auto_error."""
    
    def __init__(self, auto_error: bool = True, description: Optional[str] = None):
        super().__init__(auto_error=auto_error, description=description)


class SecuritySchemes:
    """Centralized security schemes for different use cases."""
    
    # For endpoints that require authentication
    required = ConfigurableHTTPBearer(
        auto_error=True,
        description="Bearer token required for authentication"
    )
    
    # For endpoints with optional authentication
    optional = ConfigurableHTTPBearer(
        auto_error=False,
        description="Bearer token for optional authentication"
    )


def generate_secret_key() -> str:
    """Generate a secure random secret key."""
    return secrets.token_urlsafe(32)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Get hash of a password."""
    return pwd_context.hash(password)


def generate_token() -> str:
    """Generate a secure random token."""
    return secrets.token_urlsafe(32)


def hash_token(token: str) -> str:
    """Hash a token for secure storage."""
    return hashlib.sha256(token.encode()).hexdigest()


def verify_token_hash(token: str, token_hash: str) -> bool:
    """Verify a token against its hash."""
    return hash_token(token) == token_hash


def get_client_ip(request: Request) -> str:
    """Get client IP address from request."""
    # Check for forwarded headers first (for reverse proxies)
    forwarded_for = request.headers.get("x-forwarded-for")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    
    # Check for real IP header
    real_ip = request.headers.get("x-real-ip")
    if real_ip:
        return real_ip
    
    # Fall back to direct client IP
    if hasattr(request, "client") and request.client:
        return request.client.host
    
    return "unknown"


def get_user_agent(request: Request) -> str:
    """Get user agent from request."""
    return request.headers.get("user-agent", "unknown")


# Global security schemes
security = SecuritySchemes()
