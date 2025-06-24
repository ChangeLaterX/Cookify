"""
Mock Utilities for Auth Testing.

This module provides mock factories and context managers for Auth tests.
"""

import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from unittest.mock import MagicMock, Mock, patch

from domains.auth.schemas import TokenResponse, UserCreate, UserLogin, UserResponse


class AuthMockFactory:
    """Factory for creating Auth-related mocks."""

    @staticmethod
    def create_user_create(
        email: Optional[str] = None,
        password: Optional[str] = None,
        username: Optional[str] = None,
    ) -> UserCreate:
        """Create a mock UserCreate schema."""
        return UserCreate(
            email=email or f"test_{uuid.uuid4().hex[:8]}@test.cookify.app",
            password=password or "SecurePassword123!",
            username=username or f"testuser_{uuid.uuid4().hex[:6]}",
        )

    @staticmethod
    def create_user_login(email: Optional[str] = None, password: Optional[str] = None) -> UserLogin:
        """Create a mock UserLogin schema."""
        return UserLogin(
            email=email or "test@test.cookify.app",
            password=password or "SecurePassword123!",
        )

    @staticmethod
    def create_token_response(
        access_token: Optional[str] = None,
        refresh_token: Optional[str] = None,
        expires_in: int = 3600,
    ) -> TokenResponse:
        """Create a mock TokenResponse."""
        return TokenResponse(
            access_token=access_token or f"mock_access_token_{uuid.uuid4().hex[:8]}",
            refresh_token=refresh_token or f"mock_refresh_token_{uuid.uuid4().hex[:8]}",
            token_type="bearer",
            expires_in=expires_in,
            user=AuthMockFactory.create_user_response(),
        )

    @staticmethod
    def create_user_response(
        user_id: Optional[str] = None,
        email: Optional[str] = None,
        username: Optional[str] = None,
    ) -> UserResponse:
        """Create a mock UserResponse."""
        return UserResponse(
            id=user_id or str(uuid.uuid4()),
            email=email or "test@test.cookify.app",
            username=username or "testuser",
            email_verified=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

    @staticmethod
    def create_supabase_user_dict(
        user_id: Optional[str] = None,
        email: Optional[str] = None,
        username: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a mock Supabase user dictionary."""
        return {
            "id": user_id or str(uuid.uuid4()),
            "email": email or "test@test.cookify.app",
            "user_metadata": {
                "username": username or "testuser",
                "display_name": username or "testuser",
            },
            "email_confirmed_at": datetime.utcnow().isoformat(),
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "aud": "authenticated",
            "role": "authenticated",
        }

    @staticmethod
    def create_supabase_session_dict(
        access_token: Optional[str] = None,
        refresh_token: Optional[str] = None,
        expires_in: int = 3600,
    ) -> Dict[str, Any]:
        """Create a mock Supabase session dictionary."""
        return {
            "access_token": access_token or f"mock_access_token_{uuid.uuid4().hex[:8]}",
            "refresh_token": refresh_token or f"mock_refresh_token_{uuid.uuid4().hex[:8]}",
            "expires_in": expires_in,
            "token_type": "bearer",
            "expires_at": (datetime.utcnow() + timedelta(seconds=expires_in)).timestamp(),
        }

    @staticmethod
    def create_supabase_response(
        success: bool = True,
        user_data: Optional[Dict[str, Any]] = None,
        session_data: Optional[Dict[str, Any]] = None,
        error_message: Optional[str] = None,
    ) -> Mock:
        """Create a mock Supabase response object."""
        response = Mock()

        if success:
            response.user = Mock()
            response.user.__dict__.update(user_data or AuthMockFactory.create_supabase_user_dict())

            response.session = Mock()
            response.session.__dict__.update(
                session_data or AuthMockFactory.create_supabase_session_dict()
            )
        else:
            response.user = None
            response.session = None

        return response

    @staticmethod
    def create_auth_error(
        message: str = "Authentication failed",
        status_code: int = 400,
        error_code: str = "auth_error",
    ) -> Exception:
        """Create a mock authentication error."""

        # Use a simple fallback implementation for tests
        class MockAuthError(Exception):
            def __init__(self, message: str, code: str = error_code, status: int = status_code):
                self.message = message
                self.status = status
                self.code = code
                self.error_code = code  # Some tests might expect this attribute
                super().__init__(message)

        return MockAuthError(message, error_code, status_code)


class MockContextManager:
    """Context manager for setting up Auth mocks."""

    def __init__(
        self,
        mock_supabase: bool = True,
        mock_dependencies: bool = True,
        success_responses: bool = True,
    ):
        self.mock_supabase = mock_supabase
        self.mock_dependencies = mock_dependencies
        self.success_responses = success_responses
        self.patches = []

    def __enter__(self):
        """Setup mocks when entering context."""
        if self.mock_dependencies:
            # Mock core dependencies
            self.patches.append(
                patch(
                    "domains.auth.services.get_supabase_client",
                    return_value=self._create_mock_supabase_client(),
                )
            )

        if self.mock_supabase:
            # Mock Supabase client
            self.patches.append(
                patch(
                    "shared.database.supabase.get_supabase_client",
                    return_value=self._create_mock_supabase_client(),
                )
            )

        # Start all patches
        for p in self.patches:
            p.start()

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Cleanup mocks when exiting context."""
        for p in self.patches:
            p.stop()

    def _create_mock_supabase_client(self) -> Mock:
        """Create a mock Supabase client."""
        client = Mock()

        # Mock auth operations
        client.auth = Mock()

        if self.success_responses:
            client.auth.sign_up.return_value = AuthMockFactory.create_supabase_response()
            client.auth.sign_in_with_password.return_value = (
                AuthMockFactory.create_supabase_response()
            )
            client.auth.sign_out.return_value = Mock(error=None)
            client.auth.refresh_session.return_value = AuthMockFactory.create_supabase_response()
        else:
            client.auth.sign_up.side_effect = AuthMockFactory.create_auth_error(
                "Registration failed"
            )
            client.auth.sign_in_with_password.side_effect = AuthMockFactory.create_auth_error(
                "Login failed"
            )

        # Mock table operations
        client.table.return_value = self._create_mock_table()

        return client

    def _create_mock_table(self) -> Mock:
        """Create a mock Supabase table."""
        table = Mock()

        # Mock query operations
        query = Mock()

        if self.success_responses:
            query.execute.return_value = Mock(
                data=[{"id": "123", "username": "testuser"}], error=None
            )
        else:
            query.execute.return_value = Mock(data=None, error="Database error")

        table.insert.return_value = query
        table.select.return_value = query
        table.update.return_value = query
        table.eq.return_value = query

        return table


def with_mocked_auth(success: bool = True):
    """Decorator for mocking Auth dependencies in tests."""

    def decorator(test_func):
        def wrapper(*args, **kwargs):
            with MockContextManager(success_responses=success):
                return test_func(*args, **kwargs)

        return wrapper

    return decorator


class MockRateLimiter:
    """Mock rate limiter for testing."""

    def __init__(self, allow_requests: bool = True):
        self.allow_requests = allow_requests
        self.request_count = 0

    async def check_rate_limit(self, identifier: str) -> bool:
        """Mock rate limit check."""
        self.request_count += 1
        return self.allow_requests

    def reset(self):
        """Reset the mock rate limiter."""
        self.request_count = 0


class MockEmailService:
    """Mock email service for testing."""

    def __init__(self, send_success: bool = True):
        self.send_success = send_success
        self.sent_emails = []

    async def send_verification_email(self, email: str, token: str) -> bool:
        """Mock sending verification email."""
        self.sent_emails.append(
            {
                "type": "verification",
                "email": email,
                "token": token,
                "sent_at": datetime.utcnow(),
            }
        )
        return self.send_success

    async def send_password_reset_email(self, email: str, token: str) -> bool:
        """Mock sending password reset email."""
        self.sent_emails.append(
            {
                "type": "password_reset",
                "email": email,
                "token": token,
                "sent_at": datetime.utcnow(),
            }
        )
        return self.send_success
