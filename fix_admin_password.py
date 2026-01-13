import streamlit as st
import bcrypt
from modules.db import init_supabase

def fix_password():
    print("--- FIXING ADMIN PASSWORD ---")
    supabase = init_supabase()
    
    username = "alain_admin"
    password = "supad_alain1"
    
    # 1. Generate New Hash
    # Using default rounds (12) and 2b prefix
    new_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    print(f"Generated new hash: {new_hash}")
    
    # 2. Update DB
    try:
        response = supabase.table("users").update({"password_hash": new_hash}).eq("username", username).execute()
        print(f"Update response: {response}")
        
        if response.data:
            print("✅ Password updated successfully!")
        else:
            print("⚠️ Update returned no data, user might not exist.")
            
    except Exception as e:
        print(f"Update Error: {e}")

if __name__ == "__main__":
    fix_password()
