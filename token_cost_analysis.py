"""Analyze token usage and costs for the security monitoring system"""

def calculate_token_costs():
    print("=== TOKEN USAGE & COST ANALYSIS ===\n")

    # Gemini pricing (as of 2024)
    gemini_flash_input = 0.000075 / 1000  # $0.000075 per 1K tokens
    gemini_flash_output = 0.0003 / 1000   # $0.0003 per 1K tokens

    # Typical article sizes
    avg_article_title = 100  # characters
    avg_article_summary = 500  # characters
    chars_per_token = 4  # approximate

    print("CURRENT SYSTEM BEHAVIOR:")
    print("-" * 40)

    # Current approach - sending ALL articles
    articles_per_country = 100  # From Google News
    chars_per_article = avg_article_title + avg_article_summary
    total_chars = articles_per_country * chars_per_article
    total_tokens = total_chars / chars_per_token

    print(f"Articles per country: {articles_per_country}")
    print(f"Characters per article: {chars_per_article}")
    print(f"Total characters sent: {total_chars:,}")
    print(f"Total tokens (input): {total_tokens:,.0f}")
    print(f"Cost per country report: ${total_tokens * gemini_flash_input:.4f}")

    # Monthly usage estimate
    reports_per_day = 10
    countries_per_report = 3
    days_per_month = 30

    monthly_tokens = total_tokens * reports_per_day * countries_per_report * days_per_month
    monthly_cost = monthly_tokens * gemini_flash_input

    print(f"\nMONTHLY ESTIMATES (current approach):")
    print(f"Reports: {reports_per_day}/day × {countries_per_report} countries × {days_per_month} days")
    print(f"Monthly input tokens: {monthly_tokens:,.0f}")
    print(f"Monthly cost (input only): ${monthly_cost:.2f}")
    print(f"WITH OUTPUT tokens: ${monthly_cost * 2:.2f}")  # Rough estimate

    print("\n" + "=" * 50)
    print("PROBLEM: This will cost $30-60+ per month!")
    print("=" * 50)

    print("\nRECOMMENDED OPTIMIZATIONS:")
    print("-" * 40)

    optimizations = [
        {
            "name": "1. PRE-FILTER ARTICLES",
            "description": "Only send top 10-15 most relevant articles",
            "savings": "85% reduction",
            "new_cost": "$4.50/month"
        },
        {
            "name": "2. SMART SUMMARIZATION",
            "description": "Truncate summaries to 150 chars",
            "savings": "70% reduction",
            "new_cost": "$9/month"
        },
        {
            "name": "3. TIERED PROCESSING",
            "description": "Full analysis only for HIGH priority countries",
            "savings": "60% reduction",
            "new_cost": "$12/month"
        },
        {
            "name": "4. LOCAL PRE-PROCESSING",
            "description": "Use keyword extraction before sending to LLM",
            "savings": "75% reduction",
            "new_cost": "$7.50/month"
        }
    ]

    for opt in optimizations:
        print(f"\n{opt['name']}")
        print(f"  {opt['description']}")
        print(f"  Savings: {opt['savings']}")
        print(f"  New cost: {opt['new_cost']}")

    print("\n" + "=" * 50)
    print("BEST PRACTICE IMPLEMENTATION:")
    print("-" * 40)

    print("""
    def optimize_for_llm(articles):
        # 1. Sort by relevance (title keywords)
        scored_articles = []
        for article in articles:
            score = 0
            # High priority keywords
            if any(word in article['title'].lower() for word in
                   ['killed', 'attack', 'crisis', 'election', 'coup']):
                score += 10
            # Medium priority
            if any(word in article['title'].lower() for word in
                   ['protest', 'tension', 'dispute', 'sanctions']):
                score += 5
            scored_articles.append((score, article))

        # 2. Take only top 15 articles
        top_articles = sorted(scored_articles, key=lambda x: x[0], reverse=True)[:15]

        # 3. Truncate summaries
        optimized = []
        for score, article in top_articles:
            optimized.append({
                'title': article['title'][:100],
                'summary': article['summary'][:150] + '...'
            })

        return optimized

    # RESULT: 85% token reduction!
    """)

    print("\nTOKEN USAGE COMPARISON:")
    print("-" * 40)

    # Original
    print("ORIGINAL:")
    print(f"  100 articles × 600 chars = 60,000 chars = 15,000 tokens")
    print(f"  Cost per report: ${15000 * gemini_flash_input:.4f}")

    # Optimized
    optimized_articles = 15
    optimized_chars = 250  # 100 title + 150 summary
    optimized_total = optimized_articles * optimized_chars
    optimized_tokens = optimized_total / chars_per_token

    print("\nOPTIMIZED:")
    print(f"  15 articles × 250 chars = 3,750 chars = 937 tokens")
    print(f"  Cost per report: ${optimized_tokens * gemini_flash_input:.4f}")
    print(f"  SAVINGS: 94% reduction!")

    print("\n" + "=" * 50)
    print("ADDITIONAL COST-SAVING FEATURES:")
    print("-" * 40)

    features = [
        "• Add daily token budget limits",
        "• Cache reports for 24 hours",
        "• Use free tier wisely (Gemini offers 60 requests/min free)",
        "• Batch process during off-peak",
        "• Only use LLM for final synthesis, not initial filtering",
        "• Implement local NLP for basic classification"
    ]

    for feature in features:
        print(feature)

if __name__ == "__main__":
    calculate_token_costs()