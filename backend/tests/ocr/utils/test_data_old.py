"""
OCR Test Data Utilities.

This module provides utilities for generating and managing test data.
"""

from typing import Dict, List, Tuple, Any
from pathlib import Path
import json

from tests.ocr.config import OCRTestConfig

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
    """
}

# Common OCR error patterns
OCR_ERROR_PATTERNS = {
    'lbs': ['its', 'ibs', 'ib', '1b', '11b', 'bs', 'ts'],
    'oz': ['goz', '02', '0z'],
    'gallon': ['galon', 'gailon', 'galion'],
    'count': ['cound', 'couns', 'counl'],
    'bulbs': ['bults', 'butte', 'bulhs'],
    'fresh': ['tresh', 'frfsh', 'frcsh']
}


class TestDataGenerator:
    """Generator for OCR test data."""
    
    @staticmethod
    def generate_receipt_variations() -> Dict[str, str]:
        """Generate various receipt text variations for testing."""
        return {
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
            """.strip(),
            
            "medium_quality": """
            FRESH MARKET GROCERY
            123 Main Street
            
            Tomatoes (2 Ibs)      $3.98
            Onions (1 ib)         $1.49
            Garlic (3 bults)      $2.25
            Bell Peppers (4)      $4.76
            Mitk (1 gallon)       $3.29
            """.strip(),
            
            "poor_quality": """
            FRESH MARKET GR0CERY
            123 Main Street
            
            Tomatnes (2 its)      $398
            0ni0ns (1 ib)         $149
            Garlie (3 bults)      $225
            Bell Peppers (4)      $476
            Mitk (1 gallon)       $329
            """.strip(),
            
            "very_poor_quality": """
            FR3SH MARK3T GR0C3RY
            123 Main Str33t
            
            Tm8t0es (Z !ts)       $39B
            0n!0ns (1 !b)         $14g
            G8rl!e (3 bu1ts)      $ZZ5
            B3ll P3pp3rs (4)      $47G
            M!tk (1 g8ll0n)       $3Zg
            """.strip(),
            
            "minimal_receipt": """
            Milk $3.29
            Bread $2.99
            Total: $6.28
            """.strip(),
            
            "handwritten_style": """
            Shopping List:
            - tomatoes (2lbs) - $3.98
            - milk 1gal - $3.29  
            - bread - $2.99
            total = $10.26
            """.strip()
        }
    
    @staticmethod
    def generate_quantity_price_test_cases() -> List[Tuple[str, float, str, float]]:
        """Generate test cases for quantity and price extraction."""
        return [
            # (text, expected_quantity, expected_unit, expected_price)
            ("Tomatoes (2 lbs) $3.98", 2.0, "lb", 3.98),
            ("Milk (1 gallon) $3.29", 1.0, "gal", 3.29),
            ("Eggs (12 count) $2.89", 12.0, "count", 2.89),
            ("Bananas (6) $2.94", 6.0, "pcs", 2.94),
            ("Olive Oil (500ml) $6.99", 500.0, "ml", 6.99),
            ("Cheese (8oz) $3.99", 8.0, "oz", 3.99),
            ("Rice (2 lbs) $3.49", 2.0, "lb", 3.49),
            ("Dozen Eggs $2.89", 12.0, "pcs", 2.89),
            ("Half Dozen Bagels $3.99", 6.0, "pcs", 3.99),
        ]
    
    @staticmethod
    def generate_ocr_error_test_cases() -> List[Tuple[str, str]]:
        """Generate OCR error correction test cases."""
        cases = []
        
        # Unit errors
        for error, correction in OCR_ERROR_PATTERNS["unit_errors"].items():
            cases.append((f"Tomatoes (2 {error})", correction))
        
        # Product errors  
        for error, correction in OCR_ERROR_PATTERNS["product_errors"].items():
            cases.append((f"{error} (2 lbs)", correction))
        
        return cases
    
    @staticmethod
    def generate_price_extraction_test_cases() -> List[Tuple[str, float]]:
        """Generate price extraction test cases."""
        return [
            ("Tomatoes $3.98", 3.98),
            ("Milk $3.29", 3.29),
            ("$4.76 Bell Peppers", 4.76),
            ("Item 12.34", 12.34),  # No dollar sign
            ("Product $129", 129.0),  # 3 digits - no auto-correction
            ("Item $234", 234.0),    # 3 digits - no auto-correction
            ("Food $1299", 12.99),   # 4 digits - gets corrected
            ("Store $2345", 23.45),  # 4 digits - gets corrected
            ("Bread $12.50", 12.50), # Standard format
            ("Eggs $2.89", 2.89),    # Standard format
        ]
    
    @staticmethod
    def generate_unit_normalization_test_cases() -> List[Tuple[str, str]]:
        """Generate unit normalization test cases."""
        return [
            # Weight units
            ("lbs", "lb"), ("pounds", "lb"), ("its", "lb"), ("ibs", "lb"),
            ("ounces", "oz"), ("goz", "oz"), ("kg", "kg"), ("grams", "g"),
            
            # Volume units
            ("gallon", "gal"), ("gallons", "gal"), ("liters", "l"),
            ("ml", "ml"), ("500ml", "ml"),
            
            # Count units
            ("pieces", "pcs"), ("count", "count"), ("cound", "count"),
            ("each", "pcs"), ("dozen", "dozen"),
            
            # OCR errors
            ("bults", "bulbs"), ("tresh", "fresh"),
        ]


class TestDataLoader:
    """Loader for test data from files."""
    
    def __init__(self, fixtures_path: Path):
        self.fixtures_path = fixtures_path
    
    def load_receipt_expectations(self, filename: str) -> Dict[str, Any]:
        """Load expected results for receipt processing."""
        file_path = self.fixtures_path / f"{filename}.json"
        if file_path.exists():
            with open(file_path, 'r') as f:
                return json.load(f)
        return {}
    
    def load_sample_image_data(self, filename: str) -> bytes:
        """Load sample image data for testing."""
        file_path = self.fixtures_path / "images" / filename
        if file_path.exists():
            with open(file_path, 'rb') as f:
                return f.read()
        return b"fake_image_data"


class TestDataValidator:
    """Validator for test data consistency."""
    
    @staticmethod
    def validate_receipt_item_expectations(data: Dict[str, Any]) -> bool:
        """Validate that receipt item expectations are properly formatted."""
        required_fields = ['text', 'expected_items']
        return all(field in data for field in required_fields)
    
    @staticmethod
    def validate_ocr_response_format(response: Dict[str, Any]) -> bool:
        """Validate OCR response format."""
        required_fields = ['extracted_text', 'confidence', 'processing_time_ms']
        return all(field in response for field in required_fields)


# Pre-generated test data for common scenarios
COMMON_TEST_DATA = {
    "receipt_variations": TestDataGenerator.generate_receipt_variations(),
    "quantity_price_cases": TestDataGenerator.generate_quantity_price_test_cases(),
    "ocr_error_cases": TestDataGenerator.generate_ocr_error_test_cases(),
    "price_extraction_cases": TestDataGenerator.generate_price_extraction_test_cases(),
    "unit_normalization_cases": TestDataGenerator.generate_unit_normalization_test_cases(),
}


def get_test_data(category: str) -> Any:
    """Get test data for a specific category."""
    return COMMON_TEST_DATA.get(category, [])


def create_test_fixtures_directory(base_path: Path):
    """Create the test fixtures directory structure."""
    fixtures_path = base_path / "fixtures"
    fixtures_path.mkdir(exist_ok=True)
    
    # Create subdirectories
    (fixtures_path / "images").mkdir(exist_ok=True)
    (fixtures_path / "expectations").mkdir(exist_ok=True)
    (fixtures_path / "responses").mkdir(exist_ok=True)
    
    # Create sample expectations file
    sample_expectations = {
        "clean_receipt": {
            "text": "Tomatoes (2 lbs) $3.98\nMilk (1 gallon) $3.29",
            "expected_items": ["Tomatoes", "Milk"],
            "expected_total_items": 2,
            "expected_confidence_range": [80, 95]
        }
    }
    
    with open(fixtures_path / "expectations" / "sample_receipts.json", 'w') as f:
        json.dump(sample_expectations, f, indent=2)
