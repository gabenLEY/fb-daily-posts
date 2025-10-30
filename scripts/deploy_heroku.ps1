# Heroku Deployment Script for FB Daily Posts (PowerShell)
# Complete setup for Heroku deployment

Write-Host "🚀 FB Daily Posts - Heroku Deployment Setup" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green

# Check if Heroku CLI is installed
try {
    $herokuVersion = heroku --version
    Write-Host "✅ Heroku CLI found: $herokuVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Heroku CLI not found. Please install it first:" -ForegroundColor Red
    Write-Host "   https://devcenter.heroku.com/articles/heroku-cli" -ForegroundColor Yellow
    exit 1
}

# Check if user is logged in to Heroku
try {
    $herokuUser = heroku auth:whoami
    Write-Host "✅ Heroku authentication verified: $herokuUser" -ForegroundColor Green
} catch {
    Write-Host "❌ Not logged in to Heroku. Please run: heroku login" -ForegroundColor Red
    exit 1
}

# Get app name from user
$APP_NAME = Read-Host "Enter your Heroku app name (or press Enter for auto-generated)"

# Create Heroku app
if ([string]::IsNullOrEmpty($APP_NAME)) {
    Write-Host "📱 Creating Heroku app with auto-generated name..." -ForegroundColor Blue
    heroku create
} else {
    Write-Host "📱 Creating Heroku app: $APP_NAME" -ForegroundColor Blue
    heroku create $APP_NAME
}

# Get the actual app name (in case it was auto-generated)
$appInfo = heroku apps:info --json | ConvertFrom-Json
$ACTUAL_APP_NAME = $appInfo.app.name
Write-Host "✅ App created: $ACTUAL_APP_NAME" -ForegroundColor Green

# Add PostgreSQL addon
Write-Host "🗄️  Adding PostgreSQL database..." -ForegroundColor Blue
heroku addons:create heroku-postgresql:essential-0 --app $ACTUAL_APP_NAME

# Set environment variables
Write-Host "⚙️  Setting environment variables..." -ForegroundColor Blue

# Generate a secure secret key
$secretKey = [System.Convert]::ToBase64String([System.Security.Cryptography.RNGCryptoServiceProvider]::new().GetBytes(32))

# Required environment variables
heroku config:set "FLASK_ENV=production" --app $ACTUAL_APP_NAME
heroku config:set "SECRET_KEY=$secretKey" --app $ACTUAL_APP_NAME
heroku config:set "PORT=80" --app $ACTUAL_APP_NAME

# Facebook configuration
Write-Host ""
Write-Host "📘 Facebook Configuration:" -ForegroundColor Cyan
Write-Host "You need to set these variables with your Facebook app credentials:" -ForegroundColor Yellow
Write-Host ""
Write-Host "heroku config:set FB_APP_ID=your_facebook_app_id --app $ACTUAL_APP_NAME" -ForegroundColor White
Write-Host "heroku config:set FB_APP_SECRET=your_facebook_app_secret --app $ACTUAL_APP_NAME" -ForegroundColor White
Write-Host "heroku config:set FB_REDIRECT_URI=https://$ACTUAL_APP_NAME.herokuapp.com/api/facebook-auth/callback --app $ACTUAL_APP_NAME" -ForegroundColor White
Write-Host ""

# AI configuration
Write-Host "🤖 AI Services Configuration:" -ForegroundColor Cyan
Write-Host "You need to set these variables with your API keys:" -ForegroundColor Yellow
Write-Host ""
Write-Host "heroku config:set OPENAI_API_KEY=your_openai_api_key --app $ACTUAL_APP_NAME" -ForegroundColor White
Write-Host "heroku config:set OPENROUTER_API_KEY=your_openrouter_api_key --app $ACTUAL_APP_NAME" -ForegroundColor White
Write-Host ""

# Optional configurations
heroku config:set "FRONTEND_URL=https://your-frontend-domain.com" --app $ACTUAL_APP_NAME
heroku config:set "LLAMA_MODEL=meta-llama/llama-3.1-70b-instruct" --app $ACTUAL_APP_NAME
heroku config:set "USE_PLACEHOLDER_IMAGES=false" --app $ACTUAL_APP_NAME

# Set fallback Facebook credentials (optional)
Write-Host "📝 Optional Facebook Fallback:" -ForegroundColor Cyan
Write-Host "If you want admin fallback, set these:" -ForegroundColor Yellow
Write-Host ""
Write-Host "heroku config:set FB_PAGE_ID=your_page_id --app $ACTUAL_APP_NAME" -ForegroundColor White
Write-Host "heroku config:set FB_PAGE_ACCESS_TOKEN=your_page_token --app $ACTUAL_APP_NAME" -ForegroundColor White
Write-Host ""

# Add git remote if not exists
try {
    git remote get-url heroku | Out-Null
    Write-Host "✅ Heroku git remote already exists" -ForegroundColor Green
} catch {
    heroku git:remote -a $ACTUAL_APP_NAME
    Write-Host "✅ Added Heroku git remote" -ForegroundColor Green
}

# Deploy the application
Write-Host "🚀 Deploying application..." -ForegroundColor Blue
git add .
git commit -m "Deploy to Heroku - $(Get-Date)"
git push heroku main

# Run database migrations
Write-Host "🔄 Running database migrations..." -ForegroundColor Blue
heroku run "python scripts/migrate_user_facebook.py" --app $ACTUAL_APP_NAME

# Open the application
Write-Host "🌐 Opening application..." -ForegroundColor Blue
heroku open --app $ACTUAL_APP_NAME

Write-Host ""
Write-Host "🎉 Deployment Complete!" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Your Heroku App Details:" -ForegroundColor Cyan
Write-Host "   App Name: $ACTUAL_APP_NAME" -ForegroundColor White
Write-Host "   URL: https://$ACTUAL_APP_NAME.herokuapp.com" -ForegroundColor White
Write-Host "   Git Remote: heroku" -ForegroundColor White
Write-Host ""
Write-Host "⚙️  Don't forget to set your API keys:" -ForegroundColor Yellow
Write-Host "   1. Facebook: FB_APP_ID, FB_APP_SECRET" -ForegroundColor White
Write-Host "   2. OpenAI: OPENAI_API_KEY" -ForegroundColor White
Write-Host "   3. OpenRouter: OPENROUTER_API_KEY" -ForegroundColor White
Write-Host ""
Write-Host "🔧 Useful Heroku Commands:" -ForegroundColor Cyan
Write-Host "   heroku logs --tail                    # View logs" -ForegroundColor White
Write-Host "   heroku config                         # View all config vars" -ForegroundColor White
Write-Host "   heroku run python scripts/test.py    # Run scripts" -ForegroundColor White
Write-Host "   heroku restart                        # Restart app" -ForegroundColor White
Write-Host ""
Write-Host "📚 Next Steps:" -ForegroundColor Cyan
Write-Host "   1. Set your API keys using the commands shown above" -ForegroundColor White
Write-Host "   2. Update your Facebook app settings with the callback URL" -ForegroundColor White
Write-Host "   3. Test your deployment: https://$ACTUAL_APP_NAME.herokuapp.com/health" -ForegroundColor White
Write-Host ""

# Ask if user wants to set API keys now
$setKeys = Read-Host "Would you like to set your API keys now? (y/n)"
if ($setKeys -eq "y" -or $setKeys -eq "Y") {
    Write-Host ""
    Write-Host "📝 Setting API Keys..." -ForegroundColor Blue
    
    $fbAppId = Read-Host "Enter your Facebook App ID"
    if (![string]::IsNullOrEmpty($fbAppId)) {
        heroku config:set "FB_APP_ID=$fbAppId" --app $ACTUAL_APP_NAME
    }
    
    $fbAppSecret = Read-Host "Enter your Facebook App Secret"
    if (![string]::IsNullOrEmpty($fbAppSecret)) {
        heroku config:set "FB_APP_SECRET=$fbAppSecret" --app $ACTUAL_APP_NAME
    }
    
    $openaiKey = Read-Host "Enter your OpenAI API Key"
    if (![string]::IsNullOrEmpty($openaiKey)) {
        heroku config:set "OPENAI_API_KEY=$openaiKey" --app $ACTUAL_APP_NAME
    }
    
    $openrouterKey = Read-Host "Enter your OpenRouter API Key"
    if (![string]::IsNullOrEmpty($openrouterKey)) {
        heroku config:set "OPENROUTER_API_KEY=$openrouterKey" --app $ACTUAL_APP_NAME
    }
    
    Write-Host "✅ API keys configured!" -ForegroundColor Green
    
    # Restart the app to apply new configuration
    Write-Host "🔄 Restarting app to apply configuration..." -ForegroundColor Blue
    heroku restart --app $ACTUAL_APP_NAME
}

Write-Host ""
Write-Host "🚀 Your app is ready! Visit: https://$ACTUAL_APP_NAME.herokuapp.com" -ForegroundColor Green