import reflex as rx

"""
Sistema de Tokens de Diseño Semántico (Dark Mode Ready)
Usamos rx.color(scale, step) para que Reflex maneje automáticamente 
la inversión de colores en Modo Oscuro.
"""

# --- Backgrounds ---
# Fondo general de la aplicación (detrás de las tarjetas)
# Light: gray-2 (Gris muy claro) | Dark: gray-2 (Gris muy oscuro)
BG_APP = rx.color("gray", 2)

# Fondo de paneles, tarjetas, sidebar, modales
# Light: white (gray-1) | Dark: gris oscuro (gray-1) -> Usually "surface"
BG_PANEL = rx.color("gray", 1)  # Equivalent to "white" in light mode for surfaces
BG_HOVER = rx.color("gray", 3)

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
