
import toml
import sys
from unittest.mock import MagicMock
import os

# Function to locate secrets
def load_secrets():
    paths = [".streamlit/secrets.toml", "../.streamlit/secrets.toml"]
    for p in paths:
        if os.path.exists(p):
            return toml.load(p)
    return {}

secrets = load_secrets()
if not secrets:
    print("WARNING: No secrets.toml found. DB connection may fail.")

# Mock streamlit
st = MagicMock()
st.secrets = secrets
st.cache_resource = lambda func: func # minimal mock for cache
sys.modules["streamlit"] = st

# Now import modules
try:
    from modules.db import fetch_departments, fetch_ticket_by_id
except ImportError as e:
    print(f"Import Error: {e}")
    sys.exit(1)

try:
    print("\n--- FETCHING DEPARTMENTS ---")
    depts = fetch_departments()
    print(f"Found {len(depts)} departments:")
    for d in depts:
        print(f"ID: {d.get('id')} | Name: {d.get('name')} | Code: {d.get('code')}")

    target_id = "d65e47e9-5b1c-4e9c-87f7-5d39d7d6c5bd"
    print(f"\n--- FETCHING TICKET {target_id} ---")
    ticket = fetch_ticket_by_id(target_id)
    if ticket:
        print("Ticket Found:")
        for k, v in ticket.items():
            print(f"  {k}: {v}")
    else:
        print("Ticket NOT FOUND")

except Exception as e:
    print(f"Error: {e}")
