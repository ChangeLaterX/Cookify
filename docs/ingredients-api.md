# Ingredients API Documentation

This document provides comprehensive documentation for all ingredients endpoints in the Cookify meal planning application.

## Overview

The Ingredients API handles the management of ingredient master data including nutritional information, pricing, and search functionality. It provides CRUD operations for ingredients and supports advanced search and filtering capabilities.

**Base URL:** `/api/ingredients`

## Table of Contents

1. [API Flow](#api-flow)
2. [Endpoints Overview](#endpoints-overview)
3. [Endpoint Documentation](#endpoint-documentation)
4. [Error Handling](#error-handling)
5. [Data Models](#data-models)
6. [Usage Examples](#usage-examples)

## API Flow

```mermaid
sequenceDiagram
    participant Client
    participant API
    participant Database

    Note over Client: Public endpoints (no auth required)
    Client->>API: GET /ingredients/master
    API->>Database: Query ingredients
    Database-->>API: Return ingredient list
    API-->>Client: Return paginated results

    Client->>API: GET /ingredients/search?q=chicken
    API->>Database: Search by name
    Database-->>API: Return matching ingredients
    API-->>Client: Return search results

    Note over Client: Protected endpoints (auth required)
    Client->>API: POST /ingredients/master (with Bearer token)
    API->>API: Validate JWT token
    API->>Database: Create ingredient
    Database-->>API: Return created ingredient
    API-->>Client: Return ingredient data

    Client->>API: PUT /ingredients/master/{id} (with Bearer token)
    API->>API: Validate JWT token
    API->>Database: Update ingredient
    Database-->>API: Return updated ingredient
    API-->>Client: Return updated data
```

## Endpoints Overview

| Method | Endpoint                   | Description                          | Auth Required |
| ------ | -------------------------- | ------------------------------------ | ------------- |
| GET    | `/ingredients/master`      | List all ingredients with pagination | ❌            |
| GET    | `/ingredients/master/{id}` | Get specific ingredient by ID        | ❌            |
| POST   | `/ingredients/master`      | Create new ingredient                | ✅            |
| PUT    | `/ingredients/master/{id}` | Update existing ingredient           | ✅            |
| DELETE | `/ingredients/master/{id}` | Delete ingredient (admin-only)       | ✅            |
| GET    | `/ingredients/search`      | Search ingredients by name           | ❌            |

## Endpoint Documentation

### List All Ingredients

**GET** `/ingredients/master`

Retrieve all ingredients from the master database with pagination support.

#### Query Parameters

| Parameter | Type    | Default | Description                       |
| --------- | ------- | ------- | --------------------------------- |
| `limit`   | integer | 10      | Maximum number of results (1-100) |
| `offset`  | integer | 0       | Number of results to skip         |

#### Response

**Success (200):**

```json
{
  "success": true,
  "message": "Retrieved 10 ingredients",
  "error": null,
  "data": {
    "ingredients": [
      {
        "ingredient_id": "550e8400-e29b-41d4-a716-446655440000",
        "name": "Chicken Breast",
        "calories_per_100g": 165.0,
        "proteins_per_100g": 31.0,
        "fat_per_100g": 3.6,
        "carbs_per_100g": 0.0,
        "price_per_100g_cents": 899
      },
      {
        "ingredient_id": "550e8400-e29b-41d4-a716-446655440001",
        "name": "Brown Rice",
        "calories_per_100g": 123.0,
        "proteins_per_100g": 2.6,
        "fat_per_100g": 0.9,
        "carbs_per_100g": 25.0,
        "price_per_100g_cents": 150
      }
    ],
    "total": 850,
    "limit": 10,
    "offset": 0
  }
}
```

#### Example Requests

```bash
# Get first 10 ingredients
curl "http://dev.krija.info:8000/api/ingredients/master"

# Get next 20 ingredients with pagination
curl "http://dev.krija.info:8000/api/ingredients/master?limit=20&offset=20"

# Get maximum allowed ingredients per page
curl "http://dev.krija.info:8000/api/ingredients/master?limit=100&offset=0"
```

### Get Specific Ingredient

**GET** `/ingredients/master/{ingredient_id}`

Retrieve a specific ingredient by its unique ID.

#### Path Parameters

| Parameter       | Type | Description                         |
| --------------- | ---- | ----------------------------------- |
| `ingredient_id` | UUID | Unique identifier of the ingredient |

#### Response

**Success (200):**

```json
{
  "success": true,
  "message": "Ingredient retrieved successfully",
  "error": null,
  "data": {
    "ingredient_id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "Chicken Breast",
    "calories_per_100g": 165.0,
    "proteins_per_100g": 31.0,
    "fat_per_100g": 3.6,
    "carbs_per_100g": 0.0,
    "price_per_100g_cents": 899
  }
}
```

**Error (404 - Not Found):**

```json
{
  "detail": {
    "error": "Ingredient not found",
    "error_code": "INGREDIENT_NOT_FOUND"
  }
}
```

#### Example Requests

```bash
# Get specific ingredient by ID
curl "http://dev.krija.info:8000/api/ingredients/master/550e8400-e29b-41d4-a716-446655440000"
```

### Create New Ingredient

**POST** `/ingredients/master`

Create a new ingredient in the master database.

#### Headers

```
Authorization: Bearer <access_token>
Content-Type: application/json
```

#### Request Body

```json
{
  "name": "Organic Chicken Breast",
  "calories_per_100g": 165.0,
  "proteins_per_100g": 31.0,
  "fat_per_100g": 3.6,
  "carbs_per_100g": 0.0,
  "price_per_100g_cents": 1299
}
```

#### Validation Rules

- **name**: Required, 1-255 characters, must be unique
- **calories_per_100g**: Required, non-negative float
- **proteins_per_100g**: Required, non-negative float
- **fat_per_100g**: Required, non-negative float
- **carbs_per_100g**: Required, non-negative float
- **price_per_100g_cents**: Required, non-negative integer (price in cents)

#### Response

**Success (201):**

```json
{
  "success": true,
  "message": "Ingredient created successfully",
  "error": null,
  "data": {
    "ingredient_id": "550e8400-e29b-41d4-a716-446655440002",
    "name": "Organic Chicken Breast",
    "calories_per_100g": 165.0,
    "proteins_per_100g": 31.0,
    "fat_per_100g": 3.6,
    "carbs_per_100g": 0.0,
    "price_per_100g_cents": 1299
  }
}
```

**Error (409 - Name Exists):**

```json
{
  "detail": {
    "error": "Ingredient with this name already exists",
    "error_code": "INGREDIENT_NAME_EXISTS"
  }
}
```

**Error (401 - Unauthorized):**

```json
{
  "detail": "Not authenticated"
}
```

#### Example Requests

```bash
# Create new ingredient
curl -X POST "http://dev.krija.info:8000/api/ingredients/master" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Quinoa",
    "calories_per_100g": 120.0,
    "proteins_per_100g": 4.4,
    "fat_per_100g": 1.9,
    "carbs_per_100g": 22.0,
    "price_per_100g_cents": 350
  }'
```

### Update Existing Ingredient

**PUT** `/ingredients/master/{ingredient_id}`

Update nutritional data or price for an existing ingredient.

#### Headers

```
Authorization: Bearer <access_token>
Content-Type: application/json
```

#### Path Parameters

| Parameter       | Type | Description                                   |
| --------------- | ---- | --------------------------------------------- |
| `ingredient_id` | UUID | Unique identifier of the ingredient to update |

#### Request Body

All fields are optional. Only provide the fields you want to update:

```json
{
  "name": "Premium Chicken Breast",
  "calories_per_100g": 170.0,
  "proteins_per_100g": 32.0,
  "fat_per_100g": 4.0,
  "carbs_per_100g": 0.5,
  "price_per_100g_cents": 1499
}
```

#### Response

**Success (200):**

```json
{
  "success": true,
  "message": "Ingredient updated successfully",
  "error": null,
  "data": {
    "ingredient_id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "Premium Chicken Breast",
    "calories_per_100g": 170.0,
    "proteins_per_100g": 32.0,
    "fat_per_100g": 4.0,
    "carbs_per_100g": 0.5,
    "price_per_100g_cents": 1499
  }
}
```

**Error (404 - Not Found):**

```json
{
  "detail": {
    "error": "Ingredient not found",
    "error_code": "INGREDIENT_NOT_FOUND"
  }
}
```

**Error (409 - Name Conflict):**

```json
{
  "detail": {
    "error": "Ingredient with this name already exists",
    "error_code": "INGREDIENT_NAME_EXISTS"
  }
}
```

#### Example Requests

```bash
# Update ingredient price only
curl -X PUT "http://dev.krija.info:8000/api/ingredients/master/550e8400-e29b-41d4-a716-446655440000" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "price_per_100g_cents": 999
  }'

# Update multiple fields
curl -X PUT "http://dev.krija.info:8000/api/ingredients/master/550e8400-e29b-41d4-a716-446655440000" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Organic Free-Range Chicken Breast",
    "calories_per_100g": 168.0,
    "price_per_100g_cents": 1599
  }'
```

### Delete Ingredient

**DELETE** `/ingredients/master/{ingredient_id}`

Remove an ingredient from the master database. This is an admin-only operation.

#### Headers

```
Authorization: Bearer <access_token>
```

#### Path Parameters

| Parameter       | Type | Description                                   |
| --------------- | ---- | --------------------------------------------- |
| `ingredient_id` | UUID | Unique identifier of the ingredient to delete |

#### Response

**Success (200):**

```json
{
  "message": "Ingredient deleted successfully",
  "success": true
}
```

**Error (404 - Not Found):**

```json
{
  "detail": {
    "error": "Ingredient not found",
    "error_code": "INGREDIENT_NOT_FOUND"
  }
}
```

**Error (403 - Insufficient Permissions):**

```json
{
  "detail": {
    "error": "Admin access required",
    "error_code": "INSUFFICIENT_PERMISSIONS"
  }
}
```

#### Example Requests

```bash
# Delete ingredient (admin only)
curl -X DELETE "http://dev.krija.info:8000/api/ingredients/master/550e8400-e29b-41d4-a716-446655440000" \
  -H "Authorization: Bearer YOUR_ADMIN_ACCESS_TOKEN"
```

### Search Ingredients

**GET** `/ingredients/search`

Search ingredients by name using case-insensitive partial matching.

#### Query Parameters

| Parameter | Type    | Required | Description                                    |
| --------- | ------- | -------- | ---------------------------------------------- |
| `q`       | string  | Yes      | Search query (1-255 characters)                |
| `limit`   | integer | No       | Maximum number of results (1-100, default: 10) |
| `offset`  | integer | No       | Number of results to skip (default: 0)         |

#### Response

**Success (200):**

```json
{
  "success": true,
  "message": "Found 3 ingredients matching 'chicken'",
  "error": null,
  "data": {
    "ingredients": [
      {
        "ingredient_id": "550e8400-e29b-41d4-a716-446655440000",
        "name": "Chicken Breast",
        "calories_per_100g": 165.0,
        "proteins_per_100g": 31.0,
        "fat_per_100g": 3.6,
        "carbs_per_100g": 0.0,
        "price_per_100g_cents": 899
      },
      {
        "ingredient_id": "550e8400-e29b-41d4-a716-446655440003",
        "name": "Chicken Thigh",
        "calories_per_100g": 209.0,
        "proteins_per_100g": 26.0,
        "fat_per_100g": 10.9,
        "carbs_per_100g": 0.0,
        "price_per_100g_cents": 699
      },
      {
        "ingredient_id": "550e8400-e29b-41d4-a716-446655440004",
        "name": "Organic Chicken Stock",
        "calories_per_100g": 15.0,
        "proteins_per_100g": 1.5,
        "fat_per_100g": 0.5,
        "carbs_per_100g": 2.0,
        "price_per_100g_cents": 120
      }
    ],
    "total": 16,
    "limit": 10,
    "offset": 0
  }
}
```

**Error (422 - Validation Error):**

_Validation errors return a special response format where `detail` is an array of validation issues, unlike the common error response format._

```json
{
  "detail": [
    {
      "loc": ["query", "q"],
      "msg": "ensure this value has at least 1 characters",
      "type": "value_error.any_str.min_length",
      "ctx": { "limit_value": 1 }
    }
  ]
}
```

#### Example Requests

```bash
# Search for chicken ingredients
curl "http://dev.krija.info:8000/api/ingredients/search?q=chicken"

# Search with pagination
curl "http://dev.krija.info:8000/api/ingredients/search?q=rice&limit=5&offset=0"

# Search for vegetables
curl "http://dev.krija.info:8000/api/ingredients/search?q=tomato&limit=20"

# URL-encoded search query
curl "http://dev.krija.info:8000/api/ingredients/search?q=bell%20pepper"
```

## Error Handling

All endpoints return structured error responses with appropriate HTTP status codes.

### Error Response Format

```json
{
  "detail": {
    "error": "Human-readable error message",
    "error_code": "MACHINE_READABLE_ERROR_CODE"
  }
}
```

### Common Error Codes

| Error Code                 | Description                             | HTTP Status |
| -------------------------- | --------------------------------------- | ----------- |
| `INGREDIENT_NOT_FOUND`     | Ingredient with given ID does not exist | 404         |
| `INGREDIENT_NAME_EXISTS`   | Ingredient name already exists          | 409         |
| `DATABASE_ERROR`           | General database operation error        | 500         |
| `SEARCH_ERROR`             | Search operation failed                 | 500         |
| `CREATION_FAILED`          | Ingredient creation failed              | 500         |
| `UPDATE_FAILED`            | Ingredient update failed                | 500         |
| `VALIDATION_ERROR`         | Request validation failed               | 422         |
| `INSUFFICIENT_PERMISSIONS` | Admin access required                   | 403         |
| `INTERNAL_ERROR`           | Server error                            | 500         |

### HTTP Status Codes

- **200 OK**: Successful operation
- **201 Created**: Ingredient successfully created
- **400 Bad Request**: Invalid request data
- **401 Unauthorized**: Authentication required
- **403 Forbidden**: Admin access required
- **404 Not Found**: Ingredient not found
- **409 Conflict**: Ingredient name already exists
- **422 Unprocessable Entity**: Validation error
- **500 Internal Server Error**: Server error

## Data Models

### Ingredient Master Data

The ingredient master data contains comprehensive nutritional and pricing information:

```typescript
interface IngredientMaster {
  ingredient_id: string; // UUID
  name: string; // Unique ingredient name
  calories_per_100g: number; // Calories per 100 grams
  proteins_per_100g: number; // Protein content in grams
  fat_per_100g: number; // Fat content in grams
  carbs_per_100g: number; // Carbohydrate content in grams
  price_per_100g_cents: number; // Price in cents per 100 grams
}
```

### Nutritional Information

All nutritional values are per 100 grams of the ingredient:

- **Calories**: Energy content in kilocalories (kcal)
- **Proteins**: Protein content in grams
- **Fat**: Total fat content in grams
- **Carbohydrates**: Total carbohydrate content in grams

### Pricing

- **Price**: Stored in cents to avoid floating-point precision issues
- **Currency**: All prices are in the same currency (configurable)
- **Per 100g**: Standardized measurement for easy comparison

### Database Schema

```sql
CREATE TABLE public.ingredient_master (
  ingredient_id uuid NOT NULL DEFAULT gen_random_uuid(),
  name text NOT NULL,
  calories_per_100g real NOT NULL,
  proteins_per_100g real NOT NULL,
  fat_per_100g real NOT NULL,
  carbs_per_100g real NOT NULL,
  price_per_100g_cents integer NOT NULL,
  CONSTRAINT ingredient_master_pkey PRIMARY KEY (ingredient_id),
  CONSTRAINT ingredient_master_name_key UNIQUE (name)
) TABLESPACE pg_default;
```

## Usage Examples

### JavaScript/TypeScript

#### Complete Ingredients Client

```typescript
class IngredientsAPI {
  private baseURL = 'http://dev.krija.info:8000/api/ingredients';
  private token: string | null = null;

  setToken(token: string) {
    this.token = token;
  }

  // Get all ingredients with pagination
  async getIngredients(
    limit = 10,
    offset = 0
  ): Promise<IngredientListResponse> {
    const response = await fetch(
      `${this.baseURL}/master?limit=${limit}&offset=${offset}`
    );

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    return response.json();
  }

  // Get specific ingredient by ID
  async getIngredient(id: string): Promise<IngredientResponse> {
    const response = await fetch(`${this.baseURL}/master/${id}`);

    if (!response.ok) {
      if (response.status === 404) {
        throw new Error('Ingredient not found');
      }
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    return response.json();
  }

  // Search ingredients by name
  async searchIngredients(
    query: string,
    limit = 10,
    offset = 0
  ): Promise<IngredientListResponse> {
    const params = new URLSearchParams({
      q: query,
      limit: limit.toString(),
      offset: offset.toString(),
    });

    const response = await fetch(`${this.baseURL}/search?${params}`);

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    return response.json();
  }

  // Create new ingredient (requires authentication)
  async createIngredient(
    ingredient: CreateIngredientData
  ): Promise<IngredientResponse> {
    if (!this.token) {
      throw new Error('Authentication required');
    }

    const response = await fetch(`${this.baseURL}/master`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${this.token}`,
      },
      body: JSON.stringify(ingredient),
    });

    if (!response.ok) {
      const error = await response.json();
      if (response.status === 409) {
        throw new Error('Ingredient name already exists');
      }
      throw new Error(error.detail?.error || 'Failed to create ingredient');
    }

    return response.json();
  }

  // Update ingredient (requires authentication)
  async updateIngredient(
    id: string,
    updates: Partial<CreateIngredientData>
  ): Promise<IngredientResponse> {
    if (!this.token) {
      throw new Error('Authentication required');
    }

    const response = await fetch(`${this.baseURL}/master/${id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${this.token}`,
      },
      body: JSON.stringify(updates),
    });

    if (!response.ok) {
      const error = await response.json();
      if (response.status === 404) {
        throw new Error('Ingredient not found');
      }
      if (response.status === 409) {
        throw new Error('Ingredient name already exists');
      }
      throw new Error(error.detail?.error || 'Failed to update ingredient');
    }

    return response.json();
  }

  // Delete ingredient (admin only)
  async deleteIngredient(id: string): Promise<void> {
    if (!this.token) {
      throw new Error('Authentication required');
    }

    const response = await fetch(`${this.baseURL}/master/${id}`, {
      method: 'DELETE',
      headers: {
        Authorization: `Bearer ${this.token}`,
      },
    });

    if (!response.ok) {
      const error = await response.json();
      if (response.status === 404) {
        throw new Error('Ingredient not found');
      }
      if (response.status === 403) {
        throw new Error('Admin access required');
      }
      throw new Error(error.detail?.error || 'Failed to delete ingredient');
    }
  }
}

// Usage example
const ingredientsAPI = new IngredientsAPI();

// Get ingredients with pagination
const ingredients = await ingredientsAPI.getIngredients(20, 0);
console.log(`Found ${ingredients.data.total} ingredients`);

// Search for specific ingredients
const searchResults = await ingredientsAPI.searchIngredients('chicken', 5);
console.log(
  `Found ${searchResults.data.ingredients.length} chicken ingredients`
);

// Create new ingredient (after login)
ingredientsAPI.setToken(accessToken);
const newIngredient = await ingredientsAPI.createIngredient({
  name: 'Organic Quinoa',
  calories_per_100g: 120,
  proteins_per_100g: 4.4,
  fat_per_100g: 1.9,
  carbs_per_100g: 22,
  price_per_100g_cents: 450,
});
```

#### React Hook Example

```typescript
import { useState, useEffect } from 'react';

interface UseIngredientsOptions {
  limit?: number;
  searchQuery?: string;
}

export function useIngredients({
  limit = 10,
  searchQuery,
}: UseIngredientsOptions = {}) {
  const [ingredients, setIngredients] = useState<Ingredient[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [total, setTotal] = useState(0);

  useEffect(() => {
    async function fetchIngredients() {
      try {
        setLoading(true);
        setError(null);

        const api = new IngredientsAPI();
        let result;

        if (searchQuery) {
          result = await api.searchIngredients(searchQuery, limit);
        } else {
          result = await api.getIngredients(limit);
        }

        setIngredients(result.data.ingredients);
        setTotal(result.data.total);
      } catch (err) {
        setError(
          err instanceof Error ? err.message : 'Failed to fetch ingredients'
        );
      } finally {
        setLoading(false);
      }
    }

    fetchIngredients();
  }, [limit, searchQuery]);

  return { ingredients, loading, error, total };
}

// Usage in React component
function IngredientsList() {
  const [searchQuery, setSearchQuery] = useState('');
  const { ingredients, loading, error, total } = useIngredients({
    limit: 20,
    searchQuery: searchQuery || undefined,
  });

  if (loading) return <div>Loading ingredients...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <div>
      <input
        type="text"
        placeholder="Search ingredients..."
        value={searchQuery}
        onChange={(e) => setSearchQuery(e.target.value)}
      />

      <p>Found {total} ingredients</p>

      <ul>
        {ingredients.map((ingredient) => (
          <li key={ingredient.ingredient_id}>
            <h3>{ingredient.name}</h3>
            <p>Calories: {ingredient.calories_per_100g} per 100g</p>
            <p>
              Price: ${(ingredient.price_per_100g_cents / 100).toFixed(2)} per
              100g
            </p>
          </li>
        ))}
      </ul>
    </div>
  );
}
```

### Python

#### Complete Python Client

```python
import requests
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class Ingredient:
    ingredient_id: str
    name: str
    calories_per_100g: float
    proteins_per_100g: float
    fat_per_100g: float
    carbs_per_100g: float
    price_per_100g_cents: int

@dataclass
class CreateIngredientData:
    name: str
    calories_per_100g: float
    proteins_per_100g: float
    fat_per_100g: float
    carbs_per_100g: float
    price_per_100g_cents: int

class IngredientsAPI:
    def __init__(self, base_url: str = "http://dev.krija.info:8000/api/ingredients"):
        self.base_url = base_url
        self.token: Optional[str] = None

    def set_token(self, token: str):
        """Set authentication token for protected endpoints."""
        self.token = token

    def _get_headers(self) -> Dict[str, str]:
        """Get headers with authentication if token is available."""
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def get_ingredients(self, limit: int = 10, offset: int = 0) -> Dict[str, Any]:
        """Get all ingredients with pagination."""
        response = requests.get(
            f"{self.base_url}/master",
            params={"limit": limit, "offset": offset}
        )
        response.raise_for_status()
        return response.json()

    def get_ingredient(self, ingredient_id: str) -> Dict[str, Any]:
        """Get specific ingredient by ID."""
        response = requests.get(f"{self.base_url}/master/{ingredient_id}")
        response.raise_for_status()
        return response.json()

    def search_ingredients(self, query: str, limit: int = 10, offset: int = 0) -> Dict[str, Any]:
        """Search ingredients by name."""
        response = requests.get(
            f"{self.base_url}/search",
            params={"q": query, "limit": limit, "offset": offset}
        )
        response.raise_for_status()
        return response.json()

    def create_ingredient(self, ingredient: CreateIngredientData) -> Dict[str, Any]:
        """Create new ingredient (requires authentication)."""
        if not self.token:
            raise ValueError("Authentication required")

        response = requests.post(
            f"{self.base_url}/master",
            headers=self._get_headers(),
            json=ingredient.__dict__
        )

        if response.status_code == 409:
            raise ValueError("Ingredient name already exists")

        response.raise_for_status()
        return response.json()

    def update_ingredient(self, ingredient_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update ingredient (requires authentication)."""
        if not self.token:
            raise ValueError("Authentication required")

        response = requests.put(
            f"{self.base_url}/master/{ingredient_id}",
            headers=self._get_headers(),
            json=updates
        )

        if response.status_code == 404:
            raise ValueError("Ingredient not found")
        if response.status_code == 409:
            raise ValueError("Ingredient name already exists")

        response.raise_for_status()
        return response.json()

    def delete_ingredient(self, ingredient_id: str) -> None:
        """Delete ingredient (admin only)."""
        if not self.token:
            raise ValueError("Authentication required")

        response = requests.delete(
            f"{self.base_url}/master/{ingredient_id}",
            headers=self._get_headers()
        )

        if response.status_code == 404:
            raise ValueError("Ingredient not found")
        if response.status_code == 403:
            raise ValueError("Admin access required")

        response.raise_for_status()

# Usage examples
def main():
    api = IngredientsAPI()

    # Get ingredients with pagination
    ingredients_response = api.get_ingredients(limit=20, offset=0)
    print(f"Found {ingredients_response['data']['total']} total ingredients")

    # Search for specific ingredients
    search_results = api.search_ingredients("chicken", limit=5)
    for ingredient in search_results['data']['ingredients']:
        print(f"- {ingredient['name']}: {ingredient['calories_per_100g']} cal/100g")

    # Create new ingredient (after authentication)
    # api.set_token("your_access_token_here")
    # new_ingredient = CreateIngredientData(
    #     name="Organic Quinoa",
    #     calories_per_100g=120.0,
    #     proteins_per_100g=4.4,
    #     fat_per_100g=1.9,
    #     carbs_per_100g=22.0,
    #     price_per_100g_cents=450
    # )
    # result = api.create_ingredient(new_ingredient)
    # print(f"Created ingredient: {result['data']['name']}")

if __name__ == "__main__":
    main()
```

#### Django Integration Example

```python
# models.py
from django.db import models
import uuid

class LocalIngredient(models.Model):
    """Local cache of ingredient data from the API."""
    api_ingredient_id = models.UUIDField(unique=True)
    name = models.CharField(max_length=255)
    calories_per_100g = models.FloatField()
    proteins_per_100g = models.FloatField()
    fat_per_100g = models.FloatField()
    carbs_per_100g = models.FloatField()
    price_per_100g_cents = models.IntegerField()
    last_synced = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

# services.py
from django.utils import timezone
from datetime import timedelta

class IngredientSyncService:
    def __init__(self):
        self.api = IngredientsAPI()

    def sync_ingredients(self, force_update: bool = False):
        """Sync ingredients from API to local database."""
        cutoff_time = timezone.now() - timedelta(hours=1)

        if not force_update and LocalIngredient.objects.filter(
            last_synced__gte=cutoff_time
        ).exists():
            return  # Data is fresh enough

        # Fetch all ingredients from API
        offset = 0
        limit = 100

        while True:
            response = self.api.get_ingredients(limit=limit, offset=offset)
            ingredients = response['data']['ingredients']

            if not ingredients:
                break

            for ingredient_data in ingredients:
                LocalIngredient.objects.update_or_create(
                    api_ingredient_id=ingredient_data['ingredient_id'],
                    defaults={
                        'name': ingredient_data['name'],
                        'calories_per_100g': ingredient_data['calories_per_100g'],
                        'proteins_per_100g': ingredient_data['proteins_per_100g'],
                        'fat_per_100g': ingredient_data['fat_per_100g'],
                        'carbs_per_100g': ingredient_data['carbs_per_100g'],
                        'price_per_100g_cents': ingredient_data['price_per_100g_cents'],
                    }
                )

            offset += limit
            if len(ingredients) < limit:
                break

# views.py (Django REST Framework)
from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(['GET'])
def search_ingredients_local(request):
    """Search local ingredient cache."""
    query = request.GET.get('q', '')
    limit = min(int(request.GET.get('limit', 10)), 100)

    if query:
        ingredients = LocalIngredient.objects.filter(
            name__icontains=query
        )[:limit]
    else:
        ingredients = LocalIngredient.objects.all()[:limit]

    return Response({
        'ingredients': [
            {
                'id': str(ing.api_ingredient_id),
                'name': ing.name,
                'calories_per_100g': ing.calories_per_100g,
                'price_per_100g_cents': ing.price_per_100g_cents,
            }
            for ing in ingredients
        ]
    })
```

### cURL Examples

#### Complete cURL Commands

```bash
#!/bin/bash

# Set base URL
BASE_URL="http://dev.krija.info:8000/api/ingredients"

# 1. Get all ingredients (first page)
echo "=== Getting all ingredients ==="
curl -s "${BASE_URL}/master" | jq '.'

# 2. Get ingredients with pagination
echo -e "\n=== Getting ingredients with pagination ==="
curl -s "${BASE_URL}/master?limit=5&offset=0" | jq '.data | {total, limit, offset, count: (.ingredients | length)}'

# 3. Get specific ingredient by ID
echo -e "\n=== Getting specific ingredient ==="
INGREDIENT_ID="550e8400-e29b-41d4-a716-446655440000"
curl -s "${BASE_URL}/master/${INGREDIENT_ID}" | jq '.data.name'

# 4. Search ingredients by name
echo -e "\n=== Searching for chicken ingredients ==="
curl -s "${BASE_URL}/search?q=chicken&limit=3" | jq '.data.ingredients[].name'

# 5. Search with URL encoding
echo -e "\n=== Searching for bell pepper ==="
curl -s "${BASE_URL}/search?q=bell%20pepper" | jq '.'

# Protected endpoints (require authentication)
# Set your access token here
ACCESS_TOKEN="your_access_token_here"

if [ "$ACCESS_TOKEN" != "your_access_token_here" ]; then
    # 6. Create new ingredient
    echo -e "\n=== Creating new ingredient ==="
    curl -s -X POST "${BASE_URL}/master" \
      -H "Authorization: Bearer ${ACCESS_TOKEN}" \
      -H "Content-Type: application/json" \
      -d '{
        "name": "Test Ingredient",
        "calories_per_100g": 100.0,
        "proteins_per_100g": 10.0,
        "fat_per_100g": 5.0,
        "carbs_per_100g": 15.0,
        "price_per_100g_cents": 200
      }' | jq '.'

    # 7. Update ingredient
    echo -e "\n=== Updating ingredient ==="
    curl -s -X PUT "${BASE_URL}/master/${INGREDIENT_ID}" \
      -H "Authorization: Bearer ${ACCESS_TOKEN}" \
      -H "Content-Type: application/json" \
      -d '{
        "price_per_100g_cents": 999
      }' | jq '.data | {name, price_per_100g_cents}'

    # 8. Delete ingredient (admin only)
    echo -e "\n=== Deleting ingredient ==="
    curl -s -X DELETE "${BASE_URL}/master/${INGREDIENT_ID}" \
      -H "Authorization: Bearer ${ACCESS_TOKEN}" | jq '.'
else
    echo -e "\n=== Skipping protected endpoints (no access token) ==="
fi

# 9. Error handling examples
echo -e "\n=== Testing error handling ==="

# Invalid ingredient ID
echo "Testing invalid ingredient ID:"
curl -s "${BASE_URL}/master/invalid-uuid" | jq '.detail'

# Empty search query
echo "Testing empty search query:"
curl -s "${BASE_URL}/search?q=" | jq '.detail[0].msg' 2>/dev/null || echo "Validation error"

# Invalid pagination
echo "Testing invalid pagination:"
curl -s "${BASE_URL}/master?limit=200" | jq '.detail[0].msg' 2>/dev/null || echo "Validation error"
```

### Nutrition Calculator Example

```javascript
class NutritionCalculator {
  constructor(ingredientsAPI) {
    this.api = ingredientsAPI;
  }

  async calculateRecipeNutrition(recipe) {
    const nutrition = {
      totalCalories: 0,
      totalProteins: 0,
      totalFat: 0,
      totalCarbs: 0,
      totalCost: 0,
      ingredients: [],
    };

    for (const item of recipe.ingredients) {
      const ingredient = await this.api.getIngredient(item.ingredientId);
      const data = ingredient.data;

      // Calculate nutrition for the specific amount
      const multiplier = item.amount / 100; // amount in grams / 100g

      const itemNutrition = {
        name: data.name,
        amount: item.amount,
        calories: data.calories_per_100g * multiplier,
        proteins: data.proteins_per_100g * multiplier,
        fat: data.fat_per_100g * multiplier,
        carbs: data.carbs_per_100g * multiplier,
        cost: (data.price_per_100g_cents * multiplier) / 100,
      };

      nutrition.totalCalories += itemNutrition.calories;
      nutrition.totalProteins += itemNutrition.proteins;
      nutrition.totalFat += itemNutrition.fat;
      nutrition.totalCarbs += itemNutrition.carbs;
      nutrition.totalCost += itemNutrition.cost;
      nutrition.ingredients.push(itemNutrition);
    }

    return nutrition;
  }

  formatNutritionLabel(nutrition) {
    return `
Nutrition Facts (Total Recipe)
=============================
Calories: ${Math.round(nutrition.totalCalories)}
Proteins: ${nutrition.totalProteins.toFixed(1)}g
Fat: ${nutrition.totalFat.toFixed(1)}g
Carbohydrates: ${nutrition.totalCarbs.toFixed(1)}g
Estimated Cost: $${nutrition.totalCost.toFixed(2)}

Per Ingredient:
${nutrition.ingredients
  .map(
    (ing) =>
      `- ${ing.name} (${ing.amount}g): ${Math.round(
        ing.calories
      )} cal, $${ing.cost.toFixed(2)}`
  )
  .join('\n')}
    `.trim();
  }
}

// Usage example
const calculator = new NutritionCalculator(new IngredientsAPI());

const recipe = {
  name: 'Chicken and Rice Bowl',
  ingredients: [
    { ingredientId: '550e8400-e29b-41d4-a716-446655440000', amount: 150 }, // Chicken Breast
    { ingredientId: '550e8400-e29b-41d4-a716-446655440001', amount: 100 }, // Brown Rice
    { ingredientId: '550e8400-e29b-41d4-a716-446655440005', amount: 50 }, // Broccoli
  ],
};

const nutrition = await calculator.calculateRecipeNutrition(recipe);
console.log(calculator.formatNutritionLabel(nutrition));
```

## Best Practices

### Client-Side Caching

```javascript
class CachedIngredientsAPI extends IngredientsAPI {
  constructor() {
    super();
    this.cache = new Map();
    this.cacheTimeout = 5 * 60 * 1000; // 5 minutes
  }

  async getIngredient(id) {
    const cacheKey = `ingredient_${id}`;
    const cached = this.cache.get(cacheKey);

    if (cached && Date.now() - cached.timestamp < this.cacheTimeout) {
      return cached.data;
    }

    const data = await super.getIngredient(id);
    this.cache.set(cacheKey, {
      data,
      timestamp: Date.now(),
    });

    return data;
  }

  clearCache() {
    this.cache.clear();
  }
}
```

### Error Handling and Retry Logic

```javascript
class RobustIngredientsAPI extends IngredientsAPI {
  async withRetry(operation, maxRetries = 3) {
    for (let attempt = 1; attempt <= maxRetries; attempt++) {
      try {
        return await operation();
      } catch (error) {
        if (attempt === maxRetries) {
          throw error;
        }

        // Exponential backoff
        const delay = Math.pow(2, attempt - 1) * 1000;
        await new Promise((resolve) => setTimeout(resolve, delay));
      }
    }
  }

  async searchIngredients(query, limit, offset) {
    return this.withRetry(() => super.searchIngredients(query, limit, offset));
  }
}
```

### Batch Operations

```javascript
class BatchIngredientsAPI extends IngredientsAPI {
  async getMultipleIngredients(ids) {
    const promises = ids.map((id) =>
      this.getIngredient(id).catch((error) => ({ error, id }))
    );
    const results = await Promise.all(promises);

    return {
      successful: results.filter((r) => !r.error),
      failed: results.filter((r) => r.error),
    };
  }

  async searchMultipleTerms(queries) {
    const promises = queries.map((query) =>
      this.searchIngredients(query).catch((error) => ({ error, query }))
    );

    return Promise.all(promises);
  }
}
```

## Performance Considerations

### Pagination Strategy

- **Small lists**: Use `limit=10-20` for user interfaces
- **Data processing**: Use `limit=100` (maximum) for bulk operations
- **Progressive loading**: Implement infinite scroll with incremental `offset`

### Search Optimization

- **Debounce search queries**: Wait 300-500ms after user stops typing
- **Minimum query length**: Require at least 2-3 characters
- **Cache search results**: Cache frequent searches client-side

### Caching Recommendations

- **Individual ingredients**: Cache for 5-10 minutes
- **Search results**: Cache for 2-3 minutes
- **Full ingredient lists**: Cache for 1-2 minutes

## Security Notes

### Authentication

- Store JWT tokens securely (httpOnly cookies recommended)
- Implement automatic token refresh
- Clear tokens on logout

### Input Validation

- Validate all input on client-side before sending
- Handle server-side validation errors gracefully
- Sanitize search queries to prevent injection

### Rate Limiting

- Implement client-side rate limiting
- Respect server rate limits (check response headers)
- Use exponential backoff for retries

---

For more information or support, please refer to the main project documentation or contact the development team.
