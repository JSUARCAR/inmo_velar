"""
Sistema de Estilos Reutilizables - Inmobiliaria Velar
Definiciones de estilos consistentes para componentes Flet
"""

import flet as ft
from src.presentacion.theme import colors


# ============================================================================
# ESTILOS DE CARDS
# ============================================================================

def card_elevated():
    """Card con elevacion media (dashboard widgets)."""
    return ft.Container(
        bgcolor=colors.SURFACE,
        border_radius=12,
        padding=20,
        shadow=ft.BoxShadow(
            spread_radius=1,
            blur_radius=10,
            color=f"rgba(0, 0, 0, 0.08)",
            offset=ft.Offset(0, 4)
        )
    )


def card_outlined():
    """Card con borde sutil (formularios, listados)."""
    return ft.Container(
        bgcolor=colors.BACKGROUND,
        border=ft.border.all(1, colors.BORDER_DEFAULT),
        border_radius=8,
        padding=16
    )


def card_critical():
    """Card para alertas criticas (mora de pagos)."""
    return ft.Container(
        bgcolor=colors.ERROR,
        border_radius=12,
        padding=20,
        gradient=ft.LinearGradient(
            begin=ft.alignment.top_left,
            end=ft.alignment.bottom_right,
            colors=[colors.ERROR, "#DC2626"]
        )
    )


# ============================================================================
# ESTILOS DE BOTONES
# ============================================================================

def button_primary():
    """Boton primario (acciones principales)."""
    return ft.ButtonStyle(
        color=colors.TEXT_ON_PRIMARY,
        bgcolor=colors.PRIMARY,
        padding=ft.padding.symmetric(horizontal=24, vertical=12),
        shape=ft.RoundedRectangleBorder(radius=8)
    )


def button_secondary():
    """Boton secundario (acciones alternativas)."""
    return ft.ButtonStyle(
        color=colors.PRIMARY,
        bgcolor=colors.SURFACE,
        padding=ft.padding.symmetric(horizontal=24, vertical=12),
        shape=ft.RoundedRectangleBorder(radius=8)
    )


def button_danger():
    """Boton de peligro (eliminar, cancelar)."""
    return ft.ButtonStyle(
        color=colors.TEXT_ON_PRIMARY,
        bgcolor=colors.ERROR,
        padding=ft.padding.symmetric(horizontal=24, vertical=12),
        shape=ft.RoundedRectangleBorder(radius=8)
    )


# ============================================================================
# ESTILOS DE INPUTS
# ============================================================================

def text_field_style():
    """Estilo base para campos de texto."""
    return {
        "border_color": colors.BORDER_DEFAULT,
        "focused_border_color": colors.BORDER_FOCUS,
        "border_radius": 8,
        "content_padding": 12,
        "text_size": 14,
        "cursor_color": colors.PRIMARY
    }


def text_field_error():
    """Estilo para campo con error."""
    return {
        **text_field_style(),
        "border_color": colors.ERROR,
        "focused_border_color": colors.ERROR,
        "error_style": ft.TextStyle(color=colors.ERROR, size=12)
    }


# ============================================================================
# ESTILOS DE TIPOGRAFIA
# ============================================================================

def heading_1():
    """Titulo principal (H1)."""
    return ft.TextStyle(
        size=32,
        weight=ft.FontWeight.BOLD,
        color=colors.TEXT_PRIMARY,
        font_family="Outfit"
    )


def heading_2():
    """Titulo secundario (H2)."""
    return ft.TextStyle(
        size=24,
        weight=ft.FontWeight.W_600,
        color=colors.TEXT_PRIMARY,
        font_family="Outfit"
    )


def heading_3():
    """Titulo terciario (H3)."""
    return ft.TextStyle(
        size=18,
        weight=ft.FontWeight.W_600,
        color=colors.TEXT_PRIMARY,
        font_family="Inter"
    )


def body_text():
    """Texto de cuerpo normal."""
    return ft.TextStyle(
        size=14,
        color=colors.TEXT_PRIMARY,
        font_family="Inter"
    )


def caption_text():
    """Texto pequeño (captions, timestamps)."""
    return ft.TextStyle(
        size=12,
        color=colors.TEXT_SECONDARY,
        font_family="Inter"
    )


def breadcrumb_text():
    """Texto para breadcrumbs (navegación)."""
    return ft.TextStyle(
        size=14,
        color=colors.TEXT_SECONDARY,
        weight=ft.FontWeight.W_500,
        font_family="Inter"
    )


# ============================================================================
# ESTILOS DE BADGES
# ============================================================================

def badge_admin():
    """Badge para rol Administrador."""
    return ft.Container(
        content=ft.Text("ADMIN", size=10, weight=ft.FontWeight.BOLD, color=colors.TEXT_ON_PRIMARY),
        bgcolor=colors.ADMIN_BADGE,
        border_radius=4,
        padding=ft.padding.symmetric(horizontal=8, vertical=4)
    )


def badge_asesor():
    """Badge para rol Asesor."""
    return ft.Container(
        content=ft.Text("ASESOR", size=10, weight=ft.FontWeight.BOLD, color=colors.TEXT_ON_PRIMARY),
        bgcolor=colors.ASESOR_BADGE,
        border_radius=4,
        padding=ft.padding.symmetric(horizontal=8, vertical=4)
    )


def badge_alert_count(count: int):
    """Badge contador de alertas."""
    return ft.Container(
        content=ft.Text(str(count), size=10, weight=ft.FontWeight.BOLD, color=colors.TEXT_ON_PRIMARY),
        bgcolor=colors.ERROR,
        border_radius=10,
        width=20,
        height=20,
        alignment=ft.alignment.center
    )


# ============================================================================
# ANIMACIONES
# ============================================================================

TRANSITION_DURATION = 200  # ms
PULSE_DURATION = 1000      # ms para alertas criticas
