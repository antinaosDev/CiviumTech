import streamlit as st
import pandas as pd
from modules.ui import (
    UNIDADES, 
    render_status_badge, 
    render_urgency_badge
)

def render_ticket_list(tickets, filter_category, search_query):
    """
    Renderiza la lista de tickets/solicitudes estilo CiviumTech con interactividad.
    """
    # 1. Title & Header
    col_header, col_search = st.columns([3, 1])
    
    with col_header:
        label_unidad = UNIDADES.get(filter_category, {}).get('label', filter_category) if filter_category != 'Todos' else 'Vista Global'
        st.markdown(f"### 📥 Bandeja de Entrada")
        st.markdown(f"<div style='color: #64748b; margin-top: -10px; font-size: 0.9rem;'>Unidad: <strong>{label_unidad}</strong></div>", unsafe_allow_html=True)

    # 1.5 CRUD Creation Form (Admin/Official)
    if filter_category != 'Todos':
        with st.expander(f"➕ Ingresar Solicitud para {label_unidad}", expanded=False):
            with st.form("admin_create_ticket"):
                c1, c2 = st.columns(2)
                new_desc = c1.text_input("Descripción", placeholder="Resumen del requerimiento")
                new_cat = c2.selectbox("Categoría", ["Operativo / Terreno", "Social / Beneficios", "Administrativo", "Salud", "Educación", "Seguridad"])
                
                c3, c4 = st.columns(2)
                new_citizen = c3.text_input("Ciudadano / Solicitante", placeholder="Nombre o Junta de Vecinos")
                new_prio = c4.selectbox("Prioridad", ["Baja", "Media", "Alta", "Crítica"])
                
                submitted = st.form_submit_button("Crear Solicitud")
                if submitted:
                    if not new_desc:
                        st.error("Descripción requerida.")
                    else:
                        from modules.db import create_ticket
                        from datetime import date
                        import random
                        
                        # Prepare Payload
                        payload = {
                            "description": new_desc, # Fixed
                            "category": new_cat, # Fixed
                            "citizen_name": new_citizen or "Anónimo", # Fixed
                            "urgency": new_prio,
                            "status": "Pendiente", # Fixed
                            "depto": filter_category, 
                            # 'fecha': date.today() # DB uses created_at.
                            "user_email": "admin@municipalidad.cl", 
                            "subject": new_cat # Fallback
                        }
                        res = create_ticket(payload)
                        if res:
                            st.success("Ticket creado exitosamente.")
                            st.rerun()

    # from modules.db import get_mock_tickets # REMOVED: Unused and causes ImportError
    if not isinstance(tickets, pd.DataFrame):
        df = pd.DataFrame(tickets)
    else:
        df = tickets.copy()

    if df.empty:
        st.info("No hay tickets disponibles.")
        return

    # Filter by Dept (Global Filter)
    if filter_category != 'Todos':
        df = df[df['depto'] == filter_category]

    # --- ADVANCED CONTROLS ---
    with st.container(border=True):
        c_search, c_filt1, c_filt2 = st.columns([2, 1, 1])
        
        with c_search:
            # Internal search state if needed, or just text_input
            q_search = st.text_input("🔍 Buscar", placeholder="Nombre, RUT, ID o Asunto...", label_visibility="collapsed")
        
        with c_filt1:
            filtro_estado = st.multiselect("Estado", options=["Pendiente", "En Proceso", "En Revisión", "Resuelto", "Rechazado"], placeholder="Filtrar Estado", label_visibility="collapsed")
            
        with c_filt2:
            filtro_urgencia = st.multiselect("Urgencia", options=["Baja", "Media", "Alta", "Crítica"], placeholder="Filtrar Urgencia", label_visibility="collapsed")

    # Apply Filters
    if q_search:
        q = q_search.lower()
        df = df[
            df['id'].astype(str).str.lower().str.contains(q) |
            df['description'].str.lower().str.contains(q) |
            df['citizen_name'].str.lower().str.contains(q) |
            df['subject'].str.lower().str.contains(q)
        ]
        
    if filtro_estado:
        df = df[df['status'].isin(filtro_estado)]
        
    if filtro_urgencia:
        df = df[df['urgency'].isin(filtro_urgencia)]

    # Export Button
    col_count, col_export = st.columns([4, 1])
    with col_count:
        st.caption(f"Mostrando {len(df)} resultados")
    with col_export:
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            "📥 Exportar CSV",
            data=csv,
            file_name=f"reporte_tickets_{filter_category}.csv",
            mime="text/csv",
            key=f"btn_download_csv_{filter_category}"
        )
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Custom CSS for the grid layout consistency
    # Custom CSS for Cards
    st.markdown("""
    <style>
    .ticket-card {
        background-color: white;
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.05);
        transition: all 0.2s ease-in-out;
    }
    .ticket-card:hover {
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        border-color: #cbd5e1;
    }
    .ticket-id {
        font-family: 'Courier New', monospace;
        font-weight: 700;
        font-size: 0.75rem;
        color: #64748b;
        background: #f1f5f9;
        padding: 2px 6px;
        border-radius: 4px;
    }
    .ticket-title {
        color: #1e293b;
        font-weight: 700;
        font-size: 1rem;
        margin: 0.25rem 0;
    }
    .ticket-desc {
        color: #475569;
        font-size: 0.875rem;
        line-height: 1.4;
        margin-bottom: 0.75rem;
    }
    .ticket-meta {
        display: flex;
        gap: 1rem;
        align-items: center;
        font-size: 0.75rem;
        color: #94a3b8;
    }
    </style>
    """, unsafe_allow_html=True)

    # Removed Table Header
    st.markdown("<div style='margin-bottom: 1rem;'></div>", unsafe_allow_html=True)

    # 4. Render Rows
    if df.empty:
        st.warning("No se encontraron resultados.")
        return

    for _, row in df.iterrows():
        # Data Prep
        t_id = row.get('id', '???')
        # Use created_at and format it
        t_date_raw = row.get('created_at', str(pd.Timestamp.now()))
        t_date = str(t_date_raw).split("T")[0] if t_date_raw else "???"
        
        t_citizen = row.get('citizen_name', 'Anónimo')
        t_desc = row.get('description', 'Sin descripción')
        t_depto_code = row.get('depto', '???')
        t_status = row.get('status', 'Pendiente')
        t_urgency = row.get('urgency', 'Baja')
        t_sub = row.get('subject', '')
        
        # Unit Info
        unit_info = UNIDADES.get(t_depto_code, {})
        unit_label = unit_info.get('label', t_depto_code)
        unit_icon = unit_info.get('icon', 'folder')
        unit_bg = unit_info.get('hex_bg', '#f1f5f9')

        # Card Layout
        with st.container():
            c_card, c_btn = st.columns([5, 1])
            
            with c_card:

                card_html = f"""
                <div class="ticket-card">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                        <div style="display: flex; gap: 0.5rem; align-items: center;">
                            <span class="ticket-id">{t_id}</span>
                            <span style="font-size: 0.75rem; color: #94a3b8;">📅 {t_date}</span>
                        </div>
                        <div style="display: flex; align-items: center; gap: 0.5rem;">
                            <span class="material-icons-round" style="font-size: 14px; color: {unit_bg.replace('40','').replace('#','')}">{unit_icon}</span> 
                            <span style="font-size: 0.75rem; font-weight: 600; color: #475569;">{unit_label}</span>
                        </div>
                    </div>
                    <div class="ticket-title">{t_sub if t_sub else 'Sin Asunto'}</div>
                    <div class="ticket-desc">{t_desc[:120]}...</div>
                    <div class="ticket-meta">
                        <div style="display: flex; gap: 0.5rem; align-items: center;">
                            {render_status_badge(t_status)}
                            {render_urgency_badge(t_urgency)}
                        </div>
                        <div style="margin-left: auto; display: flex; align-items: center; gap: 4px;">
                            <span class="material-icons-round" style="font-size: 14px;">person</span> {t_citizen}
                        </div>
                    </div>
                </div>
                """
                st.markdown(card_html, unsafe_allow_html=True)

            with c_btn:
                # Vertically center the button
                st.markdown("<div style='height: 25px'></div>", unsafe_allow_html=True)
                def set_ticket(tid):
                    st.session_state.selected_ticket_id = tid
                    
                st.button(
                    "Gestionar", 
                    key=f"btn_{t_id}", 
                    on_click=set_ticket,
                    args=(t_id,),
                    use_container_width=True,
                    type="primary"
                )
