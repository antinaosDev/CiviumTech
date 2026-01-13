import streamlit as st
from modules.db import get_supabase
import sys

# Mock streamlit secrets if running from CLI directly (optional, 
# but we usually assume this is run via `streamlit run` or we patch it)
# For simplicity, we assume this is run in an environment where modules.db works 
# (e.g. via 'streamlit run verify_db_setup.py' or if we patch st.secrets manually)

try:
    client = get_supabase()
except Exception as e:
    print(f"CRITICAL: Cannot connect to Supabase. {e}")
    sys.exit(1)

def check_table(table_name, required_columns=[]):
    print(f"Checking table '{table_name}'...", end=" ")
    try:
        # Fetch 1 row to check existence
        res = client.table(table_name).select("*").limit(1).execute()
        print("EXISTS.", end=" ")
        
        # Check columns if possible (by inspecting the returned data keys if data exists, 
        # or just trusting the select(*) didn't fail which implies table exists)
        # Note: If table is empty, we can't easily verify columns via REST without metadata API.
        # But we can try to select specific columns.
        
        if required_columns:
            try:
                cols_str = ",".join(required_columns)
                client.table(table_name).select(cols_str).limit(1).execute()
                print(f"Columns {required_columns} VERIFIED.")
            except Exception as e:
                print(f"FAILED. Missing columns {required_columns}. Error: {e}")
                return False
        else:
            print("OK.")
        return True
    except Exception as e:
        print(f"FAILED. Table might be missing. Error: {e}")
        return False

print("--- SUPABASE INTEGRITY CHECK ---")
all_good = True

if not check_table("departments", ["id", "name"]): all_good = False
if not check_table("sub_units", ["id", "department_id"]): all_good = False
if not check_table("tickets", ["id", "ticket_number", "depto"]): all_good = False
if not check_table("assets", ["id", "name", "status"]): all_good = False
if not check_table("ticket_comments", ["id", "ticket_id"]): all_good = False

print("--------------------------------")
if all_good:
    print("SUCCESS: Database schema appears correct for the application.")
else:
    print("FAILURE: Some tables or columns are missing.")
    print("ACTION REQUIRED: Run the contents of 'complete_setup.sql' in your Supabase SQL Editor.")
