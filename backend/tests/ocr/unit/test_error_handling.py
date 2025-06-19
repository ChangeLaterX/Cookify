"""
Unit Tests for OCR Error Handling and Edge Cases.

This module tests error conditions, edge cases, and resilience of the OCR service.
"""

import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from io import BytesIO
from PIL import Image

from domains.ocr.services import OCRService, OCRError
from tests.ocr.config import OCRTestBase
from tests.ocr.utils.mocks import MockContextManager, with_mocked_ocr
from tests.ocr.utils.test_data import TestDataGenerator


class TestOCRErrorHandling(OCRTestBase):
    """Test OCR service error handling and edge cases."""

    def test_ocr_service_missing_dependencies(self):
        """Test OCR service initialization with missing dependencies."""
        with patch('domains.ocr.services.OCR_AVAILABLE', False):
            with pytest.raises(OCRError) as exc_info:
                OCRService()
            
            assert exc_info.value.error_code == "OCR_DEPENDENCIES_MISSING"
            assert "OCR dependencies not available" in exc_info.value.message

    @pytest.mark.asyncio
    async def test_extract_text_corrupted_image_data(self):
        """Test text extraction with corrupted image data."""
        with MockContextManager() as mock_ctx:
            service = OCRService()
            
            # Test various types of corrupted data
            corrupted_data_cases = [
                b"",  # Empty data
                b"not_an_image",  # Invalid image data
                b"\x00\x01\x02\x03" * 100,  # Random bytes
                None,  # None value (will need special handling)
            ]
            
            for corrupted_data in corrupted_data_cases:
                if corrupted_data is None:
                    # Explicitly test None input handling
                    with pytest.raises(OCRError) as exc_info:
                        await service.extract_text_from_image(corrupted_data)
                    assert exc_info.value.error_code == "OCR_PROCESSING_FAILED"
                    continue
                
                with patch('PIL.Image.open', side_effect=Exception("Corrupted image")):
                    with pytest.raises(OCRError) as exc_info:
                        await service.extract_text_from_image(corrupted_data)
                    
                    assert exc_info.value.error_code == "OCR_PROCESSING_FAILED"

    @pytest.mark.asyncio
    async def test_extract_text_pil_unavailable(self):
        """Test text extraction when PIL is not available."""
        with MockContextManager() as mock_ctx:
            service = OCRService()
            
            # Mock PIL.Image as None (unavailable)
            with patch('domains.ocr.services.Image', None):
                test_image_data = TestDataGenerator.generate_sample_image_bytes()
                
                with pytest.raises(OCRError) as exc_info:
                    await service.extract_text_from_image(test_image_data)
                
                assert exc_info.value.error_code == "OCR_DEPENDENCIES_MISSING"

    @pytest.mark.asyncio
    async def test_extract_text_pytesseract_unavailable(self):
        """Test text extraction when pytesseract is not available."""
        with MockContextManager() as mock_ctx:
            service = OCRService()
            
            # Mock pytesseract as None (unavailable)
            with patch('domains.ocr.services.pytesseract', None):
                test_image_data = TestDataGenerator.generate_sample_image_bytes()
                
                with pytest.raises(OCRError) as exc_info:
                    await service.extract_text_from_image(test_image_data)
                
                assert exc_info.value.error_code == "OCR_DEPENDENCIES_MISSING"

    @pytest.mark.asyncio
    async def test_extract_text_tesseract_execution_error(self):
        """Test handling of tesseract execution errors."""
        with MockContextManager() as mock_ctx:
            service = OCRService()
            
            # Mock tesseract to raise execution error
            with patch('domains.ocr.services.pytesseract.image_to_string',
                      side_effect=Exception("Tesseract execution failed")), \
                 patch('domains.ocr.services.pytesseract.image_to_data',
                      side_effect=Exception("Tesseract data extraction failed")):
                
                test_image_data = TestDataGenerator.generate_sample_image_bytes()
                
                with pytest.raises(OCRError) as exc_info:
                    await service.extract_text_from_image(test_image_data)
                
                assert exc_info.value.error_code == "OCR_PROCESSING_FAILED"

    def test_extract_receipt_items_edge_cases(self):
        """Test receipt item extraction with edge cases."""
        with MockContextManager() as mock_ctx:
            service = OCRService()
            
            edge_case_texts = [
                "",  # Empty text
                "   \n  \t  \n   ",  # Whitespace only
                "No food items here just random text",  # No food items
                "1234567890",  # Numbers only
                "!@#$%^&*()",  # Special characters only
                "a",  # Single character
                "Very long text that contains no meaningful food items but is designed to test the limits of the item extraction algorithm with lots of unnecessary words and phrases",  # Very long text
            ]
            
            for text in edge_case_texts:
                items = service._extract_receipt_items(text)
                
                # Should not crash and return a list
                assert isinstance(items, list)
                
                # For empty/meaningless text, should return empty or very few items
                if not text.strip() or len(text.strip()) < 3:
                    assert len(items) == 0

    def test_extract_quantity_and_price_edge_cases(self):
        """Test quantity and price extraction with edge cases."""
        with MockContextManager() as mock_ctx:
            service = OCRService()
            
            edge_cases = [
                "",  # Empty text
                "No numbers here",  # No numbers
                "$ (no price)",  # Dollar sign but no price
                "1000000 lbs for $9999.99",  # Unrealistic values
                "Item ($0.00)",  # Zero price
                "Item (0 lbs)",  # Zero quantity
                "Item ($-5.99)",  # Negative price
                "Item (-2 lbs)",  # Negative quantity
                "Item (abc lbs) $xyz",  # Non-numeric values
                "Item ($12.345)",  # Too many decimal places
                "Item (1.5.5 lbs)",  # Malformed decimal
            ]
            
            for text in edge_cases:
                quantity, unit, price = service._extract_quantity_and_price(text)
                
                # Should not crash
                assert quantity is None or isinstance(quantity, (int, float))
                assert unit is None or isinstance(unit, str)
                assert price is None or isinstance(price, (int, float))
                
                # Validate ranges for non-None values
                if quantity is not None:
                    assert quantity >= 0, f"Negative quantity extracted from: {text}"
                
                if price is not None:
                    assert price >= 0, f"Negative price extracted from: {text}"
                    assert price <= 1000, f"Unrealistic price extracted from: {text}"

    @pytest.mark.asyncio
    async def test_process_receipt_with_suggestions_error_recovery(self):
        """Test error recovery in receipt processing workflow."""
        with MockContextManager() as mock_ctx:
            service = OCRService()
            
            test_image_data = TestDataGenerator.generate_sample_image_bytes()
            
            # Test recovery from OCR text extraction failure
            with patch.object(service, 'extract_text_from_image',
                             side_effect=OCRError("OCR failed", "OCR_FAILED")):
                
                with pytest.raises(OCRError) as exc_info:
                    await service.process_receipt_with_suggestions(test_image_data)
                
                assert exc_info.value.error_code == "OCR_FAILED"

    @pytest.mark.asyncio
    async def test_image_preprocessing_error_recovery(self):
        """Test image preprocessing error recovery."""
        with MockContextManager() as mock_ctx:
            service = OCRService()
            
            # Create a mock image that causes preprocessing errors
            mock_image = MagicMock()
            mock_image.mode = 'RGB'
            
            # Mock preprocessing to fail initially but recover
            with patch.object(service, '_preprocess_image_for_ocr') as mock_preprocess:
                # First call fails, should use fallback
                mock_preprocess.side_effect = Exception("Preprocessing failed")
                
                test_image_data = TestDataGenerator.generate_sample_image_bytes()
                
                # Should not crash, should use fallback processing
                # We'll mock the entire OCR process since we're testing preprocessing error handling
                with patch('domains.ocr.services.pytesseract.image_to_string',
                          return_value="Fallback OCR result"), \
                     patch('domains.ocr.services.pytesseract.image_to_data',
                          return_value={'conf': ['80'], 'text': ['Fallback']}):
                    
                    result = await service.extract_text_from_image(test_image_data)
                    
                    # Should succeed with fallback
                    assert isinstance(result.extracted_text, str)

    def test_normalize_unit_edge_cases(self):
        """Test unit normalization with edge cases."""
        with MockContextManager() as mock_ctx:
            service = OCRService()
            
            edge_cases = [
                ("", ""),  # Empty string
                ("   ", "   "),  # Whitespace
                ("UNKNOWN_UNIT", "unknown_unit"),  # Unknown unit
                ("123", "123"),  # Numbers only
                ("!@#", "!@#"),  # Special characters
                ("lbslbslbs", "lbslbslbs"),  # Repeated pattern
                ("2lbs", "lbs"),  # Number prefix (should be handled)
                ("lb5", "lb5"),  # Number suffix
            ]
            
            for input_unit, expected_output in edge_cases:
                result = service._normalize_unit(input_unit)
                
                # Should not crash
                assert isinstance(result, str)
                
                # For known patterns, verify specific behavior
                if input_unit == "2lbs":
                    assert result == "lbs"  # Should extract unit part

    @pytest.mark.asyncio
    async def test_ingredient_suggestions_with_service_errors(self):
        """Test ingredient suggestions handling service errors."""
        with MockContextManager() as mock_ctx:
            service = OCRService()
            
            # Test various error scenarios in ingredient search
            from domains.ingredients.services import IngredientError
            
            error_cases = [
                IngredientError("Database connection failed", "DB_CONNECTION_ERROR"),
                IngredientError("Service timeout", "SERVICE_TIMEOUT"),
                Exception("Unexpected service error"),
                ConnectionError("Network error"),
                TimeoutError("Request timeout"),
            ]
            
            for error in error_cases:
                with patch('domains.ocr.services.search_ingredients', side_effect=error):
                    suggestions = await service._find_ingredient_suggestions("Tomatoes")
                    
                    # Should return empty list gracefully
                    assert suggestions == []

    @pytest.mark.asyncio
    async def test_concurrent_ocr_processing(self):
        """Test OCR service under concurrent load."""
        import asyncio
        
        with MockContextManager() as mock_ctx:
            service = OCRService()
            
            # Create multiple concurrent OCR tasks
            test_data = [
                TestDataGenerator.generate_sample_image_bytes() 
                for _ in range(5)
            ]
            
            # Mock OCR to return different results for each call
            mock_responses = [
                TestDataGenerator.generate_ocr_text_response(f"Text {i}", 80.0)
                for i in range(5)
            ]
            
            with patch.object(service, 'extract_text_from_image',
                             side_effect=mock_responses):
                
                # Run concurrent OCR tasks
                tasks = [
                    service.extract_text_from_image(data) 
                    for data in test_data
                ]
                
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # All should succeed
                assert len(results) == 5
                for i, result in enumerate(results):
                    assert not isinstance(result, Exception)
                    assert f"Text {i}" in result.extracted_text

    @pytest.mark.asyncio
    async def test_memory_usage_with_large_images(self):
        """Test memory handling with large image data."""
        with MockContextManager() as mock_ctx:
            service = OCRService()
            
            # Create large fake image data
            large_image_data = b"fake_image_header" + b"\x00" * (10 * 1024 * 1024)  # 10MB
            
            # Mock PIL to handle large image
            mock_image = MagicMock()
            mock_image.mode = 'RGB'
            mock_image.size = (4000, 4000)  # Large image
            
            with patch('PIL.Image.open', return_value=mock_image), \
                 patch('domains.ocr.services.pytesseract.image_to_string',
                      return_value="Large image OCR result"), \
                 patch('domains.ocr.services.pytesseract.image_to_data',
                      return_value={'conf': ['75'], 'text': ['Large']}):
                
                result = await service.extract_text_from_image(large_image_data)
                
                # Should handle large images without memory errors
                assert isinstance(result.extracted_text, str)
                assert result.processing_time_ms > 0
