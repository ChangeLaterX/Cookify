# Cookify API Quick Start Guide

## Getting Started

This guide will help you get started with the Cookify API quickly. Follow these steps to integrate with our pantry management system.

## Base URL

```
https://api.cookify.app/api
```

For local development:
```
http://localhost:8000/api
```

## Authentication Flow

### Step 1: Register a New User

```bash
curl -X POST "https://api.cookify.app/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "developer@example.com",
    "password": "SecurePassword123!",
    "username": "dev_user"
  }'
```

**Response:**
```json
{
  "success": true,
  "data": {
    "access_token": "eyJ...",
    "refresh_token": "eyJ...",
    "token_type": "bearer",
    "expires_in": 1800,
    "expires_at": "2025-06-29T12:30:00Z"
  },
  "message": "Registration successful"
}
```

### Step 2: Login (if already registered)

```bash
curl -X POST "https://api.cookify.app/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "developer@example.com",
    "password": "SecurePassword123!"
  }'
```

### Step 3: Save Your Token

From the response, save the `access_token` for future requests:

```bash
export COOKIFY_TOKEN="your_access_token_here"
```

## Core Operations

### Add Items to Pantry

```bash
curl -X POST "https://api.cookify.app/api/pantry/items" \
  -H "Authorization: Bearer $COOKIFY_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Bananas",
    "quantity": 6.0,
    "unit": "pieces",
    "category": "produce",
    "expiry_date": "2025-07-15"
  }'
```

### Get Pantry Items

```bash
curl -X GET "https://api.cookify.app/api/pantry/items" \
  -H "Authorization: Bearer $COOKIFY_TOKEN"
```

### Process Receipt with OCR

```bash
curl -X POST "https://api.cookify.app/api/ocr/process" \
  -H "Authorization: Bearer $COOKIFY_TOKEN" \
  -F "image=@receipt.jpg"
```

### Get Pantry Statistics

```bash
curl -X GET "https://api.cookify.app/api/pantry/stats" \
  -H "Authorization: Bearer $COOKIFY_TOKEN"
```

## Error Handling

All errors follow this format:

```json
{
  "detail": {
    "error": "Error description",
    "error_code": "ERROR_CODE"
  }
}
```

Common error codes:
- `AUTHENTICATION_REQUIRED`: Include Authorization header
- `INVALID_TOKEN`: Token expired, refresh or login again
- `VALIDATION_ERROR`: Check request body format
- `RATE_LIMIT_EXCEEDED`: Wait before making more requests

## Rate Limits

- **Authentication endpoints**: 10 requests/minute
- **OCR endpoints**: 20 requests/hour
- **Other endpoints**: Standard limits

## Next Steps

1. **Read the full documentation**: [API_Documentation.md](./API_Documentation.md)
2. **Explore all endpoints**: 40+ endpoints across 6 domains
3. **Try bulk operations**: Create, update, delete multiple items at once
4. **Set up webhooks**: Get notified about expiring items
5. **Use health endpoints**: Monitor your integration

## Code Examples

### JavaScript/Node.js

```javascript
const COOKIFY_API = 'https://api.cookify.app/api';
const token = 'your_access_token';

// Add pantry item
async function addPantryItem(item) {
  const response = await fetch(`${COOKIFY_API}/pantry/items`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(item)
  });
  return response.json();
}

// Get pantry items
async function getPantryItems() {
  const response = await fetch(`${COOKIFY_API}/pantry/items`, {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  return response.json();
}
```

### Python

```python
import requests

COOKIFY_API = 'https://api.cookify.app/api'
token = 'your_access_token'

headers = {
    'Authorization': f'Bearer {token}',
    'Content-Type': 'application/json'
}

# Add pantry item
def add_pantry_item(item):
    response = requests.post(
        f'{COOKIFY_API}/pantry/items',
        json=item,
        headers=headers
    )
    return response.json()

# Get pantry items
def get_pantry_items():
    response = requests.get(
        f'{COOKIFY_API}/pantry/items',
        headers=headers
    )
    return response.json()
```

## Support

- **Full Documentation**: [API_Documentation.md](./API_Documentation.md)
- **GitHub Issues**: [Report bugs or request features](https://github.com/cookify/backend/issues)
- **Email**: support@cookify.app

Happy coding! 🚀
