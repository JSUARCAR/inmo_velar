"""
Tests de Componentes
===================
Tests para componentes reutilizables del sistema PDF élite.

Autor: Sistema de Gestión Inmobiliaria
Fecha: 2026-01-18
"""

import pytest
from io import BytesIO


def test_advanced_table_data_table():
    """Test: Tabla de datos básica"""
    from src.infraestructura.servicios.pdf_elite.components.tables import AdvancedTable
    
    headers = ["Producto", "Cantidad", "Precio"]
    rows = [
        ["Item 1", "10", "$100"],
        ["Item 2", "5", "$50"]
    ]
    
    table = AdvancedTable.create_data_table(headers, rows)
    assert table is not None
    assert len(table._cellvalues) == 3  # header + 2 rows


def test_advanced_table_with_totals():
    """Test: Tabla con fila de totales"""
    from src.infraestructura.servicios.pdf_elite.components.tables import AdvancedTable
    
    headers = ["Item", "Qty", "Total"]
    rows = [["A", "10", "100"], ["B", "5", "50"]]
    totals = {1: "15", 2: "150"}
    
    table = AdvancedTable.create_data_table(headers, rows, totals=totals)
    assert table is not None
    assert len(table._cellvalues) == 4  # header + 2 rows + totals


def test_key_value_table():
    """Test: Tabla clave-valor"""
    from src.infraestructura.servicios.pdf_elite.components.tables import AdvancedTable
    
    data = {
        "Nombre": "Juan Pérez",
        "Email": "juan@example.com",
        "Teléfono": "555-1234"
    }
    
    table = AdvancedTable.create_key_value_table(data, title="Información")
    assert table is not None
    assert len(table._cellvalues) == 4  # title + 3 data rows


def test_signature_table():
    """Test: Tabla de firmas"""
    from src.infraestructura.servicios.pdf_elite.components.tables import AdvancedTable
    
    signatures = [
        ("ARRENDADOR", "Juan Pérez\nCC 123456"),
        ("ARRENDATARIO", "María López\nCC 789012")
    ]
    
    table = AdvancedTable.create_signature_table(signatures)
    assert table is not None
    assert len(table._cellvalues) == 3  # lines + labels + names


def test_qr_generator_basic():
    """Test: Generación de QR básico"""
    from src.infraestructura.servicios.pdf_elite.utils.qr_generator import QRGenerator
    
    qr_buffer = QRGenerator.generate_qr("https://example.com", size=100)
    assert isinstance(qr_buffer, BytesIO)
    assert qr_buffer.getvalue()  # Tiene contenido


def test_qr_generator_verification():
    """Test: QR de verificación de documentos"""
    from src.infraestructura.servicios.pdf_elite.utils.qr_generator import QRGenerator
    
    qr_buffer = QRGenerator.generate_verification_qr("contrato", 12345)
    assert isinstance(qr_buffer, BytesIO)
    assert qr_buffer.getvalue()


def test_qr_styles():
    """Test: Diferentes estilos de QR"""
    from src.infraestructura.servicios.pdf_elite.utils.qr_generator import QRGenerator
    
    data = "TEST_DATA"
    
    # Cuadrado
    qr1 = QRGenerator.generate_qr(data, style='square')
    assert qr1.getvalue()
    
    # Redondeado
    qr2 = QRGenerator.generate_qr(data, style='rounded')
    assert qr2.getvalue()
    
    # Círculo
    qr3 = QRGenerator.generate_qr(data, style='circle')
    assert qr3.getvalue()


def test_barcode_generator():
    """Test: Generación de código de barras"""
    from src.infraestructura.servicios.pdf_elite.utils.barcode_generator import BarcodeGenerator
    
    barcode_buffer = BarcodeGenerator.generate_barcode("12345678")
    assert isinstance(barcode_buffer, BytesIO)
    assert barcode_buffer.getvalue()


def test_barcode_document():
    """Test: Código de barras para documentos"""
    from src.infraestructura.servicios.pdf_elite.utils.barcode_generator import BarcodeGenerator
    
    barcode_buffer = BarcodeGenerator.generate_document_barcode(12345, prefix="DOC")
    assert isinstance(barcode_buffer, BytesIO)
    assert barcode_buffer.getvalue()


def test_data_validator_required_fields():
    """Test: Validación de campos requeridos"""
    from src.infraestructura.servicios.pdf_elite.utils.validators import DataValidator
    
    data = {"nombre": "Juan", "email": "juan@example.com"}
    required = ["nombre", "email", "telefono"]
    
    is_valid, missing = DataValidator.validate_required_fields(data, required)
    assert not is_valid
    assert "telefono" in missing


def test_data_validator_email():
    """Test: Validación de email"""
    from src.infraestructura.servicios.pdf_elite.utils.validators import DataValidator
    
    assert DataValidator.validate_email("juan@example.com")
    assert not DataValidator.validate_email("invalid-email")
    assert not DataValidator.validate_email("@example.com")


def test_data_validator_phone():
    """Test: Validación de teléfono"""
    from src.infraestructura.servicios.pdf_elite.utils.validators import DataValidator
    
    assert DataValidator.validate_phone("555-1234")
    assert DataValidator.validate_phone("+57 300 1234567")
    assert not DataValidator.validate_phone("123")


def test_data_validator_money():
    """Test: Validación de montos"""
    from src.infraestructura.servicios.pdf_elite.utils.validators import DataValidator
    
    assert DataValidator.validate_money_amount(100.50)
    assert DataValidator.validate_money_amount(0, allow_zero=True)
    assert not DataValidator.validate_money_amount(0, allow_zero=False)
    assert not DataValidator.validate_money_amount(-10)
    assert not DataValidator.validate_money_amount(10.123)  # Más de 2 decimales


def test_themes_exist():
    """Test: Temas predefinidos existen"""
    from src.infraestructura.servicios.pdf_elite.styles.themes import Themes
    
    assert Themes.CORPORATE is not None
    assert Themes.PROFESSIONAL is not None
    assert Themes.MINIMAL is not None
    assert Themes.LEGAL is not None
    assert Themes.CERTIFICATE is not None


def test_theme_properties():
    """Test: Propiedades de temas"""
    from src.infraestructura.servicios.pdf_elite.styles.themes import Themes
    
    theme = Themes.CORPORATE
    assert theme.name == "Corporate"
    assert theme.primary_color is not None
    assert theme.title_font is not None


def test_get_theme():
    """Test: Obtener tema por nombre"""
    from src.infraestructura.servicios.pdf_elite.styles.themes import Themes
    
    theme = Themes.get_theme("PROFESSIONAL")
    assert theme.name == "Professional"
    
    # Tema por defecto si no existe
    default = Themes.get_theme("NONEXISTENT")
    assert default.name == "Corporate"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
