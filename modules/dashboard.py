import streamlit as st
import re
import pandas as pd
import plotly.express as px
import time
from modules.ui import UNIDADES, PATH_LOGO_MUNI, PATH_LOGO_APP, get_img_as_base64
from modules.reports import generate_pdf_report

def render_mayor_dashboard(tickets_data):
    """
    Renderiza el Dashboard Analítico CiviumTech.
    """
    # 1. Header
    h_col1, h_col2 = st.columns([4, 1])
    with h_col1:
        c_logo, c_title = st.columns([1, 6])
        with c_logo:
            st.image(PATH_LOGO_APP, width=70)
        with c_title:
            st.markdown("""
                <h2 style="font-size: 1.5rem; font-weight: 800; color: #1e293b; margin: 0;">
                    📊 Inteligencia de Datos
                </h2>
                <p style="color: #64748b; font-size: 0.875rem; margin: 0;">Visión Panorámica de la Gestión Municipal</p>
            """, unsafe_allow_html=True)
    with h_col2:
        if tickets_data:
             st.markdown("<div style='height: 10px'></div>", unsafe_allow_html=True)
             # Optimization: Don't generate PDF on load. It's too slow.
             if st.button("📄 Generar Informe PDF"):
                 with st.spinner("Generando reporte..."):
                     pdf_bytes = generate_pdf_report(tickets_data)
                     if pdf_bytes:
                         st.download_button(
                            "⬇️ Descargar PDF", 
                            data=pdf_bytes, 
                            file_name="reporte_gestion.pdf", 
                            mime="application/pdf", 
                            key="btn_download_report" 
                         )

    # 2. Logic / Data Processing
    df = pd.DataFrame(tickets_data)
    if df.empty:
        st.warning("Sin datos para mostrar.")
        return

    total = len(df)
    
    # By default mock data has 'urgency' and 'estado'
    # DEBUG: Check actual values
    # st.write("DEBUG INFO:", df.columns.tolist())
    if 'urgency' in df.columns:
        # st.write("Urgency Values:", df['urgency'].unique())
        pass
        
    criticos = df[df['urgency'].isin(['Crítica', 'Critica', 'CRITICA', 'High', 'Critical'])].shape[0] if 'urgency' in df.columns else 0
    
    # Calculate Dept Counts
    if 'depto' in df.columns:
        dept_counts = df['depto'].value_counts()
        top_dept_code = dept_counts.idxmax() if not dept_counts.empty else ""
        top_dept_count = dept_counts.max() if not dept_counts.empty else 0
        top_dept_label = UNIDADES.get(top_dept_code, {}).get('label', top_dept_code)
    else:
        top_dept_label = "N/A"
        top_dept_count = 0

    # Ensure date column exists for trend analysis
    if 'created_at' in df.columns:
        df['created_at'] = pd.to_datetime(df['created_at'])
        df['date_str'] = df['created_at'].dt.date
    elif 'fecha' in df.columns: # Legacy fallback
         df['date_str'] = pd.to_datetime(df['fecha']).dt.date
         
    # Ensure category column
    if 'category' not in df.columns and 'categoria' in df.columns:
        df['category'] = df['categoria'] # Legacy fallback

    # 3. Kpi Cards
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        # Calculate Growth vs Last Month
        current_month = getattr(pd.Timestamp.now(), 'month')
        if 'created_at' in df.columns:
            this_month_count = df[df['created_at'].dt.month == current_month].shape[0]
            last_month_count = df[df['created_at'].dt.month == (current_month - 1)].shape[0]
            growth_pct = ((this_month_count - last_month_count) / last_month_count * 100) if last_month_count > 0 else 0
            growth_str = f"{growth_pct:+.1f}% vs mes anterior"
            growth_color = "#16a34a" if growth_pct >= 0 else "#dc2626"
        else:
            growth_str = "Datos insuficientes"
            growth_color = "#94a3b8"

        st.markdown(f"""
        <div class="civium-card" style="border-top: 4px solid #3b82f6;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                <span style="font-size: 0.75rem; font-weight: 700; color: #64748b; text-transform: uppercase;">Solicitudes Totales</span>
                <span style="font-size: 1.5rem;">📄</span>
            </div>
            <div style="font-size: 1.875rem; font-weight: 900; color: #1e293b;">{total}</div>
            <div style="font-size: 0.75rem; color: {growth_color}; font-weight: 700; margin-top: 0.25rem;">{growth_str}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with c2:
        st.markdown(f"""
        <div class="civium-card" style="border-top: 4px solid #ef4444; background-color: #fef2f2;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                <span style="font-size: 0.75rem; font-weight: 700; color: #dc2626; text-transform: uppercase;">Casos Críticos</span>
                <span style="font-size: 1.5rem;">⚠️</span>
            </div>
            <div style="font-size: 1.875rem; font-weight: 900; color: #b91c1c;">{criticos}</div>
            <div style="font-size: 0.75rem; color: #dc2626; margin-top: 0.25rem;">Requieren intervención hoy</div>
        </div>
        """, unsafe_allow_html=True)
        
    with c3:
        st.markdown(f"""
        <div class="civium-card" style="border-top: 4px solid #f59e0b;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                <span style="font-size: 0.75rem; font-weight: 700; color: #64748b; text-transform: uppercase;">Área Más Demandada</span>
                <span style="font-size: 1.5rem;">📈</span>
            </div>
            <div style="font-size: 1.25rem; font-weight: 800; color: #1e293b; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{top_dept_label}</div>
            <div style="font-size: 0.75rem; color: #64748b; margin-top: 0.25rem;">{top_dept_count} tickets activos</div>
        </div>
        """, unsafe_allow_html=True)
        
    with c4:
        # Calculate Resolution Rate
        if 'status' in df.columns:
            resolved_count = df[df['status'].isin(['Resuelto', 'Cerrado'])].shape[0]
            resolution_rate = (resolved_count / total * 100) if total > 0 else 0
        else:
            resolution_rate = 0
            
        st.markdown(f"""
        <div class="civium-card" style="border-top: 4px solid #a855f7;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                <span style="font-size: 0.75rem; font-weight: 700; color: #64748b; text-transform: uppercase;">Tasa de Resolución</span>
                <span style="font-size: 1.5rem;">✅</span>
            </div>
            <div style="font-size: 1.875rem; font-weight: 900; color: #1e293b;">{int(resolution_rate)}%</div>
            <div style="font-size: 0.75rem; color: #64748b; margin-top: 0.25rem;">Tickets Resueltos/Cerrados</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # 4. Main Charts Grid
    col_main, col_map = st.columns([2, 1])
    
    with col_main:
        with st.container():
            st.markdown("### 📊 Carga de Trabajo por Unidad")
            if 'depto' in df.columns:
                # Top 5
                top_5 = df['depto'].value_counts().head(5)
                # Create visual bars
                for code, count in top_5.items():
                    unit = UNIDADES.get(code, {'label': code, 'hex_bg': '#cbd5e1'})
                    pct = (count / total) * 100
                    
                    st.markdown(f"""
                    <div style="margin-bottom: 1.25rem;">
                        <div style="display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 0.5rem;">
                            <span style="font-size: 0.9rem; font-weight: 700; color: #1e293b;">{unit['label']}</span>
                            <span style="font-size: 0.85rem; font-weight: 600; color: #64748b;">{count} tickets <span style="color: #94a3b8; font-weight: 400;">({int(pct)}%)</span></span>
                        </div>
                        <div style="height: 0.75rem; background-color: #f1f5f9; border-radius: 9999px; overflow: hidden; box-shadow: inset 0 1px 2px rgba(0,0,0,0.05);">
                            <div style="height: 100%; width: {pct}%; background-color: {unit.get('hex_bg').replace('bg-', '')}; border-radius: 9999px; transition: width 1s ease-in-out;"></div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("Sin datos de departamentos.")
 
    with col_map:

        with st.container():
            st.markdown("""
            <div style="background-color: white; padding: 1.5rem; border-radius: 12px; border: 1px solid #e2e8f0; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);">
               <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 1rem;">
                   <span style="font-size: 1.5rem;">📍</span>
                   <div style="color: #1e293b !important; margin: 0; font-size: 1.1rem; font-weight: 700; font-family: 'Manrope', sans-serif;">Mapa de Calor</div>
               </div>
               <p style="color: #64748b; font-size: 0.85rem; margin: 0;">Visualización geoespacial de incidentes</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Extract Coordinates
            map_data = []
            for t in tickets_data:
                # Use dedicated columns if available
                lat = t.get('lat')
                lon = t.get('lon')
                
                if lat and lon:
                     map_data.append({'lat': float(lat), 'lon': float(lon)})
                else:
                    # Fallback to regex in description
                    desc = t.get('description', t.get('desc', ''))
                    if desc:
                        match = re.search(r'Coords: (-?\d+\.\d+), (-?\d+\.\d+)', desc)
                        if match:
                            try:
                                lat = float(match.group(1))
                                lon = float(match.group(2))
                                map_data.append({'lat': lat, 'lon': lon})
                            except: pass
            
            if map_data:
                st.map(pd.DataFrame(map_data), size=20, zoom=11)
                st.caption(f"Visualizando {len(map_data)} puntos críticos detectados.")
            else:
                st.info("Sin datos geoespaciales activos.")
                st.map(pd.DataFrame({'lat': [-38.6015], 'lon': [-72.9461]}), zoom=12)
                st.caption("Mapa centrado en Cholchol.")
                 
    st.markdown("---")
    
    # NEW: Advanced Analytics Section
    st.markdown("### 📈 Estudios y Tendencias (Data Science)")
    
    # Row 1: Time Series & Urgency Donut
    c_trend, c_urgency = st.columns([2, 1])
    
    with c_trend:
        if 'date_str' in df.columns:
            try:
                daily_counts = df.groupby('date_str').size().reset_index(name='count')
                fig_trend = px.area(
                    daily_counts, x='date_str', y='count',
                    title="Evolución de Solicitudes",
                    labels={'date_str': 'Fecha', 'count': 'Tickets'},
                    template="plotly_white"
                )
                fig_trend.update_traces(line_color='#2563eb', fillcolor='rgba(37, 99, 235, 0.2)')
                st.plotly_chart(fig_trend, use_container_width=True)
            except Exception as e:
                st.error(f"Error Tendencias: {e}")
        else:
            st.info("Sin datos de fechas.")
            
    with c_urgency:
        if 'urgency' in df.columns:
            urg_counts = df['urgency'].value_counts().reset_index()
            urg_counts.columns = ['urgency', 'count']
            
            # Custom colors for urgency
            color_map = {
                'Baja': '#22c55e', 'Media': '#f59e0b', 
                'Alta': '#f97316', 'Crítica': '#ef4444'
            }
            
            fig_urg = px.pie(
                urg_counts, names='urgency', values='count',
                title="Distribución de Urgencia",
                hole=0.6,
                template="plotly_white",
                color='urgency',
                color_discrete_map=color_map
            )
            st.plotly_chart(fig_urg, use_container_width=True)
        else:
            st.info("Sin datos de urgencia.")
            
    # Row 2: Heatmap & Categories
    c_heat, c_cat = st.columns([2, 1])
    
    with c_heat:
        # Temporal Heatmap (Day of Week vs Hour)
        if 'created_at' in df.columns:
            try:
                df['hour'] = df['created_at'].dt.hour
                df['day_name'] = df['created_at'].dt.day_name()
                
                # Translations
                spanish_days = {
                    'Monday': 'Lunes', 'Tuesday': 'Martes', 'Wednesday': 'Miércoles', 
                    'Thursday': 'Jueves', 'Friday': 'Viernes', 'Saturday': 'Sábado', 'Sunday': 'Domingo'
                }
                df['day_name'] = df['day_name'].map(spanish_days)
                
                # Order days
                days_order = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
                df['day_name'] = pd.Categorical(df['day_name'], categories=days_order, ordered=True)
                
                heatmap_data = df.groupby(['day_name', 'hour']).size().reset_index(name='count')
                
                fig_heat = px.density_heatmap(
                    heatmap_data, x='hour', y='day_name', z='count',
                    title="Mapa de Calor Temporal (Día vs Hora)",
                    labels={'hour': 'Hora del Día', 'day_name': 'Día', 'count': 'Tickets'},
                    template="plotly_white",
                    color_continuous_scale="Blues"
                )
                st.plotly_chart(fig_heat, use_container_width=True)
            except Exception as e:
                st.warning(f"No hay suficientes datos para heatmap: {e}")
        else:
            st.info("Sin datos de fechas para heatmap.") # Added info message for heatmap
                
    with c_cat:
        if 'category' in df.columns:
            cat_counts = df['category'].value_counts().reset_index()
            cat_counts.columns = ['category', 'count']
            
            fig_cat = px.pie(
                cat_counts, names='category', values='count',
                title="Categorías",
                template="plotly_white",
                color_discrete_sequence=px.colors.qualitative.Prism
            )
            fig_cat.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig_cat, use_container_width=True)
        else:
            st.info("Sin datos de categorías.")
