import reflex as rx
from src.presentacion_reflex import styles


def theme_toggle() -> rx.Component:
    """
    Elite Theme Toggle Component.
    Switches between Light and Dark mode with a smooth, premium feel.
    """
    return rx.segmented_control.root(
        rx.segmented_control.item(
            rx.icon("sun", size=16),
            value="light",
            content="Claro",  # Tooltip fallback
        ),
        rx.segmented_control.item(
            rx.icon("moon", size=16),
            value="dark",
            content="Oscuro",
        ),
        on_change=rx.toggle_color_mode,
        variant="surface",
        size="2",
        radius="full",
        cursor="pointer",
    )


def theme_toggle_icon() -> rx.Component:
    """
    Compact version (Icon only) for headers or tight spaces.
    Neumorphism Executive Edition.
    """
    return rx.tooltip(
        rx.button(
            rx.cond(
                rx.color_mode == "light",
                rx.icon("moon", size=18, color="var(--gray-11)"),
                rx.icon("sun", size=18, color="var(--gray-11)"),
            ),
            on_click=rx.toggle_color_mode,
            size="2",  # Reducido para encajar con el stack apretado
            padding="2",  # Homologado con los demás botones
            radius="full",
            background=styles.BG_PANEL,
            border="none",
            box_shadow=styles.NEU_SHADOW,
            _active={
                "box_shadow": styles.NEU_INSET,
                "transform": "scale(0.95)",
            },
            _hover={
                "transform": "translateY(-1px)",
                "box_shadow": styles.NEU_SHADOW,  # Mantener sombra en hover
            },
            transition="all 0.3s cubic-bezier(0.4, 0, 0.2, 1)",
            width="32px",
            height="32px",
            display="flex",
            align_items="center",
            justify_content="center",
        ),
        content="Cambiar Tema",
    )
