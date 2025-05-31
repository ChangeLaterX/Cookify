"""
Advanced authentication dependencies with enhanced features.
Refactored for better maintainability and performance.
"""
import logging
from typing import Dict, Optional, Callable, Any, List, Union
from functools import wraps
from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials

from domains.auth.dependencies import get_current_user, AuthDependencies
from domains.auth.schemas import User
from domains.auth.permissions import Permission, Role, has_permission
from domains.auth.context import get_current_user_from_context
from core.security import security, get_client_ip
from core.exceptions import AuthorizationError, RateLimitError, AuthenticationError
from middleware.request_id import get_request_id

logger: logging.Logger = logging.getLogger(__name__)


class AdvancedAuthDependencies:
    """Advanced authentication dependencies with audit logging and enhanced security."""
    
    @staticmethod
    def require_permission_or_self(permission: Permission) -> Callable:
        """
        Dependency that allows access if user has permission OR is accessing their own resource.
        """
        async def permission_or_self_checker(
            request: Request,
            current_user: User = Depends(get_current_user)
        ) -> User:
            user_role = current_user.app_metadata.get("role", "user")
            
            # Check if user has the required permission
            if has_permission(user_role, permission):
                return current_user
            
            # Check if user is accessing their own resource
            path_params: Dict[str, Any] = request.path_params
            resource_user_id: Any | None = path_params.get("user_id") or path_params.get("id")
            
            if resource_user_id and resource_user_id == current_user.id:
                logger.debug(f"User {current_user.id} accessing own resource")
                return current_user
            
            # Neither condition met
            raise AuthorizationError(
                f"Access denied. Required permission: {permission.value} or ownership of resource"
            )
        
        return permission_or_self_checker
    
    @staticmethod
    def require_role_or_self(*allowed_roles: Union[str, Role]) -> Callable:
        """
        Dependency that allows access if user has role OR is accessing their own resource.
        """
        async def role_or_self_checker(
            request: Request,
            current_user: User = Depends(get_current_user)
        ) -> User:
            user_role = current_user.app_metadata.get("role", "user")
            role_strings: List[str] = [role.value if isinstance(role, Role) else role for role in allowed_roles]
            
            # Check if user has required role
            if user_role in role_strings:
                return current_user
            
            # Check if user is accessing their own resource
            path_params: Dict[str, Any] = request.path_params
            resource_user_id: Any | None = path_params.get("user_id") or path_params.get("id")
            
            if resource_user_id and resource_user_id == current_user.id:
                logger.debug(f"User {current_user.id} accessing own resource")
                return current_user
            
            raise AuthorizationError(
                f"Access denied. Required roles: {', '.join(role_strings)} or ownership of resource"
            )
        
        return role_or_self_checker
    
    @staticmethod
    async def get_current_user_with_audit(
        request: Request,
        credentials: HTTPAuthorizationCredentials = Depends(security.required)
    ) -> User:
        """
        Get current user and add request metadata for comprehensive audit logging.
        """
        # Use the standard dependency to get the user
        user: User = await AuthDependencies.get_current_user(credentials)
        
        # Add request metadata to user context for audit purposes
        user._request_metadata = {
            "request_id": get_request_id(request),
            "client_ip": get_client_ip(request)[:45],
            "user_agent": request.headers.get("user-agent", "unknown")[:200],
            "endpoint": f"{request.method} {request.url.path}",
            "timestamp": request.state.start_time if hasattr(request.state, 'start_time') else None,
            "referer": request.headers.get("referer", "direct")[:200] if request.headers.get("referer") else "direct",
        }
        
        # Sanitize IP for logging
        safe_ip: str = get_client_ip(request)[:45] if get_client_ip(request) else "unknown"
        logger.info(
            f"User access - Method: {request.method}, Path: {request.url.path}, "
            f"IP: {safe_ip}, Request ID: {get_request_id(request)}"
        )
        
        return user
    
    @staticmethod
    def require_multiple_permissions(
        *permissions: Permission, 
        require_all: bool = True
    ) -> Callable:
        """
        Dependency that requires multiple permissions.
        
        Args:
            permissions: List of required permissions
            require_all: If True, user must have ALL permissions. If False, ANY permission is sufficient.
        """
        async def multi_permission_checker(
            current_user: User = Depends(get_current_user)
        ) -> User:
            user_role: str = current_user.app_metadata.get("role", "user")
            user_permissions: set[Permission] = set()

            # Get user permissions based on role
            if user_role in ["admin", "super_admin"]:
                user_permissions = set(Permission)
            elif user_role == "moderator":
                user_permissions = {
                    Permission.READ_USERS, Permission.WRITE_USERS,
                    Permission.READ_MEALS, Permission.WRITE_MEALS, Permission.DELETE_MEALS
                }
            else:
                user_permissions = {
                    Permission.READ_PROFILE, Permission.WRITE_PROFILE,
                    Permission.READ_MEALS, Permission.WRITE_MEALS, Permission.DELETE_MEALS
                }
            
            required_perms = set(permissions)
            
            if require_all:
                if not required_perms.issubset(user_permissions):
                    missing: set[Permission] = required_perms - user_permissions
                    raise AuthorizationError(
                        f"Missing required permissions: {', '.join(p.value for p in missing)}"
                    )
            else:
                if not required_perms.intersection(user_permissions):
                    raise AuthorizationError(
                        f"At least one of these permissions required: {', '.join(p.value for p in required_perms)}"
                    )
            
            return current_user
        
        return multi_permission_checker
    
    @staticmethod
    async def require_auth_for_mutations(
        request: Request,
        credentials: Optional[HTTPAuthorizationCredentials] = Depends(security.optional)
    ) -> Optional[User]:
        """
        Require authentication only for mutation operations (POST, PUT, PATCH, DELETE).
        GET and HEAD requests are allowed without authentication.
        """
        if request.method in ["GET", "HEAD", "OPTIONS"]:
            # Read operations don't require authentication
            if credentials:
                # If credentials are provided, validate them
                try:
                    return await AuthDependencies.get_current_user(credentials)
                except Exception:
                    # If validation fails, return None for read operations
                    return None
            return None
        else:
            # Mutation operations require authentication
            if not credentials:
                raise AuthenticationError("Authentication required for mutation operations")
            return await AuthDependencies.get_current_user(credentials)

    @staticmethod
    async def get_current_user_with_refresh(
        request: Request,
        credentials: HTTPAuthorizationCredentials = Depends(security.required)
    ) -> User:
        """
        Get current user with enhanced request metadata and refresh capability.
        """
        user: User = await AuthDependencies.get_current_user(credentials)
        
        # Add enhanced metadata
        user._request_metadata = {
            "request_id": get_request_id(request),
            "client_ip": get_client_ip(request),
            "user_agent": request.headers.get("user-agent", "unknown"),
            "endpoint": f"{request.method} {request.url.path}",
            "timestamp": getattr(request.state, 'start_time', None),
            "referer": request.headers.get("referer", "direct"),
            "accept_language": request.headers.get("accept-language", "unknown"),
        }
        
        return user


def audit_endpoint(description: str = "", log_request_body: bool = False) -> Callable:
    """
    Enhanced decorator for endpoints that require comprehensive audit logging.
    
    Args:
        description: Custom description for the audit log
        log_request_body: Whether to log the request body (be careful with sensitive data)
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Try to get user and request from context
            user = get_current_user_from_context()
            
            if user:
                metadata = getattr(user, '_request_metadata', {})
                
                # Sanitize audit data to prevent sensitive information exposure
                audit_data = {
                    "user_id": user.id,  # Use ID instead of email for privacy
                    "function": func.__name__,
                    "description": description or f"Executed {func.__name__}",
                    "request_id": metadata.get('request_id', 'unknown'),
                    "client_ip": str(metadata.get('client_ip', 'unknown'))[:45],  # Truncate IP
                    "endpoint": str(metadata.get('endpoint', 'unknown'))[:100],  # Limit endpoint length
                }
                
                # Only log request body for non-sensitive endpoints and if explicitly requested
                if log_request_body and 'request' in kwargs and func.__name__ not in ['signin', 'signup', 'reset_password']:
                    try:
                        audit_data["request_body_logged"] = True
                    except Exception as e:
                        logger.warning(f"Could not log request body: {str(e)[:100]}")
                
                logger.info(f"AUDIT: {audit_data}")
            else:
                # Unauthenticated access - minimal logging
                logger.info(f"AUDIT: Unauthenticated access to {func.__name__}")
            
            # Execute the original function
            result = await func(*args, **kwargs)
            
            # Log successful completion without sensitive details
            if user:
                logger.info(f"AUDIT: User {user.id} completed {func.__name__}")
            
            return result
        
        return wrapper
    return decorator


def rate_limit_per_user(max_requests: int = 100, window_seconds: int = 3600) -> Callable:
    """
    Rate limiting decorator per user.
    
    Args:
        max_requests: Maximum requests allowed in the time window
        window_seconds: Time window in seconds
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            user = get_current_user_from_context()
            
            if user:
                # In production, you'd use Redis or similar for distributed rate limiting
                # For now, this is a placeholder
                user_id = user.id
                # TODO: Implement actual rate limiting logic
                pass
            
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator


# Export the new dependencies
require_permission_or_self = AdvancedAuthDependencies.require_permission_or_self
require_role_or_self = AdvancedAuthDependencies.require_role_or_self
get_current_user_with_audit = AdvancedAuthDependencies.get_current_user_with_audit
require_multiple_permissions = AdvancedAuthDependencies.require_multiple_permissions

# Export additional functions
require_auth_for_mutations = AdvancedAuthDependencies.require_auth_for_mutations
get_current_user_with_refresh = AdvancedAuthDependencies.get_current_user_with_refresh
