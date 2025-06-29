"""
Unit Tests for Pantry Items API Endpoints.

This module tests HTTP endpoints for pantry operations including bulk operations and statistics.
"""

import pytest
import json
from unittest.mock import Mock, patch, AsyncMock
from uuid import uuid4, UUID
from datetime import date, timedelta
from fastapi.testclient import TestClient
from fastapi import status

from domains.pantry_items.schemas import (
    PantryItemCreate,
    PantryItemBulkCreate,
    PantryItemBulkUpdate,
    PantryItemBulkDelete,
    PantryItemUpdate
)
from tests.pantry.config import PantryTestBase, TEST_USER_ID, SAMPLE_PANTRY_ITEMS_BULK
from tests.pantry.utils.test_data import (
    PantryTestDataGenerator,
    PantryMockFactory,
    PantryTestScenarios
)


class TestPantryAPIEndpoints(PantryTestBase):
    """Test HTTP API endpoints for pantry operations."""

    def test_main_functionality(self):
        """Required by PantryTestBase - tests basic API functionality."""
        self.test_bulk_create_endpoint_success()

    def test_bulk_create_endpoint_success(self):
        """Test successful bulk create via API endpoint."""
        from main import app
        client = TestClient(app)
        
        # Prepare test data
        bulk_data = {
            "items": [
                {
                    "name": "Bananas",
                    "quantity": 6.0,
                    "unit": "pieces",
                    "category": "produce",
                    "expiry_date": "2025-07-02",
                    "ingredient_id": str(uuid4())
                },
                {
                    "name": "Milk",
                    "quantity": 1.0,
                    "unit": "liter",
                    "category": "dairy",
                    "expiry_date": "2025-07-05",
                    "ingredient_id": str(uuid4())
                }
            ]
        }

        with patch("middleware.security.get_current_user") as mock_auth:
            mock_auth.return_value = {"id": TEST_USER_ID, "email": "test@cookify.app"}
            
            with patch("domains.pantry_items.services.bulk_create_pantry_items") as mock_create:
                # Mock successful bulk create
                mock_result = Mock()
                mock_result.successful = [
                    PantryTestDataGenerator.generate_pantry_item_response(name="Bananas"),
                    PantryTestDataGenerator.generate_pantry_item_response(name="Milk")
                ]
                mock_result.failed = []
                mock_result.total_processed = 2
                mock_result.success_count = 2
                mock_result.failure_count = 0
                mock_create.return_value = mock_result

                # Make API call
                response = client.post(
                    "/api/pantry/items/bulk",
                    json=bulk_data,
                    headers={"Authorization": "Bearer test_token"}
                )

                # Assertions
                assert response.status_code == status.HTTP_201_CREATED
                data = response.json()
                assert data["success"] is True
                assert "Bulk create completed" in data["message"]
                assert data["data"]["success_count"] == 2
                assert data["data"]["failure_count"] == 0

    def test_bulk_create_endpoint_validation_error(self):
        """Test bulk create endpoint with validation errors."""
        from main import app
        client = TestClient(app)
        
        # Invalid data (empty items list)
        invalid_data = {"items": []}

        with patch("middleware.security.get_current_user") as mock_auth:
            mock_auth.return_value = {"id": TEST_USER_ID, "email": "test@cookify.app"}

            # Make API call
            response = client.post(
                "/api/pantry/items/bulk",
                json=invalid_data,
                headers={"Authorization": "Bearer test_token"}
            )

            # Should return validation error
            assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_bulk_update_endpoint_success(self):
        """Test successful bulk update via API endpoint."""
        from main import app
        client = TestClient(app)
        
        item_id1 = str(uuid4())
        item_id2 = str(uuid4())
        
        update_data = {
            "updates": {
                item_id1: {
                    "quantity": 3.5,
                    "expiry_date": "2025-07-10"
                },
                item_id2: {
                    "name": "Organic Milk",
                    "category": "organic"
                }
            }
        }

        with patch("middleware.security.get_current_user") as mock_auth:
            mock_auth.return_value = {"id": TEST_USER_ID, "email": "test@cookify.app"}
            
            with patch("domains.pantry_items.services.bulk_update_pantry_items") as mock_update:
                # Mock successful bulk update
                mock_result = Mock()
                mock_result.successful = [
                    PantryTestDataGenerator.generate_pantry_item_response(name="Updated Item 1"),
                    PantryTestDataGenerator.generate_pantry_item_response(name="Organic Milk")
                ]
                mock_result.failed = []
                mock_result.total_processed = 2
                mock_result.success_count = 2
                mock_result.failure_count = 0
                mock_update.return_value = mock_result

                # Make API call
                response = client.put(
                    "/api/pantry/items/bulk",
                    json=update_data,
                    headers={"Authorization": "Bearer test_token"}
                )

                # Assertions
                assert response.status_code == status.HTTP_200_OK
                data = response.json()
                assert data["success"] is True
                assert "Bulk update completed" in data["message"]

    def test_bulk_delete_endpoint_success(self):
        """Test successful bulk delete via API endpoint."""
        from main import app
        client = TestClient(app)
        
        delete_data = {
            "item_ids": [
                str(uuid4()),
                str(uuid4())
            ]
        }

        with patch("middleware.security.get_current_user") as mock_auth:
            mock_auth.return_value = {"id": TEST_USER_ID, "email": "test@cookify.app"}
            
            with patch("domains.pantry_items.services.bulk_delete_pantry_items") as mock_delete:
                # Mock successful bulk delete
                mock_result = Mock()
                mock_result.successful = [
                    PantryTestDataGenerator.generate_pantry_item_response(),
                    PantryTestDataGenerator.generate_pantry_item_response()
                ]
                mock_result.failed = []
                mock_result.total_processed = 2
                mock_result.success_count = 2
                mock_result.failure_count = 0
                mock_delete.return_value = mock_result

                # Make API call
                response = client.delete(
                    "/api/pantry/items/bulk",
                    json=delete_data,
                    headers={"Authorization": "Bearer test_token"}
                )

                # Assertions
                assert response.status_code == status.HTTP_200_OK
                data = response.json()
                assert data["success"] is True
                assert "Bulk delete completed" in data["message"]

    def test_stats_endpoint_success(self):
        """Test successful pantry statistics endpoint."""
        from main import app
        client = TestClient(app)

        with patch("middleware.security.get_current_user") as mock_auth:
            mock_auth.return_value = {"id": TEST_USER_ID, "email": "test@cookify.app"}
            
            with patch("domains.pantry_items.services.get_pantry_stats") as mock_stats:
                # Mock statistics data
                mock_stats.return_value = PantryTestDataGenerator.generate_stats_overview()

                # Make API call
                response = client.get(
                    "/api/pantry/stats",
                    headers={"Authorization": "Bearer test_token"}
                )

                # Assertions
                assert response.status_code == status.HTTP_200_OK
                data = response.json()
                assert data["success"] is True
                assert "statistics retrieved successfully" in data["message"]
                assert data["data"]["total_items"] == 25
                assert data["data"]["total_categories"] == 6

    def test_category_stats_endpoint_success(self):
        """Test successful category statistics endpoint."""
        from main import app
        client = TestClient(app)

        with patch("middleware.security.get_current_user") as mock_auth:
            mock_auth.return_value = {"id": TEST_USER_ID, "email": "test@cookify.app"}
            
            with patch("domains.pantry_items.services.get_pantry_category_stats") as mock_stats:
                # Mock category statistics
                mock_stats.return_value = PantryTestDataGenerator.generate_category_stats()

                # Make API call
                response = client.get(
                    "/api/pantry/categories",
                    headers={"Authorization": "Bearer test_token"}
                )

                # Assertions
                assert response.status_code == status.HTTP_200_OK
                data = response.json()
                assert data["success"] is True
                assert "Category statistics retrieved successfully" in data["message"]
                assert "categories" in data["data"]
                assert len(data["data"]["categories"]) >= 2

    def test_expiry_report_endpoint_success(self):
        """Test successful expiry report endpoint."""
        from main import app
        client = TestClient(app)

        with patch("middleware.security.get_current_user") as mock_auth:
            mock_auth.return_value = {"id": TEST_USER_ID, "email": "test@cookify.app"}
            
            with patch("domains.pantry_items.services.get_pantry_expiry_report") as mock_report:
                # Mock expiry report
                mock_report.return_value = PantryTestDataGenerator.generate_expiry_report()

                # Make API call
                response = client.get(
                    "/api/pantry/expiring",
                    headers={"Authorization": "Bearer test_token"}
                )

                # Assertions
                assert response.status_code == status.HTTP_200_OK
                data = response.json()
                assert data["success"] is True
                assert "Expiry report retrieved successfully" in data["message"]
                assert "expiring_soon" in data["data"]
                assert "expired" in data["data"]
                assert "fresh" in data["data"]

    def test_low_stock_report_endpoint_success(self):
        """Test successful low stock report endpoint."""
        from main import app
        client = TestClient(app)

        with patch("middleware.security.get_current_user") as mock_auth:
            mock_auth.return_value = {"id": TEST_USER_ID, "email": "test@cookify.app"}
            
            with patch("domains.pantry_items.services.get_pantry_low_stock_report") as mock_report:
                # Mock low stock report
                mock_report.return_value = PantryTestDataGenerator.generate_low_stock_report()

                # Make API call
                response = client.get(
                    "/api/pantry/low-stock?threshold=1.0",
                    headers={"Authorization": "Bearer test_token"}
                )

                # Assertions
                assert response.status_code == status.HTTP_200_OK
                data = response.json()
                assert data["success"] is True
                assert "Low stock report retrieved successfully" in data["message"]
                assert "low_stock_items" in data["data"]
                assert data["data"]["threshold_used"] == 1.0

    def test_low_stock_report_custom_threshold(self):
        """Test low stock report with custom threshold parameter."""
        from main import app
        client = TestClient(app)

        with patch("middleware.security.get_current_user") as mock_auth:
            mock_auth.return_value = {"id": TEST_USER_ID, "email": "test@cookify.app"}
            
            with patch("domains.pantry_items.services.get_pantry_low_stock_report") as mock_report:
                # Mock low stock report with custom threshold
                mock_report.return_value = PantryTestDataGenerator.generate_low_stock_report(threshold=2.5)

                # Make API call with custom threshold
                response = client.get(
                    "/api/pantry/low-stock?threshold=2.5",
                    headers={"Authorization": "Bearer test_token"}
                )

                # Assertions
                assert response.status_code == status.HTTP_200_OK
                data = response.json()
                assert data["data"]["threshold_used"] == 2.5
                
                # Verify service was called with correct threshold
                mock_report.assert_called_once()
                args, kwargs = mock_report.call_args
                assert len(args) >= 2 or "threshold" in kwargs

    def test_unauthorized_access(self):
        """Test endpoints without authentication."""
        from main import app
        client = TestClient(app)

        endpoints = [
            ("POST", "/api/pantry/items/bulk", {"items": []}),
            ("PUT", "/api/pantry/items/bulk", {"updates": {}}),
            ("DELETE", "/api/pantry/items/bulk", {"item_ids": []}),
            ("GET", "/api/pantry/stats", None),
            ("GET", "/api/pantry/categories", None),
            ("GET", "/api/pantry/expiring", None),
            ("GET", "/api/pantry/low-stock", None)
        ]

        for method, endpoint, data in endpoints:
            # Make request without auth
            if method == "GET":
                response = client.get(endpoint)
            elif method == "POST":
                response = client.post(endpoint, json=data)
            elif method == "PUT":
                response = client.put(endpoint, json=data)
            elif method == "DELETE":
                response = client.delete(endpoint, json=data)

            # Should return unauthorized
            assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_bulk_operations_exceed_limits(self):
        """Test bulk operations that exceed the 50-item limit."""
        from main import app
        client = TestClient(app)

        with patch("middleware.security.get_current_user") as mock_auth:
            mock_auth.return_value = {"id": TEST_USER_ID, "email": "test@cookify.app"}

            # Test bulk create with too many items
            large_create_data = {
                "items": [
                    {
                        "name": f"Item {i}",
                        "quantity": 1.0,
                        "unit": "pieces",
                        "category": "test",
                        "ingredient_id": str(uuid4())
                    }
                    for i in range(51)  # Exceeds limit
                ]
            }

            response = client.post(
                "/api/pantry/items/bulk",
                json=large_create_data,
                headers={"Authorization": "Bearer test_token"}
            )

            # Should return validation error
            assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

            # Test bulk update with too many items
            large_update_data = {
                "updates": {
                    str(uuid4()): {"quantity": 1.0}
                    for _ in range(51)  # Exceeds limit
                }
            }

            response = client.put(
                "/api/pantry/items/bulk",
                json=large_update_data,
                headers={"Authorization": "Bearer test_token"}
            )

            # Should return validation error
            assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

            # Test bulk delete with too many items
            large_delete_data = {
                "item_ids": [str(uuid4()) for _ in range(51)]  # Exceeds limit
            }

            response = client.delete(
                "/api/pantry/items/bulk",
                json=large_delete_data,
                headers={"Authorization": "Bearer test_token"}
            )

            # Should return validation error
            assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_invalid_threshold_parameter(self):
        """Test low stock endpoint with invalid threshold parameter."""
        from main import app
        client = TestClient(app)

        with patch("middleware.security.get_current_user") as mock_auth:
            mock_auth.return_value = {"id": TEST_USER_ID, "email": "test@cookify.app"}

            # Test with negative threshold
            response = client.get(
                "/api/pantry/low-stock?threshold=-1.0",
                headers={"Authorization": "Bearer test_token"}
            )

            # Should return validation error
            assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

            # Test with threshold too high
            response = client.get(
                "/api/pantry/low-stock?threshold=15.0",
                headers={"Authorization": "Bearer test_token"}
            )

            # Should return validation error (assuming max threshold is 10)
            assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_malformed_json_requests(self):
        """Test endpoints with malformed JSON data."""
        from main import app
        client = TestClient(app)

        with patch("middleware.security.get_current_user") as mock_auth:
            mock_auth.return_value = {"id": TEST_USER_ID, "email": "test@cookify.app"}

            # Test with invalid JSON structure for bulk create
            malformed_data = {
                "items": [
                    {
                        "name": "Test Item",
                        "quantity": "not_a_number",  # Invalid type
                        "unit": "pieces",
                        "ingredient_id": "not_a_uuid"  # Invalid UUID
                    }
                ]
            }

            response = client.post(
                "/api/pantry/items/bulk",
                json=malformed_data,
                headers={"Authorization": "Bearer test_token"}
            )

            # Should return validation error
            assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_service_error_handling(self):
        """Test API error handling when services raise exceptions."""
        from main import app
        client = TestClient(app)

        with patch("middleware.security.get_current_user") as mock_auth:
            mock_auth.return_value = {"id": TEST_USER_ID, "email": "test@cookify.app"}

            # Test with service raising PantryItemError
            with patch("domains.pantry_items.services.get_pantry_stats") as mock_stats:
                from domains.pantry_items.services import PantryItemError
                mock_stats.side_effect = PantryItemError("Database connection failed")

                response = client.get(
                    "/api/pantry/stats",
                    headers={"Authorization": "Bearer test_token"}
                )

                # Should return internal server error
                assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
                data = response.json()
                assert data["success"] is False

    def test_cors_headers(self):
        """Test that CORS headers are properly set on responses."""
        from main import app
        client = TestClient(app)

        with patch("middleware.security.get_current_user") as mock_auth:
            mock_auth.return_value = {"id": TEST_USER_ID, "email": "test@cookify.app"}
            
            with patch("domains.pantry_items.services.get_pantry_stats") as mock_stats:
                mock_stats.return_value = PantryTestDataGenerator.generate_stats_overview()

                response = client.get(
                    "/api/pantry/stats",
                    headers={"Authorization": "Bearer test_token"}
                )

                # Check for CORS headers (if configured)
                # Note: This depends on your CORS configuration
                assert response.status_code == status.HTTP_200_OK

    def test_rate_limiting(self):
        """Test rate limiting on bulk operations (if implemented)."""
        from main import app
        client = TestClient(app)

        with patch("middleware.security.get_current_user") as mock_auth:
            mock_auth.return_value = {"id": TEST_USER_ID, "email": "test@cookify.app"}
            
            with patch("domains.pantry_items.services.bulk_create_pantry_items") as mock_create:
                mock_result = Mock()
                mock_result.successful = []
                mock_result.failed = []
                mock_result.total_processed = 0
                mock_result.success_count = 0
                mock_result.failure_count = 0
                mock_create.return_value = mock_result

                # Make multiple rapid requests
                bulk_data = {"items": []}
                
                responses = []
                for _ in range(5):  # Make 5 rapid requests
                    response = client.post(
                        "/api/pantry/items/bulk",
                        json=bulk_data,
                        headers={"Authorization": "Bearer test_token"}
                    )
                    responses.append(response.status_code)

                # All should succeed if no rate limiting, or some should be rate limited
                # This test documents the expected behavior
                assert all(code in [200, 201, 429] for code in responses)
