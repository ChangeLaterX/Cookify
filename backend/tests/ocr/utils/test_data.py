"""
OCR Test Data Utilities.

This module provides utilities for generating and managing test data.
"""

import json
import random
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from uuid import uuid4

from domains.ingredients.schemas import (IngredientListResponse,
                                         IngredientMasterResponse)
from domains.ocr.schemas import (OCRItemSuggestion, OCRProcessedResponse,
                                 OCRTextResponse, ReceiptItem)
from pydantic import BaseModel


# Define missing types for test compatibility
class Ingredient(BaseModel):
    """Mock ingredient model for tests."""

    ingredient_id: str
    name: str
    description: Optional[str] = None


class IngredientSearchResult(BaseModel):
    """Mock ingredient search result for tests."""

    ingredients: List[Ingredient]
    total_count: int
    offset: int
    limit: int


# Receipt text variations for testing
RECEIPT_TEXT_VARIATIONS = {
    "perfect_quality": """
    FRESH MARKET GROCERY
    123 Main Street
    
    Tomatoes (2 lbs)      $3.98
    Onions (1 lb)         $1.49
    Garlic (3 bulbs)      $2.25
    Bell Peppers (4)      $4.76
    Milk (1 gallon)       $3.29
    
    Subtotal:            $15.77
    Tax:                 $1.26
    Total:               $17.03
    """,
    "ocr_errors": """
    FRFSH MARKFT GROCFRY
    123 Main Streft
    
    Tomatnes (2 its)      $398
    Onins (1 ib)          $149
    Garlie (3 bults)      $225
    Beli Peppfrs (4)      $476
    Mitk (1 galon)        $329
    
    Subtott:             $1577
    Tax:                 $126
    Tout:                $1703
    """,
    "poor_quality": """
    FR5H M4RK3T GR0C3RY
    
    T0m4t03s      $3 98
    0n10ns        $1 49
    G4rl1c        $2 25
    
    T0t4l:        $17 03
    """,
}

# Common OCR error patterns
OCR_ERROR_PATTERNS = {
    "unit_errors": {
        "its": "lbs",
        "ibs": "lbs",
        "ib": "lb",
        "1b": "lb",
        "11b": "lbs",
        "bs": "lbs",
        "ts": "lbs",
        "goz": "oz",
        "02": "oz",
        "0z": "oz",
        "galon": "gallon",
        "gailon": "gallon",
        "galion": "gallon",
        "cound": "count",
        "couns": "count",
        "counl": "count",
        "bults": "bulbs",
        "butte": "bulbs",
        "bulhs": "bulbs",
        "tresh": "fresh",
        "frfsh": "fresh",
        "frcsh": "fresh",
    },
    "product_errors": {
        "Tomatnes": "Tomatoes",
        "Onins": "Onions",
        "Garlie": "Garlic",
        "Mitk": "Milk",
        "Imtik": "Milk",
        "Fggs": "Eggs",
        "Chesidar": "Cheddar",
        "Pasa": "Pasta",
        "Otiweoit": "Olive Oil",
        "Basilfresh": "Basil Fresh",
    },
}


class TestDataGenerator:
    """Generator for OCR test data."""

    @staticmethod
    def generate_receipt_variations() -> Dict[str, str]:
        """Generate various receipt text variations for testing."""
        return RECEIPT_TEXT_VARIATIONS.copy()

    @staticmethod
    def generate_sample_image_bytes(size: int = 1024) -> bytes:
        """Generate sample image data for testing."""
        # Create fake image header + random data
        header = b"\x89PNG\r\n\x1a\n"  # PNG header
        data = bytes([random.randint(0, 255) for _ in range(size - len(header))])
        return header + data

    @staticmethod
    def generate_ocr_text_response(
        text: str = "Sample receipt text",
        confidence: float = 85.0,
        processing_time: int = 100,
    ) -> OCRTextResponse:
        """Generate OCR text response for testing."""
        return OCRTextResponse(
            extracted_text=text,
            confidence=confidence,
            processing_time_ms=processing_time,
        )

    @staticmethod
    def generate_ocr_text_response_with_errors(
        base_text: Optional[str] = None,
    ) -> OCRTextResponse:
        """Generate OCR text response with realistic error patterns."""
        if base_text is None:
            base_text = RECEIPT_TEXT_VARIATIONS["ocr_errors"]

        return OCRTextResponse(
            extracted_text=base_text,
            confidence=random.uniform(45.0, 75.0),  # Lower confidence for errors
            processing_time_ms=random.randint(80, 200),
        )

    @staticmethod
    def generate_receipt_item(
        text: str = "Test Item",
        quantity: Optional[float] = None,
        unit: Optional[str] = None,
        price: Optional[float] = None,
        suggestions_count: int = 2,
    ) -> ReceiptItem:
        """Generate receipt item for testing."""
        suggestions = []
        for i in range(suggestions_count):
            suggestions.append(
                OCRItemSuggestion(
                    ingredient_id=uuid4(),
                    ingredient_name=f"Test Ingredient {i+1}",
                    confidence_score=random.uniform(60.0, 95.0),
                    detected_text=text,
                )
            )

        return ReceiptItem(
            detected_text=text,
            quantity=quantity or random.uniform(1.0, 5.0),
            unit=unit or random.choice(["lbs", "oz", "count", "gallon"]),
            price=price or random.uniform(1.0, 10.0),
            suggestions=suggestions,
        )

    @staticmethod
    def generate_ocr_processed_response(
        items_count: int = 3, processing_time: int = 150
    ) -> OCRProcessedResponse:
        """Generate OCR processed response for testing."""
        items = []
        for i in range(items_count):
            items.append(
                TestDataGenerator.generate_receipt_item(
                    text=f"Test Item {i+1}", suggestions_count=random.randint(1, 3)
                )
            )

        return OCRProcessedResponse(
            raw_text="Sample receipt text",
            detected_items=items,
            processing_time_ms=processing_time,
            total_items_detected=items_count,
        )

    @staticmethod
    def generate_mock_ingredient(
        name: str = "Test Ingredient", ingredient_id: Optional[str] = None
    ) -> Ingredient:
        """Generate mock ingredient for testing."""
        return Ingredient(
            ingredient_id=str(uuid4()) if ingredient_id is None else ingredient_id,
            name=name,
            description=f"Description for {name}",
        )

    @staticmethod
    def generate_mock_ingredient_search_results(
        query: str = "test", count: int = 3
    ) -> IngredientSearchResult:
        """Generate mock ingredient search results."""
        ingredients = []
        for i in range(count):
            ingredients.append(
                TestDataGenerator.generate_mock_ingredient(
                    name=f"{query.title()} Variant {i+1}"
                )
            )

        return IngredientSearchResult(
            ingredients=ingredients, total_count=count, offset=0, limit=count
        )

    @staticmethod
    def apply_ocr_errors(text: str, error_rate: float = 0.3) -> str:
        """Apply OCR error patterns to text."""
        words = text.split()
        modified_words = []

        for word in words:
            if random.random() < error_rate:
                # Apply random OCR error pattern
                for correct, errors in OCR_ERROR_PATTERNS["unit_errors"].items():
                    if correct in word.lower():
                        word = word.lower().replace(correct, errors)
                        break
            modified_words.append(word)

        return " ".join(modified_words)

    @staticmethod
    def generate_quantity_price_test_cases() -> (
        List[Tuple[str, Optional[float], Optional[str], Optional[float]]]
    ):
        """Generate test cases for quantity and price extraction."""
        return [
            ("Tomatoes (2 lbs) $3.98", 2.0, "lbs", 3.98),
            ("Onions (1 lb) $1.49", 1.0, "lb", 1.49),
            ("Garlic (3 bulbs) $2.25", 3.0, "bulbs", 2.25),
            ("Milk (1 gallon) $3.29", 1.0, "gallon", 3.29),
            ("Eggs (12 count) $2.89", 12.0, "count", 2.89),
            ("Cheese (8 oz) $3.99", 8.0, "oz", 3.99),
            ("Bread $2.99", None, None, 2.99),  # No quantity
            ("Rice (2 lbs)", 2.0, "lbs", None),  # No price
            ("Salt", None, None, None),  # No quantity or price
        ]

    @staticmethod
    def generate_ocr_error_test_cases() -> List[Tuple[str, str]]:
        """Generate test cases with OCR errors."""
        return [
            ("Tomatoes (2 lbs) $3.98", "Tomatnes (2 its) $398"),
            ("Onions (1 lb) $1.49", "Onins (1 ib) $149"),
            ("Garlic (3 bulbs) $2.25", "Garlie (3 bults) $225"),
            ("Fresh milk (1 gallon) $3.29", "Tresh mitk (1 galon) $329"),
        ]

    @staticmethod
    def load_expected_results(test_name: str) -> Dict[str, Any]:
        """Load expected results for receipt processing."""
        # Return default expected results for testing
        return {
            "items_detected": 3,
            "confidence_threshold": 80.0,
            "processing_time_max": 5000,
            "expected_items": ["tomatoes", "onions", "garlic"],
        }

    @staticmethod
    def create_test_configuration(
        mock_mode: bool = True, integration: bool = False, performance: bool = False
    ) -> Dict[str, Any]:
        """Create test configuration for different test scenarios."""
        return {
            "mock_mode": mock_mode,
            "integration_mode": integration,
            "performance_mode": performance,
            "timeout_seconds": 30 if not performance else 120,
            "max_retries": 3,
            "confidence_threshold": 75.0,
            "sample_image_sizes": [512, 1024, 2048] if performance else [1024],
        }
