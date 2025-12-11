#!/usr/bin/env python3
"""Test Supabase database connection"""
from dotenv import load_dotenv
import os
import psycopg2
from urllib.parse import urlparse, quote_plus

load_dotenv()

database_url = os.getenv("DATABASE_URL")

if not database_url:
    print("❌ DATABASE_URL not found in .env file")
    exit(1)

print(f"Testing connection to Supabase...")
print(f"Connection string: {database_url.split('@')[0]}@[HIDDEN]")

try:
    # Parse and test connection
    parsed = urlparse(database_url)
    
    conn = psycopg2.connect(
        host=parsed.hostname,
        port=parsed.port or 5432,
        database=parsed.path[1:] if parsed.path else 'postgres',
        user=parsed.username,
        password=parsed.password
    )
    
    cur = conn.cursor()
    cur.execute("SELECT version();")
    version = cur.fetchone()
    print(f"✅ Connection successful!")
    print(f"PostgreSQL version: {version[0]}")
    
    cur.close()
    conn.close()
    
except Exception as e:
    print(f"❌ Connection failed: {e}")
    print("\nTroubleshooting:")
    print("1. Check if your Supabase project is active (not paused)")
    print("2. Verify the connection string format in Supabase dashboard")
    print("3. Check your network connection")
    print("4. Try the connection string from: https://app.supabase.com/project/xlkqhnssdyfxqjvtyxcp/settings/database")
    exit(1)
