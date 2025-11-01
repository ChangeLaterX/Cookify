# Cookify API Documentation

## Overview

This comprehensive documentation describes all available endpoints of the Cookify API with detailed information about:

- **Request/Response formats**
- **Authentication and security**
- **Error handling**
- **Rate limiting**
- **Practical examples**

## 📋 Endpoint Categories

### 🔐 Authentication (`/api/auth`)
- User registration and login
- JWT token management
- Password reset functions
- Profile management
- Email verification

### 🥗 Pantry Management (`/api/pantry`)
- CRUD operations for pantry items
- Bulk operations (create, update, delete)
- Statistics and reports
- Expiry date tracking
- Stock level alerts

### 🩺 Health Monitoring (`/api/health`)
- System health checks
- Service metrics
- Liveness/Readiness probes
- Alert system
- Performance monitoring

### 🌿 Ingredients (`/api/ingredients`)
- Master ingredient list
- Nutritional information
- Search functions
- CRUD for ingredient management

### 📸 OCR Processing (`/api/ocr`)
- Receipt text recognition
- Intelligent ingredient matching
- Image processing
- Shopping list integration

### 🔄 Cache Management (`/api/update`)
- Cache updates
- System maintenance
- Database synchronization

## 🚀 Quick Start

1. **Registration**: `POST /api/auth/register`
2. **Login**: `POST /api/auth/login`
3. **Get pantry items**: `GET /api/pantry/items`
4. **Process receipt**: `POST /api/ocr/process`

## 🔑 Authentication

Most endpoints require JWT Bearer Token:

```http
Authorization: Bearer <your_jwt_token>
```

## 📊 Rate Limiting

- **Auth Endpoints**: 10 requests/minute
- **OCR Endpoints**: 20 requests/hour
- **Other Endpoints**: Standard limits

## 🛡️ Security Features

- JWT-based authentication
- Rate limiting
- Input validation
- Security headers
- CORS configuration

## 📖 Complete Documentation

The complete API documentation with all endpoints, examples, and technical details can be found in:

**[API_Documentation.md](./API_Documentation.md)**

## 🏗️ Architecture

```
Backend (FastAPI)
├── domains/
│   ├── auth/          # Authentication
│   ├── pantry_items/  # Pantry management
│   ├── health/        # System monitoring
│   ├── ingredients/   # Ingredient management
│   ├── ocr/          # Image processing
│   └── update/       # Cache management
├── core/             # Core components
├── middleware/       # Request middleware
└── shared/          # Shared utilities
```

## 🐛 Error Handling

All endpoints use consistent error formats:

```json
{
  "detail": {
    "error": "Error description",
    "error_code": "ERROR_CODE"
  }
}
```

## 📞 Support

- **Issues**: GitHub Repository Issues
- **Email**: support@cookify.app
- **Docs**: Complete documentation in this directory

---

*Last updated: June 2025*
