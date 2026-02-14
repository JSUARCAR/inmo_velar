import reflex as rx

from src.presentacion_reflex.components.layout.sidebar import sidebar_footer, sidebar_items
from src.presentacion_reflex.state.configuracion_state import ConfiguracionState


def mobile_nav() -> rx.Component:
    """
    Barra de navegación móvil 'Expert Elite' con efecto Glassmorphism y Drawer.
    Visible solo en móviles y tablets.
    """
    return rx.box(
        rx.hstack(
            # Hamburger Menu Trigger with enhanced styling
            rx.drawer.root(
                rx.drawer.trigger(
                    rx.icon_button(
                        rx.icon("menu", size=26, color="white"),
                        variant="ghost",
                        size="3",
                        _hover={
                            "background": "rgba(255, 255, 255, 0.15)",
                            "transform": "scale(1.05)",
                        },
                        transition="all 0.2s ease",
                    )
                ),
                rx.drawer.overlay(
                    background_color="rgba(0, 0, 0, 0.7)", backdrop_filter="blur(2px)"
                ),
                rx.drawer.portal(
                    rx.drawer.content(
                        rx.vstack(
                            # Drawer Header with Gradient
                            rx.box(
                                rx.hstack(
                                    rx.hstack(
                                        rx.cond(
                                            ConfiguracionState.logo_preview != "",
                                            rx.image(
                                                src=ConfiguracionState.logo_preview,
                                                height="40px",
                                                width="auto",
                                                object_fit="contain",
                                                alt="Logo",
                                            ),
                                            rx.icon("building", size=26, color="white"),
                                        ),
                                        rx.heading(
                                            "Inmobiliaria Velar",
                                            size="5",
                                            color="white",
                                            weight="bold",
                                            letter_spacing="-0.5px",
                                        ),
                                        align="center",
                                        spacing="3",
                                    ),
                                    rx.spacer(),
                                    rx.drawer.close(
                                        rx.icon_button(
                                            rx.icon("x", size=24, color="white"),
                                            variant="ghost",
                                            size="2",
                                            _hover={
                                                "background": "rgba(255, 255, 255, 0.2)",
                                                "transform": "rotate(90deg)",
                                            },
                                            transition="all 0.3s ease",
                                        )
                                    ),
                                    width="100%",
                                    align="center",
                                ),
                                padding="6",
                                background="linear-gradient(135deg, #1f2937 0%, #111827 100%)",
                                border_bottom="1px solid rgba(255, 255, 255, 0.05)",
                            ),
                            # Drawer Content (Reused Sidebar Items)
                            rx.box(
                                sidebar_items(),
                                padding_y="4",
                                padding_x="2",
                                overflow_y="auto",
                                flex="1",
                                width="100%",
                                class_name="scrollbar-hide",  # Optional: hide scrollbar if configured
                            ),
                            # Drawer Footer (Reused Sidebar Footer)
                            rx.box(
                                sidebar_footer(),
                                width="100%",
                                padding="4", # Added padding for better look on white bg
                            ),
                            height="100%",
                            width="100%",
                            spacing="0",
                            background="white",  # Changed to white ensuring high contrast
                        ),
                        top="0",
                        left="0",
                        height="100%",
                        width="85%",
                        max_width="320px",
                        background="white",  # Changed to white
                        position="fixed",
                        z_index="100",
                        box_shadow="10px 0 50px rgba(0,0,0,0.5)",
                        border_right="1px solid rgba(0,0,0,0.1)",
                    )
                ),
                direction="left",
            ),
            # Title / Logo with Gradient Text
            rx.hstack(
                rx.cond(
                    ConfiguracionState.logo_preview != "",
                    rx.image(
                        src=ConfiguracionState.logo_preview,
                        height="32px",
                        width="auto",
                        object_fit="contain",
                        alt="Logo",
                    ),
                    rx.icon("building", size=22, color="#60a5fa"),
                ),
                rx.heading(
                    "Inmobiliaria Velar",
                    size="4",
                    weight="bold",
                    background="linear-gradient(to right, #ffffff, #93c5fd)",
                    background_clip="text",
                    color="transparent",  # Fallback handled by background_clip usually, or use darker bg
                    _hover={"background": "linear-gradient(to right, #93c5fd, #ffffff)"},
                    transition="all 0.5s ease",
                    cursor="default",
                ),
                align="center",
                spacing="2",
            ),
            rx.spacer(),
            # User Avatar (Mini) with Ring
            rx.box(
                rx.avatar(
                    fallback="IV",
                    size="2",
                    radius="full",
                    color="white",
                    background="linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)",
                    border="2px solid rgba(255,255,255,0.2)",
                ),
                _hover={"transform": "scale(1.1)"},
                transition="all 0.2s cubic-bezier(0.175, 0.885, 0.32, 1.275)",
            ),
            width="100%",
            align="center",
            padding_x="5",
            padding_y="3",
            spacing="4",
        ),
        # Container styles
        width="100%",
        position="sticky",
        top="0",
        z_index="50",
        background="rgba(17, 24, 39, 0.75)",  # More slightly transparent
        backdrop_filter="blur(16px) saturate(180%)",  # Advanced glass effect
        border_bottom="1px solid rgba(255, 255, 255, 0.08)",
        box_shadow="0 4px 30px rgba(0, 0, 0, 0.1)",
        display=["block", "block", "none", "none", "none"],
    )
