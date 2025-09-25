import os
from pathlib import Path
from dotenv import load_dotenv
from typing import List

load_dotenv()

class Config:
    BASE_DIR = Path(__file__).parent
    DATA_DIR = BASE_DIR / "data"
    REPORTS_DIR = BASE_DIR / "reports"

    # Email settings
    SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))

    # Try to get credentials from environment first, then Windows Credential Manager
    SMTP_USERNAME = os.getenv("SMTP_USERNAME")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")

    if not SMTP_USERNAME or not SMTP_PASSWORD:
        try:
            from secure_config import SecureConfig
            stored_email, stored_password = SecureConfig.get_credentials()
            if stored_email and stored_password:
                SMTP_USERNAME = stored_email
                SMTP_PASSWORD = stored_password
        except:
            pass

    EMAIL_RECIPIENTS = os.getenv("EMAIL_RECIPIENTS", "").split(",")

    # API Keys
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

    # Database
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./security_monitor.db")

    # Scheduling
    REPORT_TIME = os.getenv("REPORT_TIME", "08:00")

    # Create directories
    DATA_DIR.mkdir(exist_ok=True)
    REPORTS_DIR.mkdir(exist_ok=True)