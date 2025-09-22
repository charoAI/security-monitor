#!/bin/bash

# Security Monitor - Automated Setup Script
# Run this on your Digital Ocean droplet

set -e

echo "========================================"
echo "Security Monitor Setup Script"
echo "========================================"

# Update system
echo "Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install dependencies
echo "Installing system dependencies..."
sudo apt install -y python3-pip python3-venv git build-essential libxml2-dev libxslt-dev

# Create application directory
echo "Setting up application directory..."
mkdir -p ~/security-monitor
cd ~/security-monitor

# Clone repository (you'll need to update this with your repo URL)
echo "Please enter your GitHub repository URL:"
read REPO_URL
git clone $REPO_URL .

# Create virtual environment
echo "Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install Python packages
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Set up environment file
echo "Setting up environment configuration..."
cp .env.example .env

echo ""
echo "========================================"
echo "IMPORTANT: Manual Configuration Required"
echo "========================================"
echo "1. Edit the .env file with your email settings:"
echo "   nano .env"
echo ""
echo "2. Test email configuration:"
echo "   python main.py test --email your@email.com"
echo ""
echo "3. Create systemd service:"
echo "   sudo nano /etc/systemd/system/security-monitor.service"
echo ""
echo "4. Start the service:"
echo "   sudo systemctl enable security-monitor"
echo "   sudo systemctl start security-monitor"
echo ""
echo "Setup script completed!"
echo "========================================"