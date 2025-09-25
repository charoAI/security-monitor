"""Test the improved chat responses with CIA Factbook data and better formatting"""
import requests
import json

def test_chat():
    base_url = "http://127.0.0.1:5000"

    print("=== TESTING IMPROVED CHAT WITH CIA FACTBOOK DATA ===\n")

    test_cases = [
        {
            "country": "Haiti",
            "question": "What is Haiti's GDP and population according to CIA factbook?",
            "expected": "Should include population number and CIA Factbook reference"
        },
        {
            "country": "Ukraine",
            "question": "What is the capital and government type of Ukraine?",
            "expected": "Should include Kyiv and government information"
        },
        {
            "country": "Somalia",
            "question": "Tell me about Somalia's economy and area",
            "expected": "Should include area in km² and economic facts"
        }
    ]

    for i, test in enumerate(test_cases, 1):
        print(f"\nTest {i}: {test['question']}")
        print(f"Country: {test['country']}")
        print(f"Expected: {test['expected']}")
        print("-" * 50)

        response = requests.post(
            f"{base_url}/api/chat",
            json={
                "country": test["country"],
                "question": test["question"],
                "context": "Recent news context here..."
            }
        )

        if response.status_code == 200:
            data = response.json()
            answer = data.get('answer', 'No answer')

            print("Response:")
            print(answer)

            # Check for formatting issues
            print("\nFormatting Check:")
            issues = []

            if "**" in answer:
                issues.append("- Contains markdown bold (**)")
            if "***" in answer:
                issues.append("- Contains markdown bold-italic (***)")
            if "###" in answer or "##" in answer:
                issues.append("- Contains markdown headers (##)")
            if "*" in answer and not "**" in answer:
                issues.append("- Contains asterisks for bullets")

            if issues:
                print("Issues found:")
                for issue in issues:
                    print(f"  {issue}")
            else:
                print("  ✓ Clean formatting (no markdown)")

            # Check for CIA data
            if "population" in test['question'].lower():
                if any(char.isdigit() for char in answer):
                    print("  ✓ Contains population numbers")
                else:
                    print("  ✗ Missing population numbers")

            if "cia" in test['question'].lower() or "factbook" in test['question'].lower():
                if "cia.gov" in answer.lower() or "factbook" in answer.lower():
                    print("  ✓ Contains CIA Factbook reference")
                else:
                    print("  ✗ Missing CIA Factbook reference")

        else:
            print(f"ERROR: Status {response.status_code}")
            print(response.text[:200])

    print("\n" + "="*50)
    print("EXAMPLE OF GOOD FORMATTING:")
    print("-"*50)
    print("""Haiti has a population of 11.4 million and struggles economically.
Key facts:
- Capital: Port-au-Prince
- GDP per capita: $1,800 (2020 est.)
- Area: 27,750 km²

Source: CIA World Factbook""")

    print("\n" + "="*50)
    print("EXAMPLE OF BAD FORMATTING (to avoid):")
    print("-"*50)
    print("""**Haiti** has a population of ***11.4 million*** and struggles economically.

### Key Facts:
* Capital: **Port-au-Prince**
* GDP per capita: *$1,800*
* Area: 27,750 km²""")

if __name__ == "__main__":
    try:
        test_chat()
    except requests.exceptions.ConnectionError:
        print("ERROR: Cannot connect to dashboard.")
        print("Make sure it's running: python dashboard.py")