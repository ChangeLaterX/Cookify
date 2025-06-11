"""
Pytest configuration and shared fixtures for authentication tests.
"""

import pytest
import asyncio
import os
from typing import Generator, AsyncGenerator
from unittest.mock import Mock, patch
from uuid import uuid4

import pytest_asyncio
from fastapi.testclient import TestClient
from supabase import Client

# Import the FastAPI app
from main import app


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def test_client() -> TestClient:
    """Create a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def mock_supabase_client():
    """Create a mock Supabase client for testing."""
    mock_client = Mock(spec=Client)
    
    # Mock auth methods
    mock_client.auth = Mock()
    mock_client.auth.sign_up = Mock()
    mock_client.auth.sign_in_with_password = Mock()
    mock_client.auth.refresh_session = Mock()
    mock_client.auth.set_session = Mock()
    mock_client.auth.sign_out = Mock()
    mock_client.auth.reset_password_email = Mock()
    mock_client.auth.update_user = Mock()
    mock_client.auth.resend = Mock()
    
    # Mock table methods
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
def mock_environment_variables():
    """Mock environment variables for testing."""
    test_env = {
        'SUPABASE_URL': 'https://test.supabase.co',
        'SUPABASE_ANON_KEY': 'test_anon_key',
        'SUPABASE_SERVICE_ROLE_KEY': 'test_service_key',
        'JWT_SECRET_KEY': 'test_jwt_secret',
        'ENVIRONMENT': 'test'
    }
    
    with patch.dict(os.environ, test_env):
        yield test_env


@pytest.fixture
def sample_user_uuid():
    """Generate a sample user UUID for testing."""
    return uuid4()


@pytest.fixture
def sample_user_data():
    """Sample user registration data."""
    return {
        "email": "test@example.com",
        "password": "TestPassword123!",
        "username": "testuser"
    }


@pytest.fixture
def sample_login_data():
    """Sample login credentials."""
    return {
        "email": "test@example.com",
        "password": "TestPassword123!"
    }


@pytest.fixture
def verified_user_data():
    """Sample verified user data."""
    return {
        "id": str(uuid4()),
        "email": "verified@example.com",
        "email_confirmed_at": "2023-01-01T00:00:00Z",
        "created_at": "2023-01-01T00:00:00Z",
        "updated_at": "2023-01-01T00:00:00Z"
    }


@pytest.fixture
def unverified_user_data():
    """Sample unverified user data."""
    return {
        "id": str(uuid4()),
        "email": "unverified@example.com",
        "email_confirmed_at": None,
        "created_at": "2023-01-01T00:00:00Z",
        "updated_at": "2023-01-01T00:00:00Z"
    }


@pytest.fixture
def mock_jwt_token():
    """Mock JWT token for testing."""
    return "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"


@pytest.fixture
def auth_headers(mock_jwt_token):
    """Authorization headers for testing."""
    return {"Authorization": f"Bearer {mock_jwt_token}"}


# Pytest configuration
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "asyncio: mark test as an async test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "email_verification: mark test as email verification related"
    )
    config.addinivalue_line(
        "markers", "security: mark test as security related"
    )


# Async test configuration
@pytest.fixture(scope="function")
async def async_test_client():
    """Create an async test client."""
    from httpx import AsyncClient
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


# Mock password strength validation
@pytest.fixture
def mock_password_validation():
    """Mock password strength validation."""
    with patch('shared.utils.password_security.validate_password_strength') as mock_validate:
        mock_validate.return_value = (True, [])
        yield mock_validate


# Database fixtures for integration tests
@pytest.fixture
def mock_database_session():
    """Mock database session for testing."""
    with patch('core.database.get_db') as mock_db:
        mock_session = Mock()
        mock_db.return_value = mock_session
        yield mock_session


# Clean up any test data after tests
@pytest.fixture(autouse=True)
def cleanup_test_data():
    """Automatically clean up test data after each test."""
    yield
    # Cleanup logic would go here if needed
    pass
