"""
Sistema de Temas
================
Define temas completos para documentos PDF.

Autor: Sistema de Gestión Inmobiliaria
Fecha: 2026-01-18
"""

from dataclasses import dataclass
from typing import Tuple

from ..core.config import Colors, Fonts


@dataclass
class DocumentTheme:
    """
    Tema completo para un documento PDF

    Agrupa colores, fuentes y otras configuraciones visuales.
    """

    # Identificación
    name: str
    description: str

    # Colores principales
    primary_color: Tuple[float, float, float]
    secondary_color: Tuple[float, float, float]
    accent_color: Tuple[float, float, float]

    # Colores de texto
    title_color: Tuple[float, float, float]
    body_color: Tuple[float, float, float]

    # Colores de fondo
    header_bg: Tuple[float, float, float]
    table_header_bg: Tuple[float, float, float]

    # Fuentes
    title_font: str
    body_font: str


class Themes:
    """
    Colección de temas predefinidos

    Proporciona temas listos para usar en diferentes tipos de documentos.
    """

    # Tema corporativo por defecto
    CORPORATE = DocumentTheme(
        name="Corporate",
        description="Tema corporativo estándar de Inmobiliaria Velar",
        primary_color=Colors.PRIMARY,
        secondary_color=Colors.SECONDARY,
        accent_color=Colors.ACCENT,
        title_color=Colors.PRIMARY,
        body_color=Colors.BLACK,
        header_bg=Colors.PRIMARY,
        table_header_bg=Colors.PRIMARY,
        title_font=Fonts.TITLE,
        body_font=Fonts.BODY,
    )

    # Tema profesional (tonos azules/grises)
    PROFESSIONAL = DocumentTheme(
        name="Professional",
        description="Tema profesional con tonos azules y grises",
        primary_color=Colors.PRIMARY_DARK,
        secondary_color=Colors.GRAY_DARK,
        accent_color=Colors.INFO,
        title_color=Colors.PRIMARY_DARK,
        body_color=Colors.GRAY_DARKEST,
        header_bg=Colors.PRIMARY_DARK,
        table_header_bg=Colors.GRAY_DARK,
        title_font=Fonts.TITLE,
        body_font=Fonts.BODY,
    )

    # Tema minimalista (blanco y negro con acentos)
    MINIMAL = DocumentTheme(
        name="Minimal",
        description="Tema minimalista con énfasis en espacios en blanco",
        primary_color=Colors.BLACK,
        secondary_color=Colors.GRAY_MEDIUM,
        accent_color=Colors.ACCENT,
        title_color=Colors.BLACK,
        body_color=Colors.GRAY_DARKEST,
        header_bg=Colors.GRAY_LIGHTEST,
        table_header_bg=Colors.GRAY_LIGHT,
        title_font=Fonts.TITLE,
        body_font=Fonts.BODY,
    )

    # Tema para contratos (formal y legal)
    LEGAL = DocumentTheme(
        name="Legal",
        description="Tema formal para documentos legales y contratos",
        primary_color=Colors.GRAY_DARKEST,
        secondary_color=Colors.GRAY_DARK,
        accent_color=Colors.PRIMARY,
        title_color=Colors.BLACK,
        body_color=Colors.BLACK,
        header_bg=Colors.GRAY_DARKEST,
        table_header_bg=Colors.GRAY_DARK,
        title_font=Fonts.FAMILY_SERIF_BOLD,
        body_font=Fonts.FAMILY_SERIF,
    )

    # Tema para certificados (elegante)
    CERTIFICATE = DocumentTheme(
        name="Certificate",
        description="Tema elegante para certificados y documentos oficiales",
        primary_color=(0.1, 0.2, 0.4),  # Azul marino
        secondary_color=(0.7, 0.6, 0.3),  # Dorado
        accent_color=(0.7, 0.6, 0.3),
        title_color=(0.1, 0.2, 0.4),
        body_color=Colors.BLACK,
        header_bg=(0.1, 0.2, 0.4),
        table_header_bg=(0.7, 0.6, 0.3),
        title_font=Fonts.FAMILY_SERIF_BOLD,
        body_font=Fonts.FAMILY_SERIF,
    )

    @classmethod
    def get_theme(cls, name: str) -> DocumentTheme:
        """
        Obtiene un tema por nombre

        Args:
            name: Nombre del tema

        Returns:
            Tema solicitado o CORPORATE por defecto
        """
        themes = {
            "CORPORATE": cls.CORPORATE,
            "PROFESSIONAL": cls.PROFESSIONAL,
            "MINIMAL": cls.MINIMAL,
            "LEGAL": cls.LEGAL,
            "CERTIFICATE": cls.CERTIFICATE,
        }

        return themes.get(name.upper(), cls.CORPORATE)

    @classmethod
    def list_themes(cls) -> list[str]:
        """
        Lista nombres de temas disponibles

        Returns:
            Lista de nombres de temas
        """
        return ["CORPORATE", "PROFESSIONAL", "MINIMAL", "LEGAL", "CERTIFICATE"]


__all__ = ["DocumentTheme", "Themes"]
