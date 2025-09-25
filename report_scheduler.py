"""
Report Scheduler Service
Runs scheduled reports and sends them via email
"""
import time
import threading
import json
from datetime import datetime
from typing import List, Dict
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os
from dotenv import load_dotenv

from scheduled_reports import ScheduledReport
from report_synthesizer import IntelligenceSynthesizer
from google_news_engine import GoogleNewsEngine
from article_extractor import ArticleExtractor
from fast_llm_synthesizer import FastLLMSynthesizer

load_dotenv()

class ReportScheduler:
    def __init__(self):
        self.db = ScheduledReport()
        self.running = False
        self.thread = None
        self.check_interval = 60  # Check every minute

        # Email configuration
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', 587))
        self.smtp_username = os.getenv('SMTP_USERNAME')
        self.smtp_password = os.getenv('SMTP_PASSWORD')

    def start(self):
        """Start the scheduler in a background thread"""
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._run_scheduler, daemon=True)
            self.thread.start()
            print("Report scheduler started")

    def stop(self):
        """Stop the scheduler"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        print("Report scheduler stopped")

    def _run_scheduler(self):
        """Main scheduler loop"""
        while self.running:
            try:
                # Check for due reports
                due_reports = self.db.get_due_reports()

                for report in due_reports:
                    try:
                        print(f"Running scheduled report: {report['name']}")
                        self._run_report(report)
                    except Exception as e:
                        print(f"Error running report {report['name']}: {str(e)}")
                        self.db.mark_report_run(
                            report['id'],
                            status='error',
                            error_message=str(e)
                        )

            except Exception as e:
                print(f"Scheduler error: {str(e)}")

            # Wait before next check
            time.sleep(self.check_interval)

    def _run_report(self, report: Dict):
        """Run a single report"""
        try:
            # Generate the report
            report_data = self._generate_report(
                report['countries'],
                report.get('prompt', ''),
                report['schedule_type']
            )

            # Format the report
            formatted_report = self._format_report(
                report['name'],
                report['countries'],
                report.get('prompt', ''),
                report_data
            )

            # Send via email if recipients configured
            if report['email_recipients']:
                self._send_email_report(
                    report['email_recipients'],
                    report['name'],
                    formatted_report,
                    report_data
                )

            # Mark as successful
            self.db.mark_report_run(
                report['id'],
                status='success',
                report_data=json.dumps({
                    'summary': formatted_report[:1000],
                    'article_count': len(report_data.get('articles', [])),
                    'timestamp': datetime.now().isoformat()
                })
            )

            print(f"Report '{report['name']}' completed successfully")

        except Exception as e:
            raise Exception(f"Report generation failed: {str(e)}")

    def _generate_report(self, countries: List[str], prompt: str, schedule_type: str) -> Dict:
        """Generate report data for specified countries with time-based filtering"""
        google_engine = GoogleNewsEngine()
        synthesizer = IntelligenceSynthesizer()
        articles = []

        # Determine time window based on schedule type
        time_windows = {
            'hourly': ('1h', 0.04),  # 1 hour, 0.04 days (~1 hour)
            'daily': ('1d', 1),       # 24 hours, 1 day
            'weekly': ('7d', 7),      # 7 days
            'monthly': ('30d', 30)    # 30 days
        }

        when_param, days_back = time_windows.get(schedule_type, ('1d', 1))

        # Fetch news for each country
        for country in countries:
            print(f"  Fetching news for {country} (last {when_param})...")

            # Get general country news with appropriate time window
            country_articles = google_engine.get_country_news(country, days_back=days_back)

            # If prompt specified, use it to create targeted searches
            if prompt:
                # Extract key themes from prompt for searching
                search_terms = self._extract_search_terms(prompt)
                for term in search_terms:
                    query = f"{country} {term}"
                    prompt_articles = google_engine.search(query, when=when_param)
                    country_articles.extend(prompt_articles)

            # Add to main list with country tag
            for article in country_articles:
                article['location'] = [country]
                articles.append(article)

        # Remove duplicates based on URL
        seen_urls = set()
        unique_articles = []
        for article in articles:
            if article['link'] not in seen_urls:
                seen_urls.add(article['link'])
                unique_articles.append(article)

        # Synthesize reports by country
        country_reports = synthesizer.synthesize_by_country(unique_articles, countries)

        # Add threat assessment for each country
        for country, data in country_reports.items():
            # Calculate threat level based on articles
            data['threat_level'] = synthesizer.assess_threat_level(data)

        # Try to add LLM narratives if available
        try:
            if os.getenv('GEMINI_API_KEY'):
                fast_synth = FastLLMSynthesizer()
                for country, data in country_reports.items():
                    # Pass prompt to LLM for focused analysis
                    result = fast_synth.synthesize_country_report(country, data['articles'], custom_prompt=prompt)
                    data['narrative'] = result['narrative']
                    data['articles_with_content'] = result['articles_with_content']
        except:
            pass  # Continue without LLM if it fails

        return {
            'countries': country_reports,
            'articles': unique_articles,
            'total_articles': len(unique_articles),
            'generated_at': datetime.now().isoformat()
        }

    def _format_report(self, report_name: str, countries: List[str],
                      prompt: str, report_data: Dict) -> str:
        """Format report data into readable text"""
        lines = []
        lines.append("=" * 80)
        lines.append(f"GARDAWORLD INTELLIGENCE REPORT")
        lines.append(f"Report: {report_name}")
        lines.append(f"Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p %Z')}")
        lines.append(f"Countries: {', '.join(countries)}")
        if prompt:
            lines.append(f"Focus Areas: {prompt[:100]}...")
        lines.append("=" * 80)
        lines.append("")

        # Executive Summary
        lines.append("EXECUTIVE SUMMARY")
        lines.append("-" * 40)
        lines.append(f"Total Articles Analyzed: {report_data['total_articles']}")
        lines.append("")

        # Country sections
        for country, data in report_data['countries'].items():
            lines.append(f"\n{country.upper()}")
            lines.append("=" * len(country))
            lines.append("")

            # Threat Assessment
            threat_level = data.get('threat_level', 'Unknown')
            lines.append(f"Threat Level: {threat_level}")
            lines.append(f"Articles: {len(data['articles'])}")
            lines.append(f"Sources: {', '.join(list(data['sources'])[:5])}")
            lines.append("")

            # Narrative or Key Points
            if 'narrative' in data and data['narrative']:
                lines.append("SITUATION ANALYSIS:")
                lines.append(data['narrative'])
            elif 'key_points' in data:
                lines.append("KEY DEVELOPMENTS:")
                for point in data['key_points'][:5]:
                    lines.append(f"• {point}")
            lines.append("")

            # Top Articles
            lines.append("TOP ARTICLES:")
            for i, article in enumerate(data['articles'][:5], 1):
                lines.append(f"{i}. {article['title'][:100]}")
                if article.get('summary'):
                    lines.append(f"   {article['summary'][:150]}")
                lines.append(f"   Source: {article.get('source', 'Unknown')}")
                lines.append("")

            lines.append("-" * 40)

        lines.append("\n" + "=" * 80)
        lines.append("END OF REPORT")
        lines.append("GardaWorld - Integrity • Trust • Vigilance • Respect")

        return "\n".join(lines)

    def _send_email_report(self, recipients: List[str], report_name: str,
                          report_text: str, report_data: Dict):
        """Send report via email"""
        if not self.smtp_username or not self.smtp_password:
            print("Email credentials not configured")
            return

        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"GardaWorld Intelligence Report: {report_name}"
            msg['From'] = self.smtp_username
            msg['To'] = ', '.join(recipients)

            # Create HTML version
            html_content = self._create_html_report(report_name, report_data)

            # Attach text and HTML versions
            text_part = MIMEText(report_text, 'plain')
            html_part = MIMEText(html_content, 'html')

            msg.attach(text_part)
            msg.attach(html_part)

            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)

            print(f"Report emailed to {', '.join(recipients)}")

        except Exception as e:
            print(f"Failed to send email: {str(e)}")
            raise

    def _convert_markdown_to_html(self, text: str) -> str:
        """Convert markdown-style formatting to HTML"""
        if not text:
            return text

        # Convert **bold** to <strong>
        import re
        text = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', text)

        # Convert *italic* to <em>
        text = re.sub(r'\*([^*]+)\*', r'<em>\1</em>', text)

        # Convert bullet points
        text = re.sub(r'^\* ', '• ', text, flags=re.MULTILINE)
        text = re.sub(r'^\- ', '• ', text, flags=re.MULTILINE)

        # Convert line breaks to <br> for paragraphs
        text = text.replace('\n\n', '</p><p>')
        text = text.replace('\n', '<br>')

        return f"<p>{text}</p>"

    def _create_html_report(self, report_name: str, report_data: Dict) -> str:
        """Create HTML version of the report"""
        html = f"""
        <html>
        <head>
            <style>
                body {{
                    font-family: 'Segoe UI', Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    background: #f5f5f5;
                }}
                .header {{
                    background: linear-gradient(135deg, #e31e24 0%, #b71c20 100%);
                    color: white;
                    padding: 30px;
                    text-align: center;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                }}
                .header h1 {{
                    margin: 0;
                    font-size: 28px;
                    font-weight: 600;
                    letter-spacing: 1px;
                }}
                .header h2 {{
                    margin: 10px 0 0 0;
                    font-size: 20px;
                    font-weight: 400;
                    opacity: 0.95;
                }}
                .header p {{
                    margin: 10px 0 0 0;
                    font-size: 14px;
                    opacity: 0.9;
                }}
                .content {{
                    max-width: 800px;
                    margin: 20px auto;
                    background: white;
                    border-radius: 8px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.05);
                    overflow: hidden;
                }}
                .executive-summary {{
                    background: #f8f9fa;
                    padding: 20px;
                    border-bottom: 2px solid #e31e24;
                }}
                .country-section {{
                    margin: 0;
                    padding: 25px;
                    border-bottom: 1px solid #eee;
                }}
                .country-section:last-child {{
                    border-bottom: none;
                }}
                .country-section h2 {{
                    color: #e31e24;
                    margin: 0 0 15px 0;
                    font-size: 26px;
                    font-weight: 700;
                    border-bottom: 3px solid #e31e24;
                    padding-bottom: 10px;
                    text-transform: uppercase;
                    letter-spacing: 1px;
                }}
                .threat-assessment {{
                    background: #f8f9fa;
                    padding: 15px;
                    border-radius: 5px;
                    margin: 15px 0;
                }}
                .threat-critical {{
                    color: #d32f2f;
                    font-weight: bold;
                    font-size: 18px;
                }}
                .threat-high {{
                    color: #e31e24;
                    font-weight: bold;
                    font-size: 18px;
                }}
                .threat-moderate {{
                    color: #f39c12;
                    font-weight: bold;
                    font-size: 18px;
                }}
                .threat-low {{
                    color: #27ae60;
                    font-weight: bold;
                    font-size: 18px;
                }}
                .threat-minimal {{
                    color: #4caf50;
                    font-weight: bold;
                    font-size: 18px;
                }}
                .threat-unknown, .threat-undetermined {{
                    color: #757575;
                    font-weight: bold;
                    font-size: 18px;
                }}
                .narrative {{
                    background: white;
                    padding: 15px 0;
                    margin: 15px 0;
                    font-size: 15px;
                    line-height: 1.7;
                }}
                .narrative p {{
                    margin: 10px 0;
                }}
                .narrative strong {{
                    color: #2c3e50;
                }}
                .articles-section {{
                    margin-top: 20px;
                }}
                .articles-section h3 {{
                    color: #2c3e50;
                    font-size: 18px;
                    margin: 20px 0 10px 0;
                    padding-bottom: 5px;
                    border-bottom: 1px solid #ddd;
                }}
                .article {{
                    margin: 15px 0;
                    padding: 15px;
                    background: #f8f9fa;
                    border-radius: 5px;
                    border-left: 3px solid #ddd;
                }}
                .article:hover {{
                    border-left-color: #e31e24;
                    background: #f5f5f5;
                }}
                .article h4 {{
                    margin: 0 0 8px 0;
                    color: #2c3e50;
                    font-size: 16px;
                }}
                .article p {{
                    margin: 8px 0;
                    color: #555;
                    font-size: 14px;
                }}
                .article small {{
                    color: #888;
                    font-size: 12px;
                }}
                .footer {{
                    background: #2c3e50;
                    color: white;
                    text-align: center;
                    padding: 20px;
                    font-size: 13px;
                }}
                .footer p {{
                    margin: 5px 0;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>GARDAWORLD INTELLIGENCE REPORT</h1>
                <h2>{report_name}</h2>
                <p>{datetime.now().strftime('%B %d, %Y at %I:%M %p %Z')}</p>
            </div>
            <div class="content">
                <div class="executive-summary">
                    <h3 style="margin: 0 0 10px 0; color: #2c3e50;">Executive Summary</h3>
                    <p style="margin: 5px 0;"><strong>Total Articles Analyzed:</strong> {report_data['total_articles']}</p>
                    <p style="margin: 5px 0;"><strong>Countries Covered:</strong> {len(report_data['countries'])}</p>
                    <p style="margin: 5px 0;"><strong>Report Period:</strong> Last 24 hours</p>
                </div>
        """

        for country, data in report_data['countries'].items():
            threat_level = data.get('threat_level', 'Unknown')
            threat_class = f"threat-{threat_level.lower()}"

            html += f"""
                <div class="country-section">
                    <h2>{country.upper()}</h2>
                    <div class="threat-assessment">
                        <p class="{threat_class}">⚠️ Threat Level: {threat_level}</p>
                        <p><strong>Articles Analyzed:</strong> {len(data['articles'])}</p>
                        <p><strong>Primary Sources:</strong> {', '.join(list(data.get('sources', []))[:3])}</p>
                    </div>
            """

            if 'narrative' in data and data['narrative']:
                # Convert markdown formatting in narrative to HTML
                formatted_narrative = self._convert_markdown_to_html(data['narrative'])
                html += f"""
                <div class="narrative">
                    <h4 style="margin: 0 0 10px 0; color: #2c3e50; font-size: 18px;">Situation Analysis</h4>
                    {formatted_narrative}
                </div>
                """

            html += """
                <div class="articles-section">
                    <h3>Top Security Articles</h3>
            """

            for i, article in enumerate(data['articles'][:5], 1):
                # Extract and clean article content
                title = article.get('title', 'No title')
                # Remove source from title if it's included
                if ' - ' in title:
                    title_parts = title.rsplit(' - ', 1)
                    if len(title_parts) == 2:
                        title = title_parts[0]
                        article_source = title_parts[1]
                    else:
                        article_source = article.get('source', 'Unknown')
                else:
                    article_source = article.get('source', 'Unknown')

                summary = article.get('summary', article.get('full_content', ''))[:250]
                published = article.get('published', '')

                # Format date if available
                date_str = ""
                if published:
                    try:
                        from datetime import datetime as dt
                        pub_date = dt.fromisoformat(published.replace('Z', '+00:00'))
                        date_str = f" • {pub_date.strftime('%b %d, %Y')}"
                    except:
                        date_str = ""

                html += f"""
                    <div class="article">
                        <h4>{i}. {title}</h4>
                        <p>{summary}{'...' if len(summary) >= 250 else ''}</p>
                        <small>📰 {article_source}{date_str}</small>
                    </div>
                """

            html += """
                </div>
            </div>
            """

        html += """
            </div>
            <div class="footer">
                <p><strong>GARDAWORLD</strong></p>
                <p>Integrity • Trust • Vigilance • Respect</p>
                <p style="font-size: 11px; margin-top: 10px;">
                    This intelligence report is confidential and intended solely for the recipient(s) listed above.
                    Unauthorized distribution is prohibited.
                </p>
            </div>
        </body>
        </html>
        """

        return html

    def _extract_search_terms(self, prompt: str) -> List[str]:
        """Extract key search terms from natural language prompt"""
        # Common security-related keywords to search for
        security_terms = [
            'military', 'terrorist', 'attack', 'threat', 'security', 'protest',
            'violence', 'explosion', 'bombing', 'shooting', 'kidnapping',
            'cyber', 'hack', 'breach', 'coup', 'rebellion', 'insurgency',
            'sanctions', 'embargo', 'conflict', 'war', 'missile', 'nuclear'
        ]

        # Extract terms mentioned in the prompt
        prompt_lower = prompt.lower()
        found_terms = []

        # Check for security terms in prompt
        for term in security_terms:
            if term in prompt_lower:
                found_terms.append(term)

        # If no specific terms found, use general security search
        if not found_terms:
            found_terms = ['security', 'threat', 'military']

        return found_terms[:5]  # Limit to 5 terms to avoid too many API calls

    def run_report_now(self, report_id: int) -> Dict:
        """Manually run a report immediately"""
        report = self.db.get_report(report_id)
        if not report:
            raise ValueError(f"Report {report_id} not found")

        print(f"Manually running report: {report['name']}")
        self._run_report(report)

        return {'status': 'success', 'message': f"Report '{report['name']}' executed successfully"}


# Singleton instance
scheduler_instance = None

def get_scheduler():
    """Get or create the scheduler instance"""
    global scheduler_instance
    if scheduler_instance is None:
        scheduler_instance = ReportScheduler()
    return scheduler_instance


if __name__ == "__main__":
    # Test scheduler
    scheduler = ReportScheduler()
    scheduler.start()

    print("Scheduler running. Press Ctrl+C to stop...")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        scheduler.stop()
        print("\nScheduler stopped")