from modules.ui import UNIDADES
from modules.db import init_supabase
import random
from datetime import datetime, timedelta
import faker

fake = faker.Faker('es_CL')

def seed_headless():
    print("Iniciando inyección de datos headless...")
    client = init_supabase()
    
    status_opts = ['Pendiente', 'Pendiente', 'En Proceso', 'En Proceso', 'Resuelto', 'Resuelto', 'Rechazado']
    urgency_opts = ['Baja', 'Media', 'Media', 'Alta', 'Crítica']
    unidades_keys = list(UNIDADES.keys())
    
    success_count = 0
    for i in range(50):
        dept = random.choice(unidades_keys)
        desc = fake.sentence(nb_words=12)
        created_at = fake.date_time_between(start_date='-30d', end_date='now')
        
        ticket = {
            "user_email": fake.email(),
            "category": UNIDADES[dept]['group'], 
            "sub": fake.bs(), 
            "description": desc,
            "status": random.choice(status_opts),
            "urgency": random.choice(urgency_opts),
            "depto": dept,
            "created_at": created_at.isoformat(),
            "ticket_number": random.randint(10000, 99999) 
        }
        
        try:
            client.table("tickets").insert(ticket).execute()
            success_count += 1
        except Exception as e:
            print(f"Error en inserción {i}: {e}")
            
    print(f"Finalizado. {success_count} tickets creados exitosamente.")

if __name__ == "__main__":
    # Mocking streamlit secrets access by ensuring toml is loaded if needed, 
    # but init_supabase uses st.secrets. 
    # To run this headless, we might need to patch st.secrets or run via streamlit run BUT
    # since we want to avoid opening browser, running via `streamlit run` with headless config is best.
    seed_headless()
