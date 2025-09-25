import feedparser
import json
from pathlib import Path

def test_feeds():
    """Test which RSS feeds are actually working and returning Ukraine content"""
    
    # Load sources
    sources_file = Path('sources_config.json')
    if sources_file.exists():
        with open(sources_file, 'r') as f:
            data = json.load(f)
            sources = data['sources']
    else:
        print("No sources file found. Run the dashboard first.")
        return
    
    print(f"Testing {len(sources)} sources...\n")
    
    total_articles = 0
    ukraine_articles = 0
    working_feeds = 0
    
    for source in sources:
        if not source.get('active', True):
            continue
            
        try:
            feed = feedparser.parse(source['url'])
            
            if len(feed.entries) > 0:
                working_feeds += 1
                print(f"✓ {source['name']:30} - {len(feed.entries)} articles")
                
                # Check for Ukraine mentions
                ukraine_count = 0
                for entry in feed.entries[:20]:
                    title = entry.get('title', '').lower()
                    summary = entry.get('summary', '').lower()
                    description = entry.get('description', '').lower()
                    
                    content = f"{title} {summary} {description}"
                    
                    if 'ukraine' in content or 'ukrainian' in content or 'kyiv' in content or 'kiev' in content:
                        ukraine_count += 1
                        ukraine_articles += 1
                        if ukraine_count <= 2:  # Show first 2 Ukraine articles
                            print(f"    → Ukraine article: {entry.get('title', 'No title')[:60]}...")
                
                total_articles += len(feed.entries)
                
                if ukraine_count > 0:
                    print(f"    Found {ukraine_count} Ukraine-related articles")
            else:
                print(f"✗ {source['name']:30} - No articles (feed might be broken)")
                
        except Exception as e:
            print(f"✗ {source['name']:30} - Error: {str(e)[:50]}")
    
    print(f"\n" + "="*60)
    print(f"Summary:")
    print(f"  Working feeds: {working_feeds}/{len(sources)}")
    print(f"  Total articles: {total_articles}")
    print(f"  Ukraine-related articles: {ukraine_articles}")
    print("="*60)

if __name__ == "__main__":
    test_feeds()