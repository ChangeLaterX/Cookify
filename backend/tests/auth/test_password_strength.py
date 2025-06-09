"""
Tests for /auth/check-password-strength endpoint.
"""

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient


class TestPasswordStrengthEndpoint:
    """Test class for password strength check endpoint."""

    async def get_valid_token(self, async_client: AsyncClient, test_user_credentials):
        """Helper method to get valid access token for testing."""
        login_response = await async_client.post("/auth/login", json=test_user_credentials)
        assert login_response.status_code == 200
        return login_response.json()["data"]["access_token"]

    @pytest.mark.asyncio
    async def test_password_strength_strong_password(self, async_client: AsyncClient):
        """Test password strength check with strong password."""
        strength_data = {
            "password": "VerySecurePassword123!@#"
        }

        response = await async_client.post("/auth/check-password-strength", json=strength_data)

        assert response.status_code == 200
        data = response.json()
        assert "strength" in data
        assert "score" in data
        assert "is_valid" in data
        assert "strength_label" in data
        assert "requirements" in data
        assert isinstance(data["requirements"], list)
        
        # Strong password should have high strength
        assert data["strength"] >= 3  # Assuming 0-5 scale
        assert data["is_valid"] is True

    @pytest.mark.asyncio
    async def test_password_strength_weak_password(self, async_client: AsyncClient):
        """Test password strength check with weak password."""
        strength_data = {
            "password": "123"
        }

        response = await async_client.post("/auth/check-password-strength", json=strength_data)

        assert response.status_code == 200
        data = response.json()
        assert "strength" in data
        assert "score" in data
        assert "is_valid" in data
        assert "strength_label" in data
        
        # Weak password should have low strength
        assert data["strength"] <= 2
        assert data["is_valid"] is False

    @pytest.mark.asyncio
    async def test_password_strength_with_authentication(self, async_client: AsyncClient, test_user_credentials, auth_headers):
        """Test password strength check while authenticated (for personal info checks)."""
        # First login to get access token
        access_token = await self.get_valid_token(async_client, test_user_credentials)
        headers = auth_headers(access_token)

        strength_data = {
            "password": "SecurePassword123!"
        }

        response = await async_client.post("/auth/check-password-strength", json=strength_data, headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert "strength" in data
        assert "score" in data
        assert "is_valid" in data

    @pytest.mark.asyncio
    async def test_password_strength_personal_info_detection(self, async_client: AsyncClient, test_user_credentials, auth_headers):
        """Test password strength detects personal information when authenticated."""
        # First login to get access token
        access_token = await self.get_valid_token(async_client, test_user_credentials)
        headers = auth_headers(access_token)

        # Use email as password (should be detected as personal info)
        strength_data = {
            "password": test_user_credentials["email"]
        }

        response = await async_client.post("/auth/check-password-strength", json=strength_data, headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert data["is_valid"] is False
        # Should have warnings or errors about personal information
        assert "errors" in data or "warnings" in data

    @pytest.mark.asyncio
    async def test_password_strength_common_password(self, async_client: AsyncClient):
        """Test password strength check with common password."""
        strength_data = {
            "password": "password123"  # Common weak password
        }

        response = await async_client.post("/auth/check-password-strength", json=strength_data)

        assert response.status_code == 200
        data = response.json()
        assert data["is_valid"] is False
        assert "errors" in data or "warnings" in data

    @pytest.mark.asyncio
    async def test_password_strength_missing_password(self, async_client: AsyncClient):
        """Test password strength check with missing password field."""
        strength_data = {}

        response = await async_client.post("/auth/check-password-strength", json=strength_data)

        assert response.status_code == 422
        data = response.json()
        assert "detail" in data

    @pytest.mark.asyncio
    async def test_password_strength_empty_password(self, async_client: AsyncClient):
        """Test password strength check with empty password."""
        strength_data = {
            "password": ""
        }

        response = await async_client.post("/auth/check-password-strength", json=strength_data)

        assert response.status_code == 200
        data = response.json()
        assert data["is_valid"] is False
        assert data["strength"] == 0  # Assuming 0 is lowest

    @pytest.mark.asyncio
    async def test_password_strength_very_long_password(self, async_client: AsyncClient):
        """Test password strength check with very long password."""
        strength_data = {
            "password": "a" * 200  # Very long password
        }

        response = await async_client.post("/auth/check-password-strength", json=strength_data)

        assert response.status_code == 200
        data = response.json()
        # Might be invalid due to length restriction
        assert "is_valid" in data

    @pytest.mark.asyncio
    async def test_password_strength_requirements_structure(self, async_client: AsyncClient):
        """Test that requirements array has proper structure."""
        strength_data = {
            "password": "TestPassword123!"
        }

        response = await async_client.post("/auth/check-password-strength", json=strength_data)

        assert response.status_code == 200
        data = response.json()
        assert "requirements" in data
        assert isinstance(data["requirements"], list)
        
        if len(data["requirements"]) > 0:
            requirement = data["requirements"][0]
            assert "key" in requirement
            assert "met" in requirement
            assert "description" in requirement
            assert isinstance(requirement["met"], bool)

    @pytest.mark.asyncio
    async def test_password_strength_empty_body(self, async_client: AsyncClient):
        """Test password strength check with empty request body."""
        response = await async_client.post("/auth/check-password-strength", json={})

        assert response.status_code == 422
        data = response.json()
        assert "detail" in data
