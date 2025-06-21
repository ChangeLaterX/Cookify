# Auth Test Suite

This directory contains comprehensive tests for the Authentication functionality in the Cookify backend application.

## Structure

```
tests/auth/
├── __init__.py              # Package initialization and exports
├── config.py                # Test configuration and base classes
├── run_tests.py             # Test runner script
├── README.md                # This file
├── unit/                    # Unit tests
│   ├── test_service_initialization.py    # Service setup tests
│   ├── test_user_registration.py         # Registration tests  
│   ├── test_user_authentication.py       # Authentication tests
│   ├── test_error_handling.py            # Error handling tests
│   └── test_complete_workflow.py         # End-to-end workflow tests
├── integration/             # Integration tests  
│   ├── __init__.py
│   └── test_real_auth.py    # Tests with real Supabase
├── fixtures/                # Test data and fixtures
│   └── test_data.py         # Sample test data
└── utils/                   # Testing utilities
    ├── __init__.py
    ├── mocks.py             # Mock factories and context managers
    └── test_data.py         # Test data generators
```

## Running Tests

### Using the Test Runner

The recommended way to run tests is using the included test runner:

```bash
# Run all auth tests
python tests/auth/run_tests.py --all

# Run only unit tests
python tests/auth/run_tests.py --unit

# Run only integration tests (requires Supabase credentials)
python tests/auth/run_tests.py --integration

# Run with coverage report
python tests/auth/run_tests.py --all --coverage

# Run with verbose output
python tests/auth/run_tests.py --unit --verbose
```

### Using pytest directly

You can also run tests directly with pytest:

```bash
# Run all auth tests
pytest tests/auth/

# Run specific test file
pytest tests/auth/unit/test_user_registration.py

# Run with coverage
pytest tests/auth/ --cov=domains.auth --cov-report=html
```

## Test Types

### Unit Tests

Located in `tests/auth/unit/`, these tests use mocks and don't require external dependencies:

- **Service Initialization** (`test_service_initialization.py`): Tests AuthService setup, dependency injection, and configuration
- **User Registration** (`test_user_registration.py`): Tests user registration logic, validation, and error handling  
- **User Authentication** (`test_user_authentication.py`): Tests login, logout, and token management
- **Error Handling** (`test_error_handling.py`): Tests error scenarios and exception handling
- **Complete Workflows** (`test_complete_workflow.py`): Tests end-to-end authentication flows

### Integration Tests

Located in `tests/auth/integration/`, these tests require real Supabase credentials:

- **Real Auth** (`test_real_auth.py`): Tests with actual Supabase instance
- **Performance Tests**: Load and performance testing

## Configuration

### Environment Variables

Set these environment variables for different test modes:

```bash
# Enable integration tests (requires Supabase credentials)
export AUTH_TEST_INTEGRATION=true

# Test Supabase credentials (for integration tests)
export TEST_SUPABASE_URL="your-test-supabase-url"
export TEST_SUPABASE_ANON_KEY="your-test-supabase-anon-key"

# Enable email testing (if you have test email setup)
export AUTH_TEST_EMAIL=true
export AUTH_TEST_EMAIL_DOMAIN="test.yourapp.com"

# Enable rate limiting tests
export AUTH_TEST_RATE_LIMITING=true

# Force mock mode (default: true)
export AUTH_TEST_MOCK_MODE=true
```

### Test Configuration

The `AuthTestConfig` class in `config.py` provides centralized configuration:

```python
from tests.auth.config import AuthTestConfig

config = AuthTestConfig()
print(f"Supabase available: {config.SUPABASE_AVAILABLE}")
print(f"Integration mode: {config.INTEGRATION_MODE}")
```

## Test Utilities

### Mock Factories

The `AuthMockFactory` class provides factories for creating test data:

```python
from tests.auth.utils.mocks import AuthMockFactory

# Create mock user data
user_response = AuthMockFactory.create_user_response()
token_response = AuthMockFactory.create_token_response()
supabase_response = AuthMockFactory.create_supabase_response()
```

### Test Data Generators

The `TestDataGenerator` class generates realistic test data:

```python
from tests.auth.utils.test_data import TestDataGenerator

# Generate test user
user_data = TestDataGenerator.generate_user_data()
print(f"Email: {user_data.email}")
print(f"Password: {user_data.password}")

# Generate bulk test users
users = TestDataGenerator.generate_bulk_users(count=10)
```

### Mock Context Managers

Use `MockContextManager` to easily mock dependencies:

```python
from tests.auth.utils.mocks import MockContextManager

with MockContextManager(success_responses=True) as mock_ctx:
    service = AuthService()
    # service.supabase is now mocked
```

Or use the decorator:

```python
from tests.auth.utils.mocks import with_mocked_auth

@with_mocked_auth(success=True)
def test_my_function():
    service = AuthService()
    # Supabase is mocked
```

## Writing New Tests

### Unit Test Template

```python
import pytest
from tests.auth.config import AuthTestBase
from tests.auth.utils.mocks import MockContextManager
from tests.auth.utils.test_data import TestDataGenerator

class TestMyFeature(AuthTestBase):
    """Test my auth feature."""

    def test_main_functionality(self):
        """Required by AuthTestBase."""
        self.test_my_specific_feature()

    @pytest.mark.asyncio
    async def test_my_specific_feature(self):
        """Test specific feature."""
        with MockContextManager(success_responses=True):
            service = AuthService()
            user_data = TestDataGenerator.generate_user_data()
            
            # Your test logic here
            result = await service.my_method(user_data)
            
            assert result is not None
```

### Integration Test Template

```python
import pytest
from tests.auth.config import AuthTestBase, AuthTestConfig

@pytest.mark.skipif(
    not AuthTestConfig.INTEGRATION_MODE,
    reason="Integration tests disabled"
)
class TestMyIntegration(AuthTestBase):
    """Integration test for my feature."""

    def test_main_functionality(self):
        """Required by AuthTestBase."""
        pass

    @pytest.mark.asyncio
    async def test_with_real_supabase(self):
        """Test with real Supabase."""
        service = AuthService()
        # Test with real service
```

## Best Practices

1. **Use the test runner** (`run_tests.py`) for consistent test execution
2. **Mock external dependencies** in unit tests using `MockContextManager`
3. **Generate unique test data** using `TestDataGenerator` to avoid conflicts
4. **Test error scenarios** explicitly with appropriate mock responses
5. **Use descriptive test names** that explain what is being tested
6. **Group related tests** in logical test classes
7. **Include performance tests** for critical paths
8. **Test edge cases** like rate limiting, network errors, etc.

## Troubleshooting

### Common Issues

1. **Import errors**: Make sure you're running tests from the project root
2. **Missing dependencies**: Install test dependencies with `pip install pytest pytest-asyncio pytest-cov`
3. **Supabase errors in integration tests**: Check your test environment credentials
4. **Rate limiting in tests**: Use appropriate delays or mocking

### Debug Mode

Run tests in debug mode with verbose output:

```bash
python tests/auth/run_tests.py --unit --verbose
```

### Coverage Reports

Generate detailed coverage reports:

```bash
python tests/auth/run_tests.py --all --coverage
# Open htmlcov/auth/index.html in browser
```

## Contributing

When adding new auth functionality:

1. Add unit tests for core logic
2. Add integration tests for external dependencies  
3. Update test data generators if needed
4. Add error handling tests
5. Update this README if adding new test categories

## Related Documentation

- [Auth API Documentation](../../../docs/auth-api.md)
- [Main Auth Module](../../../domains/auth/)
- [OCR Test Suite](../ocr/) (similar structure reference)
