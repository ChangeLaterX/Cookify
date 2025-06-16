"""
Integration Tests for OCR Service with Real Dependencies.

This module contains integration tests that use real OCR dependencies and sample images.
These tests are skipped if tesseract is not available or if running in mock mode.
"""

import pytest
import os
from pathlib import Path

from domains.receipt.services import OCRService, extract_text_from_image, process_receipt_image
from tests.ocr.config import OCRTestConfig


# Skip integration tests if tesseract not available or in mock mode
pytestmark = pytest.mark.skipif(
    not OCRTestConfig.should_run_integration_tests(),
    reason="Integration tests require tesseract and INTEGRATION_MODE=true"
)


class TestOCRIntegration:
    """Integration tests with real OCR dependencies."""

    @pytest.mark.asyncio
    async def test_extract_text_from_real_receipt_image(self):
        """Test text extraction from real receipt images."""
        config = OCRTestConfig()
        
        # Test with sample receipt images
        sample_images = [
            "sample_receipt.png",
            "sample_receipt_blurred.png",
            "sample_receipt_rotated.png"
        ]
        
        for image_name in sample_images:
            image_path = config.get_sample_image_path(image_name)
            
            if image_path and image_path.exists():
                # Read the actual image file
                with open(image_path, 'rb') as f:
                    image_data = f.read()
                
                # Test the OCR extraction
                result = await extract_text_from_image(image_data)
                
                # Verify results
                assert result.extracted_text is not None
                assert len(result.extracted_text.strip()) > 0
                assert result.confidence >= 0
                assert result.processing_time_ms > 0
                
                # Should extract some expected content
                text_lower = result.extracted_text.lower()
                expected_keywords = ["fresh", "market", "grocery", "total", "tomato"]
                found_keywords = sum(1 for keyword in expected_keywords if keyword in text_lower)
                
                # Should find at least some keywords (accounting for OCR errors)
                assert found_keywords >= 1, f"No expected keywords found in OCR text for {image_name}"

    @pytest.mark.asyncio
    async def test_process_real_receipt_with_ingredient_suggestions(self):
        """Test complete receipt processing with real images."""
        config = OCRTestConfig()
        
        image_path = config.get_sample_image_path("sample_receipt.png")
        
        if image_path and image_path.exists():
            with open(image_path, 'rb') as f:
                image_data = f.read()
            
            # Process the receipt
            result = await process_receipt_image(image_data)
            
            # Verify results
            assert result.total_items_detected >= 0
            assert isinstance(result.detected_items, list)
            assert result.processing_time_ms > 0
            assert result.raw_text is not None
            
            # If items were detected, verify they have reasonable structure
            for item in result.detected_items:
                assert item.detected_text is not None
                assert len(item.detected_text.strip()) > 0
                
                # Suggestions should be properly formatted if present
                if item.suggestions:
                    for suggestion in item.suggestions:
                        assert suggestion.ingredient_id is not None
                        assert suggestion.ingredient_name is not None
                        assert 0 <= suggestion.confidence_score <= 100

    @pytest.mark.asyncio
    async def test_ocr_service_real_initialization(self):
        """Test OCR service initialization with real dependencies."""
        # This should succeed if tesseract is properly installed
        service = OCRService()
        
        # Verify service is properly configured
        assert hasattr(service, 'optimal_config')
        assert 'primary' in service.optimal_config
        assert 'fallback_psm_4' in service.optimal_config

    @pytest.mark.asyncio
    async def test_ocr_accuracy_with_different_image_qualities(self):
        """Test OCR accuracy across different image qualities."""
        config = OCRTestConfig()
        
        # Test different quality versions
        quality_variants = [
            ("sample_receipt.png", "clean"),
            ("sample_receipt_blurred.png", "blurred"),
            ("sample_receipt_rotated.png", "rotated")
        ]
        
        results = {}
        
        for image_name, quality_type in quality_variants:
            image_path = config.get_sample_image_path(image_name)
            
            if image_path and image_path.exists():
                with open(image_path, 'rb') as f:
                    image_data = f.read()
                
                result = await extract_text_from_image(image_data)
                results[quality_type] = result
        
        # Compare results across qualities
        if len(results) > 1:
            # Clean image should generally have higher confidence
            if "clean" in results and "blurred" in results:
                # Allow some tolerance for OCR variability
                clean_conf = results["clean"].confidence
                blurred_conf = results["blurred"].confidence
                
                # Clean should be equal or better (with some tolerance)
                assert clean_conf >= blurred_conf - 10, \
                    f"Clean image confidence ({clean_conf}) significantly lower than blurred ({blurred_conf})"

    @pytest.mark.asyncio
    async def test_performance_benchmarking(self):
        """Test OCR performance benchmarks."""
        config = OCRTestConfig()
        
        image_path = config.get_sample_image_path("sample_receipt.png")
        
        if image_path and image_path.exists():
            with open(image_path, 'rb') as f:
                image_data = f.read()
            
            # Run multiple times to get average performance
            times = []
            for _ in range(3):
                result = await extract_text_from_image(image_data)
                times.append(result.processing_time_ms)
            
            avg_time = sum(times) / len(times)
            
            # Performance expectations (adjust based on your environment)
            assert avg_time < 10000, f"OCR taking too long: {avg_time}ms average"
            assert all(t > 0 for t in times), "Invalid processing times recorded"

    @pytest.mark.asyncio
    async def test_real_image_preprocessing(self):
        """Test image preprocessing with real images."""
        config = OCRTestConfig()
        service = OCRService()
        
        image_path = config.get_sample_image_path("sample_receipt.png")
        
        if image_path and image_path.exists():
            from PIL import Image
            
            # Load the real image
            with Image.open(image_path) as img:
                # Test preprocessing
                preprocessed = service._preprocess_image_for_ocr(img)
                
                # Verify preprocessing worked
                assert preprocessed is not None
                assert hasattr(preprocessed, 'mode')
                assert preprocessed.mode == 'RGB'
                
                # Size should be reasonable (not too small, not gigantic)
                width, height = preprocessed.size
                assert width >= 100 and height >= 100, "Image too small after preprocessing"
                assert width <= 5000 and height <= 5000, "Image too large after preprocessing"

    @pytest.mark.asyncio
    async def test_cross_platform_compatibility(self):
        """Test OCR functionality across different platforms."""
        # This test verifies that OCR works regardless of platform-specific differences
        config = OCRTestConfig()
        
        image_path = config.get_sample_image_path("sample_receipt.png")
        
        if image_path and image_path.exists():
            with open(image_path, 'rb') as f:
                image_data = f.read()
            
            # Test basic functionality
            result = await extract_text_from_image(image_data)
            
            # Should work on any platform where tesseract is available
            assert result.extracted_text is not None
            assert result.confidence >= 0
            
            # Verify character encoding handling
            text = result.extracted_text
            assert isinstance(text, str), "OCR result should be a string"
            
            # Should handle unicode characters properly if present
            try:
                encoded = text.encode('utf-8')
                decoded = encoded.decode('utf-8')
                assert decoded == text, "Unicode encoding/decoding failed"
            except UnicodeError:
                pytest.fail("Unicode handling error in OCR result")

    @pytest.mark.asyncio
    async def test_memory_usage_real_images(self):
        """Test memory usage with real images."""
        import gc
        import sys
        
        config = OCRTestConfig()
        
        image_path = config.get_sample_image_path("sample_receipt.png")
        
        if image_path and image_path.exists():
            # Get initial memory usage
            gc.collect()
            initial_objects = len(gc.get_objects())
            
            # Process image multiple times
            for _ in range(5):
                with open(image_path, 'rb') as f:
                    image_data = f.read()
                
                result = await extract_text_from_image(image_data)
                assert result.extracted_text is not None
            
            # Check for memory leaks
            gc.collect()
            final_objects = len(gc.get_objects())
            
            # Allow some object growth but not excessive
            object_growth = final_objects - initial_objects
            assert object_growth < 1000, f"Possible memory leak: {object_growth} new objects"

    @pytest.mark.asyncio
    async def test_concurrent_real_ocr_processing(self):
        """Test concurrent processing with real images."""
        import asyncio
        
        config = OCRTestConfig()
        
        image_path = config.get_sample_image_path("sample_receipt.png")
        
        if image_path and image_path.exists():
            with open(image_path, 'rb') as f:
                image_data = f.read()
            
            # Process same image concurrently
            tasks = [extract_text_from_image(image_data) for _ in range(3)]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # All should succeed
            assert len(results) == 3
            for result in results:
                assert not isinstance(result, Exception), f"Concurrent OCR failed: {result}"
                assert result.extracted_text is not None
                assert result.confidence >= 0

    @pytest.mark.asyncio 
    async def test_large_real_image_handling(self):
        """Test handling of large real images."""
        config = OCRTestConfig()
        
        # Try to find the largest available sample image
        for image_name in ["sample_receipt.png", "sample_receipt_blurred.png"]:
            image_path = config.get_sample_image_path(image_name)
            
            if image_path and image_path.exists():
                # Check if image is reasonably large
                file_size = image_path.stat().st_size
                
                if file_size > 50000:  # 50KB+
                    with open(image_path, 'rb') as f:
                        image_data = f.read()
                    
                    # Should handle large images without issues
                    result = await extract_text_from_image(image_data)
                    
                    assert result.extracted_text is not None
                    assert result.processing_time_ms > 0
                    # Large images might take longer but shouldn't timeout
                    assert result.processing_time_ms < 30000  # 30 seconds max
                    
                    break
