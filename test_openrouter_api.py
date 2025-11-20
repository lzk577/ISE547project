"""
Test script to verify OpenRouter API key
"""
import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

API_KEY = os.getenv('OPENROUTER_API_KEY')

if not API_KEY:
    print("❌ ERROR: OPENROUTER_API_KEY not found in .env file")
    print("Please run setup_env.bat first")
    exit(1)

print(f"✓ API Key loaded: {API_KEY[:20]}...{API_KEY[-10:]}")
print(f"✓ API Key length: {len(API_KEY)} characters")
print()

# Test API call
print("Testing OpenRouter API...")
print()

url = "https://openrouter.ai/api/v1/chat/completions"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "HTTP-Referer": "https://github.com/yourusername/ise547project",
    "X-Title": "Chat with Your Data",
    "Content-Type": "application/json"
}

payload = {
    "model": "openai/gpt-4",
    "messages": [
        {"role": "user", "content": "Say hello"}
    ]
}

try:
    response = requests.post(url, headers=headers, json=payload, timeout=30)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response Headers: {dict(response.headers)}")
    print()
    
    if response.status_code == 200:
        print("✅ SUCCESS! API key is valid")
        result = response.json()
        print(f"Response: {result.get('choices', [{}])[0].get('message', {}).get('content', 'No content')}")
    else:
        print(f"❌ ERROR: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 401:
            print()
            print("Possible issues:")
            print("1. API key is invalid or expired")
            print("2. API key format is incorrect")
            print("3. Account not found or not activated")
            print("4. Check your OpenRouter account at https://openrouter.ai/keys")
            
except requests.exceptions.RequestException as e:
    print(f"❌ Network Error: {e}")
    print("Please check your internet connection")




