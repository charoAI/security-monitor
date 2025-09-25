"""Test that ANY country now returns comprehensive coverage"""
from dynamic_feed_generator import DynamicFeedGenerator

def test_country_coverage():
    generator = DynamicFeedGenerator()

    # Test obscure/random countries that definitely aren't in our static sources
    test_countries = [
        'Bhutan',          # Small Himalayan country
        'Suriname',        # Small South American country
        'Fiji',            # Pacific island nation
        'Moldova',         # Eastern European country
        'Botswana',        # African country
        'Luxembourg',      # Small European country
        'Mongolia',        # Central Asian country
        'Paraguay',        # South American country
        'Iceland',         # Nordic island country
        'Malta'            # Mediterranean island country
    ]

    print("=== TESTING COVERAGE FOR RANDOM COUNTRIES ===\n")
    print("These countries are NOT in our static RSS sources")
    print("But with dynamic feeds, we should get excellent coverage!\n")
    print("=" * 50)

    all_successful = True

    for country in test_countries:
        print(f"\n{country}:")
        articles, sources = generator.get_country_coverage(country)

        if len(articles) > 20:
            print(f"  SUCCESS: {len(articles)} articles from {len(sources)} sources")
            # Show sample headline
            if articles:
                print(f"  Sample: {articles[0]['title'][:60]}...")
        else:
            print(f"  POOR COVERAGE: Only {len(articles)} articles")
            all_successful = False

    print("\n" + "=" * 50)
    if all_successful:
        print("\nEXCELLENT! All countries have comprehensive coverage!")
        print("The dynamic feed system is working perfectly.")
        print("\nNow ANY country a user searches for will return rich results,")
        print("not just the ones we specifically configured!")
    else:
        print("\nSome countries had poor coverage. May need adjustment.")

if __name__ == "__main__":
    test_country_coverage()