"""Security-focused article analyzer that reads full content for deep intelligence"""
import requests
from bs4 import BeautifulSoup
import feedparser
from typing import List, Dict
import re

class SecurityArticleAnalyzer:
    def __init__(self):
        # Security-relevant categories and their keywords
        self.security_categories = {
            'conflict': {
                'keywords': ['war', 'battle', 'combat', 'fighting', 'conflict', 'clash',
                            'attack', 'strike', 'offensive', 'assault', 'raid', 'siege'],
                'weight': 10
            },
            'terrorism': {
                'keywords': ['terrorist', 'terrorism', 'bomb', 'bombing', 'explosion',
                            'suicide', 'isis', 'al-qaeda', 'al-shabaab', 'taliban', 'extremist'],
                'weight': 10
            },
            'violence': {
                'keywords': ['killed', 'death', 'dead', 'murder', 'massacre', 'shooting',
                            'violence', 'violent', 'casualty', 'casualties', 'injured', 'wounded'],
                'weight': 9
            },
            'security': {
                'keywords': ['security', 'military', 'police', 'troops', 'forces', 'army',
                            'defense', 'soldier', 'deployment', 'operation', 'checkpoint'],
                'weight': 7
            },
            'political_crisis': {
                'keywords': ['coup', 'overthrow', 'revolution', 'uprising', 'protest',
                            'unrest', 'riot', 'demonstration', 'opposition', 'crisis'],
                'weight': 8
            },
            'crime': {
                'keywords': ['crime', 'gang', 'cartel', 'kidnap', 'abduction', 'trafficking',
                            'smuggling', 'corruption', 'organized crime', 'mafia'],
                'weight': 7
            },
            'humanitarian': {
                'keywords': ['humanitarian', 'refugee', 'displaced', 'famine', 'hunger',
                            'disease', 'outbreak', 'epidemic', 'emergency', 'disaster'],
                'weight': 6
            },
            'natural_disaster': {
                'keywords': ['earthquake', 'tsunami', 'hurricane', 'typhoon', 'flood',
                            'drought', 'volcano', 'wildfire', 'storm', 'cyclone'],
                'weight': 6
            },
            'political': {
                'keywords': ['election', 'vote', 'parliament', 'president', 'government',
                            'minister', 'politics', 'referendum', 'constitution', 'sanctions'],
                'weight': 5
            },
            'economic_crisis': {
                'keywords': ['collapse', 'crisis', 'default', 'inflation', 'shortage',
                            'poverty', 'unemployment', 'recession', 'blockade', 'embargo'],
                'weight': 5
            }
        }

    def calculate_relevance_score(self, title: str, summary: str = "") -> Dict:
        """Calculate security relevance score for an article"""
        text = f"{title} {summary}".lower()

        score = 0
        matched_categories = []
        matched_keywords = []

        for category, info in self.security_categories.items():
            category_matches = []
            for keyword in info['keywords']:
                if keyword in text:
                    category_matches.append(keyword)
                    score += info['weight']

            if category_matches:
                matched_categories.append(category)
                matched_keywords.extend(category_matches)

        return {
            'score': score,
            'categories': matched_categories,
            'keywords': list(set(matched_keywords)),
            'is_security_relevant': score >= 5  # Minimum threshold
        }

    def filter_security_relevant(self, articles: List[Dict], min_score: int = 5) -> List[Dict]:
        """Filter articles to only security-relevant ones"""
        filtered = []

        for article in articles:
            analysis = self.calculate_relevance_score(
                article.get('title', ''),
                article.get('summary', '')
            )

            if analysis['score'] >= min_score:
                # Add analysis metadata to article
                article['security_analysis'] = analysis
                article['relevance_score'] = analysis['score']
                filtered.append(article)

        # Sort by relevance score (highest first)
        filtered.sort(key=lambda x: x['relevance_score'], reverse=True)

        return filtered

    def fetch_full_article(self, url: str) -> str:
        """Fetch and extract full article text from URL"""
        try:
            # Set headers to avoid bot detection
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }

            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()

            # Parse HTML
            soup = BeautifulSoup(response.text, 'html.parser')

            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()

            # Try common article content selectors
            article_text = ""

            # Try different content selectors
            selectors = [
                'article',
                'div.article-content',
                'div.story-body',
                'div.content',
                'main',
                'div.entry-content',
                'div.post-content',
                '[itemprop="articleBody"]'
            ]

            for selector in selectors:
                content = soup.select_one(selector)
                if content:
                    article_text = content.get_text(separator=' ', strip=True)
                    break

            # Fallback: get all paragraphs
            if not article_text:
                paragraphs = soup.find_all('p')
                if paragraphs:
                    article_text = ' '.join([p.get_text(strip=True) for p in paragraphs])

            # Clean up text
            article_text = re.sub(r'\s+', ' ', article_text)
            article_text = article_text.strip()

            # Limit to reasonable length (5000 chars) to avoid token overload
            if len(article_text) > 5000:
                article_text = article_text[:5000] + "..."

            return article_text

        except Exception as e:
            print(f"Error fetching article from {url}: {e}")
            return ""

    def analyze_articles_deeply(self, articles: List[Dict], country: str, max_articles: int = 10) -> Dict:
        """
        Perform deep analysis on security-relevant articles

        1. Filter for security relevance
        2. Select top articles
        3. Fetch full text
        4. Return comprehensive analysis
        """

        # Step 1: Filter for security relevance
        print(f"\n[STEP 1] Filtering {len(articles)} articles for security relevance...")
        relevant_articles = self.filter_security_relevant(articles)
        print(f"Found {len(relevant_articles)} security-relevant articles")

        # Step 2: Select top articles (by relevance score)
        top_articles = relevant_articles[:max_articles]
        print(f"\n[STEP 2] Selected top {len(top_articles)} articles for deep analysis")

        # Step 3: Fetch full text for top articles
        print(f"\n[STEP 3] Fetching full text for selected articles...")
        articles_with_full_text = []

        for i, article in enumerate(top_articles, 1):
            print(f"  [{i}/{len(top_articles)}] Fetching: {article['title'][:60]}...")

            full_text = self.fetch_full_article(article.get('link', ''))

            if full_text:
                article['full_text'] = full_text
                article['has_full_text'] = True
                print(f"    ✓ Got {len(full_text)} chars")
            else:
                # Fall back to summary if can't get full text
                article['full_text'] = article.get('summary', '')
                article['has_full_text'] = False
                print(f"    ✗ Using summary instead")

            articles_with_full_text.append(article)

        # Step 4: Prepare comprehensive analysis
        analysis = {
            'country': country,
            'total_articles_analyzed': len(articles),
            'security_relevant_count': len(relevant_articles),
            'deep_analysis_count': len(articles_with_full_text),
            'articles': articles_with_full_text,
            'top_categories': self._get_top_categories(relevant_articles),
            'key_themes': self._extract_key_themes(articles_with_full_text),
            'threat_assessment': self._assess_threat_level(relevant_articles)
        }

        return analysis

    def _get_top_categories(self, articles: List[Dict]) -> List[Dict]:
        """Get most common security categories from articles"""
        category_counts = {}

        for article in articles:
            if 'security_analysis' in article:
                for category in article['security_analysis']['categories']:
                    category_counts[category] = category_counts.get(category, 0) + 1

        # Sort by count
        sorted_categories = sorted(
            category_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )

        return [
            {'category': cat, 'count': count}
            for cat, count in sorted_categories[:5]
        ]

    def _extract_key_themes(self, articles: List[Dict]) -> List[str]:
        """Extract key themes from article full texts"""
        themes = []

        # Look for patterns in full texts
        all_text = ' '.join([a.get('full_text', '')[:500] for a in articles[:5]])

        # Simple theme extraction (could be enhanced with NLP)
        if 'humanitarian' in all_text.lower():
            themes.append("Humanitarian crisis ongoing")
        if 'military' in all_text.lower() or 'troops' in all_text.lower():
            themes.append("Military operations active")
        if 'election' in all_text.lower() or 'vote' in all_text.lower():
            themes.append("Political tensions around elections")
        if 'gang' in all_text.lower() or 'cartel' in all_text.lower():
            themes.append("Organized crime activity")

        return themes[:5]  # Limit to top 5 themes

    def _assess_threat_level(self, articles: List[Dict]) -> str:
        """Assess overall threat level based on articles"""
        if not articles:
            return "LOW"

        # Calculate average relevance score
        avg_score = sum(a.get('relevance_score', 0) for a in articles) / len(articles)

        # Check for critical keywords
        critical_count = 0
        for article in articles[:10]:  # Check top 10
            text = f"{article.get('title', '')} {article.get('summary', '')}".lower()
            if any(word in text for word in ['killed', 'dead', 'attack', 'bomb', 'coup']):
                critical_count += 1

        # Determine threat level
        if avg_score > 50 or critical_count >= 5:
            return "CRITICAL"
        elif avg_score > 30 or critical_count >= 3:
            return "HIGH"
        elif avg_score > 15 or critical_count >= 1:
            return "MODERATE"
        elif avg_score > 5:
            return "ELEVATED"
        else:
            return "LOW"

    def prepare_for_llm(self, analysis: Dict, max_chars: int = 4000) -> str:
        """
        Prepare analyzed content for LLM synthesis
        Includes full text excerpts, not just headlines
        """
        parts = []

        # Add threat assessment
        parts.append(f"THREAT LEVEL: {analysis['threat_assessment']}\n")

        # Add top categories
        if analysis['top_categories']:
            parts.append("PRIMARY CONCERNS:")
            for cat in analysis['top_categories'][:3]:
                parts.append(f"- {cat['category'].replace('_', ' ').title()}: {cat['count']} incidents")
            parts.append("")

        # Add articles with full text excerpts
        parts.append("DETAILED INTELLIGENCE:\n")

        for i, article in enumerate(analysis['articles'][:5], 1):
            parts.append(f"[{i}] {article['title']}")
            parts.append(f"    Date: {article.get('published', 'Unknown')}")
            parts.append(f"    Categories: {', '.join(article.get('security_analysis', {}).get('categories', []))}")

            # Include meaningful excerpt from full text
            full_text = article.get('full_text', '')
            if full_text:
                # Get first 300 chars of actual content
                excerpt = full_text[:300].strip()
                if len(full_text) > 300:
                    # Try to end at sentence
                    last_period = excerpt.rfind('. ')
                    if last_period > 200:
                        excerpt = excerpt[:last_period + 1]
                    else:
                        excerpt += "..."
                parts.append(f"    Content: {excerpt}")
            parts.append("")

        # Add key themes
        if analysis['key_themes']:
            parts.append("KEY THEMES:")
            for theme in analysis['key_themes']:
                parts.append(f"- {theme}")

        result = '\n'.join(parts)

        # Trim if too long
        if len(result) > max_chars:
            result = result[:max_chars] + "\n[Content trimmed]"

        return result


# Example usage
if __name__ == "__main__":
    analyzer = SecurityArticleAnalyzer()

    # Test with sample articles
    sample_articles = [
        {
            'title': 'Gang violence kills 20 in Haiti capital',
            'summary': 'Armed groups clashed in Port-au-Prince...',
            'link': 'https://example.com/article1'
        },
        {
            'title': 'Haiti PM visits new school opening',
            'summary': 'Education minister announces new program...',
            'link': 'https://example.com/article2'
        },
        {
            'title': 'Drought threatens famine in Somalia',
            'summary': 'UN warns of humanitarian crisis...',
            'link': 'https://example.com/article3'
        }
    ]

    # Test relevance scoring
    for article in sample_articles:
        score = analyzer.calculate_relevance_score(article['title'], article['summary'])
        print(f"\n{article['title']}")
        print(f"  Score: {score['score']}")
        print(f"  Categories: {score['categories']}")
        print(f"  Security Relevant: {score['is_security_relevant']}")

    # Test filtering
    filtered = analyzer.filter_security_relevant(sample_articles)
    print(f"\nFiltered to {len(filtered)} security-relevant articles")