"""
OCR Test Mocking Utilities.

This module provides comprehensive mocking utilities for OCR tests.
"""

from unittest.mock import Mock, MagicMock, AsyncMock, patch
from typing import Dict, Any, Optional, List, Union
from uuid import uuid4
from contextlib import contextmanager
import pytest

from domains.ocr.schemas import (
    OCRTextResponse,
    OCRProcessedResponse,
    ReceiptItem,
    OCRItemSuggestion,
)
from domains.ingredients.schemas import Ingredient, IngredientSearchResult
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
    def create_mock_ocr_text_response(
        text: str = "Sample receipt text",
        confidence: float = 85.0,
        processing_time: int = 100
    ) -> OCRTextResponse:
        """Create a mock OCR text response."""
        return OCRTextResponse(
            extracted_text=text,
            confidence=confidence,
            processing_time_ms=processing_time
        )
    
    @staticmethod
    def create_mock_ocr_processed_response(
        items_count: int = 3,
        processing_time: int = 150
    ) -> OCRProcessedResponse:
        """Create a mock OCR processed response."""
        items = []
        for i in range(items_count):
            items.append(OCRMockFactory.create_mock_receipt_item(
                text=f"Test Item {i+1}"
            ))
        
        return OCRProcessedResponse(
            raw_text="Sample receipt text",
            detected_items=items,
            processing_time_ms=processing_time,
            total_items_detected=items_count
        )
    
    @staticmethod
    def create_mock_receipt_item(
        text: str = "Test Item",
        quantity: Optional[float] = 2.0,
        unit: Optional[str] = "lbs",
        price: Optional[float] = 3.99,
        suggestions_count: int = 2
    ) -> ReceiptItem:
        """Create a mock receipt item."""
        suggestions = []
        for i in range(suggestions_count):
            suggestions.append(OCRItemSuggestion(
                ingredient_id=uuid4(),
                ingredient_name=f"Test Ingredient {i+1}",
                confidence_score=85.0 + i,
                detected_text=text
            ))
        
        return ReceiptItem(
            detected_text=text,
            quantity=quantity,
            unit=unit,
            price=price,
            suggestions=suggestions
        )
    
    @staticmethod
    def create_mock_image():
        """Create a mock PIL Image object."""
        mock_image = MagicMock()
        mock_image.mode = 'RGB'
        mock_image.size = (800, 600)
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
    def create_mock_ingredient(
        name: str = "Tomatoes",
        ingredient_id: Optional[str] = None
    ) -> Ingredient:
        """Create a mock ingredient for suggestions."""
        return Ingredient(
            ingredient_id=uuid4() if ingredient_id is None else ingredient_id,
            name=name,
            description=f"Fresh {name.lower()}"
        )
    
    @staticmethod
    def create_mock_ingredient_search_result(
        query: str = "tomatoes",
        count: int = 3
    ) -> IngredientSearchResult:
        """Create a mock ingredient search result."""
        ingredients = []
        for i in range(count):
            ingredients.append(OCRMockFactory.create_mock_ingredient(
                name=f"{query.title()} {i+1}"
            ))
        
        return IngredientSearchResult(
            ingredients=ingredients,
            total_count=count,
            offset=0,
            limit=count
        )


class MockContextManager:
    """Context manager for comprehensive OCR mocking."""
    
    def __init__(self, 
                 ocr_available: bool = True,
                 tesseract_available: bool = True,
                 mock_responses: Optional[Dict[str, Any]] = None):
        """Initialize the mock context manager."""
        self.ocr_available = ocr_available
        self.tesseract_available = tesseract_available
        self.mock_responses = mock_responses or {}
        self.patches = []
        self.mocks = {}
    
    def __enter__(self):
        """Enter the mock context."""
        # Mock OCR availability
        ocr_patch = patch('domains.ocr.services.OCR_AVAILABLE', self.ocr_available)
        self.patches.append(ocr_patch)
        ocr_patch.start()
        
        if self.ocr_available:
            # Mock PIL Image
            image_patch = patch('domains.ocr.services.Image')
            self.patches.append(image_patch)
            mock_image_class = image_patch.start()
            mock_image_class.open.return_value = OCRMockFactory.create_mock_image()
            self.mocks['image_class'] = mock_image_class
            
            # Mock pytesseract
            tesseract_patch = patch('domains.ocr.services.pytesseract')
            self.patches.append(tesseract_patch)
            mock_tesseract = tesseract_patch.start()
            
            # Configure pytesseract mocks
            mock_tesseract.image_to_string.return_value = self.mock_responses.get(
                'extracted_text', 
                "FRESH MARKET GROCERY\nTomatoes (2 lbs) $3.98"
            )
            mock_tesseract.image_to_data.return_value = self.mock_responses.get(
                'tesseract_data',
                OCRMockFactory.create_mock_tesseract_data()
            )
            mock_tesseract.Output.DICT = 'dict'
            self.mocks['tesseract'] = mock_tesseract
            
            # Mock tesseract path detection
            which_patch = patch('shutil.which', return_value='/usr/bin/tesseract' if self.tesseract_available else None)
            self.patches.append(which_patch)
            which_patch.start()
            
            isfile_patch = patch('os.path.isfile', return_value=self.tesseract_available)
            self.patches.append(isfile_patch)
            isfile_patch.start()
        
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit the mock context."""
        for patch_obj in reversed(self.patches):
            patch_obj.stop()
        self.patches.clear()
        self.mocks.clear()
    
    def set_mock_response(self, key: str, value: Any):
        """Set a mock response value."""
        self.mock_responses[key] = value
        
        # Update existing mocks if they exist
        if key == 'extracted_text' and 'tesseract' in self.mocks:
            self.mocks['tesseract'].image_to_string.return_value = value
        elif key == 'tesseract_data' and 'tesseract' in self.mocks:
            self.mocks['tesseract'].image_to_data.return_value = value


def with_mocked_ocr(
    ocr_available: bool = True,
    tesseract_available: bool = True,
    mock_responses: Optional[Dict[str, Any]] = None
):
    """Decorator for mocking OCR dependencies in tests."""
    def decorator(test_func):
        def wrapper(*args, **kwargs):
            with MockContextManager(ocr_available, tesseract_available, mock_responses):
                return test_func(*args, **kwargs)
        return wrapper
    return decorator


class OCRTestDoubles:
    """Test doubles for OCR testing."""
    
    @staticmethod
    def create_fake_ocr_service():
        """Create a fake OCR service that doesn't use real dependencies."""
        class FakeOCRService:
            def __init__(self):
                self.optimal_config = {
                    'primary': '--psm 6 --oem 1',
                    'fallback_psm_4': '--psm 4 --oem 1',
                    'fallback_psm_11': '--psm 11 --oem 1',
                    'default': '--psm 3 --oem 3'
                }
            
            async def extract_text_from_image(self, image_data: bytes) -> OCRTextResponse:
                return OCRMockFactory.create_mock_ocr_text_response()
            
            async def process_receipt_with_suggestions(self, image_data: bytes) -> OCRProcessedResponse:
                return OCRMockFactory.create_mock_ocr_processed_response()
            
            def _extract_receipt_items(self, text: str) -> List[str]:
                return ["Tomatoes", "Onions", "Garlic"]
            
            def _extract_quantity_and_price(self, text: str):
                return (2.0, "lbs", 3.98)
            
            def _normalize_unit(self, unit: str) -> str:
                unit_mapping = {
                    'lbs': 'lb', 'its': 'lb', 'ibs': 'lb',
                    'gallon': 'gal', 'galon': 'gal'
                }
                return unit_mapping.get(unit.lower(), unit.lower())
        
        return FakeOCRService()


class MockFixtures:
    """Pre-configured mock fixtures for common test scenarios."""
    
    @staticmethod
    def perfect_receipt_scenario():
        """Mock scenario with perfect OCR results."""
        return {
            'extracted_text': """
            FRESH MARKET GROCERY
            123 Main Street
            
            Tomatoes (2 lbs)      $3.98
            Onions (1 lb)         $1.49
            Garlic (3 bulbs)      $2.25
            
            Total:               $7.72
            """,
            'tesseract_data': {
                'conf': ['95', '92', '88', '90', '85'],
                'text': ['FRESH', 'MARKET', 'Tomatoes', 'Onions', 'Garlic']
            }
        }
    
    @staticmethod
    def poor_quality_receipt_scenario():
        """Mock scenario with poor OCR quality."""
        return {
            'extracted_text': """
            FRFSH MARKFT
            
            Tomatnes (2 its)      $398
            Onins (1 ib)          $149
            Garlie (3 bults)      $225
            """,
            'tesseract_data': {
                'conf': ['45', '52', '38', '41', '35'],
                'text': ['FRFSH', 'MARKFT', 'Tomatnes', 'Onins', 'Garlie']
            }
        }
    
    @staticmethod
    def empty_receipt_scenario():
        """Mock scenario with empty or minimal content."""
        return {
            'extracted_text': "   \n  \n   ",
            'tesseract_data': {
                'conf': ['0', '0', '0'],
                'text': ['', '', '']
            }
        }


@contextmanager
def mock_ocr_environment(scenario: str = "perfect"):
    """Context manager for setting up specific OCR test scenarios."""
    scenarios = {
        "perfect": MockFixtures.perfect_receipt_scenario(),
        "poor_quality": MockFixtures.poor_quality_receipt_scenario(),
        "empty": MockFixtures.empty_receipt_scenario()
    }
    
    mock_responses = scenarios.get(scenario, MockFixtures.perfect_receipt_scenario())
    
    with MockContextManager(mock_responses=mock_responses) as mock_ctx:
        yield mock_ctx


class AsyncMockManager:
    """Manager for async mocks in OCR tests."""
    
    def __init__(self):
        self.async_mocks = {}
    
    def create_async_mock(self, name: str, return_value=None, side_effect=None):
        """Create an async mock with specified behavior."""
        async_mock = AsyncMock()
        
        if return_value is not None:
            async_mock.return_value = return_value
        if side_effect is not None:
            async_mock.side_effect = side_effect
        
        self.async_mocks[name] = async_mock
        return async_mock
    
    def get_mock(self, name: str):
        """Get an async mock by name."""
        return self.async_mocks.get(name)
    
    def reset_all_mocks(self):
        """Reset all async mocks."""
        for mock in self.async_mocks.values():
            mock.reset_mock()


# Pre-configured test scenarios
TEST_SCENARIOS = {
    "unit_test_default": {
        "ocr_available": True,
        "tesseract_available": True,
        "mock_responses": MockFixtures.perfect_receipt_scenario()
    },
    "integration_test_setup": {
        "ocr_available": True,
        "tesseract_available": True,
        "mock_responses": None  # Use real responses
    },
    "dependency_missing": {
        "ocr_available": False,
        "tesseract_available": False,
        "mock_responses": None
    },
    "poor_ocr_quality": {
        "ocr_available": True,
        "tesseract_available": True,
        "mock_responses": MockFixtures.poor_quality_receipt_scenario()
    }
}


def get_test_scenario(scenario_name: str) -> Dict[str, Any]:
    """Get a pre-configured test scenario."""
    return TEST_SCENARIOS.get(scenario_name, TEST_SCENARIOS["unit_test_default"])
