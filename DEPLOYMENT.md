# Anonymous IRC - Deployment Guide

## 🚀 Production Deployment Instructions

### Prerequisites

- Python 3.11+
- PostgreSQL database
- Redis server (for WebSocket channel layers)
- Domain name with SSL certificate

---

## 📋 Step-by-Step Deployment

### 1. Environment Setup

Create a `.env` file in the project root (use `.env.example` as template):

```bash
cp .env.example .env
```

Edit `.env` with your production values:

```env
SECRET_KEY=your-super-secret-key-here-min-50-chars
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Database
DB_NAME=anonymous_social
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=localhost
DB_PORT=5432

# Redis
REDIS_URL=redis://localhost:6379/0

# Security
SECURE_SSL_REDIRECT=True
CSRF_TRUSTED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Database Setup

Create PostgreSQL database:

```bash
sudo -u postgres psql
CREATE DATABASE anonymous_social;
CREATE USER your_db_user WITH PASSWORD 'your_db_password';
ALTER ROLE your_db_user SET client_encoding TO 'utf8';
ALTER ROLE your_db_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE your_db_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE anonymous_social TO your_db_user;
\q
```

Run migrations:

```bash
python manage.py migrate --settings=anonymous_social.settings_production
```

### 4. Create Superuser

```bash
python manage.py createsuperuser --settings=anonymous_social.settings_production
```

### 5. Collect Static Files

```bash
python manage.py collectstatic --noinput --settings=anonymous_social.settings_production
```

### 6. Create Logs Directory

```bash
mkdir -p logs
touch logs/django.log
```

---

## 🌐 Deployment Options

### Option A: Heroku Deployment

1. **Install Heroku CLI**
   ```bash
   curl https://cli-assets.heroku.com/install.sh | sh
   ```

2. **Login to Heroku**
   ```bash
   heroku login
   ```

3. **Create Heroku App**
   ```bash
   heroku create your-app-name
   ```

4. **Add PostgreSQL**
   ```bash
   heroku addons:create heroku-postgresql:mini
   ```

5. **Add Redis**
   ```bash
   heroku addons:create heroku-redis:mini
   ```

6. **Set Environment Variables**
   ```bash
   heroku config:set SECRET_KEY="your-secret-key"
   heroku config:set DEBUG=False
   heroku config:set DJANGO_SETTINGS_MODULE=anonymous_social.settings_production
   ```

7. **Deploy**
   ```bash
   git push heroku main
   ```

8. **Run Migrations**
   ```bash
   heroku run python manage.py migrate
   heroku run python manage.py createsuperuser
   ```

### Option B: DigitalOcean/VPS Deployment

1. **Install System Dependencies**
   ```bash
   sudo apt update
   sudo apt install python3-pip python3-dev libpq-dev postgresql postgresql-contrib nginx redis-server
   ```

2. **Clone Repository**
   ```bash
   git clone your-repo-url
   cd as
   ```

3. **Create Virtual Environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

4. **Configure Nginx**
   
   Create `/etc/nginx/sites-available/anonymous_social`:
   
   ```nginx
   upstream anonymous_social {
       server 127.0.0.1:8000;
   }

   server {
       listen 80;
       server_name yourdomain.com www.yourdomain.com;
       
       location / {
           proxy_pass http://anonymous_social;
           proxy_http_version 1.1;
           proxy_set_header Upgrade $http_upgrade;
           proxy_set_header Connection "upgrade";
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }

       location /static/ {
           alias /path/to/your/project/staticfiles/;
       }

       location /media/ {
           alias /path/to/your/project/media/;
       }
   }
   ```

   Enable site:
   ```bash
   sudo ln -s /etc/nginx/sites-available/anonymous_social /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl restart nginx
   ```

5. **Setup SSL with Let's Encrypt**
   ```bash
   sudo apt install certbot python3-certbot-nginx
   sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
   ```

6. **Create Systemd Service**
   
   Create `/etc/systemd/system/anonymous_social.service`:
   
   ```ini
   [Unit]
   Description=Anonymous IRC Social Network
   After=network.target

   [Service]
   User=www-data
   Group=www-data
   WorkingDirectory=/path/to/your/project
   Environment="PATH=/path/to/your/project/venv/bin"
   ExecStart=/path/to/your/project/venv/bin/daphne -b 0.0.0.0 -p 8000 anonymous_social.asgi:application

   [Install]
   WantedBy=multi-user.target
   ```

   Enable and start:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable anonymous_social
   sudo systemctl start anonymous_social
   sudo systemctl status anonymous_social
   ```

### Option C: Railway Deployment

1. **Install Railway CLI**
   ```bash
   npm i -g @railway/cli
   ```

2. **Login**
   ```bash
   railway login
   ```

3. **Initialize Project**
   ```bash
   railway init
   ```

4. **Add PostgreSQL**
   ```bash
   railway add postgresql
   ```

5. **Add Redis**
   ```bash
   railway add redis
   ```

6. **Deploy**
   ```bash
   railway up
   ```

---

## 🔒 Security Checklist

- [ ] `DEBUG = False` in production
- [ ] Strong `SECRET_KEY` (50+ random characters)
- [ ] `ALLOWED_HOSTS` configured correctly
- [ ] SSL/HTTPS enabled
- [ ] `SECURE_SSL_REDIRECT = True`
- [ ] `SESSION_COOKIE_SECURE = True`
- [ ] `CSRF_COOKIE_SECURE = True`
- [ ] Database credentials secured
- [ ] `.env` file not committed to git
- [ ] Redis password protected (if exposed)
- [ ] Regular backups configured
- [ ] Firewall configured (only ports 80, 443, 22 open)

---

## 📊 Monitoring & Maintenance

### Check Application Logs
```bash
tail -f logs/django.log
```

### Check System Service
```bash
sudo systemctl status anonymous_social
```

### Restart Application
```bash
sudo systemctl restart anonymous_social
```

### Database Backup
```bash
pg_dump anonymous_social > backup_$(date +%Y%m%d).sql
```

### Update Application
```bash
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate --settings=anonymous_social.settings_production
python manage.py collectstatic --noinput --settings=anonymous_social.settings_production
sudo systemctl restart anonymous_social
```

---

## 🐛 Troubleshooting

### WebSocket Connection Issues
- Ensure Redis is running: `sudo systemctl status redis`
- Check Redis connection: `redis-cli ping`
- Verify `REDIS_URL` in `.env`

### Static Files Not Loading
- Run `collectstatic` again
- Check Nginx configuration
- Verify `STATIC_ROOT` path

### Database Connection Errors
- Check PostgreSQL is running: `sudo systemctl status postgresql`
- Verify database credentials in `.env`
- Check database exists: `sudo -u postgres psql -l`

### 502 Bad Gateway
- Check application is running: `sudo systemctl status anonymous_social`
- Check logs: `tail -f logs/django.log`
- Verify port 8000 is not blocked

---

## 📈 Performance Optimization

1. **Enable Gzip Compression** (Nginx)
2. **Configure Redis maxmemory policy**
3. **Set up CDN for static files**
4. **Enable database connection pooling**
5. **Configure proper caching headers**
6. **Monitor with tools like New Relic or Sentry**

---

## 🎯 Post-Deployment

1. Test all features:
   - User registration/login
   - Global chat (WebSocket)
   - Channel creation
   - File uploads
   - Emoji picker

2. Monitor logs for errors

3. Set up automated backups

4. Configure monitoring/alerting

5. Update DNS records if needed

---

## 📞 Support

For issues or questions, check:
- Application logs: `logs/django.log`
- System logs: `journalctl -u anonymous_social`
- Nginx logs: `/var/log/nginx/error.log`

---

**🎉 Your Anonymous IRC Social Network is now live!**
