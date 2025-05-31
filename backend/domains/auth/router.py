"""
Refactored authentication router with better structure and error handling.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPAuthorizationCredentials
from typing import Dict, Any

from .schemas import (
    UserSignUpRequest, UserSignInRequest, AuthResponse, 
    User, TokenRefreshRequest, PasswordResetRequest,
    UserUpdateRequest, SuccessResponse, OTPVerificationRequest,
    MagicLinkRequest
)
from .service import auth_service
from .dependencies import get_current_user, get_verified_user, require_admin
from .types import TokenType
from core.exceptions import ValidationError, AuthenticationError
from core.security import security
from middleware.rate_limit import rate_limit

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/signup", response_model=AuthResponse)
async def sign_up(user_data: UserSignUpRequest) -> AuthResponse:
    """
    Register a new user with email and password.
    
    - **email**: Valid email address
    - **password**: Password (minimum 6 characters)
    - **user_metadata**: Optional additional user data
    """
    return await auth_service.sign_up(
        email=user_data.email,
        password=user_data.password,
        metadata=user_data.user_metadata
    )


@router.post("/signin", response_model=AuthResponse, dependencies=[Depends(rate_limit(max_calls=5, period=300))])
async def sign_in(credentials: UserSignInRequest) -> AuthResponse:
    """
    Sign in user with email and password.
    Rate limited to 5 attempts per 5 minutes per IP.
    
    - **email**: User's email address
    - **password**: User's password
    
    Returns access token and user information.
    """
    return await auth_service.sign_in(
        email=credentials.email,
        password=credentials.password
    )


@router.post("/signout", response_model=SuccessResponse)
async def sign_out() -> SuccessResponse:
    """
    Sign out the current user.
    Invalidates the current session.
    """
    success: bool = await auth_service.sign_out()
    return SuccessResponse(
        message="Successfully signed out" if success else "Sign out completed",
        success=success
    )


@router.post("/refresh", response_model=AuthResponse)
async def refresh_token(refresh_data: TokenRefreshRequest) -> AuthResponse:
    """
    Refresh access token using refresh token.
    
    - **refresh_token**: Valid refresh token
    
    Returns new access token and user information.
    """
    return await auth_service.refresh_token(refresh_data.refresh_token)


@router.get("/me", response_model=User)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Get current user information.
    Requires valid access token.
    """
    return current_user


@router.put("/me", response_model=User)
async def update_current_user(
    user_data: UserUpdateRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security.required),
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Update current user profile.
    
    - **email**: New email address (optional)
    - **user_metadata**: Updated user metadata (optional)
    """
    # Use properly validated token from security dependency
    access_token: str = credentials.credentials
    return await auth_service.update_user(access_token, user_data)


@router.post("/password-reset", response_model=SuccessResponse, dependencies=[Depends(rate_limit(max_calls=3, period=600))])
async def request_password_reset(reset_request: PasswordResetRequest) -> SuccessResponse:
    """
    Request password reset email.
    Rate limited to 3 attempts per 10 minutes per IP.
    
    - **email**: User's email address
    
    Sends password reset email if account exists.
    """
    success: bool = await auth_service.reset_password_request(reset_request.email)
    return SuccessResponse(
        message="Password reset email sent if account exists",
        success=success
    )


@router.post("/verify-otp", response_model=AuthResponse, dependencies=[Depends(rate_limit(max_calls=10, period=600))])
async def verify_otp(otp_data: OTPVerificationRequest) -> AuthResponse:
    """
    Verify OTP token.
    Rate limited to 10 attempts per 10 minutes per IP.
    
    - **email**: User's email address
    - **token**: OTP token received via email/SMS
    - **type**: Type of OTP (signup, recovery, email_change, etc.)
    """
    try:
        token_type = TokenType(otp_data.type)
    except ValueError:
        raise ValidationError(f"Invalid token type: {otp_data.type}")
    
    return await auth_service.verify_otp(
        email=otp_data.email,
        token=otp_data.token,
        token_type=token_type
    )


@router.post("/resend-confirmation", response_model=SuccessResponse, dependencies=[Depends(rate_limit(max_calls=3, period=600))])
async def resend_confirmation_email(email_request: PasswordResetRequest) -> SuccessResponse:
    """
    Resend email confirmation.
    Rate limited to 3 attempts per 10 minutes per IP.
    
    - **email**: User's email address
    """
    success = await auth_service.resend_confirmation(email_request.email)
    return SuccessResponse(
        message="Confirmation email sent if account exists",
        success=success
    )


@router.post("/magic-link", response_model=SuccessResponse, dependencies=[Depends(rate_limit(max_calls=3, period=600))])
async def send_magic_link(magic_link_request: MagicLinkRequest) -> SuccessResponse:
    """
    Send magic link for passwordless authentication.
    Rate limited to 3 attempts per 10 minutes per IP.
    
    - **email**: User's email address
    - **redirect_to**: Optional redirect URL after authentication
    """
    success: bool = await auth_service.send_magic_link(
        email=magic_link_request.email,
        redirect_to=magic_link_request.redirect_to
    )
    
    return SuccessResponse(
        message="Magic link sent if account exists",
        success=success
    )


@router.get("/session")
async def get_session_info(
    current_user: User = Depends(get_verified_user)
) -> Dict[str, Any]:
    """
    Get current session information.
    Returns user info and session status.
    Requires verified email.
    """
    return {
        "authenticated": True,
        "user": current_user,
        "session_active": True,
        "email_verified": current_user.email_confirmed_at is not None,
        "role": current_user.app_metadata.get("role", "user")
    }


@router.delete("/account", response_model=SuccessResponse)
async def delete_account(
    credentials: HTTPAuthorizationCredentials = Depends(security.required),
    current_user: User = Depends(get_current_user)
) -> SuccessResponse:
    """
    Delete current user account.
    This is a destructive operation and cannot be undone.
    """
    # Use properly validated token from security dependency
    access_token: str = credentials.credentials
    success: bool = await auth_service.delete_user(access_token)
    
    return SuccessResponse(
        message="Account deletion initiated" if success else "Account deletion failed",
        success=success
    )


# Admin endpoints
@router.get("/admin/users")
async def list_users(
    admin_user: User = Depends(require_admin)
) -> Dict[str, Any]:
    """
    List all users (admin only).
    """
    # This would require implementing admin functionality in the service
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Admin user management not yet implemented"
    )


@router.get("/health")
async def auth_health_check() -> Dict[str, str]:
    """
    Health check endpoint for the auth service.
    """
    return {
        "status": "healthy",
        "service": "auth",
        "version": "2.0"
    }
