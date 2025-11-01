# Cookify API Endpoint Reference

Quick reference for all Cookify API endpoints organized by domain.

## Authentication Endpoints (`/api/auth`)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `POST` | `/auth/register` | Register new user | No |
| `POST` | `/auth/login` | User login | No |
| `POST` | `/auth/refresh` | Refresh token | No |
| `POST` | `/auth/logout` | User logout | Yes |
| `GET` | `/auth/me` | Get current user | Yes |
| `GET` | `/auth/profile` | Get user profile | Yes |
| `PUT` | `/auth/me` | Update user profile | Yes |
| `POST` | `/auth/forgot-password` | Request password reset | No |
| `POST` | `/auth/reset-password` | Confirm password reset | No |
| `POST` | `/auth/verify-email` | Verify email address | No |
| `POST` | `/auth/resend-verification` | Resend verification email | No |
| `POST` | `/auth/change-password` | Change password | Yes |
| `GET` | `/auth/user-info` | Get user info (optional auth) | Optional |
| `POST` | `/auth/dev-login` | Development test login | No |
| `POST` | `/auth/check-password-strength` | Check password strength | Optional |

## Pantry Management Endpoints (`/api/pantry`)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `GET` | `/pantry/items` | List user's pantry items | Yes |
| `GET` | `/pantry/items/{item_id}` | Get pantry item by ID | Yes |
| `POST` | `/pantry/items` | Create new pantry item | Yes |
| `PUT` | `/pantry/items/{item_id}` | Update pantry item | Yes |
| `DELETE` | `/pantry/items/{item_id}` | Delete pantry item | Yes |
| `POST` | `/pantry/items/bulk` | Bulk create pantry items | Yes |
| `PUT` | `/pantry/items/bulk` | Bulk update pantry items | Yes |
| `DELETE` | `/pantry/items/bulk` | Bulk delete pantry items | Yes |
| `GET` | `/pantry/stats` | Get pantry statistics | Yes |
| `GET` | `/pantry/categories` | Get category statistics | Yes |
| `GET` | `/pantry/expiring` | Get expiry report | Yes |
| `GET` | `/pantry/low-stock` | Get low stock report | Yes |

## Health Monitoring Endpoints (`/api/health`)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `GET` | `/health` | Comprehensive health check | No |
| `GET` | `/health/quick` | Quick health check | No |
| `GET` | `/health/live` | Liveness probe | No |
| `GET` | `/health/ready` | Readiness probe | No |
| `GET` | `/health/metrics` | Health metrics | No |
| `GET` | `/health/alerts` | Health alerts | No |
| `GET` | `/health/service/{service_name}/history` | Service health history | No |

## Ingredients Management Endpoints (`/api/ingredients`)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `GET` | `/ingredients/master` | List all ingredients | No |
| `GET` | `/ingredients/master/{ingredient_id}` | Get ingredient by ID | No |
| `POST` | `/ingredients/master` | Create new ingredient | Yes |
| `PUT` | `/ingredients/master/{ingredient_id}` | Update ingredient | Yes |
| `DELETE` | `/ingredients/master/{ingredient_id}` | Delete ingredient (Admin) | Yes |
| `GET` | `/ingredients/search` | Search ingredients | No |

## OCR Processing Endpoints (`/api/ocr`)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `POST` | `/ocr/extract-text` | Extract text from receipt | No |
| `POST` | `/ocr/process` | Process receipt with suggestions | No |

## Cache Management Endpoints (`/api/update`)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `POST` | `/update/ingredient_cache` | Update ingredient cache | No |
| `GET` | `/update/ingredient_cache/status` | Get cache status | No |
| `POST` | `/update/all_caches` | Force refresh all caches | No |

## Query Parameters Reference

### Pantry Items (`/api/pantry/items`)
- `page`: Page number (default: 1, min: 1)
- `per_page`: Items per page (default: 50, min: 1, max: 100)
- `category`: Filter by category
- `search`: Search in item names

### Ingredients (`/api/ingredients/master`)
- `limit`: Maximum results (default: 50, min: 1, max: 100)
- `offset`: Skip results (default: 0, min: 0)

### Ingredient Search (`/api/ingredients/search`)
- `q`: Search query (required, min: 1, max: 255 chars)
- `limit`: Maximum results (default: 20, min: 1, max: 100)
- `offset`: Skip results (default: 0, min: 0)

### Health Alerts (`/api/health/alerts`)
- `hours`: Hours to look back (default: 1, min: 1, max: 168)

### Low Stock Report (`/api/pantry/low-stock`)
- `threshold`: Quantity threshold (default: 1.0, min: 0, max: 10)

### Cache Update (`/api/update/ingredient_cache`)
- `force`: Force update (default: false)

## HTTP Status Codes

| Code | Meaning | When Used |
|------|---------|-----------|
| `200` | OK | Successful request |
| `201` | Created | Resource created successfully |
| `204` | No Content | Successful request without content |
| `400` | Bad Request | Invalid request data |
| `401` | Unauthorized | Authentication required |
| `403` | Forbidden | Access denied |
| `404` | Not Found | Resource not found |
| `409` | Conflict | Resource already exists |
| `422` | Unprocessable Entity | Validation error |
| `429` | Too Many Requests | Rate limit exceeded |
| `500` | Internal Server Error | Server error |
| `503` | Service Unavailable | Service temporarily unavailable |

## Rate Limits

| Endpoint Group | Limit | Scope |
|----------------|-------|-------|
| Authentication | 10 requests/minute | Per IP |
| OCR Processing | 20 requests/hour | Per authenticated user |
| Other endpoints | Standard limits | Per user |

## Required Headers

### All Authenticated Requests
```http
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

### OCR File Upload
```http
Authorization: Bearer <jwt_token>
Content-Type: multipart/form-data
```

## Common Error Codes

| Error Code | Description |
|------------|-------------|
| `VALIDATION_ERROR` | Input data invalid |
| `AUTHENTICATION_REQUIRED` | Authentication required |
| `INVALID_TOKEN` | JWT token invalid or expired |
| `INSUFFICIENT_PERMISSIONS` | Insufficient permissions |
| `RESOURCE_NOT_FOUND` | Requested resource not found |
| `DUPLICATE_RESOURCE` | Resource already exists |
| `RATE_LIMIT_EXCEEDED` | Rate limit exceeded |
| `INTERNAL_ERROR` | Internal server error |
| `SERVICE_UNAVAILABLE` | Service temporarily unavailable |

## Quick Examples

### Get Bearer Token
```bash
# Login and extract token
TOKEN=$(curl -s -X POST "https://api.cookify.app/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"password"}' \
  | jq -r '.data.access_token')
```

### Basic CRUD Operations
```bash
# Create item
curl -X POST "https://api.cookify.app/api/pantry/items" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"Milk","quantity":1,"unit":"liter","category":"dairy"}'

# Read items
curl -X GET "https://api.cookify.app/api/pantry/items" \
  -H "Authorization: Bearer $TOKEN"

# Update item
curl -X PUT "https://api.cookify.app/api/pantry/items/ITEM_ID" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"quantity":2}'

# Delete item
curl -X DELETE "https://api.cookify.app/api/pantry/items/ITEM_ID" \
  -H "Authorization: Bearer $TOKEN"
```

For detailed documentation, see [API_Documentation.md](./API_Documentation.md)
