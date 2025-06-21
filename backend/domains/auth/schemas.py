"""
Pydantic Schemas for Authentication Domain.
Defines request/response models for API endpoints.
"""

from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional, Dict, Any, List
from datetime import datetime
from uuid import UUID


# ============================================================================
# Request Schemas
# ============================================================================


class UserLogin(BaseModel):
    """Schema for user login request."""

    email: EmailStr = Field(..., description="User email address")
    password: str = Field(
        ..., min_length=6, max_length=128, description="User password"
    )


class UserCreate(BaseModel):
    """Schema for user registration request."""

    email: EmailStr = Field(..., description="User email address")
    password: str = Field(
        ..., min_length=6, max_length=128, description="User password"
    )
    username: Optional[str] = Field(
        None, min_length=3, max_length=50, description="Optional username/display name"
    )

    @field_validator("password")
    @classmethod
    def validate_password(cls, v):
        """Validate password strength using enhanced security."""
        from shared.utils.password_security import validate_password_strength

        is_valid, errors = validate_password_strength(v)
        if not is_valid:
            raise ValueError("; ".join(errors))
        return v


class TokenRefresh(BaseModel):
    """Schema for token refresh request."""

    refresh_token: str = Field(..., description="Valid refresh token")


class PasswordReset(BaseModel):
    """Schema for password reset request."""

    email: EmailStr = Field(..., description="User email address for password reset")


class PasswordResetConfirm(BaseModel):
    """Schema for password reset confirmation."""

    token: str = Field(..., description="Password reset token")
    new_password: str = Field(
        ..., min_length=6, max_length=128, description="New password"
    )

    @field_validator("new_password")
    @classmethod
    def validate_new_password(cls, v):
        """Validate new password strength using enhanced security."""
        from shared.utils.password_security import validate_password_strength

        is_valid, errors = validate_password_strength(v)
        if not is_valid:
            raise ValueError("; ".join(errors))
        return v


class EmailVerification(BaseModel):
    """Schema for email verification request."""

    token: str = Field(..., description="Email verification token")


class ResendVerification(BaseModel):
    """Schema for resending verification email."""

    email: EmailStr = Field(..., description="User email address")


class PasswordChange(BaseModel):
    """Schema for password change request."""

    old_password: str = Field(
        ..., min_length=6, max_length=128, description="Current password"
    )
    new_password: str = Field(
        ..., min_length=6, max_length=128, description="New password"
    )

    @field_validator("new_password")
    @classmethod
    def validate_new_password(cls, v):
        """Validate new password strength using enhanced security."""
        from shared.utils.password_security import validate_password_strength

        is_valid, errors = validate_password_strength(v)
        if not is_valid:
            raise ValueError("; ".join(errors))
        return v


class UserProfileUpdate(BaseModel):
    """Schema for user profile update request."""

    display_name: Optional[str] = Field(
        None, min_length=1, max_length=100, description="Display name"
    )
    first_name: Optional[str] = Field(
        None, min_length=1, max_length=50, description="First name"
    )
    last_name: Optional[str] = Field(
        None, min_length=1, max_length=50, description="Last name"
    )
    avatar_url: Optional[str] = Field(None, max_length=255, description="Avatar URL")
    bio: Optional[str] = Field(None, max_length=500, description="User bio")
    timezone: Optional[str] = Field(None, max_length=50, description="User timezone")
    language: Optional[str] = Field(
        None, max_length=10, description="Preferred language"
    )
    preferences: Optional[Dict[str, Any]] = Field(
        None, description="User preferences as JSON object"
    )


# ============================================================================
# Response Schemas
# ============================================================================


class UserResponse(BaseModel):
    """Schema for user data in responses."""

    id: UUID = Field(..., description="User unique identifier")
    email: EmailStr = Field(..., description="User email address")
    is_active: bool = Field(..., description="Whether user account is active")
    is_verified: bool = Field(..., description="Whether user email is verified")
    created_at: datetime = Field(..., description="Account creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    """Schema for authentication token response."""

    access_token: str = Field(..., description="JWT access token")
    refresh_token: Optional[str] = Field(None, description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration time in seconds")
    expires_at: datetime = Field(..., description="Token expiration timestamp")


# ============================================================================
# Standardized API Response Schemas
# ============================================================================


class ApiResponse(BaseModel):
    """Standardized API response format."""

    success: bool = Field(..., description="Operation success status")
    data: Optional[Any] = Field(None, description="Response data")
    message: str = Field(..., description="Response message")
    error: Optional[str] = Field(None, description="Error message if any")


class AuthResponse(BaseModel):
    """Schema for authentication responses with standardized format."""

    success: bool = Field(default=True, description="Operation success status")
    data: TokenResponse = Field(..., description="Authentication token data")
    message: str = Field(
        default="Authentication successful", description="Response message"
    )
    error: Optional[str] = Field(None, description="Error message if any")


class UserProfileResponse(BaseModel):
    """Schema for user profile data in responses."""

    id: UUID = Field(..., description="Profile unique identifier")
    user_id: UUID = Field(..., description="Associated user ID")
    display_name: Optional[str] = Field(None, description="Display name")
    first_name: Optional[str] = Field(None, description="First name")
    last_name: Optional[str] = Field(None, description="Last name")
    avatar_url: Optional[str] = Field(None, description="Avatar URL")
    bio: Optional[str] = Field(None, description="User bio")
    timezone: str = Field(default="UTC", description="User timezone")
    language: str = Field(default="en", description="Preferred language")
    preferences: Optional[Dict[str, Any]] = Field(None, description="User preferences")
    created_at: datetime = Field(..., description="Profile creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    class Config:
        from_attributes = True


class UserWithProfileResponse(BaseModel):
    """Schema for complete user data with profile."""

    user: UserResponse = Field(..., description="User account data")
    profile: Optional[UserProfileResponse] = Field(
        None, description="User profile data"
    )


class MessageResponse(BaseModel):
    """Schema for simple message responses."""

    message: str = Field(..., description="Response message")
    success: bool = Field(default=True, description="Operation success status")
    details: Optional[Dict[str, Any]] = Field(
        default=None, description="Additional details"
    )


class ErrorResponse(BaseModel):
    """Schema for error responses."""

    error: str = Field(..., description="Error message")
    error_code: Optional[str] = Field(None, description="Specific error code")
    details: Optional[Dict[str, Any]] = Field(
        None, description="Additional error details"
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow, description="Error timestamp"
    )


# ============================================================================
# Authentication State Schemas
# ============================================================================


class AuthUser(BaseModel):
    """Schema for authenticated user context."""

    id: UUID = Field(..., description="User unique identifier")
    email: EmailStr = Field(..., description="User email address")
    is_active: bool = Field(..., description="Whether user account is active")
    is_verified: bool = Field(..., description="Whether user email is verified")
    is_super_admin: bool = Field(
        default=False, description="Whether user is super admin"
    )
    profile: Optional[UserProfileResponse] = Field(
        None, description="User profile data"
    )

    class Config:
        from_attributes = True


# ============================================================================
# Password Security Schemas
# ============================================================================


class PasswordStrengthCheck(BaseModel):
    """Schema for password strength checking request."""

    password: str = Field(
        ..., min_length=1, max_length=128, description="Password to check"
    )


class PasswordRequirement(BaseModel):
    """Schema for individual password requirement."""

    key: str = Field(..., description="Requirement key")
    met: bool = Field(..., description="Whether requirement is met")
    description: str = Field(..., description="Human-readable description")


class PasswordStrengthResponse(BaseModel):
    """Schema for password strength analysis response."""

    strength: int = Field(..., ge=0, le=5, description="Strength level (0-5)")
    score: int = Field(..., ge=0, le=100, description="Strength score (0-100)")
    is_valid: bool = Field(..., description="Whether password meets all requirements")
    errors: List[str] = Field(default_factory=list, description="Validation errors")
    warnings: List[str] = Field(default_factory=list, description="Warnings")
    suggestions: List[str] = Field(
        default_factory=list, description="Improvement suggestions"
    )
    requirements: List[PasswordRequirement] = Field(
        default_factory=list, description="Detailed requirements"
    )
    strength_label: str = Field(..., description="Human-readable strength label")


# Export schemas for easy importing
__all__ = [
    # Request schemas
    "UserLogin",
    "UserCreate",
    "TokenRefresh",
    "PasswordReset",
    "PasswordResetConfirm",
    "PasswordChange",
    "EmailVerification",
    "ResendVerification",
    "UserProfileUpdate",
    # Response schemas
    "UserResponse",
    "TokenResponse",
    "UserProfileResponse",
    "UserWithProfileResponse",
    "MessageResponse",
    "ErrorResponse",
    "AuthUser",
    "ApiResponse",
    "AuthResponse",
    # Password security schemas
    "PasswordStrengthCheck",
    "PasswordRequirement",
    "PasswordStrengthResponse",
]
