import pandas as pd
from modules.db import get_supabase
from datetime import datetime

# --- LÓGICA DE DERIVACIÓN AUTOMÁTICA (MOTOR DE ASIGNACIÓN V5) ---
# Mapea "Categoría" Seleccionada -> "Nombre Sub-Unidad" (Debe coincidir con DB)

DERIVATION_RULES = {
    # UDEL
    'Rural': {'unit': 'PDTI', 'sla': 48, 'dept': 'UDEL'},
    'Agricola': {'unit': 'Prodesal', 'sla': 48, 'dept': 'UDEL'},
    'Ambiente': {'unit': 'Medio Ambiente', 'sla': 24, 'dept': 'UDEL'},
    'Turismo': {'unit': 'Turismo', 'sla': 72, 'dept': 'UDEL'},
    
    # DIDECO
    'Social': {'unit': 'Social', 'sla': 24, 'dept': 'DIDECO'},
    'Vivienda': {'unit': 'Vivienda', 'sla': 96, 'dept': 'DIDECO'},
    'Laboral': {'unit': 'OMIL', 'sla': 48, 'dept': 'DIDECO'},
    'Seguridad': {'unit': 'Seguridad Pública', 'sla': 2, 'dept': 'DIDECO'},
    
    # DOM
    'Caminos': {'unit': 'Caminos / Operaciones', 'sla': 72, 'dept': 'DOM'},
    'Alumbrado': {'unit': 'Alumbrado', 'sla': 48, 'dept': 'DOM'},
    'Obras': {'unit': 'Caminos / Operaciones', 'sla': 72, 'dept': 'DOM'},
    
    # DAF
    'Patentes': {'unit': 'Rentas y Patentes', 'sla': 120, 'dept': 'DAF'},
    
    # SALUD
    'Salud': {'unit': 'Farmacia / Posta', 'sla': 24, 'dept': 'Salud'},
    
    # JUSTICIA
    'Juzgado': {'unit': 'Juzgado Policía Local', 'sla': 144, 'dept': 'Justicia'},
}

def get_derivation_info(category_value):
    """
    Retorna la info de derivación automática dado un valor de categoría.
    Si no encuentra la categoría, retorna 'Oficina de Partes' (Fallback).
    """
    return DERIVATION_RULES.get(category_value, {'unit': 'Alcaldía', 'sla': 48, 'dept': 'Alcaldía'})

def calculate_urgency(text, category):
    """
    Algoritmo simple NLP (Simulado) para detectar urgencia.
    """
    if not text: return 'Media'
    
    text_lower = text.lower()
    keywords_high = ['grave', 'urgente', 'peligro', 'riesgo', 'muerte', 'incendio', 'robo']
    
    if any(k in text_lower for k in keywords_high):
        return 'Alta'
    
    # Categorías críticas por defecto
    if category in ['Seguridad', 'Salud']:
        return 'Alta'
        
    return 'Media'
    
def auto_assign_ticket(category, description):
    """
    Función Principal: Toma los datos crudos y devuelve la metada de asignación completa.
    """
    derivation = get_derivation_info(category)
    urgency = calculate_urgency(description, category)
    
    return {
        'assigned_dept': derivation['dept'],
        'assigned_unit': derivation['unit'],
        'sla_hours': derivation['sla'],
        'ai_urgency': urgency
    }

def append_log(ticket_id: str, action: str, user_email: str, observation: str = ""):
    """
    Appends a new entry to the ticket's history log.
    """
    supabase = get_supabase()
    
    entry = {
        "timestamp": datetime.now().isoformat(),
        "action": action,
        "user": user_email,
        "observation": observation
    }
    
    try:
        resp = supabase.table("tickets").select("log").eq("id", ticket_id).single().execute()
        current_log = resp.data.get("log") or []
        current_log.append(entry)
        supabase.table("tickets").update({"log": current_log}).eq("id", ticket_id).execute()
    except Exception as e:
        print(f"Error appending log: {e}")
