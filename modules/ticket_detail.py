import streamlit as st
import time
from modules.ui import UNIDADES, render_status_badge, render_urgency_badge
from modules.db import update_ticket

def render_ticket_detail(ticket):
    """
    Renderiza el detalle de una solicitud para gestión usando componentes nativos de Streamlit.
    """
    
    # Header with Back Button
    col_back, col_title = st.columns([1, 5])
    with col_back:
        if st.button("← Volver", type="secondary"):
            st.session_state.selected_ticket_id = None
            st.rerun()
            
    with col_title:
        st.markdown(f"### Gestión de Solicitud: {ticket.get('id')}")

    st.markdown("---")

    # Layout: Info on Left, Actions on Right
    c_info, c_action = st.columns([2, 1])

    with c_info:
        # Ticket Metadata
        st.markdown("#### Información del Requerimiento")
        
        with st.container(border=True):
            # Row 1
            r1c1, r1c2 = st.columns(2)
            with r1c1:
                st.caption("CIUDADANO")
                st.markdown(f"**{ticket.get('citizen_name', ticket.get('ciudadano'))}**")
            with r1c2:
                st.caption("FECHA DE INGRESO")
                # Format date if possible
                t_date = str(ticket.get('created_at', ticket.get('fecha', '-'))).split('T')[0]
                st.text(t_date)
            
            # Row 2
            r2c1, r2c2 = st.columns(2)
            with r2c1:
                st.caption("UNIDAD ASIGNADA")
                unit_label = UNIDADES.get(ticket.get('depto'), {}).get('label', ticket.get('depto'))
                st.text(unit_label)
            with r2c2:
                st.caption("CLASIFICACIÓN")
                st.text(ticket.get('category', ticket.get('categoria', 'General')))
                
            st.divider()
            
            st.caption("ASUNTO")
            st.markdown(f"##### {ticket.get('subject', 'Sin Asunto')}")
            
            st.caption("DETALLE DEL PROBLEMA")
            st.info(ticket.get('description', ticket.get('desc')))
            
            st.divider()
            
            # Status / Urgency Pills
            p1, p2, p3 = st.columns([1, 1, 2])
            with p1:
                st.caption("ESTADO")
                # Using native Markdown coloring or just text
                st.markdown(render_status_badge(ticket.get('status', ticket.get('estado', 'Pendiente'))), unsafe_allow_html=True)
            with p2:
                st.caption("URGENCIA")
                st.markdown(render_urgency_badge(ticket.get('urgency', ticket.get('urgencia', 'Baja'))), unsafe_allow_html=True)

    with c_action:
        st.subheader("Acciones")
        
        with st.container(border=True):
            # Timeline Visual
            st.markdown("##### ⏳ Línea de Tiempo")
            st.markdown(f"""
            <div style="border-left: 2px solid #e2e8f0; padding-left: 1rem; margin-left: 4px; margin-bottom: 1.5rem;">
                <div style="position: relative; margin-bottom: 1rem;">
                    <div style="position: absolute; left: -21px; top: 4px; width: 12px; height: 12px; border-radius: 50%; background: #94a3b8; border: 2px solid white;"></div>
                    <div style="font-size: 0.8rem; font-weight: 600; color: #334155;">Solicitud Ingresada</div>
                    <div style="font-size: 0.75rem; color: #64748b;">{str(ticket.get('created_at', ticket.get('fecha', '-'))).split('T')[0]}</div>
                </div>
                <div style="position: relative;">
                    <div style="position: absolute; left: -21px; top: 4px; width: 12px; height: 12px; border-radius: 50%; background: #2563eb; border: 2px solid white;"></div>
                    <div style="font-size: 0.8rem; font-weight: 600; color: #1e293b;">Estado Actual</div>
                    <div style="font-size: 0.75rem; color: #2563eb;">{ticket.get('status', ticket.get('estado'))}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.subheader("Gestión")
            st.caption("Actualice el estado y comuníquese con el vecino.")
            
            # Show existing reply
            if ticket.get('reply'):
                with st.chat_message("assistant", avatar="🏛️"):
                    st.markdown(f"**Respuesta Municipal:**\n\n{ticket.get('reply')}")
            else:
                st.info("Sin respuesta registrada aún.")
            
            with st.form("ticket_update_form"):
                
                new_status = st.selectbox(
                    "Nuevo Estado", 
                    options=["Pendiente", "En Proceso", "En Revisión", "Resuelto", "Rechazado"],
                    index=["Pendiente", "En Proceso", "En Revisión", "Resuelto", "Rechazado"].index(ticket.get('status', getattr(ticket, 'estado', 'Pendiente'))) if ticket.get('status') in ["Pendiente", "En Proceso", "En Revisión", "Resuelto", "Rechazado"] else 0
                )
                
                new_urgency = st.selectbox(
                    "Nivel de Urgencia",
                    options=["Baja", "Media", "Alta", "Crítica"],
                    index=["Baja", "Media", "Alta", "Crítica"].index(ticket.get('urgency', getattr(ticket, 'urgencia', 'Baja'))) if ticket.get('urgency') in ["Baja", "Media", "Alta", "Crítica"] else 0
                )
                
                reply_text = st.text_area("Respuesta al Vecino", value=ticket.get('reply', ''), height=200, placeholder="Escriba aquí la respuesta oficial que verá el vecino...")
                
                submitted = st.form_submit_button("Guardar Cambios", type="primary")
                
                if submitted:
                    with st.spinner("Guardando..."):
                        try:
                            update_ticket(ticket.get('id'), {
                                'status': new_status, 
                                'urgency': new_urgency,
                                'reply': reply_text
                            })
                            st.success("¡Ticket actualizado!")
                            time.sleep(1)
                            st.session_state.selected_ticket_id = None
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error al actualizar: {e}")
                            
            # Delete Section
            st.markdown("---")
            st.caption("Zona de Peligro")
            if st.button("🗑️ Eliminar Solicitud", type="primary", help="Esta acción no se puede deshacer."):
                from modules.db import delete_ticket
                if delete_ticket(ticket.get('id')):
                    st.success("Solicitud eliminada.")
                    time.sleep(1)
                    st.session_state.selected_ticket_id = None
                    st.rerun()
                else:
                    st.error("No se pudo eliminar.")
