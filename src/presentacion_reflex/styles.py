import reflex as rx

"""
Sistema de Tokens de Diseño Semántico (Dark Mode Ready)
Usamos variables de CSS puro para evitar problemas de compilación con rx.color en SSR/Memoization.
"""

# --- Backgrounds ---
BG_APP = "var(--bg-app)"
BG_PANEL = "var(--bg-panel)"
BG_HOVER = "var(--bg-hover)"

# --- Neumorphism Shadows (aliases retrocompatibles) ---
NEU_SHADOW = "var(--neu-shadow)"
NEU_MODAL_SHADOW = "var(--neu-modal-shadow)"
NEU_INSET = "var(--neu-inset)"
NEU_INSET_LIGHT = "var(--neu-inset-light)"

# --- ELITE Named Shadows (fuente de verdad) ---
SHADOW_RAISED_ELITE = "var(--shadow-raised-elite)"
SHADOW_FLAT_ELITE   = "var(--shadow-flat-elite)"
SHADOW_INSET_ELITE  = "var(--shadow-inset-elite)"
SHADOW_MODAL_ELITE  = "var(--shadow-modal-elite)"

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

# --- Animaciones Globales ---
GLOBAL_TRANSITION = "all 0.3s cubic-bezier(0.4, 0, 0.2, 1)"

# --- Component Styles ---
NEU_DIVIDER_STYLE = {
    "height": "2px",
    "width": "100%",
    "background": f"linear-gradient(to bottom, rgba(184, 195, 218, 0.4) 0%, rgba(255, 255, 255, 0.8) 100%)",
    "margin_y": "1rem",
    "border_radius": "2px",
}

NEU_INPUT_STYLE = {
    "background": BG_PANEL,
    "box_shadow": NEU_INSET,
    "border": f"1px solid {BORDER_DEFAULT}",
    "transition": GLOBAL_TRANSITION,
    "border_radius": "12px",
    "padding": "0.75rem 1rem",
    "color": TEXT_PRIMARY,
    "height": "44px !important",  # Forzado
    "_focus": {
        "box_shadow": NEU_INSET + ", 0 0 0 2px rgba(102, 126, 234, 0.3)",
        "outline": "none",
        "border_color": ACCENT_COLOR,
    },
    "_placeholder": {
        "color": TEXT_TERTIARY,
    }
}

NEU_SELECT_STYLE = {
    "background": BG_PANEL,
    "box_shadow": NEU_INSET,
    "border": f"1px solid {BORDER_DEFAULT}",
    "border_radius": "12px",
    "padding": "0 1rem",
    "color": TEXT_PRIMARY,
    "height": "44px !important",  # Forzado
    "display": "flex",
    "align_items": "center",
    "transition": GLOBAL_TRANSITION,
    "_focus": {
        "box_shadow": NEU_INSET + ", 0 0 0 2px rgba(102, 126, 234, 0.3)",
        "border_color": ACCENT_COLOR,
    }
}

NEU_BUTTON_STYLE = {
    "background": BG_PANEL,
    "box_shadow": NEU_SHADOW,
    "border": f"1px solid {BORDER_DEFAULT}",
    "border_radius": "12px",
    "color": TEXT_PRIMARY,
    "height": "44px !important",  # Forzado
    "padding": "0 1.5rem",
    "font_weight": "600",
    "transition": GLOBAL_TRANSITION,
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

NEU_PANEL_STYLE = {
    "background": BG_PANEL,
    "box_shadow": NEU_SHADOW,
    "border": "none",
    "border_radius": "16px",
    "padding": "1.5rem",
}

NEU_TOOLTIP_STYLE = {
    "background": BG_PANEL,
    "box_shadow": NEU_MODAL_SHADOW,
    "border": f"1px solid {BORDER_DEFAULT}",
    "border_radius": "12px",
    "color": TEXT_PRIMARY,
    "padding": "0.75rem",
    "transition": GLOBAL_TRANSITION,
    "z_index": "9999",
}

# Botones de icono: raised → flat → inset (sombras táctiles)
NEU_ICON_BUTTON_STYLE = {
    "background": BG_PANEL,
    "box_shadow": SHADOW_RAISED_ELITE,
    "border": f"1px solid {BORDER_DEFAULT}",
    "border_radius": "10px",
    "color": TEXT_PRIMARY,
    "transition": GLOBAL_TRANSITION,
    "cursor": "pointer",
    "_hover": {
        "box_shadow": SHADOW_FLAT_ELITE,
        "background": BG_HOVER,
    },
    "_active": {
        "box_shadow": SHADOW_INSET_ELITE,
        "transform": "scale(0.97)",
    },
}

# Card de contrato con sombra raised y hover elevado
NEU_CONTRACT_CARD_STYLE = {
    "background": BG_PANEL,
    "box_shadow": SHADOW_RAISED_ELITE,
    "border": "none",
    "border_radius": "16px",
    "transition": GLOBAL_TRANSITION,
    "_hover": {
        "box_shadow": SHADOW_MODAL_ELITE,
        "transform": "translateY(-4px)",
    },
}
