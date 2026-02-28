import reflex as rx

"""
Sistema de Tokens de Diseño Semántico (Dark Mode Ready)
Usamos rx.color(scale, step) para que Reflex maneje automáticamente 
la inversión de colores en Modo Oscuro.
"""

# --- Backgrounds ---
# Fondo general de la aplicación (detrás de las tarjetas)
# --- Backgrounds ---
# Fondo general de la aplicación (detrás de las tarjetas)
BG_APP = rx.color_mode_cond(light="#e6e9ef", dark="#18191c")

# Fondo de paneles, tarjetas, sidebar, modales
# En el Neumorfismo Clásico, el fondo de panel es idéntico a la app
BG_PANEL = rx.color_mode_cond(light="#e6e9ef", dark="#18191c")
BG_HOVER = rx.color_mode_cond(light="#dbe0e8", dark="#1e1f23")

# --- Neumorphism Shadows ---
# Sombra Extruida (Elemento elevado)
NEU_SHADOW = rx.color_mode_cond(
    light="10px 10px 20px rgba(184, 195, 218, 0.45), -10px -10px 20px rgba(255, 255, 255, 0.8)",
    dark="10px 10px 20px rgba(0, 0, 0, 0.8), -10px -10px 20px rgba(45, 47, 53, 0.4)"
)

# Sombra para Modales (Flota sobre el overlay oscuro sin producir resplandor blanco excesivo)
NEU_MODAL_SHADOW = rx.color_mode_cond(
    light="10px 10px 30px rgba(184, 195, 218, 0.6), -5px -5px 15px rgba(255, 255, 255, 0.2)",
    dark="15px 15px 40px rgba(0, 0, 0, 0.9), -5px -5px 15px rgba(45, 47, 53, 0.2)"
)

# Sombra Hundida (Elemento presionado o inactivo estructuralmente)
NEU_INSET = rx.color_mode_cond(
    light="inset 6px 6px 12px rgba(184, 195, 218, 0.5), inset -6px -6px 12px rgba(255, 255, 255, 0.95)",
    dark="inset 6px 6px 12px rgba(0, 0, 0, 0.9), inset -6px -6px 12px rgba(45, 47, 53, 0.5)"
)

NEU_INSET_LIGHT = rx.color_mode_cond(
    light="inset 2px 2px 6px rgba(184, 195, 218, 0.4), inset -2px -2px 6px rgba(255, 255, 255, 0.9)",
    dark="inset 2px 2px 6px rgba(0, 0, 0, 0.6), inset -2px -2px 6px rgba(45, 47, 53, 0.4)"
)

# --- Textos ---
# Texto Principal (Títulos, Body fuerte)
# Light: Negro/Gris muy oscuro | Dark: Blanco/Gris muy claro
TEXT_PRIMARY = rx.color("gray", 12)

# Texto Secundario (Subtítulos, descripciones)
TEXT_SECONDARY = rx.color("gray", 11)

# Texto Terciario (Placeholders, disabled)
TEXT_TERTIARY = rx.color("gray", 10)

# Texto Invertido (Para botones sólidos oscuros con texto claro siempre)
TEXT_INVERTED = "white" # High contrast fixed

# --- Bordes ---
BORDER_DEFAULT = rx.color("gray", 6)
BORDER_HOVER = rx.color("gray", 8)

# --- Accents (Brand) ---
# Usamos escala 'blue' o 'indigo' según branding
ACCENT_COLOR = rx.color("blue", 9) # Color primario
ACCENT_BG_SOFT = rx.color("blue", 3) # Fondos suaves de acento
