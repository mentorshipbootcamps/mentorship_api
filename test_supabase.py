#!/usr/bin/env python3
"""Test Supabase connection"""
from dotenv import load_dotenv
import os

load_dotenv()

supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_ANON_KEY")

if not supabase_url:
    print("❌ SUPABASE_URL not found in .env file")
    exit(1)

if not supabase_key:
    print("❌ SUPABASE_ANON_KEY not found in .env file")
    exit(1)

print(f"Testing connection to Supabase...")
print(f"URL: {supabase_url}")

try:
    from app.database import supabase
    
    response = supabase.table("users").select("count", count="exact").execute()
    print(f"✅ Connection successful!")
    print(f"Users table exists and is accessible")
    
    if response.count is not None:
        print(f"Current user count: {response.count}")
    
except Exception as e:
    print(f"❌ Connection failed: {e}")
    print("\nTroubleshooting:")
    print("1. Check if your Supabase project is active (not paused)")
    print("2. Verify SUPABASE_URL and SUPABASE_ANON_KEY in .env file")
    print("3. Make sure the 'users' table exists in your Supabase database")
    print("4. Check your network connection")
    exit(1)

