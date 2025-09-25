"""Breaking news monitor for critical security events"""
import feedparser
import requests
from datetime import datetime, timedelta

class BreakingNewsMonitor:
    def __init__(self):
        self.critical_searches = [
            "NATO Article 4 Article 5",
            "airspace violation Russia",
            "missile strike NATO",
            "Finland Russia incident",
            "Estonia airspace Russia",
            "Poland Russia border"
        ]

    def get_breaking_news(self, country=None, hours_back=72):
        """Get breaking news for critical events"""
        all_breaking = []

        # Add country-specific searches if provided
        searches = self.critical_searches.copy()
        if country:
            searches.extend([
                f"{country} Russia incident",
                f"{country} security threat",
                f"{country} military alert",
                f"{country} airspace violation"
            ])

        for query in searches:
            try:
                # Use Google News with time restriction
                # when=1d limits to past day, when=7d for past week
                url = f"https://news.google.com/rss/search?q={query.replace(' ', '+')}&when=7d&hl=en-US&gl=US&ceid=US:en"

                feed = feedparser.parse(url)

                for entry in feed.entries[:10]:
                    # Check if truly recent (Google sometimes includes old articles)
                    published = entry.get('published', '')

                    article = {
                        'title': entry.get('title', ''),
                        'link': entry.get('link', ''),
                        'published': published,
                        'source': f"Breaking: {query}",
                        'is_breaking': True
                    }

                    # Avoid duplicates
                    if article['title'] and article['title'] not in [a['title'] for a in all_breaking]:
                        all_breaking.append(article)

            except:
                pass

        # Sort by relevance (NATO mentions, airspace violations get priority)
        priority_keywords = ['NATO', 'Article 4', 'Article 5', 'airspace', 'violation', 'shot down', 'scrambled']

        for article in all_breaking:
            score = sum(1 for keyword in priority_keywords if keyword.lower() in article['title'].lower())
            article['priority_score'] = score

        all_breaking.sort(key=lambda x: x['priority_score'], reverse=True)

        return all_breaking[:20]  # Return top 20 most relevant

    def check_specific_incident(self, description):
        """Check for a specific incident"""
        # Direct search for the incident
        query = description.replace(' ', '+')
        url = f"https://news.google.com/rss/search?q={query}&when=30d&hl=en-US&gl=US&ceid=US:en"

        feed = feedparser.parse(url)

        if feed.entries:
            return [
                {
                    'title': entry.get('title', ''),
                    'link': entry.get('link', ''),
                    'published': entry.get('published', ''),
                    'found': True
                }
                for entry in feed.entries[:5]
            ]
        return []


if __name__ == "__main__":
    monitor = BreakingNewsMonitor()

    print("=== BREAKING NEWS MONITOR ===\n")

    # Check for Finland-specific incidents
    print("Checking for Finland-Russia incidents...")
    breaking = monitor.get_breaking_news("Finland")

    if breaking:
        print(f"\nFound {len(breaking)} breaking news items:\n")
        for article in breaking[:10]:
            if article['priority_score'] > 0:
                print(f"[PRIORITY {article['priority_score']}] {article['title'][:100]}")
            else:
                print(f"  - {article['title'][:100]}")
    else:
        print("No breaking news found")

    # Check for the specific Estonia-Finland incident
    print("\n" + "="*50)
    print("Checking for specific incident: Finland Estonia Russia airspace...")

    specific = monitor.check_specific_incident("Finland Estonia Russia airspace violation 2024")

    if specific:
        print("\nSpecific incident coverage found:")
        for article in specific:
            print(f"  - {article['title']}")
    else:
        print("Specific incident not found in news feeds")