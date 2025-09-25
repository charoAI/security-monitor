#!/bin/bash

# Deployment script to update DigitalOcean droplet with latest changes
# Run this ON your droplet after SSH-ing in

echo "🚀 Updating Security Monitor on DigitalOcean..."

# Navigate to app directory
cd /root/security-monitor || exit 1

# Stop running containers
echo "📦 Stopping current containers..."
docker-compose down

# Pull latest changes from GitHub
echo "🔄 Pulling latest code from GitHub..."
git pull origin master

# Rebuild Docker image with new changes
echo "🔨 Rebuilding Docker image..."
docker-compose build --no-cache

# Start containers with new code
echo "🚀 Starting updated containers..."
docker-compose up -d

# Show container status
echo "✅ Deployment complete! Container status:"
docker-compose ps

# Show logs (last 20 lines)
echo ""
echo "📋 Recent logs:"
docker-compose logs --tail=20

echo ""
echo "🌐 Your updated app is available at: http://$(curl -s ifconfig.me)"
echo ""
echo "⚠️  IMPORTANT NOTES:"
echo "1. Default admin credentials: username=admin, password=changeme123"
echo "2. Change the admin password immediately at /admin"
echo "3. Users can request accounts at /register"
echo "4. Admin panel available at /admin"
echo ""
echo "✨ New features deployed:"
echo "- User registration system"
echo "- Admin panel for user management"
echo "- Per-user email configuration"
echo "- Activity tracking and analytics"