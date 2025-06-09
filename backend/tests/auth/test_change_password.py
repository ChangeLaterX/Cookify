"""
Tests for /auth/change-password endpoint.
"""

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient


class TestChangePasswordEndpoint:
    """Test class for change password endpoint."""

    async def get_valid_token(self, async_client: AsyncClient, test_user_credentials):
        """Helper method to get valid access token for testing."""
        login_response = await async_client.post("/auth/login", json=test_user_credentials)
        assert login_response.status_code == 200
        return login_response.json()["data"]["access_token"]

    @pytest.mark.asyncio
    async def test_change_password_valid_data_success(self, async_client: AsyncClient, test_user_credentials, auth_headers):
        """Test successful password change with valid current password."""
        # First login to get access token
        access_token = await self.get_valid_token(async_client, test_user_credentials)
        headers = auth_headers(access_token)

        password_data = {
            "old_password": test_user_credentials["password"],
            "new_password": "NewSecurePassword123!"
        }

        response = await async_client.post("/auth/change-password", json=password_data, headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "successfully" in data["message"].lower()

    @pytest.mark.asyncio
    async def test_change_password_wrong_old_password(self, async_client: AsyncClient, test_user_credentials, auth_headers):
        """Test password change with wrong current password."""
        # First login to get access token
        access_token = await self.get_valid_token(async_client, test_user_credentials)
        headers = auth_headers(access_token)

        password_data = {
            "old_password": "wrong_current_password",
            "new_password": "NewSecurePassword123!"
        }

        response = await async_client.post("/auth/change-password", json=password_data, headers=headers)

        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "error" in data["detail"]

    @pytest.mark.asyncio
    async def test_change_password_weak_new_password(self, async_client: AsyncClient, test_user_credentials, auth_headers):
        """Test password change with weak new password."""
        # First login to get access token
        access_token = await self.get_valid_token(async_client, test_user_credentials)
        headers = auth_headers(access_token)

        password_data = {
            "old_password": test_user_credentials["password"],
            "new_password": "123"  # Too weak
        }

        response = await async_client.post("/auth/change-password", json=password_data, headers=headers)

        assert response.status_code == 422
        data = response.json()
        assert "detail" in data

    @pytest.mark.asyncio
    async def test_change_password_invalid_token(self, async_client: AsyncClient, auth_headers):
        """Test password change with invalid access token."""
        headers = auth_headers("invalid_token_string")
        password_data = {
            "old_password": "current_password",
            "new_password": "NewSecurePassword123!"
        }

        response = await async_client.post("/auth/change-password", json=password_data, headers=headers)

        assert response.status_code in [401, 403]

    @pytest.mark.asyncio
    async def test_change_password_missing_authorization_header(self, async_client: AsyncClient):
        """Test password change without authorization header."""
        password_data = {
            "old_password": "current_password",
            "new_password": "NewSecurePassword123!"
        }

        response = await async_client.post("/auth/change-password", json=password_data)

        assert response.status_code in [401, 403, 422]

    @pytest.mark.asyncio
    async def test_change_password_missing_old_password(self, async_client: AsyncClient, test_user_credentials, auth_headers):
        """Test password change with missing old password field."""
        # First login to get access token
        access_token = await self.get_valid_token(async_client, test_user_credentials)
        headers = auth_headers(access_token)

        password_data = {
            "new_password": "NewSecurePassword123!"
        }

        response = await async_client.post("/auth/change-password", json=password_data, headers=headers)

        assert response.status_code == 422
        data = response.json()
        assert "detail" in data

    @pytest.mark.asyncio
    async def test_change_password_missing_new_password(self, async_client: AsyncClient, test_user_credentials, auth_headers):
        """Test password change with missing new password field."""
        # First login to get access token
        access_token = await self.get_valid_token(async_client, test_user_credentials)
        headers = auth_headers(access_token)

        password_data = {
            "old_password": test_user_credentials["password"]
        }

        response = await async_client.post("/auth/change-password", json=password_data, headers=headers)

        assert response.status_code == 422
        data = response.json()
        assert "detail" in data

    @pytest.mark.asyncio
    async def test_change_password_same_old_new_password(self, async_client: AsyncClient, test_user_credentials, auth_headers):
        """Test password change with same old and new password."""
        # First login to get access token
        access_token = await self.get_valid_token(async_client, test_user_credentials)
        headers = auth_headers(access_token)

        password_data = {
            "old_password": test_user_credentials["password"],
            "new_password": test_user_credentials["password"]  # Same as old
        }

        response = await async_client.post("/auth/change-password", json=password_data, headers=headers)

        # Depending on implementation, might allow or reject same password
        assert response.status_code in [200, 400, 422]

    @pytest.mark.asyncio
    async def test_change_password_empty_body(self, async_client: AsyncClient, test_user_credentials, auth_headers):
        """Test password change with empty request body."""
        # First login to get access token
        access_token = await self.get_valid_token(async_client, test_user_credentials)
        headers = auth_headers(access_token)

        response = await async_client.post("/auth/change-password", json={}, headers=headers)

        assert response.status_code == 422
        data = response.json()
        assert "detail" in data
