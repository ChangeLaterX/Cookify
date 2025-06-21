# CI/CD Integration for OCR Testing

This document describes the CI/CD setup for ensuring OCR tests work correctly across different environments.

## Overview

The OCR testing system is designed to handle varying environments gracefully:
- **Development**: Full OCR testing with Tesseract
- **CI/CD**: Intelligent fallback to mocked tests when Tesseract is unavailable
- **Docker**: Containerized testing with Tesseract pre-installed

## Test Categories

### Unit Tests (`ocr_unit`)
- **Dependencies**: None (fully mocked)
- **CI Safe**: ✅ Always run
- **Purpose**: Test logic without external dependencies

### Integration Tests (`ocr_integration`)
- **Dependencies**: Tesseract OCR
- **CI Safe**: ⚠️ Conditional (skipped if Tesseract unavailable)
- **Purpose**: Test real OCR functionality

### Performance Tests (`ocr_performance`)
- **Dependencies**: Tesseract OCR
- **CI Safe**: ⚠️ Conditional with relaxed thresholds
- **Purpose**: Ensure OCR performance meets requirements

## Environment Detection

The system automatically detects the environment and configures tests accordingly:

```python
# Automatic environment detection
is_ci = OCRTestConfig.is_ci_environment()
tesseract_available = OCRTestConfig().TESSERACT_AVAILABLE
should_run_integration = OCRTestConfig.should_run_integration_tests()
```

### Environment Variables

| Variable | Purpose | Default | CI Override |
|----------|---------|---------|-------------|
| `OCR_TEST_MOCK_MODE` | Force mocked OCR | `true` | `false` if Tesseract available |
| `OCR_TEST_INTEGRATION` | Enable integration tests | `false` | `true` if Tesseract available |
| `TEST_ENVIRONMENT` | Environment type | `development` | `ci` |
| `OCR_TEST_MAX_AVG_LATENCY_MS` | Performance threshold | `30000` | `60000` (relaxed) |
| `OCR_TEST_MAX_E2E_AVG_MS` | E2E performance | `45000` | `90000` (relaxed) |

## GitHub Actions Integration

### Main CI Pipeline (`.github/workflows/ci.yml`)

```yaml
strategy:
  matrix:
    test-mode: [unit, integration]
    include:
      - test-mode: unit
        tesseract: false
      - test-mode: integration
        tesseract: true
```

**Features:**
- Matrix builds for different test modes
- Conditional Tesseract installation
- Automatic test categorization
- Performance threshold adjustment for CI

### OCR-Specific Pipeline (`.github/workflows/ocr-tests.yml`)

```yaml
strategy:
  matrix:
    test-type: [unit, integration, performance]
```

**Features:**
- Dedicated OCR testing workflow
- Triggered by OCR-related file changes
- Manual workflow dispatch with test type selection
- Docker-based testing validation

## Docker Integration

### Test Containers

Three specialized containers for different test scenarios:

1. **backend-test-unit**: OCR mocked, fast execution
2. **backend-test-integration**: Full Tesseract, real OCR testing
3. **backend-test**: Configurable via environment variables

### Docker Compose Configuration

```yaml
services:
  backend-test-integration:
    environment:
      - OCR_TEST_MOCK_MODE=false
      - OCR_TEST_INTEGRATION=true
      - OCR_TEST_MAX_AVG_LATENCY_MS=90000  # Relaxed for containers
```

## Test Execution Scripts

### CI Test Runner (`scripts/run-ci-tests.sh`)

Intelligent test execution with automatic fallbacks:

```bash
# Run all appropriate tests
./scripts/run-ci-tests.sh all

# Run specific test categories
./scripts/run-ci-tests.sh unit
./scripts/run-ci-tests.sh ocr-unit
./scripts/run-ci-tests.sh ocr-integration  # Only if Tesseract available
```

### Docker Test Runner (`scripts/run-docker-tests.sh`)

Containerized testing for consistency:

```bash
# Test in Docker environment
./scripts/run-docker-tests.sh all
./scripts/run-docker-tests.sh ocr
```

## Pytest Markers

Tests are properly marked for selective execution:

| Marker | Description | CI Behavior |
|--------|-------------|-------------|
| `unit` | Unit tests | Always run |
| `integration` | Integration tests | Conditional |
| `ocr` | All OCR tests | Mixed |
| `ocr_unit` | OCR unit tests | Always run |
| `ocr_integration` | OCR integration tests | Conditional |
| `requires_tesseract` | Needs Tesseract | Skip if unavailable |
| `ci_safe` | Safe for CI | Always run |

## Performance Thresholds

CI environments use relaxed performance thresholds:

| Metric | Development | CI Environment |
|--------|-------------|----------------|
| Average Latency | 30s | 60s |
| E2E Processing | 45s | 90s |
| Memory Growth | 100MB | 300MB |
| Min Throughput | 0.1 tps | 0.02 tps |

## Troubleshooting

### Common CI Issues

1. **Tesseract Installation Failed**
   ```yaml
   - name: Install Tesseract OCR
     run: |
       sudo apt-get update
       sudo apt-get install -y tesseract-ocr libtesseract-dev
   ```

2. **Tests Timing Out**
   - Check performance thresholds in environment variables
   - Verify CI-specific configuration is applied

3. **Docker Build Issues**
   ```bash
   # Test Docker build locally
   docker build -t test-ocr .
   docker run --rm test-ocr tesseract --version
   ```

### Test Debugging

```bash
# Check Tesseract availability
python -c "from tests.ocr.config import OCRTestConfig; print(OCRTestConfig.get_tesseract_info())"

# Run with verbose output
pytest tests/ocr/ -v -s --tb=long

# Run only safe tests
pytest tests/ocr/ -m "ci_safe"
```

## Best Practices

### 1. Test Design
- Always provide mocked alternatives for integration tests
- Use appropriate markers for test categorization
- Design tests to be environment-aware

### 2. CI Configuration
- Install Tesseract conditionally based on test requirements
- Use matrix builds to test different scenarios
- Set appropriate timeouts and thresholds

### 3. Error Handling
- Gracefully handle missing dependencies
- Provide clear skip reasons
- Log environment context for debugging

### 4. Performance
- Use relaxed thresholds in CI environments
- Cache dependencies when possible
- Optimize test execution order

## Migration Guide

### From Manual Testing
1. Add pytest markers to existing tests
2. Configure environment variables
3. Update CI pipeline configuration

### Adding New OCR Tests
1. Choose appropriate markers (`ocr_unit` vs `ocr_integration`)
2. Use `OCRTestConfig.should_skip_ocr_tests()` for conditional skipping
3. Provide mocked alternatives when possible

## Monitoring and Metrics

### Test Results
- JUnit XML reports for CI integration
- Coverage reports with codecov integration
- Performance metrics tracking

### Environment Health
- Tesseract version and language availability
- Performance threshold compliance
- Test execution time trends
