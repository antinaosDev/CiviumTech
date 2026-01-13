
import streamlit as st
import base64
import os

# --- BRANDING ---
PATH_LOGO_APP = "CiviumTech_web.png"
PATH_LOGO_MUNI = "logo_muni_web.png"
PATH_LOGO_DEV = "logo_alain.png"

@st.cache_data
def get_img_as_base64(file_path):
    """Reads an image file and returns a base64 string."""
    try:
        with open(file_path, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except Exception:
        return ""

# COLORS - SINTIA DESIGN SYSTEM
COLOR_PRIMARY = "#2563eb"    # Blue 600
APP_NAME = "CiviumTech"
MUNICIPALITY_NAME = "I. Municipalidad de Cholchol"

# UNIDADES (Match React Spec) - Python version
# Mapping 'icon' to Material Icons names where possible
UNIDADES = {
  # DIRECCIÓN SUPERIOR
  'ALCALDIA': {'label': 'Alcalde', 'group': 'Dirección Superior', 'color': 'bg-slate-900 text-white', 'icon': 'crown', 'hex_bg': '#0f172a', 'hex_text': '#ffffff'},
  'CONCEJO': {'label': 'Concejo Municipal', 'group': 'Dirección Superior', 'color': 'bg-slate-700 text-white', 'icon': 'groups', 'hex_bg': '#334155', 'hex_text': '#ffffff'},
  'ADMIN_MUNICIPAL': {'label': 'Administración Municipal', 'group': 'Dirección Superior', 'color': 'bg-slate-800 text-slate-200', 'icon': 'business', 'hex_bg': '#1e293b', 'hex_text': '#e2e8f0'},
  'JPL': {'label': 'Juzgado Policía Local', 'group': 'Dirección Superior', 'color': 'bg-stone-200 text-stone-800', 'icon': 'balance', 'hex_bg': '#e7e5e4', 'hex_text': '#292524'},
  'COSOC': {'label': 'COSOC', 'group': 'Dirección Superior', 'color': 'bg-stone-100 text-stone-600', 'icon': 'diversity_3', 'hex_bg': '#f5f5f4', 'hex_text': '#57534e'},
  'INFORMATICA': {'label': 'Informática', 'group': 'Dirección Superior', 'color': 'bg-cyan-900 text-cyan-100', 'icon': 'computer', 'hex_bg': '#164e63', 'hex_text': '#cffafe'},
  'JURIDICO': {'label': 'Asesoría Jurídica', 'group': 'Dirección Superior', 'color': 'bg-stone-300 text-stone-900', 'icon': 'gavel', 'hex_bg': '#d6d3d1', 'hex_text': '#1c1917'},
  'CONTROL': {'label': 'Control', 'group': 'Dirección Superior', 'color': 'bg-red-900 text-white', 'icon': 'fact_check', 'hex_bg': '#7f1d1d', 'hex_text': '#ffffff'},

  # DIDECO (SOCIAL)
  'DIDECO_DIR': {'label': 'Dir. DIDECO', 'group': 'Desarrollo Social', 'color': 'bg-pink-600 text-white', 'icon': 'favorite', 'hex_bg': '#db2777', 'hex_text': '#ffffff'},
  'SOCIAL_AYUDA': {'label': 'Ayuda Social', 'group': 'Desarrollo Social', 'color': 'bg-pink-100 text-pink-800', 'icon': 'volunteer_activism', 'hex_bg': '#fce7f3', 'hex_text': '#9d174d'},
  'SOCIAL_ADULTO': {'label': 'Adulto Mayor', 'group': 'Desarrollo Social', 'color': 'bg-pink-200 text-pink-900', 'icon': 'elderly', 'hex_bg': '#fbcfe8', 'hex_text': '#831843'},
  'SOCIAL_VIVIENDA': {'label': 'Vivienda', 'group': 'Desarrollo Social', 'color': 'bg-rose-100 text-rose-800', 'icon': 'home', 'hex_bg': '#ffe4e6', 'hex_text': '#9f1239'},
  'SOCIAL_AUTOCONSUMO': {'label': 'Autoconsumo', 'group': 'Desarrollo Social', 'color': 'bg-orange-100 text-orange-800', 'icon': 'spa', 'hex_bg': '#ffedd5', 'hex_text': '#9a3412'},
  'SOCIAL_VINCULOS': {'label': 'Vínculos', 'group': 'Desarrollo Social', 'color': 'bg-pink-300 text-pink-900', 'icon': 'handshake', 'hex_bg': '#f9a8d4', 'hex_text': '#831843'},
  'SOCIAL_PUENTE': {'label': 'Programa Puente', 'group': 'Desarrollo Social', 'color': 'bg-indigo-100 text-indigo-800', 'icon': 'layers', 'hex_bg': '#e0e7ff', 'hex_text': '#3730a3'},
  'SOCIAL_INFANCIA': {'label': 'Infancia / OLN', 'group': 'Desarrollo Social', 'color': 'bg-sky-100 text-sky-800', 'icon': 'child_care', 'hex_bg': '#e0f2fe', 'hex_text': '#075985'},
  'SOCIAL_MUJER': {'label': 'Programa Mujer', 'group': 'Desarrollo Social', 'color': 'bg-fuchsia-100 text-fuchsia-800', 'icon': 'woman', 'hex_bg': '#fae8ff', 'hex_text': '#86198f'},
  'SENDA': {'label': 'SENDA Previene', 'group': 'Desarrollo Social', 'color': 'bg-green-100 text-green-800', 'icon': 'shield', 'hex_bg': '#dcfce7', 'hex_text': '#166534'},
  'MEDIO_AMBIENTE': {'label': 'Medio Ambiente', 'group': 'Desarrollo Social', 'color': 'bg-teal-100 text-teal-800', 'icon': 'recycling', 'hex_bg': '#ccfbf1', 'hex_text': '#115e59'},

  # DOM Y OPERACIONES
  'DOM_DIR': {'label': 'Dir. Obras (DOM)', 'group': 'Territorio y Obras', 'color': 'bg-orange-600 text-white', 'icon': 'engineering', 'hex_bg': '#ea580c', 'hex_text': '#ffffff'},
  'DOM_TRANSITO': {'label': 'Tránsito', 'group': 'Territorio y Obras', 'color': 'bg-yellow-100 text-yellow-800', 'icon': 'local_shipping', 'hex_bg': '#fef9c3', 'hex_text': '#854d0e'},

  # DAF
  'DAF_DIR': {'label': 'Dir. Admin y Finanzas', 'group': 'Administración', 'color': 'bg-purple-600 text-white', 'icon': 'calculate', 'hex_bg': '#9333ea', 'hex_text': '#ffffff'},
  'DAF_FINANZAS': {'label': 'Finanzas', 'group': 'Administración', 'color': 'bg-purple-100 text-purple-800', 'icon': 'bar_chart', 'hex_bg': '#f3e8ff', 'hex_text': '#6b21a8'},
  'DAF_RENTAS': {'label': 'Rentas y Patentes', 'group': 'Administración', 'color': 'bg-purple-200 text-purple-900', 'icon': 'store', 'hex_bg': '#e9d5ff', 'hex_text': '#581c87'},
  'ADQUISICIONES': {'label': 'Adquisiciones', 'group': 'Administración', 'color': 'bg-slate-200 text-slate-800', 'icon': 'shopping_cart', 'hex_bg': '#e2e8f0', 'hex_text': '#1e293b'},
  'ACTIVOS': {'label': 'Gestión de Activos', 'group': 'Administración', 'color': 'bg-teal-700 text-white', 'icon': 'inventory_2', 'hex_bg': '#0f766e', 'hex_text': '#ffffff'},

  # SECRETARÍA
  'SECRETARIA': {'label': 'Secretaría Municipal', 'group': 'Gestión Interna', 'color': 'bg-zinc-200 text-zinc-900', 'icon': 'description', 'hex_bg': '#e4e4e7', 'hex_text': '#18181b'},
  'OF_PARTES': {'label': 'Oficina de Partes', 'group': 'Gestión Interna', 'color': 'bg-zinc-100 text-zinc-800', 'icon': 'inventory', 'hex_bg': '#f4f4f5', 'hex_text': '#27272a'},
  'SECPLAN': {'label': 'SECPLAN', 'group': 'Gestión Interna', 'color': 'bg-blue-900 text-white', 'icon': 'track_changes', 'hex_bg': '#1e3a8a', 'hex_text': '#ffffff'},
  'SECPLAN_FOMENTO': {'label': 'Unidad de Fomento', 'group': 'Gestión Interna', 'color': 'bg-blue-100 text-blue-800', 'icon': 'trending_up', 'hex_bg': '#dbeafe', 'hex_text': '#1e40af'},
  'PRENSA': {'label': 'Prensa y Comunicaciones', 'group': 'Gestión Interna', 'color': 'bg-cyan-100 text-cyan-800', 'icon': 'radio', 'hex_bg': '#cffafe', 'hex_text': '#155e75'},
  'TRANSPARENCIA': {'label': 'Transparencia', 'group': 'Gestión Interna', 'color': 'bg-cyan-50 text-cyan-900', 'icon': 'search', 'hex_bg': '#f0f9ff', 'hex_text': '#0c4a6e'},

  # FOMENTO PRODUCTIVO
  'UDEL': {'label': 'UDEL (Emprendimiento)', 'group': 'Fomento Productivo', 'color': 'bg-amber-500 text-white', 'icon': 'work', 'hex_bg': '#f59e0b', 'hex_text': '#ffffff'},
  'PRODESAL': {'label': 'PRODESAL', 'group': 'Fomento Productivo', 'color': 'bg-amber-100 text-amber-800', 'icon': 'grass', 'hex_bg': '#fef3c7', 'hex_text': '#92400e'},
  'PDTI': {'label': 'PDTI (Territorial)', 'group': 'Fomento Productivo', 'color': 'bg-amber-200 text-amber-900', 'icon': 'forest', 'hex_bg': '#fde68a', 'hex_text': '#78350f'},
  'SERVICIO_PAIS': {'label': 'Servicio País', 'group': 'Fomento Productivo', 'color': 'bg-teal-100 text-teal-800', 'icon': 'map', 'hex_bg': '#ccfbf1', 'hex_text': '#115e59'},

  # SERVICIOS
  'SALUD': {'label': 'Salud Municipal', 'group': 'Servicios a la Comunidad', 'color': 'bg-teal-500 text-white', 'icon': 'local_hospital', 'hex_bg': '#14b8a6', 'hex_text': '#ffffff'},
  'EDUCACION': {'label': 'Educación (DAEM)', 'group': 'Servicios a la Comunidad', 'color': 'bg-sky-500 text-white', 'icon': 'school', 'hex_bg': '#0ea5e9', 'hex_text': '#ffffff'},
  'DEPORTES': {'label': 'Deportes', 'group': 'Servicios a la Comunidad', 'color': 'bg-lime-100 text-lime-800', 'icon': 'sports_soccer', 'hex_bg': '#ecfccb', 'hex_text': '#3f6212'},
  'CULTURA': {'label': 'Cultura', 'group': 'Servicios a la Comunidad', 'color': 'bg-violet-100 text-violet-800', 'icon': 'music_note', 'hex_bg': '#ede9fe', 'hex_text': '#5b21b6'},
  'SEGURIDAD': {'label': 'Seguridad Pública', 'group': 'Servicios a la Comunidad', 'color': 'bg-red-600 text-white', 'icon': 'security', 'hex_bg': '#dc2626', 'hex_text': '#ffffff'},
}

GROUPS_ORDER = ['Dirección Superior', 'Gestión Interna', 'Desarrollo Social', 'Territorio y Obras', 'Administración', 'Fomento Productivo', 'Servicios a la Comunidad']

def load_css(file_path="style.css"):
    """Loads CSS from a file and injects it into the app."""
    try:
        with open(file_path, "r") as f:
            css = f.read()
            st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.error(f"Error loading style: {file_path} not found.")

def apply_custom_styles():
    """Applies the premium theme from style.css."""
    load_css("style.css")

def render_status_badge(status):
    # Match colors from React: Pendiente (yellow), En Proceso (green/blue), etc.
    # React uses: Pendiente -> yellow-100/800, others check mock data
    if status == 'Pendiente':
        return f'<span class="badge" style="background-color: #fef9c3; color: #854d0e;">{status}</span>'
    elif status == 'En Proceso':
        return f'<span class="badge" style="background-color: #dbeafe; color: #1e40af;">{status}</span>'
    elif status == 'Resuelto':
        return f'<span class="badge" style="background-color: #dcfce7; color: #166534;">{status}</span>'
    elif status == 'Rechazado' or status == 'Crítica':
        return f'<span class="badge" style="background-color: #fee2e2; color: #991b1b;">{status}</span>'
    else:
        return f'<span class="badge" style="background-color: #f1f5f9; color: #475569;">{status}</span>'

def render_urgency_badge(urgency):
    if urgency in ['Alta', 'Crítica']:
        return f'<span style="color: #dc2626; font-weight: 700; font-size: 0.75rem; display: flex; align-items: center; gap: 4px;"><span class="material-icons-round" style="font-size: 14px;">local_fire_department</span> {urgency}</span>'
    return f'<span style="color: #64748b; font-size: 0.75rem;">{urgency}</span>'

def display_footer():
    st.markdown("---")
    with st.container():
        col1, col2, col3, col4 = st.columns([1,1,5,1]) # Adjusted cols to center better
        with col2:
            # LOGO PIE DE PÁGINA (Dinámico)
            try:
                st.image(PATH_LOGO_DEV, width=100)
            except:
                st.info("Logo Dev")
                
        with col3:
            st.markdown("""
                <div style='text-align: left; color: #888888; font-size: 14px; padding-bottom: 20px;'>
                    💼 Aplicación desarrollada por <strong>Alain Antinao Sepúlveda</strong> <br>
                    📧 Contacto: <a href="mailto:alain.antinao.s@gmail.com" style="color: #006DB6;">alain.antinao.s@gmail.com</a> <br>
                    🌐 Más información en: <a href="https://alain-antinao-s.notion.site/Alain-C-sar-Antinao-Sep-lveda-1d20a081d9a980ca9d43e283a278053e" target="_blank" style="color: #006DB6;">Mi página personal</a>
                </div>
            """, unsafe_allow_html=True)

# Events Mock (Shared)
EVENTS = [
  {'id': 1, 'tipo': 'Salud', 'titulo': 'Ronda Médica Rural', 'lugar': 'Sede Social Malalche', 'fecha': '2025-01-20', 'hora': '09:30', 'icon': 'medical_services'},
  {'id': 2, 'tipo': 'Veterinario', 'titulo': 'Operativo Sanitario (Ovinos)', 'lugar': 'Sector Repocura', 'fecha': '2025-01-22', 'hora': '10:00', 'icon': 'pets'},
  {'id': 3, 'tipo': 'Social', 'titulo': 'Atención en Terreno DIDECO', 'lugar': 'Posta Rucapangue', 'fecha': '2025-01-25', 'hora': '11:00', 'icon': 'favorite'},
  {'id': 4, 'tipo': 'Servicios', 'titulo': 'Camión Aljibe (Agua)', 'lugar': 'Ruta S-10 Km 15', 'fecha': '2025-01-21', 'hora': '08:00', 'icon': 'local_shipping'},
]

def render_field_ops_card_grid():
    st.subheader(f"Actividades Semanales")
    st.markdown('<div class="responsive-grid" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 1rem;">', unsafe_allow_html=True)
    
    color_map = { 'Salud': 'bg-teal-50 text-teal-700', 'Veterinario': 'bg-amber-50 text-amber-700', 'Social': 'bg-pink-50 text-pink-700', 'Servicios': 'bg-blue-50 text-blue-700' }

    for evt in EVENTS:
        style_class = color_map.get(evt['tipo'], 'bg-gray-50 text-gray-700')
        
        card_html = f"""
        <div style="background: white; border: 1px solid #e2e8f0; border-radius: 12px; padding: 1.5rem; display: flex; flex-direction: column; gap: 0.5rem;">
            <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.5rem;">
                <span class="material-icons-round" style="color: #64748b;">{evt['icon']}</span>
                <span style="font-size: 0.7rem; font-weight: 700; padding: 2px 8px; border-radius: 99px; background: #f1f5f9; color: #475569;">{evt['tipo']}</span>
            </div>
            <h4 style="margin: 0; font-size: 1rem; color: #1e293b;">{evt['titulo']}</h4>
            <div style="font-size: 0.8rem; color: #64748b; display: flex; align-items: center; gap: 4px;">
                <span class="material-icons-round" style="font-size: 14px;">event</span> {evt['fecha']} {evt['hora']}
            </div>
            <div style="font-size: 0.8rem; color: #64748b; display: flex; align-items: center; gap: 4px;">
                <span class="material-icons-round" style="font-size: 14px;">place</span> {evt['lugar']}
            </div>
        </div>
        """
        st.markdown(card_html, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)
