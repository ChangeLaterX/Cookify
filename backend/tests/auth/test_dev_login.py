"""
Tests for /auth/dev-login endpoint (development only).
"""

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient


class TestDevLoginEndpoint:
    """Test class for development login endpoint."""

    @pytest.mark.asyncio
    async def test_dev_login_success_in_debug_mode(self, async_client: AsyncClient):
        """Test successful development login when debug mode is enabled."""
        response = await async_client.post("/auth/dev-login")

        # Response depends on whether debug mode is enabled
        if response.status_code == 404:
            # Debug mode is disabled
            data = response.json()
            assert "message" in data
            assert isinstance(data["message"], list)
        elif response.status_code == 200:
            # Debug mode is enabled
            data = response.json()
            assert data["success"] is True
            assert "data" in data
            assert "access_token" in data["data"]
            assert "refresh_token" in data["data"]
            assert data["data"]["token_type"] == "bearer"
            assert "expires_in" in data["data"]
            assert "expires_at" in data["data"]
        else:
            # Unexpected status code
            pytest.fail(f"Unexpected status code: {response.status_code}")

    @pytest.mark.asyncio
    async def test_dev_login_method_not_allowed(self, async_client: AsyncClient):
        """Test that only POST method is allowed for dev login."""
        # Test GET method
        response = await async_client.get("/auth/dev-login")
        assert response.status_code in [404, 405]  # 404 if debug disabled, 405 if not allowed

        # Test PUT method
        response = await async_client.put("/auth/dev-login")
        assert response.status_code in [404, 405]

        # Test DELETE method
        response = await async_client.delete("/auth/dev-login")
        assert response.status_code in [404, 405]

    @pytest.mark.asyncio
    async def test_dev_login_no_body_required(self, async_client: AsyncClient):
        """Test that dev login doesn't require request body."""
        response = await async_client.post("/auth/dev-login")

        # Should work without any request body
        assert response.status_code in [200, 404]  # 404 if debug disabled

    @pytest.mark.asyncio
    async def test_dev_login_with_body_ignored(self, async_client: AsyncClient):
        """Test that dev login ignores request body if provided."""
        response = await async_client.post("/auth/dev-login", json={"ignored": "data"})

        # Should work and ignore the body
        assert response.status_code in [200, 404]  # 404 if debug disabled

    @pytest.mark.asyncio
    async def test_dev_login_response_structure(self, async_client: AsyncClient):
        """Test dev login response structure when successful."""
        response = await async_client.post("/auth/dev-login")

        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, dict)
            assert "success" in data
            assert "data" in data
            assert "message" in data
            
            # Check token structure
            token_data = data["data"]
            assert "access_token" in token_data
            assert "refresh_token" in token_data
            assert "token_type" in token_data
            assert "expires_in" in token_data
            assert "expires_at" in token_data
            
            # Tokens should be strings
            assert isinstance(token_data["access_token"], str)
            assert isinstance(token_data["refresh_token"], str)
            assert token_data["token_type"] == "bearer"

    @pytest.mark.asyncio
    async def test_dev_login_multiple_calls(self, async_client: AsyncClient):
        """Test multiple consecutive dev login calls."""
        # Make multiple calls to ensure endpoint is stable
        responses = []
        for _ in range(3):
            response = await async_client.post("/auth/dev-login")
            responses.append(response)
            assert response.status_code in [200, 404]

        # If any succeeded, they all should succeed
        if any(r.status_code == 200 for r in responses):
            assert all(r.status_code == 200 for r in responses)

    @pytest.mark.asyncio
    async def test_dev_login_tokens_are_different(self, async_client: AsyncClient):
        """Test that dev login generates different tokens each time."""
        import asyncio
        
        response1 = await async_client.post("/auth/dev-login")
        
        # Small delay to ensure different timestamps in JWT tokens
        await asyncio.sleep(1.1)
        
        response2 = await async_client.post("/auth/dev-login")

        if response1.status_code == 200 and response2.status_code == 200:
            data1 = response1.json()
            data2 = response2.json()
            
            # Tokens should be different on each call (due to different exp timestamps)
            assert data1["data"]["access_token"] != data2["data"]["access_token"]
            assert data1["data"]["refresh_token"] != data2["data"]["refresh_token"]
        else:
            # If endpoint is disabled, both should fail with same status
            assert response1.status_code == response2.status_code
