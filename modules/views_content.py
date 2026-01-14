import streamlit as st
import pandas as pd
from datetime import datetime
from modules.db import (
    fetch_activities, create_activity, delete_activity, update_activity,
    fetch_config, update_config
)

def render_content_manager():
    st.title("Gestor de Contenidos")
    st.markdown("Administra la información visible en el Portal Vecino.")
    
    tab_activities, tab_info = st.tabs(["📅 Actividades Semanales", "ℹ️ Datos de Utilidad"])
    
    # --- TAB 1: ACTIVITIES ---
    with tab_activities:
        st.subheader("Actividades Programadas")
        
        # 1. Initialize Session State for Editing
        if 'edit_activity_id' not in st.session_state:
            st.session_state.edit_activity_id = None
            
        activities = fetch_activities()
        
        # 2. List & Actions
        if activities:
            # Create a more interactive list
            for act in activities:
                with st.expander(f"{act['date_str']} - {act['title']} ({act['type']})", expanded=False):
                    c1, c2 = st.columns([3, 1])
                    with c1:
                        st.markdown(f"**Lugar:** {act['location']}")
                        st.markdown(f"**Hora:** {act['time_str']}")
                        st.markdown(f"**ID:** {act['id']}")
                    with c2:
                        # Edit Button
                        if st.button("✏️ Editar", key=f"edit_{act['id']}"):
                            st.session_state.edit_activity_id = act['id']
                            st.rerun()
                        
                        # Delete Button
                        if st.button("🗑️ Eliminar", key=f"del_{act['id']}", type="primary"):
                            delete_activity(act['id'])
                            st.toast("Actividad eliminada.", icon="🗑️")
                            if st.session_state.edit_activity_id == act['id']:
                                st.session_state.edit_activity_id = None
                            import time
                            time.sleep(1.5)
                            st.rerun()
        else:
            st.info("No hay actividades registradas.")

        st.divider()

        # 3. Form (Create or Update)
        
        # Determine Mode
        is_edit_mode = st.session_state.edit_activity_id is not None
        form_title = "✏️ Editar Actividad" if is_edit_mode else "➕ Agregar Nueva Actividad"
        
        # Default Values
        default_title = ""
        default_type = "Salud"
        default_date = datetime.now()
        default_time = datetime.now().time()
        default_loc = ""
        
        # If Edit Mode, find the activity
        if is_edit_mode:
            target_act = next((a for a in activities if a['id'] == st.session_state.edit_activity_id), None)
            if target_act:
                default_title = target_act['title']
                default_type = target_act['type']
                try:
                    default_date = datetime.strptime(target_act['date_str'], "%Y-%m-%d").date()
                    default_time = datetime.strptime(target_act['time_str'], "%H:%M").time()
                except: pass
                default_loc = target_act['location']
                
                st.warning(f"Editando: {default_title}")
                if st.button("Cancelar Edición"):
                    st.session_state.edit_activity_id = None
                    st.rerun()
            else:
                # ID not found (deleted?)
                st.session_state.edit_activity_id = None
                st.rerun()

        st.subheader(form_title)
        
        with st.form("activity_form"):
            col1, col2 = st.columns(2)
            with col1:
                title = st.text_input("Título", value=default_title, placeholder="Ej. Operativo Veterinario")
                
                # Type Index handling
                type_options = ["Salud", "Veterinario", "Social", "Servicios"]
                try:
                    type_idx = type_options.index(default_type)
                except:
                    type_idx = 0
                    
                type_ = st.selectbox("Tipo", type_options, index=type_idx)
                
                icon_map = {"Salud": "medical_services", "Veterinario": "pets", "Social": "favorite", "Servicios": "local_shipping"}
                
            with col2:
                date_obj = st.date_input("Fecha", value=default_date)
                time_obj = st.time_input("Hora", value=default_time)
                location = st.text_input("Lugar", value=default_loc, placeholder="Ej. Sede Social Malalche")
                
            submit_label = "💾 Actualizar Actividad" if is_edit_mode else "🚀 Guardar Actividad"
            
            if st.form_submit_button(submit_label):
                if not title or not location:
                    st.error("Título y Lugar son obligatorios.")
                else:
                    new_data = {
                        "title": title,
                        "type": type_,
                        "date_str": date_obj.strftime("%Y-%m-%d"),
                        "time_str": time_obj.strftime("%H:%M"),
                        "location": location,
                        "icon": icon_map.get(type_, "event")
                    }
                    
                    if is_edit_mode:
                        update_activity(st.session_state.edit_activity_id, new_data)
                        st.toast("Actividad actualizada correctamente.", icon="✅")
                        st.session_state.edit_activity_id = None # Exit edit mode
                    else:
                        create_activity(new_data)
                        st.toast("Actividad creada correctamente.", icon="✅")
                    
                    import time
                    time.sleep(1.5)
                    st.rerun()

    # --- TAB 2: INFO DATA ---
    with tab_info:
        st.subheader("Datos de Utilidad (Portal Vecino)")
        st.caption("Edite el texto que aparece en la barra lateral del portal ciudadano.")
        
        # Fetch current values
        current_pharma = fetch_config("pharmacy_info")
        current_emergency = fetch_config("emergency_info")
        
        with st.form("info_form"):
            st.markdown("#### 💊 Farmacias de Turno")
            pharma_text = st.text_area("Texto Farmacia", value=current_pharma, height=150, help="Soporta Markdown simple (*cursiva*, **negrita**)")
            
            st.markdown("#### 🚑 Teléfonos de Emergencia")
            emergency_text = st.text_area("Texto Emergencias", value=current_emergency, height=150)
            
            if st.form_submit_button("💾 Guardar Cambios"):
                update_config("pharmacy_info", pharma_text)
                update_config("emergency_info", emergency_text)
                st.toast("Información actualizada correctamente.", icon="✅")
                import time
                time.sleep(1.5)
                # Optional: rerun to refresh if needed, but toast is nice
                st.rerun()
