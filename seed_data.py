import os
import random
from datetime import datetime, timedelta
from modules.db import get_supabase
from modules.logic import auto_assign_ticket

# Initialize Supabase
supabase = get_supabase()

def get_authenticated_client():
    """Authenticate to ensure we can write to DB."""
    email = "admin_seed@cholchol.cl"
    password = "seedpassword123"
    
    print(f"Authenticating as {email}...")
    try:
        # Try login
        supabase.auth.sign_in_with_password({"email": email, "password": password})
        print("✅ Logged in successfully.")
    except Exception as e:
        print(f"⚠️ Login failed ({e}). Trying to Sign Up...")
        try:
            supabase.auth.sign_up({"email": email, "password": password})
            print("✅ Signed up successfully.")
            supabase.auth.sign_in_with_password({"email": email, "password": password})
        except Exception as e2:
            print(f"❌ Auth Error, proceeding anyway: {e2}")
    
    return supabase

USER_EMAILS = [
    "juan.perez@gmail.com", "maria.gonzalez@hotmail.com", 
    "pedro.torres@outlook.com", "vecino1@cholchol.cl"
]

CATEGORIES_MOCK = ["Rural", "Social", "Ambiente", "Caminos", "Salud", "Seguridad"]

DESCRIPTIONS = [
    "Camino cortado por caída de árbol.",
    "Solicito visita social urgente.",
    "Microbasural en la rivera del rio.",
    "Luminaria apagada frente a escuela.",
    "Control crónico en la Posta.",
    "Ruidos molestos en plazoleta.",
    "Apoyo PDTI para siembra.",
    "Puente en mal estado.",
    "Subsidio de agua potable.",
    "Perros vagos atacando ganado."
]

def generate_cholchol_coords():
    lat = -38.60 + (random.uniform(-0.03, 0.03))
    lon = -72.95 + (random.uniform(-0.03, 0.03))
    return lat, lon

def seed_v5_data():
    client = get_authenticated_client()
    print("🚀 Seeding Data into 'tickets' table...")
    
    # 1. Fetch Sub-Units Map (Optional)
    sub_unit_map = {}
    try:
        res = client.table("sub_units").select("id, name").execute()
        for item in res.data:
            sub_unit_map[item['name']] = item['id']
        print(f"Fetched {len(sub_unit_map)} sub-units for FK linking.")
    except:
        print("⚠️ Could not fetch sub_units (RLS?). Tickets will have sub_unit_id=NULL.")

    tickets_batch = []
    
    for _ in range(25): 
        cat = random.choice(CATEGORIES_MOCK)
        desc = random.choice(DESCRIPTIONS)
        email = random.choice(USER_EMAILS)
        
        # Logic Derivation
        assignment = auto_assign_ticket(cat, desc)
        target_unit_name = assignment['assigned_unit']
        target_unit_id = sub_unit_map.get(target_unit_name) # UUID or None
        
        days_ago = random.randint(0, 60)
        created_at = (datetime.now() - timedelta(days=days_ago)).isoformat()
        
        status = random.choice(['Pendiente']*5 + ['En Proceso']*3 + ['Resuelto']*2)
        lat, lon = generate_cholchol_coords()
        
        # VALID COLUMNS ONLY (No ticket_number, no depto)
        ticket = {
            "user_email": email,
            "category": cat,
            "description": desc,
            "status": status,
            "urgency": assignment['ai_urgency'],
            "sub_unit_id": target_unit_id, # Valid UUID or None
            "lat": lat,
            "lon": lon,
            "address_ref": f"Sector Demo {random.randint(1,99)}",
            "created_at": created_at
        }
        tickets_batch.append(ticket)
        
    try:
        client.table("tickets").insert(tickets_batch).execute()
        print("✅ Data Injected Successfully!")
    except Exception as e:
        print(f"❌ Error inserting: {e}")

if __name__ == "__main__":
    seed_v5_data()
