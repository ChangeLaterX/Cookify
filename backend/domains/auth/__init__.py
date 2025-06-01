"""
Authentication Domain Package.
Provides user authentication and profile management functionality.
"""

from .models import User, UserProfile
from .schemas import (
    UserLogin, UserCreate, TokenRefresh, PasswordReset, PasswordChange,
    UserProfileUpdate, TokenResponse, UserResponse, UserProfileResponse,
    UserWithProfileResponse, MessageResponse, ErrorResponse, AuthUser
)
from .services import (
    AuthService, AuthenticationError, auth_service,
    authenticate_user, verify_token, get_current_user, refresh_token,
    logout_user, get_user_profile, update_user_profile
)
from .routes import router

__all__ = [
    # Models
    "User", "UserProfile",
    # Schemas
    "UserLogin", "UserCreate", "TokenRefresh", "PasswordReset", "PasswordChange",
    "UserProfileUpdate", "TokenResponse", "UserResponse", "UserProfileResponse", 
    "UserWithProfileResponse", "MessageResponse", "ErrorResponse", "AuthUser",
    # Services
    "AuthService", "AuthenticationError", "auth_service",
    "authenticate_user", "verify_token", "get_current_user", "refresh_token",
    "logout_user", "get_user_profile", "update_user_profile",
    # Routes
    "router"
]