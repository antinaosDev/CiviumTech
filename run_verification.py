import toml
import os
from supabase import create_client
import sys

# Load secrets manually
SECRETS_PATH = r"D:\PROYECTOS PROGRAMACIÓN\ANTIGRAVITY_PROJECTS\gobtech\.streamlit\secrets.toml"

print(f"Loading secrets from {SECRETS_PATH}...")
try:
    secrets = toml.load(SECRETS_PATH)
    if "global" in secrets:
        url = secrets["global"]["SUPABASE_URL"]
        key = secrets["global"]["SUPABASE_KEY"]
    else:
        url = secrets["SUPABASE_URL"]
        key = secrets["SUPABASE_KEY"]
except Exception as e:
    print(f"ERROR: Could not load secrets.toml. {e}")
    sys.exit(1)

print(f"Connecting to Supabase at {url[:20]}...")
try:
    client = create_client(url, key)
except Exception as e:
    print(f"ERROR: Client init failed. {e}")
    sys.exit(1)

# Test 1: Read Departments
print("\n[TEST 1] Read 'departments' table...")
try:
    res = client.table("departments").select("*").limit(3).execute()
    print(f"SUCCESS: Found {len(res.data)} departments.")
    if len(res.data) == 0:
        print("WARNING: Table is empty. Did you run the Seed Data?")
except Exception as e:
    print(f"FAIL: {e}")

# Test 2: Check Tickets Structure
print("\n[TEST 2] Check 'tickets' table schema (by selecting 'depto')...")
try:
    # Try selecting the new column 'depto'
    res = client.table("tickets").select("id, ticket_number, depto").limit(1).execute()
    print("SUCCESS: 'depto' column exists.")
except Exception as e:
    print(f"FAIL: {e}")
    print("ACTION: You must run the SQL to add the 'depto' column.")

# Test 3: Write Test (Ticket)
print("\n[TEST 3] Write Permissions (Insert Dummy Ticket)...")
dummy_ticket = {
    "user_email": "test_script@civium.tech",
    "category": "TEST_SCRIPT",
    "description": "Auto-generated test ticket",
    "status": "Pendiente",
    "urgency": "Baja",
    "depto": "TEST"
}
ticket_id = None
try:
    res = client.table("tickets").insert(dummy_ticket).execute()
    if res.data:
        ticket_id = res.data[0]['id']
        print(f"SUCCESS: Created ticket {ticket_id}")
    else:
        print("FAIL: No data returned from insert.")
except Exception as e:
    print(f"FAIL: {e}")

# Test 4: Delete Test
if ticket_id:
    print("\n[TEST 4] Delete Test Ticket...")
    try:
        client.table("tickets").delete().eq("id", ticket_id).execute()
        print("SUCCESS: Deleted test ticket.")
    except Exception as e:
        print(f"FAIL: Could not delete ticket. {e}")

