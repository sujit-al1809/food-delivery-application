# Deployment Guide

## Production Deployment

### Backend Deployment

#### Using Gunicorn

1. **Install Gunicorn**
   ```bash
   pip install gunicorn
   ```

2. **Create WSGI entry point** (wsgi.py)
   ```python
   from app import create_app
   
   app = create_app('production')
   
   if __name__ == '__main__':
       app.run()
   ```

3. **Run with Gunicorn**
   ```bash
   gunicorn -w 4 -b 0.0.0.0:5000 wsgi:app
   ```

#### Using Docker

1. **Build image**
   ```bash
   docker build -t food-delivery-api .
   ```

2. **Run container**
   ```bash
   docker run -d \
     -p 5000:5000 \
     -e DATABASE_URL=postgresql://user:pass@db:5432/fooddelivery \
     -e FLASK_ENV=production \
     -e SECRET_KEY=your-secret-key \
     food-delivery-api
   ```

#### Using Heroku

1. **Install Heroku CLI**
   ```bash
   npm install -g heroku
   heroku login
   ```

2. **Create Procfile**
   ```
   web: gunicorn wsgi:app
   worker: celery -A tasks celery_app worker --loglevel=info
   ```

3. **Deploy**
   ```bash
   heroku create your-app-name
   heroku config:set SECRET_KEY=your-secret-key
   heroku config:set DATABASE_URL=postgresql://...
   git push heroku main
   ```

### Frontend Deployment

#### Using Vercel

1. **Install Vercel CLI**
   ```bash
   npm install -g vercel
   ```

2. **Deploy**
   ```bash
   cd frontend
   vercel
   ```

#### Using Netlify

1. **Build project**
   ```bash
   npm run build
   ```

2. **Deploy with Netlify CLI**
   ```bash
   npm install -g netlify-cli
   netlify deploy --prod --dir=dist
   ```

#### Using GitHub Pages

1. **Update package.json**
   ```json
   "homepage": "https://yourusername.github.io/food-delivery-app"
   ```

2. **Deploy**
   ```bash
   npm run build
   npm run deploy
   ```

### Database Migration (SQLite to PostgreSQL)

```bash
# Install migration tools
pip install alembic

# Initialize Alembic
alembic init migrations

# Create initial migration
alembic revision --autogenerate -m "Initial migration"

# Run migration
alembic upgrade head
```

### Environment Setup for Production

**Backend (.env)**
```
FLASK_ENV=production
DATABASE_URL=postgresql://user:password@localhost/fooddelivery_db
SECRET_KEY=generate-a-secure-key-here
SECURITY_PASSWORD_SALT=generate-another-secure-key-here
JWT_SECRET_KEY=jwt-secret-key-for-tokens
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
```

**Frontend (.env.production)**
```
VUE_APP_API_URL=https://api.yourdomain.com/api
VUE_APP_ENV=production
```

## Monitoring & Logging

### Application Logging

```python
# In app.py
import logging

logging.basicConfig(
    filename='app.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### Error Tracking (Sentry)

```bash
pip install sentry-sdk
```

```python
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

sentry_sdk.init(
    dsn="your-sentry-dsn",
    integrations=[FlaskIntegration()],
    traces_sample_rate=1.0
)
```

### Performance Monitoring

```python
# Add timing middleware
@app.before_request
def before_request():
    g.start_time = time.time()

@app.after_request
def after_request(response):
    elapsed = time.time() - g.start_time
    print(f"Request took {elapsed}s")
    return response
```

## Security Checklist

- [ ] Change default SECRET_KEY and SECURITY_PASSWORD_SALT
- [ ] Use strong database password
- [ ] Enable HTTPS/SSL certificate
- [ ] Set CORS origins to specific domains
- [ ] Implement rate limiting
- [ ] Use environment variables for all secrets
- [ ] Set secure cookie flags
- [ ] Enable CSRF protection
- [ ] Validate all user inputs
- [ ] Use prepared statements (SQLAlchemy handles this)
- [ ] Implement API key authentication for public APIs
- [ ] Set up WAF (Web Application Firewall)
- [ ] Enable logging and monitoring
- [ ] Regularly update dependencies

## Scaling Considerations

### Database
- Use connection pooling
- Implement caching (Redis)
- Consider database replication for high availability
- Use read replicas for reporting

### API
- Use load balancer (Nginx, HAProxy)
- Deploy multiple instances with process manager (Supervisor, Systemd)
- Implement caching strategies
- Use CDN for static assets

### Frontend
- Minimize bundle size
- Implement lazy loading
- Use service workers for offline support
- Enable gzip compression

### Background Jobs
- Scale Celery workers independently
- Monitor queue lengths
- Set up task retries and error handling
- Use task routing for specific worker types

## Backup & Recovery

```bash
# Database backup
pg_dump fooddelivery_db > backup.sql

# Restore
psql fooddelivery_db < backup.sql

# Automated backup script
0 2 * * * pg_dump fooddelivery_db | gzip > /backups/db-$(date +\%Y\%m\%d).sql.gz
```

## CI/CD Pipeline Example (GitHub Actions)

```yaml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.9
      
      - name: Install dependencies
        run: |
          pip install -r backend/requirements.txt
          cd frontend && npm install
      
      - name: Run tests
        run: |
          pytest backend/
          cd frontend && npm run test

  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Deploy to Heroku
        run: |
          git remote add heroku https://git.heroku.com/your-app.git
          git push heroku main
```

## Troubleshooting

### Common Issues

1. **Database connection error**
   - Check DATABASE_URL format
   - Verify database service is running
   - Check user permissions

2. **Redis connection error**
   - Ensure Redis server is running
   - Check CELERY_BROKER_URL
   - Verify network connectivity

3. **Static files not loading**
   - Run `python manage.py collectstatic`
   - Check STATIC_ROOT and STATIC_URL
   - Verify file permissions

4. **CORS errors**
   - Check CORS configuration
   - Verify frontend domain is in allowed origins
   - Check request headers

5. **Celery tasks not executing**
   - Verify worker is running
   - Check Redis connection
   - Review Celery logs
   - Ensure tasks are registered

For more help, check logs and error messages in:
- Backend: `app.log`
- Frontend: Browser console and network tab
- Celery: Worker terminal output

## Support

For deployment questions, refer to:
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Vue.js Deployment](https://v3.vuejs.org/guide/ssr.html)
- [Celery Documentation](https://docs.celeryproject.io/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
