"""
Gestión de Fuentes
==================
Registro y gestión de fuentes personalizadas para PDFs.

Autor: Sistema de Gestión Inmobiliaria
Fecha: 2026-01-18
"""

from pathlib import Path
from typing import Dict

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


class FontManager:
    """Gestor de fuentes personalizadas"""

    _registered_fonts: Dict[str, bool] = {}

    @classmethod
    def register_font(cls, font_name: str, font_path: Path) -> bool:
        """
        Registra una fuente TrueType personalizada

        Args:
            font_name: Nombre para identificar la fuente
            font_path: Ruta al archivo .ttf

        Returns:
            True si se registró exitosamente
        """
        if font_name in cls._registered_fonts:
            return True  # Ya está registrada

        try:
            if not font_path.exists():
                raise FileNotFoundError(f"Fuente no encontrada: {font_path}")

            pdfmetrics.registerFont(TTFont(font_name, str(font_path)))
            cls._registered_fonts[font_name] = True
            return True
        except Exception:
            pass  # print(f"Error registrando fuente {font_name}: {e}") [OpSec Removed]
            return False

    @classmethod
    def register_fonts_from_directory(cls, directory: Path) -> int:
        """
        Registra todas las fuentes .ttf de un directorio

        Args:
            directory: Directorio con fuentes

        Returns:
            Número de fuentes registradas
        """
        if not directory.exists():
            return 0

        count = 0
        for font_file in directory.glob("*.ttf"):
            font_name = font_file.stem  # Nombre sin extensión
            if cls.register_font(font_name, font_file):
                count += 1

        return count

    @classmethod
    def is_registered(cls, font_name: str) -> bool:
        """Verifica si una fuente está registrada"""
        return font_name in cls._registered_fonts

    @classmethod
    def get_registered_fonts(cls) -> list:
        """Retorna lista de fuentes registradas"""
        return list(cls._registered_fonts.keys())


# Auto-registro de fuentes al importar
def _auto_register_fonts():
    """Registra fuentes personalizadas automáticamente"""
    from .config import config

    if config.fonts_dir.exists():
        count = FontManager.register_fonts_from_directory(config.fonts_dir)
        if count > 0:
            pass  # print(f"✓ Registradas {count} fuentes personalizadas") [OpSec Removed]


# Ejecutar auto-registro
try:
    _auto_register_fonts()
except Exception:
    pass  # Silenciar errores en auto-registro


__all__ = ["FontManager"]
