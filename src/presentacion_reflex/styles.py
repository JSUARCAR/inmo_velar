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
BG_APP = "var(--bg-app)"

# Fondo de paneles, tarjetas, sidebar, modales
# En el Neumorfismo Clásico, el fondo de panel es idéntico a la app
BG_PANEL = "var(--bg-panel)"
BG_HOVER = "var(--bg-hover)"

# --- Neumorphism Shadows ---
# Sombra Extruida (Elemento elevado)
NEU_SHADOW = "var(--neu-shadow)"

# Sombra para Modales (Flota sobre el overlay oscuro sin producir resplandor blanco excesivo)
NEU_MODAL_SHADOW = "var(--neu-modal-shadow)"

# Sombra Hundida (Elemento presionado o inactivo estructuralmente)
NEU_INSET = "var(--neu-inset)"

NEU_INSET_LIGHT = "var(--neu-inset-light)"

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
