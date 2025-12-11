#!/usr/bin/env python3
"""
Helper script to update DATABASE_URL in .env file with connection pooling string
"""
import os
import re
from pathlib import Path

def update_env_file(connection_string):
    """Update DATABASE_URL in .env file"""
    env_path = Path(".env")
    
    if not env_path.exists():
        print("❌ .env file not found!")
        return False
    
    # Read current .env
    with open(env_path, 'r') as f:
        content = f.read()
    
    # Check if DATABASE_URL exists
    if 'DATABASE_URL=' in content:
        # Replace existing DATABASE_URL
        pattern = r'DATABASE_URL=.*'
        new_line = f'DATABASE_URL={connection_string}'
        content = re.sub(pattern, new_line, content)
        print("✓ Updated existing DATABASE_URL")
    else:
        # Append new DATABASE_URL
        content += f'\nDATABASE_URL={connection_string}\n'
        print("✓ Added new DATABASE_URL")
    
    # Write back
    with open(env_path, 'w') as f:
        f.write(content)
    
    print("✅ .env file updated successfully!")
    return True

if __name__ == "__main__":
    print("=" * 60)
    print("Supabase Connection String Updater")
    print("=" * 60)
    print("\nTo get your connection pooling string:")
    print("1. Go to: https://app.supabase.com/project/xlkqhnssdyfxqjvtyxcp/settings/database")
    print("2. Scroll to 'Connection string' section")
    print("3. Select 'Connection pooling' tab")
    print("4. Copy the connection string")
    print("\n" + "=" * 60)
    
    connection_string = input("\nPaste your connection pooling string here: ").strip()
    
    if not connection_string:
        print("❌ No connection string provided!")
        exit(1)
    
    if "pooler.supabase.com" not in connection_string and "6543" not in connection_string:
        print("⚠️  Warning: This doesn't look like a connection pooling string.")
        print("   Connection pooling strings usually contain 'pooler.supabase.com' and port 6543")
        confirm = input("Continue anyway? (y/n): ").strip().lower()
        if confirm != 'y':
            exit(1)
    
    if update_env_file(connection_string):
        print("\n✅ Done! You can now test the connection with:")
        print("   python test_connection.py")
        print("\nOr create the admin user with:")
        print("   python create_admin.py")

