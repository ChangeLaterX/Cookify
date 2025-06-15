"""
FastAPI Routes for Authentication Domain.
Provides HTTP endpoints for user authentication and profile management.
"""

import asyncio
import logging
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from .schemas import (
    UserLogin,
    UserCreate,
    TokenRefresh,
    PasswordReset,
    PasswordResetConfirm,
    PasswordChange,
    EmailVerification,
    ResendVerification,
    UserProfileUpdate,
    TokenResponse,
    UserResponse,
    UserProfileResponse,
    UserWithProfileResponse,
    MessageResponse,
    ErrorResponse,
    AuthUser,
    ApiResponse,
    AuthResponse,
    PasswordStrengthResponse,
    PasswordStrengthCheck,
    PasswordRequirement,
)
from .services import (
    authenticate_user,
    register_user,
    refresh_token,
    logout_user,
    get_user_profile,
    update_user_profile,
    AuthenticationError,
    request_password_reset,
    confirm_password_reset,
    change_password,
    verify_email,
    resend_verification_email,
)
from middleware.security import get_current_user, get_optional_user

from core.logging import get_logger
logger = get_logger(__name__)

# Create router for auth endpoints
router = APIRouter(prefix="/auth", tags=["Authentication"])

# Security scheme for bearer token
security = HTTPBearer()


@router.post(
    "/register",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
    summary="User Registration",
    description="Register new user with email and password via Supabase Auth",
)
async def register(user_data: UserCreate) -> AuthResponse:
    """
    Register new user and return access/refresh tokens.

    Args:
        user_data: User registration data (email, password, optional username)

    Returns:
        AuthResponse with access_token, refresh_token, and expiration info

    Raises:
        HTTPException: 409 if email already exists, 400 if validation fails
    """
    try:
        logger.info(f"Registration attempt for user: {user_data.email}")

        token_response = await register_user(user_data)

        logger.info(f"User {user_data.email} registered successfully")
        return AuthResponse(
            success=True,
            data=token_response,
            message="Registration successful",
            error=None,
        )

    except AuthenticationError as e:
        logger.warning(f"Registration failed for {user_data.email}: {e.message}")
        if e.error_code == "EMAIL_EXISTS":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={"error": e.message, "error_code": e.error_code},
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": e.message, "error_code": e.error_code},
        )
    except Exception as e:
        logger.error(
            f"Unexpected error during registration for {user_data.email}: {str(e)}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Internal server error", "error_code": "INTERNAL_ERROR"},
        )


@router.post(
    "/login",
    response_model=AuthResponse,
    status_code=status.HTTP_200_OK,
    summary="User Login",
    description="Authenticate user with email and password via Supabase Auth",
)
async def login(credentials: UserLogin) -> AuthResponse:
    """
    Authenticate user and return access/refresh tokens.

    Args:
        credentials: User login credentials (email, password)

    Returns:
        TokenResponse with access_token, refresh_token, and expiration info

    Raises:
        HTTPException: 401 if authentication fails
    """
    try:
        logger.info(f"Login attempt for user: {credentials.email}")

        token_response = await authenticate_user(credentials)

        logger.info(f"User {credentials.email} logged in successfully")
        return AuthResponse(
            success=True, data=token_response, message="Login successful", error=None
        )

    except AuthenticationError as e:
        logger.warning(f"Authentication failed for {credentials.email}: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": e.message, "error_code": e.error_code},
        )
    except Exception as e:
        logger.error(f"Unexpected error during login for {credentials.email}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Internal server error", "error_code": "INTERNAL_ERROR"},
        )


@router.post(
    "/refresh",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Refresh Token",
    description="Refresh access token using refresh token",
)
async def refresh_access_token(token_data: TokenRefresh) -> TokenResponse:
    """
    Refresh access token using valid refresh token.

    Args:
        token_data: Refresh token data

    Returns:
        TokenResponse with new access_token and refresh_token

    Raises:
        HTTPException: 401 if refresh token is invalid
    """
    try:
        logger.info("Token refresh attempt")

        token_response = await refresh_token(token_data.refresh_token)

        logger.info("Token refreshed successfully")
        return token_response

    except AuthenticationError as e:
        logger.warning(f"Token refresh failed: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": e.message, "error_code": e.error_code},
        )
    except Exception as e:
        logger.error(f"Unexpected error during token refresh: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Internal server error", "error_code": "INTERNAL_ERROR"},
        )


@router.post(
    "/logout",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="User Logout",
    description="Logout user and invalidate session",
)
async def logout(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> MessageResponse:
    """
    Logout user and invalidate current session.

    Args:
        credentials: Bearer token from Authorization header

    Returns:
        MessageResponse confirming logout
    """
    try:
        token = credentials.credentials
        success = await logout_user(token)

        if success:
            logger.info("User logged out successfully")
            return MessageResponse(message="Logged out successfully")
        else:
            logger.warning("Logout completed with warnings")
            return MessageResponse(
                message="Logged out (with warnings)",
                success=True,
                details={"warning": "Session may not have been fully invalidated"},
            )

    except Exception as e:
        logger.warning(f"Error during logout: {str(e)}")
        # Don't fail logout for errors - return success anyway
        return MessageResponse(
            message="Logged out (best effort)",
            success=True,
            details={
                "warning": "Logout completed but may not have been fully processed"
            },
        )


@router.get(
    "/me",
    response_model=UserWithProfileResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Current User",
    description="Get current user info from JWT token including profile data",
)
async def get_current_user_info(
    current_user: AuthUser = Depends(get_current_user),
) -> UserWithProfileResponse:
    """
    Get current authenticated user information with profile.

    Args:
        current_user: Current authenticated user from JWT token

    Returns:
        UserWithProfileResponse with user and profile data
    """
    try:
        logger.info(f"Getting user info for user: {current_user.id}")

        # Convert AuthUser to UserResponse
        user_response = UserResponse(
            id=current_user.id,
            email=current_user.email,
            is_active=current_user.is_active,
            is_verified=current_user.is_verified,
            created_at=datetime.utcnow(),  # Will be overridden if we fetch from DB
            updated_at=datetime.utcnow(),  # Will be overridden if we fetch from DB
        )

        return UserWithProfileResponse(user=user_response, profile=current_user.profile)

    except Exception as e:
        logger.error(f"Error getting current user info: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Failed to get user information",
                "error_code": "SERVICE_ERROR",
            },
        )


@router.get(
    "/profile",
    response_model=Optional[UserProfileResponse],
    status_code=status.HTTP_200_OK,
    summary="Get User Profile",
    description="Get current user's profile data",
)
async def get_profile(
    current_user: AuthUser = Depends(get_current_user),
) -> Optional[UserProfileResponse]:
    """
    Get current user's profile data.

    Args:
        current_user: Current authenticated user

    Returns:
        UserProfileResponse if profile exists, None otherwise
    """
    try:
        logger.info(f"Getting profile for user: {current_user.id}")

        profile = await get_user_profile(current_user.id)

        if profile:
            logger.info(f"Profile found for user: {current_user.id}")
        else:
            logger.info(f"No profile found for user: {current_user.id}")

        return profile

    except Exception as e:
        logger.error(f"Error getting user profile: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Failed to get user profile",
                "error_code": "SERVICE_ERROR",
            },
        )


@router.put(
    "/me",
    response_model=UserProfileResponse,
    status_code=status.HTTP_200_OK,
    summary="Update User Profile",
    description="Update current user's profile data",
)
async def update_current_user_profile(
    profile_data: UserProfileUpdate, current_user: AuthUser = Depends(get_current_user)
) -> UserProfileResponse:
    """
    Update current user's profile data.

    Args:
        profile_data: Profile update data
        current_user: Current authenticated user

    Returns:
        Updated UserProfileResponse

    Raises:
        HTTPException: 400 if update fails
    """
    try:
        logger.info(f"Updating profile for user: {current_user.id}")

        updated_profile = await update_user_profile(current_user.id, profile_data)

        logger.info(f"Profile updated successfully for user: {current_user.id}")
        return updated_profile

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating user profile: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Failed to update user profile",
                "error_code": "SERVICE_ERROR",
            },
        )


@router.post(
    "/forgot-password",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Request Password Reset",
    description="Request password reset email via Supabase",
)
async def forgot_password(reset_data: PasswordReset) -> MessageResponse:
    """
    Request password reset email.

    Args:
        reset_data: Password reset request data

    Returns:
        MessageResponse confirming request (always returns success for security)
    """
    try:
        logger.info(f"Password reset requested for email: {reset_data.email}")

        await request_password_reset(reset_data.email)

        return MessageResponse(
            message="If the email exists, a password reset link has been sent",
            success=True,
            details={"email": reset_data.email},
        )

    except Exception as e:
        logger.warning(f"Password reset request error: {str(e)}")
        # Always return success for security - don't reveal if email exists
        return MessageResponse(
            message="If the email exists, a password reset link has been sent",
            success=True,
            details={"email": reset_data.email},
        )


@router.post(
    "/reset-password",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Reset Password",
    description="Reset password with token from email",
)
async def reset_password(reset_data: PasswordResetConfirm) -> MessageResponse:
    """
    Reset password using token from email.

    Args:
        reset_data: Password reset confirmation data

    Returns:
        MessageResponse confirming password reset

    Raises:
        HTTPException: 400 if token is invalid
    """
    try:
        logger.info("Password reset confirmation attempt")

        success = await confirm_password_reset(reset_data)

        if success:
            logger.info("Password reset completed successfully")
            return MessageResponse(message="Password reset successfully", success=True)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"error": "Password reset failed", "error_code": "RESET_FAILED"},
            )

    except AuthenticationError as e:
        logger.warning(f"Password reset failed: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": e.message, "error_code": e.error_code},
        )
    except Exception as e:
        logger.error(f"Password reset error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Internal server error", "error_code": "INTERNAL_ERROR"},
        )


@router.post(
    "/verify-email",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Verify Email",
    description="Verify user email with token from email",
)
async def verify_user_email(verification_data: EmailVerification) -> MessageResponse:
    """
    Verify user email with verification token.

    Args:
        verification_data: Email verification data

    Returns:
        MessageResponse confirming email verification

    Raises:
        HTTPException: 400 if token is invalid
    """
    try:
        logger.info("Email verification attempt")

        success = await verify_email(verification_data)

        if success:
            logger.info("Email verified successfully")
            return MessageResponse(message="Email verified successfully", success=True)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": "Email verification failed",
                    "error_code": "VERIFICATION_FAILED",
                },
            )

    except AuthenticationError as e:
        logger.warning(f"Email verification failed: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": e.message, "error_code": e.error_code},
        )
    except Exception as e:
        logger.error(f"Email verification error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Internal server error", "error_code": "INTERNAL_ERROR"},
        )


@router.post(
    "/resend-verification",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Resend Verification Email",
    description="Resend email verification link",
)
async def resend_verification(resend_data: ResendVerification) -> MessageResponse:
    """
    Resend verification email to user.

    Args:
        resend_data: Resend verification data

    Returns:
        MessageResponse confirming email sent (always returns success for security)
    """
    try:
        logger.info(f"Resend verification requested for: {resend_data.email}")

        await resend_verification_email(resend_data.email)

        return MessageResponse(
            message="If the email is registered and unverified, a verification link has been sent",
            success=True,
            details={"email": resend_data.email},
        )

    except Exception as e:
        logger.warning(f"Resend verification error: {str(e)}")
        # Always return success for security
        return MessageResponse(
            message="If the email is registered and unverified, a verification link has been sent",
            success=True,
            details={"email": resend_data.email},
        )


@router.post(
    "/change-password",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Change Password",
    description="Change user password (requires current password)",
)
async def change_user_password(
    password_data: PasswordChange, current_user: AuthUser = Depends(get_current_user)
) -> MessageResponse:
    """
    Change user password.

    Args:
        password_data: Password change data (old and new password)
        current_user: Current authenticated user

    Returns:
        MessageResponse confirming password change

    Raises:
        HTTPException: 400 if current password is wrong
    """
    try:
        logger.info(f"Password change requested for user: {current_user.id}")

        success = await change_password(current_user.id, password_data)

        if success:
            logger.info(f"Password changed successfully for user: {current_user.id}")
            return MessageResponse(
                message="Password changed successfully",
                success=True,
                details={"user_id": str(current_user.id)},
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": "Password change failed",
                    "error_code": "CHANGE_FAILED",
                },
            )

    except AuthenticationError as e:
        logger.warning(f"Password change failed for {current_user.id}: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": e.message, "error_code": e.error_code},
        )
    except Exception as e:
        logger.error(f"Password change error for {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Internal server error", "error_code": "INTERNAL_ERROR"},
        )


@router.post(
    "/password-reset",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Request Password Reset (Legacy)",
    description="Legacy endpoint - use /forgot-password instead",
)
async def request_password_reset_legacy(reset_data: PasswordReset) -> MessageResponse:
    """
    Legacy password reset endpoint.

    Note: This endpoint is deprecated. Use /forgot-password instead.
    """
    return await forgot_password(reset_data)


@router.post(
    "/change-password",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Change Password (Legacy)",
    description="Legacy endpoint - use /change-password instead",
)
async def change_password_legacy(
    password_data: PasswordChange, current_user: AuthUser = Depends(get_current_user)
) -> MessageResponse:
    """
    Legacy password change endpoint.

    Note: This endpoint is deprecated but maintained for compatibility.
    """
    return await change_user_password(password_data, current_user)


# Optional user endpoint (for public pages that can show user info if logged in)
@router.get(
    "/user-info",
    response_model=Optional[UserResponse],
    status_code=status.HTTP_200_OK,
    summary="Get Optional User Info",
    description="Get user info if authenticated, returns None if not",
)
async def get_optional_user_info(
    current_user: Optional[AuthUser] = Depends(get_optional_user),
) -> Optional[UserResponse]:
    """
    Get user information if authenticated, None otherwise.

    Useful for pages that can optionally show user info without requiring authentication.

    Args:
        current_user: Optional current user from JWT token

    Returns:
        UserResponse if authenticated, None otherwise
    """
    if current_user:
        logger.info(f"Optional user info requested for user: {current_user.id}")
        return UserResponse(
            id=current_user.id,
            email=current_user.email,
            is_active=current_user.is_active,
            is_verified=current_user.is_verified,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
    else:
        logger.info("Optional user info requested - no user authenticated")
        return None


# Import datetime for responses
from datetime import datetime
from core.config import settings


# Development-only endpoint for testing
@router.post(
    "/dev-login",
    response_model=AuthResponse,
    summary="Development Test Login",
    description="Development-only endpoint to create test tokens without email verification",
    include_in_schema=settings.DEBUG,
)
async def dev_login() -> AuthResponse:
    """
    Create a test token for development purposes.
    Only available when DEBUG mode is enabled.
    """
    if not settings.DEBUG:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Endpoint not available in production",
        )

    # Create a mock token response for testing
    import jwt
    from datetime import datetime, timedelta

    # Mock user data
    user_data = {
        "user_id": "test-user-123",
        "email": "test@cookify.dev",
        "username": "test_user",
        "exp": datetime.utcnow() + timedelta(minutes=30),
    }

    # Create test tokens
    access_token = jwt.encode(
        user_data, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )
    refresh_token = jwt.encode(
        {**user_data, "exp": datetime.utcnow() + timedelta(days=7)},
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )

    logger.info("Development test login successful")

    return AuthResponse(
        success=True,
        data=TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=1800,
            expires_at=datetime.utcnow() + timedelta(minutes=30),
        ),
        message="Development test login successful",
    )


@router.post(
    "/check-password-strength",
    response_model=PasswordStrengthResponse,
    status_code=status.HTTP_200_OK,
    summary="Check Password Strength",
    description="Analyze password strength and get detailed feedback",
)
async def check_password_strength(
    strength_check: PasswordStrengthCheck,
    current_user: Optional[AuthUser] = Depends(get_optional_user),
) -> PasswordStrengthResponse:
    """
    Check password strength and provide detailed feedback.

    Args:
        strength_check: Password to analyze
        current_user: Optional current user for personalized checks

    Returns:
        PasswordStrengthResponse with detailed analysis
    """
    try:
        from shared.utils.password_security import (
            get_password_analysis,
            PasswordStrength,
        )

        # Prepare user info for personal information checks
        user_info = {}
        if current_user:
            user_info = {"email": current_user.email, "user_id": str(current_user.id)}
            if current_user.profile:
                profile_info = {}
                if current_user.profile.first_name:
                    profile_info["first_name"] = current_user.profile.first_name
                if current_user.profile.last_name:
                    profile_info["last_name"] = current_user.profile.last_name
                if current_user.profile.display_name:
                    profile_info["display_name"] = current_user.profile.display_name
                user_info.update(profile_info)

        # Analyze password
        analysis = get_password_analysis(strength_check.password, user_info)

        # Convert to response format
        strength_labels = {
            PasswordStrength.VERY_WEAK: "Very Weak",
            PasswordStrength.WEAK: "Weak",
            PasswordStrength.FAIR: "Fair",
            PasswordStrength.GOOD: "Good",
            PasswordStrength.STRONG: "Strong",
            PasswordStrength.VERY_STRONG: "Very Strong",
        }

        # Convert requirements to response format
        requirements = []
        requirement_descriptions = {
            "min_length": "At least 12 characters long",
            "max_length": "Not exceeding 128 characters",
            "uppercase": "Contains uppercase letters (A-Z)",
            "lowercase": "Contains lowercase letters (a-z)",
            "digits": "Contains numbers (0-9)",
            "special": "Contains special characters (!@#$%^&*)",
            "char_types": "Uses multiple character types",
            "unique_chars": "Has sufficient character variety",
            "repeated_chars": "Avoids excessive repetition",
            "no_common_patterns": "Avoids common patterns and sequences",
            "not_common": "Not a commonly used password",
            "no_personal_info": "Does not contain personal information",
        }

        for key, met in analysis.meets_requirements.items():
            description = requirement_descriptions.get(
                key, key.replace("_", " ").title()
            )
            requirements.append(
                PasswordRequirement(key=key, met=met, description=description)
            )

        return PasswordStrengthResponse(
            strength=int(analysis.strength),
            score=analysis.score,
            is_valid=analysis.is_valid,
            errors=analysis.errors,
            warnings=analysis.warnings,
            suggestions=analysis.suggestions,
            requirements=requirements,
            strength_label=strength_labels[analysis.strength],
        )

    except Exception as e:
        logger.error(f"Password strength check error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Internal server error", "error_code": "INTERNAL_ERROR"},
        )


# Export router
__all__: list[str] = ["router"]
