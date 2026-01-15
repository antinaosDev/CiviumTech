import streamlit as st
from supabase import create_client, Client
import httpx
import httpcore
import time

# --- INITIALIZATION ---
@st.cache_resource
def init_supabase() -> Client:
    """Initialize Supabase client using Streamlit secrets."""
    try:
        # Check for keys in [global] section first, then top-level
        # Logic updated for RBAC: Check for SERVICE_ROLE_KEY if needing admin writes
        # We prefer SERVICE_ROLE_KEY if available for this internal tool usage
        if "supabase" in st.secrets:
             url = st.secrets["supabase"]["URL"]
             key = st.secrets["supabase"].get("SERVICE_ROLE_KEY", st.secrets["supabase"]["KEY"])
        elif "global" in st.secrets:
            url = st.secrets["global"]["SUPABASE_URL"]
            key = st.secrets["global"]["SUPABASE_KEY"]
        else:
            url = st.secrets["SUPABASE_URL"]
            key = st.secrets["SUPABASE_KEY"]
            
        return create_client(url, key)
    except Exception as e:
        st.error(f"Error connecting to Supabase: {e}")
        st.stop()

def get_supabase() -> Client:
    return init_supabase()

def retry_db(func):
    """Decorator to retry Supabase queries on connection error."""
    def wrapper(*args, **kwargs):
        retries = 3
        base_delay = 1
        for attempt in range(retries):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                error_msg = str(e)
                is_network_error = (
                    "Resource temporarily unavailable" in error_msg or 
                    "ReadError" in error_msg or 
                    "ConnectError" in error_msg or
                    isinstance(e, (httpx.ReadError, httpx.ConnectError, httpcore.ReadError, httpcore.ConnectError))
                )
                
                if is_network_error:
                    if attempt < retries - 1:
                        sleep_time = base_delay * (attempt + 1)
                        print(f"Database connection error: {e}. Retrying in {sleep_time}s... (Attempt {attempt+1}/{retries})")
                        time.sleep(sleep_time)
                        continue
                raise e
        return func(*args, **kwargs)
    return wrapper

# --- RBAC USERS Management ---

@retry_db
def get_user_by_username(username):
    """Fetch user by username for Login."""
    client = get_supabase()
    try:
        res = client.table("users").select("*").eq("username", username).execute()
        return res.data if res.data else []
    except Exception as e:
        print(f"Error fetching user: {e}")
        return []

@retry_db
def get_all_users():
    """Fetch all users for Admin Panel."""
    client = get_supabase()
    try:
        res = client.table("users").select("*").order("id").execute()
        return res.data
    except Exception:
        return []

def create_user_record(data):
    """Create a new user."""
    client = get_supabase()
    return client.table("users").insert(data).execute()

def update_user_record(user_id, data):
    """Update user details."""
    client = get_supabase()
    return client.table("users").update(data).eq("id", user_id).execute()

def delete_user_record(user_id):
    """Delete a user."""
    client = get_supabase()
    return client.table("users").delete().eq("id", user_id).execute()

@retry_db
def fetch_departments():
    """Fetch all departments for selection."""
    client = get_supabase()
    try:
        res = client.table("departments").select("id, name, code").order("name").execute()
        return res.data if res.data else []
    except Exception as e:
        print(f"Error fetching departments: {e}")
        return []

# --- TICKETS CRUD ---

@retry_db
def fetch_tickets(filters=None, limit=200):
    """
    Fetch tickets with optional filters (dict) and limit.
    filters example: {'depto': 'DOM_DIR', 'status': 'Pendiente'}
    """
    client = get_supabase()
    query = client.table("tickets").select("*").order("created_at", desc=True)
    
    if filters:
        for k, v in filters.items():
            if v and v != 'Todos':
                query = query.eq(k, v)

    if limit:
        query = query.limit(limit)

    response = query.execute()
    return response.data if response.data else []

def fetch_user_tickets(email):
    """Citizen: Fetch only my tickets."""
    client = get_supabase()
    response = client.table("tickets").select("*").eq("user_email", email).order("created_at", desc=True).execute()
    return response.data if response.data else []

def create_ticket(ticket_data):
    """Insert a new ticket."""
    client = get_supabase()
    # Let exceptions propagate to UI for debugging
    res = client.table("tickets").insert(ticket_data).execute()
    return res

def fetch_ticket_by_id(ticket_id):
    """Fetch a single ticket by its ID (supports full UUID or short prefix)."""
    ticket_id = str(ticket_id).strip()
    
    # 1. If it looks like a full UUID (36 chars), try direct fetch
    if len(ticket_id) == 36:
        try:
             client = get_supabase()
             response = client.table("tickets").select("*").eq("id", ticket_id).execute()
             if response.data:
                 return response.data[0]
        except Exception:
            pass # Fallthrough if invalid format but len 36
            
    # 2. Short ID Logic: Search recent tickets
    # Since we can't easily do 'ilike' on UUID, we fetch a batch of recent IDs and filter in Python.
    # Limiting to 2000 most recent tickets should cover active cases for a while.
    if len(ticket_id) >= 6:
        client = get_supabase()
        try:
            # Optimize: Get only ID first to scan
            res = client.table("tickets").select("id").order("created_at", desc=True).limit(2000).execute()
            
            found_full_id = None
            if res.data:
                for t in res.data:
                    if str(t['id']).startswith(ticket_id):
                        found_full_id = t['id']
                        break
            
            if found_full_id:
                # Fetch the full record
                final_res = client.table("tickets").select("*").eq("id", found_full_id).execute()
                if final_res.data:
                    return final_res.data[0]
                    
        except Exception as e:
            print(f"Error searching short ID: {e}")
            return None

    return None

def delete_ticket(ticket_id):
    """Delete a ticket."""
    client = get_supabase()
    res = client.table("tickets").delete().eq('id', ticket_id).execute()
    return True

def update_ticket(ticket_id, updates):
    """Update ticket fields."""
    client = get_supabase()
    res = client.table("tickets").update(updates).eq('id', ticket_id).execute()
    return res

# --- ASSETS CRUD ---

@retry_db
def fetch_all_assets():
    """Fetch all assets."""
    client = get_supabase()
    response = client.table("assets").select("*").order("created_at", desc=True).execute()
    return response.data if response.data else []

def create_asset(asset_data):
    """Insert a new asset."""
    client = get_supabase()
    res = client.table("assets").insert(asset_data).execute()
    return res

def update_asset(asset_id, updates):
    """Update an existing asset."""
    client = get_supabase()
    res = client.table("assets").update(updates).eq('id', asset_id).execute()
    return res

def delete_asset(asset_id):
    """Delete an asset."""
    client = get_supabase()
    res = client.table("assets").delete().eq('id', asset_id).execute()
    return True

# --- DYNAMIC CONTENT CRUD ---

# 1. Activities
@retry_db
def fetch_activities():
    """Fetch all upcoming activities."""
    client = get_supabase()
    # Fetch all, ideally order by date
    res = client.table("activities").select("*").order("date_str").execute()
    return res.data if res.data else []

def create_activity(data):
    """Create a new activity."""
    client = get_supabase()
    return client.table("activities").insert(data).execute()

def delete_activity(activity_id):
    """Delete an activity."""
    client = get_supabase()
    return client.table("activities").delete().eq("id", activity_id).execute()

def update_activity(activity_id, updates):
    """Update an activity."""
    client = get_supabase()
    return client.table("activities").update(updates).eq("id", activity_id).execute()

# 2. Site Config (Pharmacies, Emergency)
@retry_db
def fetch_config(key):
    """Fetch config value by key. Returns string or empty."""
    client = get_supabase()
    res = client.table("site_config").select("value").eq("key", key).execute()
    if res.data:
        return res.data[0]['value']
    return ""

def update_config(key, value):
    """Update or insert config value."""
    client = get_supabase()
    data = {"key": key, "value": value, "updated_at": "now()"}
    return client.table("site_config").upsert(data).execute()
