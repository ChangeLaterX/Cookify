"""
Tests for /auth/register endpoint.
"""
import pytest
from httpx import AsyncClient


class TestRegisterEndpoint:
    """Test class for user registration endpoint."""

    @pytest.mark.asyncio
    async def test_register_new_user_success(self, async_client: AsyncClient):
        """Test successful user registration with valid data."""
        user_data = {
            "email": "test_new_user@example.com",
            "password": "SecurePassword123!",
            "username": "test_user"
        }

        response = await async_client.post("/auth/register", json=user_data)

        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert data["message"] == "Registration successful"
        assert "data" in data
        assert "access_token" in data["data"]
        assert "refresh_token" in data["data"]
        assert data["data"]["token_type"] == "bearer"

    @pytest.mark.asyncio
    async def test_register_existing_user_conflict(self, async_client: AsyncClient, test_user_credentials):
        """Test registration with already existing email returns conflict."""
        user_data = {
            "email": test_user_credentials["email"],
            "password": "AnotherPassword123!",
            "username": "another_user"
        }

        response = await async_client.post("/auth/register", json=user_data)

        assert response.status_code == 409
        data = response.json()
        assert "message" in data
        assert isinstance(data["message"], list)

    @pytest.mark.asyncio
    async def test_register_invalid_email(self, async_client: AsyncClient):
        """Test registration with invalid email format."""
        user_data = {
            "email": "invalid-email-format",
            "password": "SecurePassword123!",
            "username": "test_user"
        }

        response = await async_client.post("/auth/register", json=user_data)

        assert response.status_code == 422
        data = response.json()
        assert "message" in data
        assert isinstance(data["message"], list)

    @pytest.mark.asyncio
    async def test_register_weak_password(self, async_client: AsyncClient):
        """Test registration with weak password."""
        user_data = {
            "email": "test_weak@example.com",
            "password": "123",  # Too weak
            "username": "test_user"
        }

        response = await async_client.post("/auth/register", json=user_data)

        assert response.status_code == 422
        data = response.json()
        assert "message" in data
        assert isinstance(data["message"], list)

    @pytest.mark.asyncio
    async def test_register_missing_required_fields(self, async_client: AsyncClient):
        """Test registration with missing required fields."""
        user_data = {
            "email": "test@example.com"
            # Missing password
        }

        response = await async_client.post("/auth/register", json=user_data)

        assert response.status_code == 422
        data = response.json()
        assert "message" in data
        assert isinstance(data["message"], list)

    @pytest.mark.asyncio
    async def test_register_without_username(self, async_client: AsyncClient):
        """Test registration without optional username field."""
        user_data = {
            "email": "test_no_username@example.com",
            "password": "SecurePassword123!"
        }

        response = await async_client.post("/auth/register", json=user_data)

        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True

    @pytest.mark.asyncio
    async def test_register_empty_body(self, async_client: AsyncClient):
        """Test registration with empty request body."""
        response = await async_client.post("/auth/register", json={})

        assert response.status_code == 422
        data = response.json()
        assert "message" in data
        assert isinstance(data["message"], list)

    @pytest.mark.asyncio
    async def test_register_password_too_long(self, async_client: AsyncClient):
        """Test registration with password exceeding maximum length."""
        user_data = {
            "email": "test_long_password@example.com",
            "password": "a" * 200,  # Exceeds 128 char limit
            "username": "test_user"
        }

        response = await async_client.post("/auth/register", json=user_data)

        assert response.status_code == 422
        data = response.json()
        assert "message" in data
        assert isinstance(data["message"], list)
