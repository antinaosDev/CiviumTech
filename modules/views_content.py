import streamlit as st
import pandas as pd
from datetime import datetime
from modules.db import (
    fetch_activities, create_activity, delete_activity,
    fetch_config, update_config
)

def render_content_manager():
    st.title("Gestor de Contenidos")
    st.markdown("Administra la información visible en el Portal Vecino.")
    
    tab_activities, tab_info = st.tabs(["📅 Actividades Semanales", "ℹ️ Datos de Utilidad"])
    
    # --- TAB 1: ACTIVITIES ---
    with tab_activities:
        st.subheader("Actividades Programadas")
        
        # 1. List Existing
        activities = fetch_activities()
        if activities:
            df = pd.DataFrame(activities)
            # Display simpler table
            st.dataframe(
                df[['id', 'date_str', 'time_str', 'type', 'title', 'location']],
                use_container_width=True,
                hide_index=True
            )
            
            # Delete Action
            st.markdown("##### Eliminar Actividad")
            with st.form("delete_activity_form"):
                id_to_del = st.selectbox("Seleccione ID a eliminar", [a['id'] for a in activities])
                if st.form_submit_button("🗑️ Eliminar", type="primary"):
                    delete_activity(id_to_del)
                    st.success("Actividad eliminada.")
                    st.rerun()
        else:
            st.info("No hay actividades registradas.")
            
        st.divider()
        
        # 2. Add New
        st.subheader("➕ Agregar Nueva Actividad")
        with st.form("new_activity_form"):
            col1, col2 = st.columns(2)
            with col1:
                title = st.text_input("Título", placeholder="Ej. Operativo Veterinario")
                type_ = st.selectbox("Tipo", ["Salud", "Veterinario", "Social", "Servicios"])
                icon_map = {"Salud": "medical_services", "Veterinario": "pets", "Social": "favorite", "Servicios": "local_shipping"}
                
            with col2:
                date_obj = st.date_input("Fecha")
                time_obj = st.time_input("Hora")
                location = st.text_input("Lugar", placeholder="Ej. Sede Social Malalche")
                
            if st.form_submit_button("Guardar Actividad"):
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
                    create_activity(new_data)
                    st.success("Actividad creada correctamente.")
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
                # Optional: rerun to refresh if needed, but toast is nice
                st.rerun()
