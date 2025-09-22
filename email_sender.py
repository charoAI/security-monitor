import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime
from typing import List, Optional
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class EmailSender:
    def __init__(self, smtp_server: str, smtp_port: int, 
                 username: str, password: str):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
    
    def send_report(self, recipients: List[str], html_content: str, 
                   text_content: str, attachments: List[str] = None) -> bool:
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"Security Intelligence Report - {datetime.now().strftime('%B %d, %Y')}"
            msg['From'] = self.username
            msg['To'] = ', '.join(recipients)
            
            # Add text and HTML parts
            text_part = MIMEText(text_content, 'plain')
            html_part = MIMEText(html_content, 'html')
            
            msg.attach(text_part)
            msg.attach(html_part)
            
            # Add attachments if any
            if attachments:
                for filepath in attachments:
                    self._attach_file(msg, filepath)
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.username, self.password)
                server.send_message(msg)
            
            logger.info(f"Report sent successfully to {len(recipients)} recipients")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return False
    
    def _attach_file(self, msg: MIMEMultipart, filepath: str) -> None:
        try:
            path = Path(filepath)
            if not path.exists():
                logger.warning(f"Attachment file not found: {filepath}")
                return
            
            with open(path, 'rb') as f:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(f.read())
            
            encoders.encode_base64(part)
            part.add_header(
                'Content-Disposition',
                f'attachment; filename= {path.name}'
            )
            msg.attach(part)
            logger.info(f"Attached file: {path.name}")
            
        except Exception as e:
            logger.error(f"Failed to attach file {filepath}: {e}")
    
    def send_test_email(self, recipient: str) -> bool:
        test_message = f"""
Test Email from Security Monitor System
{'=' * 40}

This is a test email to verify your email configuration.

Timestamp: {datetime.now().isoformat()}
SMTP Server: {self.smtp_server}:{self.smtp_port}

If you receive this email, your configuration is working correctly.
"""
        
        try:
            msg = MIMEText(test_message)
            msg['Subject'] = "Security Monitor - Test Email"
            msg['From'] = self.username
            msg['To'] = recipient
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.username, self.password)
                server.send_message(msg)
            
            logger.info(f"Test email sent to {recipient}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send test email: {e}")
            return False