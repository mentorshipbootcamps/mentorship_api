from supabase import create_client, Client
import os
from typing import Generator

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://xlkqhnssdyfxqjvtyxcp.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")

if not SUPABASE_KEY:
    raise ValueError(
        "SUPABASE_ANON_KEY environment variable is required. "
        "Get your Supabase anon key from: https://app.supabase.com/project/_/settings/api"
    )

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


class Base:
    """Dummy Base class for compatibility with existing code"""
    pass


def get_supabase() -> Client:
    """Dependency to get Supabase client"""
    return supabase


def get_db() -> Client:
    """Compatibility function - returns Supabase client (for backward compatibility)"""
    return supabase
