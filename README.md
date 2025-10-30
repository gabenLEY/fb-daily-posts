# FB Daily Posts - Social Media Management Platform

A complete Flask-based social media management platform with AI-powered content generation, Facebook integration, and user authentication.

## Project Structure

```
fb-daily-posts/
├── app.py                 # Main Flask application (MVC Architecture)
├── .env                   # Environment variables (not in git)
├── .env.example          # Environment template
├── requirements.txt      # Python dependencies
├── runtime.txt          # Python version for deployment
├── Procfile             # Heroku deployment config
│
├── models/              # Data models and database
│   ├── __init__.py     # Models package
│   ├── database.py     # Database configuration
│   ├── user.py         # User model
│   └── post.py         # Post model
│
├── controllers/         # Business logic controllers
│   ├── __init__.py             # Controllers package
│   ├── auth_controller.py      # Authentication logic
│   ├── post_controller.py      # Post management logic
│   └── social_media_controller.py # AI generation & Facebook logic
│
├── routes/              # API route definitions
│   ├── __init__.py      # Routes package & registration
│   ├── auth_routes.py   # Authentication endpoints
│   ├── post_routes.py   # Post management endpoints
│   └── social_routes.py # AI generation & Facebook endpoints
│
├── auth/                # Authentication utilities
│   ├── __init__.py      # Auth package
│   └── auth_utils.py    # Session management & decorators
│
├── providers/           # AI and image generation services
│   ├── llama_meta.py   # OpenRouter LLM integration
│   ├── image_gen.py    # OpenAI image generation
│   └── watermark.py    # Image watermarking
│
├── utils/              # Utility functions
│   └── schedule.py     # Time/scheduling utilities
│
├── scripts/            # All scripts and development tools
│   ├── run_daily.py                # Automated posting script
│   ├── get-fb-page-token.ps1      # Facebook token extraction
│   ├── get-voyekat-token.ps1      # VoyeKat-specific tokens
│   ├── facebook_fallback.py       # Fallback posting method
│   ├── mock_facebook.py          # Mock Facebook API for testing
│   ├── verify_facebook.py        # Facebook API verification
│   └── test_*.py                 # Various test scripts
│
├── data/               # Database storage
│   └── app.db         # SQLite database (auto-created)
├── static/             # Static web assets
├── facebook_drafts/    # Local draft storage
└── .venv/             # Python virtual environment
```

## Main Components

### Core Application

- **app.py**: Main Flask server with API endpoints
- **providers/**: AI service integrations (OpenRouter, OpenAI)
- **utils/**: Helper functions for scheduling and utilities

### Scripts & Tools

- **scripts/**: All development, testing, and utility scripts
- **facebook_drafts/**: Local storage for drafts when Facebook API fails

## API Endpoints

### Authentication (`/api/auth/`)

- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - User login
- `POST /api/auth/logout` - User logout
- `GET /api/auth/profile` - Get user profile
- `PUT /api/auth/profile` - Update user profile
- `POST /api/auth/change-password` - Change password

### Posts (`/api/posts/`)

- `POST /api/posts/` - Create new post
- `GET /api/posts/` - Get user's posts
- `GET /api/posts/<id>` - Get specific post
- `PUT /api/posts/<id>` - Update post
- `DELETE /api/posts/<id>` - Delete post
- `GET /api/posts/status?status=draft` - Get posts by status
- `GET /api/posts/scheduled` - Get scheduled posts

### AI Generation & Facebook

- `POST /api/prompt` - Generate captions using LLM
- `POST /api/generate-image` - Create AI images
- `POST /api/facebook/publish_binary` - Upload and post to Facebook
- `POST /api/pipeline/generate-and-schedule` - Full content generation pipeline

## Environment Variables

Copy `.env.example` to `.env` and configure:

```
OPENROUTER_API_KEY=your_openrouter_key
OPENAI_API_KEY=your_openai_key
FB_PAGE_ID=your_facebook_page_id
FB_PAGE_ACCESS_TOKEN=your_facebook_token
DEFAULT_POST_TIME=09:00
BASE_URL=http://localhost:8000
```

## Usage

1. **Start the server**: `python app.py`
2. **Generate content**: Use the API endpoints or run scripts
3. **Facebook posting**: Supports both immediate and draft modes
4. **Fallback system**: Auto-saves drafts locally if Facebook API fails

## Development

All test files and utilities are organized in the `scripts/` folder for better project organization.
