"""
Tests for /auth/user-info endpoint (optional user info).
"""

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient


class TestUserInfoEndpoint:
    """Test class for optional user info endpoint."""

    async def get_valid_token(self, async_client: AsyncClient, test_user_credentials):
        """Helper method to get valid access token for testing."""
        login_response = await async_client.post("/auth/login", json=test_user_credentials)
        assert login_response.status_code == 200
        return login_response.json()["data"]["access_token"]

    @pytest.mark.asyncio
    async def test_user_info_with_valid_token_success(self, async_client: AsyncClient, test_user_credentials, auth_headers):
        """Test successful retrieval of user info with valid token."""
        # First login to get access token
        access_token = await self.get_valid_token(async_client, test_user_credentials)
        headers = auth_headers(access_token)

        response = await async_client.get("/auth/user-info", headers=headers)

        assert response.status_code == 200
        data = response.json()
        # Should return user data when authenticated
        assert data is not None
        assert "id" in data
        assert "email" in data
        assert data["email"] == test_user_credentials["email"]
        assert "is_active" in data
        assert "is_verified" in data

    @pytest.mark.asyncio
    async def test_user_info_without_token_returns_null(self, async_client: AsyncClient):
        """Test that user info returns null when not authenticated."""
        response = await async_client.get("/auth/user-info")

        assert response.status_code == 200
        data = response.json()
        # Should return null when not authenticated
        assert data is None

    @pytest.mark.asyncio
    async def test_user_info_with_invalid_token_returns_null(self, async_client: AsyncClient, auth_headers):
        """Test that user info returns null with invalid token."""
        headers = auth_headers("invalid_token_string")

        response = await async_client.get("/auth/user-info", headers=headers)

        assert response.status_code == 200
        data = response.json()
        # Should return null when token is invalid
        assert data is None

    @pytest.mark.asyncio
    async def test_user_info_with_expired_token_returns_null(self, async_client: AsyncClient, auth_headers):
        """Test that user info returns null with expired token."""
        expired_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyLCJleHAiOjE1MTYyMzkwMjJ9.invalid"
        headers = auth_headers(expired_token)

        response = await async_client.get("/auth/user-info", headers=headers)

        assert response.status_code == 200
        data = response.json()
        # Should return null when token is expired
        assert data is None

    @pytest.mark.asyncio
    async def test_user_info_with_malformed_authorization_header(self, async_client: AsyncClient):
        """Test user info with malformed authorization header."""
        headers = {"Authorization": "InvalidFormat token"}

        response = await async_client.get("/auth/user-info", headers=headers)

        assert response.status_code == 200
        data = response.json()
        # Should return null when authorization header is malformed
        assert data is None

    @pytest.mark.asyncio
    async def test_user_info_method_not_allowed(self, async_client: AsyncClient):
        """Test that only GET method is allowed for user info."""
        # Test POST method
        response = await async_client.post("/auth/user-info")
        assert response.status_code == 405

        # Test PUT method
        response = await async_client.put("/auth/user-info")
        assert response.status_code == 405

        # Test DELETE method
        response = await async_client.delete("/auth/user-info")
        assert response.status_code == 405

    @pytest.mark.asyncio
    async def test_user_info_response_structure_when_authenticated(self, async_client: AsyncClient, test_user_credentials, auth_headers):
        """Test that user info response has expected structure when authenticated."""
        # First login to get access token
        access_token = await self.get_valid_token(async_client, test_user_credentials)
        headers = auth_headers(access_token)

        response = await async_client.get("/auth/user-info", headers=headers)

        assert response.status_code == 200
        data = response.json()
        
        if data is not None:  # When authenticated
            assert isinstance(data, dict)
            assert "id" in data
            assert "email" in data
            assert "is_active" in data
            assert "is_verified" in data
            assert "created_at" in data
            assert "updated_at" in data
