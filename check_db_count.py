from modules.db import get_supabase
import streamlit as st

def check():
    print("Checking DB...")
    try:
        sb = get_supabase()
        # count headers='exact' is needed for count
        res = sb.table("tickets").select("*", count="exact").execute()
        count = len(res.data)
        print(f"DEBUG: Found {count} tickets in DB.")
        if count > 0:
            print(f"Sample: {res.data[0]}")
    except Exception as e:
        print(f"DEBUG: Error fetching: {e}")

if __name__ == "__main__":
    check()
