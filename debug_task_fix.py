
import streamlit as st
from modules.db import fetch_departments, fetch_ticket_by_id

# Mock st.secrets if needed, relying on local .streamlit/secrets.toml if present
# or just assuming the environment is set up for running this via 'streamlit run' or similar?
# Actually, the user environment seems to have 'app.py' which uses st.secrets.
# I'll rely on 'debug_app.py' logic or just try to run it. 
# But 'fetch_departments' relies on st.secrets internally via 'init_supabase'.

try:
    print("--- FETCHING DEPARTMENTS ---")
    depts = fetch_departments()
    print(f"Found {len(depts)} departments:")
    for d in depts:
        print(f" - {d}")

    print("\n--- FETCHING TICKET d65e47e9-5b1c-4e9c-87f7-5d39d7d6c5bd ---")
    ticket = fetch_ticket_by_id("d65e47e9-5b1c-4e9c-87f7-5d39d7d6c5bd")
    if ticket:
        print("Ticket Found:")
        for k, v in ticket.items():
            print(f"  {k}: {v}")
    else:
        print("Ticket NOT FOUND")

except Exception as e:
    print(f"Error: {e}")
