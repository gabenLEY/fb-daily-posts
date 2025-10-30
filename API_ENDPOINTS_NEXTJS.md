# Complete API Endpoints for Next.js Frontend

## Base URL

```
http://127.0.0.1:8000
```

## 🔐 User Authentication Endpoints

### 1. Register New User

```javascript
POST / api / user / register;
```

**Request Body:**

```json
{
  "username": "string",
  "email": "string",
  "password": "string",
  "connect_facebook": false
}
```

**Response:**

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
  "next_step": "connect_facebook" // Optional if connect_facebook was true
}
```

---

### 2. Login User

```javascript
POST / api / user / login;
```

**Request Body:**

```json
{
  "username": "john_doe", // Can be username or email
  "password": "password123"
}
```

**Response:**

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

---

### 3. Get User Profile

```javascript
GET / api / user / profile;
```

**Headers:**

```json
{
  "Authorization": "Bearer YOUR_JWT_TOKEN"
}
```

**Response:**

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

---

### 4. Update User Profile

```javascript
PUT / api / user / update - profile;
```

**Headers:**

```json
{
  "Authorization": "Bearer YOUR_JWT_TOKEN"
}
```

**Request Body:**

```json
{
  "username": "new_username", // Optional
  "email": "new@example.com", // Optional
  "password": "newpassword123" // Optional
}
```

---

### 5. Get Facebook Connection Status

```javascript
GET / api / user / facebook - connection - status;
```

**Headers:**

```json
{
  "Authorization": "Bearer YOUR_JWT_TOKEN"
}
```

**Response:**

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

## 📘 Facebook Authentication Endpoints

### 1. Get Facebook Login URL

```javascript
GET / api / facebook - auth / facebook / login - url;
```

**Headers:**

```json
{
  "Authorization": "Bearer YOUR_JWT_TOKEN"
}
```

**Response:**

```json
{
  "success": true,
  "login_url": "https://www.facebook.com/v19.0/dialog/oauth?client_id=..."
}
```

---

### 2. Get User's Facebook Pages

```javascript
GET / api / facebook - auth / pages;
```

**Headers:**

```json
{
  "Authorization": "Bearer YOUR_JWT_TOKEN"
}
```

**Response:**

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

---

### 3. Select Facebook Page

```javascript
POST / api / facebook - auth / select - page;
```

**Headers:**

```json
{
  "Authorization": "Bearer YOUR_JWT_TOKEN"
}
```

**Request Body:**

```json
{
  "page_id": "108496194378505"
}
```

**Response:**

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

---

### 4. Disconnect Facebook

```javascript
POST / api / facebook - auth / disconnect;
```

**Headers:**

```json
{
  "Authorization": "Bearer YOUR_JWT_TOKEN"
}
```

**Response:**

```json
{
  "success": true,
  "message": "Facebook disconnected successfully"
}
```

---

## 📝 Social Media Endpoints (Post Creation)

### 1. Generate Post Content

```javascript
POST / api / social / generate - prompt;
```

**Headers:**

```json
{
  "Authorization": "Bearer YOUR_JWT_TOKEN"
}
```

**Request Body:**

```json
{
  "topic": "AI technology trends",
  "style": "professional",
  "length": "medium"
}
```

---

### 2. Generate Post Image

```javascript
POST / api / social / generate - image;
```

**Headers:**

```json
{
  "Authorization": "Bearer YOUR_JWT_TOKEN"
}
```

**Request Body:**

```json
{
  "prompt": "Modern office with AI technology"
}
```

---

### 3. Create and Publish Post

```javascript
POST / api / social / create - post;
```

**Headers:**

```json
{
  "Authorization": "Bearer YOUR_JWT_TOKEN"
}
```

**Request Body:**

```json
{
  "content": "Check out this amazing AI technology!",
  "image_url": "https://example.com/image.jpg", // Optional
  "scheduled_time": "2025-10-31T09:00:00Z" // Optional
}
```

---

## 🔄 Complete User Flow

### Registration with Facebook Connection:

1. `POST /api/user/register` with `connect_facebook: true`
2. Get `access_token` and redirect to Facebook login URL
3. After Facebook OAuth callback, call `GET /api/facebook-auth/pages`
4. Call `POST /api/facebook-auth/select-page` to choose page
5. Ready to create posts!

### Login with Existing Account:

1. `POST /api/user/login`
2. Get user data with Facebook status
3. If Facebook not connected, call Facebook endpoints
4. Ready to create posts!

### Creating Posts:

1. `POST /api/social/generate-prompt` (optional)
2. `POST /api/social/generate-image` (optional)
3. `POST /api/social/create-post` (uses user's selected Facebook page automatically)

---

## 🛡️ Authentication Flow

1. **Store JWT Token**: After successful login/register, store `access_token` in localStorage
2. **Include in Headers**: Add `Authorization: Bearer TOKEN` to all authenticated requests
3. **Handle Expiration**: If you get 401 responses, redirect to login
4. **Logout**: Remove token from localStorage

---

## 🎯 Ready-to-Use URLs for Next.js

```javascript
// User Authentication
const AUTH_URLS = {
  register: "http://127.0.0.1:8000/api/user/register",
  login: "http://127.0.0.1:8000/api/user/login",
  profile: "http://127.0.0.1:8000/api/user/profile",
  updateProfile: "http://127.0.0.1:8000/api/user/update-profile",
  facebookStatus: "http://127.0.0.1:8000/api/user/facebook-connection-status",
};

// Facebook Integration
const FACEBOOK_URLS = {
  loginUrl: "http://127.0.0.1:8000/api/facebook-auth/facebook/login-url",
  pages: "http://127.0.0.1:8000/api/facebook-auth/pages",
  selectPage: "http://127.0.0.1:8000/api/facebook-auth/select-page",
  disconnect: "http://127.0.0.1:8000/api/facebook-auth/disconnect",
};

// Social Media Posts
const SOCIAL_URLS = {
  generatePrompt: "http://127.0.0.1:8000/api/social/generate-prompt",
  generateImage: "http://127.0.0.1:8000/api/social/generate-image",
  createPost: "http://127.0.0.1:8000/api/social/create-post",
};
```

Your Flask backend is now **fully ready** for Next.js frontend integration! 🚀
