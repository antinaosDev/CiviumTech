import streamlit as st
from modules.ui import PATH_LOGO_MUNI, UNIDADES
from modules.auth import logout_user, get_real_role

# Logic to map Roles to accessible Modules/Filters
ROLE_PERMISSIONS = {
    'Programador': ['overview', 'tickets', 'assets', 'admin_users', 'simulation'],
    'Administrador': ['overview', 'tickets', 'assets'],
    'DIDECO': ['tickets'], # Filtered by DIDECO
    'SECPLAN': ['tickets'], # Filtered
    'DOM': ['tickets', 'assets'],
    'DAF': ['assets'],
    'CITIZEN': ['citizen']
}

def render_custom_sidebar(current_role):
    with st.sidebar:
        st.image(PATH_LOGO_MUNI, width=100)
        
        # User Info
        if st.session_state.get('authenticated'):
            st.markdown(f"**Hola, {st.session_state.get('full_name', 'Vecino')}**")
            
            # Simulation Banner
            real_role = get_real_role()
            if 'simulated_role' in st.session_state:
                 st.warning(f"👁️ Simulando: {current_role}")
                 if st.button("⏹️ Dejar de Simular"):
                     del st.session_state['simulated_role']
                     st.rerun()
            else:
                st.caption(f"Rol: {current_role}")
            
            st.divider()

        # Navigation Logic
        selected_view = 'overview' # Default
        
        if current_role == 'CITIZEN':
            return 'citizen'
            
        # Global Nav
        if st.button("🏠 Inicio / Dashboard", use_container_width=True):
            st.session_state['view_mode'] = 'overview'
            st.session_state['filter'] = 'Todos'
            
        st.markdown("### Módulos")
        
        # Municipal Management Menu (Dynamic)
        if current_role in ['Programador', 'Administrador'] or current_role not in ['DAF']:
            from modules.ui import GROUPS_ORDER
            
            st.markdown("### Departamentos")
            
            # 1. Global View Option
            if st.button("🌐 Vista Global", key="nav_global"):
                st.session_state['view_mode'] = 'overview'
                st.session_state['filter'] = 'Todos'

            # 2. Iterate Groups
            # Filter groups by Role
            visible_groups = GROUPS_ORDER
            
            # --- MAPPING ROLES TO GROUPS ---
            # Direccion Superior
            if current_role in ['ALCALDIA', 'CONCEJO', 'ADMIN_MUNICIPAL', 'JPL', 'COSOC', 'INFORMATICA', 'JURIDICO', 'CONTROL']:
                visible_groups = ['Dirección Superior']
            # Gestion Interna
            elif current_role in ['SECRETARIA', 'OF_PARTES', 'SECPLAN', 'PRENSA', 'TRANSPARENCIA']:
                 visible_groups = ['Gestión Interna']
            # Desarrollo Social
            elif current_role in ['DIDECO', 'DIDECO_DIR', 'SENDA', 'MEDIO_AMBIENTE']:
                 visible_groups = ['Desarrollo Social']
            # Territorio y Obras
            elif current_role in ['DOM', 'DOM_DIR', 'DOM_TRANSITO']:
                 visible_groups = ['Territorio y Obras']
            # Administracion
            elif current_role in ['DAF', 'DAF_DIR', 'ADQUISICIONES', 'ACTIVOS']:
                 visible_groups = ['Administración']
            # Fomento
            elif current_role in ['UDEL', 'PRODESAL', 'PDTI']:
                 visible_groups = ['Fomento Productivo']
            # Servicios
            elif current_role in ['SALUD', 'EDUCACION', 'DEPORTES', 'CULTURA', 'SEGURIDAD']:
                 visible_groups = ['Servicios a la Comunidad']
                
            for group_name in visible_groups:
                # Find units in this group
                group_units = {k: v for k, v in UNIDADES.items() if v.get('group') == group_name}
                
                if group_units:
                    # Decide icon based on group header (Static mapping for visual flair)
                    g_icon = "folder"
                    if "Social" in group_name: g_icon = "favorite"
                    elif "Obras" in group_name: g_icon = "engineering"
                    elif "Admin" in group_name: g_icon = "business"
                    
                    with st.expander(f"{group_name}", expanded=False):
                        for u_code, u_data in group_units.items():
                            label = u_data.get('label', u_code)
                            icon = u_data.get('icon', 'circle')
                            
                            # Button for each unit
                            # Using markdown + button trick or just simple buttons with indentation
                            if st.button(f"{label}", key=f"nav_{u_code}", help=f"Ir a {label}"):
                                st.session_state['view_mode'] = 'tickets' # Or overview customized
                                st.session_state['filter'] = u_code
                                st.rerun()

        # Content Manager (Admin & Programador)
        if current_role in ['Programador', 'Administrador'] and 'simulated_role' not in st.session_state:
             st.divider()
             if st.button("⚙️ Gestor de Contenidos", use_container_width=True):
                 st.session_state['view_mode'] = 'content_manager'

        # Admin Menu (Programador Only - Hidden during simulation)
        if get_real_role() == 'Programador' and 'simulated_role' not in st.session_state:
            st.divider()
            with st.expander("🛠️ Super Admin", expanded=False):
                if st.button("👥 Usuarios y Roles"):
                    st.session_state['view_mode'] = 'admin_users'
                
                if st.button("📝 Base de Conocimiento", help="Wiki Interna"):
                    st.session_state['view_mode'] = 'wiki' # Placeholder if needed, or remove.
                
                # Simulation Controls
                st.markdown("Simular Rol:")
                
                roles_list = [
                    "Administrador", 
                    "ALCALDIA", "CONCEJO", "ADMIN_MUNICIPAL", "JPL", "COSOC", "INFORMATICA", "JURIDICO", "CONTROL", 
                    "SECRETARIA", "OF_PARTES", "SECPLAN", "PRENSA",
                    "DIDECO", "SENDA", "MEDIO_AMBIENTE",
                    "DOM", "DOM_TRANSITO",
                    "DAF", "ADQUISICIONES",
                    "UDEL", "PRODESAL", "PDTI",
                    "SALUD", "EDUCACION", "DEPORTES", "CULTURA", "SEGURIDAD",
                    "CITIZEN"
                ]
                
                sim_target = st.selectbox("Rol Destino", roles_list, key="sim_select")
                if st.button("▶️ Simular"):
                    st.session_state['simulated_role'] = sim_target
                    st.rerun()

        st.divider()
        st.caption("Sesión Segura")
        if st.button("🔒 Cerrar Sesión", type="primary", use_container_width=True):
            logout_user()
            
    return st.session_state.get('view_mode', 'overview')
