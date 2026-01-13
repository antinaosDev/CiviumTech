import smtplib
from email.message import EmailMessage
import streamlit as st

def send_simple_email(to_email, subject, body, pdf_bytes=None, pdf_filename="documento.pdf"):
    """
    Sends an email using credentials from st.secrets['email'].
    If credentials are missing, returns False (Simulated Mode).
    """
    # 1. Check for credentials
    email_creds = st.secrets.get("email")
    if not email_creds:
        return False
    
    smtp_server = email_creds.get("smtp_server")
    smtp_port = email_creds.get("smtp_port")
    sender_email = email_creds.get("sender_email")
    sender_password = email_creds.get("sender_password")
    
    if not (smtp_server and smtp_port and sender_email and sender_password):
        return False

    # 2. Construct Message
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = to_email
    msg.set_content(body)

    # 3. Attach PDF if provided
    if pdf_bytes:
        msg.add_attachment(pdf_bytes, maintype='application', subtype='pdf', filename=pdf_filename)

    # 4. Send
    try:
        # Add timeout to avoid hanging (5 seconds)
        with smtplib.SMTP(smtp_server, smtp_port, timeout=5) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False
