# Deployment Guide

Complete deployment guide for the FB Daily Posts platform across different environments.

## Quick Deployment Options

- [Local Development](#local-development)
- [Heroku Deployment](#heroku-deployment)
- [Docker Deployment](#docker-deployment)
- [Production Server](#production-server)

---

## Local Development

### Prerequisites

- Python 3.8+
- PostgreSQL 12+
- Git

### Setup Steps

1. **Clone Repository**

   ```bash
   git clone <repository-url>
   cd fb-daily-posts
   ```

2. **Create Virtual Environment**

   ```bash
   python -m venv venv

   # Windows
   venv\Scripts\activate

   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install Dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Setup Database**

   ```bash
   # Create PostgreSQL database
   psql -U postgres -f scripts/setup_database.sql

   # Run migrations
   python scripts/migrate_user_facebook.py
   ```

5. **Configure Environment**

   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

6. **Verify Setup**

   ```bash
   python scripts/check_facebook_config.py
   python scripts/test_user_auth.py
   ```

7. **Run Application**

   ```bash
   python app.py
   ```

   Application will be available at: `http://127.0.0.1:8000`

---

## Heroku Deployment

### Prerequisites

- Heroku CLI installed
- Heroku account
- Git repository

### Deployment Steps

1. **Create Heroku App**

   ```bash
   heroku create your-app-name
   ```

2. **Add PostgreSQL Add-on**

   ```bash
   heroku addons:create heroku-postgresql:mini
   ```

3. **Set Environment Variables**

   ```bash
   heroku config:set FLASK_ENV=production
   heroku config:set SECRET_KEY=your-secret-key
   heroku config:set FB_APP_ID=your-facebook-app-id
   heroku config:set FB_APP_SECRET=your-facebook-app-secret
   heroku config:set OPENAI_API_KEY=your-openai-key
   heroku config:set OPENROUTER_API_KEY=your-openrouter-key
   ```

4. **Configure Facebook Redirect URI**

   ```bash
   heroku config:set FB_REDIRECT_URI=https://your-app-name.herokuapp.com/api/facebook-auth/callback
   heroku config:set FRONTEND_URL=https://your-frontend-url.com
   ```

5. **Deploy Application**

   ```bash
   git add .
   git commit -m "Deploy to Heroku"
   git push heroku main
   ```

6. **Run Database Migrations**

   ```bash
   heroku run python scripts/migrate_user_facebook.py
   ```

7. **Verify Deployment**
   ```bash
   heroku open
   # Visit: https://your-app-name.herokuapp.com/health
   ```

### Heroku Configuration Files

**Procfile**:

```
web: python app.py
```

**runtime.txt**:

```
python-3.11.0
```

---

## Docker Deployment

### Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd --create-home --shell /bin/bash app
RUN chown -R app:app /app
USER app

# Expose port
EXPOSE 8000

# Run application
CMD ["python", "app.py"]
```

### docker-compose.yml

```yaml
version: "3.8"

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DB_HOST=postgres
      - DB_PORT=5432
      - DB_NAME=fb_posts_db
      - DB_USER=fb_posts_user
      - DB_PASSWORD=your_password
    depends_on:
      - postgres
    volumes:
      - ./storage:/app/storage

  postgres:
    image: postgres:13
    environment:
      - POSTGRES_DB=fb_posts_db
      - POSTGRES_USER=fb_posts_user
      - POSTGRES_PASSWORD=your_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

volumes:
  postgres_data:
```

### Docker Deployment Steps

1. **Build and Run**

   ```bash
   docker-compose up --build
   ```

2. **Run Migrations**

   ```bash
   docker-compose exec app python scripts/migrate_user_facebook.py
   ```

3. **Access Application**
   ```
   http://localhost:8000
   ```

---

## Production Server

### Prerequisites

- Ubuntu 20.04+ (or similar Linux distribution)
- Root or sudo access
- Domain name (optional)

### Server Setup

1. **Update System**

   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

2. **Install Dependencies**

   ```bash
   # Python and PostgreSQL
   sudo apt install python3 python3-pip python3-venv postgresql postgresql-contrib nginx -y

   # Install Git
   sudo apt install git -y
   ```

3. **Setup PostgreSQL**

   ```bash
   sudo -u postgres psql

   # In PostgreSQL shell:
   CREATE USER fb_posts_user WITH PASSWORD 'secure_password';
   CREATE DATABASE fb_posts_db OWNER fb_posts_user;
   GRANT ALL PRIVILEGES ON DATABASE fb_posts_db TO fb_posts_user;
   \q
   ```

4. **Clone Application**

   ```bash
   cd /opt
   sudo git clone <repository-url> fb-daily-posts
   sudo chown -R $USER:$USER fb-daily-posts
   cd fb-daily-posts
   ```

5. **Setup Python Environment**

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

6. **Configure Environment**

   ```bash
   cp .env.example .env
   # Edit .env with production values
   nano .env
   ```

7. **Run Migrations**

   ```bash
   python scripts/migrate_user_facebook.py
   ```

8. **Setup Systemd Service**

   ```bash
   sudo nano /etc/systemd/system/fb-daily-posts.service
   ```

   **Service File Content**:

   ```ini
   [Unit]
   Description=FB Daily Posts Flask Application
   After=network.target

   [Service]
   User=www-data
   Group=www-data
   WorkingDirectory=/opt/fb-daily-posts
   Environment=PATH=/opt/fb-daily-posts/venv/bin
   ExecStart=/opt/fb-daily-posts/venv/bin/python app.py
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```

9. **Start Service**

   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable fb-daily-posts
   sudo systemctl start fb-daily-posts
   ```

10. **Configure Nginx**

    ```bash
    sudo nano /etc/nginx/sites-available/fb-daily-posts
    ```

    **Nginx Configuration**:

    ```nginx
    server {
        listen 80;
        server_name your-domain.com;

        location / {
            proxy_pass http://127.0.0.1:8000;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
    ```

11. **Enable Nginx Site**

    ```bash
    sudo ln -s /etc/nginx/sites-available/fb-daily-posts /etc/nginx/sites-enabled/
    sudo nginx -t
    sudo systemctl reload nginx
    ```

12. **Setup SSL (Optional)**
    ```bash
    sudo apt install certbot python3-certbot-nginx -y
    sudo certbot --nginx -d your-domain.com
    ```

---

## Environment Variables Reference

### Required Variables

```env
# Database
DB_HOST=localhost
DB_PORT=5432
DB_USER=fb_posts_user
DB_PASSWORD=secure_password
DB_NAME=fb_posts_db

# Facebook App
FB_APP_ID=your_facebook_app_id
FB_APP_SECRET=your_facebook_app_secret
FB_REDIRECT_URI=https://yourdomain.com/api/facebook-auth/callback

# AI Services
OPENAI_API_KEY=sk-proj-...
OPENROUTER_API_KEY=sk-or-v1-...
```

### Optional Variables

```env
# Flask Configuration
FLASK_ENV=production
PORT=8000
SECRET_KEY=random-secret-key

# Facebook Fallback
FB_PAGE_ID=fallback_page_id
FB_PAGE_ACCESS_TOKEN=fallback_token

# Frontend
FRONTEND_URL=https://your-frontend-domain.com

# AI Configuration
LLAMA_MODEL=meta-llama/llama-3.1-70b-instruct
USE_PLACEHOLDER_IMAGES=false

# Branding
BRAND_GREEN=#10B981
BRAND_FOOTER=Your Brand Name
```

---

## Security Considerations

### Production Security Checklist

- [ ] Use strong, unique passwords for database
- [ ] Set secure JWT secret key
- [ ] Enable HTTPS with SSL certificate
- [ ] Configure firewall (only allow ports 80, 443, 22)
- [ ] Regular security updates
- [ ] Monitor application logs
- [ ] Backup database regularly
- [ ] Use environment variables for secrets
- [ ] Configure CORS for specific domains
- [ ] Enable PostgreSQL authentication

### Firewall Configuration

```bash
# Enable UFW
sudo ufw enable

# Allow SSH
sudo ufw allow 22

# Allow HTTP/HTTPS
sudo ufw allow 80
sudo ufw allow 443

# Check status
sudo ufw status
```

---

## Monitoring and Maintenance

### Log Monitoring

```bash
# Application logs
sudo journalctl -u fb-daily-posts -f

# Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### Database Backup

```bash
# Create backup
pg_dump -U fb_posts_user -h localhost fb_posts_db > backup_$(date +%Y%m%d).sql

# Restore backup
psql -U fb_posts_user -h localhost fb_posts_db < backup_20251030.sql
```

### Application Updates

```bash
cd /opt/fb-daily-posts
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
python scripts/migrate_user_facebook.py  # If needed
sudo systemctl restart fb-daily-posts
```

---

## Troubleshooting

### Common Issues

1. **Port Already in Use**

   ```bash
   sudo lsof -i :8000
   sudo kill <process_id>
   ```

2. **Database Connection Failed**

   ```bash
   # Check PostgreSQL status
   sudo systemctl status postgresql

   # Check database configuration
   python scripts/check_facebook_config.py
   ```

3. **Facebook OAuth Issues**

   - Verify FB_REDIRECT_URI matches Facebook app settings
   - Check Facebook app is in production mode
   - Verify required permissions are requested

4. **AI API Issues**
   - Check API keys are valid
   - Verify account has sufficient credits
   - Check network connectivity

### Log Analysis

```bash
# Check application errors
grep -i error /var/log/syslog

# Check application performance
python scripts/test_debug.py
```

---

## Performance Optimization

### Production Optimizations

1. **Use Production WSGI Server**

   ```bash
   pip install gunicorn
   gunicorn --bind 0.0.0.0:8000 app:app
   ```

2. **Database Connection Pooling**

   ```python
   # In database configuration
   SQLALCHEMY_ENGINE_OPTIONS = {
       'pool_size': 10,
       'pool_recycle': 300,
       'pool_timeout': 30,
   }
   ```

3. **Nginx Caching**
   ```nginx
   location /static/ {
       expires 1y;
       add_header Cache-Control "public, immutable";
   }
   ```

---

**Last Updated**: October 30, 2025  
**Supported Platforms**: Linux, macOS, Windows  
**Deployment Methods**: Local, Heroku, Docker, Production Server
