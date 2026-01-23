"""
Tests de Configuración
====================
Valida que la configuración del sistema PDF élite esté correcta.

Autor: Sistema de Gestión Inmobiliaria
Fecha: 2026-01-18
"""

import pytest
from pathlib import Path


def test_config_imports():
    """Test: Importación de módulo de configuración"""
    from src.infraestructura.servicios.pdf_elite.core.config import (
        config,
        Colors,
        Fonts,
        Constants,
        validate_config
    )
    assert config is not None
    assert Colors is not None
    assert Fonts is not None
    assert Constants is not None


def test_config_values():
    """Test: Valores de configuración básicos"""
    from src.infraestructura.servicios.pdf_elite.core.config import config
    
    assert config.empresa_nombre == "INMOBILIARIA VELAR SAS"
    assert config.empresa_nit == "900.123.456-7"
    assert config.page_size in ["A4", "Letter"]
    assert config.compression is True


def test_colors_defined():
    """Test: Colores corporativos definidos"""
    from src.infraestructura.servicios.pdf_elite.core.config import Colors
    
    # Verificar colores primarios
    assert Colors.PRIMARY is not None
    assert len(Colors.PRIMARY) == 3
    assert all(0 <= c <= 1 for c in Colors.PRIMARY)
    
    # Verificar colores semánticos
    assert Colors.SUCCESS is not None
    assert Colors.WARNING is not None
    assert Colors.DANGER is not None
    
    # Verificar escala de grises
    assert Colors.BLACK == (0, 0, 0)
    assert Colors.WHITE == (1, 1, 1)


def test_colors_to_hex():
    """Test: Conversión de colores a hexadecimal"""
    from src.infraestructura.servicios.pdf_elite.core.config import Colors
    
    # Negro debe ser #000000
    assert Colors.to_hex(Colors.BLACK) == "#000000"
    
    # Blanco debe ser #FFFFFF
    assert Colors.to_hex(Colors.WHITE) == "#FFFFFF"
    
    # Verificar formato
    hex_color = Colors.to_hex(Colors.PRIMARY)
    assert hex_color.startswith("#")
    assert len(hex_color) == 7


def test_fonts_defined():
    """Test: Fuentes definidas correctamente"""
    from src.infraestructura.servicios.pdf_elite.core.config import Fonts
    
    # Verificar fuentes principales
    assert Fonts.TITLE is not None
    assert Fonts.BODY is not None
    
    # Verificar tamaños
    assert Fonts.SIZE_TITLE > Fonts.SIZE_SUBTITLE
    assert Fonts.SIZE_SUBTITLE > Fonts.SIZE_BODY
    assert Fonts.SIZE_BODY > Fonts.SIZE_SMALL
    
    # Verificar que los tamaños son razonables
    assert 6 <= Fonts.SIZE_TINY <= 30
    assert 6 <= Fonts.SIZE_SMALL <= 30
    assert 8 <= Fonts.SIZE_BODY <= 30


def test_fonts_leading_calculation():
    """Test: Cálculo de interlineado"""
    from src.infraestructura.servicios.pdf_elite.core.config import Fonts
    
    # Interlineado normal para fuente de 10pt
    leading = Fonts.get_leading(10, "normal")
    assert leading == 12.0  # 10 * 1.2
    
    # Interlineado ajustado
    leading_tight = Fonts.get_leading(10, "tight")
    assert leading_tight == 10.0  # 10 * 1.0
    
    # Interlineado relajado
    leading_relaxed = Fonts.get_leading(10, "relaxed")
    assert leading_relaxed == 15.0  # 10 * 1.5


def test_constants_defined():
    """Test: Constantes útiles definidas"""
    from src.infraestructura.servicios.pdf_elite.core.config import Constants
    
    # Unidades de medida
    assert Constants.INCH == 72
    assert Constants.CM > 0
    assert Constants.MM > 0
    
    # Tamaños de página
    assert Constants.A4_WIDTH > 0
    assert Constants.A4_HEIGHT > 0
    assert Constants.LETTER_WIDTH > 0
    assert Constants.LETTER_HEIGHT > 0
    
    # Espaciados
    assert Constants.SPACING_TINY < Constants.SPACING_SMALL
    assert Constants.SPACING_SMALL < Constants.SPACING_NORMAL
    assert Constants.SPACING_NORMAL < Constants.SPACING_LARGE


def test_config_margins():
    """Test: Márgenes de página"""
    from src.infraestructura.servicios.pdf_elite.core.config import config
    
    margins = config.margins
    assert len(margins) == 4  # top, right, bottom, left
    assert all(isinstance(m, int) for m in margins)
    assert all(m >= 0 for m in margins)


def test_validate_config():
    """Test: Validación de configuración"""
    from src.infraestructura.servicios.pdf_elite.core.config import validate_config
    
    # Debe validar sin errores
    assert validate_config() is True


def test_color_palette_utilities():
    """Test: Utilidades de paleta de colores"""
    try:
        from src.infraestructura.servicios.pdf_elite.styles.colors import ColorPalette
        from src.infraestructura.servicios.pdf_elite.core.config import Colors
        
        # Test lighten
        light_color = ColorPalette.lighten(Colors.PRIMARY, 0.2)
        assert len(light_color) == 3
        assert all(0 <= c <= 1 for c in light_color)
        
        # Test darken
        dark_color = ColorPalette.darken(Colors.PRIMARY, 0.2)
        assert len(dark_color) == 3
        assert all(0 <= c <= 1 for c in dark_color)
        
        # Test interpolate
        mid_color = ColorPalette.interpolate(Colors.BLACK, Colors.WHITE, 0.5)
        assert all(0.4 <= c <= 0.6 for c in mid_color)  # Aproximadamente gris medio
        
        # Test gradient
        gradient = ColorPalette.create_gradient(Colors.BLACK, Colors.WHITE, 5)
        assert len(gradient) == 5
        assert gradient[0] == Colors.BLACK
        assert gradient[-1] == Colors.WHITE
    except ImportError:
        pytest.skip("Color palette utilities not yet fully implemented")


def test_font_manager():
    """Test: Gestor de fuentes"""
    from src.infraestructura.servicios.pdf_elite.styles.fonts import FontManager
    
    # Debe poder obtener fuentes registradas
    registered = FontManager.get_registered_fonts()
    assert isinstance(registered, list)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
