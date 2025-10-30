# Complete API Reference for Frontend Integration

## Base URL

```
http://127.0.0.1:8000
```

## 🔐 Authentication Header

For protected endpoints, include JWT token:

```javascript
headers: {
  'Authorization': 'Bearer YOUR_JWT_TOKEN_HERE',
  'Content-Type': 'application/json'
}
```

---

## 📍 Health Check Endpoints

### GET `/`

**Description:** Application health check  
**Auth Required:** No

**Response:**

```json
{
  "status": "healthy",
  "message": "FB Daily Posts API is running",
  "version": "2.0.0",
  "architecture": "MVC with Flask-SQLAlchemy and JWT"
}
```

### GET `/health`

**Description:** Simple health status  
**Auth Required:** No

**Response:**

```json
{
  "status": "healthy"
}
```

---

## 🔐 Authentication Endpoints (`/api/auth`)

### POST `/api/auth/register`

**Description:** Register new user  
**Auth Required:** No

**Request Body:**

```json
{
  "username": "johndoe",
  "email": "john@example.com",
  "password": "password123"
}
```

**Success Response (201):**

```json
{
  "success": true,
  "message": "User registered successfully",
  "user": {
    "id": 1,
    "username": "johndoe",
    "email": "john@example.com",
    "is_active": true,
    "created_at": "2025-10-29T14:30:00",
    "updated_at": "2025-10-29T14:30:00"
  },
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Error Response (400):**

```json
{
  "error": "Username must be at least 3 characters"
}
```

### POST `/api/auth/login`

**Description:** User login  
**Auth Required:** No

**Request Body:**

```json
{
  "email": "john@example.com",
  "password": "password123"
}
```

**Success Response (200):**

```json
{
  "success": true,
  "message": "Login successful",
  "user": {
    "id": 1,
    "username": "johndoe",
    "email": "john@example.com",
    "is_active": true,
    "created_at": "2025-10-29T14:30:00",
    "updated_at": "2025-10-29T14:30:00"
  },
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Error Response (401):**

```json
{
  "error": "Invalid credentials"
}
```

### POST `/api/auth/logout`

**Description:** User logout  
**Auth Required:** Yes

**Request Body:** (empty)

```json
{}
```

**Success Response (200):**

```json
{
  "success": true,
  "message": "Logged out successfully"
}
```

### GET `/api/auth/me`

**Description:** Get current user profile  
**Auth Required:** Yes

**Response (200):**

```json
{
  "success": true,
  "user": {
    "id": 1,
    "username": "johndoe",
    "email": "john@example.com",
    "is_active": true,
    "created_at": "2025-10-29T14:30:00",
    "updated_at": "2025-10-29T14:30:00"
  }
}
```

### PUT `/api/auth/me`

**Description:** Update user profile  
**Auth Required:** Yes

**Request Body:**

```json
{
  "username": "newusername",
  "email": "newemail@example.com"
}
```

**Success Response (200):**

```json
{
  "success": true,
  "message": "Profile updated successfully",
  "user": {
    "id": 1,
    "username": "newusername",
    "email": "newemail@example.com",
    "is_active": true,
    "created_at": "2025-10-29T14:30:00",
    "updated_at": "2025-10-29T14:45:00"
  }
}
```

### POST `/api/auth/change-password`

**Description:** Change user password  
**Auth Required:** Yes

**Request Body:**

```json
{
  "current_password": "oldpassword123",
  "new_password": "newpassword456"
}
```

**Success Response (200):**

```json
{
  "success": true,
  "message": "Password changed successfully"
}
```

---

## 📝 Post Management Endpoints (`/api/posts`)

### GET `/api/posts/`

**Description:** Get all user posts  
**Auth Required:** Yes

**Response (200):**

```json
{
  "posts": [
    {
      "id": 1,
      "content": "My first post!",
      "platform": "facebook",
      "status": "published",
      "scheduled_time": null,
      "published_at": "2025-10-29T14:30:00",
      "created_at": "2025-10-29T14:25:00",
      "updated_at": "2025-10-29T14:30:00",
      "media_urls": ["image_url_1"],
      "platform_post_id": "fb_12345",
      "user_id": 1
    }
  ],
  "count": 1
}
```

### POST `/api/posts/`

**Description:** Create new post  
**Auth Required:** Yes

**Request Body:**

```json
{
  "content": "Check out this amazing product!",
  "platform": "facebook",
  "scheduled_time": "2025-10-30T10:00:00Z",
  "media_urls": ["image_url_1", "image_url_2"]
}
```

**Success Response (201):**

```json
{
  "message": "Post created successfully",
  "post": {
    "id": 2,
    "content": "Check out this amazing product!",
    "platform": "facebook",
    "status": "scheduled",
    "scheduled_time": "2025-10-30T10:00:00",
    "published_at": null,
    "created_at": "2025-10-29T14:35:00",
    "updated_at": "2025-10-29T14:35:00",
    "media_urls": ["image_url_1", "image_url_2"],
    "platform_post_id": null,
    "user_id": 1
  }
}
```

### GET `/api/posts/{id}`

**Description:** Get specific post  
**Auth Required:** Yes

**Response (200):**

```json
{
  "post": {
    "id": 1,
    "content": "My first post!",
    "platform": "facebook",
    "status": "published",
    "scheduled_time": null,
    "published_at": "2025-10-29T14:30:00",
    "created_at": "2025-10-29T14:25:00",
    "updated_at": "2025-10-29T14:30:00",
    "media_urls": ["image_url_1"],
    "platform_post_id": "fb_12345",
    "user_id": 1
  }
}
```

### PUT `/api/posts/{id}`

**Description:** Update specific post  
**Auth Required:** Yes

**Request Body:**

```json
{
  "content": "Updated post content",
  "status": "published"
}
```

**Success Response (200):**

```json
{
  "message": "Post updated successfully",
  "post": {
    "id": 1,
    "content": "Updated post content",
    "platform": "facebook",
    "status": "published",
    "scheduled_time": null,
    "published_at": "2025-10-29T14:40:00",
    "created_at": "2025-10-29T14:25:00",
    "updated_at": "2025-10-29T14:40:00",
    "media_urls": ["image_url_1"],
    "platform_post_id": "fb_12345",
    "user_id": 1
  }
}
```

### DELETE `/api/posts/{id}`

**Description:** Delete specific post  
**Auth Required:** Yes

**Success Response (200):**

```json
{
  "message": "Post deleted successfully"
}
```

### GET `/api/posts/scheduled`

**Description:** Get scheduled posts  
**Auth Required:** Yes

**Response (200):**

```json
{
  "posts": [
    {
      "id": 2,
      "content": "Scheduled post",
      "platform": "facebook",
      "status": "scheduled",
      "scheduled_time": "2025-10-30T10:00:00",
      "published_at": null,
      "created_at": "2025-10-29T14:35:00",
      "updated_at": "2025-10-29T14:35:00",
      "media_urls": [],
      "platform_post_id": null,
      "user_id": 1
    }
  ],
  "count": 1
}
```

### GET `/api/posts/published`

**Description:** Get published posts  
**Auth Required:** Yes

**Response (200):**

```json
{
  "posts": [
    {
      "id": 1,
      "content": "Published post",
      "platform": "facebook",
      "status": "published",
      "scheduled_time": null,
      "published_at": "2025-10-29T14:30:00",
      "created_at": "2025-10-29T14:25:00",
      "updated_at": "2025-10-29T14:30:00",
      "media_urls": ["image_url_1"],
      "platform_post_id": "fb_12345",
      "user_id": 1
    }
  ],
  "count": 1
}
```

### POST `/api/posts/{id}/publish`

**Description:** Publish post immediately  
**Auth Required:** Yes

**Request Body:**

```json
{}
```

**Success Response (200):**

```json
{
  "message": "Post published successfully",
  "post": {
    "id": 2,
    "content": "Now published post",
    "platform": "facebook",
    "status": "published",
    "scheduled_time": null,
    "published_at": "2025-10-29T14:45:00",
    "created_at": "2025-10-29T14:35:00",
    "updated_at": "2025-10-29T14:45:00",
    "media_urls": [],
    "platform_post_id": "fb_67890",
    "user_id": 1
  }
}
```

---

## 🤖 Social Media & AI Endpoints (`/api/social`)

### POST `/api/social/generate-prompt` or `/api/prompt` (legacy)

**Description:** Generate AI prompts and captions  
**Auth Required:** Optional

**Request Body:**

```json
{
  "topic": "coffee shop",
  "style": "modern minimalist"
}
```

**Success Response (200):**

```json
{
  "success": true,
  "data": {
    "prompt": "A modern minimalist of coffee shop",
    "captions": ["Check out this coffee shop!", "Amazing coffee shop content"]
  }
}
```

**Error Response (400):**

```json
{
  "error": "Topic is required"
}
```

### POST `/api/social/generate-image` or `/api/generate-image` (legacy)

**Description:** Generate AI images  
**Auth Required:** Optional

**Request Body:**

```json
{
  "prompt": "A beautiful sunset over mountains",
  "size": "1024x1024"
}
```

**Success Response (200):**

```json
{
  "success": true,
  "data": {
    "image_url": "https://via.placeholder.com/1024x1024",
    "b64_image": null
  }
}
```

**Error Response (400):**

```json
{
  "error": "Prompt is required"
}
```

### POST `/api/social/publish-facebook`

**Description:** Publish content to Facebook  
**Auth Required:** Yes

**Request Body:**

```json
{
  "post_id": 123,
  "b64_png": "base64_encoded_image_data",
  "caption": "Check out our new product!",
  "publish_now": true
}
```

**Success Response (200):**

```json
{
  "success": true,
  "message": "Post published successfully",
  "facebook_post_id": "facebook_post_123",
  "post_url": "https://www.facebook.com/facebook_post_123"
}
```

**Error Response (400):**

```json
{
  "error": "Image data is required"
}
```

### POST `/api/social/save-draft`

**Description:** Save post as draft  
**Auth Required:** Yes

**Request Body:**

```json
{
  "content": "Draft post content",
  "image_data": "base64_encoded_image_data",
  "scheduled_time": "2025-10-30T10:00:00Z"
}
```

**Success Response (201):**

```json
{
  "success": true,
  "message": "Draft saved successfully",
  "post": {
    "id": 3,
    "content": "Draft post content",
    "platform": "facebook",
    "status": "draft",
    "scheduled_time": "2025-10-30T10:00:00",
    "published_at": null,
    "created_at": "2025-10-29T14:50:00",
    "updated_at": "2025-10-29T14:50:00",
    "media_urls": ["image_data_present"],
    "platform_post_id": null,
    "user_id": 1
  }
}
```

### POST `/api/social/schedule-post`

**Description:** Schedule post for later  
**Auth Required:** Yes

**Request Body:**

```json
{
  "content": "Scheduled post content",
  "scheduled_time": "2025-10-30T15:00:00Z",
  "image_data": "base64_encoded_image_data"
}
```

**Success Response (201):**

```json
{
  "success": true,
  "message": "Post scheduled successfully",
  "post": {
    "id": 4,
    "content": "Scheduled post content",
    "platform": "facebook",
    "status": "scheduled",
    "scheduled_time": "2025-10-30T15:00:00",
    "published_at": null,
    "created_at": "2025-10-29T14:55:00",
    "updated_at": "2025-10-29T14:55:00",
    "media_urls": ["image_data_present"],
    "platform_post_id": null,
    "user_id": 1
  }
}
```

### GET `/api/social/facebook-config`

**Description:** Check Facebook configuration  
**Auth Required:** Yes

**Response (200):**

```json
{
  "success": true,
  "configured": true,
  "page_id": "your_facebook_page_id"
}
```

---

## 🚨 Error Responses

All endpoints can return these error formats:

### 400 Bad Request

```json
{
  "error": "Missing required fields: content"
}
```

### 401 Unauthorized

```json
{
  "error": "Missing Authorization Header"
}
```

### 404 Not Found

```json
{
  "error": "Post not found"
}
```

### 409 Conflict

```json
{
  "error": "User already exists with this email"
}
```

### 500 Internal Server Error

```json
{
  "error": "Registration failed"
}
```

---

## 📋 Frontend JavaScript Examples

### Authentication Flow

```javascript
// Register
const registerUser = async (userData) => {
  const response = await fetch("http://127.0.0.1:8000/api/auth/register", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(userData),
  });
  const result = await response.json();
  if (result.access_token) {
    localStorage.setItem("token", result.access_token);
  }
  return result;
};

// Login
const loginUser = async (email, password) => {
  const response = await fetch("http://127.0.0.1:8000/api/auth/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });
  const result = await response.json();
  if (result.access_token) {
    localStorage.setItem("token", result.access_token);
  }
  return result;
};
```

### Authenticated Requests

```javascript
const makeAuthenticatedRequest = async (url, options = {}) => {
  const token = localStorage.getItem("token");
  const headers = {
    "Content-Type": "application/json",
    ...options.headers,
  };

  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  return fetch(url, {
    ...options,
    headers,
  });
};

// Get user posts
const getUserPosts = async () => {
  const response = await makeAuthenticatedRequest(
    "http://127.0.0.1:8000/api/posts/"
  );
  return response.json();
};
```

### AI Generation

```javascript
// Generate prompt
const generatePrompt = async (topic, style = "modern minimalist") => {
  const response = await fetch("http://127.0.0.1:8000/api/prompt", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ topic, style }),
  });
  return response.json();
};

// Generate image
const generateImage = async (prompt, size = "1024x1024") => {
  const response = await fetch("http://127.0.0.1:8000/api/generate-image", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ prompt, size }),
  });
  return response.json();
};
```

---

## 🎯 Status Codes Summary

- **200** - Success
- **201** - Created successfully
- **400** - Bad request (validation error)
- **401** - Unauthorized (missing/invalid token)
- **404** - Resource not found
- **409** - Conflict (duplicate data)
- **500** - Internal server error
