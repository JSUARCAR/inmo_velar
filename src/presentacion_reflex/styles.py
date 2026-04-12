import reflex as rx

"""
Sistema de Tokens de Diseño - Tema Claude (Anthropic)
Warm, editorial, parchment-toned aesthetic
"""

# --- Backgrounds ---
BG_APP = "var(--bg-app)"
BG_PANEL = "var(--bg-panel)"
BG_HOVER = "var(--bg-hover)"

# --- Text Colors (Warm neutrals) ---
TEXT_PRIMARY = "var(--text-primary)"  # #141413 Anthropic Near Black
TEXT_SECONDARY = "var(--text-secondary)"  # #5e5d59 Olive Gray
TEXT_TERTIARY = "var(--text-tertiary)"  # #87867f Stone Gray
TEXT_INVERTED = "white"

# --- Brand Colors ---
BRAND_PRIMARY = "var(--brand-primary)"  # #c96442 Terracotta
BRAND_ACCENT = "var(--brand-accent)"  # #d97757 Coral

# --- Typography Aliases ---
FONT_DISPLAY = "Playfair Display, serif"

# --- Font Size Tokens (mapped to CSS variables for centralized scaling) ---
FONT_SIZE_XS = "var(--font-size-xs)"
FONT_SIZE_SM = "var(--font-size-sm)"
FONT_SIZE_BASE = "var(--font-size-base)"
FONT_SIZE_MD = "var(--font-size-md)"
FONT_SIZE_LG = "var(--font-size-lg)"
FONT_SIZE_XL = "var(--font-size-xl)"

# --- Borders ---
BORDER_DEFAULT = "var(--border-default)"  # #f0eee6 Border Cream
BORDER_HOVER = "var(--border-emphasis)"  # #e8e6dc Border Warm
BORDER_COLOR = BORDER_DEFAULT

# --- Accents (Focus Blue - Only cool color) ---
ACCENT_COLOR = "var(--focus-blue)"  # #3898ec
ACCENT_BG_SOFT = "var(--blue-3)"

# --- Shadows - Ring System ---
SHADOW_RAISED_ELITE = "var(--shadow-raised-elite)"  # ring 0 0 0 1px
SHADOW_FLAT_ELITE = "var(--shadow-flat-elite)"  # ring variant
SHADOW_INSET_ELITE = "var(--shadow-inset-elite)"  # inset ring
SHADOW_MODAL_ELITE = "var(--shadow-modal-elite)"  # whisper shadow

# --- Aliases retrocompatibles ---
NEU_SHADOW = SHADOW_RAISED_ELITE
NEU_MODAL_SHADOW = SHADOW_MODAL_ELITE
NEU_INSET = SHADOW_INSET_ELITE
NEU_INSET_LIGHT = "var(--shadow-inset-light-elite)"

# --- Animaciones Globales ---
GLOBAL_TRANSITION = "all 0.3s cubic-bezier(0.4, 0, 0.2, 1)"

# --- Component Styles ---
NEU_DIVIDER_STYLE = {
    "height": "2px",
    "width": "100%",
    "background": f"linear-gradient(to bottom, {BORDER_DEFAULT} 0%, {BG_PANEL} 100%)",
    "margin_y": "1rem",
    "border_radius": "2px",
}

NEU_INPUT_STYLE = {
    "background": BG_PANEL,
    "border": f"1px solid {BORDER_DEFAULT}",
    "box_shadow": NEU_INSET,
    "transition": GLOBAL_TRANSITION,
    "border_radius": "12px",
    "padding": "0.75rem 1rem",
    "color": TEXT_PRIMARY,
    "height": "44px !important",
    "_focus": {
        "box_shadow": f"{NEU_INSET}, 0 0 0 2px {BRAND_PRIMARY}4D",
        "outline": "none",
        "border_color": BRAND_PRIMARY,
    },
    "_placeholder": {
        "color": TEXT_TERTIARY,
    },
}

NEU_SELECT_STYLE = {
    "background": BG_PANEL,
    "border": f"1px solid {BORDER_DEFAULT}",
    "box_shadow": NEU_INSET,
    "border_radius": "12px",
    "padding": "0 1rem",
    "color": TEXT_PRIMARY,
    "height": "44px !important",
    "display": "flex",
    "align_items": "center",
    "transition": GLOBAL_TRANSITION,
    "_focus": {
        "box_shadow": f"{NEU_INSET}, 0 0 0 2px {BRAND_PRIMARY}4D",
        "border_color": BRAND_PRIMARY,
    },
}

NEU_BUTTON_STYLE = {
    "background": BG_PANEL,
    "border": f"1px solid {BORDER_DEFAULT}",
    "box_shadow": SHADOW_RAISED_ELITE,
    "border_radius": "12px",
    "color": TEXT_PRIMARY,
    "height": "44px !important",
    "padding": "0 1.5rem",
    "font_weight": "600",
    "transition": GLOBAL_TRANSITION,
    "cursor": "pointer",
    "_hover": {
        "transform": "translateY(-2px)",
        "box_shadow": SHADOW_MODAL_ELITE,
        "background": BG_HOVER,
    },
    "_active": {
        "transform": "translateY(0)",
        "box_shadow": SHADOW_INSET_ELITE,
    },
}

NEU_PANEL_STYLE = {
    "background": BG_PANEL,
    "border": f"1px solid {BORDER_DEFAULT}",
    "border_radius": "16px",
    "padding": "1.5rem",
    "box_shadow": "var(--shadow-whisper)",
}

NEU_TOOLTIP_STYLE = {
    "background": BG_PANEL,
    "border": f"1px solid {BORDER_DEFAULT}",
    "box_shadow": SHADOW_MODAL_ELITE,
    "border_radius": "12px",
    "color": TEXT_PRIMARY,
    "padding": "0.75rem",
    "transition": GLOBAL_TRANSITION,
    "z_index": "9999",
}

# Botones de icono: ring-based (no more dual shadows)
NEU_ICON_BUTTON_STYLE = {
    "background": BG_PANEL,
    "border": f"1px solid {BORDER_DEFAULT}",
    "box_shadow": SHADOW_RAISED_ELITE,
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

# Card de contrato con whisper shadow y hover ring
NEU_CONTRACT_CARD_STYLE = {
    "background": BG_PANEL,
    "border": f"1px solid {BORDER_DEFAULT}",
    "border_radius": "16px",
    "box_shadow": "var(--shadow-whisper)",
    "transition": GLOBAL_TRANSITION,
    "_hover": {
        "box_shadow": SHADOW_MODAL_ELITE,
        "transform": "translateY(-4px)",
    },
}

NEU_INPUT_STYLE = {
    "background": BG_PANEL,
    "box_shadow": NEU_INSET,
    "border": f"1px solid {BORDER_DEFAULT}",
    "transition": GLOBAL_TRANSITION,
    "border_radius": "12px",
    "padding": "0.75rem 1rem",
    "color": TEXT_PRIMARY,
    "height": "44px !important",
    "_focus": {
        "box_shadow": NEU_INSET + f", 0 0 0 2px {BRAND_PRIMARY}4D",
        "outline": "none",
        "border_color": BRAND_PRIMARY,
    },
    "_placeholder": {
        "color": TEXT_TERTIARY,
    },
}

NEU_SELECT_STYLE = {
    "background": BG_PANEL,
    "box_shadow": NEU_INSET,
    "border": f"1px solid {BORDER_DEFAULT}",
    "border_radius": "12px",
    "padding": "0 1rem",
    "color": TEXT_PRIMARY,
    "height": "44px !important",
    "display": "flex",
    "align_items": "center",
    "transition": GLOBAL_TRANSITION,
    "_focus": {
        "box_shadow": NEU_INSET + f", 0 0 0 2px {BRAND_PRIMARY}4D",
        "border_color": BRAND_PRIMARY,
    },
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
    },
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
