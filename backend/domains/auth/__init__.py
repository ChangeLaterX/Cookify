"""
Authentication Domain Package.
Provides user authentication and profile management functionality.
"""

from .models import User, UserProfile
from .routes import router
from .schemas import (
    AuthUser,
    ErrorResponse,
    MessageResponse,
    PasswordChange,
    PasswordReset,
    TokenRefresh,
    TokenResponse,
    UserCreate,
    UserLogin,
    UserProfileResponse,
    UserProfileUpdate,
    UserResponse,
    UserWithProfileResponse,
)
from .services import (
    AuthenticationError,
    AuthService,
    auth_service,
    authenticate_user,
    get_current_user,
    get_user_profile,
    logout_user,
    refresh_token,
    update_user_profile,
    verify_token,
)

__all__: list[str] = [
    # Models
    "User",
    "UserProfile",
    # Schemas
    "UserLogin",
    "UserCreate",
    "TokenRefresh",
    "PasswordReset",
    "PasswordChange",
    "UserProfileUpdate",
    "TokenResponse",
    "UserResponse",
    "UserProfileResponse",
    "UserWithProfileResponse",
    "MessageResponse",
    "ErrorResponse",
    "AuthUser",
    # Services
    "AuthService",
    "AuthenticationError",
    "auth_service",
    "authenticate_user",
    "verify_token",
    "get_current_user",
    "refresh_token",
    "logout_user",
    "get_user_profile",
    "update_user_profile",
    # Routes
    "router",
]
