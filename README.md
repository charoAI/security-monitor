# Security Monitor

An automated security intelligence monitoring system that collects information from credible security and geopolitical sources, generates daily reports with source citations, and emails them to specified recipients.

## Features

- RSS feed collection from multiple security sources
- Source management (add/remove/blacklist)
- Daily automated reports with source citations
- Email delivery of reports
- Categorized content (government advisories, geopolitical, news, expert analysis)
- Configurable scheduling

## Quick Start

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure environment:
```bash
cp .env.example .env
# Edit .env with your SMTP settings and recipients
```

3. Run once:
```bash
python main.py run
```

4. Start scheduler:
```bash
python main.py schedule
```

## Commands

### Run report generation once
```bash
python main.py run
```

### Start daily scheduler
```bash
python main.py schedule
```

### Test email configuration
```bash
python main.py test --email your@email.com
```

### Manage sources
```bash
# List all sources
python main.py list-sources

# Add a new source
python main.py add-source --name "Source Name" --url "https://example.com/feed" --category geopolitical

# Remove a source
python main.py remove-source --url "https://example.com/feed"

# Blacklist a source
python main.py blacklist --url "https://example.com/feed"
```

## Configuration

Edit `.env` file:

- `SMTP_SERVER`: Your SMTP server (default: smtp.gmail.com)
- `SMTP_PORT`: SMTP port (default: 587)
- `SMTP_USERNAME`: Your email address
- `SMTP_PASSWORD`: Your email password or app-specific password
- `EMAIL_RECIPIENTS`: Comma-separated list of recipients
- `REPORT_TIME`: Time to send daily report (24-hour format, default: 08:00)

## Sources

Default sources are configured in `sources.json`. Categories include:
- `government`: Official government security advisories
- `geopolitical`: Geopolitical security analysis
- `news`: Security news outlets
- `blog`: Expert security blogs

## Deployment to Digital Ocean

See `deployment/DEPLOY.md` for detailed Digital Ocean deployment instructions.

## Project Structure

```
security-monitor/
├── main.py              # Main application entry point
├── config.py            # Configuration management
├── source_manager.py    # Source management
├── feed_collector.py    # RSS/web collection
├── report_generator.py  # Report generation
├── email_sender.py      # Email functionality
├── sources.json         # Source configuration
├── requirements.txt     # Python dependencies
├── .env.example         # Environment template
└── deployment/         # Deployment files
    ├── DEPLOY.md       # Deployment guide
    └── setup.sh        # Server setup script
```