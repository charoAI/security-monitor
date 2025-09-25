#!/bin/bash

# Force update script - ensures Docker uses latest code
echo "🔧 FORCING COMPLETE REBUILD ON DROPLET"
echo "======================================="

# Navigate to app directory
cd /root/security-monitor || exit 1

# Stop and remove ALL containers and images
echo "🛑 Stopping all containers..."
docker-compose down

echo "🗑️ Removing Docker images to force rebuild..."
docker rmi security-monitor_security-monitor 2>/dev/null || true
docker rmi $(docker images -f "dangling=true" -q) 2>/dev/null || true

# Clear any cached layers
echo "🧹 Pruning Docker system..."
docker system prune -f

# Pull latest code
echo "📥 Pulling latest from GitHub..."
git pull origin master

# Show that we have the logo in the code
echo "✅ Verifying GardaWorld logo in source code:"
grep -n "garda" templates/login.html | head -3

# Build completely fresh
echo "🔨 Building fresh Docker image (no cache)..."
docker-compose build --no-cache --pull

# Start fresh containers
echo "🚀 Starting fresh containers..."
docker-compose up -d

# Wait for container to be ready
echo "⏳ Waiting for container to start..."
sleep 5

# Verify the logo is in the running container
echo "🔍 Checking if logo is in RUNNING container:"
docker-compose exec -T security-monitor grep "garda" /app/templates/login.html | head -2

# Show container status
echo ""
echo "📊 Container status:"
docker-compose ps

# Test the actual site
echo ""
echo "🌐 Testing site accessibility:"
curl -I http://$(curl -s ifconfig.me) 2>/dev/null | head -3

echo ""
echo "✅ Force update complete!"
echo ""
echo "🔑 Test login at: http://$(curl -s ifconfig.me)"
echo "   Username: admin"
echo "   Password: changeme123"
echo ""
echo "If login still fails, check container logs:"
echo "   docker-compose logs --tail=50"