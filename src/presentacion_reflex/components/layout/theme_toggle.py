import reflex as rx

def theme_toggle() -> rx.Component:
    """
    Elite Theme Toggle Component.
    Switches between Light and Dark mode with a smooth, premium feel.
    """
    return rx.segmented_control.root(
        rx.segmented_control.item(
            rx.icon("sun", size=16),
            value="light",
            content="Claro", # Tooltip fallback
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
    """
    return rx.tooltip(
        rx.button(
            rx.cond(
                rx.color_mode == "light",
                rx.icon("moon", size=18),
                rx.icon("sun", size=18),
            ),
            on_click=rx.toggle_color_mode,
            variant="ghost",
            size="3",
            color="gray",
            radius="full",
            _hover={
                "background": rx.color("gray", 3),
                "transform": "rotate(15deg)",
            },
            transition="all 0.3s ease",
        ),
        content="Cambiar Tema",
    )
