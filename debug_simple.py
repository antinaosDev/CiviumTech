from modules.db import fetch_tickets
import pandas as pd

try:
    tickets = fetch_tickets(limit=5)
    # Sort by created_at desc
    tickets.sort(key=lambda x: x.get('created_at', ''), reverse=True)
    
    if tickets:
        t = tickets[0]
        print(f"LAST_TICKET_SIGNATURE: {t.get('citizen_name')}")
    else:
        print("NO_TICKETS_FOUND")

except Exception as e:
    print(f"Error: {e}")
