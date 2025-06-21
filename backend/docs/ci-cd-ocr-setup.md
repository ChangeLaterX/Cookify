# CI/CD OCR Integration

This setup ensures OCR tests work reliably across different CI/CD environments.

## Quick Start

1. **Validate Setup**:
   ```bash
   cd backend && ./scripts/validate-ci-setup.sh
   ```

2. **Run Tests Locally**:
   ```bash
   # Unit tests (always work)
   ./scripts/run-ci-tests.sh unit
   
   # OCR tests (with fallback)
   ./scripts/run-ci-tests.sh ocr
   
   # All tests
   ./scripts/run-ci-tests.sh all
   ```

3. **Test in Docker**:
   ```bash
   ./scripts/run-docker-tests.sh ocr
   ```

## How It Works

- **Automatic Detection**: Tests automatically detect if Tesseract is available
- **Intelligent Fallback**: Falls back to mocked tests when OCR is unavailable
- **Environment Aware**: Adjusts performance thresholds for CI environments
- **Proper Marking**: Tests are marked for selective execution

## Test Categories

| Category | Dependencies | Always Runs | Purpose |
|----------|-------------|-------------|---------|
| `unit` | None | ✅ | Logic testing with mocks |
| `integration` | Tesseract | ⚠️ | Real OCR functionality |
| `ocr_unit` | None | ✅ | OCR logic without real OCR |
| `ocr_integration` | Tesseract | ⚠️ | Real OCR testing |

## CI/CD Workflows

- **`.github/workflows/ci.yml`**: Main CI pipeline with matrix testing
- **`.github/workflows/ocr-tests.yml`**: Dedicated OCR testing workflow

## Environment Variables

| Variable | Purpose | CI Default |
|----------|---------|------------|
| `OCR_TEST_MOCK_MODE` | Force mocking | `false` if Tesseract available |
| `OCR_TEST_INTEGRATION` | Enable integration tests | `true` if Tesseract available |
| `TEST_ENVIRONMENT` | Environment type | `ci` |

## Documentation

See `docs/ci-cd-ocr-integration.md` for complete documentation.

## Troubleshooting

1. **Tests failing in CI**: Check if Tesseract is installed in the CI environment
2. **Timeouts**: Adjust performance thresholds via environment variables
3. **Docker issues**: Ensure Docker has enough resources allocated

## Support

The setup gracefully handles missing dependencies and provides clear skip reasons for any disabled tests.
