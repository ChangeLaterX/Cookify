"""
Authentication domain module.
Refactored for better structure and maintainability.
"""

# Core authentication components
from .service import auth_service
from .dependencies import (
    # Basic dependencies
    get_current_user,
    get_current_user_optional,
    get_current_active_user,
    get_verified_user,
    
    # Role and permission dependencies
    require_roles,
    require_permissions,
    require_admin,
    require_permission_or_self,
    
    # Utility dependencies
    get_user_id,
    get_user_email,
    get_user_permissions_dep,
    get_user_role,
    
    # Legacy support
    get_current_admin_user,
    require_email_confirmed,
)

# Advanced dependencies
from .advanced_dependencies import (
    require_role_or_self,
    get_current_user_with_audit,
    require_multiple_permissions,
    audit_endpoint,
    rate_limit_per_user,
)

# Schemas
from .schemas import (
    User,
    Session,
    AuthResponse,
    UserSignUpRequest,
    UserSignInRequest,
    TokenRefreshRequest,
    PasswordResetRequest,
    UserUpdateRequest,
    SuccessResponse,
    OTPVerificationRequest,
    MagicLinkRequest,
)

# Permissions and roles
from .permissions import Permission, Role, has_permission, get_user_permissions

# Cache
from .cache import user_cache, get_cache_stats

# Router
from .router import router

# Types
from .types import AuthProvider, TokenType, IUserCache, IAuthService

__all__ = [
    # Core service
    "auth_service",
    
    # Dependencies
    "get_current_user",
    "get_current_user_optional", 
    "get_current_active_user",
    "get_verified_user",
    "require_roles",
    "require_permissions",
    "require_admin",
    "require_permission_or_self",
    "require_role_or_self",
    "get_current_user_with_audit",
    "require_multiple_permissions",
    
    # Decorators
    "audit_endpoint",
    "rate_limit_per_user",
    
    # Utility functions
    "get_user_id",
    "get_user_email", 
    "get_user_permissions_dep",
    "get_user_role",
    
    # Schemas
    "User",
    "Session",
    "AuthResponse",
    "UserSignUpRequest",
    "UserSignInRequest",
    "TokenRefreshRequest",
    "PasswordResetRequest",
    "UserUpdateRequest",
    "SuccessResponse",
    "OTPVerificationRequest",
    "MagicLinkRequest",
    
    # Permissions
    "Permission",
    "Role", 
    "has_permission",
    "get_user_permissions",
    
    # Cache
    "user_cache",
    "get_cache_stats",
    
    # Router
    "router",
    
    # Types
    "AuthProvider",
    "TokenType",
    "IUserCache",
    "IAuthService",
    
    # Legacy support
    "get_current_admin_user",
    "require_email_confirmed",
]
