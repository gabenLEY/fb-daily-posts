# Facebook User Authentication Setup Guide

This guide shows you how to allow users to connect their own Facebook pages to your app, so each user can get their own `FB_PAGE_ID` and `FB_PAGE_ACCESS_TOKEN` when they login.

## 🚀 Quick Setup

### 1. Create Facebook App

1. Go to [Facebook Developers](https://developers.facebook.com/)
2. Create a new app (choose "Business" type)
3. Add "Facebook Login" product
4. Configure OAuth redirect URIs:
   - `http://127.0.0.1:8000/api/facebook-auth/callback` (development)
   - `https://yourdomain.com/api/facebook-auth/callback` (production)

### 2. Update Environment Variables

Add these to your `.env` file:

```bash
# Facebook App Configuration
FB_APP_ID=your_facebook_app_id_here
FB_APP_SECRET=your_facebook_app_secret_here
FB_REDIRECT_URI=http://127.0.0.1:8000/api/facebook-auth/callback
FRONTEND_URL=http://127.0.0.1:3000
```

### 3. Run Database Migration

```bash
python scripts/migrate_user_facebook.py
```

### 4. Restart Your App

```bash
python app.py
```

## 📱 Frontend Integration

### JavaScript/React Implementation

```javascript
// 1. User clicks "Connect Facebook"
const facebookAuth = new FacebookAuth();
await facebookAuth.redirectToFacebookLogin();

// 2. After redirect back, get user's pages
const pages = await facebookAuth.getUserPages();

// 3. User selects a page
await facebookAuth.selectPage(selectedPageId);

// 4. Now when user posts, it uses their page credentials
```

## 🔄 How It Works

### User Flow:

1. **User Registration/Login**: User creates account in your app
2. **Connect Facebook**: User clicks "Connect Facebook" button
3. **Facebook Authorization**: User authorizes your app to access their pages
4. **Page Selection**: User selects which Facebook page to post to
5. **Post Creation**: When user creates posts, it uses their selected page credentials

### Backend Flow:

1. Generate Facebook login URL with required permissions
2. Handle OAuth callback and exchange code for tokens
3. Fetch user's Facebook pages using their access token
4. Store selected page credentials in user record
5. Use user's page credentials instead of environment variables

## 🔑 New API Endpoints

| Endpoint                                | Method | Description               |
| --------------------------------------- | ------ | ------------------------- |
| `/api/facebook-auth/facebook/login-url` | GET    | Get Facebook login URL    |
| `/api/facebook-auth/callback`           | GET    | Handle OAuth callback     |
| `/api/facebook-auth/pages`              | GET    | Get user's Facebook pages |
| `/api/facebook-auth/select-page`        | POST   | Select page for posting   |
| `/api/facebook-auth/disconnect`         | POST   | Disconnect Facebook       |

## 📊 Data Flow

### User Record (Extended):

```python
class User(db.Model):
    # ... existing fields ...
    facebook_data = db.Column(db.Text)        # JSON with user's FB data
    selected_page_id = db.Column(db.String(50)) # Selected page ID
    selected_page_token = db.Column(db.Text)   # Page access token
```

### Facebook Data Structure:

```json
{
  "user_access_token": "user_token_here",
  "pages": [
    {
      "id": "page_id_123",
      "name": "My Business Page",
      "access_token": "page_token_here",
      "category": "Business",
      "tasks": ["MANAGE", "CREATE_CONTENT"]
    }
  ]
}
```

## 🔒 Security Features

- **State Parameter**: Uses user ID as state for CSRF protection
- **Token Masking**: Page tokens are masked in API responses
- **User Isolation**: Each user can only access their own pages
- **Fallback Support**: Still supports environment variables for backwards compatibility

## 🎯 Benefits

1. **Multi-User Support**: Multiple users can connect different Facebook pages
2. **No Shared Tokens**: Each user has their own page access tokens
3. **Better Security**: No need to share admin tokens with users
4. **User Control**: Users manage their own Facebook connections
5. **Scalable**: Supports unlimited users and pages

## 🛠️ Troubleshooting

### Common Issues:

1. **"Facebook App ID not configured"**

   - Add `FB_APP_ID` to your `.env` file

2. **"Failed to get access token"**

   - Check `FB_APP_SECRET` in `.env`
   - Verify redirect URI matches Facebook app settings

3. **"No pages found"**

   - User might not have admin access to any pages
   - Check Facebook app permissions

4. **Database errors**
   - Run the migration script: `python scripts/migrate_user_facebook.py`

## 📝 Example Frontend Component

See `examples/facebook-login-frontend.js` for a complete React component that handles the entire Facebook login flow.

## 🔄 Migration from Environment Variables

Your existing setup will continue to work! The system now:

1. **First** tries to use user's selected page credentials
2. **Falls back** to environment variables (`FB_PAGE_ID`, `FB_PAGE_ACCESS_TOKEN`)

This means existing functionality is preserved while adding multi-user support.
