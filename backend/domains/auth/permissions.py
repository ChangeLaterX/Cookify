"""
Type-safe permissions and roles system.
"""
from enum import Enum
from typing import Set, Dict
from core.exceptions import InsufficientPermissionsError


class Permission(str, Enum):
    """Available permissions in the system."""
    
    # User permissions
    READ_USERS = "read:users"
    WRITE_USERS = "write:users"
    DELETE_USERS = "delete:users"
    
    # Admin permissions
    ADMIN_ACCESS = "admin:access"
    MANAGE_ROLES = "manage:roles"
    VIEW_SYSTEM_LOGS = "view:system_logs"
    
    # Meal planning permissions
    READ_MEALS = "read:meals"
    WRITE_MEALS = "write:meals"
    DELETE_MEALS = "delete:meals"
    SHARE_MEALS = "share:meals"
    
    # Profile permissions
    READ_PROFILE = "read:profile"
    WRITE_PROFILE = "write:profile"
    DELETE_PROFILE = "delete:profile"


class Role(str, Enum):
    """Available roles in the system."""
    
    USER = "user"
    MODERATOR = "moderator"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"


# Role-Permission mapping
ROLE_PERMISSIONS: Dict[Role, Set[Permission]] = {
    Role.USER: {
        Permission.READ_PROFILE,
        Permission.WRITE_PROFILE,
        Permission.READ_MEALS,
        Permission.WRITE_MEALS,
        Permission.DELETE_MEALS,
        Permission.SHARE_MEALS,
    },
    Role.MODERATOR: {
        Permission.READ_PROFILE,
        Permission.WRITE_PROFILE,
        Permission.READ_MEALS,
        Permission.WRITE_MEALS,
        Permission.DELETE_MEALS,
        Permission.SHARE_MEALS,
        Permission.READ_USERS,
        Permission.WRITE_USERS,
    },
    Role.ADMIN: {
        Permission.READ_PROFILE,
        Permission.WRITE_PROFILE,
        Permission.READ_MEALS,
        Permission.WRITE_MEALS,
        Permission.DELETE_MEALS,
        Permission.SHARE_MEALS,
        Permission.READ_USERS,
        Permission.WRITE_USERS,
        Permission.DELETE_USERS,
        Permission.ADMIN_ACCESS,
        Permission.MANAGE_ROLES,
        Permission.VIEW_SYSTEM_LOGS,
    },
    Role.SUPER_ADMIN: {
        # Super admin has all permissions
        perm for perm in Permission
    }
}


def get_user_permissions(user_role: str) -> Set[Permission]:
    """Get permissions for a given user role."""
    try:
        role = Role(user_role)
        return ROLE_PERMISSIONS.get(role, set())
    except ValueError:
        # Unknown role, return basic user permissions
        return ROLE_PERMISSIONS.get(Role.USER, set())


def has_permission(user_role: str, required_permission: Permission) -> bool:
    """Check if a user role has a specific permission."""
    user_permissions: Set[Permission] = get_user_permissions(user_role)
    return required_permission in user_permissions


def has_any_permission(user_role: str, required_permissions: Set[Permission]) -> bool:
    """Check if a user role has any of the required permissions."""
    user_permissions: Set[Permission] = get_user_permissions(user_role)
    return bool(user_permissions.intersection(required_permissions))


def has_all_permissions(user_role: str, required_permissions: Set[Permission]) -> bool:
    """Check if a user role has all of the required permissions."""
    user_permissions: Set[Permission] = get_user_permissions(user_role)
    return required_permissions.issubset(user_permissions)


def validate_permissions(user_role: str, required_permissions: Set[Permission]) -> None:
    """Validate that a user has all required permissions, raise exception if not."""
    if not has_all_permissions(user_role, required_permissions):
        user_permissions: Set[Permission] = get_user_permissions(user_role)
        missing_permissions: Set[Permission] = required_permissions - user_permissions
        raise InsufficientPermissionsError(list(missing_permissions))
