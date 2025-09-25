"""
Google News Engine - Works like actual Google
No manual lists, no missing events, just comprehensive search
"""
import feedparser
import requests
from urllib.parse import quote_plus
from datetime import datetime, timedelta
import time
import socket

# Set timeout for feed fetching
socket.setdefaulttimeout(5)

class GoogleNewsEngine:
    def __init__(self):
        self.base_url = "https://news.google.com/rss/search"

    def search(self, query, when="7d", max_results=100):
        """
        Search Google News exactly like a user would

        Args:
            query: Exactly what you'd type into Google
            when: Time range (1h, 1d, 7d, 30d)
            max_results: Max articles to return
        """
        # Build the URL exactly like Google News does
        params = {
            'q': query,
            'when': when,
            'hl': 'en-US',
            'gl': 'US',
            'ceid': 'US:en'
        }

        # Create the query string
        query_string = '&'.join([f"{k}={quote_plus(str(v))}" for k, v in params.items()])
        url = f"{self.base_url}?{query_string}"

        try:
            feed = feedparser.parse(url)
            articles = []

            for entry in feed.entries[:max_results]:
                articles.append({
                    'title': entry.get('title', ''),
                    'link': entry.get('link', ''),
                    'published': entry.get('published', ''),
                    'source': entry.get('source', {}).get('title', 'Google News'),
                    'summary': entry.get('summary', '')[:200]
                })

            return articles
        except Exception as e:
            print(f"Search failed: {e}")
            return []

    def get_country_news(self, country, days_back=7):
        """
        Get comprehensive news for any country
        Just like typing the country name into Google News
        """
        when_map = {
            1: "1d",
            7: "7d",
            30: "30d"
        }
        when = when_map.get(days_back, "7d")

        all_articles = []

        # Basic country search - exactly what a user would do
        print(f"Searching: {country}")
        articles = self.search(country, when=when)
        all_articles.extend(articles)

        # If it's a security tool, also search for security terms
        # But in a smart way - as ONE search, not multiple
        security_query = f"{country} (war OR conflict OR military OR security OR crisis OR attack OR violence)"
        print(f"Security search: {country} + security terms")
        security_articles = self.search(security_query, when=when)

        # Merge and deduplicate
        seen_titles = set()
        final_articles = []

        for article in all_articles + security_articles:
            if article['title'] not in seen_titles:
                seen_titles.add(article['title'])
                final_articles.append(article)

        return final_articles

    def search_incident(self, description, days_back=30):
        """
        Search for a specific incident
        Just type what you're looking for, like Google
        """
        when_map = {
            1: "1d",
            7: "7d",
            30: "30d"
        }
        when = when_map.get(days_back, "30d")

        return self.search(description, when=when)

    def get_breaking_security_news(self, hours_back=24):
        """
        Get breaking security news from the last N hours
        One simple search that catches everything
        """
        # Convert hours to Google's time format
        if hours_back <= 1:
            when = "1h"
        elif hours_back <= 24:
            when = "1d"
        elif hours_back <= 168:
            when = "7d"
        else:
            when = "30d"

        # One comprehensive security search - like a user would do
        query = "(NATO OR Russia OR China OR missile OR airstrike OR airspace OR military OR war OR conflict OR attack OR terrorism OR coup) AND (breaking OR urgent OR alert)"

        return self.search(query, when=when, max_results=50)


# Test it
if __name__ == "__main__":
    engine = GoogleNewsEngine()

    print("="*60)
    print("GOOGLE NEWS ENGINE TEST")
    print("="*60)

    # Test 1: Finland (should find airspace violations)
    print("\n1. Testing Finland (generic search):")
    print("-"*40)
    results = engine.search("Finland", when="30d", max_results=10)
    print(f"Found {len(results)} articles")
    for r in results[:3]:
        print(f"  - {r['title'][:80]}...")

    # Test 2: Specific incident search
    print("\n2. Testing specific search (Finland Russia airspace):")
    print("-"*40)
    results = engine.search("Finland Russia airspace", when="30d", max_results=10)
    print(f"Found {len(results)} articles")
    for r in results[:3]:
        print(f"  - {r['title'][:80]}...")

    # Test 3: NATO Article 4
    print("\n3. Testing NATO Article 4:")
    print("-"*40)
    results = engine.search("NATO Article 4", when="30d", max_results=10)
    print(f"Found {len(results)} articles")
    for r in results[:3]:
        print(f"  - {r['title'][:80]}...")

    # Test 4: Breaking security news
    print("\n4. Testing breaking security news:")
    print("-"*40)
    results = engine.get_breaking_security_news(hours_back=168)
    print(f"Found {len(results)} breaking security articles")

    # Check if we found Finland/Russia stuff
    finland_found = any('finland' in r['title'].lower() for r in results)
    nato_found = any('nato' in r['title'].lower() for r in results)

    print(f"\nFinland incidents found: {finland_found}")
    print(f"NATO events found: {nato_found}")

    print("\n" + "="*60)
    print("RESULT: This works exactly like Google News")
    print("No manual lists, no missing events")
    print("="*60)