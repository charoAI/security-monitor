import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Get API key
api_key = os.getenv('GEMINI_API_KEY')

if not api_key:
    print("ERROR: No GEMINI_API_KEY found in .env file")
    print("Make sure you have this line in your .env file:")
    print("GEMINI_API_KEY=your_actual_key_here")
else:
    print(f"API Key found: {api_key[:10]}...")
    
    try:
        # Configure Gemini
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Test with a simple prompt
        response = model.generate_content("Say 'Hello, intelligence system is working!'")
        print("\nGemini response:", response.text)
        print("\n✓ Gemini is working correctly!")
        
    except Exception as e:
        print(f"\nERROR testing Gemini: {e}")
        print("\nPossible issues:")
        print("1. Invalid API key")
        print("2. API key not activated")
        print("3. Network issues")
        print("4. Gemini API quota exceeded")