import reflex as rx

"""
Sistema de Tokens de Diseño - Tema Claude (Anthropic)
Warm, editorial, parchment-toned aesthetic
"""

__all__ = [
    "BG_APP",
    "BG_PANEL",
    "BG_HOVER",
    "TEXT_PRIMARY",
    "TEXT_SECONDARY",
    "TEXT_TERTIARY",
    "TEXT_INVERTED",
    "BRAND_PRIMARY",
    "BRAND_ACCENT",
    "ACCENT_COLOR",
    "ACCENT_BG_SOFT",
    "ACCENT_BG",
    "FONT_DISPLAY",
    "FONT_SANS",
    "FONT_SIZE_XS",
    "FONT_SIZE_SM",
    "FONT_SIZE_BASE",
    "FONT_SIZE_MD",
    "FONT_SIZE_LG",
    "FONT_SIZE_XL",
    "BORDER_DEFAULT",
    "BORDER_HOVER",
    "BORDER_COLOR",
    "SHADOW_RING",
    "SHADOW_WHISPER",
    "SHADOW_ELEVATED",
    "SHADOW_INSET",
    "GLOBAL_TRANSITION",
    "TRANSITION_FAST",
    "TRANSITION_SLOW",
    "NEU_DIVIDER_STYLE",
    "NEU_INPUT_STYLE",
    "NEU_SELECT_STYLE",
    "NEU_BUTTON_STYLE",
    "NEU_BUTTON_PRIMARY_STYLE",
    "NEU_PANEL_STYLE",
    "NEU_CARD_STYLE",
    "NEU_TOOLTIP_STYLE",
    "NEU_ICON_BUTTON_STYLE",
    "NEU_CONTRACT_CARD_STYLE",
    "NEU_BADGE_STYLE",
    "SHADOW_RAISED_ELITE",
    "SHADOW_FLAT_ELITE",
    "SHADOW_MODAL_ELITE",
    "SHADOW_INSET_ELITE",
    "NEU_SHADOW",
    "NEU_MODAL_SHADOW",
    "NEU_PANEL_SHADOW",
    "NEU_INSET",
    "NEU_INSET_LIGHT",
    "NEU_PANEL",
    "BASE_STYLE",
    "Z_MODAL",
    "Z_POPOVER",
    "Z_TOOLTIP",
]

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
ACCENT_COLOR = BRAND_PRIMARY
ACCENT_BG_SOFT = "rgba(201, 100, 66, 0.1)"  # Soft Terracotta
ACCENT_BG = "rgba(201, 100, 66, 0.2)"

# --- Typography Aliases ---
FONT_DISPLAY = "Playfair Display, serif"
FONT_SANS = "Inter, sans-serif"

# --- Font Size Tokens ---
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

# --- Shadows - Anthropic System (Elite) ---
# Ring-based: 1px border simulation with precise coloring
SHADOW_RING = f"0px 0px 0px 1px {BORDER_DEFAULT}"
SHADOW_WHISPER = "0px 4px 24px rgba(0,0,0,0.05)"
SHADOW_ELEVATED = "0px 12px 48px rgba(0,0,0,0.08)"
SHADOW_INSET = "inset 0px 2px 4px rgba(0,0,0,0.05)"


# --- Animaciones Globales ---
GLOBAL_TRANSITION = "all 0.3s cubic-bezier(0.4, 0, 0.2, 1)"
TRANSITION_FAST = "0.15s ease-out"
TRANSITION_SLOW = "0.4s cubic-bezier(0.4, 0, 0.2, 1)"

# --- Z-Index Escala Global (Elite) ---
Z_MODAL = "1000"
Z_POPOVER = "1050"
Z_TOOLTIP = "1100"

# --- Component Styles ---
NEU_DIVIDER_STYLE = {
    "height": "1px",
    "width": "100%",
    "background": BORDER_DEFAULT,
    "margin_y": "1rem",
}

NEU_INPUT_STYLE = {
    "background": BG_PANEL,
    "border": f"1px solid {BORDER_DEFAULT}",
    "box_shadow": SHADOW_INSET,
    "transition": GLOBAL_TRANSITION,
    "border_radius": "12px",
    "padding": "0.75rem 1rem",
    "color": TEXT_PRIMARY,
    "height": "44px !important",
    "_focus": {
        "box_shadow": f"{SHADOW_INSET}, 0 0 0 2px {BRAND_PRIMARY}4D",
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
    "box_shadow": SHADOW_INSET,
    "border_radius": "12px",
    "padding": "0 1rem",
    "color": TEXT_PRIMARY,
    "height": "44px !important",
    "display": "flex",
    "align_items": "center",
    "transition": GLOBAL_TRANSITION,
    "_focus": {
        "box_shadow": f"{SHADOW_INSET}, 0 0 0 2px {BRAND_PRIMARY}4D",
        "border_color": BRAND_PRIMARY,
    },
}

NEU_BUTTON_STYLE = {
    "background": BG_PANEL,
    "border": f"1px solid {BORDER_DEFAULT}",
    "box_shadow": SHADOW_RING,
    "border_radius": "12px",
    "color": TEXT_PRIMARY,
    "height": "44px !important",
    "padding": "0 1.5rem",
    "font_weight": "600",
    "transition": GLOBAL_TRANSITION,
    "cursor": "pointer",
    "_hover": {
        "transform": "translateY(-2px)",
        "box_shadow": SHADOW_WHISPER,
        "background": BG_HOVER,
    },
    "_active": {
        "transform": "translateY(0)",
        "box_shadow": SHADOW_INSET,
    },
}

NEU_BUTTON_PRIMARY_STYLE = {
    **NEU_BUTTON_STYLE,
    "background": BRAND_PRIMARY,
    "color": "white",
    "border": "none",
    "_hover": {
        **NEU_BUTTON_STYLE.get("_hover", {}),
        "background": BRAND_ACCENT,
        "box_shadow": f"0 8px 16px {BRAND_PRIMARY}33",
    },
}

NEU_PANEL_STYLE = {
    "background": BG_PANEL,
    "border": f"1px solid {BORDER_DEFAULT}",
    "border_radius": "16px",
    "padding": "1.5rem",
    "box_shadow": SHADOW_WHISPER,
}

NEU_CARD_STYLE = {
    **NEU_PANEL_STYLE,
    "transition": GLOBAL_TRANSITION,
    "_hover": {
        "box_shadow": SHADOW_ELEVATED,
        "transform": "translateY(-4px)",
        "border_color": BRAND_PRIMARY,
    },
}

NEU_TOOLTIP_STYLE = {
    "background": BG_PANEL,
    "border": f"1px solid {BORDER_DEFAULT}",
    "box_shadow": SHADOW_WHISPER,
    "border_radius": "12px",
    "color": TEXT_PRIMARY,
    "padding": "0.75rem",
    "transition": GLOBAL_TRANSITION,
    "z_index": Z_TOOLTIP,
    "pointer_events": "auto",
}

NEU_ICON_BUTTON_STYLE = {
    "background": BG_PANEL,
    "border": f"1px solid {BORDER_DEFAULT}",
    "box_shadow": SHADOW_RING,
    "border_radius": "10px",
    "color": TEXT_PRIMARY,
    "transition": GLOBAL_TRANSITION,
    "cursor": "pointer",
    "display": "flex",
    "align_items": "center",
    "justify_content": "center",
    "_hover": {
        "background": BG_HOVER,
        "transform": "scale(1.05)",
    },
    "_active": {
        "box_shadow": SHADOW_INSET,
        "transform": "scale(0.97)",
    },
}

NEU_CONTRACT_CARD_STYLE = NEU_CARD_STYLE

# --- Estilos de Badge/Tag ---
NEU_BADGE_STYLE = {
    "padding": "4px 12px",
    "border_radius": "20px",
    "font_size": FONT_SIZE_XS,
    "font_weight": "bold",
    "text_transform": "uppercase",
    "letter_spacing": "0.05em",
}

# --- Aliases para compatibilidad ---
SHADOW_RAISED_ELITE = SHADOW_RING
SHADOW_FLAT_ELITE = SHADOW_RING
SHADOW_MODAL_ELITE = SHADOW_WHISPER
SHADOW_INSET_ELITE = SHADOW_INSET

NEU_SHADOW = SHADOW_RING
NEU_MODAL_SHADOW = SHADOW_WHISPER
NEU_PANEL_SHADOW = SHADOW_WHISPER
NEU_INSET = SHADOW_INSET_ELITE
NEU_INSET_LIGHT = SHADOW_INSET_ELITE
NEU_PANEL = NEU_PANEL_STYLE

BASE_STYLE = {
    "::selection": {
        "background_color": BRAND_PRIMARY,
        "color": "white",
    },
    rx.dialog.content: {
        "pointer_events": "auto",
        "z_index": Z_MODAL,
    },
    rx.alert_dialog.content: {
        "pointer_events": "auto",
        "z_index": Z_MODAL,
    },
    rx.popover.content: {
        "pointer_events": "auto",
        "z_index": Z_POPOVER,
    },
    rx.hover_card.content: {
        "pointer_events": "auto",
        "z_index": Z_TOOLTIP,
    },
}
