# Cookify API Documentation

Welcome to the Cookify API documentation. This document provides an overview of all available API endpoints and their documentation.

## Overview

Cookify is a comprehensive meal planning application with a RESTful API built using FastAPI. The API provides endpoints for user authentication, ingredient management, recipe handling, and meal planning.

**Base URL:** `http://dev.krija.info:8000/api`

## API Domains

### 🔐 Authentication API
**Base Path:** `/api/auth`

Handles user authentication, registration, password management, and user profiles.

**Documentation:** [Auth API Documentation](./auth-api.md)

**Key Features:**
- User registration and login
- JWT-based authentication
- Password reset and email verification  
- User profile management
- Token refresh and session management

**Quick Links:**
- [Registration](./auth-api.md#user-registration)
- [Login](./auth-api.md#user-login)
- [Profile Management](./auth-api.md#get-user-profile)

### 🥗 Ingredients API
**Base Path:** `/api/ingredients`

Manages ingredient master data including nutritional information and pricing.

**Documentation:** [Ingredients API Documentation](./ingredients-api.md)

**Key Features:**
- Ingredient CRUD operations
- Search and filtering
- Nutritional data management
- Pagination support

**Endpoints:**
- `GET /api/ingredients/master` - List all ingredients
- `GET /api/ingredients/master/{ingredient_id}` - Get specific ingredient
- `POST /api/ingredients/master` - Create ingredient (auth required)
- `PUT /api/ingredients/master/{ingredient_id}` - Update ingredient (auth required)
- `DELETE /api/ingredients/master/{id}` - Delete ingredient (admin only)
- `GET /api/ingredients/search` - Search ingredients by name

### 📄 Receipt API
**Base Path:** `/api/receipt`

Handles receipt parsing and ingredient extraction (coming soon).

## Authentication

Most write operations require authentication using JWT Bearer tokens.

### Getting a Token

```bash
curl -X POST "http://dev.krija.info:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password123"
  }'
```

### Using the Token

```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://dev.krija.info:8000/api/auth/me"
```

## Error Handling

All APIs use consistent error response format:

```json
{
  "detail": {
    "error": "Human readable error message",
    "error_code": "MACHINE_READABLE_CODE"
  }
}
```

### Common HTTP Status Codes

- `200` - Success
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `409` - Conflict
- `422` - Validation Error
- `429` - Rate Limited
- `500` - Internal Server Error

## Rate Limiting

The API implements rate limiting to prevent abuse:

- **Authentication endpoints:** 5 requests per 15 minutes
- **General endpoints:** 100 requests per minute per user
- **Search endpoints:** 50 requests per minute

## Pagination

List endpoints support pagination using query parameters:

- `limit` - Number of items per page (default: 10, max: 100)
- `offset` - Number of items to skip (default: 0)

Example:
```
GET /api/ingredients/master?limit=20&offset=40
```

Response includes pagination metadata:
```json
{
  "data": {
    "ingredients": [...],
    "total": 150,
    "limit": 20,
    "offset": 40
  }
}
```

## Interactive Documentation

The API provides interactive documentation powered by Swagger/OpenAPI:

- **Swagger UI:** <http://dev.krija.info:8000/docs>
- **ReDoc:** <http://dev.krija.info:8000/redoc>
- **OpenAPI Schema:** <http://dev.krija.info:8000/openapi.json>

## Health Check

Check API health status:

```bash
curl http://dev.krija.info:8000/health
```

Response:
```json
{
  "status": "healthy",
  "app": "Cookify Meal Planning API",
  "version": "0.1.0",
  "endpoints": {
    "auth": "/api/auth",
    "ingredients": "/api/ingredients",
    "docs": "/docs",
    "redoc": "/redoc"
  }
}
```

## Development Setup

### Prerequisites

- Python 3.10+
- Supabase account and project
- Environment variables configured

### Running the API

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### Environment Variables

```bash
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_service_key
JWT_SECRET_KEY=your_jwt_secret
ENVIRONMENT=development
```

## SDKs and Client Libraries

### JavaScript/TypeScript

```typescript
// Example client setup
class CookifyAPI {
  private baseURL = 'http://dev.krija.info:8000/api';
  private token: string | null = null;

  async login(email: string, password: string) {
    const response = await fetch(`${this.baseURL}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    });
    
    const data = await response.json();
    if (data.success) {
      this.token = data.data.access_token;
      return data.data;
    }
    throw new Error(data.detail.error);
  }

  async getIngredients(limit = 10, offset = 0) {
    const response = await fetch(
      `${this.baseURL}/ingredients/master?limit=${limit}&offset=${offset}`
    );
    return response.json();
  }

  async searchIngredients(query: string, limit = 10) {
    const response = await fetch(
      `${this.baseURL}/ingredients/search?q=${encodeURIComponent(query)}&limit=${limit}`
    );
    return response.json();
  }

  private async authenticatedRequest(url: string, options: RequestInit = {}) {
    return fetch(url, {
      ...options,
      headers: {
        ...options.headers,
        'Authorization': `Bearer ${this.token}`
      }
    });
  }
}
```

### Python

```python
import requests
from typing import Optional, Dict, Any

class CookifyAPI:
    def __init__(self, base_url: str = "http://dev.krija.info:8000/api"):
        self.base_url = base_url
        self.token: Optional[str] = None

    def login(self, email: str, password: str) -> Dict[str, Any]:
        response = requests.post(f"{self.base_url}/auth/login", json={
            "email": email,
            "password": password
        })
        
        data = response.json()
        if data.get("success"):
            self.token = data["data"]["access_token"]
            return data["data"]
        
        raise Exception(data["detail"]["error"])

    def get_ingredients(self, limit: int = 10, offset: int = 0) -> Dict[str, Any]:
        response = requests.get(
            f"{self.base_url}/ingredients/master",
            params={"limit": limit, "offset": offset}
        )
        return response.json()

    def search_ingredients(self, query: str, limit: int = 10) -> Dict[str, Any]:
        response = requests.get(
            f"{self.base_url}/ingredients/search",
            params={"q": query, "limit": limit}
        )
        return response.json()

    def _authenticated_request(self, method: str, url: str, **kwargs) -> requests.Response:
        headers = kwargs.pop("headers", {})
        headers["Authorization"] = f"Bearer {self.token}"
        return requests.request(method, url, headers=headers, **kwargs)
```

## Testing

### Running Tests

```bash
cd backend
pytest tests/ -v
```

### Test Coverage

The API includes comprehensive test coverage:

- Unit tests for all service functions
- Integration tests for all endpoints
- Schema validation tests
- Error handling tests

### Example Test

```python
def test_ingredient_creation():
    client = TestClient(app)
    
    # Login first
    login_response = client.post("/api/auth/login", json={
        "email": "test@example.com",
        "password": "password123"
    })
    token = login_response.json()["data"]["access_token"]
    
    # Create ingredient
    response = client.post(
        "/api/ingredients/master",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "Test Ingredient",
            "calories_per_100g": 100.0,
            "proteins_per_100g": 10.0,
            "fat_per_100g": 5.0,
            "carbs_per_100g": 15.0,
            "price_per_100g_cents": 200
        }
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["success"] is True
    assert data["data"]["name"] == "Test Ingredient"
```

## Contributing

### API Design Guidelines

1. **RESTful Design:** Follow REST principles
2. **Consistent Responses:** Use standard response format
3. **Error Handling:** Provide meaningful error messages
4. **Documentation:** Document all endpoints
5. **Testing:** Write comprehensive tests
6. **Security:** Implement proper authentication and validation

### Adding New Endpoints

1. Create service functions in `domains/{domain}/services.py`
2. Define schemas in `domains/{domain}/schemas.py`
3. Implement routes in `domains/{domain}/routes.py`
4. Add tests in `tests/test_{domain}.py`
5. Update documentation

## Changelog

### v0.1.0 (Current)

- ✅ Authentication API (complete)
- ✅ Ingredients API (complete)
- 🚧 Receipt API (in development)
- 📋 Recipe API (planned)
- 📋 Meal Planning API (planned)
- 📋 Shopping List API (planned)

## Support

For questions, issues, or contributions:

- 📧 Email: dev@cookify.app
- 🐛 Issues: GitHub Issues
- 💬 Discussions: GitHub Discussions
- 📖 Documentation: This repository

---

**Happy Cooking! 🍳**
