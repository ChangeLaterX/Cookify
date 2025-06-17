"""
Unit Tests for Complete Ingredients Workflows.

This module tests end-to-end ingredient management workflows.
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
from domains.ingredients.schemas import IngredientListResponse, IngredientMasterResponse
from tests.ingredients.config import IngredientsTestBase
from tests.ingredients.utils.mocks import IngredientsMockFactory, MockContextManager
from tests.ingredients.utils.test_data import TestDataGenerator, TestScenarios


class TestCompleteIngredientsWorkflows(IngredientsTestBase):
    """Test complete ingredient management workflows."""

    def test_main_functionality(self):
        """Required by IngredientsTestBase - tests basic workflow."""
        self.test_complete_crud_workflow()

    @pytest.mark.asyncio
    async def test_complete_crud_workflow(self):
        """Test complete CRUD workflow for ingredients."""
        test_ingredient = TestDataGenerator.generate_ingredient_data()
        
        with MockContextManager(success_responses=True) as mock_ctx:
            # Step 1: Create ingredient
            create_data = test_ingredient.to_ingredient_create()
            mock_create_data = [test_ingredient.to_dict()]
            
            mock_supabase_client = mock_ctx._create_mock_supabase_client()
            mock_supabase_client.table.return_value.insert.return_value.execute.return_value.data = mock_create_data
            
            with patch('domains.ingredients.services.get_supabase_client', return_value=mock_supabase_client):
                created_ingredient = await create_ingredient(create_data)
                
                assert isinstance(created_ingredient, IngredientMasterResponse)
                assert created_ingredient.name == test_ingredient.name
                
                # Step 2: Read ingredient
                mock_supabase_client.table.return_value.select.return_value.eq.return_value.execute.return_value.data = mock_create_data
                
                retrieved_ingredient = await get_ingredient_by_id(test_ingredient.ingredient_id)
                assert retrieved_ingredient.name == test_ingredient.name
                
                # Step 3: Update ingredient
                update_data = IngredientsMockFactory.create_ingredient_update(
                    name=f"{test_ingredient.name} Updated"
                )
                updated_ingredient_dict = test_ingredient.to_dict()
                updated_ingredient_dict["name"] = update_data.name
                mock_update_data = [updated_ingredient_dict]
                
                mock_supabase_client.table.return_value.update.return_value.eq.return_value.execute.return_value.data = mock_update_data
                
                updated_ingredient = await update_ingredient(test_ingredient.ingredient_id, update_data)
                assert updated_ingredient.name == update_data.name
                
                # Step 4: Delete ingredient
                mock_supabase_client.table.return_value.delete.return_value.eq.return_value.execute.return_value.data = []
                
                delete_result = await delete_ingredient(test_ingredient.ingredient_id)
                assert delete_result is True

    @pytest.mark.asyncio
    async def test_ingredient_lifecycle_management(self):
        """Test ingredient lifecycle management with multiple ingredients."""
        test_ingredients = TestDataGenerator.generate_bulk_ingredients(count=5)
        
        with MockContextManager(success_responses=True) as mock_ctx:
            mock_supabase_client = mock_ctx._create_mock_supabase_client()
            
            created_ingredients = []
            
            # Create multiple ingredients
            for ingredient_data in test_ingredients:
                create_data = ingredient_data.to_ingredient_create()
                mock_data = [ingredient_data.to_dict()]
                
                mock_supabase_client.table.return_value.insert.return_value.execute.return_value.data = mock_data
                
                with patch('domains.ingredients.services.get_supabase_client', return_value=mock_supabase_client):
                    created = await create_ingredient(create_data)
                    created_ingredients.append(created)
            
            # Verify all ingredients were created
            assert len(created_ingredients) == 5
            
            # Get all ingredients
            all_mock_data = [ing.to_dict() for ing in test_ingredients]
            mock_supabase_client.table.return_value.select.return_value.range.return_value.order.return_value.execute.return_value.data = all_mock_data
            
            with patch('domains.ingredients.services.get_supabase_client', return_value=mock_supabase_client):
                all_ingredients = await get_all_ingredients(limit=10, offset=0)
                assert len(all_ingredients.ingredients) == 5

    @pytest.mark.asyncio
    async def test_search_and_filter_workflow(self):
        """Test search and filtering workflow."""
        search_ingredients_data = TestDataGenerator.generate_search_test_data()
        
        with MockContextManager(success_responses=True) as mock_ctx:
            mock_supabase_client = mock_ctx._create_mock_supabase_client()
            
            # Test different search scenarios
            search_scenarios = TestScenarios.search_scenarios()
            
            for scenario in search_scenarios:
                # Filter ingredients based on expected matches
                matching_ingredients = []
                for expected_name in scenario["expected_matches"]:
                    for ingredient in scenario["ingredients"]:
                        if expected_name.lower() in ingredient.name.lower():
                            matching_ingredients.append(ingredient.to_dict())
                
                mock_supabase_client.table.return_value.select.return_value.ilike.return_value.execute.return_value.data = matching_ingredients
                
                with patch('domains.ingredients.services.get_supabase_client', return_value=mock_supabase_client):
                    results = await search_ingredients(scenario["query"])
                    
                    assert isinstance(results, IngredientListResponse)
                    assert len(results.ingredients) == len(scenario["expected_matches"])

    @pytest.mark.asyncio
    async def test_pagination_workflow(self):
        """Test pagination workflow with large datasets."""
        total_ingredients = TestDataGenerator.generate_pagination_test_data(50)
        
        with MockContextManager(success_responses=True) as mock_ctx:
            mock_supabase_client = mock_ctx._create_mock_supabase_client()
            
            # Test different pagination scenarios
            pagination_scenarios = TestScenarios.pagination_scenarios()
            
            for scenario in pagination_scenarios:
                start = scenario["offset"]
                end = start + scenario["limit"]
                page_ingredients = total_ingredients[start:end]
                mock_data = [ing.to_dict() for ing in page_ingredients]
                
                mock_supabase_client.table.return_value.select.return_value.range.return_value.order.return_value.execute.return_value.data = mock_data
                
                with patch('domains.ingredients.services.get_supabase_client', return_value=mock_supabase_client):
                    results = await get_all_ingredients(
                        limit=scenario["limit"],
                        offset=scenario["offset"]
                    )
                    
                    assert len(results.ingredients) == scenario["expected_items"]
                    assert results.limit == scenario["limit"]
                    assert results.offset == scenario["offset"]

    @pytest.mark.asyncio
    async def test_bulk_operations_workflow(self):
        """Test bulk operations workflow."""
        test_ingredients = TestDataGenerator.generate_bulk_ingredients(count=10)
        
        with MockContextManager(success_responses=True) as mock_ctx:
            mock_supabase_client = mock_ctx._create_mock_supabase_client()
            
            # Bulk create
            created_ingredients = []
            for ingredient_data in test_ingredients:
                create_data = ingredient_data.to_ingredient_create()
                mock_data = [ingredient_data.to_dict()]
                
                mock_supabase_client.table.return_value.insert.return_value.execute.return_value.data = mock_data
                
                with patch('domains.ingredients.services.get_supabase_client', return_value=mock_supabase_client):
                    created = await create_ingredient(create_data)
                    created_ingredients.append(created)
            
            assert len(created_ingredients) == 10
            
            # Bulk update
            updated_ingredients = []
            for i, ingredient in enumerate(created_ingredients):
                update_data = IngredientsMockFactory.create_ingredient_update(
                    name=f"Bulk Updated {i}"
                )
                
                updated_dict = test_ingredients[i].to_dict()
                updated_dict["name"] = update_data.name
                mock_data = [updated_dict]
                
                mock_supabase_client.table.return_value.update.return_value.eq.return_value.execute.return_value.data = mock_data
                
                with patch('domains.ingredients.services.get_supabase_client', return_value=mock_supabase_client):
                    updated = await update_ingredient(ingredient.ingredient_id, update_data)
                    updated_ingredients.append(updated)
            
            assert len(updated_ingredients) == 10
            
            # Bulk delete
            for ingredient in updated_ingredients:
                mock_supabase_client.table.return_value.delete.return_value.eq.return_value.execute.return_value.data = []
                
                with patch('domains.ingredients.services.get_supabase_client', return_value=mock_supabase_client):
                    deleted = await delete_ingredient(ingredient.ingredient_id)
                    assert deleted is True

    @pytest.mark.asyncio
    async def test_error_recovery_workflow(self):
        """Test error recovery in ingredient workflows."""
        test_ingredient = TestDataGenerator.generate_ingredient_data()
        
        with MockContextManager() as mock_ctx:
            mock_supabase_client = mock_ctx._create_mock_supabase_client()
            
            # Step 1: Creation fails initially
            mock_supabase_client.table.return_value.insert.return_value.execute.return_value.data = None
            mock_supabase_client.table.return_value.insert.return_value.execute.return_value.error = "Database error"
            
            create_data = test_ingredient.to_ingredient_create()
            
            with patch('domains.ingredients.services.get_supabase_client', return_value=mock_supabase_client):
                with pytest.raises(IngredientError):
                    await create_ingredient(create_data)
            
            # Step 2: Creation succeeds on retry
            mock_supabase_client.table.return_value.insert.return_value.execute.return_value.data = [test_ingredient.to_dict()]
            mock_supabase_client.table.return_value.insert.return_value.execute.return_value.error = None
            
            with patch('domains.ingredients.services.get_supabase_client', return_value=mock_supabase_client):
                created = await create_ingredient(create_data)
                assert created.name == test_ingredient.name

    @pytest.mark.asyncio
    async def test_concurrent_access_workflow(self):
        """Test concurrent access scenarios."""
        import asyncio
        
        test_ingredients = TestDataGenerator.generate_bulk_ingredients(count=5)
        
        with MockContextManager(success_responses=True) as mock_ctx:
            mock_supabase_client = mock_ctx._create_mock_supabase_client()
            
            # Create tasks for concurrent operations
            create_tasks = []
            for ingredient_data in test_ingredients:
                create_data = ingredient_data.to_ingredient_create()
                mock_data = [ingredient_data.to_dict()]
                
                mock_supabase_client.table.return_value.insert.return_value.execute.return_value.data = mock_data
                
                with patch('domains.ingredients.services.get_supabase_client', return_value=mock_supabase_client):
                    task = create_ingredient(create_data)
                    create_tasks.append(task)
            
            # Execute concurrently
            results = await asyncio.gather(*create_tasks, return_exceptions=True)
            
            # Verify all succeeded
            successful_results = [r for r in results if not isinstance(r, Exception)]
            assert len(successful_results) == len(test_ingredients)

    @pytest.mark.asyncio
    async def test_data_consistency_workflow(self):
        """Test data consistency throughout operations."""
        test_ingredient = TestDataGenerator.generate_ingredient_data()
        
        with MockContextManager(success_responses=True) as mock_ctx:
            mock_supabase_client = mock_ctx._create_mock_supabase_client()
            
            # Create ingredient
            create_data = test_ingredient.to_ingredient_create()
            mock_data = [test_ingredient.to_dict()]
            
            mock_supabase_client.table.return_value.insert.return_value.execute.return_value.data = mock_data
            
            with patch('domains.ingredients.services.get_supabase_client', return_value=mock_supabase_client):
                created = await create_ingredient(create_data)
                
                # Verify consistency
                assert created.name == test_ingredient.name
                assert created.calories_per_100g == test_ingredient.calories_per_100g
                assert created.proteins_per_100g == test_ingredient.proteins_per_100g
                assert created.fat_per_100g == test_ingredient.fat_per_100g
                assert created.carbs_per_100g == test_ingredient.carbs_per_100g
                assert created.price_per_100g_cents == test_ingredient.price_per_100g_cents

    @pytest.mark.asyncio
    async def test_performance_workflow(self):
        """Test performance-related workflows."""
        import time
        
        # Generate larger dataset for performance testing
        large_dataset = TestDataGenerator.generate_bulk_ingredients(count=100)
        page_size = 20
        
        with MockContextManager(success_responses=True) as mock_ctx:
            mock_supabase_client = mock_ctx._create_mock_supabase_client()
            
            # Test paginated retrieval performance
            start_time = time.time()
            
            pages = []
            for offset in range(0, len(large_dataset), page_size):
                page_data = large_dataset[offset:offset + page_size]
                mock_data = [ing.to_dict() for ing in page_data]
                
                mock_supabase_client.table.return_value.select.return_value.range.return_value.order.return_value.execute.return_value.data = mock_data
                
                with patch('domains.ingredients.services.get_supabase_client', return_value=mock_supabase_client):
                    page_result = await get_all_ingredients(limit=page_size, offset=offset)
                    pages.append(page_result)
            
            end_time = time.time()
            duration = end_time - start_time
            
            # Verify performance
            assert len(pages) == 5  # 100 items / 20 per page
            assert duration < 5.0  # Should complete within 5 seconds (with mocks)

    @pytest.mark.asyncio
    async def test_workflow_state_management(self):
        """Test state management throughout workflows."""
        test_ingredient = TestDataGenerator.generate_ingredient_data()
        
        with MockContextManager(success_responses=True) as mock_ctx:
            mock_supabase_client = mock_ctx._create_mock_supabase_client()
            
            # Track state changes through workflow
            states = []
            
            # Initial state: ingredient doesn't exist
            mock_supabase_client.table.return_value.select.return_value.eq.return_value.execute.return_value.data = []
            
            with patch('domains.ingredients.services.get_supabase_client', return_value=mock_supabase_client):
                try:
                    await get_ingredient_by_id(test_ingredient.ingredient_id)
                except IngredientError:
                    states.append("not_found")
            
            # State change: create ingredient
            mock_data = [test_ingredient.to_dict()]
            mock_supabase_client.table.return_value.insert.return_value.execute.return_value.data = mock_data
            
            with patch('domains.ingredients.services.get_supabase_client', return_value=mock_supabase_client):
                created = await create_ingredient(test_ingredient.to_ingredient_create())
                states.append("created")
            
            # State change: ingredient exists
            mock_supabase_client.table.return_value.select.return_value.eq.return_value.execute.return_value.data = mock_data
            
            with patch('domains.ingredients.services.get_supabase_client', return_value=mock_supabase_client):
                retrieved = await get_ingredient_by_id(test_ingredient.ingredient_id)
                states.append("exists")
            
            # State change: delete ingredient
            mock_supabase_client.table.return_value.delete.return_value.eq.return_value.execute.return_value.data = []
            
            with patch('domains.ingredients.services.get_supabase_client', return_value=mock_supabase_client):
                deleted = await delete_ingredient(test_ingredient.ingredient_id)
                states.append("deleted")
            
            # Verify state progression
            expected_states = ["not_found", "created", "exists", "deleted"]
            assert states == expected_states
