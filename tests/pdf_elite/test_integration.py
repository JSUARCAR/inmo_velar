"""
Tests de Integración End-to-End
===============================
Tests completos del sistema PDF élite integrado.

Autor: Sistema de Gestión Inmobiliaria
Fecha: 2026-01-18
"""

import pytest
from pathlib import Path


# ============================================================================
# TESTS DE FACADE
# ============================================================================

def test_facade_creation():
    """Test: Creación del facade"""
    from src.infraestructura.servicios.servicio_pdf_facade import ServicioPDFFacade
    
    facade = ServicioPDFFacade()
    assert facade is not None
    assert facade.legacy_service is not None
    assert facade.elite_enabled is True


def test_facade_legacy_compatibility():
    """Test: Compatibilidad 100% con métodos legacy"""
    from src.infraestructura.servicios.servicio_pdf_facade import ServicioPDFFacade
    
    facade = ServicioPDFFacade()
    
    # Debe tener todos los métodos legacy
    assert hasattr(facade, 'generar_comprobante_recaudo')
    assert hasattr(facade, 'generar_estado_cuenta')
    assert hasattr(facade, 'generar_cuenta_cobro_asesor')
    assert hasattr(facade, 'generar_checklist_desocupacion')


def test_facade_elite_methods():
    """Test: Métodos élite disponibles"""
    from src.infraestructura.servicios.servicio_pdf_facade import ServicioPDFFacade
    
    facade = ServicioPDFFacade()
    
    # Debe tener métodos élite
    assert hasattr(facade, 'generar_contrato_elite')
    assert hasattr(facade, 'generar_certificado_elite')
    assert hasattr(facade, 'generar_estado_cuenta_elite')


def test_facade_version_info():
    """Test: Información de versión"""
    from src.infraestructura.servicios.servicio_pdf_facade import ServicioPDFFacade
    
    facade = ServicioPDFFacade()
    version_info = facade.get_version_info()
    
    assert 'version' in version_info
    assert 'legacy_compatible' in version_info
    assert version_info['legacy_compatible'] == 'True'


def test_facade_capacidades():
    """Test: Listado de capacidades"""
    from src.infraestructura.servicios.servicio_pdf_facade import ServicioPDFFacade
    
    facade = ServicioPDFFacade()
    capacidades = facade.listar_capacidades_elite()
    
    assert 'contratos' in capacidades
    assert 'certificados' in capacidades
    assert 'estados_cuenta' in capacidades
    
    # Verificar que tiene características
    assert len(capacidades['contratos']) > 0
    assert 'QR de verificación' in capacidades['contratos']


# ============================================================================
# TESTS DE INTEGRACIÓN CON TEMPLATES
# ============================================================================

def test_contrato_elite_full_generation():
    """Test: Generación completa de contrato élite"""
    from src.infraestructura.servicios.servicio_pdf_facade import ServicioPDFFacade
    
    facade = ServicioPDFFacade()
    
    datos = {
        'contrato_id': 999,
        'fecha': '2026-01-18',
        'arrendador': {
            'nombre': 'Test Arrendador',
            'documento': '123456',
            'telefono': '555-0001'
        },
        'arrendatario': {
            'nombre': 'Test Arrendatario',
            'documento': '789012',
            'telefono': '555-0002'
        },
        'inmueble': {
            'direccion': 'Test Address 123',
            'tipo': 'Apartamento'
        },
        'condiciones': {
            'canon': 1000000,
            'duracion_meses': 12
        }
    }
    
    pdf_path = facade.generar_contrato_elite(datos)
    
    assert pdf_path is not None
    assert Path(pdf_path).exists()
    assert Path(pdf_path).suffix == '.pdf'


def test_certificado_elite_generation():
    """Test: Generación de certificado"""
    from src.infraestructura.servicios.servicio_pdf_facade import ServicioPDFFacade
    
    facade = ServicioPDFFacade()
    
    datos = {
        'certificado_id': 888,
        'tipo': 'paz_y_salvo',
        'fecha': '2026-01-18',
        'beneficiario': {
            'nombre': 'Test Beneficiario',
            'documento': '456789'
        },
        'contenido': 'Certificamos que el beneficiario está a paz y salvo.',
        'firmante': {
            'nombre': 'Gerente Test',
            'cargo': 'Gerente',
            'documento': 'NIT 123-4'
        }
    }
    
    pdf_path = facade.generar_certificado_elite(datos)
    
    assert pdf_path is not None
    assert Path(pdf_path).exists()


def test_estado_cuenta_elite_generation():
    """Test: Generación de estado de cuenta élite"""
    from src.infraestructura.servicios.servicio_pdf_facade import ServicioPDFFacade
    
    facade = ServicioPDFFacade()
    
    datos = {
        'estado_id': 777,
        'periodo': '2026-01',
        'propietario': {
            'nombre': 'Test Propietario',
            'documento': '999888'
        },
        'inmueble': {
            'direccion': 'Test Property',
            'canon': 1500000
        },
        'movimientos': [
            {
                'fecha': '2026-01-05',
                'concepto': 'Canon',
                'ingreso': 1500000,
                'egreso': 0
            }
        ],
        'resumen': {
            'total_ingresos': 1500000,
            'total_egresos': 150000,
            'valor_neto': 1350000
        }
    }
    
    pdf_path = facade.generar_estado_cuenta_elite(datos)
    
    assert pdf_path is not None
    assert Path(pdf_path).exists()


# ============================================================================
# TESTS DE REFLEX STATE
# ============================================================================

def test_pdf_state_creation():
    """Test: Creación del PDFState"""
    from src.presentacion_reflex.state.pdf_state import PDFState
    
    state = PDFState()
    assert state is not None
    assert state.generating is False
    assert state.last_pdf_path == ""


def test_pdf_state_has_handlers():
    """Test: PDFState tiene event handlers"""
    from src.presentacion_reflex.state.pdf_state import PDFState
    
    # Verificar que tiene los métodos necesarios
    assert hasattr(PDFState, 'generar_contrato_arrendamiento_elite')
    assert hasattr(PDFState, 'generar_certificado_paz_y_salvo')
    assert hasattr(PDFState, 'generar_estado_cuenta_elite')


# ============================================================================
# TESTS DE SISTEMA COMPLETO
# ============================================================================

def test_sistema_completo_disponibilidad():
    """Test: Todas las partes del sistema están disponibles"""
    
    # Config
    from src.infraestructura.servicios.pdf_elite.core.config import config
    assert config is not None
    
    # Generadores
    from src.infraestructura.servicios.pdf_elite.core.base_generator import BasePDFGenerator
    from src.infraestructura.servicios.pdf_elite.core.reportlab_generator import ReportLabGenerator
    assert BasePDFGenerator is not None
    assert ReportLabGenerator is not None
    
    # Componentes
    from src.infraestructura.servicios.pdf_elite.components.tables import AdvancedTable
    from src.infraestructura.servicios.pdf_elite.components.watermarks import Watermark
    assert AdvancedTable is not None
    assert Watermark is not None
    
    # Utilidades
    from src.infraestructura.servicios.pdf_elite.utils.qr_generator import QRGenerator
    from src.infraestructura.servicios.pdf_elite.utils.validators import DataValidator
    assert QRGenerator is not None
    assert DataValidator is not None
    
    # Templates
    from src.infraestructura.servicios.pdf_elite.templates.base_template import BaseDocumentTemplate
    from src.infraestructura.servicios.pdf_elite.templates.contrato_template import ContratoArrendamientoElite
    assert BaseDocumentTemplate is not None
    assert ContratoArrendamientoElite is not None
    
    # Facade e integración
    from src.infraestructura.servicios.servicio_pdf_facade import ServicioPDFFacade
    from src.presentacion_reflex.state.pdf_state import PDFState
    assert ServicioPDFFacade is not None
    assert PDFState is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
