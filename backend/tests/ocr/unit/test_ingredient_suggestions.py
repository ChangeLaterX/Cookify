"""
Unit Tests for OCR Ingredient Suggestion Functionality.

This module tests the ingredient matching and suggestion features of the OCR service.
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from typing import List

from domains.ocr.services import OCRService, OCRError
from domains.ocr.schemas import OCRItemSuggestion
from domains.ingredients.services import IngredientError
from tests.ocr.config import OCRTestBase
from tests.ocr.utils.mocks import MockContextManager, with_mocked_ocr
from tests.ocr.utils.test_data import TestDataGenerator


class TestOCRIngredientSuggestions(OCRTestBase):
    """Test OCR ingredient suggestion functionality."""

    @pytest.mark.asyncio
    async def test_find_ingredient_suggestions_success(self):
        """Test successful ingredient suggestion matching."""
        with MockContextManager() as mock_ctx:
            service = OCRService()
            
            # Mock search_ingredients to return matching results
            mock_ingredient_data = TestDataGenerator.generate_mock_ingredient_search_results(
                query="tomatoes",
                count=3
            )
            
            with patch('domains.ocr.services.search_ingredients', return_value=mock_ingredient_data):
                suggestions = await service._find_ingredient_suggestions("Tomatoes (2 lbs)")
                
                assert len(suggestions) > 0
                assert all(isinstance(s, OCRItemSuggestion) for s in suggestions)
                assert all(s.confidence_score > 0 for s in suggestions)
                assert suggestions[0].ingredient_name.lower() == "tomatoes"

    @pytest.mark.asyncio
    async def test_find_ingredient_suggestions_with_ocr_errors(self):
        """Test ingredient suggestions with OCR errors in item text."""
        with MockContextManager() as mock_ctx:
            service = OCRService()
            
            test_cases = [
                ("Tomatnes (2 lbs)", "tomatoes"),  # OCR error
                ("Garlie (3 bulbs)", "garlic"),    # OCR error
                ("Mitk (1 gallon)", "milk"),       # OCR error
                ("Onions", "onions"),              # Clean text
            ]
            
            for ocr_text, expected_match in test_cases:
                mock_results = TestDataGenerator.generate_mock_ingredient_search_results(
                    query=expected_match,
                    count=2
                )
                
                with patch('domains.ocr.services.search_ingredients', return_value=mock_results):
                    suggestions = await service._find_ingredient_suggestions(ocr_text)
                    
                    assert len(suggestions) > 0, f"No suggestions for {ocr_text}"
                    # Should find a reasonable match even with OCR errors
                    assert suggestions[0].confidence_score >= 30.0

    @pytest.mark.asyncio
    async def test_find_ingredient_suggestions_no_matches(self):
        """Test ingredient suggestions when no good matches are found."""
        with MockContextManager() as mock_ctx:
            service = OCRService()
            
            # Mock search_ingredients to return poor matches
            mock_results = TestDataGenerator.generate_mock_ingredient_search_results(
                query="nonsense_item",
                count=0  # No results
            )
            
            with patch('domains.ocr.services.search_ingredients', return_value=mock_results):
                suggestions = await service._find_ingredient_suggestions("Xyzabc Random Item")
                
                assert len(suggestions) == 0

    @pytest.mark.asyncio
    async def test_find_ingredient_suggestions_similarity_threshold(self):
        """Test that suggestions respect similarity threshold."""
        with MockContextManager() as mock_ctx:
            service = OCRService()
            
            # Create mock ingredients with varying similarity
            from domains.ingredients.schemas import Ingredient
            from uuid import uuid4
            
            mock_ingredients = [
                Ingredient(
                    ingredient_id=uuid4(),
                    name="Apples",  # High similarity to "Apple"
                    description="Fresh apples"
                ),
                Ingredient(
                    ingredient_id=uuid4(),
                    name="Oranges",  # Low similarity to "Apple"
                    description="Fresh oranges"
                ),
            ]
            
            mock_search_result = MagicMock()
            mock_search_result.ingredients = mock_ingredients
            
            with patch('domains.ocr.services.search_ingredients', return_value=mock_search_result):
                suggestions = await service._find_ingredient_suggestions("Apple")
                
                # Should only include suggestions above threshold (30%)
                for suggestion in suggestions:
                    assert suggestion.confidence_score >= 30.0

    @pytest.mark.asyncio
    async def test_find_ingredient_suggestions_ingredient_error(self):
        """Test handling of IngredientError during suggestion search."""
        with MockContextManager() as mock_ctx:
            service = OCRService()
            
            # Mock search_ingredients to raise IngredientError
            with patch('domains.ocr.services.search_ingredients', 
                      side_effect=IngredientError("Database error", "DB_ERROR")):
                
                suggestions = await service._find_ingredient_suggestions("Tomatoes")
                
                # Should return empty list gracefully
                assert suggestions == []

    @pytest.mark.asyncio
    async def test_find_ingredient_suggestions_unexpected_error(self):
        """Test handling of unexpected errors during suggestion search."""
        with MockContextManager() as mock_ctx:
            service = OCRService()
            
            # Mock search_ingredients to raise unexpected error
            with patch('domains.ocr.services.search_ingredients', 
                      side_effect=Exception("Unexpected error")):
                
                suggestions = await service._find_ingredient_suggestions("Tomatoes")
                
                # Should return empty list gracefully
                assert suggestions == []

    @pytest.mark.asyncio
    async def test_find_ingredient_suggestions_max_suggestions_limit(self):
        """Test that suggestions are limited to max_suggestions parameter."""
        with MockContextManager() as mock_ctx:
            service = OCRService()
            
            # Create many mock ingredients
            mock_results = TestDataGenerator.generate_mock_ingredient_search_results(
                query="tomatoes",
                count=10  # More than default max
            )
            
            with patch('domains.ocr.services.search_ingredients', return_value=mock_results):
                # Test default limit (3)
                suggestions = await service._find_ingredient_suggestions("Tomatoes")
                assert len(suggestions) <= 3
                
                # Test custom limit
                suggestions = await service._find_ingredient_suggestions("Tomatoes", max_suggestions=5)
                assert len(suggestions) <= 5

    @pytest.mark.asyncio
    async def test_find_ingredient_suggestions_sorted_by_confidence(self):
        """Test that suggestions are sorted by confidence score in descending order."""
        with MockContextManager() as mock_ctx:
            service = OCRService()
            
            mock_results = TestDataGenerator.generate_mock_ingredient_search_results(
                query="tomatoes",
                count=5
            )
            
            with patch('domains.ocr.services.search_ingredients', return_value=mock_results):
                suggestions = await service._find_ingredient_suggestions("Tomatoes")
                
                # Verify suggestions are sorted by confidence (descending)
                if len(suggestions) > 1:
                    for i in range(len(suggestions) - 1):
                        assert suggestions[i].confidence_score >= suggestions[i + 1].confidence_score

    @pytest.mark.asyncio
    async def test_ingredient_suggestions_with_special_characters(self):
        """Test ingredient suggestions with special characters in item text."""
        with MockContextManager() as mock_ctx:
            service = OCRService()
            
            test_texts = [
                "Bell Peppers (4) $4.76",
                "Olive Oil (500ml) @ $6.99",
                "Garlic - 3 bulbs",
                "Milk, 1% (1 gallon)",
            ]
            
            for text in test_texts:
                mock_results = TestDataGenerator.generate_mock_ingredient_search_results(
                    query="test_ingredient",
                    count=1
                )
                
                with patch('domains.ocr.services.search_ingredients', return_value=mock_results):
                    suggestions = await service._find_ingredient_suggestions(text)
                    
                    # Should handle special characters without errors
                    assert isinstance(suggestions, list)
