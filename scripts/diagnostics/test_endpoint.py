#!/usr/bin/env python3
"""
Quick test to verify /news/save endpoint exists
"""
import requests

API_URL = "http://localhost:8000"

print("Testing API endpoints...\n")

# 1. Test health
try:
    response = requests.get(f"{API_URL}/health")
    print(f"✅ Health: {response.status_code}")
except:
    print("❌ API not running!")
    exit(1)

# 2. Test stats
try:
    response = requests.get(f"{API_URL}/stats")
    print(f"✅ Stats: {response.status_code}")
except:
    print("❌ Stats endpoint failed")

# 3. Test GET /news/articles
try:
    response = requests.get(f"{API_URL}/news/articles?limit=10")
    print(f"✅ GET /news/articles: {response.status_code}")
except:
    print("❌ GET /news/articles failed")

# 4. Test POST /news/save (the new endpoint)
try:
    test_data = {
        "content": "Test article content for verification",
        "category": "Test",
        "source_url": "https://test.com",
        "sentiment_polarity": 0.5,
        "sentiment_confidence": 0.8,
        "sentiment_label": "neutral"
    }
    response = requests.post(f"{API_URL}/news/save", json=test_data)
    
    if response.status_code == 200:
        print(f"✅ POST /news/save: {response.status_code}")
        print(f"   Response: {response.json()}")
    elif response.status_code == 404:
        print(f"❌ POST /news/save: 404 NOT FOUND")
        print(f"   The endpoint doesn't exist - API needs restart!")
    else:
        print(f"⚠️  POST /news/save: {response.status_code}")
        print(f"   Response: {response.text}")
except Exception as e:
    print(f"❌ POST /news/save failed: {e}")

print("\n" + "="*50)
print("If you see 404 above, do this:")
print("1. Stop the API (Ctrl+C)")
print("2. Restart: uvicorn src.web.api:app --reload")
print("3. Run this test again")
print("="*50)
