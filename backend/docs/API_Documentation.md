# Cookify API Documentation

## Overview

Cookify is a pantry management application with a RESTful API built on FastAPI. This documentation describes all available endpoints with detailed information about request/response formats, authentication, and error handling.

**Base URL**: `/api`

## Authentication & Security

Most endpoints require authentication via JWT Bearer Token:

```http
Authorization: Bearer <jwt_token>
```

---

## 1. Authentication Domain (`/api/auth`)

### 1.1 User Registration

**Endpoint**: `POST /api/auth/register`

**Description**: Registers a new user through Supabase Auth.

**Request Body**:

```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!",
  "username": "optional_username"
}
```

**Response** (201 Created):

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
  "message": "Registration successful",
  "error": null
}
```

**Error Codes**:

- `409 Conflict`: Email already registered
- `400 Bad Request`: Validation error
- `500 Internal Server Error`: Server error

---

### 1.2 User Login

**Endpoint**: `POST /api/auth/login`

**Description**: Authenticates a user and returns JWT tokens.

**Request Body**:

```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!"
}
```

**Response** (200 OK):

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
  "message": "Login successful",
  "error": null
}
```

**Error Codes**:

- `401 Unauthorized`: Invalid credentials
- `500 Internal Server Error`: Server error

---

### 1.3 Token Refresh

**Endpoint**: `POST /api/auth/refresh`

**Description**: Renews access token with valid refresh token.

**Request Body**:

```json
{
  "refresh_token": "eyJ..."
}
```

**Response** (200 OK):

```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer",
  "expires_in": 1800,
  "expires_at": "2025-06-29T12:30:00Z"
}
```

**Error Codes**:

- `401 Unauthorized`: Invalid refresh token

---

### 1.4 Logout

**Endpoint**: `POST /api/auth/logout`

**Description**: Logs out user and invalidates the session.

**Headers**: `Authorization: Bearer <token>`

**Response** (200 OK):

```json
{
  "message": "Logged out successfully",
  "success": true
}
```

---

### 1.5 Get Current User

**Endpoint**: `GET /api/auth/me`

**Description**: Retrieves information of the current authenticated user.

**Headers**: `Authorization: Bearer <token>`

**Response** (200 OK):

```json
{
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com",
    "is_active": true,
    "is_verified": true,
    "created_at": "2025-06-29T10:00:00Z",
    "updated_at": "2025-06-29T10:00:00Z"
  },
  "profile": {
    "first_name": "John",
    "last_name": "Doe",
    "display_name": "John D.",
    "bio": "Food enthusiast"
  }
}
```

---

### 1.6 Get User Profile

**Endpoint**: `GET /api/auth/profile`

**Description**: Retrieves the current user's profile.

**Headers**: `Authorization: Bearer <token>`

**Response** (200 OK):

```json
{
  "first_name": "John",
  "last_name": "Doe",
  "display_name": "John D.",
  "bio": "Food enthusiast",
  "avatar_url": "https://example.com/avatar.jpg",
  "preferences": {
    "dietary_restrictions": ["vegetarian"],
    "favorite_cuisines": ["italian", "asian"]
  }
}
```

---

### 1.7 Update User Profile

**Endpoint**: `PUT /api/auth/me`

**Description**: Updates the current user's profile.

**Headers**: `Authorization: Bearer <token>`

**Request Body**:

```json
{
  "first_name": "John",
  "last_name": "Doe",
  "display_name": "John D.",
  "bio": "Updated bio",
  "avatar_url": "https://example.com/new-avatar.jpg"
}
```

**Response** (200 OK):

```json
{
  "first_name": "John",
  "last_name": "Doe",
  "display_name": "John D.",
  "bio": "Updated bio",
  "avatar_url": "https://example.com/new-avatar.jpg"
}
```

---

### 1.8 Password Reset Request

**Endpoint**: `POST /api/auth/forgot-password`

**Description**: Requests a password reset email.

**Request Body**:

```json
{
  "email": "user@example.com"
}
```

**Response** (200 OK):

```json
{
  "message": "If the email exists, a password reset link has been sent",
  "success": true,
  "details": {
    "email": "user@example.com"
  }
}
```

---

### 1.9 Password Reset Confirm

**Endpoint**: `POST /api/auth/reset-password`

**Description**: Resets password with token from email.

**Request Body**:

```json
{
  "token": "reset_token_from_email",
  "new_password": "NewSecurePassword123!"
}
```

**Response** (200 OK):

```json
{
  "message": "Password reset successfully",
  "success": true
}
```

**Error Codes**:

- `400 Bad Request`: Invalid token

---

### 1.10 Email Verification

**Endpoint**: `POST /api/auth/verify-email`

**Description**: Verifies email address with verification token.

**Request Body**:

```json
{
  "token": "verification_token_from_email"
}
```

**Response** (200 OK):

```json
{
  "message": "Email verified successfully",
  "success": true
}
```

---

### 1.11 Resend Verification Email

**Endpoint**: `POST /api/auth/resend-verification`

**Description**: Resends the verification email.

**Request Body**:

```json
{
  "email": "user@example.com"
}
```

**Response** (200 OK):

```json
{
  "message": "If the email is registered and unverified, a verification link has been sent",
  "success": true,
  "details": {
    "email": "user@example.com"
  }
}
```

---

### 1.12 Change Password

**Endpoint**: `POST /api/auth/change-password`

**Description**: Changes password of the authenticated user.

**Headers**: `Authorization: Bearer <token>`

**Request Body**:

```json
{
  "current_password": "CurrentPassword123!",
  "new_password": "NewSecurePassword123!"
}
```

**Response** (200 OK):

```json
{
  "message": "Password changed successfully",
  "success": true,
  "details": {
    "user_id": "550e8400-e29b-41d4-a716-446655440000"
  }
}
```

**Error Codes**:

- `400 Bad Request`: Current password incorrect

---

### 1.13 Optional User Info

**Endpoint**: `GET /api/auth/user-info`

**Description**: Retrieves user information if authenticated, otherwise null.

**Headers**: `Authorization: Bearer <token>` (optional)

**Response** (200 OK):

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "is_active": true,
  "is_verified": true,
  "created_at": "2025-06-29T10:00:00Z",
  "updated_at": "2025-06-29T10:00:00Z"
}
```

or `null` if not authenticated.

---

### 1.14 Development Test Login

**Endpoint**: `POST /api/auth/dev-login`

**Description**: Creates test tokens for development purposes (only available in DEBUG mode).

**Response** (200 OK):

```json
{
  "success": true,
  "data": {
    "access_token": "test_token",
    "refresh_token": "test_refresh_token",
    "token_type": "bearer",
    "expires_in": 1800,
    "expires_at": "2025-06-29T12:30:00Z"
  },
  "message": "Development test login successful"
}
```

---

### 1.15 Check Password Strength

**Endpoint**: `POST /api/auth/check-password-strength`

**Description**: Analyzes password strength and provides detailed feedback.

**Headers**: `Authorization: Bearer <token>` (optional)

**Request Body**:

```json
{
  "password": "MyPassword123!"
}
```

**Response** (200 OK):

```json
{
  "strength": 4,
  "score": 85.5,
  "is_valid": true,
  "errors": [],
  "warnings": ["Password could include more special characters"],
  "suggestions": ["Consider adding symbols like @, #, $"],
  "requirements": [
    {
      "key": "min_length",
      "met": true,
      "description": "At least 12 characters long"
    },
    {
      "key": "uppercase",
      "met": true,
      "description": "Contains uppercase letters (A-Z)"
    }
  ],
  "strength_label": "Good"
}
```

---

## 2. Pantry Items Domain (`/api/pantry`)

### 2.1 List User's Pantry Items

**Endpoint**: `GET /api/pantry/items`

**Description**: Retrieves all pantry items for the authenticated user with pagination and filter options.

**Headers**: `Authorization: Bearer <token>`

**Query Parameters**:

- `page`: Page number (default: 1, min: 1)
- `per_page`: Items per page (default: 50, min: 1, max: 100)
- `category`: Filter by category (optional)
- `search`: Search in item names (optional)

**Response** (200 OK):

```json
{
  "success": true,
  "message": "Retrieved 3 pantry items",
  "data": {
    "items": [
      {
        "id": "550e8400-e29b-41d4-a716-446655440002",
        "user_id": "550e8400-e29b-41d4-a716-446655440000",
        "name": "Bananas",
        "quantity": 6.0,
        "unit": "pieces",
        "category": "produce",
        "expiry_date": "2025-07-02",
        "added_at": "2025-06-29T10:00:00Z",
        "ingredient_id": "550e8400-e29b-41d4-a716-446655440001"
      }
    ],
    "total_count": 3,
    "page": 1,
    "per_page": 50,
    "total_pages": 1
  }
}
```

---

### 2.2 Get Pantry Item by ID

**Endpoint**: `GET /api/pantry/items/{item_id}`

**Description**: Retrieves a specific pantry item by its ID.

**Headers**: `Authorization: Bearer <token>`

**Path Parameters**:

- `item_id`: UUID of the item

**Response** (200 OK):

```json
{
  "success": true,
  "message": "Pantry item retrieved successfully",
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440002",
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "Bananas",
    "quantity": 6.0,
    "unit": "pieces",
    "category": "produce",
    "expiry_date": "2025-07-02",
    "added_at": "2025-06-29T10:00:00Z",
    "ingredient_id": "550e8400-e29b-41d4-a716-446655440001"
  }
}
```

**Error Codes**:

- `404 Not Found`: Item not found or doesn't belong to user

---

### 2.3 Create New Pantry Item

**Endpoint**: `POST /api/pantry/items`

**Description**: Adds a new item to the user's pantry.

**Headers**: `Authorization: Bearer <token>`

**Request Body**:

```json
{
  "name": "Milk",
  "quantity": 1.0,
  "unit": "liter",
  "category": "dairy",
  "expiry_date": "2025-07-05",
  "ingredient_id": "550e8400-e29b-41d4-a716-446655440003"
}
```

**Response** (201 Created):

```json
{
  "success": true,
  "message": "Pantry item created successfully",
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440004",
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "Milk",
    "quantity": 1.0,
    "unit": "liter",
    "category": "dairy",
    "expiry_date": "2025-07-05",
    "added_at": "2025-06-29T10:30:00Z",
    "ingredient_id": "550e8400-e29b-41d4-a716-446655440003"
  }
}
```

**Error Codes**:

- `422 Unprocessable Entity`: Validation error

---

### 2.4 Update Pantry Item

**Endpoint**: `PUT /api/pantry/items/{item_id}`

**Description**: Updates an existing pantry item.

**Headers**: `Authorization: Bearer <token>`

**Path Parameters**:

- `item_id`: UUID of the item

**Request Body**:

```json
{
  "name": "Fresh Milk",
  "quantity": 2.0,
  "unit": "liter",
  "category": "dairy",
  "expiry_date": "2025-07-10"
}
```

**Response** (200 OK):

```json
{
  "success": true,
  "message": "Pantry item updated successfully",
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440004",
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "Fresh Milk",
    "quantity": 2.0,
    "unit": "liter",
    "category": "dairy",
    "expiry_date": "2025-07-10",
    "added_at": "2025-06-29T10:30:00Z",
    "ingredient_id": "550e8400-e29b-41d4-a716-446655440003"
  }
}
```

**Error Codes**:

- `404 Not Found`: Item not found
- `422 Unprocessable Entity`: Validation error

---

### 2.5 Delete Pantry Item

**Endpoint**: `DELETE /api/pantry/items/{item_id}`

**Description**: Removes an item from the user's pantry.

**Headers**: `Authorization: Bearer <token>`

**Path Parameters**:

- `item_id`: UUID of the item

**Response** (200 OK):

```json
{
  "success": true,
  "message": "Pantry item deleted successfully"
}
```

**Error Codes**:

- `404 Not Found`: Item not found

---

### 2.6 Bulk Create Pantry Items

**Endpoint**: `POST /api/pantry/items/bulk`

**Description**: Adds multiple items to pantry at once (max 50 items).

**Headers**: `Authorization: Bearer <token>`

**Request Body**:

```json
{
  "items": [
    {
      "name": "Apples",
      "quantity": 5.0,
      "unit": "pieces",
      "category": "produce",
      "expiry_date": "2025-07-15",
      "ingredient_id": "550e8400-e29b-41d4-a716-446655440005"
    },
    {
      "name": "Bread",
      "quantity": 1.0,
      "unit": "loaf",
      "category": "bakery",
      "expiry_date": "2025-06-30",
      "ingredient_id": "550e8400-e29b-41d4-a716-446655440006"
    }
  ]
}
```

**Response** (201 Created):

```json
{
  "success": true,
  "message": "Bulk create completed: 2 successful, 0 failed",
  "data": {
    "successful": [
      {
        "id": "550e8400-e29b-41d4-a716-446655440007",
        "user_id": "550e8400-e29b-41d4-a716-446655440000",
        "name": "Apples",
        "quantity": 5.0,
        "unit": "pieces",
        "category": "produce",
        "expiry_date": "2025-07-15",
        "added_at": "2025-06-29T11:00:00Z",
        "ingredient_id": "550e8400-e29b-41d4-a716-446655440005"
      }
    ],
    "failed": [],
    "total_processed": 2,
    "success_count": 2,
    "failure_count": 0
  }
}
```

---

### 2.7 Bulk Update Pantry Items

**Endpoint**: `PUT /api/pantry/items/bulk`

**Description**: Updates multiple items at once (max 50 items).

**Headers**: `Authorization: Bearer <token>`

**Request Body**:

```json
{
  "updates": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440007",
      "quantity": 3.0,
      "expiry_date": "2025-07-20"
    }
  ]
}
```

**Response** (200 OK):

```json
{
  "success": true,
  "message": "Bulk update completed: 1 successful, 0 failed",
  "data": {
    "successful": [
      {
        "id": "550e8400-e29b-41d4-a716-446655440007",
        "user_id": "550e8400-e29b-41d4-a716-446655440000",
        "name": "Apples",
        "quantity": 3.0,
        "unit": "pieces",
        "category": "produce",
        "expiry_date": "2025-07-20",
        "added_at": "2025-06-29T11:00:00Z",
        "ingredient_id": "550e8400-e29b-41d4-a716-446655440005"
      }
    ],
    "failed": [],
    "total_processed": 1,
    "success_count": 1,
    "failure_count": 0
  }
}
```

---

### 2.8 Bulk Delete Pantry Items

**Endpoint**: `DELETE /api/pantry/items/bulk`

**Description**: Deletes multiple items at once (max 50 items).

**Headers**: `Authorization: Bearer <token>`

**Request Body**:

```json
{
  "item_ids": [
    "550e8400-e29b-41d4-a716-446655440007",
    "550e8400-e29b-41d4-a716-446655440008"
  ]
}
```

**Response** (200 OK):

```json
{
  "success": true,
  "message": "Bulk delete completed: 2 successful, 0 failed",
  "data": {
    "successful": [
      {
        "id": "550e8400-e29b-41d4-a716-446655440007",
        "user_id": "550e8400-e29b-41d4-a716-446655440000",
        "name": "Deleted Item",
        "quantity": 0,
        "unit": "",
        "category": null,
        "expiry_date": null,
        "added_at": "2025-06-29T12:00:00Z",
        "ingredient_id": "550e8400-e29b-41d4-a716-446655440007"
      }
    ],
    "failed": [],
    "total_processed": 2,
    "success_count": 2,
    "failure_count": 0
  }
}
```

---

### 2.9 Get Pantry Statistics

**Endpoint**: `GET /api/pantry/stats`

**Description**: Retrieves comprehensive statistics about the user's pantry.

**Headers**: `Authorization: Bearer <token>`

**Response** (200 OK):

```json
{
  "success": true,
  "message": "Pantry statistics retrieved successfully",
  "data": {
    "total_items": 15,
    "total_categories": 5,
    "items_expiring_soon": 3,
    "expired_items": 1,
    "low_stock_items": 2,
    "total_value": 45.67,
    "most_common_category": "produce",
    "newest_item_date": "2025-06-29T11:00:00Z",
    "oldest_item_date": "2025-06-15T09:00:00Z"
  }
}
```

---

### 2.10 Get Category Statistics

**Endpoint**: `GET /api/pantry/categories`

**Description**: Retrieves a breakdown of pantry items by categories.

**Headers**: `Authorization: Bearer <token>`

**Response** (200 OK):

```json
{
  "success": true,
  "message": "Category statistics retrieved successfully",
  "data": {
    "categories": [
      {
        "category": "produce",
        "count": 8,
        "percentage": 53.3,
        "total_value": 24.50
      },
      {
        "category": "dairy",
        "count": 3,
        "percentage": 20.0,
        "total_value": 12.75
      }
    ],
    "total_categories": 5,
    "most_popular": "produce",
    "least_popular": "spices"
  }
}
```

---

### 2.11 Get Expiry Report

**Endpoint**: `GET /api/pantry/expiring`

**Description**: Retrieves a report on items by expiry status (expired, expiring soon, fresh).

**Headers**: `Authorization: Bearer <token>`

**Response** (200 OK):

```json
{
  "success": true,
  "message": "Expiry report retrieved successfully",
  "data": {
    "expired": [
      {
        "id": "550e8400-e29b-41d4-a716-446655440009",
        "name": "Old Yogurt",
        "expiry_date": "2025-06-25",
        "days_overdue": 4
      }
    ],
    "expiring_soon": [
      {
        "id": "550e8400-e29b-41d4-a716-446655440010",
        "name": "Fresh Bread",
        "expiry_date": "2025-06-30",
        "days_until_expiry": 1
      }
    ],
    "fresh": [
      {
        "id": "550e8400-e29b-41d4-a716-446655440011",
        "name": "New Milk",
        "expiry_date": "2025-07-10",
        "days_until_expiry": 11
      }
    ],
    "total_expired": 1,
    "total_expiring_soon": 3,
    "total_fresh": 11
  }
}
```

---

### 2.12 Get Low Stock Report

**Endpoint**: `GET /api/pantry/low-stock`

**Description**: Retrieves a report on items with low stock.

**Headers**: `Authorization: Bearer <token>`

**Query Parameters**:

- `threshold`: Quantity threshold for low stock (default: 1.0, min: 0, max: 10)

**Response** (200 OK):

```json
{
  "success": true,
  "message": "Low stock report retrieved successfully",
  "data": {
    "low_stock_items": [
      {
        "id": "550e8400-e29b-41d4-a716-446655440012",
        "name": "Salt",
        "quantity": 0.5,
        "unit": "kg",
        "threshold_used": 1.0,
        "shortage": 0.5
      }
    ],
    "total_low_stock": 2,
    "threshold_used": 1.0,
    "suggestions": [
      "Consider restocking Salt",
      "Check if Pepper needs replenishing"
    ]
  }
}
```

---

## 3. Health Domain (`/api/health`)

### 3.1 Comprehensive Health Check

**Endpoint**: `GET /api/health`

**Description**: Performs a comprehensive health check of all services.

**Response** (200 OK):

```json
{
  "status": "healthy",
  "timestamp": "2025-06-29T12:00:00Z",
  "services": [
    {
      "name": "authentication",
      "status": "healthy",
      "response_time_ms": 45,
      "details": {
        "supabase_auth": "connected",
        "jwt_validation": "working"
      },
      "last_check": "2025-06-29T12:00:00Z"
    },
    {
      "name": "database",
      "status": "healthy",
      "response_time_ms": 23,
      "details": {
        "connection": "active",
        "query_performance": "optimal"
      },
      "last_check": "2025-06-29T12:00:00Z"
    },
    {
      "name": "ocr_service",
      "status": "healthy",
      "response_time_ms": 127,
      "details": {
        "tesseract": "available",
        "image_processing": "working"
      },
      "last_check": "2025-06-29T12:00:00Z"
    }
  ],
  "system_info": {
    "cpu_usage": 12.5,
    "memory_usage": 256.7,
    "disk_usage": 45.3,
    "uptime": 86400
  }
}
```

**Status Values**:

- `healthy`: All services functioning normally
- `degraded`: Some services have issues
- `unhealthy`: Critical services are down

---

### 3.2 Quick Health Check

**Endpoint**: `GET /api/health/quick`

**Description**: Quick health check without detailed service information.

**Response** (200 OK):

```json
{
  "status": "healthy",
  "timestamp": "2025-06-29T12:00:00Z",
  "response_time_ms": 15
}
```

---

### 3.3 Liveness Probe

**Endpoint**: `GET /api/health/live`

**Description**: Liveness probe for Kubernetes/Docker orchestration. Only checks if the application is running.

**Response** (200 OK):

```json
{
  "status": "alive",
  "timestamp": "2025-06-29T12:00:00Z"
}
```

---

### 3.4 Readiness Probe

**Endpoint**: `GET /api/health/ready`

**Description**: Readiness probe for Kubernetes/Docker orchestration. Checks if the application is ready to handle traffic.

**Response** (200 OK):

```json
{
  "status": "ready",
  "timestamp": "2025-06-29T12:00:00Z",
  "database": "connected"
}
```

**Error Response** (503 Service Unavailable):

```json
{
  "status": "not_ready",
  "error": "Database connection failed",
  "timestamp": "2025-06-29T12:00:00Z"
}
```

---

### 3.5 Health Metrics

**Endpoint**: `GET /api/health/metrics`

**Description**: Retrieves health metrics and system overview.

**Response** (200 OK):

```json
{
  "system_overview": {
    "cpu_usage": 12.5,
    "memory_usage": 256.7,
    "disk_usage": 45.3,
    "uptime": 86400,
    "active_connections": 15
  },
  "service_metrics": {
    "authentication": {
      "service_name": "authentication",
      "total_checks": 1440,
      "successful_checks": 1438,
      "failed_checks": 2,
      "avg_response_time": 45.2,
      "max_response_time": 125,
      "min_response_time": 12,
      "uptime_percentage": 99.86,
      "last_check": "2025-06-29T12:00:00Z",
      "last_failure": "2025-06-29T08:15:00Z",
      "consecutive_failures": 0,
      "consecutive_successes": 156
    }
  },
  "timestamp": "2025-06-29T12:00:00Z"
}
```

---

### 3.6 Health Alerts

**Endpoint**: `GET /api/health/alerts`

**Description**: Retrieves current health alerts.

**Query Parameters**:

- `hours`: Number of hours to look back for alerts (default: 1, min: 1, max: 168)

**Response** (200 OK):

```json
{
  "alerts": [
    {
      "level": "warning",
      "service_name": "ocr_service",
      "message": "Response time above threshold",
      "timestamp": "2025-06-29T11:30:00Z",
      "metric": {
        "status": "healthy",
        "response_time_ms": 850,
        "error_message": null
      }
    }
  ],
  "hours_back": 1,
  "alert_count": 1,
  "timestamp": "2025-06-29T12:00:00Z"
}
```

---

### 3.7 Service Health History

**Endpoint**: `GET /api/health/service/{service_name}/history`

**Description**: Retrieves health check history for a specific service.

**Path Parameters**:

- `service_name`: Name of the service (e.g. "authentication", "database", "ocr_service")

**Query Parameters**:

- `hours`: Number of hours to look back (default: 1, min: 1, max: 168)

**Response** (200 OK):

```json
{
  "service_name": "authentication",
  "hours_back": 1,
  "history": [
    {
      "timestamp": "2025-06-29T12:00:00Z",
      "status": "healthy",
      "response_time_ms": 45,
      "error_message": null,
      "details": {
        "supabase_auth": "connected"
      }
    }
  ],
  "history_count": 60,
  "service_metrics": {
    "service_name": "authentication",
    "total_checks": 1440,
    "successful_checks": 1438,
    "failed_checks": 2,
    "avg_response_time": 45.2,
    "uptime_percentage": 99.86,
    "consecutive_failures": 0
  },
  "timestamp": "2025-06-29T12:00:00Z"
}
```

---

## 4. Ingredients Domain (`/api/ingredients`)

### 4.1 List Ingredients

**Endpoint**: `GET /api/ingredients/master`

**Description**: Lists all ingredients from the master table with pagination.

**Query Parameters**:

- `limit`: Maximum number of results (default: 50, min: 1, max: 100)
- `offset`: Number of results to skip (default: 0, min: 0)

**Response** (200 OK):

```json
{
  "success": true,
  "data": {
    "ingredients": [
      {
        "id": "550e8400-e29b-41d4-a716-446655440001",
        "name": "Banana",
        "category": "produce",
        "nutritional_info": {
          "calories_per_100g": 89,
          "carbs_per_100g": 22.8,
          "protein_per_100g": 1.1,
          "fat_per_100g": 0.3,
          "fiber_per_100g": 2.6
        },
        "average_price_per_unit": 0.25,
        "common_units": ["piece", "bunch", "kg"],
        "storage_tips": "Store at room temperature until ripe",
        "created_at": "2025-06-15T10:00:00Z",
        "updated_at": "2025-06-20T14:30:00Z"
      }
    ],
    "total": 1250,
    "limit": 50,
    "offset": 0
  },
  "message": "Retrieved 50 ingredients",
  "error": null
}
```

---

### 4.2 Get Ingredient by ID

**Endpoint**: `GET /api/ingredients/master/{ingredient_id}`

**Description**: Retrieves a specific ingredient by its ID from the master table.

**Path Parameters**:

- `ingredient_id`: UUID of the ingredient

**Response** (200 OK):

```json
{
  "success": true,
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440001",
    "name": "Banana",
    "category": "produce",
    "nutritional_info": {
      "calories_per_100g": 89,
      "carbs_per_100g": 22.8,
      "protein_per_100g": 1.1,
      "fat_per_100g": 0.3,
      "fiber_per_100g": 2.6,
      "vitamin_c_mg": 8.7,
      "potassium_mg": 358
    },
    "average_price_per_unit": 0.25,
    "common_units": ["piece", "bunch", "kg"],
    "storage_tips": "Store at room temperature until ripe, then refrigerate",
    "shelf_life_days": 7,
    "seasonal_availability": ["year-round"],
    "aliases": ["banana", "banane"],
    "created_at": "2025-06-15T10:00:00Z",
    "updated_at": "2025-06-20T14:30:00Z"
  },
  "message": "Ingredient retrieved successfully",
  "error": null
}
```

**Error Codes**:

- `404 Not Found`: Ingredient not found

---

### 4.3 Create New Ingredient

**Endpoint**: `POST /api/ingredients/master`

**Description**: Creates a new ingredient in the master table.

**Headers**: `Authorization: Bearer <token>`

**Request Body**:

```json
{
  "name": "Organic Quinoa",
  "category": "grains",
  "nutritional_info": {
    "calories_per_100g": 368,
    "carbs_per_100g": 64.2,
    "protein_per_100g": 14.1,
    "fat_per_100g": 6.1,
    "fiber_per_100g": 7.0
  },
  "average_price_per_unit": 5.99,
  "common_units": ["cup", "kg", "package"],
  "storage_tips": "Store in a cool, dry place in airtight container",
  "shelf_life_days": 730,
  "aliases": ["quinoa", "kinoa"]
}
```

**Response** (201 Created):

```json
{
  "success": true,
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440013",
    "name": "Organic Quinoa",
    "category": "grains",
    "nutritional_info": {
      "calories_per_100g": 368,
      "carbs_per_100g": 64.2,
      "protein_per_100g": 14.1,
      "fat_per_100g": 6.1,
      "fiber_per_100g": 7.0
    },
    "average_price_per_unit": 5.99,
    "common_units": ["cup", "kg", "package"],
    "storage_tips": "Store in a cool, dry place in airtight container",
    "shelf_life_days": 730,
    "aliases": ["quinoa", "kinoa"],
    "created_at": "2025-06-29T12:00:00Z",
    "updated_at": "2025-06-29T12:00:00Z"
  },
  "message": "Ingredient created successfully",
  "error": null
}
```

**Error Codes**:

- `409 Conflict`: Ingredient name already exists
- `400 Bad Request`: Validation error

---

### 4.4 Update Ingredient

**Endpoint**: `PUT /api/ingredients/master/{ingredient_id}`

**Description**: Updates nutritional data or price of an ingredient.

**Headers**: `Authorization: Bearer <token>`

**Path Parameters**:

- `ingredient_id`: UUID of the ingredient

**Request Body**:

```json
{
  "nutritional_info": {
    "calories_per_100g": 370,
    "vitamin_c_mg": 9.0
  },
  "average_price_per_unit": 6.25,
  "storage_tips": "Updated storage recommendations"
}
```

**Response** (200 OK):

```json
{
  "success": true,
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440013",
    "name": "Organic Quinoa",
    "category": "grains",
    "nutritional_info": {
      "calories_per_100g": 370,
      "carbs_per_100g": 64.2,
      "protein_per_100g": 14.1,
      "fat_per_100g": 6.1,
      "fiber_per_100g": 7.0,
      "vitamin_c_mg": 9.0
    },
    "average_price_per_unit": 6.25,
    "storage_tips": "Updated storage recommendations",
    "updated_at": "2025-06-29T12:30:00Z"
  },
  "message": "Ingredient updated successfully",
  "error": null
}
```

**Error Codes**:

- `404 Not Found`: Ingredient not found
- `409 Conflict`: Name already exists

---

### 4.5 Delete Ingredient (Admin Only)

**Endpoint**: `DELETE /api/ingredients/master/{ingredient_id}`

**Description**: Removes a master ingredient from the database (admin only).

**Headers**: `Authorization: Bearer <token>`

**Path Parameters**:

- `ingredient_id`: UUID of the ingredient

**Response** (200 OK):

```json
{
  "message": "Ingredient deleted successfully",
  "success": true
}
```

**Error Codes**:

- `404 Not Found`: Ingredient not found
- `403 Forbidden`: No admin permissions (if implemented)

---

### 4.6 Search Ingredients

**Endpoint**: `GET /api/ingredients/search`

**Description**: Searches ingredients by name via query parameter.

**Query Parameters**:

- `q`: Search query (required, min: 1, max: 255 characters)
- `limit`: Maximum number of results (default: 20, min: 1, max: 100)
- `offset`: Number of results to skip (default: 0, min: 0)

**Response** (200 OK):

```json
{
  "success": true,
  "data": {
    "ingredients": [
      {
        "id": "550e8400-e29b-41d4-a716-446655440001",
        "name": "Banana",
        "category": "produce",
        "nutritional_info": {
          "calories_per_100g": 89
        },
        "average_price_per_unit": 0.25,
        "common_units": ["piece", "bunch", "kg"]
      }
    ],
    "total": 3,
    "limit": 20,
    "offset": 0
  },
  "message": "Found 3 ingredients matching 'banana'",
  "error": null
}
```

---

## 5. OCR Domain (`/api/ocr`)

### 5.1 Extract Text from Receipt

**Endpoint**: `POST /api/ocr/extract-text`

**Description**: Extracts raw text from a receipt image using OCR.

**Request**: Multipart Form Data

- `image`: Image file (JPEG, PNG, etc.)

**Response** (200 OK):

```json
{
  "extracted_text": "SUPERMARKET XYZ\nBananas 3x 0.25 = 0.75\nMilk 1L 2.99\nBread 1.89\nTOTAL: 5.63",
  "confidence": 87.5,
  "processing_time_ms": 1250,
  "text_regions": [
    {
      "text": "SUPERMARKET XYZ",
      "confidence": 95.2,
      "bbox": {
        "x": 150,
        "y": 50,
        "width": 200,
        "height": 30
      }
    }
  ],
  "image_metadata": {
    "width": 800,
    "height": 1200,
    "format": "JPEG",
    "size_bytes": 256789
  }
}
```

**Error Codes**:

- `400 Bad Request`: Invalid file type or empty file
- `500 Internal Server Error`: OCR processing error

---

### 5.2 Process Receipt with Ingredient Suggestions

**Endpoint**: `POST /api/ocr/process`

**Description**: Processes a receipt image and provides ingredient matching suggestions.

**Request**: Multipart Form Data

- `image`: Image file (JPEG, PNG, etc.)

**Response** (200 OK):

```json
{
  "success": true,
  "data": {
    "detected_items": [
      {
        "raw_text": "Bananas 3x",
        "extracted_name": "Bananas",
        "confidence": 92.1,
        "quantity": 3.0,
        "unit": "pieces",
        "price": 0.75,
        "suggestions": [
          {
            "ingredient_id": "550e8400-e29b-41d4-a716-446655440001",
            "name": "Banana",
            "category": "produce",
            "confidence_score": 95.8,
            "match_type": "exact"
          }
        ]
      },
      {
        "raw_text": "Milk 1L",
        "extracted_name": "Milk",
        "confidence": 89.4,
        "quantity": 1.0,
        "unit": "liter",
        "price": 2.99,
        "suggestions": [
          {
            "ingredient_id": "550e8400-e29b-41d4-a716-446655440014",
            "name": "Whole Milk",
            "category": "dairy",
            "confidence_score": 87.3,
            "match_type": "partial"
          },
          {
            "ingredient_id": "550e8400-e29b-41d4-a716-446655440015",
            "name": "Low-fat Milk",
            "category": "dairy",
            "confidence_score": 82.1,
            "match_type": "partial"
          }
        ]
      }
    ],
    "total_items_detected": 3,
    "processing_time_ms": 2150,
    "ocr_confidence": 88.7,
    "total_amount": 5.63,
    "store_info": {
      "name": "SUPERMARKET XYZ",
      "confidence": 95.2
    }
  },
  "message": "Receipt processed successfully. Found 3 items.",
  "error": null
}
```

**Error Response** (on OCR failure):

```json
{
  "success": false,
  "data": null,
  "message": "Failed to process receipt",
  "error": "OCR processing failed (OCR_ERROR)"
}
```

**Error Codes**:

- `400 Bad Request`: Invalid file type or empty file
- `500 Internal Server Error`: OCR processing error

---

## 6. Update Domain (`/api/update`)

### 6.1 Update Ingredient Cache

**Endpoint**: `POST /api/update/ingredient_cache`

**Description**: Updates the local cache file with ingredient names from the database.

**Query Parameters**:

- `force`: Forces update even if cache is still current (default: false)

**Response** (200 OK):

```json
{
  "success": true,
  "updated": true,
  "cache_file_path": "/app/data/ingredient_names.txt",
  "ingredients_count": 1250,
  "last_updated": "2025-06-29T12:00:00Z",
  "update_reason": "Manual update requested",
  "processing_time_ms": 450,
  "file_size_bytes": 52480,
  "metadata": {
    "source": "database",
    "version": "1.2.3",
    "categories_included": [
      "produce",
      "dairy",
      "grains",
      "proteins",
      "spices"
    ]
  }
}
```

**Error Codes**:

- `500 Internal Server Error`: Update error

---

### 6.2 Get Ingredient Cache Status

**Endpoint**: `GET /api/update/ingredient_cache/status`

**Description**: Retrieves the current status and metadata of the ingredient cache.

**Response** (200 OK):

```json
{
  "cache_exists": true,
  "cache_file_path": "/app/data/ingredient_names.txt",
  "last_updated": "2025-06-29T10:00:00Z",
  "ingredients_count": 1250,
  "file_size_bytes": 52480,
  "is_stale": false,
  "age_hours": 2.5,
  "next_auto_update": "2025-07-06T10:00:00Z",
  "cache_version": "1.2.3",
  "database_count": 1250,
  "sync_status": "in_sync",
  "performance_metrics": {
    "avg_lookup_time_ms": 0.15,
    "cache_hit_rate": 98.7
  }
}
```

---

### 6.3 Force Refresh All Caches

**Endpoint**: `POST /api/update/all_caches`

**Description**: Forces update of all application caches.

**Response** (200 OK or 207 Multi-Status):

```json
{
  "overall_success": true,
  "caches_refreshed": [
    {
      "cache_name": "ingredient_names",
      "success": true,
      "message": "Cache updated successfully",
      "processing_time_ms": 450,
      "items_count": 1250
    },
    {
      "cache_name": "nutrition_data",
      "success": true,
      "message": "Nutrition cache refreshed",
      "processing_time_ms": 230,
      "items_count": 850
    }
  ],
  "failed_caches": [],
  "total_processing_time_ms": 680,
  "timestamp": "2025-06-29T12:00:00Z"
}
```

**Partial Success Response** (207 Multi-Status):

```json
{
  "overall_success": false,
  "caches_refreshed": [
    {
      "cache_name": "ingredient_names",
      "success": true,
      "message": "Cache updated successfully",
      "processing_time_ms": 450
    }
  ],
  "failed_caches": [
    {
      "cache_name": "external_api_cache",
      "success": false,
      "error": "External service unavailable",
      "error_code": "SERVICE_UNAVAILABLE"
    }
  ],
  "total_processing_time_ms": 450,
  "timestamp": "2025-06-29T12:00:00Z"
}
```

---

## Error Handling

### Standard Error Response Format

All endpoints follow a consistent error format:

```json
{
  "detail": {
    "error": "Error message",
    "error_code": "ERROR_CODE"
  }
}
```

### Common Error Codes

- `VALIDATION_ERROR`: Input data invalid
- `AUTHENTICATION_REQUIRED`: Authentication required
- `INVALID_TOKEN`: JWT token invalid or expired
- `INSUFFICIENT_PERMISSIONS`: Insufficient permissions
- `RESOURCE_NOT_FOUND`: Requested resource not found
- `DUPLICATE_RESOURCE`: Resource already exists
- `RATE_LIMIT_EXCEEDED`: Rate limit exceeded
- `INTERNAL_ERROR`: Internal server error
- `SERVICE_UNAVAILABLE`: Service temporarily unavailable

### HTTP Status Codes

- `200 OK`: Successful request
- `201 Created`: Resource successfully created
- `204 No Content`: Successful request without content
- `400 Bad Request`: Invalid request
- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Access denied
- `404 Not Found`: Resource not found
- `409 Conflict`: Resource conflict
- `422 Unprocessable Entity`: Validation error
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Server error
- `503 Service Unavailable`: Service unavailable

---

## Rate Limiting

### Authentication Endpoints

- **Limit**: 10 requests per minute per IP
- **Affected endpoints**: `/api/auth/login`, `/api/auth/register`, `/api/auth/refresh`

### OCR Endpoints

- **Limit**: 20 requests per hour per authenticated user
- **Affected endpoints**: `/api/ocr/extract-text`, `/api/ocr/process`

### Rate Limiting Headers

```http
X-RateLimit-Limit: 10
X-RateLimit-Remaining: 7
X-RateLimit-Reset: 1719662400
```

### Rate Limit Exceeded Response

```json
{
  "detail": {
    "error": "Rate limit exceeded",
    "error_code": "RATE_LIMIT_EXCEEDED",
    "retry_after": 60
  }
}
```

---

## Security Headers

All responses include security headers:

```http
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Strict-Transport-Security: max-age=31536000; includeSubDomains
Content-Security-Policy: default-src 'self'
```

---

## Examples

### Complete User Registration Flow

```bash
# 1. Register user
curl -X POST "https://api.cookify.app/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "password": "SecurePassword123!",
    "username": "john_doe"
  }'

# 2. Verify email (token from email)
curl -X POST "https://api.cookify.app/api/auth/verify-email" \
  -H "Content-Type: application/json" \
  -d '{
    "token": "verification_token_from_email"
  }'

# 3. Login
curl -X POST "https://api.cookify.app/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "password": "SecurePassword123!"
  }'
```

### Complete Pantry Management Flow

```bash
# 1. Get auth token (from login response)
TOKEN="eyJ..."

# 2. List pantry items
curl -X GET "https://api.cookify.app/api/pantry/items?page=1&per_page=20" \
  -H "Authorization: Bearer $TOKEN"

# 3. Add new item
curl -X POST "https://api.cookify.app/api/pantry/items" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Fresh Bananas",
    "quantity": 6.0,
    "unit": "pieces",
    "category": "produce",
    "expiry_date": "2025-07-02"
  }'

# 4. Get pantry statistics
curl -X GET "https://api.cookify.app/api/pantry/stats" \
  -H "Authorization: Bearer $TOKEN"
```

### OCR Receipt Processing Flow

```bash
# 1. Process receipt image
curl -X POST "https://api.cookify.app/api/ocr/process" \
  -H "Authorization: Bearer $TOKEN" \
  -F "image=@receipt.jpg"

# 2. Add suggested items to pantry (bulk create)
curl -X POST "https://api.cookify.app/api/pantry/items/bulk" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "items": [
      {
        "name": "Bananas",
        "quantity": 3.0,
        "unit": "pieces",
        "category": "produce",
        "ingredient_id": "550e8400-e29b-41d4-a716-446655440001"
      }
    ]
  }'
```

---

## Changelog

### Version 1.0.0 (Current)

- Initial API release with all core endpoints
- JWT authentication implementation
- Pantry management features
- OCR receipt processing
- Health monitoring endpoints
- Ingredient master data management
- Cache management utilities

---

## Support

For questions or issues with the API:

- **GitHub Issues**: [Cookify Backend Issues](https://github.com/cookify/backend/issues)
- **Email**: api-support@cookify.app
- **Documentation**: Complete documentation in this directory
