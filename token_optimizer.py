"""Optimize article data to minimize token usage for LLM processing"""

class TokenOptimizer:
    def __init__(self):
        # Priority keywords for relevance scoring
        self.high_priority_keywords = [
            'killed', 'dead', 'death', 'attack', 'explosion', 'bombing',
            'crisis', 'emergency', 'coup', 'overthrow', 'assassination',
            'war', 'invasion', 'conflict', 'battle', 'offensive',
            'collapse', 'failed', 'violence', 'massacre', 'genocide'
        ]

        self.medium_priority_keywords = [
            'protest', 'tension', 'dispute', 'sanctions', 'election',
            'vote', 'referendum', 'opposition', 'unrest', 'strike',
            'deployment', 'military', 'security', 'threat', 'warning'
        ]

        self.low_priority_keywords = [
            'meeting', 'talks', 'discussion', 'agreement', 'signed',
            'visit', 'diplomatic', 'economic', 'trade', 'development'
        ]

    def score_article(self, article):
        """Score article relevance based on keywords in title and summary"""
        score = 0
        title_lower = article.get('title', '').lower()
        summary_lower = article.get('summary', '').lower()
        combined = f"{title_lower} {summary_lower}"

        # High priority in title = 10 points
        for keyword in self.high_priority_keywords:
            if keyword in title_lower:
                score += 10
            elif keyword in summary_lower:
                score += 5

        # Medium priority
        for keyword in self.medium_priority_keywords:
            if keyword in title_lower:
                score += 5
            elif keyword in summary_lower:
                score += 2

        # Low priority
        for keyword in self.low_priority_keywords:
            if keyword in title_lower:
                score += 2
            elif keyword in summary_lower:
                score += 1

        # Recency bonus (if published date available)
        # Could add time-based scoring here

        return score

    def optimize_for_llm(self, articles, max_articles=15, max_title_length=100, max_summary_length=150):
        """
        Optimize articles for LLM processing to minimize tokens

        Args:
            articles: List of article dictionaries
            max_articles: Maximum number of articles to include
            max_title_length: Maximum characters for title
            max_summary_length: Maximum characters for summary

        Returns:
            Optimized list of articles
        """
        if not articles:
            return []

        # Score and sort articles by relevance
        scored_articles = []
        for article in articles:
            score = self.score_article(article)
            scored_articles.append((score, article))

        # Sort by score (highest first)
        scored_articles.sort(key=lambda x: x[0], reverse=True)

        # Take only top articles
        top_articles = scored_articles[:max_articles]

        # Optimize each article
        optimized = []
        for score, article in top_articles:
            # Truncate title and summary
            title = article.get('title', '')[:max_title_length]
            summary = article.get('summary', '')[:max_summary_length]

            # Clean up truncated summary
            if len(article.get('summary', '')) > max_summary_length:
                # Try to end at last complete sentence
                last_period = summary.rfind('. ')
                if last_period > max_summary_length * 0.7:  # If we're at least 70% through
                    summary = summary[:last_period + 1]
                else:
                    summary = summary.rstrip() + '...'

            optimized.append({
                'title': title,
                'summary': summary,
                'relevance_score': score,
                'source': article.get('source', 'Unknown'),
                'link': article.get('link', ''),  # Keep link for reference
                'published': article.get('published', '')  # Include date
            })

        return optimized

    def prepare_context_for_llm(self, articles):
        """
        Prepare minimal context string for LLM

        Args:
            articles: List of optimized articles

        Returns:
            Formatted string for LLM context
        """
        if not articles:
            return "No recent articles available."

        context_parts = []

        # Group by relevance
        high_relevance = [a for a in articles if a['relevance_score'] >= 10]
        medium_relevance = [a for a in articles if 5 <= a['relevance_score'] < 10]
        low_relevance = [a for a in articles if a['relevance_score'] < 5]

        if high_relevance:
            context_parts.append("CRITICAL DEVELOPMENTS:")
            for article in high_relevance[:5]:  # Top 5 critical
                context_parts.append(f"• {article['title']}")

        if medium_relevance:
            context_parts.append("\nKEY UPDATES:")
            for article in medium_relevance[:5]:  # Top 5 key
                context_parts.append(f"• {article['title']}")

        # Skip low relevance to save tokens

        return '\n'.join(context_parts)

    def estimate_tokens(self, text):
        """Rough estimate of token count (1 token ≈ 4 characters)"""
        return len(text) / 4

    def get_optimization_stats(self, original_articles, optimized_articles):
        """Calculate token savings statistics"""

        # Original token estimate
        original_chars = sum(
            len(a.get('title', '')) + len(a.get('summary', ''))
            for a in original_articles
        )
        original_tokens = self.estimate_tokens(str(original_chars))

        # Optimized token estimate
        optimized_chars = sum(
            len(a['title']) + len(a['summary'])
            for a in optimized_articles
        )
        optimized_tokens = self.estimate_tokens(str(optimized_chars))

        # Calculate savings
        reduction_percent = ((original_tokens - optimized_tokens) / original_tokens * 100) if original_tokens > 0 else 0

        return {
            'original_articles': len(original_articles),
            'optimized_articles': len(optimized_articles),
            'original_tokens': int(original_tokens),
            'optimized_tokens': int(optimized_tokens),
            'token_reduction': f"{reduction_percent:.1f}%",
            'estimated_cost_savings': f"{reduction_percent:.1f}%"
        }


# Example usage
if __name__ == "__main__":
    # Test with sample data
    sample_articles = [
        {'title': 'Gang violence kills 20 in Haiti capital', 'summary': 'Armed groups clashed...', 'source': 'Reuters'},
        {'title': 'Haiti PM discusses economic reforms', 'summary': 'Prime minister met with...', 'source': 'AP'},
        {'title': 'Massacre reported in Port-au-Prince neighborhood', 'summary': 'Witnesses report...', 'source': 'CNN'},
        {'title': 'UN meeting on Haiti scheduled', 'summary': 'Security council to discuss...', 'source': 'UN'},
        {'title': 'Coup attempt thwarted in Haiti', 'summary': 'Military leaders arrested...', 'source': 'BBC'},
    ] * 20  # Simulate 100 articles

    optimizer = TokenOptimizer()

    # Optimize articles
    optimized = optimizer.optimize_for_llm(sample_articles)

    # Get stats
    stats = optimizer.get_optimization_stats(sample_articles, optimized)

    print("Token Optimization Results:")
    print("-" * 40)
    for key, value in stats.items():
        print(f"{key}: {value}")

    # Prepare context
    context = optimizer.prepare_context_for_llm(optimized)
    print("\nOptimized Context for LLM:")
    print("-" * 40)
    print(context)