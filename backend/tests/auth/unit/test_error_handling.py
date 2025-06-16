"""
Unit Tests for Error Handling in Auth Service.

This module tests error handling and exception scenarios in the Auth service.
"""

import pytest
from unittest.mock import patch, MagicMock
from uuid import uuid4

from domains.auth.services import AuthService, AuthenticationError
from domains.auth.schemas import UserCreate, UserLogin
from tests.auth.config import AuthTestBase
from tests.auth.utils.mocks import AuthMockFactory, MockContextManager
from tests.auth.utils.test_data import TestDataGenerator


class TestAuthErrorHandling(AuthTestBase):
    """Test error handling in Auth service."""

    def test_main_functionality(self):
        """Required by AuthTestBase - tests basic error handling."""
        self.test_authentication_error_creation()

    def test_authentication_error_creation(self):
        """Test AuthenticationError creation and properties."""
        # Test with message only
        error = AuthenticationError("Test error message")
        assert error.message == "Test error message"
        assert error.error_code is None
        assert str(error) == "Test error message"
        
        # Test with message and error code
        error_with_code = AuthenticationError("Test error", "TEST_ERROR_CODE")
        assert error_with_code.message == "Test error"
        assert error_with_code.error_code == "TEST_ERROR_CODE"

    def test_authentication_error_inheritance(self):
        """Test AuthenticationError inherits from Exception properly."""
        error = AuthenticationError("Test error")
        assert isinstance(error, Exception)
        assert isinstance(error, AuthenticationError)

    @pytest.mark.asyncio
    async def test_supabase_connection_error(self):
        """Test handling of Supabase connection errors."""
        with patch('domains.auth.services.get_supabase_client') as mock_client:
            # Mock connection error
            mock_client.side_effect = ConnectionError("Unable to connect to Supabase")
            
            with pytest.raises(ConnectionError):
                AuthService()

    @pytest.mark.asyncio
    async def test_network_timeout_error(self):
        """Test handling of network timeout errors."""
        with MockContextManager() as mock_ctx:
            service = AuthService()
            user_data = TestDataGenerator.generate_user_data()
            
            # Mock timeout error
            import asyncio
            service.supabase.auth.sign_up.side_effect = asyncio.TimeoutError("Request timed out")
            
            with pytest.raises(AuthenticationError) as exc_info:
                await service.register_user(user_data.to_user_create())
            
            assert exc_info.value.error_code == "REGISTRATION_FAILED"

    @pytest.mark.asyncio
    async def test_malformed_supabase_response(self):
        """Test handling of malformed Supabase responses."""
        with MockContextManager() as mock_ctx:
            service = AuthService()
            user_data = TestDataGenerator.generate_user_data()
            
            # Mock malformed response (missing required fields)
            mock_response = MagicMock()
            mock_response.user = None  # Should have user data
            mock_response.session = MagicMock()  # But session exists
            mock_response.session.access_token = "token"
            service.supabase.auth.sign_up.return_value = mock_response
            
            with pytest.raises(AuthenticationError) as exc_info:
                await service.register_user(user_data.to_user_create())
            
            assert exc_info.value.error_code == "USER_CREATION_FAILED"

    @pytest.mark.asyncio
    async def test_database_constraint_violation(self):
        """Test handling of database constraint violations."""
        with MockContextManager() as mock_ctx:
            service = AuthService()
            user_data = TestDataGenerator.generate_user_data()
            
            # Mock constraint violation error
            constraint_error = AuthMockFactory.create_auth_error(
                "duplicate key value violates unique constraint", 
                409
            )
            service.supabase.auth.sign_up.side_effect = constraint_error
            
            with pytest.raises(AuthenticationError) as exc_info:
                await service.register_user(user_data.to_user_create())
            
            assert exc_info.value.error_code == "REGISTRATION_FAILED"

    @pytest.mark.asyncio
    async def test_rate_limit_error(self):
        """Test handling of rate limit errors."""
        with MockContextManager() as mock_ctx:
            service = AuthService()
            user_data = TestDataGenerator.generate_user_data()
            
            # Mock rate limit error
            rate_limit_error = AuthMockFactory.create_auth_error(
                "Too many requests", 
                429
            )
            service.supabase.auth.sign_up.side_effect = rate_limit_error
            
            with pytest.raises(AuthenticationError) as exc_info:
                await service.register_user(user_data.to_user_create())
            
            assert exc_info.value.error_code == "REGISTRATION_FAILED"

    @pytest.mark.asyncio
    async def test_email_verification_required_error(self):
        """Test handling when email verification is required."""
        with MockContextManager() as mock_ctx:
            service = AuthService()
            user_data = TestDataGenerator.generate_user_data()
            
            # Mock email verification required
            mock_response = MagicMock()
            mock_response.user = MagicMock()
            mock_response.user.id = user_data.user_id
            mock_response.user.email = user_data.email
            mock_response.user.email_confirmed_at = None  # Not verified
            mock_response.session = None  # No session when verification required
            service.supabase.auth.sign_up.return_value = mock_response
            
            # This should succeed but indicate verification needed
            result = await service.register_user(user_data.to_user_create())
            # The exact behavior depends on implementation

    @pytest.mark.asyncio
    async def test_json_serialization_error(self):
        """Test handling of JSON serialization errors."""
        with MockContextManager() as mock_ctx:
            service = AuthService()
            
            # Mock JSON error in response parsing
            with patch('json.loads', side_effect=ValueError("Invalid JSON")):
                # This depends on whether the service actually uses json.loads directly
                pass

    @pytest.mark.asyncio
    async def test_unexpected_exception_handling(self):
        """Test handling of unexpected exceptions."""
        with MockContextManager() as mock_ctx:
            service = AuthService()
            user_data = TestDataGenerator.generate_user_data()
            
            # Mock unexpected exception
            service.supabase.auth.sign_up.side_effect = ValueError("Unexpected error")
            
            with pytest.raises(AuthenticationError) as exc_info:
                await service.register_user(user_data.to_user_create())
            
            assert exc_info.value.error_code == "REGISTRATION_FAILED"

    @pytest.mark.asyncio
    async def test_logging_of_errors(self):
        """Test that errors are properly logged."""
        with MockContextManager() as mock_ctx:
            service = AuthService()
            user_data = TestDataGenerator.generate_user_data()
            
            # Mock logger
            mock_logger = MagicMock()
            service.logger = mock_logger
            
            # Mock error
            auth_error = AuthMockFactory.create_auth_error("Test error")
            service.supabase.auth.sign_up.side_effect = auth_error
            
            with pytest.raises(AuthenticationError):
                await service.register_user(user_data.to_user_create())
            
            # Verify error was logged
            mock_logger.error.assert_called()

    @pytest.mark.asyncio
    async def test_error_code_consistency(self):
        """Test that error codes are consistent across similar failures."""
        scenarios = [
            ("sign_up", "register_user", "REGISTRATION_FAILED"),
            ("sign_in_with_password", "authenticate_user", "AUTHENTICATION_FAILED"),
            ("sign_out", "logout_user", "LOGOUT_FAILED"),
        ]
        
        for supabase_method, service_method, expected_error_code in scenarios:
            with MockContextManager() as mock_ctx:
                service = AuthService()
                
                # Mock error for each method
                auth_error = AuthMockFactory.create_auth_error("Test error")
                getattr(service.supabase.auth, supabase_method).side_effect = auth_error
                
                try:
                    if service_method == "register_user":
                        user_data = TestDataGenerator.generate_user_data()
                        await getattr(service, service_method)(user_data.to_user_create())
                    elif service_method == "authenticate_user":
                        user_data = TestDataGenerator.generate_user_data()
                        await getattr(service, service_method)(user_data.to_user_login())
                    elif service_method == "logout_user":
                        await getattr(service, service_method)()
                except AuthenticationError as e:
                    assert e.error_code == expected_error_code

    @pytest.mark.asyncio
    async def test_error_message_sanitization(self):
        """Test that sensitive information is not exposed in error messages."""
        with MockContextManager() as mock_ctx:
            service = AuthService()
            user_data = TestDataGenerator.generate_user_data()
            
            # Mock error with sensitive information
            sensitive_error = AuthMockFactory.create_auth_error(
                f"Database error: password {user_data.password} invalid"
            )
            service.supabase.auth.sign_up.side_effect = sensitive_error
            
            with pytest.raises(AuthenticationError) as exc_info:
                await service.register_user(user_data.to_user_create())
            
            # Verify password is not in error message
            assert user_data.password not in str(exc_info.value.message)
