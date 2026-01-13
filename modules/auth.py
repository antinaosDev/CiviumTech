import streamlit as st
import bcrypt
import base64
import os
from modules import db

def hash_password(password):
    """Hashes a password for storage."""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def check_password(password, hashed):
    """Checks a password against a hash."""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def login_user(username, password):
    """Verifies credentials and logs the user in."""
    users = db.get_user_by_username(username)
    if users:
        user_row = users[0]
        # Verify hash
        # CAUTION: If user was manually inserted without hash in SQL, this might fail or we need to handle plain text legacy?
        # We assume all inserts go through our tools which use bcrypt or the initial seed which used a hash.
        try:
            stored_hash = user_row['password_hash']
            if check_password(password, stored_hash):
                st.session_state['authenticated'] = True
                st.session_state['user_role'] = user_row['role']
                st.session_state['real_role'] = user_row['role'] # For simulation
                st.session_state['username'] = user_row['username']
                st.session_state['full_name'] = user_row['full_name']
                st.session_state['user_id'] = user_row['id']
                st.session_state['email'] = user_row.get('email', '')
                st.session_state['department'] = user_row.get('department', '')
                return True
        except Exception as e:
            print(f"Login error: {e}")
    return False

def logout_user():
    """Clears session state."""
    keys = ['authenticated', 'user_role', 'real_role', 'username', 'full_name', 'user_id', 'email', 'department', 'simulated_role']
    for k in keys:
        if k in st.session_state:
            del st.session_state[k]
    st.rerun()

def check_auth():
    return st.session_state.get('authenticated', False)

def get_current_role():
    if 'simulated_role' in st.session_state:
        return st.session_state['simulated_role']
    return st.session_state.get('user_role', 'GUEST')

def get_real_role():
    return st.session_state.get('real_role', 'GUEST')

def render_login():
    """Renders the Premium Login UI (Restored Corporate Identity)."""
    # Load Logo
    logo_b64 = ""
    try:
        from modules.ui import get_img_as_base64
        # Try specific branding logos
        logo_b64 = get_img_as_base64("logo_muni.png") 
    except Exception as e:
        print(f"Error loading logo: {e}")

    # Layout - Two Columns with styling
    # Layout - Two Columns with styling
# --- HTML CONSTANTS (Redesigned) ---
def get_login_html(logo_b64):
    return f"""
    <div style="display: flex; min-height: 90vh; font-family: 'Manrope', sans-serif;">
        <!-- Left Column: Branding -->
        <div style="flex: 1; position: relative; background-image: url('https://images.unsplash.com/photo-1532104997193-87588e146dd9?ixlib=rb-4.0.3&auto=format&fit=crop&w=1500&q=80'); background-size: cover; background-position: center; border-radius: 0 40px 40px 0; overflow: hidden; display: flex; flex-direction: column; justify-content: flex-end; padding: 4rem;">
            <div style="position: absolute; inset: 0; background: linear-gradient(180deg, rgba(30,58,138,0.3) 0%, rgba(30,58,138,0.95) 100%);"></div>
            
            <div style="position: relative; z-index: 10; color: white;">
                <div style="margin-bottom: 2rem;">
                     <!-- Logo Optional Here -->
                </div>
                <h1 style="font-size: 3.5rem; font-weight: 800; line-height: 1.1; margin-bottom: 1rem;">
                    Gestión municipal <br> eficiente, cerca de ti.
                </h1>
                <p style="font-size: 1.25rem; font-weight: 500; opacity: 0.9; max-width: 500px;">
                    Conectamos la gestión pública con la comunidad. Accede a trámites, solicitudes y control en un solo lugar.
                </p>
                <div style="margin-top: 2rem; display: flex; gap: 1rem; opacity: 0.8;">
                     <span>CiviumTech Cholchol</span>
                </div>
            </div>
        </div>

        <!-- Right Column: Login Form Placeholder (Will be filled by Streamlit) -->
        <div style="width: 500px; padding: 2rem;"></div> 
    </div>
    """

def render_login():
    """Renders the CiviumTech Branding Login UI."""
    # Load Logo
    logo_b64 = ""
    muni_logo_b64 = ""
    try:
        from modules.ui import get_img_as_base64, PATH_LOGO_MUNI
        logo_b64 = get_img_as_base64("CiviumTech.png") 
        muni_logo_b64 = get_img_as_base64("logo_muni.png")
    except Exception as e:
        print(f"Error loading logo: {e}")

    # Layout using Columns to mimic the split roughly within Streamlit constraints
    
    st.markdown("""
        <style>
            [data-testid="stAppViewContainer"] { background-color: white; }
            [data-testid="stHeader"] { display: none; }
            /* Hide Sidebar on Login */
            [data-testid="stSidebar"] { display: none; }
        </style>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([1.5, 1], gap="large")

    with col1:
        # Visual Hero
        
        # Visual Hero
        
        # Aggressively stripped HTML to prevent Markdown code block detection
        html_hero = (
            '<div style="height: 90vh; background-image: url(\'https://images.unsplash.com/photo-1532104997193-87588e146dd9?ixlib=rb-4.0.3&auto=format&fit=crop&w=1500&q=80\'); background-size: cover; border-radius: 20px; position: relative; overflow: hidden; display: flex; flex-direction: column; justify-content: flex-end; padding: 3rem;">'
            '<div style="position: absolute; inset: 0; background: linear-gradient(180deg, rgba(30,58,138,0.2) 0%, rgba(30,58,138,0.9) 100%);"></div>'
            '<div style="position: relative; z-index: 10; color: white;">'
            '<div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 1rem;">'
            '<span style="font-weight: 800; font-size: 1.5rem; letter-spacing: -0.5px;">CiviumTech</span>'
            '</div>'
            '<h1 style="font-size: 3rem; font-weight: 800; line-height: 1.1; margin-bottom: 1rem; color: white;">Gestión municipal <br> eficiente, cerca de ti.</h1>'
            '<p style="font-size: 1.1rem; opacity: 0.9; margin-bottom: 2rem;">Plataforma integral de gestión municipal, atención ciudadana y control de activos.</p>'
            '<!-- Operator Info -->'
            '<div style="display: flex; align-items: center; gap: 1rem; padding-top: 1rem; border-top: 1px solid rgba(255,255,255,0.2);">'
            + (f'<img src="data:image/png;base64,{muni_logo_b64}" style="height: 50px; width: auto; background: white; padding: 4px; border-radius: 6px;">' if muni_logo_b64 else '') +
            '<div>'
            '<div style="font-size: 0.75rem; text-transform: uppercase; letter-spacing: 1px; opacity: 0.8;">Operado por</div>'
            '<div style="font-weight: 700; font-size: 1rem;">Ilustre Municipalidad de Cholchol</div>'
            '</div>'
            '</div>'
            '</div>'
            '</div>'
        )
        st.markdown(html_hero, unsafe_allow_html=True)

    with col2:
        st.markdown('<div style="height: 10vh;"></div>', unsafe_allow_html=True)
        with st.container():
            # Logo & Greeting
            st.markdown(f"""
            <div style="margin-bottom: 2rem;">
                <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                    {'<img src="data:image/png;base64,' + logo_b64 + '" style="height: 60px; width: auto; margin-bottom: 1.5rem;">' if logo_b64 else ''}
                </div>
                <h2 style="font-size: 2.5rem; font-weight: 800; color: #1e293b; margin-bottom: 0.5rem; font-family: 'Manrope', sans-serif;">Bienvenido</h2>
                <p style="color: #64748b; font-size: 1.1rem;">Selecciona tu perfil para ingresar</p>
            </div>
            """, unsafe_allow_html=True)

            # Tabs for intuitiveness
            tab_func, tab_vecino = st.tabs(["🏛️ Funcionarios", "🏡 Portal Vecino"])

            with tab_func:
                st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)
                with st.form("login_form_func", border=False):
                    st.markdown("##### 🔐 Acceso Corporativo")
                    st.caption("Ingrese sus credenciales municipales")
                    username = st.text_input("Usuario", placeholder="ej. 12.345.678-9", key="user_func")
                    password = st.text_input("Contraseña", type="password", placeholder="••••••••", key="pass_func")
                    
                    st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
                    
                    if st.form_submit_button("Iniciar Sesión", type="primary", use_container_width=True):
                         if login_user(username, password):
                            st.success("¡Bienvenido!")
                            st.rerun()
                         else:
                            st.error("Credenciales inválidas.")

            with tab_vecino:
                st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)
                st.markdown("""
                <div style="background-color: #f8fafc; padding: 1.5rem; border-radius: 10px; border: 1px solid #e2e8f0; margin-bottom: 1.5rem;">
                    <h4 style="color: #0f172a; margin-top: 0;">👋 ¡Bienvenido, Vecino!</h4>
                    <p style="color: #475569; font-size: 0.9rem; margin-bottom: 1rem;">
                        No necesitas cuenta para acceder a los servicios de información pública.
                    </p>
                    <ul style="color: #475569; font-size: 0.9rem; padding-left: 1.2rem;">
                        <li>📍 <strong>Mapa de Obras:</strong> Revisa proyectos en tu sector.</li>
                        <li>📢 <strong>Reportes:</strong> Informa problemas en la vía pública.</li>
                        <li>📅 <strong>Actividades:</strong> Consulta la agenda municipal.</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button("👤 Ingresar como Invitado", use_container_width=True, type="primary", help="Acceso directo sin registro"):
                    st.session_state['authenticated'] = True
                    st.session_state['user_role'] = 'CITIZEN'
                    st.session_state['user'] = 'Invitado' 
                    st.rerun()

            st.markdown("<div style='height: 2rem;'></div>", unsafe_allow_html=True)
            st.caption("© 2026 CiviumTech - v2.4.1")
# Re-export legacy names if app.py uses them
login = render_login
get_current_user = lambda: st.session_state.get('username')
