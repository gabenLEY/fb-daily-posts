# FB Daily Posts - Application Structure

## New Organized Structure

```
fb-daily-posts/
├── app/                          # Main application folder
│   ├── __init__.py              # Application factory
│   ├── controllers/             # Request handlers (Blueprints)
│   │   ├── auth_controller_blueprint.py    # JWT Authentication
│   │   ├── post_controller.py              # Post management
│   │   ├── social_media_controller.py      # Social media & AI
│   │   └── __init__.py
│   ├── database/                # Database layer
│   │   ├── models/              # SQLAlchemy models
│   │   │   ├── user.py          # User model with JWT auth
│   │   │   ├── post.py          # Post model
│   │   │   └── __init__.py
│   │   ├── db.py                # Database configuration
│   │   ├── auth.py              # JWT utilities
│   │   └── __init__.py
│   ├── routes/                  # Blueprint registration
│   │   ├── auth_routes.py
│   │   ├── post_routes.py
│   │   ├── social_routes.py
│   │   └── __init__.py
│   ├── providers/               # External service integrations
│   │   ├── llama_meta.py        # AI prompt generation
│   │   ├── image_gen.py         # AI image generation
│   │   └── watermark.py
│   ├── utils/                   # Utility functions
│   │   └── schedule.py
│   └── static/                  # Static files (images)
├── storage/                     # Data storage
│   ├── data/                    # Database files
│   │   └── app.db
│   └── facebook_drafts/         # Draft posts
├── scripts/                     # Utility scripts
├── run.py                       # Application entry point
├── requirements.txt
├── .env
└── README.md
```

## Key Improvements

### 1. **Clean Architecture**

- Separated concerns into logical folders
- Application factory pattern in `app/__init__.py`
- Blueprint-based routing for better modularity

### 2. **Database Layer**

- **Flask-SQLAlchemy** instead of raw SQLAlchemy
- **PostgreSQL** support with SQLite fallback
- **JWT authentication** replacing sessions
- Proper model relationships and CRUD operations

### 3. **Authentication System**

- JWT token-based authentication
- Password hashing with salt
- User registration, login, profile management
- Authentication decorators for protected routes

### 4. **API Endpoints**

#### Authentication (`/api/auth/`)

- `POST /register` - User registration
- `POST /login` - User login (returns JWT token)
- `POST /logout` - Logout
- `GET /me` - Get current user profile
- `PUT /me` - Update user profile
- `POST /change-password` - Change password

#### Posts (`/api/posts/`)

- `GET /` - Get user's posts
- `POST /` - Create new post
- `GET /{id}` - Get specific post
- `PUT /{id}` - Update post
- `DELETE /{id}` - Delete post
- `GET /scheduled` - Get scheduled posts
- `GET /published` - Get published posts
- `POST /{id}/publish` - Publish post immediately

#### Social Media (`/api/social/`)

- `POST /generate-prompt` - Generate AI prompts
- `POST /generate-image` - Generate AI images
- `POST /publish-facebook` - Publish to Facebook
- `POST /save-draft` - Save post as draft
- `POST /schedule-post` - Schedule post
- `GET /facebook-config` - Check Facebook configuration

### 5. **Environment Configuration**

- `.env` file for sensitive data
- PostgreSQL connection with fallback to SQLite
- JWT secret key configuration
- Facebook API credentials

### 6. **Removed Duplicates**

- Eliminated duplicate folders (`controllers/`, `routes/`, `database/`, etc.)
- Removed old `*_old.py` files
- Consolidated static files
- Organized data storage in `storage/` folder

## Running the Application

```bash
# Start the application
python run.py

# The API will be available at:
# http://127.0.0.1:8000
```

## Status: ✅ Functional

- Database initialized with proper tables
- JWT authentication working
- All API endpoints properly structured
- Modern Flask architecture with blueprints
- PostgreSQL ready (with SQLite fallback for development)
