"""Test what's actually being used in the system"""

print("1. Testing imports...")
try:
    from fast_llm_synthesizer import FastLLMSynthesizer, generate_chat_context
    print("   FastLLMSynthesizer: AVAILABLE")
except Exception as e:
    print(f"   FastLLMSynthesizer: NOT AVAILABLE - {e}")

try:
    from llm_synthesizer import LLMSynthesizer
    print("   LLMSynthesizer: AVAILABLE")
except Exception as e:
    print(f"   LLMSynthesizer: NOT AVAILABLE - {e}")

print("\n2. Testing article extraction...")
try:
    from article_extractor import ArticleExtractor
    extractor = ArticleExtractor()
    print("   ArticleExtractor: AVAILABLE")

    # Test extraction
    test_url = "https://www.bbc.com/news"
    content = extractor.extract_article(test_url, timeout=3)
    if content:
        print(f"   Can extract articles: YES ({len(content)} chars)")
    else:
        print("   Can extract articles: NO")
except Exception as e:
    print(f"   ArticleExtractor: ERROR - {e}")

print("\n3. Testing Gemini API...")
import os
from dotenv import load_dotenv
load_dotenv()

api_key = os.getenv('GEMINI_API_KEY')
if api_key and api_key != 'your_gemini_api_key_here':
    print(f"   API Key loaded: YES")
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content("Say 'working'")
        print(f"   Gemini API works: {response.text.strip()}")
    except Exception as e:
        print(f"   Gemini API error: {e}")
else:
    print("   API Key loaded: NO")

print("\n4. Testing chat context generation...")
try:
    test_articles = [
        {'title': 'Test Article', 'full_content': 'This is test content', 'has_content': True}
    ]
    context = generate_chat_context('TestCountry', test_articles)
    print(f"   Chat context generation: WORKS ({len(context)} chars)")
except Exception as e:
    print(f"   Chat context generation: FAILED - {e}")

print("\n5. Testing synthesis...")
try:
    synth = FastLLMSynthesizer()
    if synth.enabled:
        print("   FastLLMSynthesizer enabled: YES")
    else:
        print("   FastLLMSynthesizer enabled: NO (no API key)")
except Exception as e:
    print(f"   FastLLMSynthesizer error: {e}")