# Digital Ocean Deployment Guide

Complete step-by-step guide for deploying the Security Monitor to Digital Ocean.

## Prerequisites

1. Digital Ocean account
2. GitHub account
3. Domain name (optional, for custom email)

## Step 1: Create a Digital Ocean Droplet

1. Log in to [Digital Ocean](https://cloud.digitalocean.com/)
2. Click "Create" > "Droplets"
3. Choose configuration:
   - **Image**: Ubuntu 22.04 LTS
   - **Plan**: Basic
   - **CPU**: Regular Intel with SSD
   - **Size**: $6/month (1GB RAM, 25GB SSD) is sufficient
   - **Region**: Choose closest to you
   - **Authentication**: SSH keys (recommended) or Password
   - **Hostname**: `security-monitor`

4. Click "Create Droplet"

## Step 2: Initial Server Setup

1. SSH into your droplet:
```bash
ssh root@your_droplet_ip
```

2. Update system:
```bash
apt update && apt upgrade -y
```

3. Create a non-root user:
```bash
adduser secmonitor
usermod -aG sudo secmonitor
```

4. Set up firewall:
```bash
ufw allow OpenSSH
ufw allow 80/tcp   # For future web interface
ufw allow 443/tcp  # For HTTPS
ufw enable
```

## Step 3: Install Dependencies

1. Switch to new user:
```bash
su - secmonitor
```

2. Install Python and Git:
```bash
sudo apt install python3-pip python3-venv git -y
```

3. Install system dependencies:
```bash
sudo apt install build-essential libxml2-dev libxslt-dev -y
```

## Step 4: Clone Repository from GitHub

1. Generate SSH key (if needed):
```bash
ssh-keygen -t ed25519 -C "your_email@example.com"
cat ~/.ssh/id_ed25519.pub
# Add this key to your GitHub account
```

2. Clone your repository:
```bash
cd ~
git clone git@github.com:YOUR_USERNAME/security-monitor.git
cd security-monitor
```

## Step 5: Set Up Python Environment

1. Create virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
```

2. Install requirements:
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

## Step 6: Configure Application

1. Copy and edit environment file:
```bash
cp .env.example .env
nano .env
```

2. Configure email settings:
   - For Gmail: Use app-specific password
   - Enable 2FA on your Google account
   - Generate app password at: https://myaccount.google.com/apppasswords

## Step 7: Test the Application

1. Test email configuration:
```bash
python main.py test --email your@email.com
```

2. Run once to verify:
```bash
python main.py run
```

## Step 8: Set Up Systemd Service

1. Create service file:
```bash
sudo nano /etc/systemd/system/security-monitor.service
```

2. Add the following content:
```ini
[Unit]
Description=Security Monitor Service
After=network.target

[Service]
Type=simple
User=secmonitor
WorkingDirectory=/home/secmonitor/security-monitor
Environment="PATH=/home/secmonitor/security-monitor/venv/bin"
ExecStart=/home/secmonitor/security-monitor/venv/bin/python /home/secmonitor/security-monitor/main.py schedule
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

3. Enable and start service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable security-monitor
sudo systemctl start security-monitor
```

4. Check status:
```bash
sudo systemctl status security-monitor
```

## Step 9: Set Up Logging

1. Create log rotation:
```bash
sudo nano /etc/logrotate.d/security-monitor
```

2. Add:
```
/home/secmonitor/security-monitor/security_monitor.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    create 644 secmonitor secmonitor
}
```

## Step 10: Monitoring

1. View logs:
```bash
journalctl -u security-monitor -f
```

2. Check application logs:
```bash
tail -f /home/secmonitor/security-monitor/security_monitor.log
```

## Step 11: Updates and Maintenance

### Update application:
```bash
cd ~/security-monitor
git pull
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart security-monitor
```

### Backup sources configuration:
```bash
cp sources.json sources.json.backup
```

## Step 12: Security Hardening

1. Set up automatic security updates:
```bash
sudo apt install unattended-upgrades
sudo dpkg-reconfigure --priority=low unattended-upgrades
```

2. Install fail2ban:
```bash
sudo apt install fail2ban
```

3. Disable root SSH (after setting up user):
```bash
sudo nano /etc/ssh/sshd_config
# Set: PermitRootLogin no
sudo systemctl restart sshd
```

## Troubleshooting

### Service won't start:
```bash
sudo journalctl -u security-monitor -n 50
```

### Email not sending:
- Check firewall allows outbound SMTP
- Verify app-specific password for Gmail
- Check `.env` configuration

### High memory usage:
- Consider upgrading droplet
- Check for memory leaks in logs

## Cost Estimation

- Droplet: $6/month (1GB RAM)
- Backups: $1.20/month (optional)
- Total: ~$7-8/month

## Next Steps

1. Set up domain name (optional)
2. Configure SSL with Let's Encrypt
3. Add web interface for management
4. Set up database for historical data
5. Configure alerts for failures