
try:
    from modules import views
    print("✅ Views module syntax OK.")
except Exception as e:
    print(f"❌ Syntax Error in views.py: {e}")
