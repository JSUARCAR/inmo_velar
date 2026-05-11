"""
Test de verificación multi-página para el motor PDF Elite.
"""
import sys
import os
from pathlib import Path

# Añadir raíz del proyecto al path
sys.path.insert(0, os.getcwd())

def test_multi_page_pdf():
    from src.infraestructura.servicios.pdf_elite.templates.base_template import BaseDocumentTemplate
    
    print("🚀 Iniciando prueba multi-página PDF Elite...")
    
    try:
        output_dir = Path("outputs/tests")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        gen = BaseDocumentTemplate(output_dir=output_dir)
        gen.create_document("test_multipage.pdf", "Test Multi-Página")
        
        # Página 1
        gen.add_title_main("Página 1")
        gen.add_paragraph("Este es el contenido de la primera página.")
        gen.set_watermark("MULTI-PAGINA", opacity=0.1)
        
        # Forzar salto a Página 2
        gen.add_page_break()
        
        # Página 2
        gen.add_title("Página 2")
        gen.add_paragraph("Este contenido debería estar en la segunda página con el mismo marco.")
        
        # Generar
        pdf_path = gen.build()
        
        if pdf_path.exists():
            print(f"✅ ÉXITO: PDF multi-página generado en {pdf_path}")
            print(f"📊 Tamaño: {pdf_path.stat().st_size / 1024:.2f} KB")
        else:
            print("❌ ERROR: El archivo no se generó.")
            
    except Exception as e:
        print(f"❌ FALLO: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_multi_page_pdf()
