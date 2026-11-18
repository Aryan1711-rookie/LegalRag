
from database.supabase import (
    get_supabase,
    create_auth_client
)

db_client = get_supabase()
auth_client = create_auth_client()

print("Database client:", type(db_client).__name__)
print("Authentication client:", type(auth_client).__name__)

print("Both Supabase clients initialized successfully.")
