"""Minimal test to identify the issue"""

print("Testing imports...")
try:
    from dashboard import app
    print("  Dashboard imports: OK")
except Exception as e:
    print(f"  Dashboard imports: FAILED - {e}")
    exit(1)

print("\nTesting token optimizer...")
try:
    from token_optimizer import TokenOptimizer
    optimizer = TokenOptimizer()
    test_articles = [
        {'title': 'Test article', 'summary': 'Test summary'}
    ]
    result = optimizer.optimize_for_llm(test_articles)
    print(f"  Token optimizer: OK - optimized {len(result)} articles")
except Exception as e:
    print(f"  Token optimizer: FAILED - {e}")

print("\nTesting LLM synthesizer...")
try:
    from llm_synthesizer import LLMSynthesizer
    synth = LLMSynthesizer()
    print(f"  LLM synthesizer: OK - Gemini={synth.use_gemini}, OpenAI={synth.use_openai}")
except Exception as e:
    print(f"  LLM synthesizer: FAILED - {e}")

print("\nTesting dynamic feed generator...")
try:
    from dynamic_feed_generator import DynamicFeedGenerator
    gen = DynamicFeedGenerator()
    print("  Dynamic feed generator: OK")
except Exception as e:
    print(f"  Dynamic feed generator: FAILED - {e}")

print("\nTesting country intelligence...")
try:
    from country_intelligence import CountryIntelligence
    intel = CountryIntelligence()
    print("  Country intelligence: OK")
except Exception as e:
    print(f"  Country intelligence: FAILED - {e}")

print("\nTesting article fetch (limited)...")
try:
    from dashboard import fetch_articles
    # Use very small limit to avoid timeout
    articles = fetch_articles(limit=1)
    print(f"  Article fetch: OK - got {len(articles)} articles")
except Exception as e:
    print(f"  Article fetch: FAILED - {e}")

print("\n" + "="*50)
print("DIAGNOSTIC COMPLETE")
print("="*50)