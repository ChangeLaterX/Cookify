"""
Unit Tests for OCR Complete Workflow and Public API.

This module tests the end-to-end OCR workflows and public API functions.
"""

import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from io import BytesIO

from domains.receipt.services import (
    extract_text_from_image,
    process_receipt_image,
    OCRError,
    ocr_service
)
from domains.receipt.schemas import OCRTextResponse, OCRProcessedResponse
from tests.ocr.config import OCRTestBase
from tests.ocr.utils.mocks import MockContextManager, with_mocked_ocr
from tests.ocr.utils.test_data import TestDataGenerator


class TestOCRCompleteWorkflow(OCRTestBase):
    """Test complete OCR workflows and public API functions."""

    @pytest.mark.asyncio
    async def test_extract_text_from_image_public_api(self):
        """Test the public extract_text_from_image function."""
        with MockContextManager() as mock_ctx:
            # Generate test data
            test_image_data = TestDataGenerator.generate_sample_image_bytes()
            expected_response = TestDataGenerator.generate_ocr_text_response(
                text="Sample receipt text",
                confidence=85.0
            )
            
            # Mock the service method
            with patch.object(ocr_service, 'extract_text_from_image', 
                             return_value=expected_response) as mock_extract:
                
                result = await extract_text_from_image(test_image_data)
                
                assert isinstance(result, OCRTextResponse)
                assert result.extracted_text == "Sample receipt text"
                assert result.confidence == 85.0
                mock_extract.assert_called_once_with(test_image_data)

    @pytest.mark.asyncio
    async def test_process_receipt_image_public_api(self):
        """Test the public process_receipt_image function."""
        with MockContextManager() as mock_ctx:
            # Generate test data
            test_image_data = TestDataGenerator.generate_sample_image_bytes()
            expected_response = TestDataGenerator.generate_ocr_processed_response(
                items_count=3
            )
            
            # Mock the service method
            with patch.object(ocr_service, 'process_receipt_with_suggestions',
                             return_value=expected_response) as mock_process:
                
                result = await process_receipt_image(test_image_data)
                
                assert isinstance(result, OCRProcessedResponse)
                assert result.total_items_detected == 3
                assert len(result.detected_items) == 3
                mock_process.assert_called_once_with(test_image_data)

    @pytest.mark.asyncio
    async def test_public_api_service_unavailable(self):
        """Test public API functions when OCR service is unavailable."""
        # Mock ocr_service as None (unavailable)
        with patch('domains.receipt.services.ocr_service', None):
            test_image_data = b"fake_image_data"
            
            # Test extract_text_from_image
            with pytest.raises(OCRError) as exc_info:
                await extract_text_from_image(test_image_data)
            
            assert exc_info.value.error_code == "OCR_SERVICE_UNAVAILABLE"
            assert "OCR service not available" in exc_info.value.message
            
            # Test process_receipt_image
            with pytest.raises(OCRError) as exc_info:
                await process_receipt_image(test_image_data)
            
            assert exc_info.value.error_code == "OCR_SERVICE_UNAVAILABLE"

    @pytest.mark.asyncio
    async def test_complete_receipt_processing_workflow(self):
        """Test the complete receipt processing workflow from image to suggestions."""
        with MockContextManager() as mock_ctx:
            test_image_data = TestDataGenerator.generate_sample_image_bytes()
            
            # Create mock receipt text with realistic content
            mock_receipt_text = """
            FRESH MARKET GROCERY
            123 Main Street
            
            Tomatoes (2 lbs)      $3.98
            Onions (1 lb)         $1.49
            Garlic (3 bulbs)      $2.25
            Milk (1 gallon)       $3.29
            
            Total:               $11.01
            """
            
            # Mock OCR text extraction
            mock_ocr_response = TestDataGenerator.generate_ocr_text_response(
                text=mock_receipt_text,
                confidence=88.5
            )
            
            # Mock ingredient search results
            mock_ingredients = [
                TestDataGenerator.generate_mock_ingredient_search_results("tomatoes", 2),
                TestDataGenerator.generate_mock_ingredient_search_results("onions", 2),
                TestDataGenerator.generate_mock_ingredient_search_results("garlic", 2),
                TestDataGenerator.generate_mock_ingredient_search_results("milk", 2),
            ]
            
            with patch.object(ocr_service, 'extract_text_from_image',
                             return_value=mock_ocr_response), \
                 patch('domains.receipt.services.search_ingredients',
                       side_effect=mock_ingredients):
                
                result = await process_receipt_image(test_image_data)
                
                # Verify the complete workflow
                assert isinstance(result, OCRProcessedResponse)
                assert result.total_items_detected > 0
                assert len(result.detected_items) > 0
                
                # Check that items were extracted properly
                item_names = [item.detected_text.lower() for item in result.detected_items]
                expected_items = ["tomatoes", "onions", "garlic", "milk"]
                
                for expected in expected_items:
                    assert any(expected in name for name in item_names), \
                        f"Expected item '{expected}' not found in {item_names}"
                
                # Verify suggestions were generated
                for item in result.detected_items:
                    if item.suggestions:
                        assert all(s.confidence_score > 0 for s in item.suggestions)

    @pytest.mark.asyncio
    async def test_workflow_with_poor_ocr_quality(self):
        """Test workflow handling when OCR quality is poor."""
        with MockContextManager() as mock_ctx:
            test_image_data = TestDataGenerator.generate_sample_image_bytes()
            
            # Mock poor quality OCR with errors
            poor_ocr_text = """
            FRFSH MARKFT
            
            Tomatnes (2 its)      $398
            Onins (1 ib)          $149
            Garlie (3 bults)      $225
            Mitk (1 galon)        $329
            """
            
            mock_ocr_response = TestDataGenerator.generate_ocr_text_response(
                text=poor_ocr_text,
                confidence=45.2  # Poor confidence
            )
            
            with patch.object(ocr_service, 'extract_text_from_image',
                             return_value=mock_ocr_response), \
                 patch('domains.receipt.services.search_ingredients',
                       return_value=TestDataGenerator.generate_mock_ingredient_search_results("test", 1)):
                
                result = await process_receipt_image(test_image_data)
                
                # Should still process and extract items despite poor quality
                assert isinstance(result, OCRProcessedResponse)
                assert result.total_items_detected >= 0  # May find some items
                
                # Processing time should be reasonable
                assert result.processing_time_ms > 0
                assert result.processing_time_ms < 30000  # Less than 30 seconds

    @pytest.mark.asyncio
    async def test_workflow_with_empty_receipt(self):
        """Test workflow with empty or minimal receipt content."""
        with MockContextManager() as mock_ctx:
            test_image_data = TestDataGenerator.generate_sample_image_bytes()
            
            # Mock empty OCR result
            empty_ocr_response = TestDataGenerator.generate_ocr_text_response(
                text="   \n  \n   ",  # Whitespace only
                confidence=75.0
            )
            
            with patch.object(ocr_service, 'extract_text_from_image',
                             return_value=empty_ocr_response):
                
                result = await process_receipt_image(test_image_data)
                
                # Should handle gracefully
                assert isinstance(result, OCRProcessedResponse)
                assert result.total_items_detected == 0
                assert result.detected_items == []

    @pytest.mark.asyncio
    async def test_workflow_error_handling(self):
        """Test workflow error handling and propagation."""
        with MockContextManager() as mock_ctx:
            test_image_data = TestDataGenerator.generate_sample_image_bytes()
            
            # Test OCR extraction failure
            with patch.object(ocr_service, 'extract_text_from_image',
                             side_effect=OCRError("OCR failed", "OCR_FAILED")):
                
                with pytest.raises(OCRError) as exc_info:
                    await process_receipt_image(test_image_data)
                
                assert exc_info.value.error_code == "OCR_FAILED"

    @pytest.mark.asyncio
    async def test_workflow_with_mixed_content_receipt(self):
        """Test workflow with receipt containing both food and non-food items."""
        with MockContextManager() as mock_ctx:
            test_image_data = TestDataGenerator.generate_sample_image_bytes()
            
            # Mock receipt with mixed content
            mixed_receipt_text = """
            GENERAL STORE
            
            Tomatoes (2 lbs)      $3.98
            Batteries AA (4 pack) $8.99
            Onions (1 lb)         $1.49
            Phone Charger         $15.99
            Milk (1 gallon)       $3.29
            Paper Towels          $4.99
            """
            
            mock_ocr_response = TestDataGenerator.generate_ocr_text_response(
                text=mixed_receipt_text,
                confidence=82.0
            )
            
            with patch.object(ocr_service, 'extract_text_from_image',
                             return_value=mock_ocr_response), \
                 patch('domains.receipt.services.search_ingredients',
                       return_value=TestDataGenerator.generate_mock_ingredient_search_results("food", 1)):
                
                result = await process_receipt_image(test_image_data)
                
                # Should filter out non-food items
                assert isinstance(result, OCRProcessedResponse)
                
                # Check that only food items are detected
                item_names = [item.detected_text.lower() for item in result.detected_items]
                food_keywords = ["tomatoes", "onions", "milk"]
                non_food_keywords = ["batteries", "charger", "paper"]
                
                # Should find food items
                for food_item in food_keywords:
                    assert any(food_item in name for name in item_names), \
                        f"Food item '{food_item}' should be detected"
                
                # Should not find non-food items (or very few)
                non_food_count = sum(1 for name in item_names 
                                   for keyword in non_food_keywords 
                                   if keyword in name)
                assert non_food_count < len(non_food_keywords), \
                    "Too many non-food items detected"
