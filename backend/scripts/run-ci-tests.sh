#!/bin/bash
# CI Test Runner for OCR functionality
# This script handles OCR testing in CI/CD environments with proper fallbacks

set -e

echo "=== OCR CI Test Runner ==="
echo "Environment: ${TEST_ENVIRONMENT:-development}"
echo "CI Environment: ${CI:-false}"

# Check Python environment
echo "Python version: $(python --version)"
echo "Pytest version: $(pytest --version)"

# Check Tesseract availability
echo "=== Checking Tesseract Installation ==="
if command -v tesseract &> /dev/null; then
    echo "✓ Tesseract found at: $(which tesseract)"
    echo "Version: $(tesseract --version 2>&1 | head -1)"
    echo "Available languages:"
    tesseract --list-langs 2>/dev/null | tail -n +2 | head -5
    TESSERACT_AVAILABLE=true
else
    echo "✗ Tesseract not found"
    TESSERACT_AVAILABLE=false
fi

# Set test environment variables
export OCR_TEST_MOCK_MODE=${OCR_TEST_MOCK_MODE:-true}
export OCR_TEST_INTEGRATION=${OCR_TEST_INTEGRATION:-false}
export TEST_ENVIRONMENT=${TEST_ENVIRONMENT:-ci}

# Override settings based on Tesseract availability
if [ "$TESSERACT_AVAILABLE" = false ]; then
    echo "⚠️ Tesseract not available - forcing mock mode"
    export OCR_TEST_MOCK_MODE=true
    export OCR_TEST_INTEGRATION=false
fi

echo "=== Test Configuration ==="
echo "OCR_TEST_MOCK_MODE: $OCR_TEST_MOCK_MODE"
echo "OCR_TEST_INTEGRATION: $OCR_TEST_INTEGRATION"
echo "TEST_ENVIRONMENT: $TEST_ENVIRONMENT"

# Function to run tests with specific markers
run_test_category() {
    local category=$1
    local marker=$2
    local description=$3
    
    echo ""
    echo "=== Running $description ==="
    
    pytest tests/ \
        -m "$marker" \
        --tb=short \
        -v \
        --junitxml="test-results-$category.xml" \
        --cov=domains \
        --cov-report="xml:coverage-$category.xml" \
        --cov-report=term-missing \
        || {
            echo "❌ $description failed"
            return 1
        }
    
    echo "✅ $description completed"
}

# Parse command line arguments
TEST_CATEGORY=${1:-all}

case $TEST_CATEGORY in
    "unit")
        echo "Running unit tests only..."
        run_test_category "unit" "unit and not ocr_integration" "Unit Tests"
        ;;
    "integration")
        if [ "$TESSERACT_AVAILABLE" = true ] && [ "$OCR_TEST_INTEGRATION" = true ]; then
            echo "Running integration tests..."
            run_test_category "integration" "integration" "Integration Tests"
        else
            echo "⚠️ Skipping integration tests - Tesseract not available or integration disabled"
            exit 0
        fi
        ;;
    "ocr")
        echo "Running OCR-specific tests..."
        if [ "$TESSERACT_AVAILABLE" = true ] && [ "$OCR_TEST_INTEGRATION" = true ]; then
            run_test_category "ocr-all" "ocr" "All OCR Tests"
        else
            run_test_category "ocr-unit" "ocr and not ocr_integration" "OCR Unit Tests (Mocked)"
        fi
        ;;
    "ocr-unit")
        echo "Running OCR unit tests (mocked)..."
        run_test_category "ocr-unit" "ocr_unit or (ocr and not ocr_integration)" "OCR Unit Tests"
        ;;
    "ocr-integration")
        if [ "$TESSERACT_AVAILABLE" = true ] && [ "$OCR_TEST_INTEGRATION" = true ]; then
            echo "Running OCR integration tests..."
            run_test_category "ocr-integration" "ocr_integration" "OCR Integration Tests"
        else
            echo "⚠️ Skipping OCR integration tests - requirements not met"
            echo "  Tesseract Available: $TESSERACT_AVAILABLE"
            echo "  Integration Enabled: $OCR_TEST_INTEGRATION"
            exit 0
        fi
        ;;
    "all")
        echo "Running all appropriate tests..."
        
        # Always run unit tests
        run_test_category "unit" "unit and not ocr_integration" "Unit Tests"
        
        # Run integration tests if possible
        if [ "$TESSERACT_AVAILABLE" = true ] && [ "$OCR_TEST_INTEGRATION" = true ]; then
            run_test_category "integration" "integration" "Integration Tests"
        else
            echo "⚠️ Skipping integration tests - requirements not met"
        fi
        ;;
    *)
        echo "Usage: $0 {unit|integration|ocr|ocr-unit|ocr-integration|all}"
        echo ""
        echo "Categories:"
        echo "  unit          - Run unit tests (no external dependencies)"
        echo "  integration   - Run integration tests (requires Tesseract)"
        echo "  ocr           - Run OCR tests (unit + integration if available)"
        echo "  ocr-unit      - Run only OCR unit tests"
        echo "  ocr-integration - Run only OCR integration tests"
        echo "  all           - Run all applicable tests"
        exit 1
        ;;
esac

echo ""
echo "=== Test Results Summary ==="
if ls test-results-*.xml 1> /dev/null 2>&1; then
    echo "Test result files:"
    ls -la test-results-*.xml
fi

if ls coverage-*.xml 1> /dev/null 2>&1; then
    echo "Coverage files:"
    ls -la coverage-*.xml
fi

echo "✅ OCR CI tests completed successfully"
