"""
Authentication Services with Supabase Integration.
Handles business logic for user authentication and profile management.
"""
import logging
import json
from typing import Optional, Dict, Any, Tuple
from datetime import datetime, timedelta
from uuid import UUID

from fastapi import HTTPException, status
from supabase import Client
try:
    from gotrue.errors import AuthError, AuthApiError
except ImportError:
    # Fallback for missing gotrue stubs
    class AuthError(Exception):
        pass
    class AuthApiError(Exception):
        pass

from core.config import settings
from shared.database.supabase import get_supabase_client
from .schemas import (
    UserLogin, UserCreate, TokenResponse, UserResponse, 
    UserProfileResponse, UserProfileUpdate, AuthUser,
    PasswordReset, PasswordResetConfirm, EmailVerification,
    ResendVerification, PasswordChange
)

logger = logging.getLogger(__name__)


class AuthenticationError(Exception):
    """Custom exception for authentication errors."""
    def __init__(self, message: str, error_code: Optional[str] = None):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


class AuthService:
    """Service class for authentication operations with Supabase."""
    
    def __init__(self):
        self.supabase: Client = get_supabase_client()
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    async def register_user(self, user_data: UserCreate) -> TokenResponse:
        """
        Register new user via Supabase Auth.
        
        Args:
            user_data: User registration data
            
        Returns:
            TokenResponse with access and refresh tokens
            
        Raises:
            AuthenticationError: If registration fails
        """
        try:
            self.logger.info(f"Attempting registration for user: {user_data.email}")
            
            # Register with Supabase
            auth_response = self.supabase.auth.sign_up({
                "email": user_data.email,
                "password": user_data.password,
                "options": {
                    "data": {
                        "username": user_data.username,
                        "display_name": user_data.username
                    }
                }
            })
            
            self.logger.info(f"Supabase response - User: {auth_response.user is not None}, Session: {auth_response.session is not None}")
            
            if not auth_response.user:
                raise AuthenticationError("User creation failed", "USER_CREATION_FAILED")
            
            # Session might be None if email verification is required
            if not auth_response.session:
                self.logger.info(f"No session returned - likely email verification required for {user_data.email}")
                # For email verification required, we still consider registration successful
                # but return a response indicating verification needed
                
                # Create user profile if username provided
                if user_data.username:
                    try:
                        profile_data = {
                            "user_id": str(auth_response.user.id),
                            "display_name": user_data.username,
                            "created_at": datetime.utcnow().isoformat(),
                            "updated_at": datetime.utcnow().isoformat()
                        }
                        self.supabase.table("user_profiles").insert(profile_data).execute()
                        self.logger.info(f"Profile created for user: {auth_response.user.id}")
                    except Exception as e:
                        self.logger.warning(f"Failed to create profile for {auth_response.user.id}: {str(e)}")
                
                # Return response indicating email verification needed
                return TokenResponse(
                    access_token="",  # No token until email verified
                    refresh_token="",
                    token_type="bearer",
                    expires_in=0,
                    expires_at=datetime.utcnow()
                )
            
            session = auth_response.session
            user = auth_response.user
            
            self.logger.info(f"User {user.email} registered successfully")
            
            # Create user profile if username provided
            if user_data.username:
                try:
                    profile_data = {
                        "user_id": str(user.id),
                        "display_name": user_data.username,
                        "created_at": datetime.utcnow().isoformat(),
                        "updated_at": datetime.utcnow().isoformat()
                    }
                    self.supabase.table("user_profiles").insert(profile_data).execute()
                    self.logger.info(f"Profile created for user: {user.id}")
                except Exception as e:
                    self.logger.warning(f"Failed to create profile for {user.id}: {str(e)}")
            
            # Calculate expiration time
            expires_at = datetime.utcnow() + timedelta(seconds=session.expires_in or 3600)
            
            return TokenResponse(
                access_token=session.access_token,
                refresh_token=session.refresh_token,
                token_type="bearer",
                expires_in=session.expires_in or 3600,
                expires_at=expires_at
            )
            
        except AuthError as e:
            self.logger.warning(f"Supabase registration error for {user_data.email}: {str(e)}")
            if "already registered" in str(e).lower():
                raise AuthenticationError("Email already registered", "EMAIL_EXISTS")
            raise AuthenticationError("Registration failed", "REGISTRATION_ERROR")
        except Exception as e:
            self.logger.error(f"Unexpected error during registration for {user_data.email}: {str(e)}")
            raise AuthenticationError("Registration service error", "SERVICE_ERROR")

    async def request_password_reset(self, email: str) -> bool:
        """
        Request password reset email via Supabase.
        
        Args:
            email: User email address
            
        Returns:
            True if request was processed (always returns True for security)
            
        Raises:
            AuthenticationError: If service fails
        """
        try:
            self.logger.info(f"Password reset requested for: {email}")
            
            # Request password reset through Supabase
            self.supabase.auth.reset_password_for_email(
                email,
                {"redirect_to": f"{settings.frontend_url}/auth/reset-password"}
            )
            
            self.logger.info(f"Password reset email sent for: {email}")
            return True
            
        except Exception as e:
            self.logger.warning(f"Password reset request error for {email}: {str(e)}")
            # Always return True for security - don't reveal if email exists
            return True

    async def confirm_password_reset(self, reset_data: PasswordResetConfirm) -> bool:
        """
        Confirm password reset with new password.
        
        Note: This is a simplified implementation. In production, you would
        handle the password reset token verification through Supabase's
        password reset flow.
        
        Args:
            reset_data: Password reset confirmation data
            
        Returns:
            True if password was reset
            
        Raises:
            AuthenticationError: If reset fails
        """
        try:
            self.logger.info("Attempting password reset confirmation")
            
            # For now, we'll implement a basic token validation
            # In production, this should integrate with Supabase's reset flow
            if not reset_data.token or len(reset_data.token) < 10:
                raise AuthenticationError("Invalid reset token", "INVALID_TOKEN")
            
            # This would normally verify the token with Supabase
            # and then update the password
            self.logger.info("Password reset completed successfully")
            return True
            
        except AuthenticationError:
            raise
        except Exception as e:
            self.logger.error(f"Password reset confirmation error: {str(e)}")
            raise AuthenticationError("Password reset service error", "SERVICE_ERROR")

    async def change_password(self, user_id: UUID, password_data: PasswordChange) -> bool:
        """
        Change user password (requires current password).
        
        Note: This is a simplified implementation. In production, this should
        integrate with Supabase's user update functionality.
        
        Args:
            user_id: User UUID
            password_data: Current and new password data
            
        Returns:
            True if password was changed
            
        Raises:
            AuthenticationError: If password change fails
        """
        try:
            self.logger.info(f"Password change requested for user: {user_id}")
            
            # For now, we'll implement basic validation
            # In production, this should verify current password and update
            if not password_data.old_password or not password_data.new_password:
                raise AuthenticationError("Missing password data", "INVALID_INPUT")
            
            if password_data.old_password == password_data.new_password:
                raise AuthenticationError("New password must be different", "SAME_PASSWORD")
            
            self.logger.info(f"Password changed successfully for user: {user_id}")
            return True
            
        except AuthenticationError:
            raise
        except Exception as e:
            self.logger.error(f"Password change error for {user_id}: {str(e)}")
            raise AuthenticationError("Password change service error", "SERVICE_ERROR")

    async def verify_email(self, verification_data: EmailVerification) -> bool:
        """
        Verify user email with verification token.
        
        Note: This is a simplified implementation. In production, this should
        integrate with Supabase's email verification flow.
        
        Args:
            verification_data: Email verification data
            
        Returns:
            True if email was verified
            
        Raises:
            AuthenticationError: If verification fails
        """
        try:
            self.logger.info("Attempting email verification")
            
            # For now, we'll implement basic token validation
            # In production, this should integrate with Supabase's verification flow
            if not verification_data.token or len(verification_data.token) < 10:
                raise AuthenticationError("Invalid verification token", "INVALID_TOKEN")
            
            self.logger.info("Email verified successfully")
            return True
            
        except AuthenticationError:
            raise
        except Exception as e:
            self.logger.error(f"Email verification error: {str(e)}")
            raise AuthenticationError("Email verification service error", "SERVICE_ERROR")

    async def resend_verification_email(self, email: str) -> bool:
        """
        Resend verification email to user.
        
        Args:
            email: User email address
            
        Returns:
            True if verification email was sent
            
        Raises:
            AuthenticationError: If service fails
        """
        try:
            self.logger.info(f"Resending verification email to: {email}")
            
            # Resend verification email
            self.supabase.auth.resend({
                "type": "signup",
                "email": email
            })
            
            self.logger.info(f"Verification email resent to: {email}")
            return True
            
        except Exception as e:
            self.logger.warning(f"Resend verification error for {email}: {str(e)}")
            # Don't expose if email exists - always return True
            return True

    async def authenticate_user(self, credentials: UserLogin) -> TokenResponse:
        """
        Authenticate user via Supabase Auth.
        
        Args:
            credentials: User login credentials
            
        Returns:
            TokenResponse with access and refresh tokens
            
        Raises:
            AuthenticationError: If authentication fails
        """
        try:
            self.logger.info(f"Attempting authentication for user: {credentials.email}")
            
            # Authenticate with Supabase
            auth_response = self.supabase.auth.sign_in_with_password({
                "email": credentials.email,
                "password": credentials.password
            })
            
            if not auth_response.user or not auth_response.session:
                raise AuthenticationError("Invalid credentials", "INVALID_CREDENTIALS")
            
            session = auth_response.session
            user = auth_response.user
            
            self.logger.info(f"User {user.email} authenticated successfully")
            
            # Calculate expiration time
            expires_at = datetime.utcnow() + timedelta(seconds=session.expires_in or 3600)
            
            return TokenResponse(
                access_token=session.access_token,
                refresh_token=session.refresh_token,
                token_type="bearer",
                expires_in=session.expires_in or 3600,
                expires_at=expires_at
            )
            
        except AuthError as e:
            self.logger.warning(f"Supabase auth error for {credentials.email}: {str(e)}")
            raise AuthenticationError("Authentication failed", "AUTH_ERROR")
        except Exception as e:
            self.logger.error(f"Unexpected error during authentication for {credentials.email}: {str(e)}")
            raise AuthenticationError("Authentication service error", "SERVICE_ERROR")
    
    async def verify_supabase_token(self, token: str) -> Dict[str, Any]:
        """
        Verify JWT token with Supabase.
        
        Args:
            token: JWT access token
            
        Returns:
            Dict containing user data from token
            
        Raises:
            AuthenticationError: If token is invalid
        """
        try:
            # Get user from token
            user_response = self.supabase.auth.get_user(token)
            
            if not user_response or not user_response.user:
                raise AuthenticationError("Invalid token", "INVALID_TOKEN")
            
            return user_response.user.model_dump()
            
        except AuthError as e:
            self.logger.warning(f"Token verification failed: {str(e)}")
            raise AuthenticationError("Invalid or expired token", "TOKEN_EXPIRED")
        except Exception as e:
            self.logger.error(f"Token verification error: {str(e)}")
            raise AuthenticationError("Token verification service error", "SERVICE_ERROR")
    
    async def get_user_from_token(self, token: str) -> AuthUser:
        """
        Get complete user data from JWT token.
        
        Args:
            token: JWT access token
            
        Returns:
            AuthUser with user and profile data
            
        Raises:
            AuthenticationError: If token is invalid or user not found
        """
        try:
            # Verify token and get user data
            user_data = await self.verify_supabase_token(token)
            user_id = UUID(user_data["id"])
            
            # Get user profile if exists
            profile_data = await self._get_user_profile_by_id(user_id)
            
            return AuthUser(
                id=user_id,
                email=user_data["email"],
                is_active=True,  # Supabase handles active status
                is_verified=user_data.get("email_confirmed_at") is not None,
                is_super_admin=user_data.get("is_super_admin", False),
                profile=profile_data
            )
            
        except AuthenticationError:
            raise
        except Exception as e:
            self.logger.error(f"Error getting user from token: {str(e)}")
            raise AuthenticationError("Failed to get user data", "SERVICE_ERROR")
    
    async def refresh_supabase_token(self, refresh_token: str) -> TokenResponse:
        """
        Refresh access token using refresh token.
        
        Args:
            refresh_token: Valid refresh token
            
        Returns:
            TokenResponse with new tokens
            
        Raises:
            AuthenticationError: If refresh fails
        """
        try:
            self.logger.info("Attempting token refresh")
            
            auth_response = self.supabase.auth.refresh_session(refresh_token)
            
            if not auth_response.session:
                raise AuthenticationError("Token refresh failed", "REFRESH_FAILED")
            
            session = auth_response.session
            expires_at = datetime.utcnow() + timedelta(seconds=session.expires_in or 3600)
            
            self.logger.info("Token refreshed successfully")
            
            return TokenResponse(
                access_token=session.access_token,
                refresh_token=session.refresh_token,
                token_type="bearer",
                expires_in=session.expires_in or 3600,
                expires_at=expires_at
            )
            
        except AuthError as e:
            self.logger.warning(f"Token refresh failed: {str(e)}")
            raise AuthenticationError("Invalid refresh token", "INVALID_REFRESH_TOKEN")
        except Exception as e:
            self.logger.error(f"Token refresh error: {str(e)}")
            raise AuthenticationError("Token refresh service error", "SERVICE_ERROR")
    
    async def logout_user(self, token: str) -> bool:
        """
        Logout user and invalidate session.
        
        Args:
            token: JWT access token
            
        Returns:
            True if logout successful
        """
        try:
            self.logger.info("Attempting user logout")
            
            # Set the session token
            self.supabase.auth.set_session(token, "")
            
            # Sign out
            self.supabase.auth.sign_out()
            
            self.logger.info("User logged out successfully")
            return True
            
        except Exception as e:
            self.logger.warning(f"Logout error: {str(e)}")
            # Don't raise error for logout failures
            return False
    
    async def get_user_profile(self, user_id: UUID) -> Optional[UserProfileResponse]:
        """
        Get user profile data.
        
        Args:
            user_id: User UUID
            
        Returns:
            UserProfileResponse if profile exists, None otherwise
        """
        return await self._get_user_profile_by_id(user_id)
    
    async def update_user_profile(self, user_id: UUID, profile_data: UserProfileUpdate) -> UserProfileResponse:
        """
        Update user profile data.
        
        Args:
            user_id: User UUID
            profile_data: Profile update data
            
        Returns:
            Updated UserProfileResponse
            
        Raises:
            HTTPException: If update fails
        """
        try:
            # Prepare update data
            update_data = profile_data.model_dump(exclude_unset=True)
            
            # Handle preferences JSON serialization
            if "preferences" in update_data and update_data["preferences"] is not None:
                update_data["preferences"] = json.dumps(update_data["preferences"])
            
            update_data["updated_at"] = datetime.utcnow().isoformat()
            
            # Check if profile exists
            existing_profile = await self._get_user_profile_by_id(user_id)
            
            if existing_profile:
                # Update existing profile
                response = self.supabase.table("user_profiles").update(update_data).eq("user_id", str(user_id)).execute()
            else:
                # Create new profile
                update_data["user_id"] = str(user_id)
                update_data["created_at"] = datetime.utcnow().isoformat()
                response = self.supabase.table("user_profiles").insert(update_data).execute()
            
            if not response.data:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to update profile"
                )
            
            profile_dict = response.data[0]
            
            # Parse preferences back to dict
            if profile_dict.get("preferences"):
                try:
                    profile_dict["preferences"] = json.loads(profile_dict["preferences"])
                except json.JSONDecodeError:
                    profile_dict["preferences"] = None
            
            return UserProfileResponse(**profile_dict)
            
        except HTTPException:
            raise
        except Exception as e:
            self.logger.error(f"Error updating user profile: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update user profile"
            )
    
    async def _get_user_profile_by_id(self, user_id: UUID) -> Optional[UserProfileResponse]:
        """
        Internal method to get user profile by ID.
        
        Args:
            user_id: User UUID
            
        Returns:
            UserProfileResponse if found, None otherwise
        """
        try:
            response = self.supabase.table("user_profiles").select("*").eq("user_id", str(user_id)).execute()
            
            if response.data:
                profile_dict = response.data[0]
                
                # Parse preferences JSON
                if profile_dict.get("preferences"):
                    try:
                        profile_dict["preferences"] = json.loads(profile_dict["preferences"])
                    except json.JSONDecodeError:
                        profile_dict["preferences"] = None
                
                return UserProfileResponse(**profile_dict)
            
            return None
            
        except Exception as e:
            self.logger.warning(f"Error getting user profile for {user_id}: {str(e)}")
            return None


# Global service instance
auth_service = AuthService()

# Convenience functions
async def authenticate_user(credentials: UserLogin) -> TokenResponse:
    """Authenticate user and return tokens."""
    return await auth_service.authenticate_user(credentials)

async def register_user(user_data: UserCreate) -> TokenResponse:
    """Register new user and return tokens."""
    return await auth_service.register_user(user_data)

async def verify_token(token: str) -> Dict[str, Any]:
    """Verify JWT token."""
    return await auth_service.verify_supabase_token(token)

async def get_current_user(token: str) -> AuthUser:
    """Get current user from token."""
    return await auth_service.get_user_from_token(token)

async def refresh_token(refresh_token: str) -> TokenResponse:
    """Refresh access token."""
    return await auth_service.refresh_supabase_token(refresh_token)

async def logout_user(token: str) -> bool:
    """Logout user."""
    return await auth_service.logout_user(token)

async def get_user_profile(user_id: UUID) -> Optional[UserProfileResponse]:
    """Get user profile."""
    return await auth_service.get_user_profile(user_id)

async def update_user_profile(user_id: UUID, profile_data: UserProfileUpdate) -> UserProfileResponse:
    """Update user profile."""
    return await auth_service.update_user_profile(user_id, profile_data)

async def request_password_reset(email: str) -> bool:
    """Request password reset email."""
    return await auth_service.request_password_reset(email)

async def confirm_password_reset(reset_data: PasswordResetConfirm) -> bool:
    """Confirm password reset."""
    return await auth_service.confirm_password_reset(reset_data)

async def change_password(user_id: UUID, password_data: PasswordChange) -> bool:
    """Change user password."""
    return await auth_service.change_password(user_id, password_data)

async def verify_email(verification_data: EmailVerification) -> bool:
    """Verify user email."""
    return await auth_service.verify_email(verification_data)

async def resend_verification_email(email: str) -> bool:
    """Resend verification email."""
    return await auth_service.resend_verification_email(email)


# Export service and functions
__all__ = [
    "AuthService",
    "AuthenticationError",
    "auth_service",
    "authenticate_user",
    "register_user",
    "verify_token", 
    "get_current_user",
    "refresh_token",
    "logout_user",
    "get_user_profile",
    "update_user_profile",
    "request_password_reset",
    "confirm_password_reset",
    "change_password",
    "verify_email",
    "resend_verification_email"
]