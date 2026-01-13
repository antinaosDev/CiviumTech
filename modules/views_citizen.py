import streamlit as st
import re
import pandas as pd
from datetime import datetime
import time
import threading
from geopy.geocoders import Nominatim

# Use the new UNIDADES mapping and Shared UI Components
from modules.ui import UNIDADES, render_status_badge, PATH_LOGO_MUNI, PATH_LOGO_APP, render_field_ops_card_grid
from modules.db import create_ticket, fetch_ticket_by_id
from modules.communications import send_simple_email
from modules.reports import generate_ticket_receipt_pdf

def render_citizen_view():
    """
    Vista principal para el vecino:
    - Formulario de Nueva Solicitud (Categorizada por UNIDADES)
    - Consultar Estado
    - Calendario de Operativos
    """
    
    # Header minimalista
    h_c1, h_c2, h_c3 = st.columns([1, 5, 1])
    with h_c1:
        st.image(PATH_LOGO_MUNI, width=70)
    with h_c2:
        st.markdown("## 👋 Portal Vecino")
        st.caption("Solicitudes simplificadas y calendario de servicios.")
    with h_c3:
        try:
            st.image(PATH_LOGO_APP, width=100)
        except: pass

    # Tabs
    tab_form, tab_status, tab_ops, tab_stats = st.tabs(["📝 Ingresar Solicitud", "🔍 Consultar Estado", "📅 Actividades Comunales", "📊 Cifras y Datos"])

    # --- TAB 1: FORM ---
    with tab_form:
        # Pestaña "Ingresar Solicitud"
        main_container = st.empty()
        
        # State Check
        is_success = 'success_ticket_id' in st.session_state and st.session_state.success_ticket_id

        if is_success:
            # --- RENDER SUCCESSMESSAGE ---
            with main_container.container():
                # Fetch ticket data for receipt
                ticket_data = fetch_ticket_by_id(st.session_state.success_ticket_id)
                
                st.markdown(f"""
                <div style="background: #ecfdf5; border: 1px solid #10b981; border-radius: 12px; padding: 2rem; text-align: center; margin: 1rem 0;">
                    <span class="material-icons-round" style="font-size: 48px; color: #10b981;">check_circle</span>
                    <h3 style="color: #064e3b; margin-top: 1rem;">¡Solicitud Recibida!</h3>
                    <p style="color: #065f46;">Su número de seguimiento es:</p>
                    <div style="font-size: 1.5rem; font-weight: 800; color: #1e293b; margin-top: 0.5rem; user-select: all;">{st.session_state.success_ticket_id}</div>
                    <p style="font-size: 0.8rem; color: #64748b; margin-top: 0.5rem;">Guarde este código para consultar el estado de su solicitud.</p>
                </div>
                """, unsafe_allow_html=True)
                
                # PDF Receipt Generate
                pdf_bytes = None
                if ticket_data:
                    pdf_bytes = generate_ticket_receipt_pdf(ticket_data)

                # Email Logic DISABLED as per request
                # if ticket_data and ticket_data.get('user_email') and "invitado.cl" not in ticket_data.get('user_email'):
                #     # Check if we already sent it to avoid resending on refresh
                #     if 'receipt_sent' not in st.session_state or st.session_state.receipt_sent != st.session_state.success_ticket_id:
                #         email_subject = f"Comprobante de Solicitud #{st.session_state.success_ticket_id} - CiviumTech"
                #         email_body = f"""Estimado(a) Vecino(a),\n\nHemos recibido su solicitud con éxito.\n\nID: {st.session_state.success_ticket_id}\nAsunto: {ticket_data.get('sub')}\n\nAdjuntamos el comprobante oficial en PDF.\n\nAtte,\nMunicipalidad de Cholchol"""
                #         
                #         def send_async():
                #             send_simple_email(ticket_data['user_email'], email_subject, email_body, pdf_bytes, f"Comprobante_{st.session_state.success_ticket_id}.pdf")
                #         
                #         email_thread = threading.Thread(target=send_async)
                #         email_thread.start()
                #         
                #         st.success(f"✅ Se enviará el comprobante a **{ticket_data['user_email']}**.")
                        # st.session_state.receipt_sent = st.session_state.success_ticket_id
                
                # PDF Download Button
                if pdf_bytes:
                    c_dl1, c_dl2 = st.columns([1, 1])
                    with c_dl1:
                         st.download_button(
                            label="📥 Descargar Comprobante PDF",
                            data=pdf_bytes,
                            file_name=f"Comprobante_{st.session_state.success_ticket_id}.pdf",
                            mime="application/pdf",
                            key="btn_dl_receipt",
                            type="secondary"
                        )
                    with c_dl2:
                         def clear_form():
                             keys_to_clear = ['form_rut', 'form_name', 'form_phone', 'form_email', 'form_subject', 'form_desc', 'form_addr']
                             for k in keys_to_clear:
                                 if k in st.session_state:
                                     del st.session_state[k]
                             st.session_state.success_ticket_id = None
                         
                         st.button("Volver al Inicio", on_click=clear_form)
                else:
                    col_back_1, col_back_2 = st.columns([1, 1])
                    with col_back_1:
                         def clear_form():
                             keys_to_clear = ['form_rut', 'form_name', 'form_phone', 'form_email', 'form_subject', 'form_desc', 'form_addr']
                             for k in keys_to_clear:
                                 if k in st.session_state:
                                     del st.session_state[k]
                             st.session_state.success_ticket_id = None
                         
                         st.button("Volver al Inicio", on_click=clear_form)

        else:
            # --- RENDER FORM ---
            with main_container.container():
                st.info("Complete sus datos y el requerimiento para que podamos contactarlo.")
                
                with st.form("citizen_request_form"):
                    
                    st.markdown("#### 1. Identificación del Vecino")
                    with st.container(border=True):
                        c_col1, c_col2 = st.columns(2)
                        with c_col1:
                            rut_user = st.text_input("RUT", placeholder="12.345.678-k", key="form_rut")
                            nombre_user = st.text_input("Nombre Completo", placeholder="Juan Pérez", key="form_name")
                        with c_col2:
                             fono_user = st.text_input("Teléfono", placeholder="+569 1234 5678", key="form_phone")
                             email_user = st.text_input("Correo (Opcional)", placeholder="juan@ejemplo.com", key="form_email")

                    st.markdown("#### 2. Detalle de la Solicitud")
                    with st.container(border=True):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            unit_options = {u['label']: k for k, u in UNIDADES.items()}
                            sorted_labels = sorted(unit_options.keys())
                            selected_label = st.selectbox("Área / Departamento", options=sorted_labels, help="Seleccione el departamento responsable")
                        
                        with col2:
                            cat_options = ["Operativo / Terreno", "Social / Beneficios", "Administrativo", "Seguridad", "Medio Ambiente", "Salud", "Otro"]
                            selected_cat = st.selectbox("Clasificación del Requerimiento", options=cat_options)
                        
                        subject = st.text_input("Asunto Corto", placeholder="Ej: Luminaria apagada, Ayuda alimentos...", key="form_subject")

                        description = st.text_area("Detalles del Problema", height=100, placeholder="Describa la ubicación exacta y detalles del problema...", key="form_desc")
                        
                        # --- GEOLOCATION OPTIMIZED ---
                        st.markdown("#### 3. Ubicación (Opcional)")
                        st.caption("Ingrese la dirección o calle principal para ubicar su solicitud en el mapa.")
                        
                        c_addr, c_btn_map = st.columns([3, 1])
                        with c_addr:
                            address = st.text_input("Dirección", placeholder="Ej: Av. Balmaceda 123, Cholchol", key="form_addr")
                        with c_btn_map:
                            st.write("") 
                            st.write("") 
                            check_map = st.form_submit_button("📍 Ubicar", help="Buscar dirección en el mapa")
                        
                        lat, lon = -38.6015, -72.9461 # Default Cholchol
                        found_location = False
                        
                        # Only searching if button is clicked
                        if check_map and address:
                           try:
                               with st.spinner("Buscando dirección..."):
                                   geolocator = Nominatim(user_agent="civium_tech_cholchol_app_v1", timeout=10)
                                   
                                   # Clean address of city name to avoid duplication
                                   clean_addr = re.sub(r'(?i),?\s*Cho?lcho?l', '', address).strip()
                                   clean_addr = re.sub(r'(?i),?\s*Chile', '', clean_addr).strip()
                                   
                                   # Strategy 1: Specific
                                   search_query_1 = f"{clean_addr}, Cholchol, Chile"
                                   location = geolocator.geocode(search_query_1)
                                   
                                   # Strategy 2: Street only if number fails (strip numbers from start/end if complex)
                                   if not location:
                                       # Try without specific number if it looks like "Street 123"
                                       # Sometimes nominatim prefers "123 Street" or just "Street"
                                       search_query_2 = f"{clean_addr}, Comuna de Cholchol, Chile"
                                       location = geolocator.geocode(search_query_2)

                                   if location:
                                       lat, lon = location.latitude, location.longitude
                                       st.session_state['temp_geo_lat'] = lat
                                       st.session_state['temp_geo_lon'] = lon
                                       st.session_state['temp_geo_addr'] = location.address
                                       st.success(f"📍 Encontrado: {location.address}")
                                   else:
                                       st.warning("⚠️ No encontrado. Usaremos la referencia escrita.")
                           except Exception as e:
                               st.error(f"Error mapa: {e}")

                        # Use persisted geo if available
                        if 'temp_geo_lat' in st.session_state:
                            lat = st.session_state['temp_geo_lat']
                            lon = st.session_state['temp_geo_lon']
                            found_location = True
                            st.map(pd.DataFrame({'lat': [lat], 'lon': [lon]}), size=20, zoom=15)
                        # --- GEOLOCATION END ---

                    submitted = st.form_submit_button("🚀 Enviar Solicitud", type="primary")
                    
                    if submitted:
                        if not rut_user or not nombre_user or not fono_user:
                             st.error("⚠️ Debe completar RUT, Nombre y Teléfono para poder contactarlo.")
                        elif not subject or not description:
                             st.error("⚠️ Por favor complete el Asunto y los Detalles.")
                        else:
                            unit_code = unit_options[selected_label]
                            ciudadano_str = f"{nombre_user} ({rut_user})"
                            
                            contact_str = f"\n\n[Datos de Contacto]\nFono: {fono_user}"
                            if email_user: contact_str += f"\nEmail: {email_user}"
                            
                            geo_tag = ""
                            if found_location:
                                geo_tag = f"\n\n[UBICACION]\nDirección: {address}\nCoords: {lat}, {lon}"
                            
                            full_desc = description + contact_str + geo_tag
                            backend_email = email_user if email_user else "vecino@invitado.cl"
                            
                            new_ticket = {
                                'user_email': backend_email, 
                                'citizen_name': ciudadano_str,
                                'category': selected_cat,
                                'subject': subject,
                                'description': full_desc,
                                'status': 'Pendiente',
                                'depto': unit_code,
                                'urgency': 'Baja',
                                'lat': lat if found_location else None,
                                'lon': lon if found_location else None,
                                'address_ref': address
                            }
                            
                            with st.spinner("Enviando..."):
                                try:
                                    res = create_ticket(new_ticket)
                                    # Handle Supabase response (which handles data return)
                                    new_id = "REQ-WEB"
                                    if res.data:
                                        new_id = res.data[0].get('id', 'REQ-WEB')
                                    else:
                                         new_id = f"REQ-{int(time.time())}"
                                    
                                    st.session_state.success_ticket_id = new_id
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Error técnico: {e}")

    # --- TAB 2: CONSULTAR ESTADO ---
    with tab_status:
        st.markdown("#### 🔍 Seguimiento de Solicitudes")
        st.caption("Ingrese el código de seguimiento que recibió al momento de crear su solicitud.")
        
        col_search_1, col_search_2 = st.columns([3, 1])
        with col_search_1:
            search_id = st.text_input("Número de Solicitud", placeholder="Ej: REQ-12345", label_visibility="collapsed")
        with col_search_2:
            do_search = st.button("Buscar", type="primary")
            
        if do_search:
            if not search_id:
                st.warning("Ingrese un ID válido.")
            else:
                 with st.spinner("Buscando..."):
                     ticket = fetch_ticket_by_id(search_id)
                     
                     if ticket:
                         st.markdown("---")
                         status_badge = render_status_badge(ticket.get('status', 'Pendiente'))
                         unit_label = UNIDADES.get(ticket.get('depto'), {}).get('label', ticket.get('depto'))
                         
                         st.markdown(f"""
                         <div style="background: white; border: 1px solid #e2e8f0; border-radius: 12px; padding: 2rem;">
                             <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 1rem;">
                                 <div>
                                     <h2 style="margin: 0; color: #1e293b;">{ticket.get('sub', 'Sin Asunto')}</h2>
                                     <div style="color: #64748b; font-size: 0.9rem; margin-top: 4px;">ID: <strong>{ticket.get('id')}</strong> • {ticket.get('fecha')}</div>
                                 </div>
                                 <div>{status_badge}</div>
                             </div>
                             
                             <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-bottom: 1.5rem; background: #f8fafc; padding: 1rem; border-radius: 8px;">
                                 <div>
                                     <small style="color: #64748b; font-weight: 700; text-transform: uppercase;">Departamento</small>
                                     <div style="color: #334155;">{unit_label}</div>
                                 </div>
                                 <div>
                                     <small style="color: #64748b; font-weight: 700; text-transform: uppercase;">Clasificación</small>
                                     <div style="color: #334155;">{ticket.get('categoria', 'General')}</div>
                                 </div>
                             </div>
                             
                             <div style="margin-bottom: 1rem;">
                                 <h4 style="font-size: 1rem; margin-bottom: 0.5rem; color: #334155;">Descripción Original</h4>
                                 <p style="color: #475569; font-size: 0.95rem; line-height: 1.5; background: #fff; border: 1px solid #f1f5f9; padding: 1rem; border-radius: 8px;">
                                     {ticket.get('desc')}
                                 </p>
                             </div>
                             
                             {'<div style="padding: 1rem; background: #eff6ff; border: 1px solid #bfdbfe; border-radius: 8px; color: #1e40af;"><strong>💬 Respuesta Municipal:</strong><br>' + ticket.get('reply') + '</div>' if ticket.get('reply') else ''}
                         </div>
                         """, unsafe_allow_html=True)
                     else:
                         st.error("❌ No se encontró ninguna solicitud con ese ID. Verifique y vuelva a intentar.")
    
    # --- TAB 3: OPS ---
    with tab_ops:
        render_field_ops_card_grid()
        
    # --- TAB 4: STATS/INFO ---
    with tab_stats:
        st.subheader("📊 Cifras y Datos de Utilidad")
        
        from modules.db import fetch_tickets
        import plotly.express as px
        
        # Use Exception handling for reliability
        df = pd.DataFrame()
        try:
             all_tix = fetch_tickets()
             df = pd.DataFrame(all_tix)
        except Exception:
             pass
        
        if not df.empty:
            st.markdown("##### Transparencia Municipal")
            k1, k2, k3 = st.columns(3)
            with k1:
                st.metric("Solicitudes Este Mes", len(df), delta="Total")
            with k2:
                resolved = len(df[df['status'] == 'Resuelto'])
                st.metric("Casos Resueltos", resolved, delta=f"{int(resolved/len(df)*100)}% Eficiencia")
            with k3:
                st.metric("Tiempo Promedio", "2.5 Días", help="Tiempo estimado de respuesta")
            
            st.divider()
            
            c_chart, c_info = st.columns([1, 1])
            with c_chart:
                st.caption("Temas más consultados")
                if 'categoria' in df.columns:
                    cat_counts = df['categoria'].value_counts().reset_index()
                    cat_counts.columns = ['Tema', 'Cantidad']
                    fig = px.pie(cat_counts, values='Cantidad', names='Tema', hole=0.5)
                    fig.update_layout(showlegend=False, margin=dict(t=0, b=0, l=0, r=0), height=200)
                    st.plotly_chart(fig)
            
            with c_info:
                st.caption("Farmacias de Turno (Hoy)")
                st.success("💊 **Farmacia Cruz Verde**\n\n📍 Av. Valparaíso 450\n🕒 Hasta las 23:00 hrs")
                
                st.caption("Teléfonos de Emergencia")
                st.warning("🚑 **Ambulancia/SAPU**: 131\n🚒 **Bomberos**: 132\n🚓 **Carabineros**: 133")
                
        else:
             st.info("No hay datos estadísticos disponibles aún.")
