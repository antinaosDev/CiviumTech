import streamlit as st
import bcrypt
from modules.db import init_supabase

# Mock secrets if running standalone
if not hasattr(st, "secrets"):
    print("Please run with: streamlit run debug_login.py")
    exit()

def test_login():
    print("--- DEBUGGING LOGIN ---")
    supabase = init_supabase()
    
    username = "alain_admin"
    password = "supad_alain1"
    
    print(f"Checking user: {username}")
    
    # 1. Fetch User
    try:
        response = supabase.table("users").select("*").eq("username", username).execute()
        users = response.data
    except Exception as e:
        print(f"DB Error: {e}")
        return

    if not users:
        print("❌ User 'alain_admin' NOT FOUND in database.")
        return

    user = users[0]
    print(f"✅ User found: {user['username']} (Role: {user['role']})")
    
    # 2. Check Password
    stored_hash = user.get('password_hash')
    print(f"Stored Hash (prefix): {stored_hash[:10]}...")
    
    if not stored_hash:
        print("❌ No password_hash found for user.")
        return
        
    try:
        # Encode inputs
        pwd_bytes = password.encode('utf-8')
        hash_bytes = stored_hash.encode('utf-8')
        
        if bcrypt.checkpw(pwd_bytes, hash_bytes):
            print("✅ LOGIN SUCCESS: Password matches stored hash.")
        else:
            print("❌ LOGIN FAILED: Password does NOT match hash.")
            
            # Generate new hash for reference
            new_hash = bcrypt.hashpw(pwd_bytes, bcrypt.gensalt()).decode('utf-8')
            print(f"ℹ️  Expected equivalent hash would look like: {new_hash[:10]}...")
            
            # Offer Solution
            print("\nTo fix, we should update the password hash in the database.")
            
    except Exception as e:
        print(f"Bcrypt Error: {e}")

if __name__ == "__main__":
    test_login()
