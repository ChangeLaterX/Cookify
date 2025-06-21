# OCR Test Suite - Modular Architecture

This directory contains a comprehensive, modular test suite for the OCR (Optical Character Recognition) functionality in the Cookify backend application.

## 🏗️ Architecture Overview

The test suite is organized into a clean, modular structure that separates concerns and promotes maintainability:

```
tests/ocr/
├── __init__.py                 # Package initialization
├── config.py                   # Test configuration and base classes
├── run_tests.py               # Test runner script
├── README.md                  # This documentation
├── unit/                      # Unit tests (mocked dependencies)
│   ├── test_service_initialization.py
│   ├── test_text_extraction.py
│   ├── test_receipt_items.py
│   ├── test_data_extraction.py
│   ├── test_ingredient_suggestions.py
│   ├── test_complete_workflow.py
│   └── test_error_handling.py
├── integration/               # Integration tests (real dependencies)
│   ├── __init__.py
│   ├── test_real_ocr.py
│   └── test_performance.py
├── fixtures/                  # Test data and sample responses
│   └── __init__.py
└── utils/                     # Test utilities and mocks
    ├── __init__.py
    ├── mocks.py
    └── test_data.py
```

## 🎯 Key Features

### ✅ Comprehensive Coverage
- **Service Initialization**: Dependency management and configuration
- **Text Extraction**: OCR processing with various image types
- **Receipt Processing**: Item extraction and parsing
- **Data Extraction**: Quantity, unit, and price parsing with OCR error correction
- **Ingredient Suggestions**: Matching with ingredient database
- **Error Handling**: Graceful error handling and edge cases
- **Performance**: Benchmarking and scalability testing

### 🔧 Modular Design
- **Separation of Concerns**: Each test module focuses on specific functionality
- **Reusable Components**: Shared utilities, mocks, and test data generators
- **Clean Dependencies**: Clear separation between unit and integration tests
- **Easy Maintenance**: Well-organized structure for adding new tests

### 🚀 Advanced Features
- **Smart Mocking**: Comprehensive mock framework that handles OCR dependencies
- **Test Data Generation**: Realistic test data with OCR error patterns
- **Performance Benchmarking**: Latency, throughput, and memory usage tests
- **Error Simulation**: Tests for various error conditions and edge cases
- **Cross-Platform Support**: Tests work across different environments

## 🚀 Quick Start

### Prerequisites
```bash
# Required for all tests
pip install pytest pytest-asyncio pytest-cov

# Required for integration tests only
sudo apt-get install tesseract-ocr  # Ubuntu/Debian
# or
brew install tesseract  # macOS

pip install pytesseract Pillow
```

### Running Tests

#### Using the Test Runner (Recommended)
```bash
# Run all unit tests
python tests/ocr/run_tests.py --unit

# Run integration tests (requires tesseract)
python tests/ocr/run_tests.py --integration

# Run all tests with coverage
python tests/ocr/run_tests.py --all --coverage

# Run performance benchmarks
python tests/ocr/run_tests.py --performance

# Generate comprehensive test report
python tests/ocr/run_tests.py --report
```

#### Using pytest Directly
```bash
# Unit tests only (with mocks)
pytest tests/ocr/unit/ -v

# Integration tests (requires real dependencies)
OCR_TEST_INTEGRATION=true pytest tests/ocr/integration/ -v

# All tests
pytest tests/ocr/ -v

# With coverage
pytest tests/ocr/ --cov=domains.ocr.services --cov-report=html
```

#### Running Specific Tests
```bash
# Specific test module
python tests/ocr/run_tests.py --specific unit/test_text_extraction.py

# Specific test function
pytest tests/ocr/unit/test_text_extraction.py::TestOCRTextExtraction::test_extract_text_success -v
```

## 🧪 Test Categories

### Unit Tests (`unit/`)
Fast, isolated tests with mocked dependencies. Always run regardless of system setup.

- **test_service_initialization.py**: OCR service setup and configuration
- **test_text_extraction.py**: Core OCR text extraction functionality
- **test_receipt_items.py**: Receipt item identification and filtering
- **test_data_extraction.py**: Quantity, unit, and price parsing
- **test_ingredient_suggestions.py**: Ingredient matching and suggestions
- **test_complete_workflow.py**: End-to-end workflow testing
- **test_error_handling.py**: Error conditions and edge cases

### Integration Tests (`integration/`)
Tests with real OCR dependencies. Require tesseract installation.

- **test_real_ocr.py**: Real OCR processing with sample images
- **test_performance.py**: Performance benchmarks and scalability

## 🛠️ Configuration

### Environment Variables
```bash
# Test mode configuration
export OCR_TEST_MOCK_MODE=true        # Use mocks (default)
export OCR_TEST_INTEGRATION=false     # Skip integration tests (default)

# For integration tests
export OCR_TEST_INTEGRATION=true      # Enable integration tests
export OCR_TEST_MOCK_MODE=false       # Use real dependencies
```

### Test Configuration
The `OCRTestConfig` class in `config.py` manages test settings:

```python
from tests.ocr.config import OCRTestConfig

config = OCRTestConfig()
print(f"Tesseract available: {config.TESSERACT_AVAILABLE}")
print(f"Should run integration: {config.should_run_integration_tests()}")
```

## 🔧 Utilities and Mocks

### Mock Framework (`utils/mocks.py`)
Comprehensive mocking system for OCR dependencies:

```python
from tests.ocr.utils.mocks import MockContextManager, OCRMockFactory

# Use context manager for automatic setup/teardown
with MockContextManager() as mock_ctx:
    service = OCRService()
    result = await service.extract_text_from_image(image_data)

# Create specific mock responses
mock_response = OCRMockFactory.create_ocr_text_response(
    text="Sample receipt text",
    confidence=85.0
)
```

### Test Data Generation (`utils/test_data.py`)
Realistic test data with OCR error patterns:

```python
from tests.ocr.utils.test_data import TestDataGenerator

# Generate sample image data
image_data = TestDataGenerator.generate_sample_image_bytes()

# Generate OCR responses with realistic errors
response = TestDataGenerator.generate_ocr_text_response_with_errors()

# Generate ingredient search results
ingredients = TestDataGenerator.generate_mock_ingredient_search_results("tomatoes", 3)
```

## 📊 Test Coverage

The test suite provides comprehensive coverage across multiple dimensions:

### Functional Coverage
- ✅ OCR text extraction (multiple algorithms and configurations)
- ✅ Image preprocessing (contrast, sharpening, noise reduction)
- ✅ Receipt item identification (food vs non-food filtering)
- ✅ Data extraction (quantities, units, prices with OCR error correction)
- ✅ Ingredient matching (fuzzy matching with confidence scoring)
- ✅ Error handling (graceful degradation and recovery)

### Error Scenarios
- ✅ Missing dependencies (tesseract, PIL, pytesseract)
- ✅ Corrupted image data
- ✅ OCR processing failures
- ✅ Network/database errors in ingredient search
- ✅ Memory and performance edge cases

### OCR Quality Variations
- ✅ High-quality clear images
- ✅ Blurred or low-quality images
- ✅ Rotated or skewed images
- ✅ Various image sizes and formats
- ✅ Different receipt layouts and formats

## 🎯 Best Practices

### Adding New Tests

1. **Unit Tests**: Add to appropriate module in `unit/` directory
2. **Integration Tests**: Add to `integration/` directory with proper skipif decorators
3. **Test Data**: Use `TestDataGenerator` for consistent, realistic test data
4. **Mocking**: Use `MockContextManager` for automatic mock setup/teardown

### Writing Test Functions

```python
import pytest
from tests.ocr.config import OCRTestBase
from tests.ocr.utils.mocks import MockContextManager
from tests.ocr.utils.test_data import TestDataGenerator

class TestMyOCRFeature(OCRTestBase):
    """Test my OCR feature with proper structure."""

    @pytest.mark.asyncio
    async def test_my_feature_success(self):
        """Test successful operation of my feature."""
        with MockContextManager() as mock_ctx:
            # Use test data generator
            test_data = TestDataGenerator.generate_sample_image_bytes()
            
            # Your test logic here
            result = await my_ocr_function(test_data)
            
            # Assertions
            assert result is not None
            assert result.confidence > 0
```

### Performance Testing

```python
@pytest.mark.asyncio
async def test_performance_benchmark(self):
    """Test performance with timing assertions."""
    import time
    
    start_time = time.time()
    result = await ocr_function(large_image_data)
    processing_time = (time.time() - start_time) * 1000
    
    # Performance assertions
    assert processing_time < 5000  # Less than 5 seconds
    assert result.processing_time_ms < 10000
```

## 🐛 Troubleshooting

### Common Issues

#### "OCR dependencies not available"
```bash
# Install tesseract
sudo apt-get install tesseract-ocr  # Ubuntu/Debian
brew install tesseract              # macOS

# Install Python packages
pip install pytesseract Pillow
```

#### Tests hanging or timing out
```bash
# Run with shorter timeout
pytest tests/ocr/ --timeout=30

# Check for dependency conflicts
pip list | grep -E "(PIL|pytesseract|pytest)"
```

#### Integration tests failing
```bash
# Verify tesseract installation
tesseract --version

# Check sample images exist
ls -la data/sample_receipt*.png

# Run with verbose output
python tests/ocr/run_tests.py --integration --verbose
```

### Debug Mode
```bash
# Run tests with debug output
pytest tests/ocr/ -v -s --log-cli-level=DEBUG

# Run specific failing test
pytest tests/ocr/unit/test_text_extraction.py::test_specific_function -v -s
```

## 📈 Performance Expectations

### Unit Tests
- **Execution Time**: < 30 seconds for full unit test suite
- **Individual Tests**: < 1 second per test
- **Memory Usage**: < 100MB peak

### Integration Tests
- **OCR Processing**: < 10 seconds per image
- **End-to-End Workflow**: < 15 seconds per receipt
- **Memory Usage**: < 500MB peak

### Performance Benchmarks
Run performance tests to establish baselines:
```bash
python tests/ocr/run_tests.py --performance
```

## 🔄 Migration from Old Tests

The new modular architecture replaces the monolithic `test_ocr.py`. Key improvements:

### Before (Monolithic)
- Single 600+ line file
- All tests in one class
- Mixed unit and integration tests
- Limited reusability
- Difficult to maintain

### After (Modular)
- Organized into focused modules
- Separated unit and integration tests
- Comprehensive mocking framework
- Reusable utilities and generators
- Easy to extend and maintain

### Migration Steps
1. New tests use the modular structure automatically
2. Legacy `test_ocr.py` remains for compatibility
3. Gradually migrate specific test cases to new modules
4. Eventually remove old monolithic file

## 📚 API Reference

### Configuration Classes
- `OCRTestConfig`: Test configuration management
- `OCRTestBase`: Base class for test classes

### Mock Framework
- `MockContextManager`: Automatic mock setup/teardown
- `OCRMockFactory`: Factory for creating mock objects
- `with_mocked_ocr`: Decorator for mocked OCR tests

### Test Data
- `TestDataGenerator`: Generate realistic test data
- Sample fixtures in `fixtures/` directory

### Test Runner
- `run_tests.py`: Comprehensive test execution script
- Support for unit, integration, performance, and coverage testing

---

## 🤝 Contributing

When adding new tests:

1. Follow the modular structure
2. Use the provided utilities and mocks
3. Include both positive and negative test cases
4. Add performance tests for new features
5. Update documentation as needed

For questions or issues with the test suite, refer to the troubleshooting section or check the existing test implementations for examples.
