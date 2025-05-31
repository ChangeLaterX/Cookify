"""
Type definitions for the authentication domain.
"""
from enum import Enum
from typing import Protocol, Optional, Dict, Any
from abc import ABC, abstractmethod

from .schemas import User, AuthResponse, Session


class AuthProvider(str, Enum):
    """Authentication providers."""
    EMAIL = "email"
    GOOGLE = "google"
    GITHUB = "github"
    DISCORD = "discord"
    MAGIC_LINK = "magic_link"


class TokenType(str, Enum):
    """Token types for verification."""
    SIGNUP = "signup"
    RECOVERY = "recovery"
    EMAIL_CHANGE = "email_change"
    SMS = "sms"
    PHONE_CHANGE = "phone_change"


class CacheOperationResult(str, Enum):
    """Cache operation results."""
    HIT = "hit"
    MISS = "miss"
    EXPIRED = "expired"
    INVALIDATED = "invalidated"


class IUserCache(Protocol):
    """Interface for user caching."""
    
    async def get(self, token: str) -> Optional[User]:
        """Get user from cache."""
        ...
    
    async def set(self, token: str, user: User) -> None:
        """Store user in cache."""
        ...
    
    async def invalidate(self, token: str) -> None:
        """Remove user from cache."""
        ...
    
    async def invalidate_user(self, user_id: str) -> None:
        """Remove all cache entries for a user."""
        ...
    
    async def clear(self) -> None:
        """Clear all cache entries."""
        ...


class IAuthService(Protocol):
    """Interface for authentication service."""
    
    async def sign_up(self, email: str, password: str, metadata: Optional[Dict[str, Any]] = None) -> AuthResponse:
        """Register a new user."""
        ...
    
    async def sign_in(self, email: str, password: str) -> AuthResponse:
        """Sign in user."""
        ...
    
    async def sign_out(self) -> bool:
        """Sign out user."""
        ...
    
    async def refresh_token(self, refresh_token: str) -> AuthResponse:
        """Refresh access token."""
        ...
    
    async def get_user(self, access_token: str) -> User:
        """Get user from token."""
        ...
    
    async def verify_otp(self, email: str, token: str, token_type: TokenType) -> AuthResponse:
        """Verify OTP token."""
        ...
    
    async def reset_password_request(self, email: str) -> bool:
        """Request password reset."""
        ...


class UserMapperMixin(ABC):
    """Mixin for mapping Supabase user objects to our User schema."""
    
    @staticmethod
    def map_supabase_user(supabase_user: Any) -> User:
        """Map Supabase user object to User schema."""
        return User(
            id=supabase_user.id,
            email=supabase_user.email,
            email_confirmed_at=supabase_user.email_confirmed_at,
            phone=supabase_user.phone,
            confirmed_at=supabase_user.confirmed_at,
            last_sign_in_at=supabase_user.last_sign_in_at,
            created_at=supabase_user.created_at,
            updated_at=supabase_user.updated_at,
            user_metadata=supabase_user.user_metadata or {},
            app_metadata=supabase_user.app_metadata or {},
            aud=supabase_user.aud,
            role=supabase_user.role
        )
    
    @staticmethod
    def map_supabase_session(supabase_session: Any, user: User) -> Session:
        """Map Supabase session object to Session schema."""
        return Session(
            access_token=supabase_session.access_token,
            token_type="bearer",
            expires_in=supabase_session.expires_in,
            expires_at=supabase_session.expires_at,
            refresh_token=supabase_session.refresh_token,
            user=user
        )
