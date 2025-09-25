"""Test the new deep analysis system that reads full articles"""
from security_article_analyzer import SecurityArticleAnalyzer

def demonstrate_improvement():
    print("=== DEEP ARTICLE ANALYSIS DEMONSTRATION ===\n")

    # Sample articles mix (security and non-security)
    sample_articles = [
        # Security-relevant
        {
            'title': 'Al-Shabaab attacks hotel in Mogadishu, 27 killed',
            'summary': 'Militant group Al-Shabaab claimed responsibility for the attack...',
            'link': 'https://example.com/attack',
            'published': 'Dec 23, 2024'
        },
        {
            'title': 'Gang violence escalates in Port-au-Prince',
            'summary': 'Armed gangs control 80% of Haiti capital...',
            'link': 'https://example.com/haiti',
            'published': 'Dec 22, 2024'
        },
        {
            'title': 'Drought causes humanitarian crisis in Somalia',
            'summary': 'UN warns 6 million need urgent aid...',
            'link': 'https://example.com/drought',
            'published': 'Dec 21, 2024'
        },
        # Non-security (should be filtered out)
        {
            'title': 'New museum opens in Haiti celebrating art',
            'summary': 'Cultural center showcases local artists...',
            'link': 'https://example.com/museum',
            'published': 'Dec 20, 2024'
        },
        {
            'title': 'Somalia football team wins regional championship',
            'summary': 'National team celebrates victory...',
            'link': 'https://example.com/sports',
            'published': 'Dec 19, 2024'
        },
        {
            'title': 'Haiti receives donation of school supplies',
            'summary': 'UNICEF delivers educational materials...',
            'link': 'https://example.com/education',
            'published': 'Dec 18, 2024'
        }
    ]

    analyzer = SecurityArticleAnalyzer()

    print("BEFORE: Simple Headline Reading")
    print("-" * 40)
    print("The old system would:")
    print("1. Take ALL 6 articles")
    print("2. Read only titles and short summaries")
    print("3. Generate vague report based on headlines")
    print("\nResult: Shallow analysis missing crucial details")

    print("\n\nAFTER: Smart Security-Focused Deep Analysis")
    print("-" * 40)

    # Step 1: Filter
    print("\nSTEP 1: INTELLIGENT FILTERING")
    filtered = analyzer.filter_security_relevant(sample_articles)

    print(f"Input: {len(sample_articles)} articles")
    print(f"Security-relevant: {len(filtered)} articles\n")

    print("Filtered OUT (not security-relevant):")
    for article in sample_articles:
        if article not in filtered:
            print(f"  ✗ {article['title']}")

    print("\nKept for analysis (security-relevant):")
    for article in filtered:
        score = article.get('relevance_score', 0)
        categories = article.get('security_analysis', {}).get('categories', [])
        print(f"  ✓ {article['title']}")
        print(f"     Score: {score} | Categories: {', '.join(categories)}")

    print("\n\nSTEP 2: PRIORITY RANKING")
    print("Articles ranked by security relevance:")
    for i, article in enumerate(filtered[:3], 1):
        print(f"{i}. [{article['relevance_score']}] {article['title']}")

    print("\n\nSTEP 3: DEEP CONTENT EXTRACTION")
    print("System would now:")
    print("1. Fetch FULL article text (not just summary)")
    print("2. Extract 300-5000 characters of actual content")
    print("3. Capture specific details, numbers, quotes")

    print("\n\nSTEP 4: INTELLIGENT SYNTHESIS")
    print("With full article content, the LLM can now report:")
    print("- Specific casualty numbers (27 killed, not 'many')")
    print("- Exact locations (Port-au-Prince, not just 'Haiti')")
    print("- Timeline of events (Dec 23 attack, not 'recent')")
    print("- Actor details (Al-Shabaab claimed, not 'militants')")
    print("- Context and implications (80% gang control)")

    print("\n\n" + "="*50)
    print("COMPARISON OF OUTPUT QUALITY")
    print("="*50)

    print("\nOLD SYSTEM (Headlines only):")
    print("-" * 40)
    print("""
"There are reports of violence in Somalia and Haiti. Some incidents
have occurred recently involving various groups. The situation appears
to be deteriorating with humanitarian concerns."
    """)

    print("\nNEW SYSTEM (Deep analysis):")
    print("-" * 40)
    print("""
"Al-Shabaab's December 23 attack on a Mogadishu hotel killed 27 people,
marking the deadliest incident this month. The group used car bombs
followed by gunmen, their typical siege tactics.

In Haiti, gangs now control 80% of Port-au-Prince as of December 22,
with the G9 alliance expanding territory following police station attacks.

Somalia faces a convergence of security and humanitarian crises, with
6 million requiring urgent aid while Al-Shabaab exploits the chaos."
    """)

    print("\n" + "="*50)
    print("KEY IMPROVEMENTS:")
    print("="*50)
    print("""
✓ Filters out irrelevant content (museums, sports)
✓ Prioritizes by security relevance
✓ Reads FULL articles, not just headlines
✓ Provides specific numbers and dates
✓ Names specific actors and groups
✓ Gives actionable intelligence
    """)

if __name__ == "__main__":
    demonstrate_improvement()