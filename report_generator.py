from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple
import json
from pathlib import Path
import logging
from collections import defaultdict
import re

logger = logging.getLogger(__name__)

class ReportGenerator:
    def __init__(self, reports_dir: str = "reports"):
        self.reports_dir = Path(reports_dir)
        self.reports_dir.mkdir(exist_ok=True)
    
    def generate_report(self, articles: List[Dict[str, Any]]) -> Tuple[str, str]:
        # Group articles by category
        categorized = self._categorize_articles(articles)
        
        # Generate HTML and text versions
        html_report = self._generate_html_report(categorized)
        text_report = self._generate_text_report(categorized)
        
        # Save reports
        timestamp = datetime.now().strftime('%Y%m%d')
        html_path = self.reports_dir / f"security_report_{timestamp}.html"
        text_path = self.reports_dir / f"security_report_{timestamp}.txt"
        
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_report)
        
        with open(text_path, 'w', encoding='utf-8') as f:
            f.write(text_report)
        
        logger.info(f"Reports generated: {html_path}, {text_path}")
        return html_report, text_report
    
    def _categorize_articles(self, articles: List[Dict[str, Any]]) -> Dict[str, List[Dict]]:
        categorized = defaultdict(list)
        for article in articles:
            category = article.get('category', 'general')
            categorized[category].append(article)
        
        # Sort articles within each category by publication date
        for category in categorized:
            categorized[category].sort(
                key=lambda x: x.get('published', ''),
                reverse=True
            )
        
        return dict(categorized)
    
    def _generate_html_report(self, categorized: Dict[str, List[Dict]]) -> str:
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Security Intelligence Report - {datetime.now().strftime('%B %d, %Y')}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            max-width: 900px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f4f4f4;
        }}
        h1 {{
            color: #333;
            border-bottom: 3px solid #0066cc;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #0066cc;
            margin-top: 30px;
            border-bottom: 1px solid #ccc;
            padding-bottom: 5px;
        }}
        .article {{
            background: white;
            margin: 15px 0;
            padding: 15px;
            border-left: 4px solid #0066cc;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }}
        .article-title {{
            font-weight: bold;
            color: #333;
            margin-bottom: 5px;
        }}
        .article-meta {{
            color: #666;
            font-size: 0.9em;
            margin-bottom: 10px;
        }}
        .article-summary {{
            color: #444;
            margin-bottom: 10px;
        }}
        .article-link {{
            color: #0066cc;
            text-decoration: none;
        }}
        .article-link:hover {{
            text-decoration: underline;
        }}
        .source-ref {{
            color: #888;
            font-size: 0.85em;
            font-style: italic;
        }}
        .footer {{
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #ccc;
            color: #666;
            font-size: 0.9em;
        }}
        .sources-section {{
            background: #f9f9f9;
            padding: 15px;
            margin-top: 30px;
            border-radius: 5px;
        }}
    </style>
</head>
<body>
    <h1>Security Intelligence Report</h1>
    <p><strong>Date:</strong> {datetime.now().strftime('%B %d, %Y')}</p>
    <p><strong>Report Period:</strong> Last 24 hours</p>
    <p><strong>Total Articles:</strong> {sum(len(articles) for articles in categorized.values())}</p>
"""
        
        # Add categorized articles
        category_titles = {
            'government': 'Government Advisories',
            'geopolitical': 'Geopolitical Security',
            'news': 'Security News',
            'blog': 'Expert Analysis',
            'general': 'General Updates'
        }
        
        ref_counter = 1
        source_refs = {}
        
        for category, articles in categorized.items():
            if not articles:
                continue
            
            title = category_titles.get(category, category.title())
            html += f"    <h2>{title}</h2>\n"
            
            for article in articles[:10]:  # Limit to 10 articles per category
                # Track source reference
                source_key = article['source']
                if source_key not in source_refs:
                    source_refs[source_key] = {
                        'ref': ref_counter,
                        'url': article['source_url']
                    }
                    ref_counter += 1
                
                ref_num = source_refs[source_key]['ref']
                
                html += f"""    <div class="article">
        <div class="article-title">{article['title']}</div>
        <div class="article-meta">
            Source: {article['source']} [{ref_num}] | 
            Published: {self._format_date(article.get('published', ''))}
        </div>
        <div class="article-summary">{article['summary'][:300]}...</div>
        <a href="{article['link']}" class="article-link" target="_blank">Read full article →</a>
    </div>
"""
        
        # Add sources section
        html += """    <div class="sources-section">
        <h2>Sources Referenced</h2>
        <ol>
"""
        
        for source, info in sorted(source_refs.items(), key=lambda x: x[1]['ref']):
            html += f"""            <li>{source}: <a href="{info['url']}" target="_blank">{info['url']}</a></li>
"""
        
        html += """        </ol>
    </div>
    
    <div class="footer">
        <p>This report was automatically generated by the Security Monitor system.</p>
        <p>For questions or to modify source lists, please contact your system administrator.</p>
    </div>
</body>
</html>"""
        
        return html
    
    def _generate_text_report(self, categorized: Dict[str, List[Dict]]) -> str:
        text = f"""SECURITY INTELLIGENCE REPORT
{'=' * 60}
Date: {datetime.now().strftime('%B %d, %Y')}
Report Period: Last 24 hours
Total Articles: {sum(len(articles) for articles in categorized.values())}
{'=' * 60}

"""
        
        category_titles = {
            'government': 'GOVERNMENT ADVISORIES',
            'geopolitical': 'GEOPOLITICAL SECURITY',
            'news': 'SECURITY NEWS',
            'blog': 'EXPERT ANALYSIS',
            'general': 'GENERAL UPDATES'
        }
        
        ref_counter = 1
        source_refs = {}
        
        for category, articles in categorized.items():
            if not articles:
                continue
            
            title = category_titles.get(category, category.upper())
            text += f"\n{title}\n{'-' * len(title)}\n\n"
            
            for i, article in enumerate(articles[:10], 1):
                # Track source reference
                source_key = article['source']
                if source_key not in source_refs:
                    source_refs[source_key] = {
                        'ref': ref_counter,
                        'url': article['source_url']
                    }
                    ref_counter += 1
                
                ref_num = source_refs[source_key]['ref']
                
                text += f"{i}. {article['title']}\n"
                text += f"   Source: {article['source']} [{ref_num}]\n"
                text += f"   Published: {self._format_date(article.get('published', ''))}\n"
                text += f"   Summary: {article['summary'][:200]}...\n"
                text += f"   Link: {article['link']}\n\n"
        
        # Add sources section
        text += f"\n{'=' * 60}\nSOURCES REFERENCED\n{'=' * 60}\n\n"
        
        for source, info in sorted(source_refs.items(), key=lambda x: x[1]['ref']):
            text += f"[{info['ref']}] {source}: {info['url']}\n"
        
        text += f"\n{'=' * 60}\n"
        text += "This report was automatically generated by the Security Monitor system.\n"
        text += "For questions or to modify source lists, please contact your system administrator.\n"
        
        return text
    
    def _format_date(self, date_str: str) -> str:
        try:
            dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            return dt.strftime('%B %d, %Y at %I:%M %p')
        except:
            return date_str