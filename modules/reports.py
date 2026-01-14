from fpdf import FPDF
from datetime import datetime
import pandas as pd
import tempfile
from modules.ui import UNIDADES, PATH_LOGO_APP, PATH_LOGO_DEV, PATH_LOGO_MUNI

class PDFReport(FPDF):
    def header(self):
        # 1. Branding Stripe
        self.set_fill_color(30, 58, 138) # Dark Blue Primary
        self.rect(0, 0, 210, 22, 'F')
        
        # 2. Logos (Safe drawing)
        try:
            if PATH_LOGO_MUNI:
                self.image(PATH_LOGO_MUNI, 12, 4, 14)
            if PATH_LOGO_DEV:
                self.image(PATH_LOGO_DEV, 190, 4, 14)
        except: pass
            
        # 3. Title White
        self.set_font('Arial', 'B', 16)
        self.set_text_color(255, 255, 255)
        self.set_y(5)
        self.cell(0, 8, 'REPORTE DE GESTIÓN MUNICIPAL', 0, 1, 'C')
        
        # 4. Subtitle White
        self.set_font('Arial', '', 10)
        self.set_text_color(220, 220, 220)
        self.cell(0, 6, f'Generado el: {datetime.now().strftime("%d-%m-%Y %H:%M")}', 0, 1, 'C')
        self.ln(12)

    def footer(self):
        self.set_y(-12)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(100)
        self.cell(0, 10, f'CiviumTech - Inteligencia de Datos - Página {self.page_no()}', 0, 0, 'C')

    def chapter_title(self, title):
        self.set_font('Arial', 'B', 14)
        self.set_text_color(30, 58, 138)
        self.cell(0, 8, title, 0, 1, 'L')
        self.set_line_width(0.5)
        self.set_draw_color(30, 58, 138)
        self.line(self.get_x(), self.get_y(), 200, self.get_y())
        self.ln(4)

    def draw_kpi_card(self, x, y, w, h, title, value, subtext, color_rgb):
        # Card Background
        self.set_fill_color(255, 255, 255)
        self.set_draw_color(230, 230, 230)
        self.rect(x, y, w, h, 'DF')
        
        # Top Accent
        self.set_fill_color(*color_rgb)
        self.rect(x, y, w, 2.5, 'F')
        
        # Value
        self.set_xy(x, y + 8)
        self.set_font('Arial', 'B', 20)
        self.set_text_color(30, 41, 59)
        self.cell(w, 8, str(value), 0, 1, 'C')
        
        # Title
        self.set_xy(x, y + 17)
        self.set_font('Arial', 'B', 8)
        self.set_text_color(100)
        self.cell(w, 4, title.upper(), 0, 1, 'C')
        
        # Subtext
        if subtext:
            self.set_xy(x, y + 22)
            self.set_font('Arial', '', 7)
            self.set_text_color(120)
            self.cell(w, 4, subtext, 0, 1, 'C')

    def draw_horizontal_bar_chart(self, x_start, y_start, data_dict, title, bar_color):
        """Draws top categories horizontal bars."""
        self.set_xy(x_start, y_start)
        self.set_font('Arial', 'B', 10)
        self.set_text_color(50)
        self.cell(0, 6, title, 0, 1)
        
        y = y_start + 8
        max_w = 90
        
        max_val = max(data_dict.values()) if data_dict else 1
        
        self.set_font('Arial', '', 8)
        for label, val in data_dict.items():
            self.set_xy(x_start, y)
            
            # Truncate label
            clean_label = label[:25] + "..." if len(label) > 25 else label
            self.set_text_color(70)
            self.cell(40, 5, clean_label, 0, 0)
            
            # Bar
            bar_w = (val / max_val) * max_w
            self.set_fill_color(*bar_color)
            self.rect(x_start + 40, y + 1, bar_w, 3, 'F')
            
            # Value
            self.set_xy(x_start + 40 + bar_w + 2, y)
            self.set_text_color(0)
            self.cell(15, 5, str(val), 0, 1)
            
            y += 6

    def draw_urgency_dist(self, x, y, urgency_counts, total):
        self.set_xy(x, y)
        self.set_font('Arial', 'B', 10)
        self.set_text_color(50)
        self.cell(0, 6, "Distribución por Urgencia", 0, 1)
        
        # Define Colors
        colors = {
            'Baja': (34, 197, 94),   # Green
            'Media': (245, 158, 11), # Orange
            'Alta': (249, 115, 22),  # Deep Orange
            'Crítica': (239, 68, 68) # Red
        }
        
        # Draw as stacked bar for simplicity & elegance
        bar_w = 80
        bar_h = 10
        cur_x = x
        bar_y = y + 10
        
        # Determine parts
        sorted_keys = ['Baja', 'Media', 'Alta', 'Crítica']
        
        # Draw base background
        self.set_fill_color(241, 245, 249)
        self.rect(x, bar_y, bar_w, bar_h, 'F')
        
        legend_y = bar_y + 15
        
        for k in sorted_keys:
            val = urgency_counts.get(k, 0)
            if val > 0:
                part_w = (val / total) * bar_w
                col = colors.get(k, (200, 200, 200))
                self.set_fill_color(*col)
                self.rect(cur_x, bar_y, part_w, bar_h, 'F')
                
                # Legend Item
                self.set_xy(x, legend_y)
                self.rect(x, legend_y + 1, 3, 3, 'F')
                self.set_xy(x + 4, legend_y)
                self.set_font('Arial', '', 8)
                self.set_text_color(80)
                pct = int((val/total)*100)
                self.cell(20, 5, f"{k} ({val} - {pct}%)", 0, 0)
                
                cur_x += part_w
                legend_y += 5

def generate_pdf_report(tickets_data):
    """
    Generate Advanced PDF report.
    """
    pdf = PDFReport()
    pdf.alias_nb_pages()
    pdf.add_page()
    
    # Prep Data
    df = pd.DataFrame(tickets_data)
    total = len(df)
    
    if total == 0:
        pdf.cell(0, 10, 'No data', 0, 1)
        return pdf.output(dest='S').encode('latin-1')

    # Metrics
    criticos = len(df[df['urgency'].isin(['Crítica', 'Critica', 'CRITICA', 'Critical'])]) if 'urgency' in df.columns else 0
    closed = len(df[df['status'].isin(['Resuelto', 'Cerrado'])]) if 'status' in df.columns else 0
    res_rate = int((closed/total)*100) if total > 0 else 0
    
    # Top Depts
    depto_counts = {}
    if 'depto' in df.columns:
        counts = df['depto'].value_counts().head(5)
        for code, count in counts.items():
             label = UNIDADES.get(code, {}).get('label', code)
             depto_counts[label] = count
             
    # Urgency Counts
    urgency_counts = {'Baja': 0, 'Media': 0, 'Alta': 0, 'Crítica': 0}
    if 'urgency' in df.columns:
        vc = df['urgency'].value_counts()
        for k, v in vc.items():
            # Normalize key
            k_norm = k.capitalize()
            if k_norm in urgency_counts:
                urgency_counts[k_norm] += v
            if k_norm == 'Critica': urgency_counts['Crítica'] += v

    # --- PAGE 1: EXECUTIVE SUMMARY ---
    pdf.chapter_title("RESUMEN EJECUTIVO")
    
    # 3 Big Cards
    y_start = pdf.get_y()
    card_gap = 6
    avail_w = 190
    card_w = (avail_w - (card_gap * 2)) / 3
    
    pdf.draw_kpi_card(10, y_start, card_w, 30, "Total Solicitudes", total, "Mes Actual", (59, 130, 246))
    pdf.draw_kpi_card(10 + card_w + card_gap, y_start, card_w, 30, "Tasa Resolución", f"{res_rate}%", f"{closed} Resueltos", (16, 185, 129))
    pdf.draw_kpi_card(10 + (card_w + card_gap)*2, y_start, card_w, 30, "Casos Críticos", criticos, "Requieren Intervención", (239, 68, 68))
    
    pdf.set_y(y_start + 35)
    pdf.ln(5)

    # Charts Row
    y_charts = pdf.get_y()
    
    # Left: Top Depts
    pdf.draw_horizontal_bar_chart(10, y_charts, depto_counts, "Áreas Más Demandadas", (96, 165, 250))
    
    # Right: Urgency Distribution
    pdf.draw_urgency_dist(110, y_charts, urgency_counts, total)
    
    pdf.set_y(y_charts + 50)
    
    # Watchlist Critical
    pdf.ln(5)
    pdf.set_font('Arial', 'B', 12)
    pdf.set_text_color(185, 28, 28) # Red Text
    pdf.cell(0, 10, "⚠️ WATCHLIST: CASOS CRÍTICOS PENDIENTES", 0, 1)
    
    # Filter critical pending
    crit_pending = df[
        (df['urgency'].isin(['Crítica', 'Critica', 'CRITICA'])) & 
        (~df['status'].isin(['Resuelto', 'Cerrado']))
    ].head(5)
    
    if not crit_pending.empty:
        pdf.set_font('Arial', 'B', 8)
        pdf.set_fill_color(254, 226, 226) # Red 100
        pdf.set_text_color(0)
        pdf.cell(20, 6, "ID", 1, 0, 'C', 1)
        pdf.cell(30, 6, "Fecha", 1, 0, 'C', 1)
        pdf.cell(40, 6, "Unidad", 1, 0, 'C', 1)
        pdf.cell(100, 6, "Asunto", 1, 1, 'C', 1)
        
        pdf.set_font('Arial', '', 8)
        for _, row in crit_pending.iterrows():
            id_ = str(row.get('id', ''))[:8]
            date_ = str(row.get('date_str', row.get('created_at', '')))[:10]
            dept = UNIDADES.get(row.get('depto'), {}).get('label',  row.get('depto', ''))[:20]
            subj = row.get('subject', row.get('sub', ''))[:60]
            
            pdf.cell(20, 6, id_, 1, 0, 'C')
            pdf.cell(30, 6, date_, 1, 0, 'C')
            pdf.cell(40, 6, dept, 1, 0, 'L')
            pdf.cell(100, 6, subj, 1, 1, 'L')
    else:
        pdf.set_font('Arial', 'I', 10)
        pdf.set_text_color(22, 101, 52)
        pdf.cell(0, 10, "¡Excelente! No hay casos críticos pendientes.", 0, 1)

    # --- PAGE 2: DETAILED REGISTRY ---
    pdf.add_page()
    pdf.chapter_title("DETALLE DE REGISTROS (ÚLTIMOS 100)")
    
    # Header
    pdf.set_font('Arial', 'B', 7)
    pdf.set_fill_color(241, 245, 249)
    pdf.set_text_color(71, 85, 105) # Slate 600
    
    # Cols: ID(15), Fecha(20), Hora(15), Urg(15), Unidad(35), Asunto(65), Estado(25)
    # Total = 190
    h = 7
    pdf.cell(15, h, "ID", 1, 0, 'C', 1)
    pdf.cell(20, h, "FECHA", 1, 0, 'C', 1)
    pdf.cell(15, h, "HORA", 1, 0, 'C', 1)
    pdf.cell(15, h, "URG", 1, 0, 'C', 1)
    pdf.cell(35, h, "UNIDAD", 1, 0, 'C', 1)
    pdf.cell(65, h, "ASUNTO", 1, 0, 'C', 1)
    pdf.cell(25, h, "ESTADO", 1, 1, 'C', 1)
    
    pdf.set_font('Arial', '', 7)
    pdf.set_text_color(0)
    
    fill = False
    for _, row in df.head(100).iterrows():
        # Zebra
        if fill: pdf.set_fill_color(248, 250, 252)
        else: pdf.set_fill_color(255, 255, 255)
        
        id_ = str(row.get('id', ''))[:6]
        
        dt_raw = row.get('created_at')
        if isinstance(dt_raw, str):
            try: dt = datetime.fromisoformat(dt_raw.replace('Z','')) 
            except: dt = datetime.now()
        else: dt = dt_raw if dt_raw else datetime.now()
        
        date_ = dt.strftime("%Y-%m-%d")
        time_ = dt.strftime("%H:%M")
        
        urg = row.get('urgency', '')
        dept = UNIDADES.get(row.get('depto'), {}).get('label', row.get('depto', ''))[:20]
        subj = row.get('subject', row.get('sub', ''))[:40]
        stat = row.get('status', '')
        
        pdf.cell(15, 6, id_, 1, 0, 'C', 1)
        pdf.cell(20, 6, date_, 1, 0, 'C', 1)
        pdf.cell(15, 6, time_, 1, 0, 'C', 1)
        pdf.cell(15, 6, urg, 1, 0, 'C', 1)
        pdf.cell(35, 6, dept, 1, 0, 'L', 1)
        pdf.cell(65, 6, subj, 1, 0, 'L', 1)
        pdf.cell(25, 6, stat, 1, 1, 'C', 1)
        
        fill = not fill

    try:
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        pdf.output(tmp.name)
        with open(tmp.name, "rb") as f:
            return f.read()
    except Exception as e:
        print(f"Error: {e}")
        return None

def generate_ticket_receipt_pdf(ticket_data):
    """Simple Receipt PDF - Preserved from v1 but updated"""
    # ... (Reusing logic but ensuring simple receipt works)
    # Simplify: Just call the previous logic logic or inline simple one?
    # For speed, I'll reimplement a clean simple one here.
    pdf = PDFReport()
    pdf.add_page()
    pdf.chapter_title("COMPROBANTE DE SOLICITUD")
    
    pdf.set_font("Arial", "", 12)
    pdf.set_text_color(0)
    
    pdf.cell(0, 10, f"Folio: {str(ticket_data.get('id'))[:8]}", 0, 1)
    
    fields = [
        ("Fecha", ticket_data.get('created_at', '')[:10]),
        ("Unidad", UNIDADES.get(ticket_data.get('depto'), {}).get('label')),
        ("Asunto", ticket_data.get('subject', ticket_data.get('sub'))),
        ("Estado", "Recibido"),
    ]
    
    for k, v in fields:
        pdf.set_font("Arial", "B", 10)
        pdf.cell(40, 8, k + ":", 0, 0)
        pdf.set_font("Arial", "", 10)
        pdf.cell(0, 8, str(v), 0, 1)
        
    pdf.ln(10)
    pdf.set_font("Arial", "B", 10)
    pdf.cell(0, 8, "Descripción:", 0, 1)
    pdf.set_font("Arial", "", 10)
    desc = ticket_data.get('description', ticket_data.get('desc', ''))
    pdf.multi_cell(0, 6, desc)
    
    try:
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        pdf.output(tmp.name)
        with open(tmp.name, "rb") as f:
            return f.read()
    except: return None
