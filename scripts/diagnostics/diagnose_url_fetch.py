#!/usr/bin/env python3
"""
Diagnostic: Check if URL fetching works

Tests URL fetching to identify where the 500 error comes from.
"""

import requests
from bs4 import BeautifulSoup

print("=" * 60)
print("URL FETCH DIAGNOSTIC")
print("=" * 60)

# Test URLs
test_urls = [
    "https://www.bbc.com/swahili",
    "https://www.bbc.com/swahili/articles/c88888888888",  # BBC article
    "https://www.voaswahili.com",
    "https://www.dw.com/sw",
]

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

for url in test_urls:
    print(f"\n{'=' * 60}")
    print(f"Testing: {url}")
    print(f"{'=' * 60}")

    try:
        # 1. Test basic fetch
        print("1️⃣ Fetching URL...")
        response = requests.get(url, headers=headers, timeout=10)
        print(f"   Status Code: {response.status_code}")

        if response.status_code == 200:
            print("   ✅ Fetch successful")

            # 2. Test HTML parsing
            print("2️⃣ Parsing HTML...")
            soup = BeautifulSoup(response.text, "html.parser")

            # Remove scripts and styles
            for script in soup(["script", "style", "nav", "footer", "header"]):
                script.decompose()

            # Get paragraphs
            paragraphs = soup.find_all("p")
            print(f"   Found {len(paragraphs)} paragraphs")

            # Get text
            text = " ".join([p.get_text() for p in paragraphs])
            text = " ".join(text.split())  # Clean whitespace

            print(f"   Extracted {len(text)} characters")
            print(f"   Word count: {len(text.split())}")

            if len(text) > 100:
                print(f"   ✅ Text extraction successful")
                print(f"\n   Preview: {text[:200]}...")
            else:
                print(f"   ⚠️  Very little text extracted")
                print(f"   Text: {text}")

        elif response.status_code == 403:
            print("   ❌ 403 Forbidden - Website is blocking us")
            print("   This is NOT your fault - BBC blocks scrapers")
        elif response.status_code == 404:
            print("   ❌ 404 Not Found - Invalid URL")
        elif response.status_code >= 500:
            print(f"   ❌ {response.status_code} - BBC server error")
            print("   This is BBC's problem, not yours")
        else:
            print(f"   ⚠️  Unexpected status: {response.status_code}")

    except requests.exceptions.Timeout:
        print("   ❌ Timeout - Site is slow or unreachable")
    except requests.exceptions.ConnectionError:
        print("   ❌ Connection Error - Check your internet")
    except Exception as e:
        print(f"   ❌ Error: {type(e).__name__}: {str(e)}")

print("\n" + "=" * 60)
print("SUMMARY")
print("=" * 60)

print("""
If you see:
- ✅ 200 + text extracted → URL fetching WORKS
- ❌ 403 Forbidden → BBC is blocking scrapers (common)
- ❌ 500 errors → BBC server issue (their fault)
- ❌ Timeout → Slow connection or firewall

Solutions for blocked sites:
1. Use different news sources (VOA, DW)
2. Add delays between requests
3. Rotate User-Agent headers
4. Use a proxy service
5. Manually copy/paste text into "Linguistic Insights" tab
""")

print("\nTesting with your API...")
print("=" * 60)

try:
    api_response = requests.post(
        "http://localhost:8000/analyze/url",
        json={"url": "https://www.bbc.com/swahili"},
        timeout=30,
    )

    print(f"API Status: {api_response.status_code}")

    if api_response.status_code == 200:
        data = api_response.json()
        if data.get("success"):
            print("✅ API URL analysis WORKS!")
            print(f"   Word count: {data.get('word_count', 'N/A')}")
        else:
            print(f"❌ API returned error: {data.get('error', 'Unknown')}")
    elif api_response.status_code == 500:
        print("❌ 500 Internal Server Error from API")
        print("   Check API terminal for error details")
        try:
            error_detail = api_response.json()
            print(f"   Error: {error_detail}")
        except:
            print(f"   Raw response: {api_response.text[:200]}")
    else:
        print(f"⚠️  API returned: {api_response.status_code}")

except requests.exceptions.ConnectionError:
    print("❌ Cannot connect to API - is it running?")
except Exception as e:
    print(f"❌ Error calling API: {e}")

print("=" * 60)
