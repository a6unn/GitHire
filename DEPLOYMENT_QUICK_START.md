# Quick Cloud Deployment Guide for GitHire

## Option 1: Render (Fastest - 10 minutes)

### Prerequisites
- GitHub repository: https://github.com/a6unn/GitHire
- Render account (free): https://render.com

### Steps:

1. **Sign up for Render**
   - Go to https://render.com and sign up
   - Connect your GitHub account

2. **Create a New Web Service (Backend)**
   - Click "New +" → "Web Service"
   - Connect repository: `a6unn/GitHire`
   - Name: `githire-backend`
   - Environment: `Docker`
   - Dockerfile path: `./Dockerfile`
   - Instance type: Free or Starter ($7/month)

   **Environment Variables:**
   ```
   OPENAI_API_KEY=your_openai_api_key
   GITHUB_TOKEN=your_github_token
   DATABASE_URL=sqlite:///./githire.db
   SECRET_KEY=your_secret_key_here
   ```

3. **Create Static Site (Frontend)**
   - Click "New +" → "Static Site"
   - Connect repository: `a6unn/GitHire`
   - Name: `githire-frontend`
   - Build command: `cd frontend && npm install && npm run build`
   - Publish directory: `frontend/dist`

   **Environment Variables:**
   ```
   VITE_API_URL=https://githire-backend.onrender.com
   ```

4. **Deploy**
   - Click "Create Web Service" / "Create Static Site"
   - Wait 5-10 minutes for deployment
   - Your app will be live at: `https://githire-frontend.onrender.com`

---

## Option 2: Railway (Simplest - 5 minutes)

### Prerequisites
- GitHub repository: https://github.com/a6unn/GitHire
- Railway account: https://railway.app

### Steps:

1. **Deploy with One Click**
   - Go to https://railway.app
   - Click "Start a New Project"
   - Select "Deploy from GitHub repo"
   - Choose: `a6unn/GitHire`

2. **Add Environment Variables**
   ```
   OPENAI_API_KEY=your_openai_api_key
   GITHUB_TOKEN=your_github_token
   SECRET_KEY=your_secret_key_here
   ```

3. **Configure Services**
   - Railway will auto-detect Docker setup
   - Generate domain for your app
   - Done! App will be live in 5 minutes

**Cost:** $5/month (includes $5 free credit)

---

## Option 3: DigitalOcean App Platform (Production-Ready)

### Prerequisites
- GitHub repository: https://github.com/a6unn/GitHire
- DigitalOcean account: https://digitalocean.com

### Steps:

1. **Create App**
   - Go to https://cloud.digitalocean.com/apps
   - Click "Create App"
   - Choose "GitHub" and select `a6unn/GitHire`

2. **Configure Backend**
   - Source directory: `/`
   - Dockerfile: `./Dockerfile`
   - HTTP port: 8000
   - Instance size: Basic ($5/month)

3. **Configure Frontend**
   - Source directory: `/frontend`
   - Build command: `npm install && npm run build`
   - Output directory: `dist`
   - Instance type: Static Site ($0/month)

4. **Add Environment Variables**
   ```
   OPENAI_API_KEY=your_openai_api_key
   GITHUB_TOKEN=your_github_token
   DATABASE_URL=sqlite:///./githire.db
   SECRET_KEY=your_secret_key_here
   ```

5. **Deploy**
   - Review and click "Create Resources"
   - Wait 10-15 minutes
   - Your app will be live with a `.ondigitalocean.app` domain

**Cost:** ~$5-10/month for production-ready setup

---

## Option 4: AWS (via Docker Compose) - Most Control

### Prerequisites
- AWS account
- AWS CLI installed
- Docker installed locally

### Quick Deploy using AWS App Runner:

```bash
# 1. Install AWS CLI
brew install awscli  # macOS
# or: pip install awscli

# 2. Configure AWS
aws configure

# 3. Build and push Docker image
aws ecr create-repository --repository-name githire-backend
docker build -t githire-backend .
docker tag githire-backend:latest <your-account-id>.dkr.ecr.us-east-1.amazonaws.com/githire-backend:latest
aws ecr get-login-password | docker login --username AWS --password-stdin <your-account-id>.dkr.ecr.us-east-1.amazonaws.com
docker push <your-account-id>.dkr.ecr.us-east-1.amazonaws.com/githire-backend:latest

# 4. Create App Runner service
aws apprunner create-service \
  --service-name githire-backend \
  --source-configuration '{
    "ImageRepository": {
      "ImageIdentifier": "<your-account-id>.dkr.ecr.us-east-1.amazonaws.com/githire-backend:latest",
      "ImageRepositoryType": "ECR"
    }
  }'
```

**Cost:** ~$5-15/month depending on usage

---

## Option 5: Self-Hosted VPS (Most Flexible)

### Using DigitalOcean Droplet or AWS EC2:

```bash
# 1. Create a droplet/EC2 instance (Ubuntu 22.04)
# Minimum: 2GB RAM, 1 CPU ($12/month on DigitalOcean)

# 2. SSH into your server
ssh root@your-server-ip

# 3. Install Docker and Docker Compose
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
apt-get install docker-compose-plugin

# 4. Clone your repository
git clone https://github.com/a6unn/GitHire.git
cd GitHire

# 5. Create .env file
cat > .env << EOF
OPENAI_API_KEY=your_openai_api_key
GITHUB_TOKEN=your_github_token
SECRET_KEY=your_secret_key_here
DATABASE_URL=sqlite:///./githire.db
EOF

# 6. Deploy with docker-compose
docker compose up -d

# 7. Configure Nginx reverse proxy (optional)
apt-get install nginx certbot python3-certbot-nginx
# Configure nginx.conf and get SSL certificate
certbot --nginx -d yourdomain.com
```

**Your app will be running at:**
- Backend: http://your-server-ip:8000
- Frontend: http://your-server-ip:3000

**Cost:** $12-24/month for a good VPS

---

## Environment Variables Needed

For any deployment option, you'll need these API keys:

### Required:
- `OPENAI_API_KEY` - Get from https://platform.openai.com/api-keys
- `GITHUB_TOKEN` - Generate at https://github.com/settings/tokens
  - Scopes needed: `public_repo`, `read:user`, `user:email`
- `SECRET_KEY` - Generate with: `openssl rand -hex 32`

### Optional:
- `ANTHROPIC_API_KEY` - If using Claude models (get from https://console.anthropic.com)
- `DATABASE_URL` - Defaults to SQLite, but can use PostgreSQL for production

---

## Recommendation for Your Use Case

**For Demo/Internal Use (Fastest):**
→ Use **Railway** (5 minutes, $5/month, easiest)

**For Production Deployment:**
→ Use **Render** (10 minutes, $7/month for backend, free frontend)

**For Enterprise/Full Control:**
→ Use **DigitalOcean App Platform** or **AWS** ($12-20/month, scalable)

---

## Post-Deployment Checklist

- [ ] Test login functionality
- [ ] Verify API endpoints working
- [ ] Test job description parsing
- [ ] Test GitHub search and candidate sourcing
- [ ] Configure custom domain (optional)
- [ ] Set up monitoring/logging
- [ ] Share URL with recruitment team
- [ ] Document any deployment-specific configurations

---

## Need Help?

If you encounter issues:
1. Check logs in your deployment platform
2. Verify environment variables are set correctly
3. Ensure API keys have proper permissions
4. Check that ports 8000 (backend) and 3000/5173 (frontend) are accessible
