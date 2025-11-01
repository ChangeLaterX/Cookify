# Ingredients Test Suite

A comprehensive testing framework for the Cookify ingredients module, providing unit tests, integration tests, mocking utilities, and test data generation.

## 📁 Directory Structure

```
tests/ingredients/
├── __init__.py                     # Test module initialization
├── config.py                      # Test configuration and base classes
├── run_tests.py                   # Test runner script
├── README.md                      # This documentation
├── fixtures/                      # Test fixtures and sample data
│   ├── __init__.py
│   └── sample_data.py            # Realistic ingredient sample data
├── unit/                          # Unit tests
│   ├── test_ingredient_operations.py   # CRUD operations
│   ├── test_search_functionality.py    # Search and filtering
│   ├── test_data_validation.py        # Schema validation
│   ├── test_error_handling.py         # Error scenarios
│   └── test_complete_workflow.py      # End-to-end workflows
├── integration/                   # Integration tests
│   └── test_ingredients_service.py    # Service integration tests
└── utils/                         # Testing utilities
    ├── __init__.py
    ├── mocks.py                   # Mock factories and utilities
    └── test_data.py              # Test data generators
```

## 🚀 Quick Start

### Run All Tests

```bash
cd backend/tests/ingredients
python run_tests.py
```

### Run Specific Test Types

```bash
# Unit tests only
python run_tests.py --unit

# Integration tests only
python run_tests.py --integration

# Specific test file
python run_tests.py --test unit/test_ingredient_operations.py

# Performance tests
python run_tests.py --performance
```

### Generate Test Reports

```bash
# Generate comprehensive report with coverage
python run_tests.py --report

# Validate test environment
python run_tests.py --validate

# List available tests
python run_tests.py --list
```

## 🧪 Test Categories

### Unit Tests

**test_ingredient_operations.py**

- CRUD operations (Create, Read, Update, Delete)
- Service method testing with mocks
- Data transformation validation
- Business logic verification

**test_search_functionality.py**

- Text search capabilities
- Filtering and sorting
- Pagination handling
- Case sensitivity and partial matches

**test_data_validation.py**

- Pydantic schema validation
- Field constraints and types
- Required field validation
- Edge case handling

**test_error_handling.py**

- Database connection errors
- Network timeout scenarios
- Invalid input handling
- Service layer error propagation

**test_complete_workflow.py**

- End-to-end user workflows
- Multi-step operations
- State management
- Data consistency checks

### Integration Tests

**test_ingredients_service.py**

- Real Supabase database interactions
- Service integration testing
- Concurrent operation handling
- Performance under load
- Data consistency across operations

## 🛠 Testing Utilities

### Mock System (`utils/mocks.py`)

**IngredientsMockFactory**

```python
# Create mock ingredients
mock_ingredient = IngredientsMockFactory.create_ingredient()

# Mock service responses
mock_response = IngredientsMockFactory.create_ingredient_response()

# Mock database operations
mock_db = IngredientsMockFactory.create_supabase_mock()
```

**MockContextManager**

```python
# Automated mock setup and teardown
async with MockContextManager() as mock_ctx:
    mock_service = mock_ctx.mock_service
    # Your test code here
```

### Test Data Generation (`utils/test_data.py`)

**TestDataGenerator**

```python
# Generate realistic ingredient data
ingredient_data = TestDataGenerator.generate_ingredient_create()

# Generate by category
veggie_data = TestDataGenerator.generate_ingredient_create(category="vegetables")

# Generate with custom nutritional profile
high_protein = TestDataGenerator.generate_ingredient_create(
    proteins_per_100g=30.0,
    name="High Protein Food"
)
```

**TestScenarios**

```python
# Pre-defined test scenarios
scenarios = TestScenarios.create_workflow_scenarios()
validation_tests = TestScenarios.validation_scenarios()
performance_tests = TestScenarios.performance_scenarios()
```

### Sample Data (`fixtures/sample_data.py`)

**Realistic Ingredient Database**

- 20+ realistic ingredients across categories
- Accurate nutritional information
- Real-world pricing data
- Category-based organization

**Test Scenarios**

- High protein ingredients
- Low calorie options
- Budget-friendly choices
- Vegetarian selections
- Invalid data for validation testing

## ⚙️ Configuration

### Environment Variables

```bash
# Test Configuration
INGREDIENTS_TEST_ENV=testing
INGREDIENTS_RUN_INTEGRATION_TESTS=true
INGREDIENTS_GENERATE_COVERAGE=true
INGREDIENTS_MOCK_EXTERNAL_APIS=true

# Database Configuration (for integration tests)
SUPABASE_URL=your_test_supabase_url
SUPABASE_KEY=your_test_supabase_key
```

### Test Configuration (`config.py`)

**IngredientsTestConfig**

- Centralized test settings
- Environment-specific configurations
- Feature flag management
- Database connection settings

**IngredientsTestBase**

- Abstract base class for all tests
- Common setup and teardown
- Shared assertion methods
- Standard test structure

## 📊 Coverage and Reporting

### Coverage Reports

The test suite generates comprehensive coverage reports:

```bash
# HTML Coverage Report
htmlcov/ingredients/index.html

# XML Coverage (for CI/CD)
test-results/ingredients-coverage.xml

# Terminal Coverage
python run_tests.py --unit --verbose
```

### Test Reports

```bash
# JUnit XML (for CI/CD)
test-results/ingredients-results.xml

# HTML Test Report
test-results/ingredients-report.html
```

## 🔧 Advanced Usage

### Custom Test Data

```python
from tests.ingredients.utils.test_data import TestDataGenerator

# Custom ingredient with specific constraints
custom_ingredient = TestDataGenerator.generate_ingredient_create(
    name="Custom Test Ingredient",
    calories_per_100g=150.0,
    proteins_per_100g=20.0,
    category="custom"
)
```

### Mock Service Integration

```python
from tests.ingredients.utils.mocks import IngredientsMockFactory

# Mock service with specific behavior
mock_service = IngredientsMockFactory.create_service_mock()
mock_service.create_ingredient.return_value = mock_ingredient

# Test your code with the mock
result = await your_function_using_service(mock_service)
```

### Performance Testing

```python
@pytest.mark.performance
async def test_bulk_operations_performance():
    """Test performance with large datasets."""
    # Your performance test code
```

## 🐛 Debugging Tests

### Verbose Output

```bash
python run_tests.py --verbose
```

### Specific Test Debugging

```bash
# Run single test with full output
python run_tests.py --test unit/test_ingredient_operations.py::TestIngredientOperations::test_create_ingredient -v
```

### Mock Debugging

```python
# Enable mock call tracking
mock_service = IngredientsMockFactory.create_service_mock()
mock_service.create_ingredient.assert_called_once_with(expected_data)
```

## 🔄 CI/CD Integration

### GitHub Actions Example

```yaml
- name: Run Ingredients Tests
  run: |
    cd backend/tests/ingredients
    python run_tests.py --report

- name: Upload Coverage
  uses: codecov/codecov-action@v4
  with:
    file: test-results/ingredients-coverage.xml
```

### Test Quality Gates

- Minimum 90% code coverage
- All unit tests must pass
- Integration tests must pass (if enabled)
- No critical errors in static analysis

## 📚 Best Practices

### Writing New Tests

1. **Follow the AAA Pattern**: Arrange, Act, Assert
2. **Use Descriptive Names**: `test_create_ingredient_with_valid_data_succeeds`
3. **Test One Thing**: Each test should verify a single behavior
4. **Use Fixtures**: Leverage sample data and mocks
5. **Document Complex Tests**: Add docstrings for complex scenarios

### Mock Usage Guidelines

1. **Mock External Dependencies**: Database, network calls, file I/O
2. **Keep Mocks Simple**: Mock the interface, not the implementation
3. **Verify Mock Interactions**: Use `assert_called_with()` appropriately
4. **Reset Mocks**: Use `MockContextManager` for automatic cleanup

### Test Data Management

1. **Use Realistic Data**: Base on actual ingredient nutritional values
2. **Create Diverse Scenarios**: Test edge cases and normal operations
3. **Parameterize Tests**: Use `@pytest.mark.parametrize` for multiple scenarios
4. **Clean Up Test Data**: Ensure integration tests clean up after themselves

## 🤝 Contributing

### Adding New Tests

1. Identify the functionality to test
2. Choose appropriate test category (unit/integration)
3. Use existing utilities and patterns
4. Follow naming conventions
5. Add documentation for complex scenarios

### Extending Test Utilities

1. Add new mock classes to `utils/mocks.py`
2. Extend `TestDataGenerator` for new data types
3. Create new scenarios in `TestScenarios`
4. Update documentation

### Reporting Issues

1. Include test output and error messages
2. Specify environment details
3. Provide steps to reproduce
4. Suggest potential solutions

## 📖 Related Documentation

- [Ingredients API Documentation](../../../docs/ingredients-api.md)
- [Domain Architecture](../../../domains/ingredients/README.md)
- [General Testing Guide](../../README.md)
- [Database Schema](../../../shared/database/README.md)
