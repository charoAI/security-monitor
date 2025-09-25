import feedparser
from datetime import datetime
from bs4 import BeautifulSoup

# Security RSS feeds
feeds = [
    "https://krebsonsecurity.com/feed/",
    "https://feeds.feedburner.com/TheHackersNews",
    "https://www.schneier.com/blog/atom.xml"
]

# Also save to HTML file
html = f"""<html>
<head><title>Security Report - {datetime.now().strftime('%B %d, %Y')}</title>
<style>
    body {{ font-family: Arial; max-width: 800px; margin: 40px auto; padding: 0 20px; }}
    h1 {{ color: #333; border-bottom: 3px solid #0066cc; padding-bottom: 10px; }}
    h2 {{ color: #0066cc; margin-top: 30px; }}
    .article {{ background: #f5f5f5; padding: 15px; margin: 15px 0; border-left: 4px solid #0066cc; }}
    .summary {{ color: #555; margin: 10px 0; }}
    a {{ color: #0066cc; }}
</style>
</head>
<body>
<h1>Security Intelligence Report</h1>
<p>Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
"""

print(f"\nSECURITY REPORT - {datetime.now().strftime('%B %d, %Y')}\n{'='*50}\n")

for feed_url in feeds:
    feed = feedparser.parse(feed_url)
    print(f"\n{feed.feed.title}:")
    print("-" * len(feed.feed.title))

    html += f"<h2>{feed.feed.title}</h2>"

    for entry in feed.entries[:3]:  # Just top 3 stories
        # Clean summary
        summary = BeautifulSoup(entry.get('summary', ''), 'html.parser').get_text()[:300]

        print(f"• {entry.title}")
        print(f"  {summary}...")
        print(f"  Read more: {entry.link}\n")

        html += f"""<div class="article">
            <h3>{entry.title}</h3>
            <div class="summary">{summary}...</div>
            <a href="{entry.link}" target="_blank">Read full article →</a>
        </div>"""

html += "</body></html>"

# Save HTML report
with open("security_report.html", "w", encoding="utf-8") as f:
    f.write(html)

print(f"\n{'='*50}")
print("HTML report saved as 'security_report.html'")
print("Open it in your browser to see the formatted version.")