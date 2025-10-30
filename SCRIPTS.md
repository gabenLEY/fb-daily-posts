# Scripts Documentation

This document provides detailed information about all scripts in the `scripts/` folder.

## 📋 Table of Contents

- [Setup Scripts](#setup-scripts)
- [Migration Scripts](#migration-scripts)
- [Test Scripts](#test-scripts)
- [Configuration Scripts](#configuration-scripts)
- [Utility Scripts](#utility-scripts)
- [Debug Scripts](#debug-scripts)
- [Legacy Scripts](#legacy-scripts)

---

## 🛠 Setup Scripts

### `setup_database.sql`

**Purpose**: Creates PostgreSQL database and user for the application.

**Usage**:

```bash
psql -U postgres -f scripts/setup_database.sql
```

**What it does**:

- Creates `fb_posts_user` database user
- Creates `fb_posts_db` database
- Grants necessary permissions
- Sets up schema privileges

**Prerequisites**: PostgreSQL installed and running

---

## 🔄 Migration Scripts

### `migrate_user_facebook.py`

**Purpose**: Adds Facebook integration fields to existing User table.

**Usage**:

```bash
python scripts/migrate_user_facebook.py
```

**What it does**:

- Adds `facebook_data` column (TEXT)
- Adds `selected_page_id` column (VARCHAR(50))
- Adds `selected_page_token` column (TEXT)
- Checks for existing columns before adding

**Output**:

```
🔄 Starting User table migration...
✅ Added facebook_data column
✅ Added selected_page_id column
✅ Added selected_page_token column
🎉 User table migration completed successfully!
```

---

## 🧪 Test Scripts

### `test_user_auth.py`

**Purpose**: Tests complete user authentication flow.

**Usage**:

```bash
python scripts/test_user_auth.py
```

**Tests**:

- User registration
- User login
- Profile retrieval
- Facebook connection status

**Sample Output**:

```
🚀 User Authentication Test Suite
==================================================
🧪 Testing User Registration
✅ Login successful, got token
🧪 Testing Get Profile
Status Code: 200
✅ Authentication tests completed successfully!
```

### `test_facebook_auth.py`

**Purpose**: Tests Facebook authentication endpoints.

**Usage**:

```bash
python scripts/test_facebook_auth.py
```

**Tests**:

- Facebook login URL generation
- Facebook pages retrieval
- JWT token validation

**Sample Output**:

```
🚀 Facebook Authentication Test Suite
==================================================
✅ Facebook login URL generated successfully!
🔗 URL: https://www.facebook.com/v19.0/dialog/oauth?client_id=...
```

### `test_openai_debug.py`

**Purpose**: Tests OpenAI DALL-E image generation.

**Usage**:

```bash
python scripts/test_openai_debug.py
```

**Tests**:

- OpenAI API connection
- Image generation with different prompts
- Response format validation
- Error handling

### `test_debug.py`

**Purpose**: General API endpoint testing.

**Usage**:

```bash
python scripts/test_debug.py
```

**Tests**:

- Health check endpoint
- Basic API connectivity
- Response format validation

---

## ⚙️ Configuration Scripts

### `check_facebook_config.py`

**Purpose**: Comprehensive Facebook implementation configuration check.

**Usage**:

```bash
python scripts/check_facebook_config.py
```

**Checks**:

- Environment variables (FB_APP_ID, FB_APP_SECRET, etc.)
- Database migration status
- Facebook endpoints functionality
- Overall configuration completeness

**Sample Output**:

```
🚀 Facebook Authentication Implementation Check
==================================================
📋 Environment Variables:
  FB_APP_ID: ✅ Set
  FB_APP_SECRET: ✅ Set
  FB_REDIRECT_URI: ✅ Set

🎯 Overall Status: ✅ Ready for Facebook Login
```

### `verify_facebook.py`

**Purpose**: Verifies Facebook API connectivity and permissions.

**Usage**:

```bash
python scripts/verify_facebook.py
```

**Verifies**:

- Facebook page access token validity
- Required permissions
- Page information retrieval
- Posting capabilities

---

## 🔧 Utility Scripts

### `run_daily.py`

**Purpose**: Automated daily post creation and publishing.

**Usage**:

```bash
python scripts/run_daily.py
```

**Features**:

- Generates AI content
- Creates social media posts
- Handles scheduling
- Error logging and recovery

**Configuration**: Uses environment variables for timing and content settings.

### `facebook_fallback.py`

**Purpose**: Tests admin fallback functionality when users haven't connected Facebook.

**Usage**:

```bash
python scripts/facebook_fallback.py
```

**Tests**:

- Admin credentials usage
- Fallback posting mechanism
- Error handling for missing user credentials

---

## 🐛 Debug Scripts

### `test_facebook_debug.py`

**Purpose**: Detailed Facebook API debugging.

**Usage**:

```bash
python scripts/test_facebook_debug.py
```

**Debug Features**:

- Detailed API response logging
- Permission verification
- Token validation
- Error analysis

### `test_image_debug.py`

**Purpose**: Image generation debugging and testing.

**Usage**:

```bash
python scripts/test_image_debug.py
```

**Debug Features**:

- OpenAI API response analysis
- Image URL validation
- Generation parameter testing
- Error handling verification

### `test_openai_response.py`

**Purpose**: OpenAI API response format testing.

**Usage**:

```bash
python scripts/test_openai_response.py
```

**Tests**:

- Response structure validation
- Different model responses
- Error response handling
- API key validation

---

## 🔍 Specialized Test Scripts

### `test_facebook_400.py`

**Purpose**: Tests Facebook API error handling (400 errors).

**Usage**:

```bash
python scripts/test_facebook_400.py
```

### `test_facebook_detailed.py`

**Purpose**: Comprehensive Facebook integration testing.

**Usage**:

```bash
python scripts/test_facebook_detailed.py
```

### `test_facebook_perms.py`

**Purpose**: Facebook permissions and scope testing.

**Usage**:

```bash
python scripts/test_facebook_perms.py
```

### `test_fixed_facebook.py`

**Purpose**: Tests specific Facebook fixes and improvements.

**Usage**:

```bash
python scripts/test_fixed_facebook.py
```

### `test_immediate_publish.py`

**Purpose**: Tests immediate post publishing functionality.

**Usage**:

```bash
python scripts/test_immediate_publish.py
```

### `test_modern_fb.py`

**Purpose**: Tests modern Facebook API features.

**Usage**:

```bash
python scripts/test_modern_fb.py
```

### `test_voyekat.py`

**Purpose**: Tests specific VoyeKat page integration.

**Usage**:

```bash
python scripts/test_voyekat.py
```

---

## 📜 Legacy Scripts

### `get-fb-page-token.ps1`

**Purpose**: PowerShell script for Facebook page token retrieval.

**Usage** (PowerShell):

```powershell
.\scripts\get-fb-page-token.ps1
```

### `get-voyekat-token.ps1`

**Purpose**: PowerShell script for VoyeKat page token retrieval.

**Usage** (PowerShell):

```powershell
.\scripts\get-voyekat-token.ps1
```

### `mock_facebook.py`

**Purpose**: Mock Facebook API for testing without real Facebook connectivity.

**Usage**:

```bash
python scripts/mock_facebook.py
```

---

## 🚀 Running Scripts

### Prerequisites

1. **Virtual Environment** (recommended):

   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   ```

2. **Dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

3. **Environment Variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

### Common Usage Patterns

**Initial Setup**:

```bash
# 1. Setup database
psql -U postgres -f scripts/setup_database.sql

# 2. Run migrations
python scripts/migrate_user_facebook.py

# 3. Verify configuration
python scripts/check_facebook_config.py
```

**Development Testing**:

```bash
# Test authentication
python scripts/test_user_auth.py

# Test Facebook integration
python scripts/test_facebook_auth.py

# Test AI generation
python scripts/test_openai_debug.py
```

**Production Verification**:

```bash
# Verify all systems
python scripts/check_facebook_config.py
python scripts/verify_facebook.py
python scripts/test_debug.py
```

---

## 📊 Script Categories Summary

| Category      | Count | Purpose                            |
| ------------- | ----- | ---------------------------------- |
| Setup         | 2     | Database and initial configuration |
| Migration     | 1     | Database schema updates            |
| Test          | 15+   | Various testing scenarios          |
| Configuration | 2     | System verification                |
| Utility       | 2     | Automated operations               |
| Debug         | 6+    | Troubleshooting and analysis       |
| Legacy        | 3     | Backward compatibility             |

---

## 🔧 Creating New Scripts

When creating new scripts, follow these conventions:

### Naming Convention

- `test_*.py` - Testing scripts
- `setup_*.py` - Setup and installation scripts
- `migrate_*.py` - Database migration scripts
- `verify_*.py` - Verification and validation scripts
- `debug_*.py` - Debugging and troubleshooting scripts

### Script Template

```python
"""
Script Description
Brief description of what this script does
"""
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def main():
    """Main function"""
    print("🚀 Script Name")
    print("=" * 50)

    try:
        # Script logic here
        print("✅ Script completed successfully!")

    except Exception as e:
        print(f"❌ Script failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
```

### Documentation Requirements

- Add script to this SCRIPTS.md file
- Include purpose, usage, and sample output
- Document any prerequisites or dependencies
- Provide example commands

---

**Last Updated**: October 30, 2025
**Total Scripts**: 22+ scripts covering all aspects of the application
