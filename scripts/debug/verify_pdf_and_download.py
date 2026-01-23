
from src.infraestructura.servicios.servicio_documentos_pdf import ServicioDocumentosPDF
import os
import shutil
from datetime import datetime

def test_pdf_generation_and_download():
    print("Testing Desocupación Checklist PDF Generation & Download logic...")
    
    # Mock data
    mock_data = {
        'id_desocupacion': 999,
        'fecha_solicitud': '2025-01-03',
        'fecha_programada': '2025-01-10',
        'estado': 'En Proceso',
        'observaciones': 'Test observations',
        'id_contrato': 123,
        'fecha_contrato': '2024-01-01',
        'direccion': 'Calle 123 # 45-67, Test City',
        'matricula': '50C-123456',
        'inquilino': 'Test Tenant Name',
        'documento': '123456789',
        'telefono': '555-1234',
        'email': 'tenant@example.com'
    }
    
    service = ServicioDocumentosPDF()
    try:
        # 1. Generate
        path = service.generar_checklist_desocupacion(mock_data)
        print(f"SUCCESS: PDF generated at: {path}")
        
        if not os.path.exists(path):
            print("ERROR: File returned but not found on disk.")
            return

        # 2. Simulate Download Logic
        print("Testing Download Logic...")
        user_downloads = os.path.join(os.path.expanduser("~"), "Downloads")
        print(f"Detected Downloads folder: {user_downloads}")
        
        filename = os.path.basename(path)
        dest_path = os.path.join(user_downloads, filename)
        
        print(f"Attempting to copy to: {dest_path}")
        shutil.copy2(path, dest_path)
        
        if os.path.exists(dest_path):
             print("SUCCESS: File copied to Downloads folder.")
             # Cleanup
             os.remove(dest_path)
             print("Cleanup: Removed test file from Downloads.")
        else:
             print("ERROR: File NOT found in Downloads folder after copy.")

        # 3. Check PDF size (rough heuristic for compression)
        size = os.path.getsize(path)
        print(f"PDF Size: {size / 1024:.2f} KB")

    except Exception as e:
        print(f"ERROR: Failed test. {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_pdf_generation_and_download()
