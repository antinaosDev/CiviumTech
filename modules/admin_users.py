import streamlit as st
import pandas as pd
from modules import db, auth

def render_admin_users():
    from modules.auth import get_real_role
    if get_real_role() != 'Programador':
        st.error("⛔ Acceso Denegado: Esta vista es exclusiva para el Programador del Sistema.")
        return

    st.title("👥 Gestión de Usuarios y Roles")
    st.caption("Acceso Exclusivo: Programador")
    
    # Tabs
    tab_list, tab_create = st.tabs(["Listado de Usuarios", "Crear Nuevo Usuario"])
    
    # --- LIST ---
    # --- LIST / EDIT / DELETE ---
    with tab_list:
        users = db.get_all_users()
        if users:
            df = pd.DataFrame(users)
            # Display Table
            if 'password_hash' in df.columns:
                display_df = df.drop(columns=['password_hash'])
            else:
                display_df = df
            
            st.dataframe(display_df, use_container_width=True)
            
            st.markdown("### 🛠️ Acciones")
            user_options = {u['username']: u['id'] for u in users}
            selected_username = st.selectbox("Seleccione Usuario para Editar/Eliminar", ["-- Seleccione --"] + list(user_options.keys()))
            
            if selected_username != "-- Seleccione --":
                user_id = user_options[selected_username]
                user_data = next((u for u in users if u['id'] == user_id), None)
                
                if user_data:
                    with st.form("edit_user_form"):
                        st.subheader(f"Editando: {user_data['username']}")
                        
                        ec1, ec2 = st.columns(2)
                        e_fullname = ec1.text_input("Nombre Completo", value=user_data.get('full_name', ''))
                        e_email = ec2.text_input("Email", value=user_data.get('email', ''))
                        
                        ec3, ec4 = st.columns(2)
                        # Default index handling
                        curr_role = user_data.get('role', 'DIDECO')
                        roles = ["Administrador", "DIDECO", "SECPLAN", "DOM", "DAF", "SALUD", "Programador"]
                        idx_role = roles.index(curr_role) if curr_role in roles else 0
                        
                        e_role = ec3.selectbox("Rol", roles, index=idx_role)
                        e_dept = ec4.text_input("Departamento", value=user_data.get('department', ''))
                        
                        e_pass = st.text_input("Nueva Contraseña (Dejar en blanco para no cambiar)", type="password")
                        e_status = st.selectbox("Estado", ["Activo", "Inactivo"], index=0 if user_data.get('status', 'Activo') == 'Activo' else 1)
                        
                        submitted_edit = st.form_submit_button("💾 Guardar Cambios")
                        
                        if submitted_edit:
                            updates = {
                                "full_name": e_fullname, 
                                "role": e_role, 
                                "email": e_email, 
                                "department": e_dept,
                                "status": e_status
                            }
                            if e_pass:
                                updates["password_hash"] = auth.hash_password(e_pass)
                                
                            try:
                                db.update_user_record(user_id, updates)
                                st.toast("Usuario actualizado correctamente.", icon="✅")
                                import time
                                time.sleep(1.5)
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error al actualizar: {e}")

                    st.markdown("---")
                    col_del, _ = st.columns([1, 4])
                    with col_del:
                        if st.button("🗑️ Eliminar Usuario", type="primary"):
                            try:
                                db.delete_user_record(user_id)
                                st.toast("Usuario eliminado.", icon="🗑️")
                                import time
                                time.sleep(1.5)
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error al eliminar: {e}")
        else:
            st.warning("No se encontraron usuarios.")

    # --- CREATE ---
    with tab_create:
        with st.form("create_user_form"):
            st.subheader("Registrar Nuevo Funcionario")
            c1, c2 = st.columns(2)
            new_user = c1.text_input("Nombre de Usuario (Login)", placeholder="j.perez")
            new_pass = c2.text_input("Contraseña Inicial", type="password")
            
            c3, c4 = st.columns(2)
            full_name = c3.text_input("Nombre Completo")
            email = c4.text_input("Email Corporativo")
            
            c5, c6 = st.columns(2)
            role = c5.selectbox("Rol del Sistema", ["Administrador", "DIDECO", "SECPLAN", "DOM", "DAF", "SALUD", "Programador"])
            from modules.ui import UNIDADES
            dept_options = list(UNIDADES.keys())
            dept = c6.selectbox("Departamento", options=dept_options)
            
            submitted = st.form_submit_button("Crear Usuario")
            
            if submitted:
                if not new_user or not new_pass or not full_name:
                    st.error("Campos obligatorios: Usuario, Contraseña, Nombre.")
                else:
                    # Hash password
                    hashed = auth.hash_password(new_pass)
                    data = {
                        "username": new_user,
                        "password_hash": hashed,
                        "full_name": full_name,
                        "role": role,
                        "email": email,
                        "department": dept,
                        "status": "Activo"
                    }
                    try:
                        db.create_user_record(data)
                        st.toast(f"Usuario {new_user} creado exitosamente.", icon="✅")
                    except Exception as e:
                        st.error(f"Error al crear: {e}")
