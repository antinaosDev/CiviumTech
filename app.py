import streamlit as st
# Force Redeploy - Update Citizen View

# Import Modules
from modules.ui import apply_custom_styles, PATH_LOGO_APP, display_footer
from modules.db import init_supabase, fetch_tickets
from modules.auth import login, check_auth, get_current_role, get_current_user
from modules.sidebar import render_custom_sidebar
from modules.dashboard import render_mayor_dashboard
from modules.tickets import render_ticket_list
from modules.views import render_citizen_view

# Page Config
st.set_page_config(
    page_title="CiviumTech - Cholchol",
    page_icon=PATH_LOGO_APP,
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    # 1. Init & Styles
    apply_custom_styles()
    init_supabase()

    # 2. Authentication Flow
    # Uses a placeholder to strictly manage what is shown (Login vs App)
    main_placeholder = st.empty()
    
    is_auth = check_auth()

    if not is_auth:
        # Render Login inside the placeholder
        with main_placeholder.container():
            login()
    else:
        # Clear the placeholder just in case anything residal is there (though it shouldn't be)
        main_placeholder.empty()
        
        # --- Notifications Automation ---
        try:
            from modules import notifications
            notifications.run_daily_automation()
        except Exception as e:
            print(f"Notif Error: {e}")

        # Render Main App
        # 3. User Context
        role = get_current_role()
        
        # 4. Navigation (Sidebar) - This renders to sidebar so it's fine outside
        current_view = render_custom_sidebar(role)
        current_filter = st.session_state.get('filter', 'Todos')

        # 5. Data Fetching & Routing - Render into the main page
        # 5. Data Fetching & Routing - Render into the main page
        # RBAC: All non-citizen roles enter the management area
        if role != 'CITIZEN':
            
            # --- SUPER ADMIN VIEW ---
            if current_view == 'admin_users':
                if get_current_role() != 'Programador' and dict(st.session_state).get('real_role') != 'Programador':
                     st.error("Acceso restringido.")
                else:
                    from modules.admin_users import render_admin_users
                    render_admin_users()
                    
            # --- CONTENT MANAGER ---
            elif current_view == 'content_manager':
                from modules.views_content import render_content_manager
                render_content_manager()
                
            # --- ASSETS VIEW ---
            elif current_view == 'assets':
                from modules.assets_view import render_assets_view
                render_assets_view()

            # --- WIKI VIEW ---
            elif current_view == 'wiki':
                from modules.views_wiki import render_wiki_view
                render_wiki_view()
                
            # --- TICKET LIST / DASHBOARD ---
            elif current_view in ['overview', 'list', 'tickets']:
                # Optimize: Pass filter to DB
                filters = {}
                # Map Sidebar Selection to DB Columns
                # If filter is 'Todos', no filter. If it's a dept name, filter by depto.
                if current_filter != 'Todos' and current_filter != 'ACTIVOS':
                     filters['depto'] = current_filter
                
                # Fetch Data (Common for Dashboard and List)
                tickets_data = fetch_tickets(filters=filters, limit=100)
                
                if current_view == 'overview':
                    render_mayor_dashboard(tickets_data)
                    
                elif current_view in ['list', 'tickets']:
                    sel_id = st.session_state.get("selected_ticket_id")
                    if sel_id:
                        from modules.ticket_detail import render_ticket_detail
                        from modules.db import fetch_ticket_by_id
                        
                        ticket = fetch_ticket_by_id(sel_id)
                        if ticket:
                            render_ticket_detail(ticket)
                        else:
                            st.error("Ticket no encontrado.")
                            st.session_state.selected_ticket_id = None
                            st.rerun()
                    else:
                        render_ticket_list(tickets_data, current_filter, search_query=None)
            
            else:
                 st.info(f"Seleccione una opción del menú. (Vista: {current_view})")

        else:
            # Full Citizen View
            render_citizen_view()
            
        # Footer (Always show except for Portal Vecino)
        if role != 'CITIZEN':
            display_footer()

if __name__ == "__main__":
    main()
