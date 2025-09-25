"""Test Haiti RSS feeds to verify they're working"""
import json
import feedparser
from datetime import datetime

def test_haiti_feeds():
    # Load sources
    with open('sources_config.json', 'r') as f:
        config = json.load(f)

    haiti_sources = []
    haiti_keywords = ['haiti', 'haitian', 'port-au-prince', 'google news - haiti']

    print("=== TESTING HAITI RSS FEEDS ===\n")

    for source in config['sources']:
        # Check if this is a Haiti-related source
        name_lower = source['name'].lower()
        if any(keyword in name_lower for keyword in haiti_keywords):
            haiti_sources.append(source)
            print(f"Found Haiti source: {source['name']}")

    print(f"\nTotal Haiti-specific sources: {len(haiti_sources)}\n")
    print("=" * 50)

    # Test each Haiti feed
    total_articles = 0
    working_feeds = 0

    for source in haiti_sources:
        if not source['active']:
            print(f"\n[SKIPPED] {source['name']} - inactive")
            continue

        print(f"\n[TESTING] {source['name']}")
        print(f"URL: {source['url']}")

        try:
            feed = feedparser.parse(source['url'])

            if hasattr(feed, 'status'):
                print(f"HTTP Status: {feed.status}")

            if feed.entries:
                working_feeds += 1
                article_count = len(feed.entries)
                total_articles += article_count
                print(f"[OK] Found {article_count} articles")

                # Show first 3 article titles
                print("Recent articles:")
                for i, entry in enumerate(feed.entries[:3]):
                    title = entry.get('title', 'No title')
                    print(f"  {i+1}. {title[:80]}...")
            else:
                print("[FAIL] No articles found")
                if hasattr(feed, 'bozo_exception'):
                    print(f"  Error: {feed.bozo_exception}")

        except Exception as e:
            print(f"[ERROR] Error parsing feed: {e}")

    print("\n" + "=" * 50)
    print(f"\nRESULTS:")
    print(f"- Working feeds: {working_feeds}/{len(haiti_sources)}")
    print(f"- Total articles available: {total_articles}")

    # Also test general news sources for Haiti content
    print("\n" + "=" * 50)
    print("\nTESTING GENERAL NEWS SOURCES FOR HAITI CONTENT:")

    general_sources = ['BBC World News', 'CNN World', 'Reuters World News', 'AP News']
    haiti_articles_in_general = 0

    for source in config['sources']:
        if source['name'] in general_sources and source['active']:
            print(f"\n[CHECKING] {source['name']}")
            try:
                feed = feedparser.parse(source['url'])
                haiti_count = 0

                for entry in feed.entries:
                    title = entry.get('title', '').lower()
                    summary = entry.get('summary', '').lower()

                    if 'haiti' in title or 'haiti' in summary:
                        haiti_count += 1
                        print(f"  Found Haiti article: {entry.get('title', '')[:60]}...")

                if haiti_count > 0:
                    haiti_articles_in_general += haiti_count
                    print(f"  [OK] Total Haiti articles: {haiti_count}")
                else:
                    print(f"  No Haiti articles currently")

            except Exception as e:
                print(f"  Error: {e}")

    print(f"\nHaiti articles in general news feeds: {haiti_articles_in_general}")
    print(f"\nTOTAL HAITI COVERAGE: {total_articles + haiti_articles_in_general} articles")

if __name__ == "__main__":
    test_haiti_feeds()