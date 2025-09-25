#!/bin/bash

# Deploy Security Monitor to DigitalOcean Droplet with Docker

echo "🚀 Deploying Security Monitor..."

# Install Docker if not present
if ! command -v docker &> /dev/null; then
    echo "📦 Installing Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    rm get-docker.sh
fi

# Install Docker Compose if not present
if ! command -v docker-compose &> /dev/null; then
    echo "📦 Installing Docker Compose..."
    apt-get update
    apt-get install -y docker-compose
fi

# Clone or update repository
if [ -d "/opt/security-monitor" ]; then
    echo "📥 Updating repository..."
    cd /opt/security-monitor
    git pull
else
    echo "📥 Cloning repository..."
    cd /opt
    git clone https://github.com/YOUR_USERNAME/security-monitor.git
    cd security-monitor
fi

# Create data directories
mkdir -p data article_cache

# Copy .env.example to .env if it doesn't exist
if [ ! -f .env ]; then
    cp .env.example .env
    echo "⚠️  Please edit .env file with your API keys and email settings!"
    echo "Run: nano /opt/security-monitor/.env"
fi

# Stop existing container if running
docker-compose down 2>/dev/null

# Build and start container
echo "🔨 Building Docker image..."
docker-compose build

echo "🚀 Starting container..."
docker-compose up -d

# Show status
echo "✅ Deployment complete!"
echo ""
docker-compose ps
echo ""
echo "📌 Access your dashboard at: http://YOUR_DROPLET_IP"
echo "📝 View logs: docker-compose logs -f"
echo "🔄 Restart: docker-compose restart"
echo "🛑 Stop: docker-compose down"