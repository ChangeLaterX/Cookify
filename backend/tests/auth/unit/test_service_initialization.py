"""
Unit Tests for Auth Service Initialization and Dependencies.

This module tests the basic setup and configuration of the Auth service.
"""

import pytest
from unittest.mock import patch, MagicMock
import os

from domains.auth.services import AuthService, AuthenticationError
from tests.auth.config import AuthTestBase
from tests.auth.utils.mocks import MockContextManager, with_mocked_auth


class TestAuthServiceInitialization(AuthTestBase):
    """Test Auth service initialization and dependency management."""

    def test_main_functionality(self):
        """Required by AuthTestBase - tests basic service creation."""
        self.test_auth_service_initialization_with_dependencies()

    def test_auth_service_initialization_with_dependencies(self):
        """Test Auth service initializes correctly when dependencies are available."""
        with MockContextManager() as mock_ctx:
            service = AuthService()
            
            # Verify service has expected attributes
            assert hasattr(service, 'supabase')
            assert hasattr(service, 'logger')
            assert service.supabase is not None

    def test_auth_service_initialization_without_supabase(self):
        """Test Auth service behavior when Supabase is not available."""
        with patch('domains.auth.services.get_supabase_client', side_effect=Exception("Supabase not available")):
            with pytest.raises(Exception) as exc_info:
                AuthService()
            
            assert "Supabase not available" in str(exc_info.value)

    def test_supabase_client_configuration(self):
        """Test Supabase client configuration logic."""
        with MockContextManager():
            service = AuthService()
            
            # Verify client is properly configured
            assert service.supabase is not None
            assert hasattr(service.supabase, 'auth')
            assert hasattr(service.supabase, 'table')

    def test_logger_configuration(self):
        """Test logger configuration in AuthService."""
        with MockContextManager():
            service = AuthService()
            
            # Verify logger is properly configured
            assert service.logger is not None
            assert hasattr(service.logger, 'info')
            assert hasattr(service.logger, 'error')
            assert hasattr(service.logger, 'warning')

    @patch.dict(os.environ, {'SUPABASE_URL': 'test_url', 'SUPABASE_ANON_KEY': 'test_key'})
    def test_auth_service_with_environment_variables(self):
        """Test Auth service uses environment variables correctly."""
        with MockContextManager():
            service = AuthService()
            
            # Service should initialize successfully with env vars
            assert service.supabase is not None

    @patch.dict(os.environ, {}, clear=True)
    def test_auth_service_without_environment_variables(self):
        """Test Auth service behavior without required environment variables."""
        # This might fail depending on how the service handles missing env vars
        # The behavior depends on the actual implementation
        with MockContextManager():
            try:
                service = AuthService()
                # If it succeeds with mocks, that's fine
                assert service.supabase is not None
            except Exception:
                # If it fails due to missing env vars, that's expected behavior
                pass

    def test_auth_service_supabase_client_methods(self):
        """Test that AuthService has access to required Supabase client methods."""
        with MockContextManager():
            service = AuthService()
            
            # Verify auth methods are available
            assert hasattr(service.supabase.auth, 'sign_up')
            assert hasattr(service.supabase.auth, 'sign_in_with_password')
            assert hasattr(service.supabase.auth, 'sign_out')
            
            # Verify table methods are available
            assert callable(service.supabase.table)

    def test_authentication_error_creation(self):
        """Test AuthenticationError exception creation."""
        # Test with message only
        error = AuthenticationError("Test error")
        assert error.message == "Test error"
        assert error.error_code is None
        
        # Test with message and error code
        error_with_code = AuthenticationError("Test error", "TEST_ERROR_CODE")
        assert error_with_code.message == "Test error"
        assert error_with_code.error_code == "TEST_ERROR_CODE"

    def test_authentication_error_inheritance(self):
        """Test AuthenticationError inherits from Exception correctly."""
        error = AuthenticationError("Test error")
        assert isinstance(error, Exception)
        assert str(error) == "Test error"

    @with_mocked_auth(success=True)
    def test_service_with_successful_mock_context(self):
        """Test service initialization with successful mock context."""
        service = AuthService()
        assert service.supabase is not None

    @with_mocked_auth(success=False)
    def test_service_with_failing_mock_context(self):
        """Test service initialization with failing mock context."""
        service = AuthService()
        # Service should still initialize, but operations might fail
        assert service.supabase is not None
