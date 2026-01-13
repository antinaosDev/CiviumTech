from fpdf import FPDF
from datetime import datetime
import pandas as pd
import tempfile
from modules.ui import UNIDADES, PATH_LOGO_APP, PATH_LOGO_DEV, PATH_LOGO_MUNI

class PDFReport(FPDF):
    def header(self):
        # 1. Branding Stripe
        self.set_fill_color(30, 58, 138) # Dark Blue
        self.rect(0, 0, 210, 20, 'F')
        
        # 2. Logos
        try:
            # Muni Logo (Left, over blue)
            if PATH_LOGO_MUNI:
                self.image(PATH_LOGO_MUNI, 10, 4, 12)
            
            # App/Dev Logo (Right, over blue)
            if PATH_LOGO_DEV:
                self.image(PATH_LOGO_DEV, 190, 4, 12)
        except:
            pass
            
        # 3. Title White
        self.set_font('Arial', 'B', 14)
        self.set_text_color(255, 255, 255)
        self.set_y(6)
        self.cell(0, 8, 'REPORTE DE GESTIÓN MUNICIPAL', 0, 1, 'C')
        
        # 4. Subtitle White
        self.set_font('Arial', '', 9)
        self.set_text_color(200, 200, 200)
        self.cell(0, 5, f'Generado el: {datetime.now().strftime("%d-%m-%Y %H:%M")}', 0, 1, 'C')
        self.ln(15)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(128)
        self.cell(0, 10, f'CiviumTech - Página {self.page_no()}', 0, 0, 'C')

    def draw_kpi_card(self, x, y, w, h, title, value, color_rgb):
        # Card Background
        self.set_fill_color(255, 255, 255)
        self.set_draw_color(220, 220, 220)
        self.rect(x, y, w, h, 'DF')
        
        # Top Border Color
        self.set_fill_color(*color_rgb)
        self.rect(x, y, w, 2, 'F')
        
        # Title
        self.set_xy(x, y + 5)
        self.set_font('Arial', 'B', 8)
        self.set_text_color(100, 100, 100)
        self.cell(w, 5, title, 0, 1, 'C')
        
        # Value
        self.set_xy(x, y + 12)
        self.set_font('Arial', 'B', 16)
        self.set_text_color(30, 41, 59)
        self.cell(w, 10, str(value), 0, 1, 'C')

def generate_pdf_report(tickets_data):
    """
    Generate a Professional PDF report with KPIs and Charts.
    """
    pdf = PDFReport()
    pdf.alias_nb_pages()
    pdf.add_page()
    
    # --- DATA PREP ---
    df = pd.DataFrame(tickets_data)
    total = len(df)
    
    if total == 0:
        pdf.set_font('Arial', '', 12)
        pdf.set_text_color(0)
        pdf.cell(0, 10, 'No hay datos disponibles para el reporte.', 0, 1)
        return pdf.output(dest='S').encode('latin-1')

    criticos = len(df[df['urgencia'] == 'Crítica']) if 'urgencia' in df.columns else 0
    resueltos = len(df[df['status'].isin(['Resuelto', 'Cerrado'])]) if 'status' in df.columns else 0
    
    # --- 1. KPI SECTION ---
    pdf.set_font('Arial', 'B', 12)
    pdf.set_text_color(30, 58, 138)
    pdf.cell(0, 10, 'Resumen Ejecutivo', 0, 1)
    
    # Draw Cards (Total, Críticos, Resueltos)
    y_start = pdf.get_y()
    card_w = 60
    gap = 5
    
    pdf.draw_kpi_card(10, y_start, card_w, 30, "TOTAL SOLICITUDES", total, (59, 130, 246)) # Blue
    pdf.draw_kpi_card(10 + card_w + gap, y_start, card_w, 30, "CASOS CRÍTICOS", criticos, (239, 68, 68)) # Red
    pdf.draw_kpi_card(10 + (card_w + gap)*2, y_start, card_w, 30, "RESUELTOS", resueltos, (16, 185, 129)) # Green
    
    pdf.set_y(y_start + 35)
    
    # --- 2. CHART SECTION (Simple Bar Chart) ---
    pdf.set_font('Arial', 'B', 12)
    pdf.set_text_color(30, 58, 138)
    pdf.cell(0, 10, 'Distribución por Estado', 0, 1)
    
    if 'status' in df.columns:
        status_counts = df['status'].value_counts()
        bar_max_w = 120
        start_x = 40
        y_loc = pdf.get_y() + 5
        
        pdf.set_font('Arial', '', 9)
        pdf.set_text_color(0)
        
        for status, count in status_counts.head(5).items():
            # Label
            pdf.set_xy(10, y_loc)
            pdf.cell(25, 6, status, 0, 0, 'R')
            
            # Bar using Rect
            bar_w = (count / total) * bar_max_w
            
            # Color based on status
            if status == 'Pendiente': pdf.set_fill_color(253, 224, 71) # Yellow
            elif status == 'Resuelto': pdf.set_fill_color(134, 239, 172) # Green
            elif status == 'Crítica': pdf.set_fill_color(252, 165, 165) # Red
            else: pdf.set_fill_color(191, 219, 254) # Blue
            
            pdf.rect(start_x, y_loc, bar_w, 6, 'F')
            
            # Value Label
            pdf.set_xy(start_x + bar_w + 2, y_loc)
            pdf.cell(20, 6, f"{count}", 0, 0)
            
            y_loc += 8
            
        pdf.set_y(y_loc + 10)
    
    # --- 3. DETAILED TABLE ---
    pdf.set_font('Arial', 'B', 12)
    pdf.set_text_color(30, 58, 138)
    pdf.cell(0, 10, 'Detalle de Últimos Registros', 0, 1)
    
    # Header
    pdf.set_fill_color(30, 58, 138) # Dark Blue
    pdf.set_text_color(255, 255, 255)
    pdf.set_font('Arial', 'B', 8)
    
    # Cols: ID (25), Fecha (20), Unidad (50), Estado (25), Asunto (70)
    pdf.cell(25, 8, 'ID', 1, 0, 'C', 1)
    pdf.cell(20, 8, 'Fecha', 1, 0, 'C', 1)
    pdf.cell(50, 8, 'Unidad', 1, 0, 'C', 1)
    pdf.cell(25, 8, 'Estado', 1, 0, 'C', 1)
    pdf.cell(70, 8, 'Asunto', 1, 0, 'C', 1)
    pdf.ln()
    
    # Rows
    pdf.set_font('Arial', '', 8)
    pdf.set_text_color(0)
    fill = False
    
    for i, row in df.head(50).iterrows(): # Limit to 50 for performance in detailed report
        id_ = str(row.get('id', ''))[:8]
        # Use created_at or fecha, handle datetime objects
        raw_date = row.get('created_at', row.get('fecha'))
        if isinstance(raw_date, (pd.Timestamp, datetime)):
            date_ = raw_date.strftime("%Y-%m-%d")
        else:
             date_ = str(raw_date)[:10]

        dept_code = row.get('depto', '')
        unit = UNIDADES.get(dept_code, {}).get('label', dept_code)[:30]
        status = row.get('status', row.get('estado', ''))
        subject = row.get('subject', row.get('sub', ''))[:45]
        
        # Zebra Striping
        if fill:
            pdf.set_fill_color(241, 245, 249) # Slate 100
        else:
            pdf.set_fill_color(255, 255, 255)
            
        pdf.cell(25, 6, id_, 1, 0, 'C', 1)
        pdf.cell(20, 6, date_, 1, 0, 'C', 1)
        pdf.cell(50, 6, unit, 1, 0, 'L', 1)
        pdf.cell(25, 6, status, 1, 0, 'C', 1)
        pdf.cell(70, 6, subject, 1, 0, 'L', 1)
        pdf.ln()
        fill = not fill

    # Finish
    try:
        tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        pdf.output(tmp_file.name)
        with open(tmp_file.name, "rb") as f:
            pdf_bytes = f.read()
        return pdf_bytes
    except Exception as e:
        print(f"Error generating PDF: {e}")
        return None

def generate_ticket_receipt_pdf(ticket_data):
    """
    Generates a single-page PDF receipt for a citizen's ticket.
    """
    pdf = PDFReport()
    pdf.alias_nb_pages()
    pdf.add_page()
    
    # Title
    pdf.set_font('Arial', 'B', 16)
    pdf.set_text_color(37, 99, 235) # Blue
    pdf.cell(0, 10, 'Comprobante de Solicitud', 0, 1, 'C')
    pdf.ln(10)
    
    # Ticket ID
    pdf.set_font('Arial', '', 10)
    pdf.set_text_color(0)
    pdf.cell(0, 8, 'Su número de seguimiento es:', 0, 1, 'C')
    
    pdf.set_font('Courier', 'B', 24)
    pdf.set_text_color(30, 41, 59) # Dark Slate
    pdf.cell(0, 15, ticket_data.get('id', 'N/A'), 0, 1, 'C')
    pdf.ln(5)
    
    # Details Box
    pdf.set_font('Arial', 'B', 12)
    pdf.set_text_color(0)
    pdf.cell(0, 10, 'Detalle del Requerimiento', 0, 1)
    
    # Helper to print fields
    def print_field(label, value):
        pdf.set_font('Arial', 'B', 10)
        pdf.set_text_color(100)
        pdf.cell(50, 8, label, 0, 0)
        pdf.set_font('Arial', '', 10)
        pdf.set_text_color(0)
        # Fixed width layout: Label (50) + Value (140) = 190 (fits in 210 with 10mm margins)
        try:
            # Save x,y
            x = pdf.get_x()
            y = pdf.get_y()
            
            # Align check
            # pdf.set_xy(x, y) # already there
            
            pdf.multi_cell(140, 8, val_str)
        except:
             pdf.cell(140, 8, val_str, ln=1)
        
    print_field("Fecha:", ticket_data.get('created_at', '').split('T')[0] if ticket_data.get('created_at') else ticket_data.get('fecha', '-'))
    print_field("Departamento:", UNIDADES.get(ticket_data.get('depto'), {}).get('label', ticket_data.get('depto')))
    print_field("Clasificación:", ticket_data.get('category', ticket_data.get('categoria', '-')))
    print_field("Asunto:", ticket_data.get('subject', ticket_data.get('sub', '-')))
    pdf.ln(5)
    
    pdf.set_font('Arial', 'B', 10)
    pdf.set_text_color(100)
    pdf.cell(0, 8, "Descripción:", 0, 1)
    pdf.set_font('Arial', '', 10)
    pdf.set_text_color(0)
    desc_val = ticket_data.get('description', ticket_data.get('desc', ''))
    pdf.multi_cell(0, 6, desc_val if desc_val else "-")
    
    pdf.ln(20)
    pdf.set_font('Arial', 'I', 9)
    pdf.set_text_color(100)
    pdf.multi_cell(0, 6, "Se ha enviado un respaldo de esta solicitud a su correo electrónico (si fue proporcionado).\n\nPuede consultar el estado de este requerimiento en el Portal Vecino utilizando su número de seguimiento.", 0, 'C')

    try:
        tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        pdf.output(tmp_file.name)
        with open(tmp_file.name, "rb") as f:
            pdf_bytes = f.read()
        return pdf_bytes
    except Exception as e:
        print(f"Error generating Receipt PDF: {e}")
        return None
