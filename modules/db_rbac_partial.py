import streamlit as st
from supabase import create_client, Client
import time
import httpx
import httpcore

# --- INITIALIZATION ---
@st.cache_resource
def init_supabase():
    url = st.secrets["supabase"]["URL"]
    # Check for Service Role Key for Admin privileges (RBAC)
    key = st.secrets["supabase"].get("SERVICE_ROLE_KEY", st.secrets["supabase"]["KEY"])
    return create_client(url, key)

supabase: Client = init_supabase()

def retry_db(func):
    """Decorator to retry Supabase queries on connection error."""
    def wrapper(*args, **kwargs):
        retries = 3
        base_delay = 1
        for attempt in range(retries):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                is_net_error = isinstance(e, (httpx.ReadError, httpx.ConnectError, httpcore.ReadError, httpcore.ConnectError)) or "Resource temporarily unavailable" in str(e)
                if is_net_error and attempt < retries - 1:
                    time.sleep(base_delay * (attempt + 1))
                    continue
                raise e
        return func(*args, **kwargs)
    return wrapper

# --- RBAC USERS Management ---

@retry_db
def get_user_by_username(username):
    """Fetch user by username for Login."""
    try:
        res = supabase.table("users").select("*").eq("username", username).execute()
        return res.data if res.data else []
    except Exception as e:
        print(f"Error fetching user: {e}")
        return []

@retry_db
def get_all_users():
    """Fetch all users for Admin Panel."""
    res = supabase.table("users").select("*").order("id").execute()
    return res.data

def create_user_record(data):
    """Create a new user."""
    supabase.table("users").insert(data).execute()

def update_user_record(user_id, data):
    """Update user details."""
    supabase.table("users").update(data).eq("id", user_id).execute()

def delete_user_record(user_id):
    """Delete a user."""
    supabase.table("users").delete().eq("id", user_id).execute()


# --- EXISTING TICKET/ASSET CRUD (Preserved) ---
# ... (Fetch Tickets, Assets, etc. - we won't rewrite them all, just append or ensure usage)
# Wait, I should maintain formatting. I will use 'replace_file_content' to inject the new functions 
# or 'multi_replace' to update init and append functions.
# Since I'm here, I'll rewrite the Init block and Append the User block.
