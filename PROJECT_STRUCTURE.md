# Project Structure

Complete overview of the FB Daily Posts project organization and file structure.

## Directory Overview

```
fb-daily-posts/
├── app/                          # Main application code
│   ├── __init__.py              # Flask app factory
│   ├── controllers/             # API endpoints (MVC controllers)
│   ├── database/               # Database models and configuration
│   ├── providers/              # External service integrations
│   └── static/                 # Static files (images, CSS, JS)
├── scripts/                     # Utility and test scripts
├── examples/                    # Frontend integration examples
├── storage/                     # Local storage (databases, files)
├── docs/                       # Documentation files
├── app.py                      # Application entry point
├── requirements.txt            # Python dependencies
├── Procfile                    # Heroku deployment config
├── runtime.txt                 # Python runtime specification
└── .env                        # Environment variables (not in git)
```

## Application Structure (`app/`)

### Core Application (`app/`)

- **`__init__.py`** - Flask application factory with blueprint registration
- **`app.py`** (root) - Application entry point and server startup

### Controllers (`app/controllers/`)

MVC controllers handling HTTP requests and responses:

- **`facebook_auth_controller.py`** - Facebook OAuth and page management
- **`social_media_controller.py`** - Content generation and post creation
- **`user_auth_controller.py`** - User registration, login, and profile management

### Database Layer (`app/database/`)

Database models, configuration, and utilities:

- **`db.py`** - Database configuration and connection setup
- **`auth.py`** - JWT authentication utilities and decorators
- **`models/`** - SQLAlchemy ORM models
  - **`user.py`** - User model with authentication and Facebook integration
  - **`post.py`** - Social media post model with metadata

### External Providers (`app/providers/`)

Integrations with external services:

- **`image_gen.py`** - OpenAI DALL-E image generation
- **`llama_meta.py`** - Meta Llama text generation via OpenRouter
- **`watermark.py`** - Image watermarking and branding utilities

### Static Files (`app/static/`)

Static assets served by Flask:

- **`images/`** - Generated and uploaded images
- **`css/`** - Stylesheets
- **`js/`** - JavaScript files
- **`fonts/`** - Custom fonts for branding

## Scripts Directory (`scripts/`)

Utility scripts for setup, testing, and maintenance:

### Setup and Migration Scripts

- **`setup_database.sql`** - PostgreSQL database initialization
- **`migrate_user_facebook.py`** - Database migration for Facebook integration

### Testing Scripts

- **`test_user_auth.py`** - User authentication testing
- **`test_facebook_auth.py`** - Facebook integration testing
- **`test_openai_debug.py`** - AI image generation testing
- **`test_debug.py`** - General API endpoint testing

### Configuration Scripts

- **`check_facebook_config.py`** - Complete configuration verification
- **`verify_facebook.py`** - Facebook API connectivity testing

### Utility Scripts

- **`run_daily.py`** - Automated post creation scheduler
- **`facebook_fallback.py`** - Admin fallback functionality testing

## Examples Directory (`examples/`)

Frontend integration examples and templates:

- **`nextjs-complete-auth.jsx`** - Complete Next.js authentication component
- **`facebook-login-frontend.js`** - Facebook integration for frontend
- **`api-usage-examples.js`** - API usage patterns and examples

## Configuration Files

### Environment Configuration

- **`.env`** - Environment variables (local development)
- **`.env.example`** - Environment variable template

### Deployment Configuration

- **`requirements.txt`** - Python package dependencies
- **`Procfile`** - Heroku process configuration
- **`runtime.txt`** - Python runtime version for Heroku
- **`Dockerfile`** - Docker container configuration
- **`docker-compose.yml`** - Docker Compose setup

### Documentation

- **`README.md`** - Main project documentation
- **`API_DOCUMENTATION.md`** - Complete API reference
- **`SCRIPTS.md`** - Scripts documentation
- **`DEPLOYMENT.md`** - Deployment guide
- **`API_ENDPOINTS_NEXTJS.md`** - Next.js specific API guide

## File Responsibilities

### Core Application Files

#### `app/__init__.py`

```python
# Application factory pattern
# Blueprint registration
# CORS configuration
# Database initialization
# JWT setup
```

#### `app.py`

```python
# Application entry point
# Development server startup
# Environment configuration loading
```

### Controller Files

#### `user_auth_controller.py`

```python
# User registration and login
# JWT token management
# Profile management
# Password hashing and validation
```

#### `facebook_auth_controller.py`

```python
# Facebook OAuth flow
# Page selection and management
# Token handling and refresh
# Facebook API integration
```

#### `social_media_controller.py`

```python
# Content generation orchestration
# Post creation and publishing
# AI service coordination
# Multi-user content management
```

### Database Files

#### `models/user.py`

```python
# User authentication model
# Facebook integration fields
# Password hashing utilities
# User relationship management
```

#### `models/post.py`

```python
# Social media post model
# Content and metadata storage
# Publishing status tracking
# User relationship mapping
```

### Provider Files

#### `providers/image_gen.py`

```python
# OpenAI DALL-E integration
# Image generation and processing
# Error handling and retries
# Response format standardization
```

#### `providers/llama_meta.py`

```python
# Meta Llama integration via OpenRouter
# Text generation and formatting
# Prompt engineering utilities
# Content optimization
```

## Data Flow Architecture

### User Authentication Flow

```
Client Request → user_auth_controller → User Model → Database
                                    ↓
JWT Token ← Response ← JSON ← Authentication Logic
```

### Facebook Integration Flow

```
Client → facebook_auth_controller → Facebook API
          ↓
Database ← User Model ← OAuth Response
```

### Content Generation Flow

```
Client Request → social_media_controller → AI Providers
                                        ↓
Post Model ← Database ← Generated Content
```

## Database Schema

### Users Table

```sql
users (
  id SERIAL PRIMARY KEY,
  username VARCHAR(80) UNIQUE NOT NULL,
  email VARCHAR(120) UNIQUE NOT NULL,
  password_hash VARCHAR(128) NOT NULL,
  is_active BOOLEAN DEFAULT TRUE,
  facebook_data TEXT,
  selected_page_id VARCHAR(50),
  selected_page_token TEXT,
  created_at TIMESTAMP,
  updated_at TIMESTAMP
)
```

### Posts Table

```sql
posts (
  id SERIAL PRIMARY KEY,
  user_id INTEGER REFERENCES users(id),
  content TEXT NOT NULL,
  image_url TEXT,
  facebook_post_id VARCHAR(100),
  status VARCHAR(20) DEFAULT 'draft',
  scheduled_time TIMESTAMP,
  created_at TIMESTAMP,
  updated_at TIMESTAMP
)
```

## API Route Structure

### Authentication Routes (`/api/user/`)

- `POST /register` - User registration
- `POST /login` - User login
- `GET /profile` - Get user profile
- `PUT /update-profile` - Update user profile
- `GET /facebook-connection-status` - Facebook status

### Facebook Routes (`/api/facebook-auth/`)

- `GET /facebook/login-url` - Get OAuth URL
- `GET /callback` - OAuth callback handler
- `GET /pages` - Get user's Facebook pages
- `POST /select-page` - Select Facebook page
- `POST /disconnect` - Disconnect Facebook

### Social Media Routes (`/api/social/`)

- `POST /generate-prompt` - Generate text content
- `POST /generate-image` - Generate image content
- `POST /create-post` - Create and publish post

## Security Architecture

### Authentication Layer

- JWT token-based authentication
- Password hashing with salt
- User session management
- Token expiration handling

### Authorization Layer

- Route-level authentication requirements
- User-specific resource access
- Facebook page ownership validation
- Admin fallback mechanisms

### Data Protection

- Environment variable configuration
- Secure password storage
- API key protection
- Database connection security

## External Dependencies

### Core Dependencies

```python
Flask==3.0.3              # Web framework
Flask-SQLAlchemy==3.1.1    # ORM
Flask-JWT-Extended==4.6.0  # JWT authentication
Flask-CORS==4.0.0          # Cross-origin requests
psycopg2-binary==2.9.9     # PostgreSQL adapter
python-dotenv==1.0.0       # Environment variables
```

### AI and Social Media

```python
openai==1.35.15            # OpenAI API
requests==2.31.0           # HTTP requests
Pillow==10.4.0            # Image processing
```

## Development Workflow

### Local Development Setup

1. Clone repository
2. Create virtual environment
3. Install dependencies
4. Configure environment variables
5. Setup database
6. Run migrations
7. Start development server

### Testing Workflow

1. Run unit tests (`scripts/test_*.py`)
2. Verify configuration (`check_facebook_config.py`)
3. Test API endpoints
4. Validate Facebook integration
5. Check AI service connectivity

### Deployment Workflow

1. Code review and testing
2. Environment configuration
3. Database migrations
4. Service deployment
5. Health checks and monitoring

---

**Project Type**: Flask Web Application  
**Architecture**: MVC with Blueprint Pattern  
**Database**: PostgreSQL with SQLAlchemy ORM  
**Authentication**: JWT-based with Facebook OAuth  
**AI Integration**: OpenAI DALL-E, Meta Llama  
**Frontend**: API-first with Next.js examples
