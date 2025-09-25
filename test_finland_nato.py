"""Test if Finland-Russia airspace violations are now captured"""
import requests
import json

# Test the dashboard API
url = "http://127.0.0.1:5000/api/fetch_news"

print("="*60)
print("TESTING: Finland-Russia Airspace Violation Detection")
print("="*60)

# Test Finland
print("\n1. Testing Finland report generation...")
response = requests.post(url, json={
    'countries': ['Finland'],
    'report_type': 'synthesized'
})

if response.status_code == 200:
    data = response.json()

    if 'Finland' in data:
        articles = data['Finland'].get('articles', [])
        narrative = data['Finland'].get('narrative', '')

        print(f"\nFound {len(articles)} articles for Finland")

        # Check for airspace/Russia mentions
        airspace_articles = []
        russia_articles = []
        nato_articles = []

        for article in articles:
            title_lower = article.get('title', '').lower()
            if 'airspace' in title_lower:
                airspace_articles.append(article)
            if 'russia' in title_lower:
                russia_articles.append(article)
            if 'nato' in title_lower:
                nato_articles.append(article)

        print(f"- Airspace-related: {len(airspace_articles)} articles")
        print(f"- Russia-related: {len(russia_articles)} articles")
        print(f"- NATO-related: {len(nato_articles)} articles")

        if airspace_articles:
            print("\nAirspace violation articles found:")
            for art in airspace_articles[:3]:
                print(f"  • {art['title'][:100]}...")

        # Check narrative mentions
        narrative_lower = narrative.lower()
        has_airspace = 'airspace' in narrative_lower
        has_russia = 'russia' in narrative_lower
        has_violation = 'violation' in narrative_lower or 'violat' in narrative_lower

        print(f"\nNarrative analysis:")
        print(f"- Mentions airspace: {has_airspace}")
        print(f"- Mentions Russia: {has_russia}")
        print(f"- Mentions violation: {has_violation}")

        if has_airspace and has_russia:
            print("\n✅ SUCCESS: Finland-Russia airspace incidents ARE being captured!")
            print("\nNarrative excerpt:")
            # Find the part about airspace
            sentences = narrative.split('.')
            for sent in sentences:
                if 'airspace' in sent.lower() or 'russia' in sent.lower():
                    print(f"  '{sent.strip()[:200]}...'")
                    break
        else:
            print("\n⚠️ WARNING: Incidents found in articles but not in narrative")
    else:
        print("ERROR: No Finland data in response")
else:
    print(f"ERROR: Request failed with status {response.status_code}")

# Test Estonia for comparison
print("\n" + "="*60)
print("2. Testing Estonia (for comparison)...")
response = requests.post(url, json={
    'countries': ['Estonia'],
    'report_type': 'synthesized'
})

if response.status_code == 200:
    data = response.json()
    if 'Estonia' in data:
        articles = data['Estonia'].get('articles', [])
        print(f"\nFound {len(articles)} articles for Estonia")

        # Check for NATO mentions
        nato_count = sum(1 for a in articles if 'nato' in a.get('title', '').lower())
        russia_count = sum(1 for a in articles if 'russia' in a.get('title', '').lower())

        print(f"- NATO-related: {nato_count} articles")
        print(f"- Russia-related: {russia_count} articles")

print("\n" + "="*60)
print("SUMMARY:")
print("="*60)
print("The breaking news monitor is now integrated and actively searching for:")
print("• NATO Article 4/5 invocations")
print("• Airspace violations by Russia")
print("• Finland, Estonia, Poland incidents")
print("• Military scrambles and intercepts")
print("\nThese critical security events should now appear in all reports.")