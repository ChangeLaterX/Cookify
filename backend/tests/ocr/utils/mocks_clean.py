"""
OCR Test Mocking Utilities.

This module provides comprehensive mocking utilities for OCR tests.
"""

from unittest.mock import Mock, MagicMock, AsyncMock, patch
from typing import Dict, Any, Optional, List, Union
from uuid import uuid4
from contextlib import contextmanager
import pytest

from domains.receipt.schemas import (
    OCRTextResponse,
    OCRProcessedResponse,
    ReceiptItem,
    OCRItemSuggestion,
)
from tests.ocr.config import OCRTestConfig


class OCRMockFactory:
    """Factory for creating OCR-related mocks."""
    
    @staticmethod
    def create_mock_ocr_service():
        """Create a fully mocked OCR service."""
        mock_service = MagicMock()
        
        # Mock async methods
        mock_service.extract_text_from_image = AsyncMock()
        mock_service.process_receipt_with_suggestions = AsyncMock()
        mock_service._find_ingredient_suggestions = AsyncMock()
        
        # Mock sync methods
        mock_service._extract_receipt_items = Mock()
        mock_service._extract_quantity_and_price = Mock()
        mock_service._preprocess_image_for_ocr = Mock()
        mock_service._normalize_unit = Mock()
        
        # Mock configuration
        mock_service.optimal_config = {
            'primary': '--psm 6 --oem 1',
            'fallback_psm_4': '--psm 4 --oem 1',
            'fallback_psm_11': '--psm 11 --oem 1',
            'default': '--psm 3 --oem 3'
        }
        
        return mock_service
    
    @staticmethod
    def create_mock_image():
        """Create a mock PIL Image."""
        mock_image = MagicMock()
        mock_image.mode = 'RGB'
        mock_image.size = (400, 600)
        mock_image.convert.return_value = mock_image
        mock_image.filter.return_value = mock_image
        mock_image.resize.return_value = mock_image
        return mock_image
    
    @staticmethod
    def create_mock_tesseract_data():
        """Create mock tesseract data output."""
        return {
            'conf': ['85', '90', '75', '80', '70'],
            'text': ['FRESH', 'MARKET', 'GROCERY', 'Tomatoes', '$3.98']
        }
    
    @staticmethod
    def create_mock_ingredient_suggestion():
        """Create a mock ingredient suggestion."""
        return OCRItemSuggestion(
            ingredient_id=uuid4(),
            ingredient_name="Tomatoes",
            confidence_score=90.0,
            detected_text="Tomatoes"
        )
    
    @staticmethod
    def create_mock_search_result():
        """Create a mock ingredient search result."""
        mock_result = Mock()
        mock_result.ingredients = [Mock(name="Tomatoes", ingredient_id=uuid4())]
        return mock_result


class OCRResponseFactory:
    """Factory for creating OCR response objects."""
    
    @staticmethod
    def create_ocr_text_response(
        text: str = "Sample OCR text",
        confidence: float = 85.0,
        processing_time: int = 100
    ) -> OCRTextResponse:
        """Create an OCR text response."""
        return OCRTextResponse(
            extracted_text=text,
            confidence=confidence,
            processing_time_ms=processing_time
        )
    
    @staticmethod
    def create_receipt_item(
        text: str = "Tomatoes",
        quantity: Optional[float] = 2.0,
        unit: Optional[str] = "lb",
        price: Optional[float] = 3.98,
        suggestions: Optional[List[OCRItemSuggestion]] = None
    ) -> ReceiptItem:
        """Create a receipt item."""
        if suggestions is None:
            suggestions = [OCRMockFactory.create_mock_ingredient_suggestion()]
        
        return ReceiptItem(
            detected_text=text,
            quantity=quantity,
            unit=unit,
            price=price,
            suggestions=suggestions
        )
    
    @staticmethod
    def create_ocr_processed_response(
        raw_text: str = "Sample receipt text",
        items: Optional[List[ReceiptItem]] = None,
        processing_time: int = 500
    ) -> OCRProcessedResponse:
        """Create an OCR processed response."""
        if items is None:
            items = [OCRResponseFactory.create_receipt_item()]
        
        return OCRProcessedResponse(
            raw_text=raw_text,
            detected_items=items,
            processing_time_ms=processing_time,
            total_items_detected=len(items)
        )


@pytest.fixture
def mock_ocr_environment():
    """Pytest fixture for comprehensive OCR environment mocking."""
    with patch.dict('sys.modules', {
        'pytesseract': MagicMock(),
        'PIL': MagicMock(),
        'PIL.Image': MagicMock(),
        'PIL.ImageEnhance': MagicMock(),
        'PIL.ImageFilter': MagicMock(),
    }):
        with patch('domains.receipt.services.OCR_AVAILABLE', True):
            yield


@pytest.fixture
def mock_ocr_service():
    """Pytest fixture for a mocked OCR service."""
    return OCRMockFactory.create_mock_ocr_service()


@pytest.fixture
def mock_image():
    """Pytest fixture for a mocked PIL Image."""
    return OCRMockFactory.create_mock_image()


@pytest.fixture
def mock_ingredient_search():
    """Pytest fixture for mocked ingredient search."""
    with patch('domains.receipt.services.search_ingredients') as mock_search:
        mock_search.return_value = OCRMockFactory.create_mock_search_result()
        yield mock_search


@pytest.fixture
def ocr_test_config():
    """Pytest fixture for OCR test configuration."""
    return OCRTestConfig()


class MockContextManager:
    """Context manager for complex mocking scenarios."""
    
    def __init__(self, mock_tesseract: bool = True, mock_pil: bool = True):
        self.mock_tesseract = mock_tesseract
        self.mock_pil = mock_pil
        self.patches = []
    
    def __enter__(self):
        """Enter the context manager."""
        if self.mock_tesseract:
            # Mock pytesseract
            mock_tesseract = MagicMock()
            mock_tesseract.image_to_string.return_value = "Sample OCR text"
            mock_tesseract.image_to_data.return_value = OCRMockFactory.create_mock_tesseract_data()
            mock_tesseract.Output.DICT = 'dict'
            
            tesseract_patch = patch('domains.receipt.services.pytesseract', mock_tesseract)
            self.patches.append(tesseract_patch)
            tesseract_patch.start()
        
        if self.mock_pil:
            # Mock PIL
            mock_image_class = MagicMock()
            mock_image_class.open.return_value = OCRMockFactory.create_mock_image()
            
            pil_patch = patch('domains.receipt.services.Image', mock_image_class)
            self.patches.append(pil_patch)
            pil_patch.start()
        
        # Mock OCR availability
        ocr_available_patch = patch('domains.receipt.services.OCR_AVAILABLE', True)
        self.patches.append(ocr_available_patch)
        ocr_available_patch.start()
        
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit the context manager."""
        for patch_obj in reversed(self.patches):
            patch_obj.stop()


# Convenience function for common mocking scenarios
def with_mocked_ocr(func):
    """Decorator to run a test with fully mocked OCR environment."""
    def wrapper(*args, **kwargs):
        with MockContextManager():
            return func(*args, **kwargs)
    return wrapper
