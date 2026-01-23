"""
Tests de Templates
=================
Tests para templates de documentos avanzados.

Autor: Sistema de Gestión Inmobiliaria
Fecha: 2026-01-18
"""

import pytest
from pathlib import Path


def test_base_template_watermark():
    """Test: Configuración de marca de agua"""
    from src.infraestructura.servicios.pdf_elite.templates.base_template import BaseDocumentTemplate
    
    template = BaseDocumentTemplate()
    template.set_watermark("BORRADOR", opacity=0.15)
    
    assert template.watermark_text == "BORRADOR"
    assert template.watermark_opacity == 0.15


def test_base_template_qr():
    """Test: Configuración de QR code"""
    from src.infraestructura.servicios.pdf_elite.templates.base_template import BaseDocumentTemplate
    
    template = BaseDocumentTemplate()
    template.set_qr_code("https://example.com", size=150)
    
    assert template.include_qr is True
    assert template.qr_data == "https://example.com"
    assert template.qr_size == 150


def test_base_template_verification_qr():
    """Test: QR de verificación automático"""
    from src.infraestructura.servicios.pdf_elite.templates.base_template import BaseDocumentTemplate
    
    template = BaseDocumentTemplate()
    template.enable_verification_qr("contrato", 12345)
    
    assert template.include_qr is True
    assert "contrato/12345" in template.qr_data


def test_contrato_validation():
    """Test: Validación de datos de contrato"""
    from src.infraestructura.servicios.pdf_elite.templates.contrato_template import ContratoArrendamientoElite
    
    gen = ContratoArrendamientoElite()
    
    # Datos válidos
    data = {
        'contrato_id': 123,
        'fecha': '2026-01-18',
        'arrendador': {
            'nombre': 'Juan Pérez',
            'documento': '123456',
            'telefono': '555-1234'
        },
        'arrendatario': {
            'nombre': 'María López',
            'documento': '789012',
            'telefono': '555-5678'
        },
        'inmueble': {
            'direccion': 'Calle 123 #45-67',
            'tipo': 'Apartamento'
        },
        'condiciones': {
            'canon': 1000000,
            'duracion_meses': 12
        }
    }
    
    assert gen.validate_data(data) is True


def test_contrato_invalid_data():
    """Test: Validación rechaza datos inválidos"""
    from src.infraestructura.servicios.pdf_elite.templates.contrato_template import ContratoArrendamientoElite
    
    gen = ContratoArrendamientoElite()
    
    # Datos incompletos
    data = {
        'contrato_id': 123,
'fecha': '2026-01-18'
    }
    
    with pytest.raises(ValueError):
        gen.validate_data(data)


def test_certificado_tipos():
    """Test: Diferentes tipos de certificados"""
    from src.infraestructura.servicios.pdf_elite.templates.certificado_template import CertificadoTemplate
    
    gen = CertificadoTemplate()
    
    assert gen._get_titulo_certificado('paz_y_salvo') == 'CERTIFICADO DE PAZ Y SALVO'
    assert gen._get_titulo_certificado('cumplimiento') == 'CERTIFICADO DE CUMPLIMIENTO'
    assert gen._get_titulo_certificado('general') == 'CERTIFICACIÓN'


def test_certificado_fecha_formateada():
    """Test: Formateo de fecha elegante"""
    from src.infraestructura.servicios.pdf_elite.templates.certificado_template import CertificadoTemplate
    
    gen = CertificadoTemplate()
    fecha = gen._formatear_fecha('2026-01-18')
    
    assert 'enero' in fecha.lower()
    assert '2026' in fecha
    assert '18' in fecha


def test_estado_cuenta_validation():
    """Test: Validación de estado de cuenta"""
    from src.infraestructura.servicios.pdf_elite.templates.estado_cuenta_elite import EstadoCuentaElite
    
    gen = EstadoCuentaElite()
    
    data = {
        'estado_id': 789,
        'propietario': {
            'nombre': 'Carlos Ruiz',
            'documento': '456789'
        },
        'inmueble': {
            'direccion': 'Av. Principal #10-20',
            'canon': 1500000
        },
        'periodo': '2026-01',
        'movimientos': [],
        'resumen': {
            'total_ingresos': 1500000,
            'total_egresos': 200000,
            'valor_neto': 1300000
        }
    }
    
    assert gen.validate_data(data) is True


def test_chart_converter_availability():
    """Test: Verificar disponibilidad de chart converter"""
    from src.infraestructura.servicios.pdf_elite.utils.chart_converter import ChartConverter, PLOTLY_AVAILABLE
    
    # Debe importar sin errores
    assert ChartConverter is not None
    
    # Si plotly está disponible, debe poder crear gráfico de muestra
    if PLOTLY_AVAILABLE:
        fig = ChartConverter.create_sample_chart()
        assert fig is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
