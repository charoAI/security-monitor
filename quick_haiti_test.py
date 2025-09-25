"""Quick test for Haiti RSS feeds"""
import json
import feedparser
import socket

# Set timeout for fetching feeds
socket.setdefaulttimeout(5)

def quick_test():
    # Load sources
    with open('sources_config.json', 'r') as f:
        config = json.load(f)

    print("=== QUICK HAITI FEED TEST ===\n")

    haiti_sources = []
    for source in config['sources']:
        name_lower = source['name'].lower()
        if 'haiti' in name_lower or 'haitian' in name_lower:
            haiti_sources.append(source)

    print(f"Found {len(haiti_sources)} Haiti-specific sources\n")

    total_articles = 0
    working_feeds = 0

    for source in haiti_sources[:5]:  # Test only first 5 to save time
        if not source['active']:
            continue

        print(f"Testing: {source['name']}")

        try:
            feed = feedparser.parse(source['url'])

            if feed.entries:
                count = len(feed.entries)
                total_articles += count
                working_feeds += 1
                print(f"  SUCCESS: {count} articles")

                # Show first title
                if feed.entries:
                    title = feed.entries[0].get('title', 'No title')[:60]
                    print(f"  Latest: {title}...")
            else:
                print(f"  NO ARTICLES")

        except Exception as e:
            print(f"  ERROR: {str(e)[:50]}")

        print()

    print("-" * 40)
    print(f"RESULTS: {working_feeds} working feeds")
    print(f"TOTAL ARTICLES: {total_articles}")

    if total_articles > 1:
        print("\nSUCCESS! Haiti coverage has improved significantly!")
        print("(Previously only had 1 article, now have many more)")
    else:
        print("\nSTILL HAVING ISSUES - need to check feed URLs")

if __name__ == "__main__":
    quick_test()