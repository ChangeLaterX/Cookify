"""
Tests for /auth/health endpoint.
"""

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient


class TestHealthEndpoint:
    """Test class for auth service health check endpoint."""

    @pytest.mark.asyncio
    async def test_health_check_success(self, async_client: AsyncClient):
        """Test successful health check."""
        response = await async_client.get("/auth/health")

        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "healthy" in data["message"].lower()
        if "details" in data:
            assert "service" in data["details"]
            assert "status" in data["details"]

    @pytest.mark.asyncio
    async def test_health_check_no_auth_required(self, async_client: AsyncClient):
        """Test that health check doesn't require authentication."""
        # Should work without any authorization headers
        response = await async_client.get("/auth/health")

        assert response.status_code == 200
        data = response.json()
        assert "message" in data

    @pytest.mark.asyncio
    async def test_health_check_method_not_allowed(self, async_client: AsyncClient):
        """Test that only GET method is allowed for health check."""
        # Test POST method
        response = await async_client.post("/auth/health")
        assert response.status_code == 405

        # Test PUT method
        response = await async_client.put("/auth/health")
        assert response.status_code == 405

        # Test DELETE method
        response = await async_client.delete("/auth/health")
        assert response.status_code == 405

    @pytest.mark.asyncio
    async def test_health_check_response_structure(self, async_client: AsyncClient):
        """Test that health check response has expected structure."""
        response = await async_client.get("/auth/health")

        assert response.status_code == 200
        data = response.json()
        
        # Should have message field
        assert "message" in data
        assert isinstance(data["message"], str)
        
        # May have details field
        if "details" in data:
            assert isinstance(data["details"], dict)

    @pytest.mark.asyncio
    async def test_health_check_multiple_calls(self, async_client: AsyncClient):
        """Test multiple consecutive health check calls."""
        import asyncio
        
        # Make multiple calls to ensure endpoint is stable
        for i in range(5):
            response = await async_client.get("/auth/health")
            assert response.status_code == 200
            data = response.json()
            assert "message" in data
            
            # Small delay between requests to avoid rate limiting
            if i < 4:  # Don't wait after the last request
                await asyncio.sleep(0.5)
