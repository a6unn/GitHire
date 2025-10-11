# Deployment Guide

This guide covers deploying GitHire to production environments.

## Table of Contents

- [Production Considerations](#production-considerations)
- [Environment Configuration](#environment-configuration)
- [Deployment Options](#deployment-options)
  - [Docker Deployment](#docker-deployment)
  - [VPS Deployment](#vps-deployment)
  - [Cloud Platform Deployment](#cloud-platform-deployment)
- [Database Setup](#database-setup)
- [Security Checklist](#security-checklist)
- [Monitoring](#monitoring)

## Production Considerations

Before deploying to production:

1. **Use PostgreSQL** instead of SQLite for better concurrency
2. **Enable Redis** for caching to reduce GitHub API calls
3. **Set strong JWT secret** for token security
4. **Use HTTPS** with valid SSL certificates
5. **Set up monitoring** and logging
6. **Configure CORS** properly for your frontend domain
7. **Set up backups** for database
8. **Review rate limits** for GitHub and OpenAI APIs

## Environment Configuration

### Production Environment Variables

Create a `.env.production` file:

```bash
# ============================================================================
# API Keys (Required)
# ============================================================================
OPENAI_API_KEY=sk-proj-...
GITHUB_TOKEN=ghp_...

# ============================================================================
# Database (PostgreSQL Recommended)
# ============================================================================
DATABASE_URL=postgresql://user:password@localhost:5432/githire

# ============================================================================
# Security
# ============================================================================
JWT_SECRET_KEY=<strong-random-secret-min-32-chars>
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# ============================================================================
# Redis Cache
# ============================================================================
REDIS_ENABLED=true
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=<redis-password>
REDIS_DB=0

# ============================================================================
# Application
# ============================================================================
ENV=production
DEBUG=false
LOG_LEVEL=INFO

# CORS Origins (comma-separated)
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# ============================================================================
# Server
# ============================================================================
HOST=0.0.0.0
PORT=8000
WORKERS=4  # CPU cores * 2 + 1
```

### Generate Secure JWT Secret

```bash
# Python
python3 -c 'import secrets; print(secrets.token_urlsafe(32))'

# OpenSSL
openssl rand -hex 32
```

## Deployment Options

### Docker Deployment

#### 1. Create Dockerfile (Backend)

`Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY pyproject.toml .
RUN pip install --no-cache-dir -e .

# Copy application
COPY src/ ./src/
COPY demo_pipeline.py .

# Create database directory
RUN mkdir -p /app/data

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "src.backend_api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### 2. Create Dockerfile (Frontend)

`frontend/Dockerfile`:
```dockerfile
FROM node:18-alpine AS builder

WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm ci

# Build application
COPY . .
RUN npm run build

# Production image
FROM nginx:alpine

# Copy build files
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

#### 3. Create docker-compose.yml

`docker-compose.yml`:
```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: githire
      POSTGRES_PASSWORD: ${DB_PASSWORD}
      POSTGRES_DB: githire
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    command: redis-server --requirepass ${REDIS_PASSWORD}
    ports:
      - "6379:6379"
    restart: unless-stopped

  backend:
    build: .
    environment:
      DATABASE_URL: postgresql://githire:${DB_PASSWORD}@postgres:5432/githire
      REDIS_HOST: redis
      REDIS_PASSWORD: ${REDIS_PASSWORD}
      REDIS_ENABLED: "true"
      OPENAI_API_KEY: ${OPENAI_API_KEY}
      GITHUB_TOKEN: ${GITHUB_TOKEN}
      JWT_SECRET_KEY: ${JWT_SECRET_KEY}
      CORS_ORIGINS: https://yourdomain.com
    depends_on:
      - postgres
      - redis
    ports:
      - "8000:8000"
    volumes:
      - ./data:/app/data
    restart: unless-stopped

  frontend:
    build: ./frontend
    ports:
      - "80:80"
      - "443:443"
    depends_on:
      - backend
    restart: unless-stopped

volumes:
  postgres_data:
```

#### 4. Deploy with Docker Compose

```bash
# Create .env file with secrets
cat > .env << EOF
DB_PASSWORD=<strong-password>
REDIS_PASSWORD=<strong-password>
OPENAI_API_KEY=sk-proj-...
GITHUB_TOKEN=ghp_...
JWT_SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_urlsafe(32))')
EOF

# Build and start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

###VPS Deployment (Ubuntu/Debian)

#### 1. Server Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y python3.11 python3.11-venv python3-pip \
    nginx postgresql postgresql-contrib redis-server \
    certbot python3-certbot-nginx git curl

# Install Node.js
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs
```

#### 2. PostgreSQL Setup

```bash
# Switch to postgres user
sudo -u postgres psql

# Create database and user
CREATE DATABASE githire;
CREATE USER githire WITH ENCRYPTED PASSWORD 'your-strong-password';
GRANT ALL PRIVILEGES ON DATABASE githire TO githire;
\q
```

#### 3. Application Setup

```bash
# Create application user
sudo useradd -m -s /bin/bash githire
sudo su - githire

# Clone repository
git clone https://github.com/a6unn/GitHire.git
cd githire

# Backend setup
python3.11 -m venv venv
source venv/bin/activate
pip install -e .

# Create .env file
cp .env.example .env
nano .env  # Configure production values

# Frontend setup
cd frontend
npm install
npm run build
cd ..
```

#### 4. Systemd Service (Backend)

`/etc/systemd/system/githire-backend.service`:
```ini
[Unit]
Description=GitHire Backend API
After=network.target postgresql.service redis.service

[Service]
Type=simple
User=githire
WorkingDirectory=/home/githire/githire
Environment="PATH=/home/githire/githire/venv/bin"
ExecStart=/home/githire/githire/venv/bin/uvicorn src.backend_api.main:app \
    --host 0.0.0.0 --port 8000 --workers 4
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
sudo systemctl enable githire-backend
sudo systemctl start githire-backend
sudo systemctl status githire-backend
```

#### 5. Nginx Configuration

`/etc/nginx/sites-available/githire`:
```nginx
# Backend API
server {
    listen 80;
    server_name api.yourdomain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# Frontend
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    root /home/githire/githire/frontend/dist;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    # API proxy
    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/githire /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

#### 6. SSL Certificate (Let's Encrypt)

```bash
# Install certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com -d api.yourdomain.com

# Auto-renewal is configured by default
sudo certbot renew --dry-run
```

### Cloud Platform Deployment

#### AWS (Elastic Beanstalk)

1. Install AWS CLI and EB CLI
2. Initialize EB application:
```bash
eb init -p python-3.11 githire
eb create githire-prod
```

3. Configure environment variables in AWS Console

#### Heroku

`Procfile`:
```
web: uvicorn src.backend_api.main:app --host 0.0.0.0 --port $PORT
```

```bash
heroku create githire-app
heroku addons:create heroku-postgresql:mini
heroku addons:create heroku-redis:mini
heroku config:set OPENAI_API_KEY=sk-...
heroku config:set GITHUB_TOKEN=ghp_...
git push heroku main
```

#### Railway

1. Connect GitHub repository
2. Add environment variables
3. Deploy automatically on push

## Database Setup

### Migration from SQLite to PostgreSQL

```bash
# Export data from SQLite
sqlite3 githire.db .dump > backup.sql

# Import to PostgreSQL (may need manual adjustments)
psql -U githire -d githire < backup.sql
```

### Database Backups

```bash
# PostgreSQL backup
pg_dump -U githire githire > backup_$(date +%Y%m%d).sql

# Restore
psql -U githire githire < backup_20251010.sql

# Automated backups (crontab)
0 2 * * * pg_dump -U githire githire > /backups/githire_$(date +\%Y\%m\%d).sql
```

## Security Checklist

- [ ] Change default JWT secret
- [ ] Use strong database passwords
- [ ] Enable HTTPS with valid SSL certificate
- [ ] Configure CORS for specific origins only
- [ ] Set up firewall (ufw/iptables)
- [ ] Disable debug mode in production
- [ ] Use environment variables for secrets
- [ ] Enable rate limiting (nginx)
- [ ] Set up fail2ban for SSH
- [ ] Regular security updates
- [ ] Database backups configured
- [ ] Monitor API usage and costs

### Nginx Rate Limiting

Add to nginx config:
```nginx
# Define rate limit zone
limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;

# Apply to API location
location /api {
    limit_req zone=api_limit burst=20 nodelay;
    # ... rest of proxy config
}
```

## Monitoring

### Application Logs

```bash
# Backend logs (systemd)
sudo journalctl -u githire-backend -f

# Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### Health Check Endpoint

The backend provides a health check endpoint:
```bash
curl http://localhost:8000/health
```

### Monitoring Tools

**Recommended**:
- **Uptime monitoring**: UptimeRobot, Better Uptime
- **Error tracking**: Sentry
- **Performance**: New Relic, Datadog
- **Logs**: Papertrail, Logtail

### Resource Monitoring

```bash
# Server resources
htop
df -h
free -m

# PostgreSQL connections
psql -U githire -c "SELECT count(*) FROM pg_stat_activity;"

# Redis info
redis-cli INFO stats
```

## Performance Optimization

### Application

1. **Enable Redis caching** to reduce GitHub API calls
2. **Use connection pooling** for database
3. **Async operations** for I/O-bound tasks
4. **CDN** for static assets (CloudFlare, AWS CloudFront)

### Database

```sql
-- Create indexes
CREATE INDEX idx_projects_user_id ON projects(user_id);
CREATE INDEX idx_shortlisted_project_id ON shortlisted_candidates(project_id);
CREATE INDEX idx_outreach_project_username ON outreach_messages(project_id, github_username);

-- Vacuum and analyze
VACUUM ANALYZE;
```

### Nginx

```nginx
# Enable gzip compression
gzip on;
gzip_types text/plain text/css application/json application/javascript;

# Browser caching
location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
    expires 1y;
    add_header Cache-Control "public, immutable";
}
```

## Scaling

### Horizontal Scaling

```yaml
# docker-compose.yml
backend:
  deploy:
    replicas: 3

# Add load balancer
nginx:
  image: nginx:alpine
  volumes:
    - ./nginx-lb.conf:/etc/nginx/nginx.conf
  ports:
    - "80:80"
  depends_on:
    - backend
```

### Database Read Replicas

For high-traffic deployments, set up PostgreSQL read replicas for read-heavy operations.

## Troubleshooting

### Check Service Status

```bash
sudo systemctl status githire-backend
sudo systemctl status nginx
sudo systemctl status postgresql
sudo systemctl status redis
```

### View Application Logs

```bash
# Last 100 lines
sudo journalctl -u githire-backend -n 100

# Follow logs
sudo journalctl -u githire-backend -f

# Logs from last hour
sudo journalctl -u githire-backend --since "1 hour ago"
```

### Common Issues

**Issue**: Database connection errors
```bash
# Check PostgreSQL is running
sudo systemctl status postgresql

# Check connection
psql -U githire -d githire -h localhost
```

**Issue**: High memory usage
```bash
# Reduce workers
# Edit /etc/systemd/system/githire-backend.service
# Change --workers 4 to --workers 2

sudo systemctl daemon-reload
sudo systemctl restart githire-backend
```

## Rollback Procedure

```bash
# Git rollback
git log  # Find commit hash
git checkout <commit-hash>

# Restart services
sudo systemctl restart githire-backend

# Frontend rollback
cd frontend
git checkout <commit-hash>
npm run build
sudo systemctl restart nginx
```

---

**Last Updated**: 2025-10-10
