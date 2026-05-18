import sys
import os

# Añadir root al path
sys.path.append(os.getcwd())

from src.infraestructura.servicios.servicio_documentos_pdf import ServicioDocumentosPDF
from datetime import datetime

def test_pdf():
    print("Probando generación de PDF de asesor con nuevos campos...")
    servicio = ServicioDocumentosPDF()
    
    datos = {
        "id_liquidacion": 999,
        "periodo": "2026-05",
        "nombre_asesor": "ASESOR PRUEBA ÉLITE",
        "documento_asesor": "123456789",
        "porcentaje_comision": 800, # Escala 10000 (8.0%)
        "porcentaje_real": 8.0,
        "comision_bruta": 240000,
        "total_descuentos": 40000,
        "valor_neto": 200000,
        "observaciones": "Prueba de desglose individual de contratos.",
        "contratos": [
            {
                "id_contrato": 101,
                "direccion": "AVENIDA SIEMPRE VIVA 123",
                "canon_incluido": 1000000,
                "comision_porcentaje_contrato": 1000, # 10%
                "comision_monto_contrato": 100000
            },
            {
                "id_contrato": 102,
                "direccion": "CALLE FALSA 456",
                "canon_incluido": 2000000,
                "comision_porcentaje_contrato": 700, # 7%
                "comision_monto_contrato": 140000
            }
        ],
        "descuentos_lista": [
            {"tipo_descuento": "Otros", "descripcion_descuento": "Papelería", "valor_descuento": 40000}
        ]
    }
    
    try:
        path = servicio.generar_cuenta_cobro_asesor(datos)
        print(f"✅ PDF generado con éxito en: {path}")
    except Exception as e:
        print(f"❌ Error generando PDF: {e}")

if __name__ == "__main__":
    test_pdf()
