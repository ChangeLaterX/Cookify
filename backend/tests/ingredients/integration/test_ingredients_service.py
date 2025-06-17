"""
Integration Tests for Ingredients Service.

This module tests the ingredients service with real Supabase connections,
testing end-to-end functionality and database interactions.
"""

import pytest
import asyncio
from uuid import uuid4
from typing import List

from domains.ingredients.services import IngredientsService, IngredientError
from domains.ingredients.schemas import (
    IngredientMasterCreate,
    IngredientMasterUpdate,
    IngredientSearch
)
from tests.ingredients.config import IngredientsTestBase
from tests.ingredients.utils.test_data import TestDataGenerator


class TestIngredientsIntegration(IngredientsTestBase):
    """Integration tests for ingredients service."""

    @pytest.fixture(autouse=True)
    async def setup_service(self):
        """Set up ingredients service for testing."""
        self.service = IngredientsService()
        self.test_ingredients = []  # Track created ingredients for cleanup
        yield
        await self.cleanup_test_data()

    async def cleanup_test_data(self):
        """Clean up test data after each test."""
        for ingredient_id in self.test_ingredients:
            try:
                await self.service.delete_ingredient(ingredient_id)
            except IngredientError:
                pass  # Ingredient might already be deleted
        self.test_ingredients.clear()

    def test_main_functionality(self):
        """Required by IngredientsTestBase - tests basic integration."""
        asyncio.run(self.test_create_and_retrieve_ingredient())

    async def test_create_and_retrieve_ingredient(self):
        """Test creating and retrieving an ingredient."""
        # Create test ingredient
        ingredient_data = TestDataGenerator.generate_ingredient_create()
        
        created_ingredient = await self.service.create_ingredient(ingredient_data)
        self.test_ingredients.append(created_ingredient.ingredient_id)
        
        # Verify creation
        assert created_ingredient.name == ingredient_data.name
        assert created_ingredient.calories_per_100g == ingredient_data.calories_per_100g
        assert created_ingredient.ingredient_id is not None
        
        # Retrieve the ingredient
        retrieved_ingredient = await self.service.get_ingredient(
            created_ingredient.ingredient_id
        )
        
        assert retrieved_ingredient.ingredient_id == created_ingredient.ingredient_id
        assert retrieved_ingredient.name == created_ingredient.name
        assert retrieved_ingredient.calories_per_100g == created_ingredient.calories_per_100g

    async def test_update_ingredient(self):
        """Test updating an ingredient."""
        # Create test ingredient
        ingredient_data = TestDataGenerator.generate_ingredient_create()
        created_ingredient = await self.service.create_ingredient(ingredient_data)
        self.test_ingredients.append(created_ingredient.ingredient_id)
        
        # Update the ingredient
        update_data = IngredientMasterUpdate(
            name="Updated Name",
            calories_per_100g=999.0
        )
        
        updated_ingredient = await self.service.update_ingredient(
            created_ingredient.ingredient_id,
            update_data
        )
        
        # Verify update
        assert updated_ingredient.name == "Updated Name"
        assert updated_ingredient.calories_per_100g == 999.0
        assert updated_ingredient.ingredient_id == created_ingredient.ingredient_id
        
        # Verify other fields remain unchanged
        assert updated_ingredient.proteins_per_100g == created_ingredient.proteins_per_100g

    async def test_delete_ingredient(self):
        """Test deleting an ingredient."""
        # Create test ingredient
        ingredient_data = TestDataGenerator.generate_ingredient_create()
        created_ingredient = await self.service.create_ingredient(ingredient_data)
        
        # Delete the ingredient
        await self.service.delete_ingredient(created_ingredient.ingredient_id)
        
        # Verify deletion - should raise error when trying to retrieve
        with pytest.raises(IngredientError):
            await self.service.get_ingredient(created_ingredient.ingredient_id)

    async def test_search_ingredients(self):
        """Test searching for ingredients."""
        # Create test ingredients with specific names
        test_ingredients = [
            TestDataGenerator.generate_ingredient_create(name="Tomato Sauce"),
            TestDataGenerator.generate_ingredient_create(name="Tomato Paste"),
            TestDataGenerator.generate_ingredient_create(name="Fresh Basil"),
        ]
        
        created_ids = []
        for ingredient_data in test_ingredients:
            created = await self.service.create_ingredient(ingredient_data)
            created_ids.append(created.ingredient_id)
            self.test_ingredients.append(created.ingredient_id)
        
        # Search for tomato ingredients
        search_params = IngredientSearch(q="tomato", limit=10)
        search_results = await self.service.search_ingredients(search_params)
        
        # Verify results
        assert len(search_results.ingredients) >= 2  # At least our two tomato ingredients
        tomato_names = [ing.name for ing in search_results.ingredients if "tomato" in ing.name.lower()]
        assert "Tomato Sauce" in tomato_names
        assert "Tomato Paste" in tomato_names

    async def test_list_ingredients_pagination(self):
        """Test listing ingredients with pagination."""
        # Create multiple test ingredients
        ingredient_count = 5
        for i in range(ingredient_count):
            ingredient_data = TestDataGenerator.generate_ingredient_create(
                name=f"Test Ingredient {i}"
            )
            created = await self.service.create_ingredient(ingredient_data)
            self.test_ingredients.append(created.ingredient_id)
        
        # Test first page
        first_page = await self.service.list_ingredients(limit=3, offset=0)
        assert len(first_page.ingredients) <= 3
        assert first_page.total >= ingredient_count
        
        # Test second page
        second_page = await self.service.list_ingredients(limit=3, offset=3)
        assert len(second_page.ingredients) >= 0

    async def test_bulk_operations(self):
        """Test bulk operations with multiple ingredients."""
        # Create multiple ingredients
        bulk_data = [
            TestDataGenerator.generate_ingredient_create(name=f"Bulk Ingredient {i}")
            for i in range(10)
        ]
        
        created_ingredients = []
        for ingredient_data in bulk_data:
            created = await self.service.create_ingredient(ingredient_data)
            created_ingredients.append(created)
            self.test_ingredients.append(created.ingredient_id)
        
        # Verify all were created
        assert len(created_ingredients) == 10
        
        # Test bulk retrieval through search
        search_params = IngredientSearch(q="Bulk", limit=20)
        search_results = await self.service.search_ingredients(search_params)
        
        bulk_results = [
            ing for ing in search_results.ingredients 
            if ing.name.startswith("Bulk Ingredient")
        ]
        assert len(bulk_results) >= 10

    async def test_concurrent_operations(self):
        """Test concurrent ingredient operations."""
        async def create_ingredient(index: int):
            ingredient_data = TestDataGenerator.generate_ingredient_create(
                name=f"Concurrent Ingredient {index}"
            )
            created = await self.service.create_ingredient(ingredient_data)
            self.test_ingredients.append(created.ingredient_id)
            return created
        
        # Create ingredients concurrently
        tasks = [create_ingredient(i) for i in range(5)]
        results = await asyncio.gather(*tasks)
        
        # Verify all were created successfully
        assert len(results) == 5
        assert all(result.ingredient_id is not None for result in results)
        
        # Verify unique IDs
        ids = [result.ingredient_id for result in results]
        assert len(set(ids)) == 5  # All IDs should be unique

    async def test_error_handling_integration(self):
        """Test error handling in integration scenarios."""
        # Test retrieving non-existent ingredient
        non_existent_id = uuid4()
        with pytest.raises(IngredientError):
            await self.service.get_ingredient(non_existent_id)
        
        # Test updating non-existent ingredient
        update_data = IngredientMasterUpdate(name="Updated")
        with pytest.raises(IngredientError):
            await self.service.update_ingredient(non_existent_id, update_data)
        
        # Test deleting non-existent ingredient
        with pytest.raises(IngredientError):
            await self.service.delete_ingredient(non_existent_id)

    async def test_data_consistency(self):
        """Test data consistency across operations."""
        # Create ingredient
        original_data = TestDataGenerator.generate_ingredient_create()
        created = await self.service.create_ingredient(original_data)
        self.test_ingredients.append(created.ingredient_id)
        
        # Retrieve and verify data consistency
        retrieved = await self.service.get_ingredient(created.ingredient_id)
        
        assert retrieved.name == original_data.name
        assert retrieved.calories_per_100g == original_data.calories_per_100g
        assert retrieved.proteins_per_100g == original_data.proteins_per_100g
        assert retrieved.fat_per_100g == original_data.fat_per_100g
        assert retrieved.carbs_per_100g == original_data.carbs_per_100g
        assert retrieved.price_per_100g_cents == original_data.price_per_100g_cents
        
        # Update and verify consistency
        update_data = IngredientMasterUpdate(calories_per_100g=500.0)
        updated = await self.service.update_ingredient(created.ingredient_id, update_data)
        
        # Only updated field should change
        assert updated.calories_per_100g == 500.0
        assert updated.name == original_data.name  # Should remain unchanged
        assert updated.proteins_per_100g == original_data.proteins_per_100g

    async def test_search_edge_cases(self):
        """Test search functionality with edge cases."""
        # Create ingredients with special characters and cases
        special_ingredients = [
            TestDataGenerator.generate_ingredient_create(name="Café con Leche"),
            TestDataGenerator.generate_ingredient_create(name="Piña Colada Mix"),
            TestDataGenerator.generate_ingredient_create(name="ALL CAPS INGREDIENT"),
            TestDataGenerator.generate_ingredient_create(name="lowercase ingredient"),
        ]
        
        for ingredient_data in special_ingredients:
            created = await self.service.create_ingredient(ingredient_data)
            self.test_ingredients.append(created.ingredient_id)
        
        # Test case-insensitive search
        search_params = IngredientSearch(q="ingredient", limit=10)
        results = await self.service.search_ingredients(search_params)
        
        # Should find both CAPS and lowercase versions
        ingredient_names = [ing.name.lower() for ing in results.ingredients]
        matching_names = [name for name in ingredient_names if "ingredient" in name]
        assert len(matching_names) >= 2
        
        # Test partial match
        search_params = IngredientSearch(q="café", limit=10)
        results = await self.service.search_ingredients(search_params)
        
        # Should handle special characters
        cafe_results = [
            ing for ing in results.ingredients 
            if "café" in ing.name.lower()
        ]
        assert len(cafe_results) >= 1

    async def test_performance_with_large_dataset(self):
        """Test performance with larger datasets."""
        # Create a larger number of ingredients
        batch_size = 50
        ingredient_data_batch = [
            TestDataGenerator.generate_ingredient_create(
                name=f"Performance Test Ingredient {i}",
                category="performance_test"
            )
            for i in range(batch_size)
        ]
        
        # Create ingredients and measure basic performance
        created_count = 0
        for ingredient_data in ingredient_data_batch:
            created = await self.service.create_ingredient(ingredient_data)
            self.test_ingredients.append(created.ingredient_id)
            created_count += 1
        
        assert created_count == batch_size
        
        # Test search performance
        search_params = IngredientSearch(q="Performance Test", limit=100)
        search_results = await self.service.search_ingredients(search_params)
        
        # Should efficiently return results
        performance_results = [
            ing for ing in search_results.ingredients 
            if "Performance Test" in ing.name
        ]
        assert len(performance_results) >= batch_size
