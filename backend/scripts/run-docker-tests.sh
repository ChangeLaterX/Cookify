#!/bin/bash
# Docker-based OCR Test Runner
# This script runs OCR tests inside Docker containers to ensure consistency

set -e

echo "=== Docker OCR Test Runner ==="

BACKEND_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PROJECT_ROOT="$(cd "$BACKEND_DIR/.." && pwd)"

# Default values
TEST_TYPE=${1:-all}
CLEANUP=${CLEANUP:-true}

echo "Backend directory: $BACKEND_DIR"
echo "Project root: $PROJECT_ROOT"
echo "Test type: $TEST_TYPE"

# Function to run tests in Docker
run_docker_tests() {
    local service_name=$1
    local test_description=$2
    
    echo ""
    echo "=== Running $test_description ==="
    
    cd "$BACKEND_DIR"
    
    # Build and run the specific test service
    docker-compose -f docker-compose.test.yml build "$service_name"
    docker-compose -f docker-compose.test.yml run --rm "$service_name"
    
    local exit_code=$?
    
    if [ $exit_code -eq 0 ]; then
        echo "✅ $test_description completed successfully"
    else
        echo "❌ $test_description failed with exit code $exit_code"
        if [ "$CLEANUP" = true ]; then
            echo "Cleaning up..."
            docker-compose -f docker-compose.test.yml down -v
        fi
        return $exit_code
    fi
}

# Function to test OCR functionality specifically
test_ocr_in_docker() {
    echo ""
    echo "=== Testing OCR Functionality in Docker ==="
    
    cd "$BACKEND_DIR"
    
    # Build the test image
    docker-compose -f docker-compose.test.yml build backend-test
    
    # Run OCR-specific tests
    docker-compose -f docker-compose.test.yml run --rm \
        -e OCR_TEST_MOCK_MODE=false \
        -e OCR_TEST_INTEGRATION=true \
        backend-test \
        sh -c "
            echo 'Verifying Tesseract in container...' &&
            tesseract --version &&
            tesseract --list-langs &&
            echo 'Running OCR tests...' &&
            pytest tests/ocr/ --tb=short -v -x
        "
    
    local exit_code=$?
    
    if [ $exit_code -eq 0 ]; then
        echo "✅ Docker OCR tests completed successfully"
    else
        echo "❌ Docker OCR tests failed"
        return $exit_code
    fi
}

# Main test execution
case $TEST_TYPE in
    "unit")
        run_docker_tests "backend-test-unit" "Unit Tests in Docker"
        ;;
    "integration")
        run_docker_tests "backend-test-integration" "Integration Tests in Docker"
        ;;
    "ocr")
        test_ocr_in_docker
        ;;
    "all")
        echo "Running all Docker test suites..."
        
        run_docker_tests "backend-test-unit" "Unit Tests in Docker"
        run_docker_tests "backend-test-integration" "Integration Tests in Docker"
        test_ocr_in_docker
        ;;
    *)
        echo "Usage: $0 {unit|integration|ocr|all}"
        echo ""
        echo "Test types:"
        echo "  unit        - Run unit tests in Docker (OCR mocked)"
        echo "  integration - Run integration tests in Docker (with Tesseract)"
        echo "  ocr         - Run OCR-specific tests in Docker"
        echo "  all         - Run all test suites in Docker"
        exit 1
        ;;
esac

# Cleanup
if [ "$CLEANUP" = true ]; then
    echo ""
    echo "=== Cleaning up Docker resources ==="
    cd "$BACKEND_DIR"
    docker-compose -f docker-compose.test.yml down -v
    
    # Remove unused test images
    docker image prune -f --filter label=stage=test 2>/dev/null || true
fi

echo ""
echo "✅ Docker OCR testing completed"
