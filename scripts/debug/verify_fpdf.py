try:
    import fpdf
    print("SUCCESS: fpdf imported successfully")
except ImportError as e:
    print(f"FAILURE: {e}")
except Exception as e:
    print(f"FAILURE: Unexpected error {e}")
