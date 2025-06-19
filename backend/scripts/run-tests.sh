#!/bin/bash

# Comprehensive Test Runner for Cookify Backend
# Runs all backend tests with various options

set -e

echo "🧪 Cookify Backend Test Runner"
echo "============================="

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() { echo -e "${BLUE}[INFO]${NC} $1"; }
print_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
print_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Navigate to backend directory
cd "$(dirname "$0")/.."

# Parse command line arguments
COVERAGE=false
VERBOSE=false
FAST=false
DOMAIN=""
PERFORMANCE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -c|--coverage)
            COVERAGE=true
            shift
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -f|--fast)
            FAST=true
            shift
            ;;
        -d|--domain)
            DOMAIN="$2"
            shift 2
            ;;
        -p|--performance)
            PERFORMANCE=true
            shift
            ;;
        -h|--help)
            echo "Usage: $0 [OPTIONS]"
            echo "Options:"
            echo "  -c, --coverage     Run tests with coverage report"
            echo "  -v, --verbose      Verbose output"
            echo "  -f, --fast         Skip slow tests"
            echo "  -d, --domain       Run tests for specific domain only"
            echo "  -p, --performance  Run performance tests"
            echo "  -h, --help         Show this help message"
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Activate virtual environment
if [ -d "venv" ]; then
    print_status "Activating Virtual Environment..."
    source venv/bin/activate
else
    print_warning "No Virtual Environment found. Using system Python."
fi

# Check if pytest is available
if ! command -v pytest &> /dev/null; then
    print_error "pytest is not installed. Run './scripts/setup-backend-dev.sh'."
    exit 1
fi

# Build pytest command
PYTEST_CMD="python -m pytest"

if [ "$VERBOSE" = true ]; then
    PYTEST_CMD="$PYTEST_CMD -v"
fi

if [ "$FAST" = true ]; then
    PYTEST_CMD="$PYTEST_CMD -m 'not slow'"
    print_status "Skipping slow tests..."
fi

if [ "$COVERAGE" = true ]; then
    PYTEST_CMD="$PYTEST_CMD --cov=. --cov-report=html --cov-report=term-missing"
    print_status "Enabling Coverage Reporting..."
fi

if [ -n "$DOMAIN" ]; then
    PYTEST_CMD="$PYTEST_CMD tests/$DOMAIN/"
    print_status "Running tests for domain '$DOMAIN'..."
else
    PYTEST_CMD="$PYTEST_CMD tests/"
    print_status "Running all tests..."
fi

# Run linting first
print_status "Running code quality checks..."

# Flake8 linting
if command -v flake8 &> /dev/null; then
    print_status "Running flake8 linting..."
    flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics || print_warning "Linting warnings found"
fi

# Black formatting check
if command -v black &> /dev/null; then
    print_status "Checking code formatting with black..."
    black --check . || print_warning "Code formatting not consistent. Run 'black .' to fix."
fi

# Import sorting check
if command -v isort &> /dev/null; then
    print_status "Checking import sorting..."
    isort --check-only . || print_warning "Import sorting not consistent. Run 'isort .' to fix."
fi

# Run unit tests
print_status "Starting Unit Tests..."
echo "Kommando: $PYTEST_CMD"
$PYTEST_CMD

# Run performance tests if requested
if [ "$PERFORMANCE" = true ]; then
    print_status "Running Performance Tests..."
    
    # Source performance test configuration
    if [ -f "scripts/configure_performance_tests.sh" ]; then
        source scripts/configure_performance_tests.sh
        configure_development
    fi
    
    python -m pytest tests/ -m "performance" -v || print_warning "Performance Tests failed"
fi

# Generate coverage report if requested
if [ "$COVERAGE" = true ]; then
    print_status "Generating Coverage Report..."
    if [ -d "htmlcov" ]; then
        print_success "Coverage Report generated: htmlcov/index.html"
        
        # Open coverage report in browser if available
        if command -v xdg-open &> /dev/null; then
            xdg-open htmlcov/index.html
        elif command -v open &> /dev/null; then
            open htmlcov/index.html
        fi
    fi
fi

# Test summary
echo ""
print_success "🎉 Test execution completed!"

if [ "$COVERAGE" = true ]; then
    echo "📊 Coverage Report: htmlcov/index.html"
fi

echo ""
echo "Additional test options:"
echo "./scripts/run-tests.sh --help           # Show all options"
echo "./scripts/run-tests.sh --coverage       # With Coverage"
echo "./scripts/run-tests.sh --domain auth    # Auth tests only"
echo "./scripts/run-tests.sh --performance    # Performance tests"
echo "./scripts/run-tests.sh --fast           # Fast tests only"
