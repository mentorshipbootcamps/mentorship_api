#!/usr/bin/env python3
"""
Setup script to configure Supabase environment variables
"""
import os
from pathlib import Path
from dotenv import load_dotenv, set_key

load_dotenv()

env_file = Path(".env")

print("=" * 60)
print("Supabase Setup")
print("=" * 60)
print("\nYour Supabase project URL: https://xlkqhnssdyfxqjvtyxcp.supabase.co")
print("\nYou need to set:")
print("1. SUPABASE_URL (already set to your project URL)")
print("2. SUPABASE_ANON_KEY (get from Supabase dashboard)")

supabase_url = input("\nSupabase URL (press Enter to use default): ").strip()
if not supabase_url:
    supabase_url = "https://xlkqhnssdyfxqjvtyxcp.supabase.co"

anon_key = input("\nPaste your Supabase anon key: ").strip()

if not anon_key:
    print("❌ Anon key is required!")
    exit(1)

if env_file.exists():
    set_key(env_file, "SUPABASE_URL", supabase_url)
    set_key(env_file, "SUPABASE_ANON_KEY", anon_key)
    print("\n✅ Updated .env file with Supabase credentials")
else:
    with open(env_file, "w") as f:
        f.write(f"SUPABASE_URL={supabase_url}\n")
        f.write(f"SUPABASE_ANON_KEY={anon_key}\n")
        f.write("SECRET_KEY=dev-secret-key-change-in-production\n")
    print("\n✅ Created .env file with Supabase credentials")

print("\nYou can now:")
print("1. Test connection: python test_supabase.py")
print("2. Create admin user: python create_admin.py")

