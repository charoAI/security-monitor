"""
WSGI entry point for production deployment with Gunicorn
"""
import os
from dashboard import app
from report_scheduler import get_scheduler

# Start the scheduler in a background thread
scheduler = get_scheduler()
scheduler.start()

if __name__ == "__main__":
    app.run()