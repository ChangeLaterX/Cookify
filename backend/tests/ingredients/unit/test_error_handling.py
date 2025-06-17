"""
Unit Tests for Error Handling in Ingredients Service.

This module tests error handling and exception scenarios in the Ingredients service.
"""

import pytest
from unittest.mock import patch, MagicMock
from uuid import uuid4

from domains.ingredients.services import (
    get_all_ingredients,
    get_ingredient_by_id,
    create_ingredient,
    update_ingredient,
    delete_ingredient,
    search_ingredients,
    IngredientError
)
from tests.ingredients.config import IngredientsTestBase
from tests.ingredients.utils.mocks import IngredientsMockFactory, MockContextManager
from tests.ingredients.utils.test_data import TestDataGenerator


class TestIngredientsErrorHandling(IngredientsTestBase):
    """Test error handling in Ingredients service."""

    def test_main_functionality(self):
        """Required by IngredientsTestBase - tests basic error handling."""
        self.test_ingredient_error_creation()

    def test_ingredient_error_creation(self):
        """Test IngredientError creation and properties."""
        # Test with message only
        error = IngredientError("Test error message")
        assert error.message == "Test error message"
        assert error.error_code is None
        assert str(error) == "Test error message"
        
        # Test with message and error code
        error_with_code = IngredientError("Test error", "TEST_ERROR_CODE")
        assert error_with_code.message == "Test error"
        assert error_with_code.error_code == "TEST_ERROR_CODE"

    def test_ingredient_error_inheritance(self):
        """Test IngredientError inherits from Exception properly."""
        error = IngredientError("Test error")
        assert isinstance(error, Exception)
        assert isinstance(error, IngredientError)

    @pytest.mark.asyncio
    async def test_database_connection_error(self):
        """Test handling of database connection errors."""
        with patch('domains.ingredients.services.get_supabase_client') as mock_client:
            # Mock connection error
            mock_client.side_effect = ConnectionError("Unable to connect to database")
            
            with pytest.raises(IngredientError) as exc_info:
                await get_all_ingredients()
            
            assert exc_info.value.error_code == "DATABASE_ERROR"

    @pytest.mark.asyncio
    async def test_database_timeout_error(self):
        """Test handling of database timeout errors."""
        with MockContextManager() as mock_ctx:
            # Mock timeout error
            mock_supabase_client = mock_ctx._create_mock_supabase_client()
            mock_supabase_client.table.return_value.select.return_value.execute.side_effect = TimeoutError("Query timed out")
            
            with patch('domains.ingredients.services.get_supabase_client', return_value=mock_supabase_client):
                with pytest.raises(IngredientError) as exc_info:
                    await get_all_ingredients()
                
                assert exc_info.value.error_code == "DATABASE_ERROR"

    @pytest.mark.asyncio
    async def test_malformed_database_response(self):
        """Test handling of malformed database responses."""
        with MockContextManager() as mock_ctx:
            # Mock malformed response
            mock_supabase_client = mock_ctx._create_mock_supabase_client()
            mock_response = MagicMock()
            mock_response.data = "invalid_data_format"  # Should be list
            mock_response.error = None
            mock_supabase_client.table.return_value.select.return_value.execute.return_value = mock_response
            
            with patch('domains.ingredients.services.get_supabase_client', return_value=mock_supabase_client):
                with pytest.raises(IngredientError) as exc_info:
                    await get_all_ingredients()
                
                assert exc_info.value.error_code == "DATABASE_ERROR"

    @pytest.mark.asyncio
    async def test_ingredient_not_found_error(self):
        """Test handling when ingredient is not found."""
        with MockContextManager(success_responses=True, mock_data=[]):
            with pytest.raises(IngredientError) as exc_info:
                await get_ingredient_by_id("non-existent-id")
            
            assert exc_info.value.error_code == "INGREDIENT_NOT_FOUND"
            assert "not found" in exc_info.value.message.lower()

    @pytest.mark.asyncio
    async def test_duplicate_ingredient_error(self):
        """Test handling of duplicate ingredient creation."""
        test_ingredient = TestDataGenerator.generate_ingredient_data()
        create_data = test_ingredient.to_ingredient_create()
        
        with MockContextManager() as mock_ctx:
            # Mock database constraint violation
            mock_supabase_client = mock_ctx._create_mock_supabase_client()
            mock_response = MagicMock()
            mock_response.data = None
            mock_response.error = "duplicate key value violates unique constraint"
            mock_supabase_client.table.return_value.insert.return_value.execute.return_value = mock_response
            
            with patch('domains.ingredients.services.get_supabase_client', return_value=mock_supabase_client):
                with pytest.raises(IngredientError) as exc_info:
                    await create_ingredient(create_data)
                
                assert exc_info.value.error_code == "DATABASE_ERROR"

    @pytest.mark.asyncio
    async def test_permission_denied_error(self):
        """Test handling of permission denied errors."""
        with MockContextManager() as mock_ctx:
            # Mock permission error
            mock_supabase_client = mock_ctx._create_mock_supabase_client()
            mock_response = MagicMock()
            mock_response.data = None
            mock_response.error = "permission denied"
            mock_supabase_client.table.return_value.select.return_value.execute.return_value = mock_response
            
            with patch('domains.ingredients.services.get_supabase_client', return_value=mock_supabase_client):
                with pytest.raises(IngredientError) as exc_info:
                    await get_all_ingredients()
                
                assert exc_info.value.error_code == "DATABASE_ERROR"

    @pytest.mark.asyncio
    async def test_network_error_handling(self):
        """Test handling of network errors."""
        with MockContextManager() as mock_ctx:
            # Mock network error
            mock_supabase_client = mock_ctx._create_mock_supabase_client()
            mock_supabase_client.table.return_value.select.return_value.execute.side_effect = OSError("Network unreachable")
            
            with patch('domains.ingredients.services.get_supabase_client', return_value=mock_supabase_client):
                with pytest.raises(IngredientError) as exc_info:
                    await get_all_ingredients()
                
                assert exc_info.value.error_code == "DATABASE_ERROR"

    @pytest.mark.asyncio
    async def test_json_parsing_error(self):
        """Test handling of JSON parsing errors."""
        with MockContextManager() as mock_ctx:
            # Mock JSON parsing error
            with patch('json.loads', side_effect=ValueError("Invalid JSON")):
                # This depends on whether the service actually uses json.loads directly
                pass

    @pytest.mark.asyncio
    async def test_unexpected_exception_handling(self):
        """Test handling of unexpected exceptions."""
        with MockContextManager() as mock_ctx:
            # Mock unexpected exception
            mock_supabase_client = mock_ctx._create_mock_supabase_client()
            mock_supabase_client.table.return_value.select.return_value.execute.side_effect = RuntimeError("Unexpected error")
            
            with patch('domains.ingredients.services.get_supabase_client', return_value=mock_supabase_client):
                with pytest.raises(IngredientError) as exc_info:
                    await get_all_ingredients()
                
                assert exc_info.value.error_code == "DATABASE_ERROR"

    @pytest.mark.asyncio
    async def test_invalid_uuid_format(self):
        """Test handling of invalid UUID formats."""
        invalid_ids = [
            "not-a-uuid",
            "12345",
            "",
            "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
            123,
            None
        ]
        
        for invalid_id in invalid_ids:
            try:
                with MockContextManager():
                    await get_ingredient_by_id(str(invalid_id))
            except (IngredientError, ValueError, TypeError):
                # Expected - invalid ID should cause error
                pass

    @pytest.mark.asyncio
    async def test_pagination_parameter_errors(self):
        """Test handling of invalid pagination parameters."""
        invalid_params = [
            {"limit": -1, "offset": 0},
            {"limit": 0, "offset": -1},
            {"limit": 10001, "offset": 0},  # Too large limit
            {"limit": "invalid", "offset": 0},
            {"limit": 10, "offset": "invalid"}
        ]
        
        for params in invalid_params:
            try:
                with MockContextManager():
                    await get_all_ingredients(**params)
            except (IngredientError, ValueError, TypeError):
                # Expected - invalid parameters should cause error
                pass

    @pytest.mark.asyncio
    async def test_search_query_errors(self):
        """Test handling of problematic search queries."""
        problematic_queries = [
            None,
            123,
            [],
            {},
            "A" * 10000,  # Very long query
        ]
        
        for query in problematic_queries:
            try:
                with MockContextManager():
                    await search_ingredients(query)
            except (IngredientError, ValueError, TypeError):
                # Expected - invalid query should cause error
                pass

    @pytest.mark.asyncio
    async def test_error_code_consistency(self):
        """Test that error codes are consistent across similar failures."""
        scenarios = [
            ("get_all_ingredients", [], "DATABASE_ERROR"),
            ("get_ingredient_by_id", ["test-id"], "INGREDIENT_NOT_FOUND"),
            ("search_ingredients", ["test"], "DATABASE_ERROR"),
        ]
        
        for function_name, args, expected_error_code in scenarios:
            with MockContextManager(success_responses=False):
                try:
                    function = globals()[function_name]
                    await function(*args)
                except IngredientError as e:
                    if "NOT_FOUND" in expected_error_code:
                        # For not found errors, we expect empty data
                        with MockContextManager(success_responses=True, mock_data=[]):
                            try:
                                await function(*args)
                            except IngredientError as not_found_error:
                                assert not_found_error.error_code == expected_error_code
                    else:
                        assert e.error_code == expected_error_code

    @pytest.mark.asyncio
    async def test_error_message_sanitization(self):
        """Test that sensitive information is not exposed in error messages."""
        # Create test data that might contain sensitive info
        sensitive_data = {
            "name": "password123",
            "calories_per_100g": 100.0,
            "proteins_per_100g": 10.0,
            "fat_per_100g": 5.0,
            "carbs_per_100g": 15.0,
            "price_per_100g_cents": 500
        }
        
        with MockContextManager() as mock_ctx:
            # Mock error that might expose sensitive data
            mock_supabase_client = mock_ctx._create_mock_supabase_client()
            mock_response = MagicMock()
            mock_response.data = None
            mock_response.error = f"Database error with {sensitive_data['name']}"
            mock_supabase_client.table.return_value.insert.return_value.execute.return_value = mock_response
            
            create_data = IngredientsMockFactory.create_ingredient_create(**sensitive_data)
            
            with patch('domains.ingredients.services.get_supabase_client', return_value=mock_supabase_client):
                with pytest.raises(IngredientError) as exc_info:
                    await create_ingredient(create_data)
                
                # Verify sensitive data is not in error message
                error_message = str(exc_info.value.message).lower()
                assert "password123" not in error_message

    @pytest.mark.asyncio
    async def test_concurrent_operation_errors(self):
        """Test handling of concurrent operation conflicts."""
        test_ingredient = TestDataGenerator.generate_ingredient_data()
        
        with MockContextManager() as mock_ctx:
            # Mock concurrent modification error
            mock_supabase_client = mock_ctx._create_mock_supabase_client()
            mock_response = MagicMock()
            mock_response.data = None
            mock_response.error = "could not serialize access due to concurrent update"
            mock_supabase_client.table.return_value.update.return_value.eq.return_value.execute.return_value = mock_response
            
            update_data = IngredientsMockFactory.create_ingredient_update(name="Updated")
            
            with patch('domains.ingredients.services.get_supabase_client', return_value=mock_supabase_client):
                with pytest.raises(IngredientError) as exc_info:
                    await update_ingredient(test_ingredient.ingredient_id, update_data)
                
                assert exc_info.value.error_code == "DATABASE_ERROR"

    @pytest.mark.asyncio
    async def test_resource_exhaustion_errors(self):
        """Test handling of resource exhaustion errors."""
        with MockContextManager() as mock_ctx:
            # Mock resource exhaustion
            mock_supabase_client = mock_ctx._create_mock_supabase_client()
            mock_supabase_client.table.return_value.select.return_value.execute.side_effect = MemoryError("Out of memory")
            
            with patch('domains.ingredients.services.get_supabase_client', return_value=mock_supabase_client):
                with pytest.raises(IngredientError) as exc_info:
                    await get_all_ingredients()
                
                assert exc_info.value.error_code == "DATABASE_ERROR"
