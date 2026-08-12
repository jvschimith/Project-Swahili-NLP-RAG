#!/usr/bin/env python3
"""
Test /news/save endpoint and show detailed error
"""

import requests
import json

print("=" * 60)
print("Testing POST /news/save with detailed error output")
print("=" * 60)

# Test data (minimal valid request)
test_data = {
    "content": "Habari za leo ni nzuri sana. Waziri amesema uchumi unaendelea vizuri.",
    "category": "Politics",
    "source_url": "https://test.com/article1",
    "sentiment_polarity": 0.5,
    "sentiment_confidence": 0.8,
    "sentiment_label": "positive",
}

print("\nSending request to: http://localhost:8000/news/save")
print(f"Data: {json.dumps(test_data, indent=2)}")
print("\n" + "=" * 60)

try:
    response = requests.post(
        "http://localhost:8000/news/save", json=test_data, timeout=10
    )

    print(f"\nStatus Code: {response.status_code}")
    print("=" * 60)

    if response.status_code == 200:
        print("✅ SUCCESS!")
        print(json.dumps(response.json(), indent=2))

    elif response.status_code == 500:
        print("❌ 500 INTERNAL SERVER ERROR")
        print("\nThis means there's a bug in the API code.")
        print("Check the API terminal for the Python traceback.")
        print("\nResponse content:")
        print("-" * 60)
        try:
            error_data = response.json()
            print(json.dumps(error_data, indent=2))
        except:
            print(response.text)
        print("-" * 60)

        print("\n🔍 Common causes of 500 error in /news/save:")
        print("1. Database connection issue")
        print("2. Missing import (NewsArticle or SentimentScore)")
        print("3. NewsRepository.save() method error")
        print("4. Database schema mismatch")
        print("5. Pydantic validation error")

        print("\n📋 To debug:")
        print("1. Look at API terminal for full Python traceback")
        print("2. Look for lines starting with 'Traceback' or 'Error'")
        print("3. Share that error here")

    elif response.status_code == 404:
        print("❌ 404 NOT FOUND")
        print("Endpoint doesn't exist - API needs restart")

    elif response.status_code == 422:
        print("❌ 422 VALIDATION ERROR")
        print("Request data format is wrong")
        print(json.dumps(response.json(), indent=2))

    else:
        print(f"⚠️  Unexpected status: {response.status_code}")
        print(response.text)

except requests.exceptions.ConnectionError:
    print("❌ Cannot connect to API")
    print("Make sure API is running: uvicorn src.web.api:app --reload")

except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "=" * 60)
