#!/bin/bash

# OCR Performance Test Configuration Examples
# This file shows recommended configurations for different environments

echo "Available OCR Performance Test Configurations:"
echo "=============================================="

configure_development() {
    echo "Configuration for development environment (local, fast hardware)..."
    export TEST_ENVIRONMENT=development
    export OCR_TEST_MAX_AVG_LATENCY_MS=25000          # 25 seconds
    export OCR_TEST_MAX_LATENCY_STD_DEV_MS=8000       # 8 seconds
    export OCR_TEST_MAX_THROUGHPUT_TIME_S=90          # 1.5 minutes
    export OCR_TEST_MAX_E2E_AVG_MS=35000              # 35 seconds
    export OCR_TEST_MAX_E2E_MAX_MS=50000              # 50 seconds
    export OCR_TEST_MAX_SCALABILITY_MS=40000          # 40 seconds
    export OCR_TEST_MAX_MEMORY_GROWTH_MB=150          # 150MB
    export OCR_TEST_MIN_THROUGHPUT_TPS=0.08           # 0.08 tasks/sec
    
    echo "✓ Development environment configured"
}

configure_ci_cd() {
    echo "Configuration for CI/CD Pipeline (GitHub Actions, etc.)..."
    export TEST_ENVIRONMENT=ci
    export OCR_TEST_MAX_AVG_LATENCY_MS=45000          # 45 seconds
    export OCR_TEST_MAX_LATENCY_STD_DEV_MS=12000      # 12 seconds
    export OCR_TEST_MAX_THROUGHPUT_TIME_S=150         # 2.5 minutes
    export OCR_TEST_MAX_E2E_AVG_MS=60000              # 60 seconds
    export OCR_TEST_MAX_E2E_MAX_MS=90000              # 90 seconds
    export OCR_TEST_MAX_SCALABILITY_MS=70000          # 70 seconds
    export OCR_TEST_MAX_MEMORY_GROWTH_MB=250          # 250MB
    export OCR_TEST_MIN_THROUGHPUT_TPS=0.04           # 0.04 tasks/sec
    
    echo "✓ CI/CD Environment configured"
}

configure_staging() {
    echo "Configuration for staging environment (production-like)..."
    export TEST_ENVIRONMENT=staging
    export OCR_TEST_MAX_AVG_LATENCY_MS=50000          # 50 seconds
    export OCR_TEST_MAX_LATENCY_STD_DEV_MS=15000      # 15 seconds
    export OCR_TEST_MAX_THROUGHPUT_TIME_S=180         # 3 minutes
    export OCR_TEST_MAX_E2E_AVG_MS=75000              # 75 seconds
    export OCR_TEST_MAX_E2E_MAX_MS=120000             # 2 minutes
    export OCR_TEST_MAX_SCALABILITY_MS=90000          # 90 seconds
    export OCR_TEST_MAX_MEMORY_GROWTH_MB=300          # 300MB
    export OCR_TEST_MIN_THROUGHPUT_TPS=0.03           # 0.03 tasks/sec
    
    echo "✓ Staging environment configured"
}

configure_production() {
    echo "Configuration for production environment (conservative values)..."
    export TEST_ENVIRONMENT=production
    export OCR_TEST_MAX_AVG_LATENCY_MS=60000          # 60 seconds (1 minute)
    export OCR_TEST_MAX_LATENCY_STD_DEV_MS=20000      # 20 seconds
    export OCR_TEST_MAX_THROUGHPUT_TIME_S=240         # 4 minutes
    export OCR_TEST_MAX_E2E_AVG_MS=90000              # 90 seconds
    export OCR_TEST_MAX_E2E_MAX_MS=150000             # 2.5 minutes
    export OCR_TEST_MAX_SCALABILITY_MS=120000         # 2 minutes
    export OCR_TEST_MAX_MEMORY_GROWTH_MB=500          # 500MB
    export OCR_TEST_MIN_THROUGHPUT_TPS=0.02           # 0.02 tasks/sec
    
    echo "✓ Production environment configured"
}

configure_debug() {
    echo "Configuration for debugging (very generous values)..."
    export TEST_ENVIRONMENT=debug
    export OCR_TEST_MAX_AVG_LATENCY_MS=120000         # 2 minutes
    export OCR_TEST_MAX_LATENCY_STD_DEV_MS=30000      # 30 seconds
    export OCR_TEST_MAX_THROUGHPUT_TIME_S=300         # 5 minutes
    export OCR_TEST_MAX_E2E_AVG_MS=180000             # 3 minutes
    export OCR_TEST_MAX_E2E_MAX_MS=300000             # 5 minutes
    export OCR_TEST_MAX_SCALABILITY_MS=240000         # 4 minutes
    export OCR_TEST_MAX_MEMORY_GROWTH_MB=1000         # 1GB
    export OCR_TEST_MIN_THROUGHPUT_TPS=0.01           # 0.01 tasks/sec
    
    echo "✓ Debug environment configured"
}

show_current_config() {
    echo "Current Performance Test Configuration:"
    echo "========================================"
    echo "TEST_ENVIRONMENT: ${TEST_ENVIRONMENT:-'default'}"
    echo "OCR_TEST_MAX_AVG_LATENCY_MS: ${OCR_TEST_MAX_AVG_LATENCY_MS:-'30000 (default)'}"
    echo "OCR_TEST_MAX_E2E_AVG_MS: ${OCR_TEST_MAX_E2E_AVG_MS:-'45000 (default)'}"
    echo "OCR_TEST_MAX_E2E_MAX_MS: ${OCR_TEST_MAX_E2E_MAX_MS:-'60000 (default)'}"
    echo "OCR_TEST_MAX_MEMORY_GROWTH_MB: ${OCR_TEST_MAX_MEMORY_GROWTH_MB:-'200 (default)'}"
    echo "OCR_TEST_MIN_THROUGHPUT_TPS: ${OCR_TEST_MIN_THROUGHPUT_TPS:-'0.05 (default)'}"
}

# Main function
case "${1:-help}" in
    "development" | "dev")
        configure_development
        ;;
    "ci" | "ci-cd")
        configure_ci_cd
        ;;
    "staging")
        configure_staging
        ;;
    "production" | "prod")
        configure_production
        ;;
    "debug")
        configure_debug
        ;;
    "show" | "current")
        show_current_config
        ;;
    "help" | *)
        echo "Usage: $0 [ENVIRONMENT]"
        echo ""
        echo "Available environments:"
        echo "  development  - Local development (fast hardware)"
        echo "  ci           - CI/CD Pipeline"
        echo "  staging      - Staging environment"
        echo "  production   - Production environment"
        echo "  debug        - Debugging (generous timeouts)"
        echo "  show         - Show current configuration"
        echo ""
        echo "Examples:"
        echo "  $0 development"
        echo "  $0 production"
        echo "  $0 show"
        echo ""
        echo "After setting a configuration, run the tests:"
        echo "  pytest backend/tests/ocr/integration/test_performance.py -v"
        ;;
esac
