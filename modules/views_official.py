import streamlit as st
import time
from modules.db import fetch_tickets, fetch_ticket_by_id, delete_ticket, update_ticket
from modules.tickets import render_ticket_list
from modules.ticket_detail import render_ticket_detail
from modules.ui import render_field_ops_card_grid



def render_official_view(tickets_data, current_filter):
    # Determine Label for Title
    from modules.ui import UNIDADES
    label_unidad = UNIDADES.get(current_filter, {}).get('label', current_filter) if current_filter != 'Todos' else 'Vista Global'
    
    st.title(f"Gestión: {label_unidad}")
    
    # Check if a ticket is selected for detail view
    selected_id = st.session_state.get('selected_ticket_id')
    
    if selected_id:
        # Fetch fresh data for that ticket
        ticket = fetch_ticket_by_id(selected_id)
        if ticket:
            render_ticket_detail(ticket)
        else:
            st.error("Error al cargar el ticket o fue eliminado.")
            if st.button("Volver"):
                st.session_state.selected_ticket_id = None
                st.rerun()
    else:
        # Tabs for Inbox vs Outbox/Create
        tab_inbox, tab_create = st.tabs(["📥 Bandeja de Entrada", "✍️ Generar Solicitud / Interna"])

        with tab_inbox:
            st.subheader(f"Solicitudes: {label_unidad}")
            
            # Use the passed tickets_data which is already filtered by app.py
            if tickets_data:
                # We reuse render_ticket_list to render the actual CARDS, but strictly for display
                # Note: render_ticket_list has its own Header/Form logic we want to bypass if we are wrapping it.
                # However, render_ticket_list is designed to be a standalone full view. 
                # We should probably strip render_ticket_list of its header/form OR just call the rendering part.
                # For now, let's call render_ticket_list but pass a flag or just let it render. 
                # Wait, render_ticket_list renders a Header and a Form. We don't want that double header.
                
                # Let's extract the loop from render_ticket_list or copy it here? 
                # Better: Use render_ticket_list but we might see the duplicate form if we don't be careful.
                # The form in render_ticket_list appears if filter_category != 'Todos'.
                
                # OPTION: We modified render_ticket_list to NOT show the form? 
                # Or we just implement the card loop here to be clean and custom.
                # Let's use the card loop here for the "Official View" style using the code from render_ticket_list.
                
                # ... copying card rendering logic ...
                # Import UNIDADES and badges is needed (already at top)
                from modules.ui import render_status_badge, render_urgency_badge
                
                import pandas as pd
                df = pd.DataFrame(tickets_data)
                
                # --- Search & Filter UI (Mini) ---
                c_search, c_filt = st.columns([3, 1])
                search = c_search.text_input("🔍 Buscar en lista...", label_visibility="collapsed", placeholder="Buscar...")
                
                if search:
                    q = search.lower()
                    df = df[
                         df['title'].astype(str).str.lower().str.contains(q) |
                         df['description'].str.lower().str.contains(q)
                    ]

                for _, row in df.iterrows():
                     # ... Render Card ...
                     # (Simplified version of tickets.py card)
                     with st.container():
                        t_id = row.get('id', '???')
                        t_title = row.get('title', 'Sin Asunto')
                        t_desc = row.get('description', '')
                        t_status = row.get('status', 'RECIBIDO')
                        t_prio = row.get('priority', 'MEDIA')
                        t_depto_code = row.get('depto', '???')
                        
                        # Unit Info
                        u_info = UNIDADES.get(t_depto_code, {})
                        u_label = u_info.get('label', t_depto_code)
                        
                        st.markdown(f"""
                        <div style="background:white; padding:1rem; border-radius:8px; border:1px solid #e2e8f0; margin-bottom:0.8rem; box-shadow:0 1px 2px rgba(0,0,0,0.05);">
                           <div style="display:flex; justify-content:space-between; margin-bottom:0.5rem">
                               <span style="font-weight:700; color:#475569">#{str(t_id)[-6:]}</span>
                               <span style="font-size:0.8rem; background:#f1f5f9; padding:2px 6px; border-radius:4px">{u_label}</span>
                           </div>
                           <div style="font-weight:600; font-size:1.05rem; margin-bottom:0.2rem">{t_title}</div>
                           <div style="color:#64748b; font-size:0.9rem; margin-bottom:0.8rem">{t_desc[:100]}...</div>
                           <div style="display:flex; gap:0.5rem; align-items:center">
                               {render_status_badge(t_status)}
                               {render_urgency_badge(t_prio)}
                           </div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        if st.button("Gestionar", key=f"btn_manage_{t_id}"):
                            st.session_state.selected_ticket_id = t_id
                            st.rerun()

            else:
                st.info("No hay solicitudes en esta bandeja.")

        with tab_create:
            st.subheader("Generar Solicitud Interna")
            st.caption("Cree un ticket para solicitar gestión a otra unidad municipal.")
            
            c1, c2 = st.columns([1, 1])
            with c1:
                # Form
                with st.form("internal_ticket_form"):
                    subject = st.text_input("Asunto")
                    
                    # Fetch Depts for Dropdown
                    from modules.db import fetch_departments
                    from modules.ui import UNIDADES
                    
                    depts = fetch_departments() 
                    
                    # Robust Mapping: Name -> {id, code}
                    dept_map = {}
                    
                    # Helper for reverse lookup (Label -> Code)
                    label_to_code = {v['label']: k for k, v in UNIDADES.items()}
                    
                    for d in depts:
                        d_id = d['id']
                        d_name = d['name']
                        d_code = d.get('code') # Might be None/Missing if DB schema differs
                        
                        # If code is missing, try to infer from UNIDADES or Name
                        # If code is missing, try to infer from UNIDADES or Name
                        if not d_code:
                            # Explicit Override for Justicia -> JPL
                            if d_name == 'Justicia':
                                d_code = 'JPL'
                            # Try to match Name to UNIDADES Label
                            elif d_name in label_to_code:
                                d_code = label_to_code[d_name]
                            else:
                                # Fallback: Generate a code from name (e.g. "DIDECO" from "DIDECO (Desc...)")
                                # This is risky but necessary if column is missing.
                                # Simple: Take first word upper
                                d_code = d_name.split(' ')[0].upper()[:10]
                        
                        dept_map[d_name] = {'id': d_id, 'code': d_code}
                    
                    
                    target_dept_name = st.selectbox("Unidad de Destino", options=list(dept_map.keys()))
                    
                    priority = st.select_slider("Prioridad", options=["Baja", "Media", "Alta", "Crítica"], value="Media")
                    desc = st.text_area("Descripción de la Solicitud")
                    
                    submitted = st.form_submit_button("Enviar Solicitud", type="primary")
                    
                    if submitted:
                        if not subject or not desc:
                            st.error("Complete los campos obligatorios.")
                        else:
                            # Create Ticket Payload
                            selected_dept = dept_map[target_dept_name]
                            new_ticket = {
                                'subject': subject, # Renamed from 'title' to match DB/Citizen
                                'description': desc,
                                'category': 'Interna', 
                                'citizen_name': f"Interna - {st.session_state.get('user_role', 'Funcionario')}", # Identify Origin Role
                                'urgency': priority.capitalize(), # Match Citizen Format 'Baja' vs 'BAJA'
                                'status': 'Pendiente', # 'RECIBIDO' violated check constraint on live DB
                                'depto': selected_dept['code'],
                                'user_email': st.session_state.get('email') # Restoring as it works in Citizen
                            }
                            
                            # Add Email to description as metadata workaround
                            # if st.session_state.get('email'):
                            #    new_ticket['description'] += f"\n\n[Enviado por: {st.session_state.get('email')}]"

                            from modules.db import create_ticket
                            try:
                                create_ticket(new_ticket)
                                st.success("Solicitud enviada exitosamente.")
                                time.sleep(1)
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error al enviar: {e}")

            with c2:
                st.write("###### Mis Solicitudes Enviadas")
                st.caption("Gestione las solicitudes que ha generado.")
                
                # Fetches ALL tickets and filters in Python (Safe Fallback)
                my_email = st.session_state.get('email')
                current_role = st.session_state.get('user_role', '')
                
                if my_email or current_role:
                     all_tickets = fetch_tickets(limit=100)
                     
                     # Robust filter for my tickets:
                     # STRICT MODE: Only match tickets clearly signed by the current role.
                     # We disable email fallback to prevent "polluting" the view with tickets
                     # from other roles created with the same testing email.
                     
                     sent_tickets = []
                     target_signature = f"Interna - {current_role}"
                     
                     for t in all_tickets:
                         c_name = t.get('citizen_name') or ''
                         
                         # Check strict role match
                         if current_role and target_signature in c_name:
                             sent_tickets.append(t)
                         
                         # Note: Legacy tickets (without signature) are excluded prevents ambiguity.
                         # Users must create new tickets to see them here reliably.
                     
                     if sent_tickets:
                         for t in sent_tickets[:10]: # Limit to last 10 for performance
                             # Handle 'subject' or 'title'
                             t_id = t.get('id')
                             subj = t.get('subject', t.get('title', 'Sin título'))
                             status = t.get('status', 'Pendiente')
                             
                             with st.expander(f"{t.get('created_at', '')[:10]} - {subj}"):
                                 st.caption(f"ID: {str(t_id)[-6:]} | Estado: {status} | Destino: {t.get('depto')}")
                                 st.write(t.get('description'))
                                 
                                 st.divider()
                                 
                                 # CRUD Controls
                                 # Allow editing/deleting mainly if 'Pendiente', but user asked for CRUD. 
                                 # We'll allow it generally but maybe warn/restrict if finalized.
                                 
                                 cr_cols = st.columns([1, 1])
                                 
                                 # DELETE BUTTON
                                 with cr_cols[1]:
                                     if st.button("🗑️ Eliminar", key=f"btn_del_{t_id}", help="Eliminar permanentemente esta solicitud"):
                                         try:
                                             delete_ticket(t_id)
                                             st.success("Solicitud eliminada.")
                                             time.sleep(1)
                                             st.rerun()
                                         except Exception as e:
                                             st.error(f"Error al eliminar: {e}")
                                 
                                 # EDIT FORM (Toggle or Inline)
                                 # We'll use a checkbox to reveal the edit form to keep UI clean
                                 if st.checkbox("✏️ Editar Solicitud", key=f"chk_edit_{t_id}"):
                                     with st.form(key=f"form_edit_{t_id}"):
                                         new_subj = st.text_input("Asunto", value=subj)
                                         new_desc = st.text_area("Descripción", value=t.get('description', ''))
                                         
                                         if st.form_submit_button("💾 Guardar Cambios"):
                                             updates = {
                                                 'subject': new_subj,
                                                 'description': new_desc
                                             }
                                             try:
                                                 update_ticket(t_id, updates)
                                                 st.success("Actualizado correctamente.")
                                                 time.sleep(1)
                                                 st.rerun()
                                             except Exception as e:
                                                 st.error(f"Error al actualizar: {e}")
                                                 
                     else:
                         st.info("No ha enviado solicitudes aún.")

def render_field_ops_view():
    render_field_ops_card_grid()
