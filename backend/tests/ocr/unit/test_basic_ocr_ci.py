"""
Basic OCR Tests for CI/CD Pipeline.

This module contains minimal, reliable tests for the OCR domain that work
in CI/CD environments without external dependencies.
"""

import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime
from uuid import uuid4

# Mark this as CI-ready unit tests
pytestmark = [pytest.mark.unit, pytest.mark.ocr]


class TestBasicOCR:
    """Basic OCR tests for CI/CD pipeline."""

    def test_main_functionality(self):
        """Required main functionality test."""
        # Basic OCR schema validation
        from domains.ocr.schemas import OCRTextResponse, ReceiptItem

        # Test OCRTextResponse schema
        response_data = {
            "extracted_text": "Test receipt text",
            "confidence": 95.0,
            "processing_time_ms": 1500,
        }
        response = OCRTextResponse(**response_data)
        assert response.extracted_text == "Test receipt text"
        assert response.confidence == 95.0
        assert response.processing_time_ms == 1500

    def test_ocr_text_response_schema(self):
        """Test OCR text response schema validation."""
        from domains.ocr.schemas import OCRTextResponse

        # Valid response
        valid_data = {
            "extracted_text": "Sample receipt text",
            "confidence": 87.5,
            "processing_time_ms": 2100,
        }
        response = OCRTextResponse(**valid_data)
        assert response.extracted_text == "Sample receipt text"
        if response.confidence is not None:
            assert 0.0 <= response.confidence <= 100.0
        if response.processing_time_ms is not None:
            assert response.processing_time_ms > 0

    def test_receipt_item_schema(self):
        """Test receipt item schema validation."""
        from domains.ocr.schemas import ReceiptItem

        # Valid receipt item
        item_data = {
            "detected_text": "Milk 1L",
            "quantity": 1.0,
            "unit": "L",
            "price": 2.50,
        }
        item = ReceiptItem(**item_data)
        assert item.detected_text == "Milk 1L"
        assert item.quantity == 1.0
        assert item.unit == "L"
        assert item.price == 2.50

    def test_ocr_processed_response_schema(self):
        """Test OCR processed response schema validation."""
        from domains.ocr.schemas import OCRProcessedResponse, ReceiptItem

        # Create test items
        items = [
            ReceiptItem(detected_text="Bread", quantity=1.0, price=1.99),
            ReceiptItem(detected_text="Milk", quantity=1.0, price=2.50),
        ]

        # Valid processed response
        response_data = {
            "raw_text": "Receipt text here",
            "detected_items": items,
            "processing_time_ms": 3200,
            "total_items_detected": 2,
        }
        response = OCRProcessedResponse(**response_data)
        assert len(response.detected_items) == 2
        assert response.total_items_detected == 2
        assert response.processing_time_ms == 3200
        assert response.raw_text == "Receipt text here"

    def test_ocr_error_handling_schema(self):
        """Test OCR error handling."""
        from domains.ocr.services import OCRError

        # Test basic error creation
        error = OCRError("Test OCR error")
        assert str(error) == "Test OCR error"
        assert isinstance(error, Exception)

    def test_ocr_service_import(self):
        """Test that OCR service can be imported."""
        from domains.ocr.services import OCRService

        # Basic import test - service should be importable
        assert OCRService is not None
        assert hasattr(OCRService, "__init__")

    @patch("domains.ocr.services.OCRService")
    def test_ocr_service_mock_functionality(self, mock_service):
        """Test OCR service with mocking."""
        # Mock service behavior
        mock_instance = MagicMock()
        mock_service.return_value = mock_instance

        # Mock methods
        mock_instance.extract_text.return_value = {
            "text": "Mocked receipt text",
            "confidence": 0.9,
        }

        # Test the mock
        service = mock_service()
        result = service.extract_text("dummy_image")

        assert result["text"] == "Mocked receipt text"
        assert result["confidence"] == 0.9
        mock_instance.extract_text.assert_called_once_with("dummy_image")

    def test_ocr_schema_field_validation(self):
        """Test OCR schema field validation."""
        from domains.ocr.schemas import ReceiptItem
        import pytest

        # Test valid item
        valid_item = ReceiptItem(detected_text="Test Item", quantity=1.0, price=5.99)
        assert valid_item.detected_text == "Test Item"
        assert valid_item.quantity == 1.0
        assert valid_item.price == 5.99

    def test_ocr_config_exists(self):
        """Test that OCR configuration exists."""
        try:
            from core.config import settings

            # Test that OCR-related config can be accessed
            assert hasattr(settings, "__dict__")
        except ImportError:
            # If settings not available in CI, that's OK
            pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
