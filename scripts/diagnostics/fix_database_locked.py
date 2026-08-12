#!/usr/bin/env python3
"""
Fix: Database is Locked Error

Enables WAL mode for better concurrent access.
"""

import sqlite3
import os
from pathlib import Path

print("=" * 60)
print("Fixing 'database is locked' error")
print("=" * 60)

# Find database
db_path = Path("data/swahili_knowledge.db")

if not db_path.exists():
    print(f"❌ Database not found at: {db_path}")
    print("   Run from project root directory")
    exit(1)

print(f"\n✅ Found database: {db_path}")

# Check current mode
conn = sqlite3.connect(str(db_path))
cursor = conn.cursor()

cursor.execute("PRAGMA journal_mode;")
current_mode = cursor.fetchone()[0]
print(f"   Current mode: {current_mode}")

if current_mode == "wal":
    print("   ✅ Already in WAL mode - good!")
else:
    print(f"   Changing from {current_mode} to WAL mode...")
    cursor.execute("PRAGMA journal_mode=WAL;")
    new_mode = cursor.fetchone()[0]
    print(f"   ✅ Changed to: {new_mode}")

# Set busy timeout
cursor.execute("PRAGMA busy_timeout = 30000;")  # 30 seconds
print("   ✅ Set busy timeout: 30 seconds")

# Optimize
cursor.execute("PRAGMA optimize;")
print("   ✅ Optimized database")

conn.close()

print("\n" + "=" * 60)
print("✅ Database fixed!")
print("=" * 60)
print("\nWhat was done:")
print("1. Enabled WAL mode (Write-Ahead Logging)")
print("   - Allows concurrent reads/writes")
print("   - Prevents 'database is locked' errors")
print("2. Set 30-second timeout for busy database")
print("3. Optimized database")

print("\nNow restart your API:")
print("  uvicorn src.web.api:app --reload")
print("\nThe error should be gone!")
print("=" * 60)
