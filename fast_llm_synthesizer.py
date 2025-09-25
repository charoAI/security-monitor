"""
Fast, accurate LLM synthesis with REAL article content
"""
import os
from typing import List, Dict
import google.generativeai as genai
from article_extractor import ArticleExtractor
import concurrent.futures

class FastLLMSynthesizer:
    def __init__(self):
        self.gemini_key = os.getenv('GEMINI_API_KEY')
        if self.gemini_key:
            genai.configure(api_key=self.gemini_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
            self.enabled = True
        else:
            self.enabled = False

    def synthesize_country_report(self, country: str, articles: List[Dict], custom_prompt: str = None) -> Dict:
        """
        Generate report with actual article content
        Returns both narrative and articles with full content for chat
        """
        if not self.enabled or not articles:
            return {
                'narrative': f"No LLM available. {len(articles)} articles found for {country}.",
                'articles_with_content': articles
            }

        # Step 1: Extract actual article content in parallel (FAST)
        print(f"Extracting article content for {country}...")
        extractor = ArticleExtractor()
        articles_with_content = extractor.extract_articles_parallel(articles[:20], max_workers=10)

        # Step 2: Prepare content for LLM
        article_data = self._prepare_for_llm(articles_with_content)

        # Step 3: Generate narrative with custom focus if provided
        try:
            from datetime import datetime
            current_date = datetime.now().strftime('%B %d, %Y')

            base_prompt = f"""
You are a security intelligence analyst. Today's date is {current_date}.
Analyze these RECENT articles about {country} and write a 3-paragraph briefing.
Remember: These are current events happening in 2025, NOT historical events from 2024.

{article_data}"""

            if custom_prompt:
                prompt = base_prompt + f"""

USER FOCUS AREAS: {custom_prompt}

Write a professional intelligence assessment focusing on the areas mentioned above:

PARAGRAPH 1: Start with the most significant development related to the focus areas. Include specific dates, numbers, and actors.

PARAGRAPH 2: Analyze patterns and connections within the focus areas. What are the underlying causes?

PARAGRAPH 3: Assess implications specific to the focus areas and what to watch next.

Be specific. Use facts from the articles. Include dates and numbers."""
            else:
                prompt = base_prompt + """

Write a professional intelligence assessment:

PARAGRAPH 1: Start with the most significant security development. Include specific dates, numbers, and actors from the articles.

PARAGRAPH 2: Analyze patterns and connections. What are the underlying causes? How do events relate?

PARAGRAPH 3: Assess implications for stability and what to watch next.

Be specific. Use facts from the articles. Include dates and numbers."""

            response = self.model.generate_content(prompt)
            narrative = response.text

        except Exception as e:
            print(f"LLM generation failed: {e}")
            narrative = self._fallback_narrative(country, articles_with_content)

        return {
            'narrative': narrative,
            'articles_with_content': articles_with_content  # Pass full content for chat
        }

    def _prepare_for_llm(self, articles: List[Dict]) -> str:
        """Prepare actual article content for LLM"""
        prepared = []

        for i, article in enumerate(articles[:10], 1):  # Top 10 articles
            # Use real content
            content = article.get('full_content', article.get('summary', article['title']))

            # Extract key info
            if len(content) > 500:
                content = content[:500] + "..."

            date = article.get('published', 'Unknown date')[:10] if article.get('published') else 'Unknown date'

            prepared.append(f"""
Article {i} ({date}):
Title: {article['title'][:100]}
Content: {content}
""")

        return "\n".join(prepared)

    def _fallback_narrative(self, country: str, articles: List[Dict]) -> str:
        """Basic narrative without LLM"""
        if not articles:
            return f"No significant developments in {country}."

        # Count articles with actual content
        with_content = sum(1 for a in articles if a.get('has_content'))

        narrative = f"Analysis based on {len(articles)} reports ({with_content} with full content):\n\n"

        # Group by topic
        security_articles = [a for a in articles if any(
            word in a.get('title', '').lower()
            for word in ['military', 'attack', 'security', 'police', 'violence']
        )]

        if security_articles:
            narrative += f"Security Developments: {len(security_articles)} reports indicate ongoing security concerns. "
            narrative += f"Key incident: {security_articles[0]['title'][:100]}. "

        political_articles = [a for a in articles if any(
            word in a.get('title', '').lower()
            for word in ['government', 'election', 'president', 'minister', 'political']
        )]

        if political_articles:
            narrative += f"\n\nPolitical Updates: {len(political_articles)} reports on political developments. "
            narrative += f"Main story: {political_articles[0]['title'][:100]}."

        return narrative


def generate_chat_context(country: str, articles_with_content: List[Dict]) -> str:
    """
    Generate context for the chat assistant with REAL article content
    """
    from datetime import datetime
    current_date = datetime.now().strftime('%Y-%m-%d')
    context_parts = [f"Today's date: {current_date}\nCurrent intelligence on {country}:\n"]

    # Sort articles by date (most recent first)
    sorted_articles = sorted(articles_with_content[:15],
                           key=lambda x: x.get('published', ''),
                           reverse=True)

    for i, article in enumerate(sorted_articles, 1):
        date = article.get('published', 'Unknown date')

        # Calculate days ago for temporal awareness
        days_ago = "Unknown"
        if date != 'Unknown date':
            try:
                from datetime import datetime
                article_date = datetime.fromisoformat(date.replace('Z', '+00:00'))
                current = datetime.now(article_date.tzinfo)
                delta = (current - article_date).days
                if delta == 0:
                    days_ago = "today"
                elif delta == 1:
                    days_ago = "yesterday"
                else:
                    days_ago = f"{delta} days ago"
            except:
                pass

        # Use actual content
        if article.get('has_content') and article.get('full_content'):
            content = article['full_content'][:1000]  # First 1000 chars
        else:
            content = article.get('summary', article['title'])

        context_parts.append(f"""
Article {i}:
Date: {date} ({days_ago})
Title: {article['title']}
Content: {content}
Source: {article.get('source', 'Unknown')}
---""")

    return "\n".join(context_parts)


if __name__ == "__main__":
    # Test
    synthesizer = FastLLMSynthesizer()

    test_articles = [
        {
            'title': 'Russia violates Finland airspace with military aircraft',
            'link': 'https://example.com/1',
            'published': '2024-01-15',
            'summary': 'Russian military aircraft violated Finnish airspace on Monday...'
        },
        {
            'title': 'NATO responds to airspace violations',
            'link': 'https://example.com/2',
            'published': '2024-01-16',
            'summary': 'NATO condemned the violations and called for consultations...'
        }
    ]

    result = synthesizer.synthesize_country_report('Finland', test_articles)

    print("Narrative:")
    print(result['narrative'])

    print("\n\nArticles with content:")
    for a in result['articles_with_content']:
        if a.get('has_content'):
            print(f"✓ {a['title']}: {len(a.get('full_content', ''))} chars")
        else:
            print(f"✗ {a['title']}: No content extracted")