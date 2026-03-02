import reflex as rx

"""
Sistema de Tokens de Diseño Semántico (Dark Mode Ready)
Usamos variables de CSS puro para evitar problemas de compilación con rx.color en SSR/Memoization.
"""

# --- Backgrounds ---
BG_APP = "var(--bg-app)"
BG_PANEL = "var(--bg-panel)"
BG_HOVER = "var(--bg-hover)"

# --- Neumorphism Shadows ---
NEU_SHADOW = "var(--neu-shadow)"
NEU_MODAL_SHADOW = "var(--neu-modal-shadow)"
NEU_INSET = "var(--neu-inset)"
NEU_INSET_LIGHT = "var(--neu-inset-light)"

# --- Textos ---
TEXT_PRIMARY = "var(--gray-12)"
TEXT_SECONDARY = "var(--gray-11)"
TEXT_TERTIARY = "var(--gray-10)"
TEXT_INVERTED = "white"

# --- Bordes ---
BORDER_DEFAULT = "var(--gray-6)"
BORDER_HOVER = "var(--gray-8)"

# --- Accents (Brand) ---
ACCENT_COLOR = "var(--blue-9)"
ACCENT_BG_SOFT = "var(--blue-3)"

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
        "box_shadow": NEU_INSET + ", 0 0 0 2px rgba(102, 126, 234, 0.3)",
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
        "box_shadow": NEU_INSET + ", 0 0 0 2px rgba(102, 126, 234, 0.3)",
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
