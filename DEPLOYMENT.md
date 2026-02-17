# Deployment Guide

This guide covers deploying the Product Marketplace to production.

## Pre-Deployment Checklist

### Backend
- [ ] Set `DEBUG=False` in settings
- [ ] Configure `ALLOWED_HOSTS`
- [ ] Use PostgreSQL instead of SQLite
- [ ] Set strong `SECRET_KEY`
- [ ] Configure CORS for production domain
- [ ] Set up environment variables
- [ ] Enable HTTPS
- [ ] Configure static file serving
- [ ] Set up logging
- [ ] Configure email backend (for notifications)

### Frontend
- [ ] Update API URL to production
- [ ] Build optimized production bundle
- [ ] Configure environment variables
- [ ] Enable error tracking
- [ ] Set up analytics (optional)

### Security
- [ ] Review security settings
- [ ] Enable CSRF protection
- [ ] Configure secure cookies
- [ ] Set up rate limiting
- [ ] Review CORS settings
- [ ] Enable security headers

## Backend Deployment

### Option 1: Railway

1. Install Railway CLI:
```bash
npm i -g @railway/cli
```

2. Login:
```bash
railway login
```

3. Initialize project:
```bash
cd backend
railway init
```

4. Add PostgreSQL:
```bash
railway add postgresql
```

5. Set environment variables:
```bash
railway variables set SECRET_KEY=your-secret-key
railway variables set OPENAI_API_KEY=your-openai-key
railway variables set ALLOWED_HOSTS=your-domain.railway.app
```

6. Deploy:
```bash
railway up
```

7. Run migrations:
```bash
railway run python manage.py migrate
railway run python manage.py createsuperuser
```

### Option 2: Heroku

1. Install Heroku CLI

2. Create app:
```bash
cd backend
heroku create your-app-name
```

3. Add PostgreSQL:
```bash
heroku addons:create heroku-postgresql:mini
```

4. Set environment variables:
```bash
heroku config:set SECRET_KEY=your-secret-key
heroku config:set OPENAI_API_KEY=your-openai-key
heroku config:set ALLOWED_HOSTS=your-app-name.herokuapp.com
```

5. Create Procfile:
```
web: gunicorn config.wsgi --log-file -
release: python manage.py migrate
```

6. Update requirements.txt:
```bash
pip install gunicorn psycopg2-binary
pip freeze > requirements.txt
```

7. Deploy:
```bash
git push heroku main
```

8. Create superuser:
```bash
heroku run python manage.py createsuperuser
```

### Option 3: AWS EC2

1. Launch EC2 instance (Ubuntu)

2. SSH into instance:
```bash
ssh -i your-key.pem ubuntu@your-instance-ip
```

3. Install dependencies:
```bash
sudo apt update
sudo apt install python3-pip python3-venv nginx postgresql
```

4. Clone repository:
```bash
git clone your-repo-url
cd product-marketplace/backend
```

5. Set up virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install gunicorn
```

6. Configure PostgreSQL:
```bash
sudo -u postgres psql
CREATE DATABASE marketplace;
CREATE USER marketplace_user WITH PASSWORD 'your-password';
GRANT ALL PRIVILEGES ON DATABASE marketplace TO marketplace_user;
\q
```

7. Set environment variables:
```bash
export SECRET_KEY=your-secret-key
export DATABASE_URL=postgresql://marketplace_user:your-password@localhost/marketplace
export OPENAI_API_KEY=your-openai-key
```

8. Run migrations:
```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic
```

9. Configure Gunicorn:
```bash
gunicorn config.wsgi:application --bind 0.0.0.0:8000
```

10. Configure Nginx:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /static/ {
        alias /path/to/backend/staticfiles/;
    }
}
```

11. Set up systemd service:
```ini
[Unit]
Description=Product Marketplace
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/path/to/backend
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/gunicorn config.wsgi:application --bind 0.0.0.0:8000

[Install]
WantedBy=multi-user.target
```

## Frontend Deployment

### Option 1: Vercel (Recommended)

1. Install Vercel CLI:
```bash
npm i -g vercel
```

2. Login:
```bash
vercel login
```

3. Deploy:
```bash
cd frontend
vercel
```

4. Set environment variables in Vercel dashboard:
```
NEXT_PUBLIC_API_URL=https://your-backend-url.com/api
```

5. Deploy to production:
```bash
vercel --prod
```

### Option 2: Netlify

1. Install Netlify CLI:
```bash
npm install -g netlify-cli
```

2. Build:
```bash
cd frontend
npm run build
```

3. Deploy:
```bash
netlify deploy --prod
```

4. Set environment variables in Netlify dashboard

### Option 3: AWS S3 + CloudFront

1. Build:
```bash
cd frontend
npm run build
```

2. Create S3 bucket

3. Upload build files:
```bash
aws s3 sync out/ s3://your-bucket-name
```

4. Configure CloudFront distribution

5. Set up custom domain

## Database Migration

### From SQLite to PostgreSQL

1. Dump data:
```bash
python manage.py dumpdata > data.json
```

2. Update database settings:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'marketplace',
        'USER': 'marketplace_user',
        'PASSWORD': 'your-password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

3. Run migrations:
```bash
python manage.py migrate
```

4. Load data:
```bash
python manage.py loaddata data.json
```

## Environment Variables

### Backend (.env)
```env
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=your-domain.com,www.your-domain.com
DATABASE_URL=postgresql://user:password@host:5432/dbname
OPENAI_API_KEY=sk-your-openai-key
CORS_ALLOWED_ORIGINS=https://your-frontend-domain.com
```

### Frontend (.env.local)
```env
NEXT_PUBLIC_API_URL=https://your-backend-domain.com/api
```

## SSL/HTTPS Setup

### Using Let's Encrypt (Free)

1. Install Certbot:
```bash
sudo apt install certbot python3-certbot-nginx
```

2. Get certificate:
```bash
sudo certbot --nginx -d your-domain.com -d www.your-domain.com
```

3. Auto-renewal:
```bash
sudo certbot renew --dry-run
```

## Monitoring & Logging

### Sentry Setup

1. Install:
```bash
pip install sentry-sdk
```

2. Configure in settings.py:
```python
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

sentry_sdk.init(
    dsn="your-sentry-dsn",
    integrations=[DjangoIntegration()],
    traces_sample_rate=1.0,
)
```

### Logging Configuration

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': '/var/log/marketplace/error.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'ERROR',
            'propagate': True,
        },
    },
}
```

## Backup Strategy

### Database Backups

1. Automated daily backups:
```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
pg_dump marketplace > /backups/marketplace_$DATE.sql
```

2. Add to crontab:
```bash
0 2 * * * /path/to/backup-script.sh
```

### File Backups

Use AWS S3 or similar for file storage backups.

## Performance Optimization

### Backend
- Enable database connection pooling
- Use Redis for caching
- Optimize database queries
- Enable gzip compression
- Use CDN for static files

### Frontend
- Enable Next.js image optimization
- Use CDN for assets
- Enable caching headers
- Minimize bundle size
- Use lazy loading

## Scaling

### Horizontal Scaling
- Use load balancer (AWS ELB, Nginx)
- Multiple application servers
- Shared database
- Redis for session storage

### Vertical Scaling
- Increase server resources
- Optimize database
- Add read replicas

## Rollback Plan

1. Keep previous version deployed
2. Use blue-green deployment
3. Database migration rollback scripts
4. Quick rollback command ready

## Post-Deployment

- [ ] Test all functionality
- [ ] Monitor error logs
- [ ] Check performance metrics
- [ ] Verify SSL certificate
- [ ] Test from different locations
- [ ] Monitor API response times
- [ ] Check database connections
- [ ] Verify email sending (if configured)

## Troubleshooting

### Common Issues

**Static files not loading:**
```bash
python manage.py collectstatic --noinput
```

**Database connection errors:**
- Check DATABASE_URL
- Verify database is running
- Check firewall rules

**CORS errors:**
- Update CORS_ALLOWED_ORIGINS
- Check frontend URL

**502 Bad Gateway:**
- Check application is running
- Verify Gunicorn/uWSGI config
- Check Nginx configuration

## Support

For deployment issues, check:
- Application logs
- Server logs
- Database logs
- Nginx/Apache logs

## Cost Estimation

### Small Scale (< 1000 users)
- Backend: $5-10/month (Railway/Heroku)
- Frontend: Free (Vercel/Netlify)
- Database: Included
- Total: ~$10/month

### Medium Scale (1000-10000 users)
- Backend: $25-50/month
- Frontend: Free-$20/month
- Database: $15-30/month
- CDN: $10-20/month
- Total: ~$70-120/month

### Large Scale (10000+ users)
- Custom infrastructure
- Load balancers
- Multiple servers
- Managed services
- Total: $500+/month
