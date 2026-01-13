
import streamlit as st
from supabase import create_client
import sys

# Mock secrets if not running in streamlit
if not st.secrets:
    print("❌ No secrets found outside Streamlit.")
    # Assuming we can't run this easily without st.secrets unless we mock them or run via streamlit
    # We will rely on streamlit run
    
def test_connection():
    try:
        if "global" in st.secrets:
            url = st.secrets["global"]["SUPABASE_URL"]
            key = st.secrets["global"]["SUPABASE_KEY"]
        else:
            url = st.secrets["SUPABASE_URL"]
            key = st.secrets["SUPABASE_KEY"]
            
        print(f"✅ Credentials found. URL: {url[:20]}...")
        client = create_client(url, key)
        
        # Test 1: Select
        print("Testing SELECT...")
        try:
            res = client.table("tickets").select("count", count="exact").execute()
            print(f"✅ SELECT OK. Count: {res.count}")
        except Exception as e:
            print(f"❌ SELECT FAILED: {e}")

        # Test 2: Insert (Mock)
        print("Testing INSERT...")
        new_ticket = {
            'sub': 'DEBUG_TEST',
            'desc': 'Connectivity Test',
            'estado': 'Pendiente',
            'fecha': '2025-01-01',
            'urgencia': 'Baja'
        }
        try:
            res = client.table("tickets").insert(new_ticket).execute()
            print(f"✅ INSERT OK. Data: {res.data}")
            
            # Clean up
            if res.data:
                tid = res.data[0]['id']
                client.table("tickets").delete().eq('id', tid).execute()
                print("✅ CLEANUP OK.")
                
        except Exception as e:
            print(f"❌ INSERT FAILED: {e}")
            
    except Exception as e:
        print(f"❌ CRITICAL ERROR: {e}")

if __name__ == "__main__":
    test_connection()
