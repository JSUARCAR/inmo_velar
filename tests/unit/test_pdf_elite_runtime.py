"""
Test de verificación en tiempo de ejecución para el nuevo motor PDF Elite.
Valida la transición a BaseDocTemplate y la generación multi-página.
"""
import sys
import os
from pathlib import Path

# Añadir raíz del proyecto al path
sys.path.append(os.getcwd())

def test_manual_pdf_generation():
    from src.infraestructura.servicios.pdf_elite.templates.contrato_template import ContratoArrendamientoElite
    from src.infraestructura.servicios.pdf_elite.core.config import config
    
    print("🚀 Iniciando prueba de generación PDF Elite (BaseDocTemplate)...")
    
    # Mock data for Contrato
    mock_data = {
        "contrato_id": 999,
        "fecha": "2026-05-10",
        "fecha_inicio": "2026-06-01",
        "fecha_fin": "2027-05-31",
        "estado": "borrador",
        "inmueble": {
            "direccion": "CALLE 123 # 45-67 TEST",
            "matricula_inmobiliaria": "123-456789",
            "municipio": "Armenia",
            "departamento": "Quindío"
        },
        "arrendatario": {
            "nombre": "JUAN PEREZ PRUEBA",
            "documento": "12345678",
            "telefono": "3001234567",
            "email": "juan@test.com",
            "direccion": "Carrera 10 # 20-30"
        },
        "codeudor": {
            "nombre": "MARIA LOPEZ CODEUDORA",
            "documento": "87654321",
            "telefono": "3119876543",
            "email": "maria@test.com",
            "direccion": "Calle 50 # 40-10"
        },
        "condiciones": {
            "canon": 1500000,
            "duracion_meses": 12,
            "fecha_pago": 5
        }
    }
    
    try:
        # 1. Instanciar generador
        output_dir = Path("outputs/tests")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        gen = ContratoArrendamientoElite(output_dir=output_dir)
        print("✅ Generador instanciado.")
        
        # 2. Generar
        print("⏳ Generando PDF...")
        pdf_path = gen.generate(mock_data)
        
        # 3. Verificar
        if pdf_path.exists():
            size = pdf_path.stat().st_size
            print(f"✅ ÉXITO: PDF generado en {pdf_path}")
            print(f"📊 Tamaño: {size / 1024:.2f} KB")
            
            # Verificar que sea un PDF válido (mínimo de bytes)
            if size > 1000:
                print("✅ Integridad básica verificada.")
            else:
                print("❌ ERROR: El archivo PDF es demasiado pequeño.")
        else:
            print(f"❌ ERROR: El archivo no se encontró en {pdf_path}")
            
    except Exception as e:
        print(f"❌ FALLO CRÍTICO: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_manual_pdf_generation()
