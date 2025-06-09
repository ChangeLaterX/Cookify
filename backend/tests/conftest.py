"""
pytest configuration and shared fixtures for all tests.
"""

import pytest
import asyncio
from typing import Generator, AsyncGenerator
from httpx import AsyncClient


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """Create an async test client for the remote FastAPI server."""
    async with AsyncClient(base_url="http://dev.krija.info:8000/api", timeout=30.0) as ac:
        yield ac


@pytest.fixture
def test_user_credentials():
    """Test user credentials provided by the user."""
    return {
        "email": "krijajannis@gmail.com",
        "password": "221224"
    }


@pytest.fixture
def auth_headers():
    """Helper to create authorization headers."""
    def _create_headers(token: str) -> dict:
        return {"Authorization": f"Bearer {token}"}
    return _create_headers
