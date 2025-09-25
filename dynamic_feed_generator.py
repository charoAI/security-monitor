"""Dynamic Google News RSS feed generator for any country/topic"""
import urllib.parse
import feedparser
import socket

class DynamicFeedGenerator:
    def __init__(self):
        self.base_url = "https://news.google.com/rss/search"
        socket.setdefaulttimeout(10)  # Set timeout for feed fetching

    def build_google_news_url(self, query, language='en-US', country='US'):
        """Build Google News RSS URL for a specific query"""
        params = {
            'q': query,
            'hl': language,
            'gl': country,
            'ceid': f'{country}:{language[:2]}'
        }
        query_string = urllib.parse.urlencode(params)
        return f"{self.base_url}?{query_string}"

    def generate_country_feeds(self, country_name):
        """Generate multiple Google News feeds for a country"""
        feeds = []

        # Security and conflict feed
        feeds.append({
            'name': f'Google News - {country_name} Security',
            'url': self.build_google_news_url(f'{country_name} security conflict violence'),
            'type': 'dynamic',
            'category': 'security'
        })

        # Political feed
        feeds.append({
            'name': f'Google News - {country_name} Politics',
            'url': self.build_google_news_url(f'{country_name} politics government elections'),
            'type': 'dynamic',
            'category': 'politics'
        })

        # Crisis and humanitarian feed
        feeds.append({
            'name': f'Google News - {country_name} Crisis',
            'url': self.build_google_news_url(f'{country_name} crisis humanitarian emergency'),
            'type': 'dynamic',
            'category': 'humanitarian'
        })

        # General news feed
        feeds.append({
            'name': f'Google News - {country_name} News',
            'url': self.build_google_news_url(f'{country_name} news latest'),
            'type': 'dynamic',
            'category': 'general'
        })

        return feeds

    def fetch_country_news(self, country_name, max_per_feed=25):
        """Fetch news for a country from dynamically generated feeds"""
        feeds = self.generate_country_feeds(country_name)
        all_articles = []
        sources_used = set()

        for feed_info in feeds:
            try:
                feed = feedparser.parse(feed_info['url'])

                if feed.entries:
                    for entry in feed.entries[:max_per_feed]:
                        article = {
                            'title': entry.get('title', 'No title'),
                            'summary': entry.get('summary', ''),
                            'link': entry.get('link', ''),
                            'published': entry.get('published', ''),
                            'source': feed_info['name'],
                            'category': feed_info['category']
                        }
                        all_articles.append(article)
                        sources_used.add(feed_info['name'])

                    print(f"  [OK] {feed_info['name']}: {len(feed.entries)} articles found")
                else:
                    print(f"  [EMPTY] {feed_info['name']}: No articles")

            except Exception as e:
                print(f"  [ERROR] {feed_info['name']}: {str(e)[:50]}")

        return all_articles, list(sources_used)

    def get_country_coverage(self, country_name):
        """Get comprehensive news coverage for a country"""
        print(f"\nFetching comprehensive coverage for: {country_name}")
        articles, sources = self.fetch_country_news(country_name)

        # Remove duplicates based on title
        seen_titles = set()
        unique_articles = []
        for article in articles:
            title = article['title'].lower()
            if title not in seen_titles:
                seen_titles.add(title)
                unique_articles.append(article)

        print(f"Total unique articles: {len(unique_articles)} from {len(sources)} sources")
        return unique_articles, sources

    def enhance_existing_sources(self, country_name, existing_articles):
        """Add dynamic feeds to enhance existing source coverage"""
        # Get articles from dynamic feeds
        dynamic_articles, dynamic_sources = self.get_country_coverage(country_name)

        # Merge with existing articles, avoiding duplicates
        existing_titles = {a.get('title', '').lower() for a in existing_articles}

        enhanced_articles = existing_articles.copy()
        added_count = 0

        for article in dynamic_articles:
            if article['title'].lower() not in existing_titles:
                enhanced_articles.append(article)
                added_count += 1

        print(f"Enhanced {country_name} coverage: Added {added_count} new articles")
        print(f"Total articles: {len(enhanced_articles)} (was {len(existing_articles)})")

        return enhanced_articles

# Example usage
if __name__ == "__main__":
    generator = DynamicFeedGenerator()

    # Test with different countries
    test_countries = ['Haiti', 'Somalia', 'Ukraine', 'Taiwan', 'Yemen']

    for country in test_countries:
        articles, sources = generator.get_country_coverage(country)
        print(f"\n{country}: {len(articles)} articles from {len(sources)} dynamic sources")

        if articles:
            print(f"Latest headlines:")
            for article in articles[:3]:
                print(f"  - {article['title'][:70]}...")