import os
from dotenv import load_dotenv

load_dotenv()

gemini_key = os.getenv('GEMINI_API_KEY')

if gemini_key:
    if gemini_key == 'your_gemini_api_key_here':
        print("GEMINI_API_KEY is still set to placeholder value")
    else:
        print(f"GEMINI_API_KEY is set: {gemini_key[:20]}...")
else:
    print("GEMINI_API_KEY is not set in .env file")

# Test if it works
try:
    import google.generativeai as genai
    genai.configure(api_key=gemini_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content("Say 'API works'")
    print(f"API Test: {response.text}")
except Exception as e:
    print(f"API Error: {e}")