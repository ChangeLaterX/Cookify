"""
Unit Tests for User Authentication Functionality.

This module tests user login/logout logic in the Auth service.
"""

from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest
from domains.auth.schemas import TokenResponse, UserLogin
from domains.auth.services import AuthenticationError, AuthService
from tests.auth.config import AuthTestBase
from tests.auth.utils.mocks import (AuthMockFactory, MockContextManager,
                                    with_mocked_auth)
from tests.auth.utils.test_data import TestDataGenerator, TestScenarios


class TestUserAuthentication(AuthTestBase):
    """Test user authentication functionality."""

    def test_main_functionality(self):
        """Required by AuthTestBase - tests basic authentication."""
        self.test_successful_user_login()

    @pytest.mark.asyncio
    async def test_successful_user_login(self):
        """Test successful user login flow."""
        with MockContextManager(success_responses=True) as mock_ctx:
            service = AuthService()
            user_data = TestDataGenerator.generate_user_data()

            # Mock successful Supabase login response
            mock_response = AuthMockFactory.create_supabase_response(
                success=True,
                user_data=TestDataGenerator.generate_supabase_user_dict(user_data),
            )
            service.supabase.auth.sign_in_with_password.return_value = mock_response

            # Test login
            result = await service.authenticate_user(user_data.to_user_login())

            # Verify result
            assert isinstance(result, TokenResponse)
            assert result.access_token is not None
            assert result.refresh_token is not None
            assert result.token_type == "bearer"
            assert result.expires_in > 0
            assert result.expires_at is not None

    @pytest.mark.asyncio
    async def test_login_with_invalid_credentials(self):
        """Test login with invalid credentials."""
        with MockContextManager(success_responses=False) as mock_ctx:
            service = AuthService()

            # Mock Supabase auth error for invalid credentials
            auth_error = AuthMockFactory.create_auth_error("Invalid credentials", 401)
            service.supabase.auth.sign_in_with_password.side_effect = auth_error

            login_data = UserLogin(email="test@example.com", password="wrongpassword")

            # Test login should fail
            with pytest.raises(AuthenticationError) as exc_info:
                await service.authenticate_user(login_data)

            assert exc_info.value.error_code == "AUTHENTICATION_FAILED"

    @pytest.mark.asyncio
    async def test_login_with_nonexistent_user(self):
        """Test login with non-existent user email."""
        with MockContextManager(success_responses=False) as mock_ctx:
            service = AuthService()

            # Mock Supabase auth error for non-existent user
            auth_error = AuthMockFactory.create_auth_error("User not found", 404)
            service.supabase.auth.sign_in_with_password.side_effect = auth_error

            login_data = UserLogin(
                email="nonexistent@example.com", password="anypassword123"
            )

            # Test login should fail
            with pytest.raises(AuthenticationError) as exc_info:
                await service.authenticate_user(login_data)

            assert exc_info.value.error_code == "AUTHENTICATION_FAILED"

    @pytest.mark.asyncio
    async def test_login_supabase_response_parsing(self):
        """Test parsing of Supabase login response."""
        with MockContextManager(success_responses=True) as mock_ctx:
            service = AuthService()
            user_data = TestDataGenerator.generate_user_data()

            # Create detailed mock response
            supabase_user = TestDataGenerator.generate_supabase_user_dict(user_data)
            supabase_session = TestDataGenerator.generate_supabase_session_dict(
                user_data
            )

            mock_response = AuthMockFactory.create_supabase_response(
                success=True, user_data=supabase_user, session_data=supabase_session
            )
            service.supabase.auth.sign_in_with_password.return_value = mock_response

            # Test login
            result = await service.authenticate_user(user_data.to_user_login())

            # Verify response parsing
            assert result.access_token is not None
            assert result.token_type == "bearer"
            assert result.user.username == user_data.username

    @pytest.mark.asyncio
    async def test_login_without_session(self):
        """Test login when Supabase doesn't return a session."""
        with MockContextManager() as mock_ctx:
            service = AuthService()
            user_data = TestDataGenerator.generate_user_data()

            # Mock response with user but no session
            mock_response = MagicMock()
            mock_response.user = MagicMock()
            mock_response.user.id = user_data.user_id
            mock_response.user.email = user_data.email
            mock_response.session = None
            service.supabase.auth.sign_in_with_password.return_value = mock_response

            # Test login should fail
            with pytest.raises(AuthenticationError) as exc_info:
                await service.authenticate_user(user_data.to_user_login())

            assert exc_info.value.error_code == "SESSION_CREATION_FAILED"

    @pytest.mark.asyncio
    async def test_login_logging(self):
        """Test that login attempts are properly logged."""
        with MockContextManager(success_responses=True) as mock_ctx:
            service = AuthService()
            user_data = TestDataGenerator.generate_user_data()

            # Mock logger to capture calls
            mock_logger = MagicMock()
            service.logger = mock_logger

            mock_response = AuthMockFactory.create_supabase_response(success=True)
            service.supabase.auth.sign_in_with_password.return_value = mock_response

            # Test login
            await service.authenticate_user(user_data.to_user_login())

            # Verify logging occurred
            mock_logger.info.assert_called()

    @pytest.mark.asyncio
    async def test_successful_user_logout(self):
        """Test successful user logout."""
        with MockContextManager(success_responses=True) as mock_ctx:
            service = AuthService()

            # Mock successful logout response
            mock_response = MagicMock()
            mock_response.error = None
            service.supabase.auth.sign_out.return_value = mock_response

            # Test logout
            result = await service.logout_user()

            # Verify result
            assert result is True

    @pytest.mark.asyncio
    async def test_logout_with_error(self):
        """Test logout when Supabase returns an error."""
        with MockContextManager(success_responses=False) as mock_ctx:
            service = AuthService()

            # Mock logout error response
            mock_response = MagicMock()
            mock_response.error = "Logout failed"
            service.supabase.auth.sign_out.return_value = mock_response

            # Test logout should handle error gracefully
            with pytest.raises(AuthenticationError) as exc_info:
                await service.logout_user()

            assert exc_info.value.error_code == "LOGOUT_FAILED"

    @pytest.mark.asyncio
    async def test_refresh_token_functionality(self):
        """Test token refresh functionality."""
        with MockContextManager(success_responses=True) as mock_ctx:
            service = AuthService()

            # Mock successful refresh response
            mock_response = AuthMockFactory.create_supabase_response(success=True)
            service.supabase.auth.refresh_session.return_value = mock_response

            # Test token refresh
            refresh_token = "mock_refresh_token"
            result = await service.refresh_user_token(refresh_token)

            # Verify result
            assert isinstance(result, TokenResponse)
            assert result.access_token is not None
            assert result.refresh_token is not None

    @pytest.mark.asyncio
    async def test_refresh_token_with_invalid_token(self):
        """Test token refresh with invalid refresh token."""
        with MockContextManager(success_responses=False) as mock_ctx:
            service = AuthService()

            # Mock refresh error
            auth_error = AuthMockFactory.create_auth_error("Invalid refresh token", 401)
            service.supabase.auth.refresh_session.side_effect = auth_error

            # Test refresh should fail
            with pytest.raises(AuthenticationError) as exc_info:
                await service.refresh_user_token("invalid_token")

            assert exc_info.value.error_code == "TOKEN_REFRESH_FAILED"

    @pytest.mark.asyncio
    async def test_authentication_flow_scenarios(self):
        """Test multiple authentication scenarios from TestScenarios."""
        scenarios = TestScenarios.authentication_flow_scenarios()

        for scenario in scenarios:
            if scenario["expected_success"]:
                with MockContextManager(success_responses=True) as mock_ctx:
                    service = AuthService()

                    mock_response = AuthMockFactory.create_supabase_response(
                        success=True
                    )
                    service.supabase.auth.sign_in_with_password.return_value = (
                        mock_response
                    )

                    result = await service.authenticate_user(scenario["credentials"])
                    assert isinstance(result, TokenResponse)
            else:
                with MockContextManager(success_responses=False) as mock_ctx:
                    service = AuthService()

                    auth_error = AuthMockFactory.create_auth_error(
                        "Authentication failed"
                    )
                    service.supabase.auth.sign_in_with_password.side_effect = auth_error

                    with pytest.raises(AuthenticationError):
                        await service.authenticate_user(scenario["credentials"])
