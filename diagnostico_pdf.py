"""
Script de Diagnóstico del Sistema PDF Élite
============================================
Ejecuta diagnóstico completo del sistema para identificar problemas.

Uso: python diagnostico_pdf.py
"""

import sys
from pathlib import Path

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent))

def test_1_imports():
    """Test 1: Verificar que todos los imports funcionan"""
    print("\n" + "="*80)
    print("🔍 TEST 1: Verificando Imports")
    print("="*80)
    
    try:
        from src.infraestructura.servicios.servicio_pdf_facade import ServicioPDFFacade
        print("✅ ServicioPDFFacade importado correctamente")
        
        from src.presentacion_reflex.state.pdf_state import PDFState
        print("✅ PDFState importado correctamente")
        
        from src.infraestructura.servicios.pdf_elite.utils.mock_data_repository import MockPDFRepository
        print("✅ MockPDFRepository importado correctamente")
        
        return True
    except Exception as e:
        print(f"❌ Error en imports: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_2_mock_data():
    """Test 2: Verificar datos mock"""
    print("\n" + "="*80)
    print("🔍 TEST 2: Verificando Mock Data")
    print("="*80)
    
    try:
        from src.infraestructura.servicios.pdf_elite.utils.mock_data_repository import MockPDFRepository
        
        # Test contrato
        contrato = MockPDFRepository.get_contrato_data(1)
        print(f"✅ Contrato 1 obtenido: {list(contrato.keys())}")
        
        # Test estado cuenta
        estado = MockPDFRepository.get_estado_cuenta_data(1, "2026-01")
        print(f"✅ Estado cuenta obtenido: {list(estado.keys())}")
        print(f"   - Movimientos: {len(estado['movimientos'])}")
        
        return True
    except Exception as e:
        print(f"❌ Error en mock data: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_3_pdf_generation():
    """Test 3: Generar PDF de prueba"""
    print("\n" + "="*80)
    print("🔍 TEST 3: Generando PDF de Prueba")
    print("="*80)
    
    try:
        from src.infraestructura.servicios.servicio_pdf_facade import ServicioPDFFacade
        from src.infraestructura.servicios.pdf_elite.utils.mock_data_repository import MockPDFRepository
        
        facade = ServicioPDFFacade()
        print("✅ Facade creado")
        
        # Test contrato
        print("\n📄 Generando contrato élite...")
        datos_contrato = MockPDFRepository.get_contrato_data(1)
        pdf_path = facade.generar_contrato_elite(datos_contrato, usar_borrador=True)
        print(f"✅ Contrato generado: {pdf_path}")
        print(f"   Archivo existe: {Path(pdf_path).exists()}")
        
        # Test estado cuenta
        print("\n💰 Generando estado de cuenta élite...")
        datos_estado = MockPDFRepository.get_estado_cuenta_data(1, "2026-01")
        pdf_path2 = facade.generar_estado_cuenta_elite(datos_estado)
        print(f"✅ Estado cuenta generado: {pdf_path2}")
        print(f"   Archivo existe: {Path(pdf_path2).exists()}")
        
        return True
    except Exception as e:
        print(f"❌ Error generando PDF: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_4_config():
    """Test 4: Verificar configuración"""
    print("\n" + "="*80)
    print("🔍 TEST 4: Verificando Configuración")
    print("="*80)
    
    try:
        from src.infraestructura.servicios.pdf_elite.core.config import config
        
        print(f"✅ Config cargado")
        print(f"   Output dir: {config.output_dir}")
        print(f"   Empresa: {config.empresa_nombre}")
        print(f"   Page size: {config.page_size}")
        print(f"   Compression: {config.compression}")
        
        return True
    except Exception as e:
        print(f"❌ Error en config: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Ejecuta todos los tests"""
    print("\n" + "="*80)
    print("🚀 DIAGNÓSTICO SISTEMA PDF ÉLITE")
    print("="*80)
    
    results = {
        "Imports": test_1_imports(),
        "Mock Data": test_2_mock_data(),
        "Config": test_4_config(),
        "Generación PDF": test_3_pdf_generation(),
    }
    
    print("\n" + "="*80)
    print("📊 RESUMEN DE DIAGNÓSTICO")
    print("="*80)
    
    for test, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test}")
    
    all_pass = all(results.values())
    
    if all_pass:
        print("\n🎉 TODOS LOS TESTS PASARON - Sistema funcionando correctamente")
    else:
        print("\n⚠️ ALGUNOS TESTS FALLARON - Revisar errores arriba")
    
    return all_pass

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
