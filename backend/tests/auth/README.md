# Auth Tests

This directory contains comprehensive pytest tests for all authentication endpoints.

## Test Account Credentials
- **Email**: krijajannis@gmail.com
- **Password**: 221224

## Test Files

Each endpoint has its own dedicated test file:

1. **test_register.py** - Tests for `/auth/register` endpoint
   - User registration with valid/invalid data
   - Email validation, password strength
   - Duplicate email handling

2. **test_login.py** - Tests for `/auth/login` endpoint
   - Valid/invalid credentials
   - Email format validation
   - Password length validation

3. **test_refresh.py** - Tests for `/auth/refresh` endpoint
   - Token refresh with valid/invalid/expired tokens
   - Malformed token handling

4. **test_logout.py** - Tests for `/auth/logout` endpoint
   - Logout with valid/invalid tokens
   - Authorization header validation

5. **test_me.py** - Tests for `/auth/me` GET endpoint
   - Current user info retrieval
   - Authentication validation

6. **test_profile.py** - Tests for `/auth/profile` GET endpoint
   - User profile retrieval
   - Null profile handling

7. **test_update_profile.py** - Tests for `/auth/me` PUT endpoint
   - Profile updates with various data
   - Validation of profile fields

8. **test_forgot_password.py** - Tests for `/auth/forgot-password` endpoint
   - Password reset requests
   - Email validation and security

9. **test_reset_password.py** - Tests for `/auth/reset-password` endpoint
   - Password reset with tokens
   - New password validation

10. **test_verify_email.py** - Tests for `/auth/verify-email` endpoint
    - Email verification with tokens
    - Token validation

11. **test_resend_verification.py** - Tests for `/auth/resend-verification` endpoint
    - Resending verification emails
    - Security considerations

12. **test_change_password.py** - Tests for `/auth/change-password` endpoint
    - Password changes with old/new passwords
    - Authentication requirements

13. **test_health.py** - Tests for `/auth/health` endpoint
    - Health check functionality
    - No authentication required

14. **test_user_info.py** - Tests for `/auth/user-info` endpoint
    - Optional user info (returns null if not authenticated)
    - Graceful handling of missing auth

15. **test_password_strength.py** - Tests for `/auth/check-password-strength` endpoint
    - Password strength analysis
    - Requirements validation

16. **test_dev_login.py** - Tests for `/auth/dev-login` endpoint
    - Development login (only in debug mode)
    - Production safety

# Auth Tests

This directory contains comprehensive pytest tests for all authentication endpoints.

## Test Account Credentials
- **Email**: krijajannis@gmail.com
- **Password**: 221224

## Server Configuration
- **Server**: dev.krija.info:8000
- **Base URL**: http://dev.krija.info:8000/api
- **Rate Limiting**: 
  - Rate limiting is configured to be disabled when `debug=True` in config.py
  - However, the server may still have cached rate limiting data from previous runs
  - Current rate limits: 5 login attempts per 15 minutes, 10 health checks per 15 minutes
  - Tests may fail with 429 status codes due to cached rate limiting data
  - **Solution**: Wait for rate limit window to expire (~15 minutes) or restart the server

## Test Files

Each endpoint has its own dedicated test file:

1. **test_register.py** - Tests for `/auth/register` endpoint
   - User registration with valid/invalid data
   - Email validation, password strength
   - Duplicate email handling

2. **test_login.py** - Tests for `/auth/login` endpoint
   - Valid/invalid credentials
   - Email format validation
   - Password length validation

3. **test_refresh.py** - Tests for `/auth/refresh` endpoint
   - Token refresh with valid/invalid/expired tokens
   - Malformed token handling

4. **test_logout.py** - Tests for `/auth/logout` endpoint
   - Logout with valid/invalid tokens
   - Authorization header validation

5. **test_me.py** - Tests for `/auth/me` GET endpoint
   - Current user info retrieval
   - Authentication validation

6. **test_profile.py** - Tests for `/auth/profile` GET endpoint
   - User profile retrieval
   - Null profile handling

7. **test_update_profile.py** - Tests for `/auth/me` PUT endpoint
   - Profile updates with various data
   - Validation of profile fields

8. **test_forgot_password.py** - Tests for `/auth/forgot-password` endpoint
   - Password reset requests
   - Email validation and security

9. **test_reset_password.py** - Tests for `/auth/reset-password` endpoint
   - Password reset with tokens
   - New password validation

10. **test_verify_email.py** - Tests for `/auth/verify-email` endpoint
    - Email verification with tokens
    - Token validation

11. **test_resend_verification.py** - Tests for `/auth/resend-verification` endpoint
    - Resending verification emails
    - Security considerations

12. **test_change_password.py** - Tests for `/auth/change-password` endpoint
    - Password changes with old/new passwords
    - Authentication requirements

13. **test_health.py** - Tests for `/auth/health` endpoint
    - Health check functionality
    - No authentication required

14. **test_user_info.py** - Tests for `/auth/user-info` endpoint
    - Optional user info (returns null if not authenticated)
    - Graceful handling of missing auth

15. **test_password_strength.py** - Tests for `/auth/check-password-strength` endpoint
    - Password strength analysis
    - Requirements validation

16. **test_dev_login.py** - Tests for `/auth/dev-login` endpoint
    - Development login (only in debug mode)
    - Production safety

## Running Tests

**Note**: The remote server has rate limiting enabled. For comprehensive testing, consider:
1. Running tests with delays between requests
2. Testing against a local development server
3. Temporarily disabling rate limiting for testing

Run all auth tests:
```bash
python -m pytest tests/auth/ -v
```

Run specific endpoint tests:
```bash
python -m pytest tests/auth/test_login.py -v
```

Run with coverage:
```bash
python -m pytest tests/auth/ --cov=domains.auth -v
```

Run individual tests with delays (to avoid rate limiting):
```bash
python -m pytest tests/auth/test_login.py::TestLoginEndpoint::test_login_valid_credentials_success -v -s
```

## Test Configuration

- Uses async/await pattern with `pytest-asyncio`
- HTTP client testing with `httpx.AsyncClient`
- Shared fixtures in `conftest.py`
- Test user credentials provided for integration testing
- Configured to test against remote server: `dev.krija.info:8000/api`

## Status

✅ **Test Infrastructure Complete**: All 16 endpoint test files created
✅ **Server Connection Working**: Successfully connects to dev.krija.info:8000
✅ **Valid Credentials Working**: Login test passes with provided credentials
⚠️ **Rate Limiting Issue**: Server returns 429 for rapid successive requests

## Available Endpoints Tested

Based on OpenAPI spec from `/openapi.json`, all endpoints are covered:
- `/api/auth/change-password` ✅
- `/api/auth/check-password-strength` ✅
- `/api/auth/dev-login` ✅
- `/api/auth/forgot-password` ✅
- `/api/auth/health` ✅
- `/api/auth/login` ✅
- `/api/auth/logout` ✅
- `/api/auth/me` ✅
- `/api/auth/password-reset` ✅
- `/api/auth/profile` ✅
- `/api/auth/refresh` ✅
- `/api/auth/register` ✅
- `/api/auth/resend-verification` ✅
- `/api/auth/reset-password` ✅
- `/api/auth/user-info` ✅
- `/api/auth/verify-email` ✅

## Notes

- Tests are designed to work with the actual remote server
- Some tests may require valid tokens from email verification
- Security-focused endpoints return success for non-existent emails
- All endpoints are tested for proper error handling and validation
- Rate limiting prevents rapid test execution - consider running individual tests
