# Auth Module GitHub Actions Setup

## Overview

This setup provides comprehensive automated testing for the Auth module across different scenarios and environments.

## Workflows Created

### 1. `auth-tests.yml` - Core Auth Testing
**Triggers**: Push/PR to auth-related files, manual dispatch
**Jobs**:
- **Unit Tests**: Fast tests with mocking, coverage reporting
- **Integration Tests**: Database + Redis integration
- **Security Tests**: Bandit, Safety, security-focused test scenarios
- **Performance Tests**: Benchmark tests with pytest-benchmark
- **Summary**: Aggregates results and posts PR comments

### 2. `auth-e2e-tests.yml` - End-to-End Testing
**Triggers**: Push to main, PR to main, scheduled daily, manual dispatch
**Jobs**:
- **E2E Tests**: Full system testing with scenarios
- **Load Tests**: Locust-based performance testing (scheduled/manual only)
- **Security Scan**: Deep security analysis with multiple tools

### 3. `auth-pr-validation.yml` - Pull Request Validation
**Triggers**: PR to main/develop with auth changes
**Jobs**:
- **Code Quality**: Black, isort, flake8, mypy checks
- **Security**: Bandit, Safety vulnerability scanning
- **Fast Tests**: Unit tests for quick feedback
- **Integration Preview**: Optional integration tests (with label)

## Test Categories

### Unit Tests (`pytest -m unit`)
- Fast execution (< 5 seconds each)
- No external dependencies
- High coverage requirements (80%+)
- Mocked external services

### Integration Tests (`pytest -m integration`)
- Database integration
- Redis caching
- Real service interactions
- Slower but comprehensive

### End-to-End Tests (`pytest -m e2e`)
- Full system scenarios
- User registration flows
- Authentication workflows
- Token management cycles

### Security Tests (`pytest -m security`)
- Input validation
- SQL injection protection
- JWT security
- Rate limiting verification

### Performance Tests (`pytest -m benchmark`)
- Response time benchmarks
- Throughput measurements
- Memory usage tracking
- Performance regression detection

## Usage Examples

### Local Development
```bash
# Run all auth tests
python backend/tests/auth/run_tests.py all --coverage

# Run specific test type
python backend/tests/auth/run_tests.py unit --verbose
python backend/tests/auth/run_tests.py integration
python backend/tests/auth/run_tests.py security
python backend/tests/auth/run_tests.py performance

# Run load tests
python backend/tests/auth/run_tests.py load --users 50 --run-time 120s
```

### GitHub Actions
```bash
# Trigger specific test level
gh workflow run auth-tests.yml -f test_level=security

# Trigger load tests
gh workflow run auth-e2e-tests.yml

# Check PR validation
# Automatically runs on PR creation/updates
```

## Environment Variables

### Required for CI
- `JWT_SECRET_KEY`: JWT signing secret
- `DATABASE_URL`: Database connection string
- `REDIS_URL`: Redis connection string

### Optional Configuration
- `AUTH_MAX_LOGIN_TIME_MS`: Performance threshold (default: 100)
- `AUTH_MAX_TOKEN_VALIDATION_TIME_MS`: Performance threshold (default: 50)
- `AUTH_MIN_THROUGHPUT_LOGIN_PER_SEC`: Throughput threshold (default: 20)
- `RATE_LIMITING_ENABLED`: Enable rate limiting tests (default: true)

## Artifacts and Reports

### Generated Artifacts
- **Test Results**: JUnit XML files for test reporting
- **Coverage Reports**: HTML and XML coverage reports
- **Performance Metrics**: JSON benchmark results
- **Security Reports**: Bandit and Safety scan results
- **Load Test Data**: CSV files with performance metrics

### Coverage Requirements
- **Unit Tests**: 90%+ line coverage
- **Integration Tests**: 80%+ line coverage
- **Combined**: 85%+ overall coverage

## Performance Thresholds

### Response Time Targets
- Login: < 100ms average
- Token validation: < 50ms average
- Registration: < 200ms average
- Password operations: < 150ms average

### Throughput Targets
- Login operations: > 20 req/sec
- Token validation: > 100 req/sec
- Registration: > 10 req/sec

## Security Checks

### Automated Scans
- **Bandit**: Python security linter
- **Safety**: Dependency vulnerability scanner
- **Semgrep**: Advanced security pattern detection

### Security Test Scenarios
- SQL injection attempts
- XSS prevention
- JWT manipulation tests
- Rate limiting verification
- Input validation edge cases

## Notifications

### PR Comments
- Test result summaries
- Coverage reports
- Performance metrics
- Security scan results

### Artifact Uploads
- Test reports for debugging
- Coverage data for analysis
- Performance baselines
- Security scan details

## Maintenance

### Regular Tasks
- Update performance thresholds based on infrastructure changes
- Review security scan results
- Monitor test execution times
- Update dependency versions

### Troubleshooting
- Check artifact uploads for detailed error logs
- Review environment variable configuration
- Verify service dependencies (Redis, Database)
- Monitor rate limiting in test environments
