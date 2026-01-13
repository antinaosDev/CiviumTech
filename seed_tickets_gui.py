import streamlit as st
from modules.db import init_supabase
from modules.ui import UNIDADES
import random
from datetime import datetime, timedelta
import faker

# Initialize Faker
fake = faker.Faker('es_CL')

def seed_data():
    st.title("🌱 Generador de Datos Ficticios")
    
    if st.button("Generar 50 Tickets de Prueba"):
        client = init_supabase()
        
        tickets = []
        unidades_keys = list(UNIDADES.keys())
        status_opts = ['Pendiente', 'Pendiente', 'En Proceso', 'En Proceso', 'Resuelto', 'Resuelto', 'Rechazado']
        urgency_opts = ['Baja', 'Media', 'Media', 'Alta', 'Crítica']
        
        progress = st.progress(0)
        
        for i in range(50):
            dept = random.choice(unidades_keys)
            # Create meaningful description based on dept
            desc = fake.sentence(nb_words=10)
            
            created_at = fake.date_time_between(start_date='-30d', end_date='now')
            
            ticket = {
                "user_email": fake.email(),
                "category": UNIDADES[dept]['group'], # Use group as category proxy
                "sub": fake.bs(), # Subject/Sub-category
                "description": desc,
                "status": random.choice(status_opts),
                "urgency": random.choice(urgency_opts),
                "depto": dept,
                "created_at": created_at.isoformat(),
                "ticket_number": random.randint(1000, 9999) # Serial is auto, but just in case we need a number field
            }
            
            try:
                # Remove fields that might not exist or let DB handle defaults
                # We need to ensure 'depto' exists in DB first!
                client.table("tickets").insert(ticket).execute()
            except Exception as e:
                st.error(f"Error insertando ticket {i}: {e}")
                
            progress.progress((i + 1) / 50)
            
        st.success("¡Datos generados exitosamente!")
        st.info("Recuerda: Debes haber corrido el script 'fix_schema_depto.sql' en Supabase primero para que el campo 'depto' exista.")

if __name__ == "__main__":
    # Minimal setup to run this as a standalone streamlit page or module
    st.set_page_config(page_title="Seeder")
    seed_data()
