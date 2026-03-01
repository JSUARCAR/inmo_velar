import reflex as rx

"""
Sistema de Tokens de Diseño Semántico (Dark Mode Ready)
Usamos rx.color(scale, step) para que Reflex maneje automáticamente 
la inversión de colores en Modo Oscuro.
"""

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

# Alias para compatibilidad con código existente
BORDER_COLOR = BORDER_DEFAULT

# --- Component Styles ---
NEU_INPUT_STYLE = {
    "background": BG_PANEL,
    "box_shadow": NEU_INSET,
    "border": "none",
    "transition": "all 0.2s ease",
    "border_radius": "10px",
    "padding": "0.5rem 1rem",
    "color": TEXT_PRIMARY,
    "_focus": {
        "box_shadow": f"{NEU_INSET}, 0 0 0 2px rgba(102, 126, 234, 0.3)",
        "outline": "none",
    },
    "_placeholder": {
        "color": TEXT_TERTIARY,
    }
}

NEU_SELECT_STYLE = {
    "background": BG_PANEL,
    "box_shadow": NEU_INSET,
    "border": "none",
    "border_radius": "10px",
    "padding": "0 0.5rem",
    "color": TEXT_PRIMARY,
    "transition": "all 0.2s ease",
    "_focus": {
        "box_shadow": f"{NEU_INSET}, 0 0 0 2px rgba(102, 126, 234, 0.3)",
    }
}

NEU_BUTTON_STYLE = {
    "background": BG_PANEL,
    "box_shadow": NEU_SHADOW,
    "border": "none",
    "border_radius": "10px",
    "color": TEXT_PRIMARY,
    "transition": "all 0.2s cubic-bezier(0.4, 0, 0.2, 1)",
    "cursor": "pointer",
    "_hover": {
        "transform": "translateY(-2px)",
        "box_shadow": NEU_MODAL_SHADOW,
        "background": BG_HOVER,
    },
    "_active": {
        "transform": "translateY(0)",
        "box_shadow": NEU_INSET,
    }
}
