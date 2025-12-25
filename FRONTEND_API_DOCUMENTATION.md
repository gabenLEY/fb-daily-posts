# Frontend API Documentation

## Base URL

- **Development:** `http://127.0.0.1:8000`
- **Production:** `https://your-domain.com`

## Authentication

Most endpoints require authentication. Include the JWT token in the Authorization header:

```javascript
headers: {
  'Authorization': 'Bearer YOUR_JWT_TOKEN_HERE',
  'Content-Type': 'application/json'
}
```

---

## 🎨 Social Media & AI Endpoints (`/api/social`)

### POST `/api/social/generate-prompt`

Generate AI-powered prompts and captions for your posts.

**Auth Required:** Optional

**Request Body:**
```json
{
  "topic": "Summer Sale",
  "style": "clean product shot"
}
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "prompt": "A clean product shot of Summer Sale with vibrant colors",
    "captions": [
      "Check out our amazing Summer Sale!",
      "Don't miss out on these incredible deals!"
    ]
  }
}
```

**Error Response (400):**
```json
{
  "error": "Topic is required"
}
```

---

### POST `/api/social/generate-image`

Generate professional images and flyers using AI with dynamic watermark support.

**Auth Required:** Optional

**Request Body:**
```json
{
  "prompt": "A professional flyer for Summer Sale with vibrant colors",
  "size": "1024x1792",
  "logo_path": "/path/to/logo.png",
  "logo_url": "https://example.com/logo.png",
  "footer_text": "Your Brand Name"
}
```

**Parameters:**
- `prompt` (required): Image generation prompt
- `size` (optional): Image size - `"1024x1024"`, `"1024x1792"` (portrait flyer), or `"1792x1024"` (landscape flyer). Defaults to `"1024x1792"` for flyers
- `logo_path` (optional): Path to logo file for watermark
- `logo_url` (optional): URL to logo image for watermark
- `footer_text` (optional): Custom footer text for watermark

**Response (200):**
```json
{
  "success": true,
  "data": {
    "imageUrl": "http://localhost:8000/static/abc123.png",
    "b64_png": "data:image/png;base64,iVBORw0KGgoAAAANS...",
    "prompt": "A professional flyer for Summer Sale...",
    "revised_prompt": "A vibrant professional flyer...",
    "size": "1024x1792",
    "model": "gpt-image-1.5"
  }
}
```

**Error Response (400):**
```json
{
  "error": "Prompt is required"
}
```

**Notes:**
- Uses GPT-Image-1.5 (newest model) for professional quality
- Automatically applies watermark with user-provided logo
- Returns base64 image for immediate use
- Optimized for flyer creation

---

### POST `/api/social/publish-facebook`

Publish or schedule a post to Facebook. **Always saves to database.**

**Auth Required:** Yes

**Request Body:**
```json
{
  "post_id": 123,
  "b64_png": "data:image/png;base64,iVBORw0KGgoAAAANS...",
  "caption": "Check out our amazing **Summer Sale**!\n\nDon't miss out!",
  "image_url": "http://localhost:8000/static/abc123.png",
  "title": "Summer Sale Post",
  "publish_now": true
}
```

**Parameters:**
- `post_id` (optional): Existing post ID to update
- `b64_png` (required): Base64 encoded image data
- `caption` (required): Post caption with text formatting support
- `image_url` (optional): URL to the image
- `title` (optional): Post title
- `publish_now` (optional): `true` to publish immediately, `false` to schedule. Defaults to `true`

**Text Formatting Support:**
- Line breaks: Use `\n` for new lines
- The API automatically formats text for Facebook

**Response (200):**
```json
{
  "success": true,
  "message": "Post published successfully",
  "facebook_post_id": "1234567890123456",
  "post_id": 123,
  "post_url": "https://www.facebook.com/1234567890123456",
  "post": {
    "id": 123,
    "user_id": 1,
    "title": "Summer Sale Post",
    "caption": "Check out our amazing **Summer Sale**!...",
    "image_url": "http://localhost:8000/static/abc123.png",
    "facebook_post_id": "1234567890123456",
    "status": "published",
    "published_at": "2024-01-15T09:00:00",
    "created_at": "2024-01-15T08:55:00",
    "updated_at": "2024-01-15T09:00:00"
  }
}
```

**Error Responses:**

**400 - Missing Data:**
```json
{
  "error": "Image data is required"
}
```

**400 - Facebook Not Connected:**
```json
{
  "error": "Facebook page not connected",
  "message": "Please connect your Facebook page first"
}
```

**400 - Facebook API Error:**
```json
{
  "error": "Failed to publish to Facebook",
  "details": "Invalid access token"
}
```

**Notes:**
- If `post_id` is provided, updates existing post
- If `post_id` is not provided, creates new post in database
- Post status is automatically set to `"published"` or `"scheduled"`
- `published_at` timestamp is set when published
- Facebook post ID is stored for reference

---

### POST `/api/social/auto-generate-posts`

**NEW FEATURE:** Auto-generate posts with flexible duration, posting frequency, and AI-powered content generation!

**Auth Required:** Yes

**Request Body:**
```json
{
  "business_context": "Tech Startup - Mobile App Development",
  "style": "modern minimalist",
  "duration_type": "months",
  "duration": 1,
  "posting_frequency": 3,
  "start_date": "2024-01-15T00:00:00Z",
  "default_time": "09:00",
  "daily_topics": [
    "Mobile App Launch",
    "User Success Stories",
    "New Features Update"
  ],
  "logo_path": "/path/to/logo.png",
  "logo_url": "https://example.com/logo.png",
  "footer_text": "Tech Startup"
}
```

**Parameters:**
- `business_context` (required): Main business/page context for auto-generating content
- `style` (optional): Image style. Defaults to `"clean product shot"`
- `duration_type` (optional): `"days"`, `"weeks"`, or `"months"`. Defaults to `"days"`
- `duration` (optional): Number of days/weeks/months. Defaults to `7`
- `posting_frequency` (optional): Post every N days. 
  - `1` = Every day
  - `3` = Every 3 days
  - `5` = Every 5 days
  - Defaults to `1` (daily)
- `start_date` (optional): Start date in ISO format. Defaults to today
- `default_time` (optional): Default publish time (HH:MM format). Defaults to `"09:00"`
- `daily_topics` (optional): Array of specific topics for each post. If not provided, AI auto-generates based on business context
- `logo_path` (optional): Path to logo for watermark
- `logo_url` (optional): URL to logo for watermark
- `footer_text` (optional): Custom footer text

**Response (201):**
```json
{
  "success": true,
  "message": "Generated 10 posts over 30 days",
  "posts": [
    {
      "post_id": 101,
      "post_number": 1,
      "day_offset": 0,
      "scheduled_time": "2024-01-15T09:00:00",
      "topic": "Tech Startup - Tips & Insights",
      "caption": "Check out our amazing Tech Startup content!",
      "image_url": "http://localhost:8000/static/abc123.png"
    },
    {
      "post_id": 102,
      "post_number": 2,
      "day_offset": 3,
      "scheduled_time": "2024-01-18T09:00:00",
      "topic": "Tech Startup - Special Offers",
      "caption": "Don't miss our special offers!",
      "image_url": "http://localhost:8000/static/def456.png"
    }
    // ... more posts
  ],
  "total_generated": 10,
  "total_errors": 0,
  "duration_days": 30,
  "posting_frequency": "Every 3 day(s)",
  "total_posts": 10
}
```

**Error Response (400):**
```json
{
  "error": "Business context is required for auto-generation"
}
```

**Examples:**

**Generate posts for 1 month, posting every day:**
```json
{
  "business_context": "Fitness Coach - Personal Training",
  "duration_type": "months",
  "duration": 1,
  "posting_frequency": 1
}
```
*Result: ~30 posts (one per day for 30 days)*

**Generate posts for 2 weeks, posting every 3 days:**
```json
{
  "business_context": "Restaurant - Italian Cuisine",
  "duration_type": "weeks",
  "duration": 2,
  "posting_frequency": 3
}
```
*Result: ~5 posts (every 3 days for 14 days)*

**Generate posts with custom topics:**
```json
{
  "business_context": "E-commerce Store",
  "duration": 7,
  "posting_frequency": 1,
  "daily_topics": [
    "New Product Launch",
    "Customer Reviews",
    "Flash Sale",
    "Behind the Scenes",
    "Shipping Update",
    "Product Tutorial",
    "Weekend Special"
  ]
}
```
*Result: 7 posts with your specified topics*

**Notes:**
- If `daily_topics` is provided, uses those topics; otherwise AI auto-generates based on business context
- Auto-generated content cycles through different content types (Tips, Offers, Stories, etc.)
- All posts are saved to database with `"scheduled"` status
- Posts are ready to be published automatically
- If some posts fail, they're reported in `errors` array
- Supports flexible durations: days, weeks, or months
- Supports flexible posting frequencies: daily, every 3 days, every 5 days, etc.

---

### POST `/api/social/auto-generate-weekly-posts`

**Legacy Endpoint:** Auto-generate 7 posts for the week (backward compatibility).

**Auth Required:** Yes

**Request Body:**
```json
{
  "topic": "Weekly Tech Tips",
  "style": "modern minimalist",
  "start_date": "2024-01-15T00:00:00Z",
  "default_time": "09:00"
}
```

**Note:** This endpoint is kept for backward compatibility. It internally calls `/api/social/auto-generate-posts` with:
- `duration_type`: `"weeks"`
- `duration`: `1`
- `posting_frequency`: `1`
- `business_context`: Uses `topic` parameter

**Recommendation:** Use `/api/social/auto-generate-posts` for new integrations.

---

### POST `/api/social/save-draft`

Save a post as draft without publishing.

**Auth Required:** Yes

**Request Body:**
```json
{
  "caption": "Draft post content",
  "title": "My Draft Post",
  "image_data": "data:image/png;base64,iVBORw0KGgoAAAANS...",
  "image_url": "http://localhost:8000/static/abc123.png",
  "scheduled_time": "2024-01-20T10:00:00Z"
}
```

**Response (201):**
```json
{
  "success": true,
  "message": "Draft saved successfully",
  "post": {
    "id": 124,
    "user_id": 1,
    "title": "My Draft Post",
    "caption": "Draft post content",
    "status": "draft",
    "created_at": "2024-01-15T10:00:00"
  }
}
```

---

### POST `/api/social/schedule-post`

Schedule a post for later publishing.

**Auth Required:** Yes

**Request Body:**
```json
{
  "caption": "Scheduled post content",
  "title": "Scheduled Post",
  "image_data": "data:image/png;base64,iVBORw0KGgoAAAANS...",
  "image_url": "http://localhost:8000/static/abc123.png",
  "scheduled_time": "2024-01-20T10:00:00Z"
}
```

**Response (201):**
```json
{
  "success": true,
  "message": "Post scheduled successfully",
  "post": {
    "id": 125,
    "status": "scheduled",
    "scheduled_time": "2024-01-20T10:00:00"
  }
}
```

**Error Response (400):**
```json
{
  "error": "Scheduled time must be in the future"
}
```

---

### GET `/api/social/facebook-config`

Get Facebook configuration status.

**Auth Required:** Yes

**Response (200):**
```json
{
  "success": true,
  "configured": true,
  "page_id": "123456789012345"
}
```

---

## 📝 Post Management Endpoints (`/api/posts`)

### GET `/api/posts/`

Get all posts for the authenticated user.

**Auth Required:** Yes

**Query Parameters:**
- `status` (optional): Filter by status (`draft`, `scheduled`, `published`, `failed`)
- `limit` (optional): Number of posts to return. Default: 50
- `offset` (optional): Pagination offset. Default: 0

**Response (200):**
```json
{
  "posts": [
    {
      "id": 123,
      "user_id": 1,
      "title": "Summer Sale Post",
      "caption": "Check out our amazing sale!",
      "image_url": "http://localhost:8000/static/abc123.png",
      "facebook_post_id": "1234567890123456",
      "status": "published",
      "published_at": "2024-01-15T09:00:00",
      "created_at": "2024-01-15T08:55:00"
    }
  ],
  "count": 1
}
```

---

### POST `/api/posts/`

Create a new post.

**Auth Required:** Yes

**Request Body:**
```json
{
  "caption": "New post content",
  "title": "My New Post",
  "image_url": "http://localhost:8000/static/abc123.png",
  "image_data": "data:image/png;base64,iVBORw0KGgoAAAANS...",
  "scheduled_time": "2024-01-20T10:00:00Z"
}
```

**Response (201):**
```json
{
  "message": "Post created successfully",
  "post": {
    "id": 126,
    "caption": "New post content",
    "status": "draft",
    "created_at": "2024-01-15T10:00:00"
  }
}
```

---

### GET `/api/posts/{id}`

Get a specific post by ID.

**Auth Required:** Yes

**Response (200):**
```json
{
  "post": {
    "id": 123,
    "caption": "Post content",
    "status": "published",
    "facebook_post_id": "1234567890123456"
  }
}
```

---

### PUT `/api/posts/{id}`

Update a specific post.

**Auth Required:** Yes

**Request Body:**
```json
{
  "caption": "Updated post content",
  "title": "Updated Title",
  "status": "published"
}
```

**Response (200):**
```json
{
  "message": "Post updated successfully",
  "post": {
    "id": 123,
    "caption": "Updated post content"
  }
}
```

---

### DELETE `/api/posts/{id}`

Delete a specific post.

**Auth Required:** Yes

**Response (200):**
```json
{
  "message": "Post deleted successfully"
}
```

---

## 🔐 Authentication Endpoints (`/api/auth`)

### POST `/api/auth/register`

Register a new user.

**Auth Required:** No

**Request Body:**
```json
{
  "username": "johndoe",
  "email": "john@example.com",
  "password": "password123"
}
```

**Response (201):**
```json
{
  "success": true,
  "message": "User registered successfully",
  "user": {
    "id": 1,
    "username": "johndoe",
    "email": "john@example.com"
  },
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

---

### POST `/api/auth/login`

User login.

**Auth Required:** No

**Request Body:**
```json
{
  "email": "john@example.com",
  "password": "password123"
}
```

**Response (200):**
```json
{
  "success": true,
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "id": 1,
    "username": "johndoe",
    "email": "john@example.com"
  }
}
```

---

### GET `/api/auth/me`

Get current user profile.

**Auth Required:** Yes

**Response (200):**
```json
{
  "user": {
    "id": 1,
    "username": "johndoe",
    "email": "john@example.com",
    "is_active": true
  }
}
```

---

## 📊 Post Status Values

Posts can have the following statuses:

- `draft`: Post is saved but not published
- `scheduled`: Post is scheduled for future publishing
- `published`: Post has been published to Facebook
- `failed`: Post publishing failed

---

## 🎯 Complete Workflow Examples

### Example 1: Generate and Publish a Single Post

```javascript
// Step 1: Generate prompt
const promptResponse = await fetch('/api/social/generate-prompt', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    topic: 'Summer Sale',
    style: 'vibrant'
  })
});
const { data: { prompt, captions } } = await promptResponse.json();

// Step 2: Generate image with custom logo
const imageResponse = await fetch('/api/social/generate-image', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    prompt: prompt,
    size: '1024x1792',
    logo_url: 'https://example.com/logo.png',
    footer_text: 'My Brand'
  })
});
const { data: { b64_png, imageUrl } } = await imageResponse.json();

// Step 3: Publish to Facebook
const publishResponse = await fetch('/api/social/publish-facebook', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`
  },
  body: JSON.stringify({
    b64_png: b64_png,
    caption: captions[0],
    image_url: imageUrl,
    publish_now: true
  })
});
const { post_id, facebook_post_id } = await publishResponse.json();
```

### Example 2: Auto-Generate Posts for a Month (Every 3 Days)

```javascript
const monthlyResponse = await fetch('/api/social/auto-generate-posts', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`
  },
  body: JSON.stringify({
    business_context: 'Fitness Coach - Personal Training',
    style: 'energetic and motivational',
    duration_type: 'months',
    duration: 1,
    posting_frequency: 3,  // Every 3 days
    start_date: '2024-01-15T00:00:00Z',
    default_time: '09:00',
    logo_url: 'https://example.com/logo.png',
    footer_text: 'FitLife Coaching'
  })
});

const { posts, total_generated, duration_days } = await monthlyResponse.json();
console.log(`Generated ${total_generated} posts over ${duration_days} days!`);
```

### Example 3: Auto-Generate Posts with Custom Topics

```javascript
const customResponse = await fetch('/api/social/auto-generate-posts', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`
  },
  body: JSON.stringify({
    business_context: 'Restaurant - Italian Cuisine',
    duration: 14,  // 14 days
    posting_frequency: 2,  // Every 2 days
    daily_topics: [
      'Monday Special: Pasta Night',
      'Chef\'s Recommendation',
      'Wine Pairing Tips',
      'Customer Favorite: Margherita Pizza',
      'Behind the Scenes: Kitchen Tour',
      'Weekend Brunch Menu',
      'Italian Cooking Class'
    ],
    logo_url: 'https://example.com/logo.png'
  })
});

const { posts } = await customResponse.json();
console.log('Generated posts with custom topics!');
```

---

## ⚠️ Error Handling

All endpoints return consistent error responses:

```json
{
  "error": "Error message here"
}
```

Common HTTP status codes:
- `200`: Success
- `201`: Created
- `400`: Bad Request (validation error)
- `401`: Unauthorized (missing/invalid token)
- `404`: Not Found
- `500`: Internal Server Error

---

## 🔄 Compatibility Endpoints

For backward compatibility, these legacy endpoints are still available:

- `POST /api/prompt` → `POST /api/social/generate-prompt`
- `POST /api/generate-image` → `POST /api/social/generate-image`

**Note:** Use the new `/api/social/*` endpoints for new integrations.

---

## 📝 Notes for Frontend Team

1. **Image Generation:**
   - Always use base64 images (`b64_png`) for immediate display
   - Image URLs are also provided for caching
   - Default size is optimized for flyers (1024x1792)

2. **Watermark:**
   - Logo can be provided via `logo_path` (file path) or `logo_url` (URL)
   - Footer text is customizable
   - If not provided, uses environment defaults

3. **Post Publishing:**
   - Posts are **always saved to database** when published
   - Status is automatically updated
   - Facebook post ID is stored for reference

4. **Auto-Generate Posts:**
   - Flexible duration: days, weeks, or months
   - Flexible posting frequency: every day, every 3 days, every 5 days, etc.
   - Auto-generates content based on business context
   - Can use custom topics if provided
   - All posts are scheduled (not published immediately)
   - Each post has unique AI-generated content

5. **Text Formatting:**
   - Facebook supports basic formatting
   - Use `\n` for line breaks
   - API handles formatting automatically

---

## 🚀 Quick Start

1. **Register/Login** to get JWT token
2. **Generate prompt** for your content
3. **Generate image** with custom watermark
4. **Publish to Facebook** (automatically saves to database)
5. Or use **auto-generate-weekly-posts** for bulk content creation

---

**Last Updated:** January 2024  
**API Version:** 2.0.0

