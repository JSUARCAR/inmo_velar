
from src.infraestructura.servicios.servicio_documentos_pdf import ServicioDocumentosPDF
import os

def test_pdf_generation():
    print("Testing Desocupación Checklist PDF Generation...")
    
    # Mock data structure matching what obtener_datos_para_checklist returns
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
        path = service.generar_checklist_desocupacion(mock_data)
        print(f"SUCCESS: PDF generated at: {path}")
        
        if os.path.exists(path):
            print("File exists on disk.")
        else:
            print("ERROR: File returned but not found on disk.")
            
    except Exception as e:
        print(f"ERROR: Failed to generate PDF. {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_pdf_generation()
