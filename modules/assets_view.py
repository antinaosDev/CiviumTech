import streamlit as st
import pandas as pd
from modules.db import fetch_all_assets, create_asset, delete_asset, update_asset
from datetime import date

def render_assets_view():
    st.title("📦 Gestión de Activos y Inventario")
    st.markdown("Administración de recursos municipales, vehículos, equipos y mobiliario.")

    # 1. Fetch Data
    assets = fetch_all_assets()
    
    # 2. Formulario de Creación (Create)
    with st.expander("➕ Registrar Nuevo Activo", expanded=False):
        with st.form("new_asset_form"):
            c1, c2 = st.columns(2)
            name = c1.text_input("Nombre del Activo", placeholder="Ej: Camioneta Nissan NP300")
            tipo = c2.selectbox("Tipo", ["Vehículo", "Maquinaria", "Equipo Computacional", "Mobiliario", "Inmueble", "Otro"])
            
            c3, c4 = st.columns(2)
            status = c3.selectbox("Estado", ["Operativo", "En Mantención", "De Baja", "Extraviado"])
            assigned_to = c4.text_input("Asignado a (Responsable)", placeholder="Ej: Dirección de Obras")
            
            c5, c6 = st.columns(2)
            purchase_date = c5.date_input("Fecha de Adquisición", value=date.today())
            cost = c6.number_input("Costo Estimado ($)", min_value=0, step=1000)
            
            desc = st.text_area("Descripción / Observaciones")
            
            submitted = st.form_submit_button("Guardar Activo")
            if submitted:
                if not name:
                    st.error("El nombre es obligatorio.")
                else:
                    new_asset = {
                        "name": name,
                        "type": tipo,
                        "status": status,
                        "assigned_to": assigned_to,
                        "purchase_date": str(purchase_date),
                        "cost": cost,
                        "description": desc
                    }
                    res = create_asset(new_asset)
                    if res:
                        st.success("Activo creado exitosamente.")
                        st.rerun()

    st.divider()

    # 3. Listado de Activos (Read)
    if not assets:
        st.info("No hay activos registrados.")
    else:
        # Convert search/filter
        search = st.text_input("🔍 Buscar Activo", placeholder="Nombre, Responsable o Tipo...")
        
        df = pd.DataFrame(assets)
        if search:
            mask = df.apply(lambda x: x.astype(str).str.contains(search, case=False).any(), axis=1)
            df = df[mask]
            
        # Display Stats
        m1, m2, m3 = st.columns(3)
        with m1:
            st.metric("Total Activos", len(df))
        with m2:
            st.metric("Valor Total Patrimonio", f"${df['cost'].sum():,.0f}")
        with m3:
            # Example third metric
            in_maintenance = len(df[df['status'] == 'En Mantención'])
            st.metric("En Mantención", in_maintenance, delta="-1" if in_maintenance > 0 else "OK", delta_color="inverse")
        
        st.divider()        
        # Table
        st.dataframe(
            df[['name', 'type', 'status', 'assigned_to', 'cost', 'purchase_date', 'description']],
            hide_index=True
        )
        
        # 4. Acciones de Edición/Eliminación (Update/Delete)
        st.subheader("🛠️ Acciones")
        
        asset_options = {a['name']: a['id'] for a in assets}
        selected_asset_name = st.selectbox("Seleccionar Activo para Editar/Eliminar", ["-- Seleccione --"] + list(asset_options.keys()))
        
        if selected_asset_name != "-- Seleccione --":
            asset_id = asset_options[selected_asset_name]
            # Find current data
            current_data = next((a for a in assets if a['id'] == asset_id), None)
            
            if current_data:
                with st.form("edit_asset_form"):
                    st.write(f"Editando: **{current_data['name']}**")
                    
                    ec1, ec2 = st.columns(2)
                    e_name = ec1.text_input("Nombre", value=current_data.get('name', ''))
                    e_type = ec2.selectbox("Tipo", ["Vehículo", "Maquinaria", "Equipo Computacional", "Mobiliario", "Inmueble", "Otro"], index=["Vehículo", "Maquinaria", "Equipo Computacional", "Mobiliario", "Inmueble", "Otro"].index(current_data.get('type', "Otro")))
                    
                    ec3, ec4 = st.columns(2)
                    e_status = ec3.selectbox("Estado", ["Operativo", "En Mantención", "De Baja", "Extraviado"], index=["Operativo", "En Mantención", "De Baja", "Extraviado"].index(current_data.get('status', 'Operativo')))
                    e_assigned = ec4.text_input("Asignado a", value=current_data.get('assigned_to', ''))
                    
                    ec5, ec6 = st.columns(2)
                    # Handle date parsing safely
                    try:
                        def_date = pd.to_datetime(current_data.get('purchase_date')).date()
                    except:
                        def_date = date.today()
                        
                    e_date = ec5.date_input("Fecha Adquisición", value=def_date)
                    e_cost = ec6.number_input("Costo", value=float(current_data.get('cost', 0)))
                    
                    e_desc = st.text_area("Descripción", value=current_data.get('description', ''))
                    
                    c_edit, c_del = st.columns([1, 4])
                    with c_edit:
                        save_changes = st.form_submit_button("💾 Guardar Cambios")
                    with c_del:
                        pass # Delete button must be outside form to avoid double submit issues or handled carefully
                    
                    if save_changes:
                        updates = {
                            "name": e_name,
                            "type": e_type,
                            "status": e_status,
                            "assigned_to": e_assigned,
                            "purchase_date": str(e_date),
                            "cost": e_cost,
                            "description": e_desc
                        }
                        ures = update_asset(asset_id, updates)
                        if ures:
                            st.success("Activo actualizado corrextamente.")
                            st.rerun()

                # Delete Button (Outside Form for safety)
                st.markdown("---")
                if st.button("❌ Eliminar este Activo", type="primary"):
                    if delete_asset(asset_id):
                        st.warning("Activo eliminado.")
                        st.rerun()
