import streamlit as st
from modules.db import get_supabase

def test_search():
    st.title("Test Short ID Search (Retry with Cast)")
    try:
        client = get_supabase()
        
        # 1. Get a real ticket
        res = client.table("tickets").select("id").limit(1).execute()
        
        if not res.data:
            st.error("No tickets found to test.")
            with open("test_results.txt", "w") as f: f.write("FAIL: No tickets")
            return

        full_uuid = res.data[0]['id']
        short_id = full_uuid[:8]
        st.write(f"Testing with UUID: {full_uuid}")
        
        # 2. Try partial search with CAST
        # Trying "id::text" as the column name for filtering
        
        st.write("Attempting .ilike search with cast...")
        
        try:
             # Usage: .ilike("column", "pattern") -> .ilike("id::text", ...)
             # Note: postgrest-py might escape the column name, breaking the cast syntax.
             # If this fails, we might need using 'filter' method strictly or RPC.
             # But let's try the simple column hack first.
             
             res_short = client.table("tickets").select("*").filter("id::text", "ilike", f"{short_id}%").execute()
             
             if res_short.data and res_short.data[0]['id'] == full_uuid:
                 st.success("SUCCESS: Found ticket by short ID using cast!")
                 with open("test_results.txt", "w") as f: f.write(f"SUCCESS_CAST: {short_id}")
             else:
                 st.error("FAIL: Query ran but returned no data.")
                 with open("test_results.txt", "w") as f: f.write("FAIL_CAST: No data returned")
                 
        except Exception as q_err:
             st.error(f"FAIL_CAST: Query Error: {q_err}")
             # Try another syntax if first fails?
             # maybe .ilike("id", pattern) is impossible, but .eq might work? No.
             with open("test_results.txt", "w") as f: f.write(f"FAIL_CAST: Query invalid: {q_err}")

    except Exception as e:
        st.error(f"Global Error: {e}")
        with open("test_results.txt", "w") as f: f.write(f"FAIL: {e}")

if __name__ == "__main__":
    test_search()
