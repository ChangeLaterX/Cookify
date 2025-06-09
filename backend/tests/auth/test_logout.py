"""
Tests for /auth/logout endpoint.
"""

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient


class TestLogoutEndpoint:
    """Test class for user logout endpoint."""

    async def get_valid_token(self, async_client: AsyncClient, test_user_credentials):
        """Helper method to get valid access token for testing."""
        login_response = await async_client.post("/auth/login", json=test_user_credentials)
        assert login_response.status_code == 200
        return login_response.json()["data"]["access_token"]

    @pytest.mark.asyncio
    async def test_logout_valid_token_success(self, async_client: AsyncClient, test_user_credentials, auth_headers):
        """Test successful logout with valid access token."""
        # First login to get access token
        access_token = await self.get_valid_token(async_client, test_user_credentials)
        headers = auth_headers(access_token)

        response = await async_client.post("/auth/logout", headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "successfully" in data["message"].lower()

    @pytest.mark.asyncio
    async def test_logout_invalid_token(self, async_client: AsyncClient, auth_headers):
        """Test logout with invalid access token."""
        headers = auth_headers("invalid_token_string")

        response = await async_client.post("/auth/logout", headers=headers)

        assert response.status_code in [401, 403]

    @pytest.mark.asyncio
    async def test_logout_expired_token(self, async_client: AsyncClient, auth_headers):
        """Test logout with expired access token."""
        # Use a known expired token format
        expired_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyLCJleHAiOjE1MTYyMzkwMjJ9.invalid"
        headers = auth_headers(expired_token)

        response = await async_client.post("/auth/logout", headers=headers)

        assert response.status_code in [401, 403]

    @pytest.mark.asyncio
    async def test_logout_missing_authorization_header(self, async_client: AsyncClient):
        """Test logout without authorization header."""
        response = await async_client.post("/auth/logout")

        assert response.status_code in [401, 403, 422]

    @pytest.mark.asyncio
    async def test_logout_malformed_authorization_header(self, async_client: AsyncClient):
        """Test logout with malformed authorization header."""
        headers = {"Authorization": "InvalidFormat token"}

        response = await async_client.post("/auth/logout", headers=headers)

        assert response.status_code in [401, 403, 422]

    @pytest.mark.asyncio
    async def test_logout_empty_token(self, async_client: AsyncClient):
        """Test logout with empty bearer token."""
        headers = {"Authorization": "Bearer "}

        response = await async_client.post("/auth/logout", headers=headers)

        assert response.status_code in [401, 403, 422]

    @pytest.mark.asyncio
    async def test_logout_without_bearer_prefix(self, async_client: AsyncClient):
        """Test logout with token but without Bearer prefix."""
        headers = {"Authorization": "some_token_without_bearer"}

        response = await async_client.post("/auth/logout", headers=headers)

        assert response.status_code in [401, 403, 422]
