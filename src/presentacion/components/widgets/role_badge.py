"""
Componente: Badge de Rol
Muestra el rol de una persona con un color distintivo.
"""

import flet as ft
from src.presentacion.theme import colors


# Paleta de colores por rol
ROLE_COLORS = {
    "Propietario": colors.SUCCESS,      # Verde
    "Arrendatario": colors.INFO,        # Azul
    "Codeudor": colors.WARNING,         # Amarillo/Ámbar
    "Asesor": colors.ADMIN_BADGE        # Violeta
}


class RoleBadge(ft.Container):
    """
    Badge visual para mostrar el rol de una persona.
    
    Args:
        role_name: Nombre del rol ("Propietario", "Arrendatario", etc.)
        small: Si True, tamaño reducido para listas compactas
    """
    
    def __init__(self, role_name: str, small: bool = False):
        super().__init__()
        self.role_name = role_name
        self.small = small
        
        # Obtener color según rol
        bg_color = ROLE_COLORS.get(role_name, colors.SECONDARY)
        
        # Configurar estilos
        self.bgcolor = bg_color
        self.border_radius = 12 if not small else 8
        self.padding = ft.padding.symmetric(horizontal=10, vertical=4) if not small else ft.padding.symmetric(horizontal=6, vertical=2)
        
        # Contenido
        self.content = ft.Text(
            role_name,
            size=12 if not small else 10,
            weight=ft.FontWeight.W_500,
            color=colors.TEXT_ON_PRIMARY
        )
