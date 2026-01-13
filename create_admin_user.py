import streamlit as st
from supabase import create_client

def create_admin():
    # 1. Get Secrets
    try:
        # Check global first
        if "global" in st.secrets:
            url = st.secrets["global"]["SUPABASE_URL"]
            service_key = st.secrets["global"]["SUPABASE_SERVICE_KEY"]
        else:
            url = st.secrets["SUPABASE_URL"]
            service_key = st.secrets["SUPABASE_SERVICE_KEY"]
    except Exception as e:
        print(f"Error fetching secrets: {e}")
        return

    # 2. Init Admin Client
    supabase = create_client(url, service_key)
    
    email = "admin@cholchol.cl"
    password = "admin123"
    
    print(f"Attempting to create user: {email}...")
    
    try:
        # 3. Create User via Admin API
        # Supabase Python client signature for admin.create_user might vary by version
        # trying standard gotrue signatures
        
        attributes = {
            "email": email,
            "password": password,
            "email_confirm": True,
            "user_metadata": {"full_name": "Administrador", "role": "ADMIN"}
        }
        
        user = supabase.auth.admin.create_user(attributes)
        print(f"User created successfully: {user}")
        
    except Exception as e:
        print(f"Error creating user (might already exist): {e}")

if __name__ == "__main__":
    create_admin()
