"""
Test configuration and fixtures.
"""
import pytest
from fastapi.testclient import TestClient
from main import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI """
    return TestClient(app)


@pytest.fixture
def auth_headers():
    """Mock authentication headers for testing."""
    return {"Authorization": "Bearer test_token"}
