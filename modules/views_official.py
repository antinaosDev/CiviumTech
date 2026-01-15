import streamlit as st
from modules.db import fetch_tickets, fetch_ticket_by_id
from modules.tickets import render_ticket_list
from modules.ticket_detail import render_ticket_detail
from modules.ui import render_field_ops_card_grid

def render_official_view():
    st.title("Bandeja de Entrada")
    
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
        # Default: Show List
        # Note: We rely on the caller (app.py) to have set filters if needed, 
        # basically app.py seems to call `fetch_tickets` and pass data to `render_ticket_list`. 
        # But `render_official_view` in original code fetched tickets itself implicitly (lines 433).
        # We will keep this behavior but handle it robustly.
        
        st.info("Seleccione una unidad en el menú lateral para ver las solicitudes.")
        
        # Determine User Context
        user_dept = st.session_state.get('department') # e.g., 'DOM', 'DIDECO'
        # user_dept_id = ... (We might need the ID, but ticket filtering primarily relies on department codes or IDs depending on DB implementation)
        # Looking at schema, 'assigned_department_id' is UUID.
        # But 'fetch_tickets' filters logic relies on exact match.
        # Let's verify if `department` in session is ID or Code. 
        # In `auth.py`, `st.session_state['department'] = user_row.get('department', '')`.
        # We need to know if that is ID string or Name. Assuming ID based on `users` table FK.
        
        # Tabs for Inbox vs Outbox/Create
        tab_inbox, tab_create = st.tabs(["📥 Bandeja de Entrada", "✍️ Generar Solicitud"])

        with tab_inbox:
            st.subheader(f"Solicitudes para mi Unidad")
            # Filter tickets where assigned_department_id == user's department
            # If user_dept is None/Empty, they see nothing or all? -> Nothing for safety.
            if user_dept:
                # We need to filter by 'assigned_department_id'
                # Note: `fetch_tickets` filters argument is dynamic.
                # Use 'assigned_department_id' if your DB uses UUIDs, or 'depto' if using codes. 
                # Based on schema it is `assigned_department_id`.
                inbox_tickets = fetch_tickets(filters={'assigned_department_id': user_dept}) 
                render_ticket_list(inbox_tickets, 'Todos', None)
            else:
                st.warning("No tiene un departamento asignado. Contacte al administrador.")

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
                    depts = fetch_departments() 
                    # Convert to format for selectbox: Name -> {id, code}
                    dept_map = {d['name']: {'id': d['id'], 'code': d['code']} for d in depts}
                    
                    target_dept_name = st.selectbox("Unidad de Destino", options=list(dept_map.keys()))
                    
                    priority = st.select_slider("Prioridad", options=["Baja", "Media", "Alta", "Urgente"], value="Media")
                    desc = st.text_area("Descripción de la Solicitud")
                    
                    submitted = st.form_submit_button("Enviar Solicitud", type="primary")
                    
                    if submitted:
                        if not subject or not desc:
                            st.error("Complete los campos obligatorios.")
                        else:
                            # Create Ticket Payload
                            selected_dept = dept_map[target_dept_name]
                            new_ticket = {
                                'title': subject,
                                'description': desc,
                                'category': 'Interna', 
                                'priority': priority.upper(),
                                'status': 'RECIBIDO',
                                'user_id': st.session_state.get('user_id'),
                                'assigned_department_id': selected_dept['id'],
                                'depto': selected_dept['code'] # REQUIRED for compatibility with UI
                            }
                            
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
                # Fetch tickets created by me (user_id)
                my_id = st.session_state.get('user_id')
                if my_id:
                     # We need to filter by creator. 
                     # fetch_tickets filters are for equality. 
                     # Schema: user_id is the creator.
                     sent_tickets = fetch_tickets(filters={'user_id': my_id})
                     if sent_tickets:
                         for t in sent_tickets[:5]: # Show last 5
                             with st.expander(f"{t.get('created_at', '')[:10]} - {t.get('title', 'Sin título')}"):
                                 st.caption(f"Estado: {t.get('status')} | Destino: {t.get('assigned_department_id')}") # fast fix, prefer name
                                 st.write(t.get('description'))
                     else:
                         st.info("No ha enviado solicitudes aún.")

def render_field_ops_view():
    render_field_ops_card_grid()
