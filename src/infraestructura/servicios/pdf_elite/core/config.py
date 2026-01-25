"""
Configuración Global del Sistema PDF de Élite
=============================================
Centraliza toda la configuración del sistema de generación PDF,
incluyendo información de la empresa, estilos, colores y fuentes.

Autor: Sistema de Gestión Inmobiliaria
Fecha: 2026-01-18
"""

from pathlib import Path
from typing import Literal, Tuple

from pydantic import BaseModel, Field
from reportlab.lib import colors as rl_colors

# ============================================================================
# CONFIGURACIÓN PRINCIPAL
# ============================================================================


class PDFConfig(BaseModel):
    """Configuración global del sistema PDF élite"""

    # === Directorios ===
    output_dir: Path = Field(
        default=Path("documentos_generados"), description="Directorio de salida para PDFs generados"
    )
    fonts_dir: Path = Field(
        default=Path("assets/fonts"), description="Directorio para fuentes personalizadas"
    )
    temp_dir: Path = Field(
        default=Path("temp/pdf"), description="Directorio temporal para procesamiento"
    )

    # === Información de la Empresa ===
    empresa_nombre: str = "INMOBILIARIA VELAR SAS"
    empresa_nit: str = "900.123.456-7"
    empresa_direccion: str = "Calle 100 # 15-20, Bogotá"
    empresa_telefono: str = "(601) 555-5555"
    empresa_email: str = "contacto@inmovelar.com"
    empresa_web: str = "www.inmovelar.com"

    # === Configuración de Página ===
    page_size: Literal["A4", "Letter"] = "A4"
    margins_top: int = Field(default=72, description="Margen superior en puntos")
    margins_right: int = Field(default=72, description="Margen derecho en puntos")
    margins_bottom: int = Field(default=72, description="Margen inferior en puntos")
    margins_left: int = Field(default=72, description="Margen izquierdo en puntos")

    # === Características ===
    compression: bool = Field(default=True, description="Comprimir PDFs")
    enable_watermarks: bool = Field(default=True, description="Permitir marcas de agua")
    enable_qr_codes: bool = Field(default=True, description="Permitir códigos QR")
    enable_encryption: bool = Field(default=False, description="Encriptación de PDFs")

    # === Performance ===
    cache_enabled: bool = Field(default=True, description="Habilitar cache de templates")
    max_cache_size_mb: int = Field(default=100, description="Tamaño máximo de cache en MB")

    @property
    def margins(self) -> Tuple[int, int, int, int]:
        """Retorna márgenes como tupla (top, right, bottom, left)"""
        return (self.margins_top, self.margins_right, self.margins_bottom, self.margins_left)

    class Config:
        """Configuración de Pydantic"""

        validate_assignment = True


# Instancia global singleton
config = PDFConfig()


# ============================================================================
# PALETA DE COLORES CORPORATIVOS
# ============================================================================


class Colors:
    """
    Paleta de colores estandarizada para documentos PDF

    Todos los colores están en formato RGB normalizado (0.0 - 1.0)
    compatible con ReportLab.
    """

    # === Colores Primarios ===
    PRIMARY = (0.2, 0.3, 0.6)  # Azul corporativo oscuro #334D99
    PRIMARY_LIGHT = (0.4, 0.5, 0.75)  # Azul claro #6680BF
    PRIMARY_DARK = (0.1, 0.2, 0.45)  # Azul muy oscuro #1A3373

    # === Colores Secundarios ===
    SECONDARY = (0.4, 0.6, 0.8)  # Azul medio #6699CC
    ACCENT = (0.9, 0.5, 0.2)  # Naranja acento #E68033

    # === Colores Semánticos ===
    SUCCESS = (0.2, 0.7, 0.3)  # Verde éxito #33B34D
    SUCCESS_LIGHT = (0.85, 0.95, 0.85)  # Verde claro fondo #D9F2D9

    WARNING = (0.9, 0.7, 0.2)  # Amarillo advertencia #E6B333
    WARNING_LIGHT = (0.98, 0.95, 0.85)  # Amarillo claro fondo #FAF2D9

    DANGER = (0.8, 0.2, 0.2)  # Rojo error #CC3333
    DANGER_LIGHT = (0.95, 0.85, 0.85)  # Rojo claro fondo #F2D9D9

    INFO = (0.2, 0.6, 0.8)  # Azul información #3399CC
    INFO_LIGHT = (0.85, 0.93, 0.97)  # Azul claro fondo #D9EDF7

    # === Escala de Grises ===
    BLACK = (0, 0, 0)  # Negro puro #000000
    GRAY_DARKEST = (0.2, 0.2, 0.2)  # Gris muy oscuro #333333
    GRAY_DARK = (0.3, 0.3, 0.3)  # Gris oscuro #4D4D4D
    GRAY_MEDIUM = (0.5, 0.5, 0.5)  # Gris medio #808080
    GRAY_LIGHT = (0.7, 0.7, 0.7)  # Gris claro #B3B3B3
    GRAY_LIGHTER = (0.85, 0.85, 0.85)  # Gris muy claro #D9D9D9
    GRAY_LIGHTEST = (0.95, 0.95, 0.95)  # Gris casi blanco #F2F2F2
    WHITE = (1, 1, 1)  # Blanco puro #FFFFFF

    # === Colores para gráficos ===
    CHART_COLORS = [
        (0.2, 0.3, 0.6),  # Azul
        (0.9, 0.5, 0.2),  # Naranja
        (0.2, 0.7, 0.3),  # Verde
        (0.8, 0.2, 0.2),  # Rojo
        (0.6, 0.4, 0.8),  # Morado
        (0.9, 0.7, 0.2),  # Amarillo
        (0.3, 0.7, 0.7),  # Cyan
        (0.9, 0.4, 0.6),  # Rosa
    ]

    @classmethod
    def to_reportlab(cls, rgb_tuple: Tuple[float, float, float]) -> rl_colors.Color:
        """Convierte tupla RGB a Color de ReportLab"""
        return rl_colors.Color(*rgb_tuple)

    @classmethod
    def to_hex(cls, rgb_tuple: Tuple[float, float, float]) -> str:
        """Convierte tupla RGB a código hexadecimal"""
        r, g, b = rgb_tuple
        return f"#{int(r*255):02X}{int(g*255):02X}{int(b*255):02X}"


# ============================================================================
# CONFIGURACIÓN DE FUENTES
# ============================================================================


class Fonts:
    """
    Configuración de fuentes para documentos PDF

    Define fuentes estándar, tamaños y estilos consistentes
    en todo el sistema.
    """

    # === Familias de Fuentes ===
    # Usando fuentes estándar de ReportLab (siempre disponibles)
    FAMILY_MAIN = "Helvetica"
    FAMILY_MAIN_BOLD = "Helvetica-Bold"
    FAMILY_MAIN_ITALIC = "Helvetica-Oblique"
    FAMILY_MAIN_BOLD_ITALIC = "Helvetica-BoldOblique"

    FAMILY_SERIF = "Times-Roman"
    FAMILY_SERIF_BOLD = "Times-Bold"
    FAMILY_SERIF_ITALIC = "Times-Italic"
    FAMILY_SERIF_BOLD_ITALIC = "Times-BoldItalic"

    FAMILY_MONO = "Courier"
    FAMILY_MONO_BOLD = "Courier-Bold"

    # === Fuentes por Propósito ===
    TITLE = FAMILY_MAIN_BOLD  # Para títulos principales
    SUBTITLE = FAMILY_MAIN_BOLD  # Para subtítulos
    HEADING = FAMILY_MAIN_BOLD  # Para encabezados de sección
    BODY = FAMILY_MAIN  # Para texto normal
    BODY_BOLD = FAMILY_MAIN_BOLD  # Para texto enfatizado
    BODY_ITALIC = FAMILY_MAIN_ITALIC  # Para texto en cursiva
    CODE = FAMILY_MONO  # Para código o monoespaciado

    # Alias para compatibilidad
    MAIN = FAMILY_MAIN
    MAIN_BOLD = FAMILY_MAIN_BOLD
    MAIN_ITALIC = FAMILY_MAIN_ITALIC

    # === Tamaños de Fuente (en puntos) ===
    SIZE_TITLE_MAIN = 20  # Título principal del documento
    SIZE_TITLE = 16  # Títulos de sección
    SIZE_SUBTITLE = 14  # Subtítulos
    SIZE_HEADING_1 = 13  # Encabezado nivel 1
    SIZE_HEADING_2 = 12  # Encabezado nivel 2
    SIZE_HEADING_3 = 11  # Encabezado nivel 3
    SIZE_BODY = 10  # Texto normal
    SIZE_SMALL = 8  # Texto pequeño (notas, pies de página)
    SIZE_TINY = 7  # Texto muy pequeño (disclaimers)

    # === Interlineado ===
    LEADING_TIGHT = 1.0  # Interlineado ajustado
    LEADING_NORMAL = 1.2  # Interlineado normal
    LEADING_RELAXED = 1.5  # Interlineado relajado
    LEADING_DOUBLE = 2.0  # Interlineado doble

    @classmethod
    def get_leading(cls, font_size: int, style: str = "normal") -> float:
        """
        Calcula el interlineado apropiado para un tamaño de fuente

        Args:
            font_size: Tamaño de fuente en puntos
            style: 'tight', 'normal', 'relaxed', 'double'

        Returns:
            Interlineado en puntos
        """
        multipliers = {
            "tight": cls.LEADING_TIGHT,
            "normal": cls.LEADING_NORMAL,
            "relaxed": cls.LEADING_RELAXED,
            "double": cls.LEADING_DOUBLE,
        }
        multiplier = multipliers.get(style, cls.LEADING_NORMAL)
        return font_size * multiplier


# ============================================================================
# CONSTANTES ÚTILES
# ============================================================================


class Constants:
    """Constantes útiles para generación de PDFs"""

    # === Unidades de medida ===
    INCH = 72  # Puntos por pulgada
    CM = 28.35  # Puntos por centímetro
    MM = 2.835  # Puntos por milímetro

    # === Tamaños de página (en puntos) ===
    A4_WIDTH = 595.27
    A4_HEIGHT = 841.89
    LETTER_WIDTH = 612
    LETTER_HEIGHT = 792

    # === Espaciados comunes ===
    SPACING_TINY = 4  # Espaciado mínimo
    SPACING_SMALL = 8  # Espaciado pequeño
    SPACING_NORMAL = 12  # Espaciado normal
    SPACING_LARGE = 20  # Espaciado grande
    SPACING_XLARGE = 30  # Espaciado muy grande

    # === Tamaños de QR code ===
    QR_SIZE_SMALL = 60  # QR pequeño (60x60 px)
    QR_SIZE_MEDIUM = 100  # QR mediano (100x100 px)
    QR_SIZE_LARGE = 150  # QR grande (150x150 px)


# ============================================================================
# VALIDACIÓN DE CONFIGURACIÓN
# ============================================================================


def validate_config() -> bool:
    """
    Valida la configuración global

    Returns:
        True si la configuración es válida

    Raises:
        ValueError: Si hay problemas en la configuración
    """
    # Validar que los directorios existen o se pueden crear
    try:
        config.output_dir.mkdir(parents=True, exist_ok=True)
        config.temp_dir.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        raise ValueError(f"No se pueden crear directorios: {e}")

    # Validar márgenes
    if any(m < 0 or m > 200 for m in config.margins):
        raise ValueError("Los márgenes deben estar entre 0 y 200 puntos")

    return True


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    "config",
    "Colors",
    "Fonts",
    "Constants",
    "PDFConfig",
    "validate_config",
]
