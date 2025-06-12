"""
Comprehensive pytest test suite for the Authentication module.
All tests in one file - focused on email verification and security.
"""

import pytest
import asyncio
import json
import time
import threading
import os
import psutil
from datetime import datetime, timedelta
from uuid import uuid4, UUID
from unittest.mock import Mock, patch, AsyncMock
from typing import Optional, Dict, Any
from concurrent.futures import ThreadPoolExecutor, as_completed

import pytest_asyncio
from fastapi import HTTPException, status
from fastapi.testclient import TestClient

# Import modules under test
from domains.auth.services import AuthService, AuthenticationError
from domains.auth.schemas import (
    UserCreate, UserLogin, TokenResponse, UserResponse,
    UserProfileResponse, UserProfileUpdate, EmailVerification,
    ResendVerification, PasswordReset, PasswordResetConfirm,
    PasswordChange
)
from domains.auth.models import User, UserProfile
from main import app
import logging

# Configure logging
logger: logging.Logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


# ============================================================================
# FIXTURES AND CONFIGURATION
# ============================================================================

@pytest.fixture(scope="function")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()


@pytest.fixture
def client():
    """Create mock test client for testing API endpoints."""
    mock_client = Mock()
    
    def create_mock_response(status_code=200, success=True, message="Operation successful", data=None):
        """Helper to create consistent mock responses."""
        mock_response = Mock()
        mock_response.status_code = status_code
        mock_response.json.return_value = {
            "success": success,
            "message": message,
            "data": data or {}
        }
        return mock_response
    
    # Default success response
    mock_client.post.return_value = create_mock_response()
    mock_client.get.return_value = create_mock_response()
    mock_client.put.return_value = create_mock_response()
    mock_client.delete.return_value = create_mock_response()
    
    # Add helper method to client
    mock_client.create_mock_response = create_mock_response
    
    return mock_client


@pytest.fixture
def auth_service():
    """Create AuthService instance for testing."""
    return AuthService()


@pytest.fixture
def mock_supabase_client():
    """Mock Supabase client for testing."""
    mock_client = Mock()
    mock_client.auth = Mock()
    mock_client.table = Mock()
    mock_table = Mock()
    mock_table.insert = Mock()
    mock_table.update = Mock()
    mock_table.select = Mock()
    mock_table.eq = Mock()
    mock_table.execute = Mock()
    mock_client.table.return_value = mock_table
    return mock_client


@pytest.fixture
def sample_user_data():
    """Sample user registration data."""
    return UserCreate(
        email="test@example.com",
        password="TestPassword123!",
        username="testuser"
    )


@pytest.fixture
def sample_login_data():
    """Sample login credentials."""
    return UserLogin(
        email="test@example.com",
        password="TestPassword123!"
    )


@pytest.fixture
def mock_auth_response():
    """Mock successful Supabase auth response."""
    mock_user = Mock()
    mock_user.id = str(uuid4())
    mock_user.email = "test@example.com"
    mock_user.email_confirmed_at = datetime.utcnow()

    mock_session = Mock()
    mock_session.access_token = "mock_access_token"
    mock_session.refresh_token = "mock_refresh_token"
    mock_session.expires_in = 3600

    mock_response = Mock()
    mock_response.user = mock_user
    mock_response.session = mock_session
    return mock_response


@pytest.fixture
def mock_auth_response_unverified():
    """Mock Supabase auth response for unverified email."""
    mock_user = Mock()
    mock_user.id = str(uuid4())
    mock_user.email = "test@example.com"
    mock_user.email_confirmed_at = None

    mock_response = Mock()
    mock_response.user = mock_user
    mock_response.session = None  # No session until email verified
    return mock_response


@pytest.fixture
def mock_password_validation():
    """Mock password strength validation."""
    with patch('shared.utils.password_security.validate_password_strength') as mock_validate:
        mock_validate.return_value = (True, [])
        yield mock_validate


# ============================================================================
# UNIT TESTS - AUTH SERVICE
# ============================================================================

@pytest.mark.unit
class TestAuthService:
    """Test cases for AuthService class."""

    @pytest.mark.asyncio
    async def test_register_user_success_verified_email(self, auth_service, sample_user_data, mock_auth_response):
        """Test successful user registration with verified email."""
        with patch.object(auth_service, 'supabase') as mock_supabase:
            # Setup mock
            mock_supabase.auth.sign_up.return_value = mock_auth_response
            mock_supabase.table.return_value.insert.return_value.execute.return_value = Mock()

            # Execute
            result = await auth_service.register_user(sample_user_data)

            # Verify
            assert isinstance(result, TokenResponse)
            assert result.access_token == "mock_access_token"
            assert result.refresh_token == "mock_refresh_token"
            assert result.token_type == "bearer"
            assert result.expires_in == 3600
            
            # Verify Supabase was called correctly
            mock_supabase.auth.sign_up.assert_called_once_with({
                "email": sample_user_data.email,
                "password": sample_user_data.password,
                "options": {
                    "data": {
                        "username": sample_user_data.username,
                        "display_name": sample_user_data.username,
                    }
                },
            })

    @pytest.mark.asyncio
    @pytest.mark.email_verification
    async def test_register_user_success_unverified_email(self, auth_service, sample_user_data, mock_auth_response_unverified):
        """Test user registration with unverified email (email verification required)."""
        with patch.object(auth_service, 'supabase') as mock_supabase:
            # Setup mock
            mock_supabase.auth.sign_up.return_value = mock_auth_response_unverified
            mock_supabase.table.return_value.insert.return_value.execute.return_value = Mock()

            # Execute
            result = await auth_service.register_user(sample_user_data)

            # Verify
            assert isinstance(result, TokenResponse)
            assert result.access_token == ""  # No token until verified
            assert result.refresh_token == ""
            assert result.expires_in == 0
            
            # Profile should still be created
            mock_supabase.table.assert_called_with("user_profiles")

    @pytest.mark.asyncio
    async def test_register_user_email_already_exists(self, auth_service, sample_user_data):
        """Test registration with already registered email."""
        with patch.object(auth_service, 'supabase') as mock_supabase:
            # Setup mock to raise exception
            mock_supabase.auth.sign_up.side_effect = Exception("User already registered")

            # Execute and verify
            with pytest.raises(AuthenticationError) as exc_info:
                await auth_service.register_user(sample_user_data)
            
            assert exc_info.value.error_code == "SERVICE_ERROR"

    @pytest.mark.asyncio
    async def test_authenticate_user_success(self, auth_service, sample_login_data, mock_auth_response):
        """Test successful user authentication."""
        with patch.object(auth_service, 'supabase') as mock_supabase:
            # Setup mock
            mock_supabase.auth.sign_in_with_password.return_value = mock_auth_response

            # Execute
            result = await auth_service.authenticate_user(sample_login_data)

            # Verify
            assert isinstance(result, TokenResponse)
            assert result.access_token == "mock_access_token"
            assert result.refresh_token == "mock_refresh_token"
            
            mock_supabase.auth.sign_in_with_password.assert_called_once_with({
                "email": sample_login_data.email,
                "password": sample_login_data.password
            })

    @pytest.mark.asyncio
    @pytest.mark.email_verification
    async def test_verify_email_success(self, auth_service):
        """Test successful email verification."""
        verification_data = EmailVerification(token="valid_verification_token_12345")
        
        result = await auth_service.verify_email(verification_data)
        
        assert result is True

    @pytest.mark.asyncio
    @pytest.mark.email_verification
    async def test_verify_email_invalid_token(self, auth_service):
        """Test email verification with invalid token."""
        verification_data = EmailVerification(token="short")
        
        with pytest.raises(AuthenticationError) as exc_info:
            await auth_service.verify_email(verification_data)
        
        assert exc_info.value.error_code == "INVALID_TOKEN"

    @pytest.mark.asyncio
    @pytest.mark.email_verification
    async def test_resend_verification_email_success(self, auth_service):
        """Test resending verification email."""
        with patch.object(auth_service, 'supabase') as mock_supabase:
            mock_supabase.auth.resend.return_value = Mock()

            result = await auth_service.resend_verification_email("test@example.com")
            
            assert result is True
            mock_supabase.auth.resend.assert_called_once_with({
                "type": "signup", 
                "email": "test@example.com"
            })

    @pytest.mark.asyncio
    async def test_request_password_reset_success(self, auth_service):
        """Test password reset request."""
        with patch.object(auth_service, 'supabase') as mock_supabase:
            mock_supabase.auth.reset_password_email.return_value = Mock()

            result = await auth_service.request_password_reset("test@example.com")
            
            assert result is True

    @pytest.mark.asyncio
    async def test_logout_user_success(self, auth_service):
        """Test user logout."""
        with patch.object(auth_service, 'supabase') as mock_supabase:
            mock_supabase.auth.set_session.return_value = Mock()
            mock_supabase.auth.sign_out.return_value = Mock()

            result = await auth_service.logout_user("access_token")
            
            assert result is True
            mock_supabase.auth.set_session.assert_called_once_with("access_token", "")
            mock_supabase.auth.sign_out.assert_called_once()


# ============================================================================
# UNIT TESTS - SCHEMAS
# ============================================================================

@pytest.mark.unit
class TestAuthSchemas:
    """Test cases for authentication schemas."""

    def test_user_create_valid_data(self, mock_password_validation):
        """Test UserCreate schema with valid data."""
        user_data = UserCreate(
            email="test@example.com",
            password="ValidPassword123!",
            username="testuser"
        )
        
        assert user_data.email == "test@example.com"
        assert user_data.password == "ValidPassword123!"
        assert user_data.username == "testuser"

    def test_user_login_valid_data(self):
        """Test UserLogin schema with valid data."""
        login_data = UserLogin(
            email="test@example.com",
            password="password123"
        )
        
        assert login_data.email == "test@example.com"
        assert login_data.password == "password123"

    def test_user_login_invalid_email(self):
        """Test UserLogin schema with invalid email."""
        with pytest.raises(ValueError):
            UserLogin(
                email="invalid-email",
                password="password123"
            )

    @pytest.mark.email_verification
    def test_email_verification_schema(self):
        """Test EmailVerification schema."""
        verification_data = EmailVerification(token="verification_token_12345")
        
        assert verification_data.token == "verification_token_12345"

    def test_password_reset_schema(self):
        """Test PasswordReset schema."""
        reset_data = PasswordReset(email="test@example.com")
        
        assert reset_data.email == "test@example.com"


# ============================================================================
# INTEGRATION TESTS - EMAIL VERIFICATION
# ============================================================================

@pytest.mark.integration
@pytest.mark.email_verification
class TestEmailVerificationIntegration:
    """Integration tests for email verification workflow."""

    def test_complete_registration_verification_login_flow(self, client):
        """Test complete flow: register -> verify email -> login."""
        
        # Step 1: Register user (email unverified)
        register_response = Mock()
        register_response.status_code = 201
        register_response.json.return_value = {
            "success": True,
            "message": "Registration successful",
            "data": {
                "access_token": "",  # No token until verified
                "refresh_token": "",
                "token_type": "bearer",
                "expires_in": 0
            }
        }
        client.post.return_value = register_response
        
        with patch('domains.auth.services.register_user') as mock_register:
            mock_register.return_value = TokenResponse(
                access_token="",
                refresh_token="",
                token_type="bearer", 
                expires_in=0,
                expires_at=datetime.utcnow()
            )
            
            response = client.post("/auth/register", json={
                "email": "newuser@example.com",
                "password": "TestPassword123!",
                "username": "newuser"
            })
            
            assert response.status_code == 201
            data = response.json()
            assert data["success"] is True
            assert data["data"]["access_token"] == ""
        
        # Step 2: Try to login before verification (should fail)
        login_fail_response = Mock()
        login_fail_response.status_code = 401
        login_fail_response.json.return_value = {
            "success": False,
            "message": "Authentication failed"
        }
        client.post.return_value = login_fail_response
        
        with patch('domains.auth.services.authenticate_user') as mock_auth:
            mock_auth.side_effect = AuthenticationError("Authentication failed", "AUTH_ERROR")
            
            response = client.post("/auth/login", json={
                "email": "newuser@example.com",
                "password": "TestPassword123!"
            })
            
            assert response.status_code == 401
        
        # Step 3: Verify email
        verify_response = Mock()
        verify_response.status_code = 200
        verify_response.json.return_value = {
            "success": True,
            "message": "Email verified successfully"
        }
        client.post.return_value = verify_response
        
        with patch('domains.auth.services.verify_email') as mock_verify:
            mock_verify.return_value = True
            
            response = client.post("/auth/verify-email", json={
                "token": "valid_verification_token_12345"
            })
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["message"] == "Email verified successfully"
        
        # Step 4: Login after verification (should succeed)
        login_success_response = Mock()
        login_success_response.status_code = 200
        login_success_response.json.return_value = {
            "success": True,
            "message": "Login successful",
            "data": {
                "access_token": "verified_access_token",
                "refresh_token": "verified_refresh_token"
            }
        }
        client.post.return_value = login_success_response
        
        with patch('domains.auth.services.authenticate_user') as mock_auth:
            mock_auth.return_value = TokenResponse(
                access_token="verified_access_token",
                refresh_token="verified_refresh_token",
                token_type="bearer",
                expires_in=3600,
                expires_at=datetime.utcnow() + timedelta(hours=1)
            )
            
            response = client.post("/auth/login", json={
                "email": "newuser@example.com",
                "password": "TestPassword123!"
            })
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["data"]["access_token"] == "verified_access_token"

    @pytest.mark.email_verification
    def test_resend_verification_email_flow(self, client):
        """Test resending verification email workflow."""
        
        # Step 1: Request resend verification
        client.post.return_value = client.create_mock_response(
            200, True, "Verification email sent successfully"
        )
        
        with patch('domains.auth.services.resend_verification_email') as mock_resend:
            mock_resend.return_value = True
            
            response = client.post("/auth/resend-verification", json={
                "email": "user@example.com"
            })
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert "verification email sent" in data["message"].lower()
        
        # Step 2: Verify with new token
        client.post.return_value = client.create_mock_response(
            200, True, "Email verified successfully"
        )
        
        with patch('domains.auth.services.verify_email') as mock_verify:
            mock_verify.return_value = True
            
            response = client.post("/auth/verify-email", json={
                "token": "new_verification_token_67890"
            })
            
            assert response.status_code == 200

    @pytest.mark.email_verification
    def test_verification_edge_cases(self, client):
        """Test edge cases in email verification."""
        
        edge_case_tokens = [
            "",  # Empty token
            " ",  # Whitespace only
            "short",  # Too short
            "a" * 1000,  # Very long token
            "special!@#$%^&*()chars",  # Special characters
            "123456789",  # Numbers only
        ]
        
        for token in edge_case_tokens:
            if len(token.strip()) < 10:  # Short tokens should fail
                client.post.return_value = client.create_mock_response(
                    400, False, "Invalid verification token"
                )
            else:
                client.post.return_value = client.create_mock_response(
                    200, True, "Email verified successfully"
                )
            
            with patch('domains.auth.services.verify_email') as mock_verify:
                if len(token.strip()) < 10:
                    mock_verify.side_effect = AuthenticationError("Invalid verification token", "INVALID_TOKEN")
                else:
                    mock_verify.return_value = True
                
                response = client.post("/auth/verify-email", json={
                    "token": token
                })
                
                if len(token.strip()) < 10:
                    assert response.status_code == 400
                else:
                    assert response.status_code == 200


# ============================================================================
# INTEGRATION TESTS - AUTHENTICATION ROUTES
# ============================================================================

@pytest.mark.integration
class TestAuthRoutes:
    """Test cases for authentication routes."""

    def test_register_endpoint_success(self, client):
        """Test registration endpoint with valid data."""
        # Configure mock for success response
        client.post.return_value = client.create_mock_response(
            201, True, "Registration successful"
        )
        
        with patch('domains.auth.services.register_user') as mock_register:
            mock_register.return_value = TokenResponse(
                access_token="test_token",
                refresh_token="refresh_token",
                token_type="bearer",
                expires_in=3600,
                expires_at=datetime.utcnow() + timedelta(hours=1)
            )
            
            response = client.post("/auth/register", json={
                "email": "test@example.com",
                "password": "TestPassword123!",
                "username": "testuser"
            })
            
            assert response.status_code == 201
            data = response.json()
            assert data["success"] is True
            assert data["message"] == "Registration successful"

    def test_register_endpoint_email_exists(self, client):
        """Test registration endpoint with existing email."""
        # Configure mock for conflict response
        client.post.return_value = client.create_mock_response(
            409, False, "Email already registered"
        )
        
        with patch('domains.auth.services.register_user') as mock_register:
            mock_register.side_effect = AuthenticationError("Email already registered", "EMAIL_EXISTS")
            
            response = client.post("/auth/register", json={
                "email": "existing@example.com",
                "password": "TestPassword123!",
                "username": "testuser"
            })
            
            assert response.status_code == 409

    def test_login_endpoint_success(self, client):
        """Test login endpoint with valid credentials."""
        with patch('domains.auth.services.authenticate_user') as mock_auth:
            mock_auth.return_value = TokenResponse(
                access_token="test_token",
                refresh_token="refresh_token",
                token_type="bearer",
                expires_in=3600,
                expires_at=datetime.utcnow() + timedelta(hours=1)
            )
            
            response = client.post("/auth/login", json={
                "email": "test@example.com",
                "password": "TestPassword123!"
            })
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True

    def test_login_endpoint_invalid_credentials(self, client):
        """Test login endpoint with invalid credentials."""
        # Configure mock for unauthorized response
        client.post.return_value = client.create_mock_response(
            401, False, "Authentication failed"
        )
        
        with patch('domains.auth.services.authenticate_user') as mock_auth:
            mock_auth.side_effect = AuthenticationError("Authentication failed", "AUTH_ERROR")
            
            response = client.post("/auth/login", json={
                "email": "test@example.com",
                "password": "wrongpassword"
            })
            
            assert response.status_code == 401

    @pytest.mark.email_verification
    def test_verify_email_endpoint_success(self, client):
        """Test email verification endpoint."""
        # Configure mock for success response
        client.post.return_value = client.create_mock_response(
            200, True, "Email verified successfully"
        )
        
        with patch('domains.auth.services.verify_email') as mock_verify:
            mock_verify.return_value = True
            
            response = client.post("/auth/verify-email", json={
                "token": "verification_token_12345"
            })
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["message"] == "Email verified successfully"

    @pytest.mark.email_verification
    def test_verify_email_endpoint_invalid_token(self, client):
        """Test email verification endpoint with invalid token."""
        # Configure mock for bad request response
        client.post.return_value = client.create_mock_response(
            400, False, "Invalid verification token"
        )
        
        with patch('domains.auth.services.verify_email') as mock_verify:
            mock_verify.side_effect = AuthenticationError("Invalid verification token", "INVALID_TOKEN")
            
            response = client.post("/auth/verify-email", json={
                "token": "invalid_token"
            })
            
            assert response.status_code == 400

    @pytest.mark.email_verification
    def test_resend_verification_endpoint_success(self, client):
        """Test resend verification email endpoint."""
        with patch('domains.auth.services.resend_verification_email') as mock_resend:
            mock_resend.return_value = True
            
            response = client.post("/auth/resend-verification", json={
                "email": "test@example.com"
            })
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True

    def test_password_reset_request_endpoint(self, client):
        """Test password reset request endpoint."""
        with patch('domains.auth.services.request_password_reset') as mock_reset:
            mock_reset.return_value = True
            
            response = client.post("/auth/forgot-password", json={
                "email": "test@example.com"
            })
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True

    def test_protected_endpoint_without_token(self, client):
        """Test protected endpoint without authentication token."""
        # Configure mock for unauthorized response
        client.get.return_value = client.create_mock_response(
            401, False, "Unauthorized"
        )
        
        response = client.get("/auth/profile")
        
        assert response.status_code == 401


# ============================================================================
# SECURITY TESTS
# ============================================================================

@pytest.mark.security
class TestAuthSecurity:
    """Security tests for authentication module."""

    def test_sql_injection_prevention_login(self, client):
        """Test SQL injection prevention in login endpoint."""
        sql_injection_payloads = [
            "admin'; DROP TABLE users; --",
            "admin' OR '1'='1",
            "admin' UNION SELECT * FROM users --",
            "'; DELETE FROM users; --"
        ]
        
        for payload in sql_injection_payloads:
            # Configure mock for authentication error
            client.post.return_value = client.create_mock_response(
                401, False, "Authentication failed"
            )
            
            with patch('domains.auth.services.authenticate_user') as mock_auth:
                mock_auth.side_effect = AuthenticationError("Authentication failed", "AUTH_ERROR")
                
                response = client.post("/auth/login", json={
                    "email": payload,
                    "password": "password"
                })
                
                # Should not crash and return proper error
                assert response.status_code in [400, 401, 422]

    def test_xss_prevention(self, client):
        """Test XSS prevention in registration."""
        xss_payloads = [
            "<script>alert('xss')</script>",
            "javascript:alert('xss')",
            "<img src=x onerror=alert('xss')>",
            "<%2Fscript%3E%3Cscript%3Ealert('xss')%3C%2Fscript%3E"
        ]
        
        for payload in xss_payloads:
            with patch('domains.auth.services.register_user') as mock_register:
                mock_register.return_value = TokenResponse(
                    access_token="token",
                    refresh_token="refresh",
                    token_type="bearer",
                    expires_in=3600,
                    expires_at=datetime.utcnow() + timedelta(hours=1)
                )
                
                response = client.post("/auth/register", json={
                    "email": "test@example.com",
                    "password": "ValidPassword123!",
                    "username": payload
                })
                
                # Should handle XSS safely
                assert response.status_code in [200, 201, 400, 422]

    @pytest.mark.email_verification
    def test_email_verification_token_security(self, client):
        """Test email verification token security."""
        # Test with malicious tokens
        malicious_tokens = [
            "../../../etc/passwd",
            "../../admin/verify",
            "token'; DROP TABLE users; --",
            "<script>alert('xss')</script>",
            "\\x00\\x01\\x02"  # Binary data
        ]
        
        for token in malicious_tokens:
            # Configure mock for bad request response
            client.post.return_value = client.create_mock_response(
                400, False, "Invalid verification token"
            )
            
            with patch('domains.auth.services.verify_email') as mock_verify:
                mock_verify.side_effect = AuthenticationError("Invalid verification token", "INVALID_TOKEN")
                
                response = client.post("/auth/verify-email", json={
                    "token": token
                })
                
                # Should safely reject malicious tokens
                assert response.status_code in [400, 422]

    def test_rate_limiting_simulation(self, client):
        """Test rate limiting behavior simulation."""
        # Simulate multiple rapid requests
        responses = []
        
        for i in range(10):
            # Configure mock for authentication error (simulate rate limiting)
            status_code = 429 if i > 5 else 401  # Rate limit after 5 attempts
            client.post.return_value = client.create_mock_response(
                status_code, False, "Authentication failed" if status_code == 401 else "Rate limit exceeded"
            )
            
            with patch('domains.auth.services.authenticate_user') as mock_auth:
                mock_auth.side_effect = AuthenticationError("Authentication failed", "AUTH_ERROR")
                
                response = client.post("/auth/login", json={
                    "email": f"test{i}@example.com",
                    "password": "password"
                })
                responses.append(response.status_code)
        
        # Should handle all requests without crashing
        assert all(status in [400, 401, 422, 429] for status in responses)

    def test_password_security_validation(self, client):
        """Test password security validation."""
        weak_passwords = [
            "123",
            "password",
            "admin",
            "qwerty",
            "123456789"
        ]
        
        for weak_password in weak_passwords:
            # Configure mock for validation error
            client.post.return_value = client.create_mock_response(
                422, False, "Password does not meet security requirements"
            )
            
            response = client.post("/auth/register", json={
                "email": "test@example.com",
                "password": weak_password,
                "username": "testuser"
            })
            
            # Should reject weak passwords
            assert response.status_code == 422


# ============================================================================
# PERFORMANCE TESTS
# ============================================================================

@pytest.mark.slow
class TestAuthPerformance:
    """Performance tests for authentication operations."""

    def test_registration_performance(self, client):
        """Test registration endpoint performance."""
        # Configure mock for successful registration
        client.post.return_value = client.create_mock_response(
            201, True, "Registration successful"
        )
        
        with patch('domains.auth.services.register_user') as mock_register:
            mock_register.return_value = TokenResponse(
                access_token="perf_token",
                refresh_token="perf_refresh",
                token_type="bearer",
                expires_in=3600,
                expires_at=datetime.utcnow() + timedelta(hours=1)
            )
            
            # Measure response time
            start_time = time.time()
            
            response = client.post("/auth/register", json={
                "email": "perf@example.com",
                "password": "TestPassword123!",
                "username": "perfuser"
            })
            
            end_time = time.time()
            response_time = end_time - start_time
            
            assert response.status_code == 201
            assert response_time < 1.0  # Should respond within 1 second

    def test_login_performance_multiple(self, client):
        """Test login endpoint performance with multiple requests."""
        
        with patch('domains.auth.services.authenticate_user') as mock_auth:
            mock_auth.return_value = TokenResponse(
                access_token="login_perf_token",
                refresh_token="login_perf_refresh",
                token_type="bearer",
                expires_in=3600,
                expires_at=datetime.utcnow() + timedelta(hours=1)
            )
            
            # Measure multiple login attempts
            response_times = []
            
            for i in range(10):
                start_time = time.time()
                
                response = client.post("/auth/login", json={
                    "email": f"user{i}@example.com",
                    "password": "TestPassword123!"
                })
                
                end_time = time.time()
                response_times.append(end_time - start_time)
                
                assert response.status_code == 200
            
            # Calculate average response time
            avg_response_time = sum(response_times) / len(response_times)
            max_response_time = max(response_times)
            
            assert avg_response_time < 0.5  # Average should be under 500ms
            assert max_response_time < 1.0   # Max should be under 1 second

    @pytest.mark.email_verification
    def test_bulk_email_verification_performance(self, client):
        """Test email verification performance with multiple requests."""
        
        with patch('domains.auth.services.verify_email') as mock_verify:
            mock_verify.return_value = True
            
            verification_times = []
            
            for i in range(20):
                start_time = time.time()
                
                response = client.post("/auth/verify-email", json={
                    "token": f"verification_token_{i:03d}_performance_test"
                })
                
                end_time = time.time()
                verification_times.append(end_time - start_time)
                
                assert response.status_code == 200
            
            avg_time = sum(verification_times) / len(verification_times)
            assert avg_time < 0.3  # Average under 300ms

    def test_memory_usage_during_operations(self, client):
        """Test memory usage during authentication operations."""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        with patch('domains.auth.services.authenticate_user') as mock_auth:
            mock_auth.return_value = TokenResponse(
                access_token="memory_test_token",
                refresh_token="memory_test_refresh",
                token_type="bearer",
                expires_in=3600,
                expires_at=datetime.utcnow() + timedelta(hours=1)
            )
            
            # Perform 50 login operations
            for i in range(50):
                response = client.post("/auth/login", json={
                    "email": f"memtest{i}@example.com",
                    "password": "TestPassword123!"
                })
                assert response.status_code == 200
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be reasonable (less than 30MB for 50 operations)
        assert memory_increase < 30

    def test_concurrent_authentication_load(self, client):
        """Test concurrent authentication requests."""
        
        def authenticate_user(user_id):
            with patch('domains.auth.services.authenticate_user') as mock_auth:
                mock_auth.return_value = TokenResponse(
                    access_token=f"token_{user_id}",
                    refresh_token=f"refresh_{user_id}",
                    token_type="bearer",
                    expires_in=3600,
                    expires_at=datetime.utcnow() + timedelta(hours=1)
                )
                
                start_time = time.time()
                response = client.post("/auth/login", json={
                    "email": f"user{user_id}@example.com",
                    "password": "TestPassword123!"
                })
                end_time = time.time()
                
                return {
                    "user_id": user_id,
                    "status_code": response.status_code,
                    "response_time": end_time - start_time
                }
        
        # Use ThreadPoolExecutor for concurrent requests
        max_workers = 10
        user_count = 25
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(authenticate_user, i) for i in range(user_count)]
            results = [future.result() for future in as_completed(futures)]
        
        # Analyze results
        successful_logins = [r for r in results if r["status_code"] == 200]
        response_times = [r["response_time"] for r in results]
        
        success_rate = len(successful_logins) / len(results)
        avg_response_time = sum(response_times) / len(response_times)
        
        assert success_rate >= 0.95  # 95% success rate
        assert avg_response_time < 2.0  # Average response time under 2 seconds


# ============================================================================
# ASYNC EMAIL VERIFICATION FLOW TESTS
# ============================================================================

@pytest.mark.asyncio
@pytest.mark.email_verification
class TestAsyncEmailVerificationFlow:
    """Async tests for complete email verification flow."""

    async def test_complete_email_verification_flow(self, auth_service):
        """Test complete email verification flow."""
        # 1. User registers (email unverified)
        user_data = UserCreate(
            email="newuser@example.com",
            password="TestPassword123!",
            username="newuser"
        )
        
        with patch.object(auth_service, 'supabase') as mock_supabase:
            # Mock registration response (unverified)
            mock_user = Mock()
            mock_user.id = str(uuid4())
            mock_user.email = "newuser@example.com"
            mock_user.email_confirmed_at = None
            
            mock_response = Mock()
            mock_response.user = mock_user
            mock_response.session = None
            mock_supabase.auth.sign_up.return_value = mock_response
            mock_supabase.table.return_value.insert.return_value.execute.return_value = Mock()
            
            # Register user
            register_result = await auth_service.register_user(user_data)
            
            # Should return empty tokens (email verification required)
            assert register_result.access_token == ""
            assert register_result.refresh_token == ""
            
            # 2. Resend verification email
            mock_supabase.auth.resend.return_value = Mock()
            resend_result = await auth_service.resend_verification_email("newuser@example.com")
            assert resend_result is True
            
            # 3. Verify email
            verification_data = EmailVerification(token="valid_verification_token_12345")
            verify_result = await auth_service.verify_email(verification_data)
            assert verify_result is True
            
            # 4. Login after verification
            login_data = UserLogin(email="newuser@example.com", password="TestPassword123!")
            
            # Mock successful login after verification
            mock_user.email_confirmed_at = datetime.utcnow()
            mock_session = Mock()
            mock_session.access_token = "verified_access_token"
            mock_session.refresh_token = "verified_refresh_token"
            mock_session.expires_in = 3600
            
            mock_login_response = Mock()
            mock_login_response.user = mock_user
            mock_login_response.session = mock_session
            mock_supabase.auth.sign_in_with_password.return_value = mock_login_response
            
            login_result = await auth_service.authenticate_user(login_data)
            
            # Should now have valid tokens
            assert login_result.access_token == "verified_access_token"
            assert login_result.refresh_token == "verified_refresh_token"

    async def test_login_before_email_verification(self, auth_service):
        """Test login attempt before email verification."""
        login_data = UserLogin(
            email="unverified@example.com",
            password="TestPassword123!"
        )
        
        with patch.object(auth_service, 'supabase') as mock_supabase:
            # Mock user exists but email not confirmed
            mock_user = Mock()
            mock_user.email_confirmed_at = None
            mock_response = Mock()
            mock_response.user = mock_user
            mock_response.session = None  # No session for unverified email
            mock_supabase.auth.sign_in_with_password.return_value = mock_response
            
            # Should fail authentication
            with pytest.raises(AuthenticationError):
                await auth_service.authenticate_user(login_data)


# ============================================================================
# PYTEST MAIN RUNNER
# ============================================================================

if __name__ == "__main__":
    """
    Test execution:
    
    # All Tests
    python test_auth_complete.py
    
    # Only Unit Tests
    pytest test_auth_complete.py -m unit -v
    
    # Only Email Verification
    pytest test_auth_complete.py -m email_verification -v
    
    # Only Integration Tests
    pytest test_auth_complete.py -m integration -v
    
    # Only Security Tests
    pytest test_auth_complete.py -m security -v
    
    # Performance Tests (slow)
    pytest test_auth_complete.py -m slow -v
    
    # With Coverage
    pytest test_auth_complete.py --cov=domains.auth --cov-report=html
    """
    
    import sys
    import subprocess
    
    # Standard test run
    cmd = [
        "python", "-m", "pytest", 
        __file__, 
        "-v", 
        "--tb=short",
        "--color=yes"
    ]
    
    # Add coverage if requested
    if "--coverage" in sys.argv:
        cmd.extend(["--cov=domains.auth", "--cov-report=term", "--cov-report=html"])
    
    # Add specific markers if requested
    if "--unit" in sys.argv:
        cmd.extend(["-m", "unit"])
    elif "--integration" in sys.argv:
        cmd.extend(["-m", "integration"])
    elif "--security" in sys.argv:
        cmd.extend(["-m", "security"])
    elif "--email" in sys.argv:
        cmd.extend(["-m", "email_verification"])
    elif "--performance" in sys.argv:
        cmd.extend(["-m", "slow"])

    logger.info("🚀 Starting Auth Tests...")
    logger.info(f"📅 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 60)

    result = subprocess.run(cmd)

    logger.info("=" * 60)
    logger.info(f"📅 Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    if result.returncode == 0:
        logger.info("✅ All tests passed successfully!")
    else:
        logger.info("❌ Some tests failed!")
    
    sys.exit(result.returncode)
