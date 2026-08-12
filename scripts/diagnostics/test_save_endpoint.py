#!/usr/bin/env python3
"""
Quick test: Check if /news/save endpoint is working

Usage:
    python test_save_endpoint.py
"""

import requests
import json

API_URL = "http://localhost:8000"

# Test data
test_article = {
    "content": "Habari za leo ni nzuri sana. Serikali imeahidi kuboresha huduma.",
    "category": "Politics",
    "source_url": "https://example.com/test",
    "sentiment_polarity": 0.5,
    "sentiment_confidence": 0.8,
    "sentiment_label": "positive",
}

print("=" * 60)
print("Testing POST /news/save endpoint")
print("=" * 60)

try:
    # Test the endpoint
    response = requests.post(f"{API_URL}/news/save", json=test_article, timeout=10)

    print(f"\nStatus Code: {response.status_code}")

    if response.status_code == 200:
        print("✅ SUCCESS!")
        print(f"\nResponse:")
        print(json.dumps(response.json(), indent=2))
    elif response.status_code == 404:
        print("❌ 404 Not Found - Endpoint doesn't exist!")
        print("\n🔧 SOLUTION:")
        print("1. Stop your API (Ctrl+C)")
        print("2. Make sure you replaced src/web/api.py")
        print("3. Restart: uvicorn src.web.api:app --reload")
    else:
        print(f"❌ Error: {response.status_code}")
        print(f"Response: {response.text}")

except requests.exceptions.ConnectionError:
    print("❌ Cannot connect to API!")
    print("\n🔧 SOLUTION:")
    print("Start the API first:")
    print("uvicorn src.web.api:app --reload")

except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "=" * 60)
