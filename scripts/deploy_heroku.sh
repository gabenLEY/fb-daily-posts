#!/bin/bash
# Heroku Deployment Script for FB Daily Posts
# Complete setup for Heroku deployment

echo "🚀 FB Daily Posts - Heroku Deployment Setup"
echo "=========================================="

# Check if Heroku CLI is installed
if ! command -v heroku &> /dev/null; then
    echo "❌ Heroku CLI not found. Please install it first:"
    echo "   https://devcenter.heroku.com/articles/heroku-cli"
    exit 1
fi

echo "✅ Heroku CLI found"

# Check if user is logged in to Heroku
if ! heroku auth:whoami &> /dev/null; then
    echo "❌ Not logged in to Heroku. Please run: heroku login"
    exit 1
fi

echo "✅ Heroku authentication verified"

# Get app name from user
read -p "Enter your Heroku app name (or press Enter for auto-generated): " APP_NAME

# Create Heroku app
if [ -z "$APP_NAME" ]; then
    echo "📱 Creating Heroku app with auto-generated name..."
    heroku create
else
    echo "📱 Creating Heroku app: $APP_NAME"
    heroku create $APP_NAME
fi

# Get the actual app name (in case it was auto-generated)
ACTUAL_APP_NAME=$(heroku apps:info --json | python3 -c "import sys, json; print(json.load(sys.stdin)['app']['name'])")
echo "✅ App created: $ACTUAL_APP_NAME"

# Add PostgreSQL addon
echo "🗄️  Adding PostgreSQL database..."
heroku addons:create heroku-postgresql:essential-0 --app $ACTUAL_APP_NAME

# Set environment variables
echo "⚙️  Setting environment variables..."

# Required environment variables
heroku config:set FLASK_ENV=production --app $ACTUAL_APP_NAME
heroku config:set SECRET_KEY=$(openssl rand -base64 32) --app $ACTUAL_APP_NAME
heroku config:set PORT=80 --app $ACTUAL_APP_NAME

# Facebook configuration
echo "📘 Facebook Configuration:"
echo "You need to set these variables with your Facebook app credentials:"
echo ""
echo "heroku config:set FB_APP_ID=your_facebook_app_id --app $ACTUAL_APP_NAME"
echo "heroku config:set FB_APP_SECRET=your_facebook_app_secret --app $ACTUAL_APP_NAME"
echo "heroku config:set FB_REDIRECT_URI=https://$ACTUAL_APP_NAME.herokuapp.com/api/facebook-auth/callback --app $ACTUAL_APP_NAME"
echo ""

# AI configuration
echo "🤖 AI Services Configuration:"
echo "You need to set these variables with your API keys:"
echo ""
echo "heroku config:set OPENAI_API_KEY=your_openai_api_key --app $ACTUAL_APP_NAME"
echo "heroku config:set OPENROUTER_API_KEY=your_openrouter_api_key --app $ACTUAL_APP_NAME"
echo ""

# Optional configurations
heroku config:set FRONTEND_URL=https://your-frontend-domain.com --app $ACTUAL_APP_NAME
heroku config:set LLAMA_MODEL=meta-llama/llama-3.1-70b-instruct --app $ACTUAL_APP_NAME
heroku config:set USE_PLACEHOLDER_IMAGES=false --app $ACTUAL_APP_NAME

# Set fallback Facebook credentials (optional)
echo "📝 Optional Facebook Fallback:"
echo "If you want admin fallback, set these:"
echo ""
echo "heroku config:set FB_PAGE_ID=your_page_id --app $ACTUAL_APP_NAME"
echo "heroku config:set FB_PAGE_ACCESS_TOKEN=your_page_token --app $ACTUAL_APP_NAME"
echo ""

# Add git remote if not exists
if ! git remote get-url heroku &> /dev/null; then
    heroku git:remote -a $ACTUAL_APP_NAME
    echo "✅ Added Heroku git remote"
fi

# Deploy the application
echo "🚀 Deploying application..."
git add .
git commit -m "Deploy to Heroku - $(date)"
git push heroku main

# Run database migrations
echo "🔄 Running database migrations..."
heroku run python scripts/migrate_user_facebook.py --app $ACTUAL_APP_NAME

# Open the application
echo "🌐 Opening application..."
heroku open --app $ACTUAL_APP_NAME

echo ""
echo "🎉 Deployment Complete!"
echo "================================"
echo ""
echo "📋 Your Heroku App Details:"
echo "   App Name: $ACTUAL_APP_NAME"
echo "   URL: https://$ACTUAL_APP_NAME.herokuapp.com"
echo "   Git Remote: heroku"
echo ""
echo "⚙️  Don't forget to set your API keys:"
echo "   1. Facebook: FB_APP_ID, FB_APP_SECRET"
echo "   2. OpenAI: OPENAI_API_KEY"
echo "   3. OpenRouter: OPENROUTER_API_KEY"
echo ""
echo "🔧 Useful Heroku Commands:"
echo "   heroku logs --tail                    # View logs"
echo "   heroku config                         # View all config vars"
echo "   heroku run python scripts/test.py    # Run scripts"
echo "   heroku restart                        # Restart app"
echo ""
echo "📚 Next Steps:"
echo "   1. Set your API keys using the commands shown above"
echo "   2. Update your Facebook app settings with the callback URL"
echo "   3. Test your deployment: https://$ACTUAL_APP_NAME.herokuapp.com/health"
echo ""