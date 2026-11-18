import os
from pathlib import Path
from dotenv import load_dotenv # pyright: ignore[reportMissingImports]
from supabase import Client, create_client


BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR/".env"
load_dotenv(ENV_PATH, override = True)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_PUBLISHABLE_KEY = os.getenv("SUPABASE_PUBLISHABLE_KEY")
SUPABASE_SECRET_KEY = os.getenv("SECRET_KEY")

if not SUPABASE_URL or not SUPABASE_SECRET_KEY:
    raise ValueError(
        "SUPABASE_URL or SUPABASE_KEY is missing in .env"
    )

supabase: Client = create_client(SUPABASE_URL, SUPABASE_SECRET_KEY)

def get_supabase() -> Client:
    return supabase

def create_auth_client() -> Client:
    """
    Creates a Supabase client for authentication purposes using the publishable key.
    Used for user authentication operations such as signup and login.
    """
    return create_client(SUPABASE_URL, SUPABASE_PUBLISHABLE_KEY)