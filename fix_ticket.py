
import toml
import sys
from unittest.mock import MagicMock
import os

# --- MOCK SETUP (Same as debug_console.py) ---
def load_secrets():
    paths = [".streamlit/secrets.toml", "../.streamlit/secrets.toml"]
    for p in paths:
        if os.path.exists(p):
            return toml.load(p)
    return {}

secrets = load_secrets()
if not secrets:
    print("WARNING: No secrets.toml found.")

st = MagicMock()
st.secrets = secrets
st.cache_resource = lambda func: func
sys.modules["streamlit"] = st

from modules.db import update_ticket, fetch_ticket_by_id

TICKET_ID = "d65e47e9-5b1c-4e9c-87f7-5d39d7d6c5bd"

print(f"--- PATCHING TICKET {TICKET_ID} ---")
ticket = fetch_ticket_by_id(TICKET_ID)

if not ticket:
    print("Ticket not found! Cannot patch.")
    sys.exit(1)

print(f"Current Citizen Name: {ticket.get('citizen_name')}")
print(f"Current Category: {ticket.get('category')}")

# PATCH DATA
updates = {
    "citizen_name": "Interna - Dir. Admin y Finanzas",
    "category": "Interna",
    # Optionally update status if needed, but user didn't explicitly ask to change from Pendiente
}

try:
    update_ticket(TICKET_ID, updates)
    print("Update command sent.")
    
    # Verify
    updated_ticket = fetch_ticket_by_id(TICKET_ID)
    print(f"NEW Citizen Name: {updated_ticket.get('citizen_name')}")
    print(f"NEW Category: {updated_ticket.get('category')}")
    print("SUCCESS: Ticket patched to appear as Internal DAF request.")

except Exception as e:
    print(f"FAILED to update ticket: {e}")
