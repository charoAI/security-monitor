import logging
import schedule
import time
import argparse
from datetime import datetime
from pathlib import Path

from config import Config
from source_manager import SourceManager
from feed_collector import FeedCollector
from report_generator import ReportGenerator
from email_sender import EmailSender

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('security_monitor.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class SecurityMonitor:
    def __init__(self):
        self.config = Config()
        self.source_manager = SourceManager()
        self.feed_collector = FeedCollector()
        self.report_generator = ReportGenerator()
        
        # Initialize email sender if configured
        if self.config.SMTP_USERNAME and self.config.SMTP_PASSWORD:
            self.email_sender = EmailSender(
                self.config.SMTP_SERVER,
                self.config.SMTP_PORT,
                self.config.SMTP_USERNAME,
                self.config.SMTP_PASSWORD
            )
        else:
            self.email_sender = None
            logger.warning("Email configuration not complete. Email sending disabled.")
    
    def run_collection_and_report(self):
        logger.info("Starting security report generation...")
        
        try:
            # Get active sources
            active_sources = self.source_manager.get_active_sources()
            logger.info(f"Found {len(active_sources)} active sources")
            
            if not active_sources:
                logger.warning("No active sources found. Skipping report generation.")
                return
            
            # Collect articles
            articles = self.feed_collector.collect_all(active_sources)
            logger.info(f"Collected {len(articles)} articles")
            
            if not articles:
                logger.warning("No articles collected. Skipping report generation.")
                return
            
            # Save collected data
            collection_file = self.feed_collector.save_collection(articles)
            
            # Generate reports
            html_report, text_report = self.report_generator.generate_report(articles)
            
            # Send email if configured
            if self.email_sender and self.config.EMAIL_RECIPIENTS:
                success = self.email_sender.send_report(
                    self.config.EMAIL_RECIPIENTS,
                    html_report,
                    text_report
                )
                if success:
                    logger.info("Report emailed successfully")
                else:
                    logger.error("Failed to email report")
            else:
                logger.info("Email not configured or no recipients. Report saved locally only.")
            
            logger.info("Security report generation completed successfully")
            
        except Exception as e:
            logger.error(f"Error during report generation: {e}", exc_info=True)
    
    def test_email(self, recipient: str):
        if not self.email_sender:
            logger.error("Email not configured")
            return False
        
        return self.email_sender.send_test_email(recipient)
    
    def add_source(self, name: str, url: str, source_type: str = "rss", 
                   category: str = "general"):
        return self.source_manager.add_source(name, url, source_type, category)
    
    def remove_source(self, url: str):
        return self.source_manager.remove_source(url)
    
    def blacklist_source(self, url: str):
        return self.source_manager.blacklist_source(url)
    
    def list_sources(self, category: str = None):
        sources = self.source_manager.list_sources(category)
        for source in sources:
            status = "Active" if source['active'] else "Inactive"
            print(f"- {source['name']} ({source['category']}) - {status}")
            print(f"  URL: {source['url']}")
    
    def start_scheduler(self):
        # Schedule daily report
        schedule_time = self.config.REPORT_TIME
        schedule.every().day.at(schedule_time).do(self.run_collection_and_report)
        
        logger.info(f"Scheduler started. Daily report scheduled for {schedule_time}")
        logger.info("Press Ctrl+C to stop...")
        
        # Run immediately on start
        self.run_collection_and_report()
        
        # Keep running
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            logger.info("Scheduler stopped by user")

def main():
    parser = argparse.ArgumentParser(description='Security Monitor System')
    parser.add_argument('command', choices=['run', 'test', 'schedule', 'add-source', 
                                           'remove-source', 'blacklist', 'list-sources'],
                       help='Command to execute')
    parser.add_argument('--name', help='Source name (for add-source)')
    parser.add_argument('--url', help='Source URL')
    parser.add_argument('--type', default='rss', help='Source type (default: rss)')
    parser.add_argument('--category', default='general', 
                       help='Source category (default: general)')
    parser.add_argument('--email', help='Email address (for test command)')
    
    args = parser.parse_args()
    
    monitor = SecurityMonitor()
    
    if args.command == 'run':
        # Run collection and report once
        monitor.run_collection_and_report()
    
    elif args.command == 'test':
        # Test email configuration
        if not args.email:
            print("Please provide an email address with --email")
        else:
            success = monitor.test_email(args.email)
            if success:
                print(f"Test email sent to {args.email}")
            else:
                print("Failed to send test email. Check logs for details.")
    
    elif args.command == 'schedule':
        # Start the scheduler
        monitor.start_scheduler()
    
    elif args.command == 'add-source':
        if not args.name or not args.url:
            print("Please provide --name and --url")
        else:
            success = monitor.add_source(args.name, args.url, args.type, args.category)
            if success:
                print(f"Added source: {args.name}")
            else:
                print("Failed to add source. It may already exist.")
    
    elif args.command == 'remove-source':
        if not args.url:
            print("Please provide --url")
        else:
            success = monitor.remove_source(args.url)
            if success:
                print(f"Removed source: {args.url}")
            else:
                print("Source not found")
    
    elif args.command == 'blacklist':
        if not args.url:
            print("Please provide --url")
        else:
            success = monitor.blacklist_source(args.url)
            if success:
                print(f"Blacklisted source: {args.url}")
            else:
                print("Source already blacklisted")
    
    elif args.command == 'list-sources':
        monitor.list_sources(args.category)

if __name__ == '__main__':
    main()