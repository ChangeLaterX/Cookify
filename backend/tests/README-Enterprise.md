# 🧪 Enterprise Test Suite - Cookify Backend

> **Professional-grade testing infrastructure for medium-sized software companies**

## 📋 Overview

This repository implements a comprehensive, enterprise-ready test suite designed for professional software development teams. The architecture follows industry best practices and provides robust quality assurance for the Cookify backend application.

## 🏗️ Architecture

### Test Pipeline Structure

```
🔍 Code Quality → 🧪 Unit Tests → 🔗 Integration → 🚀 Performance → 🛡️ Security → 📊 Coverage → 🎯 Summary
```

### Job Matrix Strategy

- **Multi-Python Support**: Tests run on Python 3.11 and 3.12
- **Domain Isolation**: Parallel execution per domain (auth, ingredients, ocr)
- **Fail-Fast Logic**: Critical failures stop the pipeline early
- **Resource Optimization**: Intelligent caching and dependency management

## 🎯 Test Categories

### 🧪 Unit Tests

- **Speed**: < 100ms per test
- **Isolation**: No external dependencies
- **Coverage**: 90%+ target per domain
- **Parallel**: 4 workers per domain

### 🔗 Integration Tests

- **Database**: PostgreSQL test containers
- **APIs**: Full endpoint validation
- **Services**: External service mocking
- **Authentication**: Real JWT workflows

### 🚀 Performance Tests

- **Benchmarks**: Automated performance regression detection
- **Load Testing**: Concurrent user simulation
- **Memory Profiling**: Memory leak detection
- **SLA Validation**: Response time thresholds

### 🛡️ Security Tests

- **Static Analysis**: Bandit, Semgrep, Safety
- **Dependency Scanning**: Vulnerability detection
- **Code Quality**: Security-focused linting
- **Penetration Testing**: Automated security probes

## 🚀 Quick Start

### Local Development

```bash
# Run all tests
cd backend
python tests/run_tests.py --coverage --parallel

# Run specific domain
python tests/run_tests.py --domain auth --type unit

# Run with enterprise config
pytest -c tests/pytest-enterprise.ini
```

### CI/CD Integration

```bash
# Trigger specific test suite
gh workflow run "Backend Test Suite" --input test_suite=unit-only

# Performance testing
gh workflow run "Backend Test Suite" --input test_suite=performance-only

# Security audit
gh workflow run "Backend Test Suite" --input test_suite=security-only
```

## 📊 Quality Gates

### Coverage Thresholds

- **Unit Tests**: 90%+
- **Integration Tests**: 75%+
- **Overall Coverage**: 80%+

### Performance SLAs

- **API Response Time**: < 200ms (P95)
- **Health Endpoint**: < 50ms average
- **Database Queries**: < 100ms (P95)
- **OCR Processing**: < 30s per image

### Security Requirements

- **Zero High-Severity Vulnerabilities**
- **All Dependencies Scanned**
- **Static Analysis Passing**
- **No Hardcoded Secrets**

## 🎛️ Configuration

### Environment Variables

```bash
# Test Configuration
COVERAGE_THRESHOLD=80
PERFORMANCE_THRESHOLD_MS=5000
PYTEST_WORKERS=4

# Database
TEST_DATABASE_URL=postgresql://test_user:test_password@localhost:5432/test_db

# Security
SUPABASE_URL=${SUPABASE_URL}
SUPABASE_KEY=${SUPABASE_KEY}
JWT_SECRET=${JWT_SECRET}
```

### Test Markers

```python
# Domain markers
@pytest.mark.auth
@pytest.mark.ingredients
@pytest.mark.ocr

# Type markers
@pytest.mark.unit
@pytest.mark.integration
@pytest.mark.performance

# Quality markers
@pytest.mark.critical
@pytest.mark.security
@pytest.mark.ci_safe
```

## 📈 Reporting & Artifacts

### Generated Reports

- **Coverage Reports**: HTML + XML + Badge
- **Performance Benchmarks**: JSON + Histogram
- **Security Scans**: Bandit + Safety + Semgrep
- **Test Results**: JUnit XML + HTML + JSON

### Artifact Retention

- **Test Results**: 30 days
- **Coverage Reports**: 30 days
- **Security Scans**: 30 days
- **Performance Data**: 30 days

## 🔧 Advanced Usage

### Custom Test Runs

```bash
# Critical tests only
pytest -m "critical and not experimental"

# CI-safe performance tests
pytest -m "performance and ci_safe"

# Security audit
pytest -m "security or vulnerability"

# Smoke tests
pytest -m "smoke"
```

### Matrix Testing

```bash
# Test across Python versions
pytest --python-versions="3.11,3.12"

# Cross-platform testing (when configured)
pytest --platforms="ubuntu,windows,macos"
```

## 🎯 Test Development Guidelines

### 1. Test Naming Convention

```python
def test_[component]_[scenario]_[expected_result]():
    """
    Test description following enterprise standards.

    Given: Initial conditions
    When: Action taken
    Then: Expected outcome
    """
```

### 2. Test Structure (AAA Pattern)

```python
def test_user_login_with_valid_credentials_succeeds():
    # Arrange
    user = UserFactory.create()
    credentials = {"email": user.email, "password": "valid_password"}

    # Act
    response = client.post("/api/auth/login", json=credentials)

    # Assert
    assert response.status_code == 200
    assert "access_token" in response.json()
```

### 3. Fixture Usage

```python
@pytest.fixture
def authenticated_client(client, test_user):
    """Provide an authenticated test client."""
    token = generate_test_token(test_user)
    client.headers.update({"Authorization": f"Bearer {token}"})
    return client
```

## 🚨 Troubleshooting

### Common Issues

#### Test Timeouts

```bash
# Increase timeout for slow tests
pytest --timeout=300

# Run with less parallelism
pytest -n 2
```

#### Memory Issues

```bash
# Monitor memory usage
pytest --memray

# Run tests sequentially
pytest -n 0
```

#### Flaky Tests

```bash
# Run flaky tests multiple times
pytest --count=5 -m flaky

# Identify flaky tests
pytest --flaky-report
```

### Performance Optimization

```bash
# Profile test execution
pytest --profile

# Cache dependencies aggressively
export PIP_CACHE_DIR=/tmp/pip-cache

# Use faster database
export TEST_DATABASE_URL=sqlite:///test.db
```

## 🔗 Integration with Tools

### IDE Integration

- **VS Code**: `.vscode/settings.json` configured
- **PyCharm**: Run configurations included
- **Vim/Neovim**: Compatible with pytest plugins

### CI/CD Platforms

- **GitHub Actions**: Workflow included
- **GitLab CI**: Pipeline template available
- **Jenkins**: Jenkinsfile template available
- **Azure DevOps**: Pipeline YAML available

### Monitoring & Alerting

- **Test Results**: Automatic notification on failures
- **Coverage Trends**: Track coverage over time
- **Performance Regression**: Alert on performance degradation
- **Security Issues**: Immediate notification of vulnerabilities

## 📚 Resources

### Documentation

- [Pytest Official Docs](https://docs.pytest.org/)
- [Testing Best Practices](https://docs.python.org/3/library/unittest.html)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [SQLAlchemy Testing](https://docs.sqlalchemy.org/en/14/orm/session_api.html#sqlalchemy.orm.Session)
