# Pantry Items Tests

This directory contains comprehensive tests for the Pantry Items domain, covering bulk operations, statistics, API endpoints, and data validation.

## Test Structure

### Unit Tests (`unit/`)

- **`test_bulk_operations.py`** - Tests for bulk create, update, and delete operations
- **`test_statistics.py`** - Tests for pantry statistics, expiry reports, category breakdown, and low stock analysis
- **`test_api_endpoints.py`** - Tests for HTTP API endpoints and request/response handling
- **`test_data_validation.py`** - Tests for input validation, schema validation, and error handling

### Configuration (`config.py`)

Contains base test configuration, mock utilities, and shared test fixtures for pantry tests.

### Utilities (`utils/`)

- **`test_data.py`** - Test data generators, mock factories, and common test scenarios

## Test Coverage

### Bulk Operations
- ✅ Bulk create (up to 50 items)
- ✅ Bulk update (up to 50 items) 
- ✅ Bulk delete (up to 50 items)
- ✅ Validation of bulk limits
- ✅ Partial success/failure scenarios
- ✅ Database error handling
- ✅ Performance testing

### Statistics & Analytics
- ✅ Pantry overview statistics
- ✅ Category breakdown and percentages
- ✅ Expiry reports (expiring soon, expired, fresh)
- ✅ Low stock reports with custom thresholds
- ✅ Empty pantry scenarios
- ✅ Edge cases and date calculations

### API Endpoints
- ✅ All bulk operation endpoints
- ✅ All statistics endpoints
- ✅ Authentication and authorization
- ✅ Request/response validation
- ✅ Error response handling
- ✅ CORS and rate limiting considerations

### Data Validation
- ✅ Schema validation for all models
- ✅ Field-level validation (names, quantities, units, etc.)
- ✅ Optional field handling
- ✅ Unicode and special character support
- ✅ Edge cases and boundary conditions
- ✅ Error message clarity

## Running Tests

### Run All Pantry Tests
```bash
# From backend directory
pytest tests/pantry/ -v
```

### Run Specific Test Categories
```bash
# Bulk operations only
pytest tests/pantry/unit/test_bulk_operations.py -v

# Statistics only
pytest tests/pantry/unit/test_statistics.py -v

# API endpoints only
pytest tests/pantry/unit/test_api_endpoints.py -v

# Data validation only
pytest tests/pantry/unit/test_data_validation.py -v
```

### Run with Coverage
```bash
pytest tests/pantry/ --cov=domains.pantry_items --cov-report=html
```

### Run Performance Tests Only
```bash
pytest tests/pantry/ -k "performance" -v
```

## Test Configuration

### Environment Variables

- `PANTRY_TEST_MOCK_MODE` - Enable/disable mock mode (default: true)
- `PANTRY_TEST_INTEGRATION` - Enable integration tests (default: false)
- `PANTRY_MAX_QUERY_TIME_MS` - Max query time threshold (default: 500ms)
- `PANTRY_MAX_BULK_TIME_MS` - Max bulk operation time threshold (default: 2000ms)

### Mock vs Real Database

Tests can run in two modes:

1. **Mock Mode** (default) - Uses mocked database responses for fast, isolated testing
2. **Integration Mode** - Uses real database connections for end-to-end testing

```bash
# Run with real database
PANTRY_TEST_MOCK_MODE=false pytest tests/pantry/
```

## Test Data

### Sample Data

The tests use realistic sample data including:

- Various food items (produce, dairy, bakery, spices)
- Different quantities and units
- Mixed expiry dates (fresh, expiring soon, expired)
- Categorized and uncategorized items

### Data Generators

Test data generators provide:
- Configurable item creation
- Bulk operation data sets
- Statistics mock data
- Edge case scenarios

## Key Test Scenarios

### Bulk Operations
1. **Happy Path**: All items processed successfully
2. **Partial Failure**: Some items fail validation or database constraints
3. **Limit Exceeded**: More than 50 items in one operation
4. **Database Errors**: Connection failures, constraint violations
5. **Performance**: Large batches complete within time limits

### Statistics
1. **Populated Pantry**: Various items across categories and expiry states
2. **Empty Pantry**: No items, all statistics should be zero/null
3. **Edge Cases**: Items expiring today, exactly at thresholds
4. **Custom Thresholds**: Low stock with different threshold values

### API Integration
1. **Authentication**: Valid tokens, unauthorized access
2. **Request Validation**: Malformed JSON, invalid parameters
3. **Response Format**: Consistent API response structure
4. **Error Handling**: Service errors mapped to HTTP status codes

### Data Validation
1. **Required Fields**: All mandatory fields validated
2. **Optional Fields**: Proper handling of null/missing values
3. **Type Validation**: Correct data types enforced
4. **Business Rules**: Quantities > 0, valid UUIDs, etc.
5. **Edge Cases**: Unicode, special characters, extreme values

## Performance Benchmarks

- Single item operations: < 100ms
- Bulk operations (50 items): < 2000ms
- Statistics queries: < 500ms
- API response times: < 200ms

## Mocking Strategy

Tests use comprehensive mocking for:

- **Supabase Client**: Database operations and responses
- **Authentication**: User authentication and authorization
- **External Services**: Any third-party service dependencies
- **Time-dependent Operations**: Fixed dates for consistent testing

## Error Testing

Comprehensive error scenario coverage:

- **Validation Errors**: Invalid input data
- **Not Found Errors**: Non-existent items or users
- **Database Errors**: Connection issues, constraint violations
- **Authorization Errors**: Insufficient permissions
- **Rate Limiting**: Too many requests (if implemented)

## Contributing

When adding new pantry functionality:

1. Add corresponding test methods to appropriate test files
2. Update test data generators if new data patterns are needed
3. Add new mock scenarios for complex operations
4. Update this README with new test coverage
5. Ensure tests follow the established patterns and naming conventions

## Integration with CI/CD

These tests are designed to run in CI/CD pipelines with:

- Fast execution in mock mode
- Comprehensive coverage reporting
- Clear error reporting and debugging information
- Parallel execution support
- Database setup/teardown automation
