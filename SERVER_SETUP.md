# Server Setup for anonymousocial.com

## 🌐 Domain Configuration

**Domain:** anonymousocial.com
**WWW:** www.anonymousocial.com

---

## 📋 Complete Server Setup Commands

### 1. Create .env File on Server

```bash
cd /var/www/as
sudo -u www-data nano .env
```

**Paste this content (update the values):**

```env
# Django Settings
SECRET_KEY=GENERATE_A_NEW_SECRET_KEY_HERE
DEBUG=False
ALLOWED_HOSTS=anonymousocial.com,www.anonymousocial.com

# Database
DB_NAME=anonymous_social
DB_USER=postgres
DB_PASSWORD=YOUR_POSTGRES_PASSWORD
DB_HOST=localhost
DB_PORT=5432

# Redis
REDIS_URL=redis://localhost:6379/0

# Security
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
CSRF_TRUSTED_ORIGINS=https://anonymousocial.com,https://www.anonymousocial.com
```

**Generate SECRET_KEY:**
```bash
python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 2. Setup PostgreSQL Database

```bash
# Switch to postgres user
sudo -u postgres psql

# In PostgreSQL prompt:
CREATE DATABASE anonymous_social;
CREATE USER postgres WITH PASSWORD 'YOUR_STRONG_PASSWORD';
ALTER ROLE postgres SET client_encoding TO 'utf8';
ALTER ROLE postgres SET default_transaction_isolation TO 'read committed';
ALTER ROLE postgres SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE anonymous_social TO postgres;
\q
```

### 3. Run Migrations and Setup

```bash
cd /var/www/as

# Create logs directory
sudo -u www-data mkdir -p logs

# Run migrations
sudo -u www-data /var/www/as/venv/bin/python manage.py migrate

# Collect static files
sudo -u www-data /var/www/as/venv/bin/python manage.py collectstatic --noinput

# Create superuser
sudo -u www-data /var/www/as/venv/bin/python manage.py createsuperuser
```

### 4. Configure Nginx for anonymousocial.com

```bash
sudo nano /etc/nginx/sites-available/anonymousocial
```

**Paste this configuration:**

```nginx
upstream anonymous_social {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name anonymousocial.com www.anonymousocial.com;
    
    # Redirect HTTP to HTTPS (after SSL is configured)
    # return 301 https://$server_name$request_uri;
    
    location / {
        proxy_pass http://anonymous_social;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support
        proxy_read_timeout 86400;
    }

    location /static/ {
        alias /var/www/as/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location /media/ {
        alias /var/www/as/media/;
        expires 7d;
    }
}
```

**Enable the site:**

```bash
sudo ln -s /etc/nginx/sites-available/anonymousocial /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 5. Setup SSL with Let's Encrypt

```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d anonymousocial.com -d www.anonymousocial.com

# Certbot will automatically update Nginx config for HTTPS
```

### 6. Start the Application Service

```bash
sudo systemctl daemon-reload
sudo systemctl enable anonymous_social
sudo systemctl start anonymous_social
sudo systemctl status anonymous_social
```

### 7. Verify Everything Works

```bash
# Check service status
sudo systemctl status anonymous_social

# Check logs
sudo journalctl -u anonymous_social -f

# Check Nginx logs
sudo tail -f /var/log/nginx/error.log

# Test the website
curl http://anonymousocial.com
```

---

## 🔒 DNS Configuration

Point your domain to the server IP:

```
A Record:     anonymousocial.com     →  YOUR_SERVER_IP
A Record:     www.anonymousocial.com →  YOUR_SERVER_IP
```

---

## 🧪 Testing Checklist

After deployment, test:

- [ ] Landing page: https://anonymousocial.com/
- [ ] User registration: https://anonymousocial.com/signup/
- [ ] User login: https://anonymousocial.com/login/
- [ ] Home page (after login): https://anonymousocial.com/home/
- [ ] Global chat WebSocket connection
- [ ] Channels page: https://anonymousocial.com/channels/
- [ ] Create channel
- [ ] Post in channel with text
- [ ] Post in channel with media
- [ ] Emoji picker works
- [ ] File uploads work
- [ ] SSL certificate valid (green padlock)

---

## 🔧 Troubleshooting

### Service won't start
```bash
sudo journalctl -u anonymous_social -n 50
```

### Database connection errors
```bash
# Check PostgreSQL is running
sudo systemctl status postgresql

# Test connection
sudo -u postgres psql -d anonymous_social
```

### Static files not loading
```bash
# Re-collect static files
sudo -u www-data /var/www/as/venv/bin/python manage.py collectstatic --noinput

# Check Nginx config
sudo nginx -t
```

### WebSocket not connecting
```bash
# Check Redis is running
sudo systemctl status redis

# Test Redis
redis-cli ping
```

---

## 📊 Monitoring

```bash
# Watch service logs
sudo journalctl -u anonymous_social -f

# Watch Nginx access logs
sudo tail -f /var/log/nginx/access.log

# Watch Nginx error logs
sudo tail -f /var/log/nginx/error.log

# Check system resources
htop
```

---

**🎉 Your Anonymous IRC Social Network is now live at https://anonymousocial.com!**
