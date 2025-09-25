"""
ACTUALLY extracts article content - not just headlines
Uses multiple methods to get real article text fast
"""
import requests
from bs4 import BeautifulSoup
import concurrent.futures
import hashlib
import json
from pathlib import Path
import time
from datetime import datetime, timedelta

class ArticleExtractor:
    def __init__(self, cache_dir="article_cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def _get_cache_key(self, url):
        """Create cache key from URL"""
        return hashlib.md5(url.encode()).hexdigest()

    def _get_from_cache(self, url):
        """Get article from cache if fresh (24 hours)"""
        cache_file = self.cache_dir / f"{self._get_cache_key(url)}.json"

        if cache_file.exists():
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                # Check if cache is fresh (24 hours)
                cached_time = datetime.fromisoformat(data['cached_at'])
                if datetime.now() - cached_time < timedelta(hours=24):
                    return data['content']
            except:
                pass

        return None

    def _save_to_cache(self, url, content):
        """Save article to cache"""
        cache_file = self.cache_dir / f"{self._get_cache_key(url)}.json"

        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'url': url,
                    'content': content,
                    'cached_at': datetime.now().isoformat()
                }, f)
        except:
            pass

    def extract_article(self, url, timeout=3):
        """Extract actual article content from URL"""

        # Check cache first
        cached = self._get_from_cache(url)
        if cached:
            return cached

        try:
            response = self.session.get(url, timeout=timeout)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()

            # Try different methods to find article content
            content = ""

            # Method 1: Look for article tags
            article = soup.find('article')
            if article:
                content = article.get_text()

            # Method 2: Look for common content divs
            if not content:
                for selector in ['div.article-content', 'div.entry-content', 'div.post-content',
                                'main', 'div.content', 'div.story-body']:
                    element = soup.select_one(selector)
                    if element:
                        content = element.get_text()
                        break

            # Method 3: Get all paragraphs
            if not content:
                paragraphs = soup.find_all('p')
                if len(paragraphs) > 3:
                    content = ' '.join([p.get_text() for p in paragraphs[:20]])

            # Clean up the text
            if content:
                content = ' '.join(content.split())
                content = content[:5000]  # Limit to 5000 chars

                # Save to cache
                self._save_to_cache(url, content)

                return content

            return None

        except Exception as e:
            return None

    def extract_articles_parallel(self, articles, max_workers=10):
        """
        Extract content from multiple articles in parallel
        Super fast - processes 10 articles simultaneously
        """
        enhanced_articles = []

        # Create a list of URLs to process
        urls_to_fetch = []
        url_to_article = {}

        for article in articles:
            url = article.get('link', '')
            if url:
                urls_to_fetch.append(url)
                url_to_article[url] = article

        print(f"Extracting content from {len(urls_to_fetch)} articles...")
        start_time = time.time()

        # Process URLs in parallel
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tasks
            future_to_url = {
                executor.submit(self.extract_article, url, timeout=3): url
                for url in urls_to_fetch
            }

            # Collect results as they complete
            completed = 0
            for future in concurrent.futures.as_completed(future_to_url):
                url = future_to_url[future]
                article = url_to_article[url].copy()

                try:
                    content = future.result()
                    if content:
                        article['full_content'] = content
                        article['has_content'] = True
                    else:
                        article['full_content'] = article.get('summary', article.get('title', ''))
                        article['has_content'] = False
                except:
                    article['full_content'] = article.get('summary', article.get('title', ''))
                    article['has_content'] = False

                enhanced_articles.append(article)
                completed += 1

                # Progress update
                if completed % 10 == 0:
                    print(f"  Processed {completed}/{len(urls_to_fetch)} articles...")

        elapsed = time.time() - start_time
        print(f"Extracted content from {len(enhanced_articles)} articles in {elapsed:.1f} seconds")

        # Add success rate info
        with_content = sum(1 for a in enhanced_articles if a.get('has_content', False))
        print(f"  Successfully extracted full text from {with_content}/{len(enhanced_articles)} articles")

        return enhanced_articles


# Test it
if __name__ == "__main__":
    extractor = ArticleExtractor()

    # Test single article
    test_url = "https://www.bbc.com/news/world-europe-68660599"
    print(f"Testing single article: {test_url}")
    content = extractor.extract_article(test_url)

    if content:
        print(f"Extracted {len(content)} characters")
        print(f"Preview: {content[:200]}...")
    else:
        print("Failed to extract content")

    # Test parallel extraction
    print("\nTesting parallel extraction with multiple articles...")

    test_articles = [
        {'title': 'Test 1', 'link': 'https://www.bbc.com/news/world'},
        {'title': 'Test 2', 'link': 'https://www.reuters.com/world/'},
        {'title': 'Test 3', 'link': 'https://www.cnn.com/world'},
    ]

    enhanced = extractor.extract_articles_parallel(test_articles)

    for article in enhanced:
        if article.get('has_content'):
            print(f"✓ {article['title']}: {len(article.get('full_content', ''))} chars")
        else:
            print(f"✗ {article['title']}: No content extracted")