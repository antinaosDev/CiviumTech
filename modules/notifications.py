import asyncio
from notificationapi_python_server_sdk import notificationapi
from modules import db
import streamlit as st
import datetime

def _init_api():
    # Get credentials from secrets
    try:
        if "global" in st.secrets and "NOTIFICATIONAPI" in st.secrets["global"]:
             client_id = st.secrets["global"]["NOTIFICATIONAPI"]["CLIENT_ID"]
             client_secret = st.secrets["global"]["NOTIFICATIONAPI"]["CLIENT_SECRET"]
        elif "NOTIFICATIONAPI" in st.secrets:
             client_id = st.secrets["NOTIFICATIONAPI"]["CLIENT_ID"]
             client_secret = st.secrets["NOTIFICATIONAPI"]["CLIENT_SECRET"]
        else:
             return False
    except:
        return False
    
    if client_id and client_secret:
        notificationapi.init(client_id, client_secret)
        return True
    return False

async def _send_async(user_email, subject, message):
    try:
        await notificationapi.send({
            "notificationId": "generic_alert", 
            "user": {
                "id": user_email,
                "email": user_email
            },
            "email": {
                "subject": subject,
                "html": message
            }
        })
        return True
    except Exception as e:
        print(f"DEBUG: Async Send Error: {e}")
        return False

def send_notification(user_email, subject, message):
    """
    Sends a notification via Email (NotificationAPI).
    """
    if not user_email:
        return False

    if _init_api():
        try:
            # Send
            asyncio.run(_send_async(user_email, subject, message))
            return True
        except Exception as e:
            print(f"Sync Wrapper Error: {e}")
            return False
    else:
        # Silently fail if API not configured
        return False

# --- Templates ---
def _tpl_ticket_alert(ticket_id, citizen, days_open, urgency):
    color = "#dc2626" if urgency == "Crítica" else "#e67e22"
    return f"""
    <div style="font-family: sans-serif; padding: 20px; border: 1px solid #e2e8f0; border-radius: 8px;">
        <h2 style="color: {color};">⚠️ Solicitud Pendiente ({urgency})</h2>
        <p>La solicitud <strong>#{ticket_id}</strong> de {citizen} lleva {days_open} días abierta.</p>
        <ul>
            <li><strong>ID:</strong> {ticket_id}</li>
            <li><strong>Ciudadano:</strong> {citizen}</li>
            <li><strong>Días Transcurridos:</strong> {days_open}</li>
        </ul>
        <p style="color: #64748b; font-size: 14px;">Por favor ingrese al portal para gestionar.</p>
        <hr>
        <small>Notificación Automática - CiviumTech</small>
    </div>
    """

# --- Automation ---
def check_and_notify_overdue_tickets():
    """
    Checks for tickets pending for more than 7 days (or 3 if Critical).
    Sends alerts to Admins.
    """
    if not _init_api():
        return "API no configurada."

    # Fetch active tickets from DB
    tickets = db.fetch_tickets(filters={'estado': 'Pendiente'}, limit=100)
    if not tickets:
        return "No hay tickets pendientes."

    # Get Admins
    # We don't have a direct get_admins function in db.py yet, assuming 'admin@cholchol.cl' or loop users
    # For now, let's hardcode the recipient or look for ADMIN role if we implemented get_users
    # Implementation Plan: just target a specific configurable email or the current user if they are admin? 
    # Automation usually runs on server. We'll target a hardcoded admin email for now or skip if no users table access.
    # CiviumTech DB has users table.
    
    target_email = "alain.antinao.s@gmail.com" # Default dev email for testing 
    
    sent_count = 0
    now = datetime.datetime.now().date()
    
    for t in tickets:
        # Check date
        try:
            created_at = datetime.datetime.strptime(t['created_at'].split("T")[0], '%Y-%m-%d').date()
            days_open = (now - created_at).days
            
            urgency = t.get('urgencia', 'Media')
            threshold = 3 if urgency == 'Crítica' else 7
            
            if days_open >= threshold:
                # Send Alert
                # Idempotency check? We rely on daily run.
                subject = f"⚠️ Solicitud #{t['id']} Atrasada ({days_open} días)"
                msg = _tpl_ticket_alert(t['id'], t.get('ciudadano_nombre', 'Vecino'), days_open, urgency)
                
                if send_notification(target_email, subject, msg):
                    sent_count += 1
        except:
            continue
            
    return f"Se enviaron {sent_count} alertas."

def run_daily_automation():
    """
    Daily check for overdue tickets.
    """
    try:
        today_str = datetime.datetime.now().strftime('%Y-%m-%d')
        # We need a place to store 'last_run'. usage of session_state is ephemeral.
        # Ideally DB config table. For now, we use a simple st.cache_resource hack or just run on login (idempotent locally)
        # We'll use a session state marker to avoid running on every rerun of the script for the same session.
        
        if 'last_notification_check' not in st.session_state:
            st.session_state['last_notification_check'] = None
            
        if st.session_state['last_notification_check'] != today_str:
            print(f"Running Daily Check for {today_str}...")
            res = check_and_notify_overdue_tickets()
            print(f"Notification Result: {res}")
            st.session_state['last_notification_check'] = today_str
            return True
            
        return False
    except Exception as e:
        print(f"Auto Error: {e}")
        return False
