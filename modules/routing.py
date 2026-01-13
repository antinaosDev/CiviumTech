from modules.db import get_supabase

def get_department_by_code(code: str):
    """Fetch department ID by its unique code."""
    supabase = get_supabase()
    response = supabase.table("departments").select("id").eq("code", code).single().execute()
    if response.data:
        return response.data["id"]
    return None

def get_cholchol_categories():
    """
    Returns the categories structure adapted for rural citizens.
    """
    return {
        "Mundo Rural / Agro": ["Apoyo Siembra", "Animales", "Cercos", "Riego"],
        "Medio Ambiente": ["Denuncia Ambiental", "Registro Apicultores", "Basura/Microbasurales"],
        "Caminos y Obras": ["Arreglo Camino", "Luminarias", "Puentes"],
        "Ayuda Social": ["Canastas/Alimentos", "Materiales Construcción", "Rebaja Aseo", "Exenciones"],
        "Patentes y Comercio": ["Patente Comercial", "Permiso Ambulante", "Kiosco", "CIPA"],
        "Participación": ["Junta de Vecinos", "FONDEVE", "Audiencia Alcalde"]
    }

def route_ticket(category: str, subcategory: str) -> str:
    """
    Determines the assigned department ID based on strict Cholchol rules.
    """
    dept_code = None

    # A. MUNDO RURAL / AGRO -> UDEL (Prodesal/PDTI)
    if category == "Mundo Rural / Agro":
        dept_code = "UDEL_AGRO"

    # B. MEDIO AMBIENTE
    elif category == "Medio Ambiente":
        dept_code = "UDEL_AMBIENTE"
    
    # C. CAMINOS (DOM)
    elif category == "Caminos y Obras":
        dept_code = "DOM_OPS" 

    # D. AYUDA SOCIAL -> DIDECO
    elif category == "Ayuda Social":
        dept_code = "DIDECO_SOCIAL"

    # E. PATENTES -> DAF (Rentas)
    elif category == "Patentes y Comercio":
        dept_code = "DAF_RENTAS"

    # F. PARTICIPACION -> SECMU
    elif category == "Participación":
        dept_code = "SECMU_PARTICIPACION"

    # Default fallback logic
    if not dept_code:
        # Try to map broad categories if specific logic fails
        broad_map = {
            "Mundo Rural / Agro": "UDEL",
            "Medio Ambiente": "UDEL_AMBIENTE", 
            "Ayuda Social": "DIDECO",
            "Caminos y Obras": "DOM",
            "Patentes y Comercio": "DAF"
        }
        dept_code = broad_map.get(category, "ALC_ADMIN") # Fallback to Admin

    return get_department_by_code(dept_code)
