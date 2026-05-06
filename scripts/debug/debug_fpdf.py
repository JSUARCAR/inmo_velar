
try:
    from fpdf import FPDF
    print("SUCCESS: FPDF importado")
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font('helvetica', size=12)
    pdf.cell(10, 10, "Hola")
    print("SUCCESS: FPDF instanciado")
except ImportError as e:
    print(f"ERROR: {e}")
except Exception as e:
    print(f"ERROR GENERAL: {e}")
