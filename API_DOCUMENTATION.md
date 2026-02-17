# API Documentation

Base URL: `http://localhost:8000/api`

## Authentication

All endpoints except public product listing require JWT authentication.

Include the token in the Authorization header:
```
Authorization: Bearer <access_token>
```

### Register
```http
POST /auth/register/
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123",
  "first_name": "John",
  "last_name": "Doe",
  "business_name": "My Business"
}

Response: 201 Created
{
  "user": {
    "id": 1,
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "role": "admin",
    "business": 1,
    "business_name": "My Business"
  },
  "tokens": {
    "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
  }
}
```

### Login
```http
POST /auth/login/
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123"
}

Response: 200 OK
{
  "user": { ... },
  "tokens": {
    "access": "...",
    "refresh": "..."
  }
}
```

### Refresh Token
```http
POST /auth/token/refresh/
Content-Type: application/json

{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}

Response: 200 OK
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### Get Current User
```http
GET /auth/me/
Authorization: Bearer <token>

Response: 200 OK
{
  "id": 1,
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "role": "admin",
  "business": 1,
  "business_name": "My Business"
}
```

## Products

### List Products (Internal)
```http
GET /products/
Authorization: Bearer <token>

Response: 200 OK
{
  "count": 10,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "Product Name",
      "description": "Product description",
      "price": "99.99",
      "status": "approved",
      "business": 1,
      "business_name": "My Business",
      "created_by": 1,
      "created_by_email": "user@example.com",
      "approved_by": 2,
      "approved_by_email": "approver@example.com",
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z",
      "approved_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

### List Products (Public)
```http
GET /products/?public=true

Response: 200 OK
[
  {
    "id": 1,
    "name": "Product Name",
    "description": "Product description",
    "price": "99.99",
    "status": "approved",
    "business_name": "My Business"
  }
]
```

### Create Product
```http
POST /products/
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "New Product",
  "description": "Product description",
  "price": "49.99"
}

Response: 201 Created
{
  "id": 2,
  "name": "New Product",
  "description": "Product description",
  "price": "49.99",
  "status": "draft",
  "business": 1,
  "created_by": 1,
  ...
}
```

### Get Product
```http
GET /products/{id}/
Authorization: Bearer <token>

Response: 200 OK
{
  "id": 1,
  "name": "Product Name",
  ...
}
```

### Update Product
```http
PUT /products/{id}/
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "Updated Product Name",
  "description": "Updated description",
  "price": "59.99"
}

Response: 200 OK
```

### Delete Product
```http
DELETE /products/{id}/
Authorization: Bearer <token>

Response: 204 No Content
```

### Submit for Approval
```http
POST /products/{id}/submit_for_approval/
Authorization: Bearer <token>

Response: 200 OK
{
  "id": 1,
  "status": "pending_approval",
  ...
}
```

### Approve Product
```http
POST /products/{id}/approve/
Authorization: Bearer <token>

Response: 200 OK
{
  "id": 1,
  "status": "approved",
  "approved_by": 2,
  "approved_at": "2024-01-01T00:00:00Z",
  ...
}
```

## Business Management

### List Businesses
```http
GET /auth/businesses/
Authorization: Bearer <token>

Response: 200 OK
[
  {
    "id": 1,
    "name": "My Business",
    "description": "",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
  }
]
```

### Create Business
```http
POST /auth/businesses/
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "New Business",
  "description": "Business description"
}

Response: 201 Created
```

## User Management

### List Users
```http
GET /auth/users/
Authorization: Bearer <token>

Response: 200 OK
[
  {
    "id": 1,
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "role": "admin",
    "business": 1,
    "business_name": "My Business",
    "is_active": true
  }
]
```

### Create User
```http
POST /auth/users/
Authorization: Bearer <token>
Content-Type: application/json

{
  "email": "newuser@example.com",
  "password": "password123",
  "first_name": "Jane",
  "last_name": "Smith",
  "role": "editor",
  "business": 1
}

Response: 201 Created
```

## AI Chatbot

### Send Message
```http
POST /chatbot/query/
Authorization: Bearer <token>
Content-Type: application/json

{
  "message": "What products are available?"
}

Response: 200 OK
{
  "message": "What products are available?",
  "response": "We currently have the following products available: ...",
  "id": 1
}
```

### Get Chat History
```http
GET /chatbot/history/
Authorization: Bearer <token>

Response: 200 OK
[
  {
    "id": 1,
    "user_message": "What products are available?",
    "ai_response": "We currently have...",
    "created_at": "2024-01-01T00:00:00Z"
  }
]
```

## Error Responses

### 400 Bad Request
```json
{
  "error": "Invalid input",
  "details": { ... }
}
```

### 401 Unauthorized
```json
{
  "detail": "Authentication credentials were not provided."
}
```

### 403 Forbidden
```json
{
  "error": "You don't have permission to perform this action"
}
```

### 404 Not Found
```json
{
  "detail": "Not found."
}
```

### 500 Internal Server Error
```json
{
  "error": "Internal server error"
}
```

## Permissions Matrix

| Role | Create Product | Edit Product | Approve Product | Delete Product | View All |
|------|---------------|--------------|-----------------|----------------|----------|
| Admin | ✅ | ✅ | ✅ | ✅ | ✅ |
| Editor | ✅ | ✅ | ❌ | ❌ | ✅ |
| Approver | ❌ | ❌ | ✅ | ❌ | ✅ |
| Viewer | ❌ | ❌ | ❌ | ❌ | ✅ |

## Rate Limiting

Currently not implemented. Consider adding rate limiting for production.

## Pagination

List endpoints support pagination with `page` and `page_size` parameters:

```http
GET /products/?page=2&page_size=10
```
