# Ingredients Test Suite Architecture

## 🏗 System Architecture Overview

The ingredients test suite follows a layered architecture that mirrors the production code structure while providing comprehensive testing capabilities through mocking, data generation, and realistic test scenarios.

```
┌─────────────────────────────────────────────────────────────┐
│                     Test Runner Layer                       │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │   run_tests.py  │  │  Test Reports   │  │   Coverage      │ │
│  │                 │  │                 │  │   Analysis      │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
└─────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────┐
│                      Test Layer                             │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │   Unit Tests    │  │ Integration     │  │   Fixtures      │ │
│  │                 │  │    Tests        │  │                 │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
└─────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────┐
│                    Utilities Layer                          │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │   Mock System   │  │  Data Generator │  │  Test Config    │ │
│  │                 │  │                 │  │                 │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
└─────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────┐
│                 Production System Under Test                │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │ Ingredients     │  │ Ingredients     │  │   Database      │ │
│  │   Service       │  │   Schemas       │  │   (Supabase)    │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## 🧩 Component Architecture

### Test Configuration (`config.py`)

**IngredientsTestConfig**

- Environment variable management
- Feature flag configuration
- Database connection settings
- Test execution parameters

**IngredientsTestBase**

- Abstract base class for all test classes
- Common setup and teardown methods
- Shared assertion utilities
- Standard test structure enforcement

```python
class IngredientsTestBase(ABC):
    """Base class providing common test infrastructure."""

    @abstractmethod
    def test_main_functionality(self):
        """Required test method for basic functionality verification."""
        pass

    def setup_method(self):
        """Common setup for all test methods."""
        pass

    def teardown_method(self):
        """Common cleanup for all test methods."""
        pass
```

### Mock System (`utils/mocks.py`)

**IngredientsMockFactory**

- Factory pattern for creating consistent mocks
- Realistic data generation for different scenarios
- Configurable success/failure responses
- Database operation simulation

**MockContextManager**

- Automatic mock setup and cleanup
- Context management for test isolation
- Resource management and disposal
- State tracking and verification

**Specialized Mocks**

- `MockIngredientDatabase`: Simulates database operations
- `MockSupabaseClient`: Mocks Supabase interactions
- `MockSearchEngine`: Simulates search functionality
- `MockValidationService`: Handles validation scenarios

```python
class IngredientsMockFactory:
    """Factory for creating ingredient-related mocks."""

    @staticmethod
    def create_ingredient(**overrides) -> Dict[str, Any]:
        """Create mock ingredient with optional field overrides."""

    @staticmethod
    def create_service_mock() -> Mock:
        """Create fully configured service mock."""

    @staticmethod
    def create_supabase_mock() -> Mock:
        """Create Supabase client mock with method chaining."""
```

### Test Data Generation (`utils/test_data.py`)

**TestDataGenerator**

- Realistic ingredient data creation
- Category-based generation (vegetables, meats, etc.)
- Nutritional value calculation
- Price modeling based on real-world data

**TestIngredientData**

- Data class for structured ingredient representation
- Validation and constraint checking
- Conversion utilities for different formats
- Nutritional analysis helpers

**TestScenarios**

- Pre-defined test scenarios for common use cases
- Workflow scenario generation
- Edge case and error scenario creation
- Performance testing data sets

```python
class TestDataGenerator:
    """Generates realistic test data for ingredients."""

    @classmethod
    def generate_ingredient_create(cls, **kwargs) -> IngredientMasterCreate:
        """Generate realistic ingredient creation data."""

    @classmethod
    def generate_by_category(cls, category: str) -> IngredientMasterCreate:
        """Generate ingredient data for specific category."""

    @classmethod
    def generate_batch(cls, count: int) -> List[IngredientMasterCreate]:
        """Generate multiple ingredients for bulk testing."""
```

## 🔧 Testing Patterns

### Unit Testing Pattern

```python
class TestIngredientOperations(IngredientsTestBase):
    """Unit tests following standard pattern."""

    def test_main_functionality(self):
        """Required base class implementation."""
        self.test_create_ingredient_success()

    @patch('domains.ingredients.services.supabase_client')
    def test_create_ingredient_success(self, mock_supabase):
        """Test successful ingredient creation."""
        # Arrange
        mock_data = TestDataGenerator.generate_ingredient_create()
        mock_response = IngredientsMockFactory.create_ingredient_response()
        mock_supabase.table().insert().execute.return_value = mock_response

        # Act
        service = IngredientsService()
        result = await service.create_ingredient(mock_data)

        # Assert
        assert result.name == mock_data.name
        mock_supabase.table().insert.assert_called_once()
```

### Integration Testing Pattern

```python
class TestIngredientsIntegration(IngredientsTestBase):
    """Integration tests with real database."""

    async def setup_service(self):
        """Set up real service with test database."""
        self.service = IngredientsService()
        self.cleanup_queue = []

    async def test_full_lifecycle(self):
        """Test complete ingredient lifecycle."""
        # Create -> Read -> Update -> Delete
        created = await self.service.create_ingredient(test_data)
        retrieved = await self.service.get_ingredient(created.id)
        updated = await self.service.update_ingredient(created.id, update_data)
        await self.service.delete_ingredient(created.id)
```

### Mock Testing Pattern

```python
def test_with_mock_context(self):
    """Test using mock context manager."""
    async with MockContextManager() as mock_ctx:
        # Mock is automatically configured and cleaned up
        result = await mock_ctx.service.create_ingredient(test_data)

        # Verify mock interactions
        mock_ctx.verify_create_called_once()
        assert result.name == test_data.name
```

## 📊 Data Flow Architecture

### Test Data Flow

```
Sample Data (fixtures) → TestDataGenerator → Test Cases
                                ↓
Mock Factories ← Test Utilities ← Test Configuration
                                ↓
Service Layer ← Mock System ← Unit Tests
                                ↓
Database ← Integration Tests ← Real Services
```

### Mock Data Flow

```
TestDataGenerator → Mock Factory → Mock Objects → Test Cases
                                        ↓
                    Mock Responses ← Mock Behavior Configuration
                                        ↓
                    Test Assertions ← Mock Verification
```

## 🔄 Test Execution Flow

### Unit Test Execution

1. **Setup Phase**

   - Load test configuration
   - Initialize mock objects
   - Prepare test data

2. **Execution Phase**

   - Run test methods with mocks
   - Capture interactions and results
   - Handle async operations

3. **Verification Phase**

   - Assert expected results
   - Verify mock interactions
   - Check side effects

4. **Cleanup Phase**
   - Reset mock states
   - Clear test data
   - Release resources

### Integration Test Execution

1. **Environment Setup**

   - Connect to test database
   - Initialize real services
   - Prepare test isolation

2. **Test Execution**

   - Run operations against real systems
   - Handle actual async operations
   - Manage test data lifecycle

3. **Verification**

   - Check database state
   - Verify data consistency
   - Validate business rules

4. **Cleanup**
   - Remove test data
   - Close connections
   - Reset environment state

## 🛡 Error Handling Architecture

### Mock Error Simulation

```python
class MockErrorSimulator:
    """Simulates various error conditions."""

    @staticmethod
    def database_connection_error():
        """Simulate database connection failure."""

    @staticmethod
    def validation_error():
        """Simulate data validation failure."""

    @staticmethod
    def timeout_error():
        """Simulate network timeout."""
```

### Error Propagation Testing

```
Service Layer Error → Test Capture → Assertion Verification
        ↓
Mock Layer Error → Error Simulation → Expected Error Types
        ↓
Database Error → Integration Test → Real Error Handling
```

## 📈 Performance Testing Architecture

### Load Testing Structure

```python
class PerformanceTestSuite:
    """Performance testing utilities."""

    async def test_concurrent_operations(self):
        """Test system under concurrent load."""

    async def test_bulk_operations(self):
        """Test bulk data operations."""

    async def test_memory_usage(self):
        """Monitor memory usage patterns."""
```

### Performance Metrics Collection

- Response time measurement
- Memory usage tracking
- Database query analysis
- Concurrent operation handling
- Resource utilization monitoring

## 🔧 Configuration Management

### Environment-Based Configuration

```python
class TestEnvironmentConfig:
    """Environment-specific test configuration."""

    DEVELOPMENT = {
        "database": "test_dev_db",
        "mock_external": True,
        "coverage_required": 80
    }

    CI_CD = {
        "database": "test_ci_db",
        "mock_external": True,
        "coverage_required": 90
    }
```

### Feature Flag Management

- Mock vs. real service selection
- Integration test enablement
- Coverage report generation
- Performance test execution
- Debug output control

## 🧪 Test Quality Assurance

### Code Coverage Strategy

- **Unit Tests**: 95%+ coverage requirement
- **Integration Tests**: Critical path coverage
- **End-to-End**: User workflow coverage
- **Error Handling**: Exception path coverage

### Test Quality Metrics

- Test execution time
- Mock verification completeness
- Data generation realism
- Error scenario coverage
- Documentation completeness

This architecture ensures comprehensive testing while maintaining performance, reliability, and maintainability of the ingredients module test suite.
