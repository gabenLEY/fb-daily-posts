# FB Daily Posts - API Routes Documentation

## Base URL

- Development: `http://127.0.0.1:8000`
- Production: `https://your-domain.com`

## ✅ Status: All Routes Working

**Server:** `http://127.0.0.1:8000`  
**Last Tested:** October 29, 2025 ✅ **PASSED ALL TESTS**  
**Test Results:**

- ✅ Empty requests → 400 (proper validation)
- ✅ Missing fields → 400 (clear error messages)
- ✅ Valid requests → 200 (successful responses)
- ✅ CORS OPTIONS → 200 (working correctly)

**Issues Resolved:** ✅ `/api/prompt` and `/api/generate-image` compatibility routes fixed

## 🔄 Compatibility Routes (Legacy Support)

For backward compatibility, these old endpoints are redirected to the new structured routes:

| Old Endpoint                  | New Endpoint                          | Status    |
| ----------------------------- | ------------------------------------- | --------- |
| `POST /api/prompt`            | `POST /api/social/generate-prompt`    | ✅ Active |
| `POST /api/generate-image`    | `POST /api/social/generate-image`     | ✅ Active |
| `OPTIONS /api/prompt`         | `OPTIONS /api/social/generate-prompt` | ✅ Active |
| `OPTIONS /api/generate-image` | `OPTIONS /api/social/generate-image`  | ✅ Active |

**Note:** Use the new structured endpoints (`/api/social/*`) for new integrations.

## 📊 Expected Status Codes

| Status Code | Meaning         | Example                                                       |
| ----------- | --------------- | ------------------------------------------------------------- |
| `200`       | ✅ Success      | Valid request with proper data                                |
| `400`       | ⚠️ Bad Request  | Missing required fields (e.g., no `prompt` in generate-image) |
| `401`       | 🔒 Unauthorized | Missing or invalid JWT token                                  |
| `404`       | ❌ Not Found    | Route doesn't exist                                           |
| `500`       | 💥 Server Error | Internal server error                                         |

**Current Behavior:**

- `POST /api/generate-image` with empty data → `400` (expected - needs `prompt` field)
- `OPTIONS /api/generate-image` → `200` (working correctly)

## Health Check

- `GET /` - Application health check
- `GET /health` - Simple health status

## Authentication Routes (`/api/auth`)

All authentication endpoints for user management and JWT tokens.

| Method | Endpoint                    | Description                    | Auth Required |
| ------ | --------------------------- | ------------------------------ | ------------- |
| `POST` | `/api/auth/register`        | Register new user              | No            |
| `POST` | `/api/auth/login`           | User login (returns JWT token) | No            |
| `POST` | `/api/auth/logout`          | User logout                    | Yes           |
| `GET`  | `/api/auth/me`              | Get current user profile       | Yes           |
| `PUT`  | `/api/auth/me`              | Update user profile            | Yes           |
| `POST` | `/api/auth/change-password` | Change user password           | Yes           |

### Example Request Bodies:

**Register:**

```json
{
  "username": "johndoe",
  "email": "john@example.com",
  "password": "password123"
}
```

**Login:**

```json
{
  "email": "john@example.com",
  "password": "password123"
}
```

## Post Management Routes (`/api/posts`)

Manage social media posts and content.

| Method   | Endpoint                  | Description              | Auth Required |
| -------- | ------------------------- | ------------------------ | ------------- |
| `GET`    | `/api/posts/`             | Get all user posts       | Yes           |
| `POST`   | `/api/posts/`             | Create new post          | Yes           |
| `GET`    | `/api/posts/{id}`         | Get specific post by ID  | Yes           |
| `PUT`    | `/api/posts/{id}`         | Update specific post     | Yes           |
| `DELETE` | `/api/posts/{id}`         | Delete specific post     | Yes           |
| `GET`    | `/api/posts/scheduled`    | Get scheduled posts      | Yes           |
| `GET`    | `/api/posts/published`    | Get published posts      | Yes           |
| `POST`   | `/api/posts/{id}/publish` | Publish post immediately | Yes           |

### Example Post Creation:

```json
{
  "content": "Check out this amazing product!",
  "platform": "facebook",
  "scheduled_time": "2025-10-30T10:00:00Z",
  "media_urls": ["image_url_1", "image_url_2"]
}
```

## Social Media & AI Routes (`/api/social`)

AI content generation and social media publishing.

| Method | Endpoint                       | Description                      | Auth Required |
| ------ | ------------------------------ | -------------------------------- | ------------- |
| `POST` | `/api/social/generate-prompt`  | Generate AI prompts and captions | Optional      |
| `POST` | `/api/social/generate-image`   | Generate AI images               | Optional      |
| `POST` | `/api/social/publish-facebook` | Publish content to Facebook      | Yes           |
| `POST` | `/api/social/save-draft`       | Save post as draft               | Yes           |
| `POST` | `/api/social/schedule-post`    | Schedule post for later          | Yes           |
| `GET`  | `/api/social/facebook-config`  | Check Facebook configuration     | Yes           |

### Example AI Generation Requests:

**Generate Prompt:**

```json
{
  "topic": "coffee shop",
  "style": "clean product shot"
}
```

**Generate Image:**

```json
{
  "prompt": "A modern coffee shop with warm lighting",
  "size": "1024x1024"
}
```

**Publish to Facebook:**

```json
{
  "post_id": 123,
  "b64_png": "base64_encoded_image_data",
  "caption": "Check out our new coffee!",
  "publish_now": true
}
```

## Error Responses

All endpoints return consistent error responses:

```json
{
  "error": "Error message description",
  "details": "Additional error details (optional)"
}
```

Common HTTP status codes:

- `200` - Success
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized
- `404` - Not Found
- `409` - Conflict (e.g., user already exists)
- `500` - Internal Server Error

## Authentication

Include JWT token in Authorization header for protected endpoints:

```
Authorization: Bearer your_jwt_token_here
```

## CORS

CORS is enabled for all origins in development. Adjust for production security.

---

**Note:** The endpoint you tried `/api/prompt` should be `/api/social/generate-prompt`
