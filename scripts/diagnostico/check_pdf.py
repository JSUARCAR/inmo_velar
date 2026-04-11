
import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

def check_pdf_validity(path):
    try:
        # No hay una forma fácil de "validar" un PDF con ReportLab solo, 
        # pero podemos intentar leerlo con algo básico si estuviera instalado.
        # Como no tenemos PyPDF2, vamos a ver si el tamaño es razonable 
        # y si tiene los marcadores básicos.
        size = os.path.getsize(path)
        print(f"File: {path}")
        print(f"Size: {size} bytes")
        
        with open(path, 'rb') as f:
            header = f.read(10)
            f.seek(-10, 2)
            footer = f.read(10)
            
        print(f"Header: {header}")
        print(f"Footer: {footer}")
        
        if header.startswith(b'%PDF') and b'%%EOF' in footer:
            print("v PDF seems structuraly valid (header/footer)")
        else:
            print("x PDF seems structuraly INVALID")
            
    except Exception as e:
        print(f"x Error checking PDF: {e}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        check_pdf_validity(sys.argv[1])
    else:
        # Check the latest ones
        import glob
        files = glob.glob("documentos_generados/contrato_mandato_70_*.pdf")
        for f in sorted(files, reverse=True)[:2]:
            check_pdf_validity(f)
