"""Test report generation through the API"""
import requests
import json

def test_report_generation():
    base_url = "http://127.0.0.1:5000"

    print("=== TESTING REPORT GENERATION ===\n")

    # Test 1: Simple list report
    print("1. Testing LIST report for Haiti...")
    response = requests.post(
        f"{base_url}/api/fetch_news",
        json={
            "countries": ["Haiti"],
            "report_type": "list"
        }
    )

    if response.status_code == 200:
        data = response.json()
        print(f"   SUCCESS: Got {len(data.get('articles', []))} articles")
        if data.get('articles'):
            print(f"   First article: {data['articles'][0].get('title', 'No title')[:60]}...")
    else:
        print(f"   ERROR: Status {response.status_code}")
        print(f"   Response: {response.text[:200]}")

    print("\n2. Testing SYNTHESIZED report for Haiti...")
    response = requests.post(
        f"{base_url}/api/fetch_news",
        json={
            "countries": ["Haiti"],
            "report_type": "synthesized"
        }
    )

    if response.status_code == 200:
        data = response.json()
        if 'country_reports' in data:
            print(f"   SUCCESS: Generated synthesized report")
            haiti_report = data['country_reports'].get('Haiti', {})
            print(f"   Article count: {haiti_report.get('article_count', 0)}")
            print(f"   Has narrative: {'narrative' in haiti_report}")
            print(f"   Has historical context: {'historical_context' in haiti_report}")

            # Show first 200 chars of narrative
            if 'narrative' in haiti_report:
                print(f"   Narrative preview: {haiti_report['narrative'][:200]}...")
        else:
            print(f"   ERROR: No country_reports in response")
    else:
        print(f"   ERROR: Status {response.status_code}")
        print(f"   Response: {response.text[:200]}")

    print("\n3. Testing multiple countries...")
    response = requests.post(
        f"{base_url}/api/fetch_news",
        json={
            "countries": ["Ukraine", "Somalia"],
            "report_type": "synthesized"
        }
    )

    if response.status_code == 200:
        data = response.json()
        if 'country_reports' in data:
            print(f"   SUCCESS: Generated reports for {len(data['country_reports'])} countries")
            for country in data['country_reports']:
                report = data['country_reports'][country]
                print(f"   - {country}: {report.get('article_count', 0)} articles")
        else:
            print(f"   ERROR: No country_reports in response")
    else:
        print(f"   ERROR: Status {response.status_code}")

    print("\n" + "="*50)
    print("REPORT GENERATION TEST COMPLETE")

if __name__ == "__main__":
    try:
        test_report_generation()
    except requests.exceptions.ConnectionError:
        print("ERROR: Cannot connect to dashboard. Make sure it's running:")
        print("  python dashboard.py")
    except Exception as e:
        print(f"ERROR: {e}")