#!/bin/bash

# GitHire Quick Deployment Script
# This script helps you deploy GitHire to various cloud platforms

set -e

echo "🚀 GitHire Deployment Helper"
echo "================================"
echo ""
echo "Choose your deployment platform:"
echo "1. Railway (Fastest - 5 min)"
echo "2. Render (Easy - 10 min)"
echo "3. DigitalOcean VPS (Self-hosted - 15 min)"
echo "4. Local Docker (Testing)"
echo ""
read -p "Enter choice [1-4]: " choice

case $choice in
  1)
    echo ""
    echo "📦 Railway Deployment"
    echo "================================"
    echo "1. Go to https://railway.app"
    echo "2. Click 'Start a New Project'"
    echo "3. Select 'Deploy from GitHub repo'"
    echo "4. Choose: a6unn/GitHire"
    echo "5. Add these environment variables:"
    echo ""
    echo "   OPENAI_API_KEY=<your_key>"
    echo "   GITHUB_TOKEN=<your_token>"
    echo "   SECRET_KEY=$(openssl rand -hex 32)"
    echo ""
    echo "6. Railway will auto-deploy!"
    echo ""
    echo "Cost: $5/month (includes $5 free credit)"
    ;;

  2)
    echo ""
    echo "🎨 Render Deployment"
    echo "================================"
    echo "Step 1: Deploy Backend"
    echo "  1. Go to https://render.com"
    echo "  2. Click 'New +' → 'Web Service'"
    echo "  3. Connect repo: a6unn/GitHire"
    echo "  4. Name: githire-backend"
    echo "  5. Environment: Docker"
    echo "  6. Add environment variables:"
    echo ""
    echo "     OPENAI_API_KEY=<your_key>"
    echo "     GITHUB_TOKEN=<your_token>"
    echo "     SECRET_KEY=$(openssl rand -hex 32)"
    echo "     DATABASE_URL=sqlite:///./githire.db"
    echo ""
    echo "Step 2: Deploy Frontend"
    echo "  1. Click 'New +' → 'Static Site'"
    echo "  2. Connect repo: a6unn/GitHire"
    echo "  3. Build command: cd frontend && npm install && npm run build"
    echo "  4. Publish directory: frontend/dist"
    echo "  5. Add environment variable:"
    echo "     VITE_API_URL=https://githire-backend.onrender.com"
    echo ""
    echo "Cost: Free tier available, or $7/month for always-on"
    ;;

  3)
    echo ""
    echo "🌊 DigitalOcean VPS Deployment"
    echo "================================"
    echo ""
    read -p "Enter your DigitalOcean droplet IP: " server_ip
    read -p "Enter your OpenAI API key: " openai_key
    read -p "Enter your GitHub token: " github_token

    echo ""
    echo "Deploying to $server_ip..."

    # Create deployment script
    cat > /tmp/deploy_remote.sh << 'EOF'
#!/bin/bash
set -e

# Update system
apt-get update
apt-get install -y git docker.io docker-compose

# Clone repository
cd /opt
git clone https://github.com/a6unn/GitHire.git
cd GitHire

# Create .env file
cat > .env << ENVEOF
OPENAI_API_KEY=$OPENAI_KEY
GITHUB_TOKEN=$GITHUB_TOKEN
SECRET_KEY=$(openssl rand -hex 32)
DATABASE_URL=sqlite:///./githire.db
ENVEOF

# Deploy with docker-compose
docker-compose up -d

echo "✅ GitHire deployed successfully!"
echo "Backend: http://$SERVER_IP:8000"
echo "Frontend: http://$SERVER_IP:3000"
EOF

    # Make script executable and copy to server
    chmod +x /tmp/deploy_remote.sh

    echo "Connecting to server and deploying..."
    ssh root@$server_ip "export OPENAI_KEY='$openai_key' GITHUB_TOKEN='$github_token' SERVER_IP='$server_ip'; bash -s" < /tmp/deploy_remote.sh

    echo ""
    echo "✅ Deployment complete!"
    echo "Backend: http://$server_ip:8000"
    echo "Frontend: http://$server_ip:3000"
    ;;

  4)
    echo ""
    echo "🐳 Local Docker Deployment"
    echo "================================"
    echo ""

    # Check if .env exists
    if [ ! -f .env ]; then
      echo "Creating .env file..."
      read -p "Enter your OpenAI API key: " openai_key
      read -p "Enter your GitHub token: " github_token

      cat > .env << EOF
OPENAI_API_KEY=$openai_key
GITHUB_TOKEN=$github_token
SECRET_KEY=$(openssl rand -hex 32)
DATABASE_URL=sqlite:///./githire.db
VITE_API_URL=http://localhost:8000
EOF
      echo "✅ .env file created"
    fi

    echo ""
    echo "Starting GitHire with docker-compose..."
    docker-compose up -d

    echo ""
    echo "✅ GitHire is running!"
    echo "Backend: http://localhost:8000"
    echo "Frontend: http://localhost:3000"
    echo ""
    echo "To view logs: docker-compose logs -f"
    echo "To stop: docker-compose down"
    ;;

  *)
    echo "Invalid choice. Exiting."
    exit 1
    ;;
esac

echo ""
echo "================================"
echo "📚 For detailed instructions, see:"
echo "   DEPLOYMENT_QUICK_START.md"
echo ""
echo "Need API keys?"
echo "  - OpenAI: https://platform.openai.com/api-keys"
echo "  - GitHub: https://github.com/settings/tokens"
echo "================================"
