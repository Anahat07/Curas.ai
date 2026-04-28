import os
from supabase import create_client

def get_client():
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")  # <-- IMPORTANT FIX

    if not url or not key:
        raise ValueError("Missing Supabase environment variables")

    return create_client(url, key)