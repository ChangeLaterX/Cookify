"""
Authentication schemas for Supabase Auth integration.
Enhanced with better validation and type safety.
"""

from datetime import datetime
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator
from shared.utils.validation import (
    is_valid_email, 
    validate_password_complexity,
    sanitize_metadata_value,
    validate_metadata_size,
    sanitize_metadata_key,
    sanitize_url,
    validate_phone_number
)
import string


class UserSignUpRequest(BaseModel):
    """Schema for user registration with enhanced validation."""

    email: EmailStr
    password: str = Field(
        ...,
        min_length=6,
        max_length=128,
        description="Password must be 6-128 characters",
    )
    user_metadata: Optional[Dict[str, Any]] = Field(
        default=None, description="Additional user metadata"
    )

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Validate password strength using comprehensive validation."""
        is_valid, errors = validate_password_complexity(
            password=v,
            min_length=8,
            require_uppercase=True,
            require_lowercase=True,
            require_digits=True,
            require_special=True
        )
        
        if not is_valid:
            raise ValueError("; ".join(errors))
        
        return v

    @field_validator("user_metadata")
    @classmethod
    def validate_metadata(cls, v: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Validate user metadata using comprehensive validation."""
        if v is None:
            return v

        # Validate total metadata size (10KB limit)
        if not validate_metadata_size(v, max_total_size=10240):
            raise ValueError("User metadata too large (max 10KB)")

        # Sanitize and validate metadata
        sanitized_metadata: Dict[str, Any] = {}
        forbidden_keys: set[str] = {"password", "token", "secret", "key", "auth", "session"}
        
        for key, value in v.items():
            # Sanitize the key
            sanitized_key: EmailStr = sanitize_metadata_key(key, max_length=50)
            if not sanitized_key:
                continue
            
            # Check for forbidden keys
            if sanitized_key.lower() in forbidden_keys:
                raise ValueError(f"Metadata cannot contain sensitive field: {sanitized_key}")
            
            # Sanitize the value
            sanitized_value: str = sanitize_metadata_value(value, max_string_length=1000)
            sanitized_metadata[sanitized_key] = sanitized_value

        return sanitized_metadata


class UserSignInRequest(BaseModel):
    """Schema for user login with rate limiting support."""

    email: EmailStr
    password: str = Field(..., min_length=6, max_length=128)
    remember_me: bool = Field(default=False, description="Extended session duration")

    @field_validator("password")
    @classmethod
    def validate_password_not_empty(cls, v: str) -> str:
        """Ensure password is not empty or just whitespace."""
        if not v.strip():
            raise ValueError("Password cannot be empty")
        return v


class PasswordResetRequest(BaseModel):
    """Schema for password reset request."""

    email: EmailStr


class PasswordUpdateRequest(BaseModel):
    """Schema for password update."""

    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="New password must be at least 8 characters",
    )

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Validate password strength using comprehensive validation."""
        is_valid, errors = validate_password_complexity(
            password=v,
            min_length=8,
            require_uppercase=True,
            require_lowercase=True,
            require_digits=True,
            require_special=True
        )
        
        if not is_valid:
            raise ValueError("; ".join(errors))
        
        return v


class UserUpdateRequest(BaseModel):
    """Schema for updating user profile."""

    email: Optional[EmailStr] = None
    user_metadata: Optional[Dict[str, Any]] = None

    @field_validator("user_metadata")
    @classmethod
    def validate_metadata(cls, v: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Validate user metadata using comprehensive validation."""
        if v is None:
            return v

        # Validate total metadata size (10KB limit)
        if not validate_metadata_size(v, max_total_size=10240):
            raise ValueError("User metadata too large (max 10KB)")

        # Sanitize and validate metadata
        sanitized_metadata: Dict[str, Any] = {}
        forbidden_keys: set[str] = {"password", "token", "secret", "key", "auth", "session"}
        
        for key, value in v.items():
            # Sanitize the key
            sanitized_key: EmailStr = sanitize_metadata_key(key, max_length=50)
            if not sanitized_key:
                continue 
            
            # Check for forbidden keys
            if sanitized_key.lower() in forbidden_keys:
                raise ValueError(f"Metadata cannot contain sensitive field: {sanitized_key}")
            
            # Sanitize the value
            sanitized_value: str = sanitize_metadata_value(value, max_string_length=1000)
            sanitized_metadata[sanitized_key] = sanitized_value

        return sanitized_metadata


class User(BaseModel):
    """Schema for user data response."""

    id: str
    email: Optional[str] = None
    email_confirmed_at: Optional[datetime] = None
    phone: Optional[str] = None
    confirmed_at: Optional[datetime] = None
    last_sign_in_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    user_metadata: Dict[str, Any] = {}
    app_metadata: Dict[str, Any] = {}
    aud: Optional[str] = None
    role: Optional[str] = None

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        """Validate phone number format."""
        if v is None or v == "":
            return v
        
        # Use comprehensive phone validation
        if not validate_phone_number(v, strict_international=True):
            raise ValueError("Phone number must be in valid international format (e.g., +1234567890)")
        
        return v


class Session(BaseModel):
    """Schema for session data response."""

    access_token: str
    token_type: str = "bearer"
    expires_in: Optional[int] = None
    expires_at: Optional[int] = None
    refresh_token: str
    user: User


class AuthResponse(BaseModel):
    """Schema for authentication response."""

    user: Optional[User] = None
    session: Optional[Session] = None


class TokenRefreshRequest(BaseModel):
    """Schema for token refresh request."""

    refresh_token: str = Field(..., min_length=1)

    @field_validator("refresh_token")
    @classmethod
    def validate_refresh_token(cls, v: str) -> str:
        """Validate refresh token."""
        if not v.strip():
            raise ValueError("Refresh token cannot be empty or just whitespace")
        return v.strip()


class EmailVerificationRequest(BaseModel):
    """Schema for email verification."""

    token: str = Field(..., min_length=1)
    type: str = "signup"

    @field_validator("token")
    @classmethod
    def validate_token(cls, v: str) -> str:
        """Validate verification token."""
        if not v.strip():
            raise ValueError("Token cannot be empty or just whitespace")
        return v.strip()

    @field_validator("type")
    @classmethod
    def validate_type(cls, v: str) -> str:
        """Validate verification type."""
        allowed_types: set[str] = {"signup", "recovery", "email_change", "invite"}
        if v.lower() not in allowed_types:
            raise ValueError(f'Type must be one of: {", ".join(sorted(allowed_types))}')
        return v.lower()


class OTPVerificationRequest(BaseModel):
    """Schema for OTP verification."""

    email: EmailStr
    token: str = Field(..., min_length=4, max_length=10)
    type: str = "email"

    @field_validator("token")
    @classmethod
    def validate_token(cls, v: str) -> str:
        """Validate OTP token."""
        if not v.strip():
            raise ValueError("Token cannot be empty or just whitespace")
        if not v.isdigit():
            raise ValueError("Token must contain only digits")
        return v.strip()

    @field_validator("type")
    @classmethod
    def validate_type(cls, v: str) -> str:
        """Validate OTP type."""
        allowed_types: set[str] = {"email", "sms", "phone_change"}
        if v.lower() not in allowed_types:
            raise ValueError(f'Type must be one of: {", ".join(sorted(allowed_types))}')
        return v.lower()


class MagicLinkRequest(BaseModel):
    """Schema for magic link request."""

    email: EmailStr
    redirect_to: Optional[str] = None

    @field_validator("redirect_to")
    @classmethod
    def validate_redirect_to(cls, v: Optional[str]) -> Optional[str]:
        """Validate redirect URL using comprehensive validation."""
        if v is None:
            return v

        # Use comprehensive URL validation with security checks
        sanitized_url: EmailStr = sanitize_url(
            v, 
            allowed_schemes=['https', 'http'],
            allow_localhost=True
        )
        
        if not sanitized_url:
            raise ValueError("Redirect URL must be a valid HTTP/HTTPS URL")

        return sanitized_url


class AdminUsersResponse(BaseModel):
    """Schema for admin users list response."""

    users: List[User]
    aud: str
    next_page: Optional[str] = None


class AdminUserCreateRequest(BaseModel):
    """Schema for admin user creation."""

    email: EmailStr
    password: Optional[str] = Field(None, min_length=8, max_length=128)
    email_confirm: bool = False
    phone_confirm: bool = False
    user_metadata: Optional[Dict[str, Any]] = None
    app_metadata: Optional[Dict[str, Any]] = None

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: Optional[str]) -> Optional[str]:
        """Validate password if provided using comprehensive validation."""
        if v is None:
            return v
        
        # Use comprehensive password validation
        is_valid, errors = validate_password_complexity(
            password=v,
            min_length=8,
            require_uppercase=True,
            require_lowercase=True,
            require_digits=True,
            require_special=True
        )
        
        if not is_valid:
            raise ValueError("; ".join(errors))
        
        return v

    @field_validator("user_metadata")
    @classmethod
    def validate_user_metadata(
        cls, v: Optional[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """Validate user metadata."""
        if v is None:
            return v

        # Limit metadata size
        if len(str(v)) > 1024:
            raise ValueError("User metadata too large (max 1024 characters)")

        # Ensure no sensitive fields in metadata
        forbidden_keys: set[str] = {"password", "token", "secret", "key"}
        if any(key.lower() in forbidden_keys for key in v.keys()):
            raise ValueError("Metadata cannot contain sensitive fields")

        return v

    @field_validator("app_metadata")
    @classmethod
    def validate_app_metadata(
        cls, v: Optional[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """Validate app metadata."""
        if v is None:
            return v

        # Limit metadata size
        if len(str(v)) > 2048:
            raise ValueError("App metadata too large (max 2048 characters)")

        return v


class AdminUserUpdateRequest(BaseModel):
    """Schema for admin user update."""

    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=6, max_length=128)
    email_confirm: Optional[bool] = None
    phone_confirm: Optional[bool] = None
    user_metadata: Optional[Dict[str, Any]] = None
    app_metadata: Optional[Dict[str, Any]] = None
    ban_duration: Optional[str] = None

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: Optional[str]) -> Optional[str]:
        """Validate password if provided."""
        if v is None:
            return v
        if not v.strip():
            raise ValueError("Password cannot be empty or just whitespace")

        # Apply complexity rules
        has_upper: bool = any(c.isupper() for c in v)
        has_lower: bool = any(c.islower() for c in v)
        has_digit: bool = any(c.isdigit() for c in v)
        has_special: bool = any(c in string.punctuation for c in v)

        if not (has_upper and has_lower and has_digit and has_special):
            raise ValueError(
                "Password must contain at least one uppercase letter, one lowercase letter, one digit, and one special character"
            )

        return v

    @field_validator("user_metadata")
    @classmethod
    def validate_user_metadata(
        cls, v: Optional[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """Validate user metadata."""
        if v is None:
            return v

        # Limit metadata size
        if len(str(v)) > 1024:
            raise ValueError("User metadata too large (max 1024 characters)")

        # Ensure no sensitive fields in metadata
        forbidden_keys: set[str] = {"password", "token", "secret", "key"}
        if any(key.lower() in forbidden_keys for key in v.keys()):
            raise ValueError("Metadata cannot contain sensitive fields")

        return v

    @field_validator("app_metadata")
    @classmethod
    def validate_app_metadata(
        cls, v: Optional[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """Validate app metadata."""
        if v is None:
            return v

        # Limit metadata size
        if len(str(v)) > 2048:
            raise ValueError("App metadata too large (max 2048 characters)")

        return v

    @field_validator("ban_duration")
    @classmethod
    def validate_ban_duration(cls, v: Optional[str]) -> Optional[str]:
        """Validate ban duration format."""
        if v is None:
            return v

        # Accept ISO 8601 duration format or 'none' to unban
        if v.lower() == "none":
            return v

        # Basic validation for ISO 8601 duration (P[n]DT[n]H[n]M[n]S)
        import re

        pattern = r"^P(?:\d+D)?(?:T(?:\d+H)?(?:\d+M)?(?:\d+S)?)?$"
        if not re.match(pattern, v.upper()):
            raise ValueError(
                'Ban duration must be in ISO 8601 format (e.g., P7D, PT24H) or "none" to unban'
            )

        return v


class ErrorResponse(BaseModel):
    """Schema for error responses."""

    error: str
    error_description: Optional[str] = None
    message: str


class SuccessResponse(BaseModel):
    """Schema for success responses."""

    message: str
    success: bool = True


class ProviderAuthRequest(BaseModel):
    """Schema for OAuth provider authentication."""

    provider: str = Field(
        ..., description="OAuth provider (google, github, discord, etc.)"
    )
    redirect_to: Optional[str] = None
    scopes: Optional[str] = None

    @field_validator("provider")
    @classmethod
    def validate_provider(cls, v: str) -> str:
        """Validate OAuth provider."""
        allowed_providers: set[str] = {
            "google",
            "github",
            "discord",
            "facebook",
            "twitter",
            "apple",
            "linkedin",
        }
        if v.lower() not in allowed_providers:
            raise ValueError(
                f'Provider must be one of: {", ".join(sorted(allowed_providers))}'
            )
        return v.lower()

    @field_validator("redirect_to")
    @classmethod
    def validate_redirect_to(cls, v: Optional[str]) -> Optional[str]:
        """Validate redirect URL."""
        if v is None:
            return v

        # Basic URL validation
        import re

        url_pattern = r"^https?://.+"
        if not re.match(url_pattern, v):
            raise ValueError("Redirect URL must be a valid HTTP/HTTPS URL")

        # Security: Prevent open redirects by checking against allowed domains
        # In production, you should maintain a whitelist of allowed redirect domains
        return v


class PhoneAuthRequest(BaseModel):
    """Schema for phone authentication."""

    phone: str = Field(..., description="Phone number in international format")

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        """Validate phone number format."""
        import re

        # Basic international phone number validation
        phone_pattern = r"^\+[1-9]\d{1,14}$"
        if not re.match(phone_pattern, v):
            raise ValueError(
                "Phone number must be in international format (e.g., +1234567890)"
            )
        return v


class PhoneVerificationRequest(BaseModel):
    """Schema for phone verification."""

    phone: str = Field(..., description="Phone number in international format")
    token: str = Field(..., min_length=4, max_length=10)

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        """Validate phone number format."""
        import re

        phone_pattern = r"^\+[1-9]\d{1,14}$"
        if not re.match(phone_pattern, v):
            raise ValueError("Phone number must be in international format")
        return v

    @field_validator("token")
    @classmethod
    def validate_token(cls, v: str) -> str:
        """Validate OTP token."""
        if not v.isdigit():
            raise ValueError("Token must contain only digits")
        return v
