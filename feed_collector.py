import feedparser
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from typing import List, Dict, Any
import logging
import hashlib
import json
from pathlib import Path

logger = logging.getLogger(__name__)

class FeedCollector:
    def __init__(self, cache_dir: str = "data/cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'SecurityMonitor/1.0 (Geopolitical Security Feed Aggregator)'
        })
    
    def collect_from_source(self, source: Dict[str, Any]) -> List[Dict[str, Any]]:
        try:
            if source['type'] == 'rss':
                return self._collect_rss(source)
            elif source['type'] == 'web':
                return self._collect_web(source)
            else:
                logger.warning(f"Unknown source type: {source['type']}")
                return []
        except Exception as e:
            logger.error(f"Error collecting from {source['name']}: {e}")
            return []
    
    def _collect_rss(self, source: Dict[str, Any]) -> List[Dict[str, Any]]:
        feed = feedparser.parse(source['url'])
        articles = []
        
        # Only get articles from last 24 hours
        cutoff_time = datetime.now() - timedelta(days=1)
        
        for entry in feed.entries:
            # Parse publication date
            pub_date = None
            if hasattr(entry, 'published_parsed'):
                pub_date = datetime.fromtimestamp(
                    feedparser._parse_date(entry.published).timetuple().__hash__()
                ).replace(microsecond=0)
            elif hasattr(entry, 'updated_parsed'):
                pub_date = datetime.fromtimestamp(
                    feedparser._parse_date(entry.updated).timetuple().__hash__()
                ).replace(microsecond=0)
            
            # Create article ID
            article_id = hashlib.md5(
                f"{source['name']}{entry.get('link', '')}".encode()
            ).hexdigest()
            
            article = {
                'id': article_id,
                'source': source['name'],
                'source_url': source['url'],
                'category': source['category'],
                'title': entry.get('title', 'No title'),
                'link': entry.get('link', ''),
                'summary': self._clean_html(entry.get('summary', '')),
                'published': pub_date.isoformat() if pub_date else datetime.now().isoformat(),
                'collected_at': datetime.now().isoformat(),
                'tags': entry.get('tags', []),
                'author': entry.get('author', 'Unknown')
            }
            
            # Filter by time if we have a valid date
            if pub_date and pub_date >= cutoff_time:
                articles.append(article)
            elif not pub_date:
                # Include if we can't determine the date
                articles.append(article)
        
        logger.info(f"Collected {len(articles)} articles from {source['name']}")
        return articles
    
    def _collect_web(self, source: Dict[str, Any]) -> List[Dict[str, Any]]:
        # Placeholder for web scraping implementation
        # This would need custom parsers for each website
        logger.warning(f"Web scraping not yet implemented for {source['name']}")
        return []
    
    def _clean_html(self, text: str) -> str:
        if not text:
            return ""
        soup = BeautifulSoup(text, 'html.parser')
        return soup.get_text(separator=' ', strip=True)
    
    def collect_all(self, sources: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        all_articles = []
        for source in sources:
            articles = self.collect_from_source(source)
            all_articles.extend(articles)
        
        # Remove duplicates based on article ID
        unique_articles = {}
        for article in all_articles:
            if article['id'] not in unique_articles:
                unique_articles[article['id']] = article
        
        return list(unique_articles.values())
    
    def save_collection(self, articles: List[Dict[str, Any]], 
                       filename: str = None) -> str:
        if not filename:
            filename = f"collection_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        filepath = self.cache_dir / filename
        with open(filepath, 'w') as f:
            json.dump(articles, f, indent=2, default=str)
        
        logger.info(f"Saved {len(articles)} articles to {filepath}")
        return str(filepath)