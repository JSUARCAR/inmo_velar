"""
Paleta de Colores Extendida
===========================
Definiciones adicionales y utilidades para manejo de colores.

Autor: Sistema de Gestión Inmobiliaria
Fecha: 2026-01-18
"""

from typing import Tuple, List
from reportlab.lib import colors as rl_colors


class ColorPalette:
    """Paleta de colores extendida con utilidades"""
    
    # Heredar colores base de config
    from .config import Colors
    
    @staticmethod
    def lighten(rgb: Tuple[float, float, float], amount: float = 0.2) -> Tuple[float, float, float]:
        """
        Aclara un color RGB
        
        Args:
            rgb: Color RGB normalizado (0-1)
            amount: Cantidad a aclarar (0-1)
        
        Returns:
            Color aclarado
        """
        r, g, b = rgb
        return (
            min(1.0, r + (1.0 - r) * amount),
            min(1.0, g + (1.0 - g) * amount),
            min(1.0, b + (1.0 - b) * amount)
        )
    
    @staticmethod
    def darken(rgb: Tuple[float, float, float], amount: float = 0.2) -> Tuple[float, float, float]:
        """
        Oscurece un color RGB
        
        Args:
            rgb: Color RGB normalizado (0-1)
            amount: Cantidad a oscurecer (0-1)
        
        Returns:
            Color oscurecido
        """
        r, g, b = rgb
        return (
            max(0.0, r * (1.0 - amount)),
            max(0.0, g * (1.0 - amount)),
            max(0.0, b * (1.0 - amount))
        )
    
    @staticmethod
    def interpolate(
        color1: Tuple[float, float, float],
        color2: Tuple[float, float, float],
        factor: float = 0.5
    ) -> Tuple[float, float, float]:
        """
        Interpola entre dos colores
        
        Args:
            color1: Primer color
            color2: Segundo color
            factor: Factor de interpolación (0 = color1, 1 = color2)
        
        Returns:
            Color interpolado
        """
        r1, g1, b1 = color1
        r2, g2, b2 = color2
        
        return (
            r1 + (r2 - r1) * factor,
            g1 + (g2 - g1) * factor,
            b1 + (b2 - b1) * factor
        )
    
    @staticmethod
    def create_gradient(
        color1: Tuple[float, float, float],
        color2: Tuple[float, float, float],
        steps: int = 5
    ) -> List[Tuple[float, float, float]]:
        """
        Crea un gradiente entre dos colores
        
        Args:
            color1: Color inicial
            color2: Color final
            steps: Número de pasos en el gradiente
        
        Returns:
            Lista de colores del gradiente
        """
        if steps < 2:
            return [color1]
        
        gradient = []
        for i in range(steps):
            factor = i / (steps - 1)
            gradient.append(ColorPalette.interpolate(color1, color2, factor))
        
        return gradient


__all__ = ['ColorPalette']
