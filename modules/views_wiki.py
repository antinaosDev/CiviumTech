import streamlit as st

def render_wiki_view():
    """
    Renders the Knowledge Base (Wiki) for internal staff.
    """
    st.markdown("## 📚 Base de Conocimiento (Wiki Interna)")
    st.caption("Repositorio central de protocolos, manuales y procedimientos de CiviumTech.")
    
    tab1, tab2, tab3 = st.tabs(["📘 Manual de Usuario", "⚡ Protocolos de Acción", "❓ Preguntas Frecuentes"])
    
    with tab1:
        st.markdown("""
        ### Manual de Plataforma
        
        **1. Gestión de Tickets**
        - Los tickets llegan al estado 'Pendiente'.
        - Use el botón **'Gestionar'** para cambiar estado o asignar prioridad.
        - **Cerrar tickets**: Requiere indicar la solución final.
        
        **2. Dashboard**
        - El panel principal se actualiza cada 5 minutos.
        - Use los filtros laterales para ver métricas por departamento.
        
        **3. Geolocalización**
        - Los mapas muestran puntos rojos (Alta urgencia) y azules (Baja/Media).
        """)
        
    with tab2:
        st.markdown("""
        ### Protocolos de Urgencia
        
        > [!IMPORTANT]
        > **Prioridad Crítica**: Contactar inmediatamente al departamento responsable.
        
        | Tipo de Incidente | Tiempo de Respuesta | Responsable |
        | :--- | :--- | :--- |
        | 🚑 Salud / Riesgo Vital | Inmediato (15 min) | Depto. Salud / SAPU |
        | 🌪️ Desastres Naturales | 1 hora | DIDECO / Emergencias |
        | 💡 Corte de Suministro | 4 horas | Servicios Generales |
        
        #### Flujo de Escalabilidad
        1. **Recepción**: Operador valida la solicitud.
        2. **Asignación**: Se deriva al departamento (automático si el vecino lo selecciona).
        3. **Acción**: Cuadrilla en terreno resuelve.
        4. **Cierre**: Se sube foto de evidencia y se notifica al vecino.
        """)
        
    with tab3:
        st.expander("¿Cómo restablezco mi contraseña?").write("Contacte al Administrador del sistema (Programador).")
        st.expander("¿Puedo eliminar un ticket?").write("Solo los Administradores pueden eliminar tickets definitivamente.")
        st.expander("¿Los vecinos ven mis comentarios internos?").write("No, el campo 'Bitácora Interna' es privado para funcionarios.")
