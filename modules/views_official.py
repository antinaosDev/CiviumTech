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
        
        tickets = fetch_tickets()
        st.info("Seleccione una unidad en el menú lateral para ver las solicitudes.")
        
        # Show global list by default
        render_ticket_list(tickets, 'Todos', None)

def render_field_ops_view():
    render_field_ops_card_grid()
