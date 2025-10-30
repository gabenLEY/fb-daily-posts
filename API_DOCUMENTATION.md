# API Documentation

Complete REST API documentation for the FB Daily Posts platform.

## Base URL

```
http://127.0.0.1:8000
```

## Authentication

All authenticated endpoints require a JWT token in the Authorization header:

```
Authorization: Bearer <jwt_token>
```

## Response Format

All responses follow this format:

```json
{
  "success": true|false,
  "message": "Human readable message",
  "data": {}, // Response data (varies by endpoint)
  "error": "Error message" // Only present on errors
}
```

## Error Codes

- `400` - Bad Request (validation errors)
- `401` - Unauthorized (invalid/missing token)
- `404` - Not Found
- `409` - Conflict (duplicate data)
- `500` - Internal Server Error

---

## User Authentication Endpoints

### Register User

Create a new user account.

**Endpoint**: `POST /api/user/register`

**Request Body**:

```json
{
  "username": "string (required)",
  "email": "string (required, valid email)",
  "password": "string (required, min 6 chars)",
  "connect_facebook": "boolean (optional, default false)"
}
```

**Response** (201):

```json
{
  "success": true,
  "message": "User registered successfully",
  "user": {
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com",
    "facebook_connected": false
  },
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "next_step": "connect_facebook" // Only if connect_facebook is true
}
```

**Error Responses**:

- `400` - Missing required fields, invalid email, weak password
- `409` - Username or email already exists

---

### Login User

Authenticate an existing user.

**Endpoint**: `POST /api/user/login`

**Request Body**:

```json
{
  "username": "string (required, username or email)",
  "password": "string (required)"
}
```

**Response** (200):

```json
{
  "success": true,
  "message": "Login successful",
  "user": {
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com",
    "facebook_connected": true,
    "selected_page_id": "108496194378505",
    "facebook_pages": [
      {
        "id": "108496194378505",
        "name": "My Business Page",
        "category": "Business"
      }
    ]
  },
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Error Responses**:

- `400` - Missing credentials
- `401` - Invalid credentials or inactive account

---

### Get User Profile

Get current user's profile information.

**Endpoint**: `GET /api/user/profile`

**Headers**: `Authorization: Bearer <jwt_token>`

**Response** (200):

```json
{
  "success": true,
  "user": {
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com",
    "facebook_connected": true,
    "selected_page_id": "108496194378505",
    "facebook_pages": [...],
    "created_at": "2025-10-30T10:00:00",
    "updated_at": "2025-10-30T10:00:00"
  }
}
```

**Error Responses**:

- `401` - Invalid token
- `404` - User not found

---

### Update User Profile

Update user profile information.

**Endpoint**: `PUT /api/user/update-profile`

**Headers**: `Authorization: Bearer <jwt_token>`

**Request Body**:

```json
{
  "username": "string (optional)",
  "email": "string (optional, valid email)",
  "password": "string (optional, min 6 chars)"
}
```

**Response** (200):

```json
{
  "success": true,
  "message": "Profile updated successfully",
  "user": {
    "id": 1,
    "username": "new_username",
    "email": "new@example.com",
    "facebook_connected": true
  }
}
```

**Error Responses**:

- `400` - Invalid data, weak password
- `401` - Invalid token
- `409` - Username/email already taken

---

### Get Facebook Connection Status

Check user's Facebook connection status.

**Endpoint**: `GET /api/user/facebook-connection-status`

**Headers**: `Authorization: Bearer <jwt_token>`

**Response** (200):

```json
{
  "success": true,
  "facebook_connected": true,
  "selected_page_id": "108496194378505",
  "facebook_pages": [...],
  "next_step": "ready_to_post" // or "connect_facebook"
}
```

---

## Facebook Authentication Endpoints

### Get Facebook Login URL

Generate Facebook OAuth login URL.

**Endpoint**: `GET /api/facebook-auth/facebook/login-url`

**Headers**: `Authorization: Bearer <jwt_token>`

**Response** (200):

```json
{
  "success": true,
  "login_url": "https://www.facebook.com/v19.0/dialog/oauth?client_id=..."
}
```

**Error Responses**:

- `401` - Invalid token
- `500` - Facebook App ID not configured

---

### Facebook OAuth Callback

Handle Facebook OAuth callback (called by Facebook).

**Endpoint**: `GET /api/facebook-auth/callback`

**Query Parameters**:

- `code` - Authorization code from Facebook
- `state` - User ID for security

**Response**: Redirects to frontend with success/error status

---

### Get User's Facebook Pages

Get list of Facebook pages user can manage.

**Endpoint**: `GET /api/facebook-auth/pages`

**Headers**: `Authorization: Bearer <jwt_token>`

**Response** (200):

```json
{
  "success": true,
  "pages": [
    {
      "id": "108496194378505",
      "name": "My Business Page",
      "category": "Business",
      "access_token": "hidden_for_security"
    }
  ]
}
```

**Error Responses**:

- `400` - Facebook not connected
- `401` - Invalid token

---

### Select Facebook Page

Choose which Facebook page to use for posting.

**Endpoint**: `POST /api/facebook-auth/select-page`

**Headers**: `Authorization: Bearer <jwt_token>`

**Request Body**:

```json
{
  "page_id": "string (required)"
}
```

**Response** (200):

```json
{
  "success": true,
  "message": "Page selected successfully",
  "selected_page": {
    "id": "108496194378505",
    "name": "My Business Page"
  }
}
```

**Error Responses**:

- `400` - Missing page_id or invalid page
- `401` - Invalid token

---

### Disconnect Facebook

Remove Facebook connection from user account.

**Endpoint**: `POST /api/facebook-auth/disconnect`

**Headers**: `Authorization: Bearer <jwt_token>`

**Response** (200):

```json
{
  "success": true,
  "message": "Facebook disconnected successfully"
}
```

---

## Social Media Content Endpoints

### Generate Text Content

Generate AI-powered text content for posts.

**Endpoint**: `POST /api/social/generate-prompt`

**Headers**: `Authorization: Bearer <jwt_token>`

**Request Body**:

```json
{
  "topic": "string (required)",
  "style": "string (optional: professional, casual, creative)",
  "length": "string (optional: short, medium, long)",
  "audience": "string (optional)"
}
```

**Response** (200):

```json
{
  "success": true,
  "content": "Generated text content here...",
  "metadata": {
    "word_count": 45,
    "style": "professional",
    "topic": "AI technology"
  }
}
```

---

### Generate Image

Generate AI-powered images for posts.

**Endpoint**: `POST /api/social/generate-image`

**Headers**: `Authorization: Bearer <jwt_token>`

**Request Body**:

```json
{
  "prompt": "string (required)",
  "size": "string (optional: 1024x1024, 512x512)",
  "style": "string (optional)"
}
```

**Response** (200):

```json
{
  "success": true,
  "image_url": "https://example.com/generated-image.jpg",
  "metadata": {
    "size": "1024x1024",
    "prompt": "Modern office with AI technology",
    "model": "dall-e-3"
  }
}
```

---

### Create and Publish Post

Create and optionally publish a social media post.

**Endpoint**: `POST /api/social/create-post`

**Headers**: `Authorization: Bearer <jwt_token>`

**Request Body**:

```json
{
  "content": "string (required)",
  "image_url": "string (optional)",
  "scheduled_time": "string (optional, ISO format)",
  "publish_immediately": "boolean (optional, default false)"
}
```

**Response** (200):

```json
{
  "success": true,
  "message": "Post created successfully",
  "post": {
    "id": 123,
    "content": "Post content here...",
    "image_url": "https://example.com/image.jpg",
    "facebook_post_id": "page_id_post_id",
    "status": "published",
    "created_at": "2025-10-30T10:00:00"
  }
}
```

**Error Responses**:

- `400` - Missing content, invalid data
- `401` - Invalid token
- `403` - Facebook page not selected

---

## Health and Status Endpoints

### Health Check

Check if the API is running.

**Endpoint**: `GET /`

**Response** (200):

```json
{
  "status": "healthy",
  "message": "FB Daily Posts API is running",
  "version": "2.0.0",
  "architecture": "MVC with Flask-SQLAlchemy and JWT"
}
```

---

### Simple Health Check

Simplified health check endpoint.

**Endpoint**: `GET /health`

**Response** (200):

```json
{
  "status": "healthy"
}
```

---

## Legacy Compatibility Endpoints

These endpoints are maintained for backward compatibility:

### Legacy Prompt Generation

**Endpoint**: `POST /api/prompt`

Redirects to: `POST /api/social/generate-prompt`

### Legacy Image Generation

**Endpoint**: `POST /api/generate-image`

Redirects to: `POST /api/social/generate-image`

---

## Rate Limiting

- **General**: 100 requests per minute per IP
- **AI Generation**: 10 requests per minute per user
- **Facebook Posts**: 5 posts per hour per user

## CORS

Cross-Origin Resource Sharing is enabled for all origins in development mode.

Production deployments should configure specific allowed origins.

## Webhook Support

The application supports Facebook webhook events for real-time updates.

**Webhook URL**: `/api/facebook-auth/webhook`

**Supported Events**:

- Page post updates
- Message events
- Engagement notifications

---

## Examples

### Complete User Flow with cURL

```bash
# 1. Register user
curl -X POST http://127.0.0.1:8000/api/user/register \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","email":"test@example.com","password":"password123"}'

# 2. Login (get token from register response)
curl -X POST http://127.0.0.1:8000/api/user/login \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"password123"}'

# 3. Get Facebook login URL
curl -X GET http://127.0.0.1:8000/api/facebook-auth/facebook/login-url \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# 4. Generate content
curl -X POST http://127.0.0.1:8000/api/social/generate-prompt \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"topic":"AI technology","style":"professional"}'

# 5. Create post
curl -X POST http://127.0.0.1:8000/api/social/create-post \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"content":"Amazing AI technology trends!","publish_immediately":true}'
```

### JavaScript/Next.js Example

```javascript
const API_BASE = "http://127.0.0.1:8000";

// Register user
const registerUser = async (userData) => {
  const response = await fetch(`${API_BASE}/api/user/register`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(userData),
  });
  return response.json();
};

// Login user
const loginUser = async (credentials) => {
  const response = await fetch(`${API_BASE}/api/user/login`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(credentials),
  });
  return response.json();
};

// Get Facebook login URL
const getFacebookLoginUrl = async (token) => {
  const response = await fetch(
    `${API_BASE}/api/facebook-auth/facebook/login-url`,
    {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    }
  );
  return response.json();
};

// Create post
const createPost = async (token, postData) => {
  const response = await fetch(`${API_BASE}/api/social/create-post`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify(postData),
  });
  return response.json();
};
```

---

**Last Updated**: October 30, 2025  
**API Version**: 2.0.0  
**Documentation Version**: 1.0
