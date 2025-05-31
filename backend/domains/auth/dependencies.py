"""
Refactored authentication dependencies with better separation of concerns.
"""
import logging
from typing import Optional, List, Set, Union, Callable, Dict, Any
from functools import wraps
from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials

from domains.auth.service import auth_service
from domains.auth.schemas import User
from domains.auth.cache import user_cache
from domains.auth.context import set_current_user_in_context
from domains.auth.permissions import Permission, Role, validate_permissions, get_user_permissions
from core.security import security
from core.exceptions import (
    AuthenticationError, 
    AuthorizationError, 
    EmailNotVerifiedError,
    InsufficientPermissionsError
)

logger: logging.Logger = logging.getLogger(__name__)


class AuthDependencies:
    """Collection of authentication dependencies."""
    
    @staticmethod
    async def get_current_user_optional(
        credentials: Optional[HTTPAuthorizationCredentials] = Depends(security.optional)
    ) -> Optional[User]:
        """Get the current user from the authorization header (optional)."""
        if not credentials:
            return None
        
        try:
            token: str = credentials.credentials
            
            # Try cache first
            cached_user: User | None = await user_cache.get(token)
            if cached_user:
                set_current_user_in_context(cached_user)
                return cached_user
            
            # Get user from service
            user: User | None = await auth_service.get_user(token)

            if user:
                # Cache the user
                await user_cache.set(token, user)
                set_current_user_in_context(user)
            
            return user
            
        except AuthenticationError as e:
            logger.warning(f"Authentication failed: {e.status_code}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error in get_current_user_optional: {e}")
            return None
    
    @staticmethod
    async def get_current_user(
        credentials: HTTPAuthorizationCredentials = Depends(security.required)
    ) -> User:
        """Get the current user from the authorization header (required)."""
        try:
            token: str = credentials.credentials
            
            # Try cache first
            cached_user: User | None = await user_cache.get(token)
            if cached_user:
                set_current_user_in_context(cached_user)
                return cached_user
            
            # Get user from service
            user: User | None = await auth_service.get_user(token)

            if not user:
                raise AuthenticationError("Invalid token")
            
            # Cache the user
            await user_cache.set(token, user)
            set_current_user_in_context(user)
            
            return user
            
        except AuthenticationError:
            raise
        except Exception as e:
            logger.error(f"Unexpected error in get_current_user: {e}")
            raise AuthenticationError("Could not validate credentials")
    
    @staticmethod
    async def get_current_active_user(
        current_user: User = Depends(get_current_user)
    ) -> User:
        """Get the current active user with additional checks."""
        # Add any additional checks here:
        # - Check if user is banned
        # - Check if user account is suspended
        # - Check rate limits, etc.
        
        return current_user
    
    @staticmethod
    async def get_verified_user(
        current_user: User = Depends(get_current_user)
    ) -> User:
        """Get current user and ensure email is verified."""
        if not current_user.email_confirmed_at:
            raise EmailNotVerifiedError("Email verification required")
        return current_user


class RolePermissionDependencies:
    """Dependencies for role and permission checking."""
    
    @staticmethod
    def require_roles(*roles: Union[str, Role]) -> Callable:
        """Dependency factory to require specific roles."""
        def role_checker(current_user: User = Depends(AuthDependencies.get_current_user)) -> User:
            user_role: str = current_user.app_metadata.get("role", "user")
            role_strings: List[str] = [role.value if isinstance(role, Role) else role for role in roles]
            
            if user_role not in role_strings:
                raise AuthorizationError(f"Access denied. Required roles: {', '.join(role_strings)}")
            return current_user
        
        return role_checker
    
    @staticmethod
    def require_permissions(*permissions: Permission) -> Callable:
        """Dependency factory to require specific permissions."""
        def permission_checker(current_user: User = Depends(AuthDependencies.get_current_user)) -> User:
            user_role: str = current_user.app_metadata.get("role", "user")
            try:
                validate_permissions(user_role, set(permissions))
            except InsufficientPermissionsError:
                raise
            return current_user
        
        return permission_checker
    
    @staticmethod
    def require_admin(current_user: User = Depends(AuthDependencies.get_current_user)) -> User:
        """Require admin privileges."""
        user_role = current_user.app_metadata.get("role", "user")
        if user_role not in [Role.ADMIN.value, Role.SUPER_ADMIN.value]:
            raise AuthorizationError("Admin access required")
        return current_user
    
    @staticmethod
    def require_permission_or_self(permission: Permission) -> Callable:
        """Allow access if user has permission OR is accessing their own resource."""
        def permission_or_self_checker(
            request: Request,
            current_user: User = Depends(AuthDependencies.get_current_user)
        ) -> User:
            user_role: str = current_user.app_metadata.get("role", "user")
            user_permissions: Set[Permission] = get_user_permissions(user_role)
            
            # Check if user has the required permission
            if permission in user_permissions:
                return current_user
            
            # Check if user is accessing their own resource
            path_params: Dict[str, Any] = request.path_params
            resource_user_id: str | None = path_params.get("user_id") or path_params.get("id")

            if resource_user_id:
                # Sanitize and validate user ID
                resource_user_id = str(resource_user_id).strip()
                if resource_user_id == current_user.id:
                    logger.debug(f"User accessing own resource")
                    return current_user
            
            # Neither condition met
            raise AuthorizationError(
                f"Access denied. Required permission: {permission.value} or ownership of resource"
            )
        
        return permission_or_self_checker


class UtilityDependencies:
    """Utility dependencies for extracting specific user data."""
    
    @staticmethod
    async def get_user_id(current_user: User = Depends(AuthDependencies.get_current_user)) -> str:
        """Extract just the user ID from the current user."""
        return current_user.id
    
    @staticmethod
    async def get_user_email(current_user: User = Depends(AuthDependencies.get_current_user)) -> str:
        """Extract just the user email from the current user."""
        if not current_user.email:
            raise AuthenticationError("User email not available")
        return current_user.email
    
    @staticmethod
    async def get_user_permissions_dep(current_user: User = Depends(AuthDependencies.get_current_user)) -> set:
        """Get the current user's permissions."""
        user_role: str = current_user.app_metadata.get("role", "user")
        return get_user_permissions(user_role)
    
    @staticmethod
    async def get_user_role(current_user: User = Depends(AuthDependencies.get_current_user)) -> str:
        """Get the current user's role."""
        return current_user.app_metadata.get("role", "user")


# Convenience exports for backward compatibility
get_current_user_optional = AuthDependencies.get_current_user_optional
get_current_user = AuthDependencies.get_current_user
get_current_active_user = AuthDependencies.get_current_active_user
get_verified_user = AuthDependencies.get_verified_user

require_roles = RolePermissionDependencies.require_roles
require_permissions = RolePermissionDependencies.require_permissions
require_admin = RolePermissionDependencies.require_admin
require_permission_or_self = RolePermissionDependencies.require_permission_or_self

get_user_id = UtilityDependencies.get_user_id
get_user_email = UtilityDependencies.get_user_email
get_user_permissions_dep = UtilityDependencies.get_user_permissions_dep
get_user_role = UtilityDependencies.get_user_role


# Legacy support
async def get_current_admin_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Legacy admin user dependency."""
    return require_admin(current_user)


def require_email_confirmed():
    """Legacy email confirmation dependency."""
    return get_verified_user
