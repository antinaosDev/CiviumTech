from modules.db import fetch_tickets
import pandas as pd

try:
    tickets = fetch_tickets(limit=10)
    # Sort by created_at desc
    tickets.sort(key=lambda x: x.get('created_at', ''), reverse=True)
    
    print("\n--- Last 5 Tickets Globally ---")
    for t in tickets[:5]:
        print(f"ID: {t.get('id')} | Subject: '{(t.get('subject') or t.get('title'))}' | Sign: '{t.get('citizen_name')}' | Created: {t.get('created_at')} | Category: {t.get('category')}")

except Exception as e:
    print(f"Error: {e}")
