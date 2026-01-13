import streamlit as st
import pandas as pd
from modules.db import get_supabase

st.set_page_config(page_title="Supabase Debugger", layout="centered")

st.title("🐞 Supabase Connection Debugger")

# 1. Secrets Check
st.subheader("1. Configuration Check")
try:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    st.success(f"✅ Secrets found. URL: `{url[:20]}...`")
except Exception as e:
    st.error(f"❌ Secrets Error: {e}")
    st.stop()

# 2. Connection Check
st.subheader("2. Basic Connectivity (Ping)")
try:
    client = get_supabase()
    st.success("✅ Supabase Client initialized.")
except Exception as e:
    st.error(f"❌ Client Init Failed: {e}")
    st.stop()

# 3. Reading 'tickets' (Anon Role)
st.subheader("3. Reading 'tickets' (Anon/Public)")
try:
    res = client.table("tickets").select("*", count="exact").execute()
    count = len(res.data) if res.data else 0
    st.info(f"Tickets found (Anon): **{count}**")
    
    if count > 0:
        st.dataframe(pd.DataFrame(res.data).head(3))
    else:
        st.warning("⚠️ No data found with Anon Key. (Could be empty DB or RLS blocking)")
        
except Exception as e:
    st.error(f"❌ Read Error: {e}")
    st.markdown("""
    **Possible Causes:**
    1. Table `tickets` does not exist. (Did you run `setup_cholchol_v5.sql`?)
    2. RLS Policy denies 'anon' role.
    """)

# 4. Auth Test
st.subheader("4. Authentication Test")
with st.form("debug_login"):
    email = st.text_input("Test Email", "admin@cholchol.cl")
    password = st.text_input("Test Password", "admin123", type="password")
    submit = st.form_submit_button("Test Login & Read")

if submit:
    try:
        auth_res = client.auth.sign_in_with_password({"email": email, "password": password})
        user = auth_res.user
        st.success(f"✅ Logged in as: {user.email} (ID: {user.id})")
        
        # Try read as User
        st.write("--- Reading as Authenticated User ---")
        res_auth = client.table("tickets").select("*").execute()
        st.metric("Tickets Visible to User", len(res_auth.data))
        if res_auth.data:
            st.dataframe(res_auth.data)
        else:
            st.warning("User Logged in, but checks see 0 tickets. (RLS might filter them?)")
            
    except Exception as e:
        st.error(f"❌ Login/Read Failed: {e}")

st.markdown("---")
st.caption("MuniSmart Diagnostic Tool")
