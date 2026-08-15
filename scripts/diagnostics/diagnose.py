#!/usr/bin/env python3
"""
Complete Diagnostic and Fix Script
"""

import os
import sys
import requests
import subprocess
from pathlib import Path

print("=" * 60)
print("SWAHILI NLP API DIAGNOSTIC")
print("=" * 60)

# Check 1: Are we in the right directory?
print("\n1️⃣ Checking directory...")
cwd = Path.cwd()
api_file = Path("src/web/api.py")

if not api_file.exists():
    print(f"❌ Not in project root!")
    print(f"   Current: {cwd}")
    print("   Please change to the repository root.")
    sys.exit(1)
else:
    print(f"✅ In correct directory: {cwd}")

# Check 2: Does the file have the new endpoint?
print("\n2️⃣ Checking if api.py has new endpoint...")
with open(api_file, "r") as f:
    content = f.read()
    if '@app.post("/news/save"' in content:
        print("✅ File has @app.post('/news/save') endpoint")
    else:
        print("❌ File DOES NOT have the endpoint!")
        print("   You need to replace src/web/api.py")
        print("   Extract from FIX_PACKAGE.zip")
        sys.exit(1)

# Check 3: When was the file last modified?
print("\n3️⃣ Checking file timestamp...")
import time

mod_time = os.path.getmtime(api_file)
mod_date = time.ctime(mod_time)
age_seconds = time.time() - mod_time
age_minutes = age_seconds / 60

print(f"   Last modified: {mod_date}")
print(f"   Age: {age_minutes:.1f} minutes ago")

if age_minutes > 30:
    print("   ⚠️  File is old - you may not have updated it")

# Check 4: Is API running?
print("\n4️⃣ Checking if API is running...")
try:
    response = requests.get("http://localhost:8000/health", timeout=2)
    print(f"✅ API is running (status: {response.status_code})")
except requests.exceptions.ConnectionError:
    print("❌ API is NOT running!")
    print("   Start it: uvicorn src.web.api:app --reload")
    sys.exit(1)

# Check 5: Does the endpoint exist in the RUNNING API?
print("\n5️⃣ Testing if endpoint exists in RUNNING API...")
try:
    test_data = {
        "content": "Diagnostic test",
        "category": "Test",
        "sentiment_polarity": 0.0,
        "sentiment_confidence": 0.5,
        "sentiment_label": "neutral",
    }
    response = requests.post(
        "http://localhost:8000/news/save", json=test_data, timeout=5
    )

    if response.status_code == 200:
        print(f"✅ Endpoint works! Status: {response.status_code}")
        print(f"   Response: {response.json()}")
        print("\n🎉 EVERYTHING IS WORKING!")
    elif response.status_code == 404:
        print(f"❌ Endpoint returns 404 - API has OLD code!")
        print(f"\n🔧 THE FIX:")
        print(f"   The file on disk is correct, but the API is running old code.")
        print(f"   You MUST restart the API:")
        print(f"\n   Steps:")
        print(f"   1. Go to terminal running uvicorn")
        print(f"   2. Press Ctrl+C to stop it")
        print(f"   3. Run: uvicorn src.web.api:app --reload")
        print(f"   4. Run this script again to verify")
    else:
        print(f"⚠️  Unexpected status: {response.status_code}")
        print(f"   Response: {response.text}")

except Exception as e:
    print(f"❌ Request failed: {e}")

# Check 6: Available endpoints
print("\n6️⃣ Listing available endpoints from running API...")
try:
    response = requests.get("http://localhost:8000/openapi.json", timeout=2)
    if response.status_code == 200:
        openapi = response.json()
        paths = openapi.get("paths", {})

        print("   Available POST endpoints:")
        for path, methods in paths.items():
            if "post" in methods:
                print(f"   ✓ POST {path}")

        if "/news/save" not in paths:
            print(f"\n   ❌ /news/save NOT in running API!")
            print(f"      But it IS in your file on disk.")
            print(f"      This confirms: API is running OLD code")
            print(f"\n   👉 MUST RESTART API!")
except:
    pass

print("\n" + "=" * 60)
print("SUMMARY")
print("=" * 60)

# Final verdict
file_ok = '@app.post("/news/save"' in content
try:
    api_response = requests.post(
        "http://localhost:8000/news/save",
        json={
            "content": "test",
            "category": "test",
            "sentiment_polarity": 0,
            "sentiment_confidence": 0.5,
            "sentiment_label": "neutral",
        },
        timeout=2,
    )
    api_ok = api_response.status_code == 200
except:
    api_ok = False

if file_ok and api_ok:
    print("✅ EVERYTHING WORKING - No action needed!")
elif file_ok and not api_ok:
    print("⚠️  FILE CORRECT - API NEEDS RESTART")
    print("\n🔧 DO THIS NOW:")
    print("   1. Stop API (Ctrl+C in uvicorn terminal)")
    print("   2. Start API: uvicorn src.web.api:app --reload")
    print("   3. Rerun this script to verify")
elif not file_ok:
    print("❌ FILE INCORRECT - Need to replace src/web/api.py")
    print("   Extract from FIX_PACKAGE.zip")

print("=" * 60)
