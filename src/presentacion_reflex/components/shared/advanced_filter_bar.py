import reflex as rx
from src.presentacion_reflex.styles import (
    NEU_FILTER_BAR_STYLE,
    NEU_BUTTON_STYLE,
    NEU_BADGE_STYLE,
    BRAND_PRIMARY,
    NEU_FILTER_INPUT_STYLE,
    NEU_FILTER_LABEL_STYLE,
)
from typing import Callable, List

def advanced_filter_bar(
    *children,
    search_placeholder: str = "Buscar...",
    on_search: Callable = None,
    search_value: str = "",
    on_clear: Callable = None,
    action_buttons: List[rx.Component] = None,
    **props
) -> rx.Component:
    """
    AdvancedFilterBar: Reusable filter container with standardized styling.
    """
    active_filter_count = props.pop("active_filter_count", 0)
    
    search_box = rx.box(
        rx.text("Buscar", style=NEU_FILTER_LABEL_STYLE),
        rx.input(
            placeholder=search_placeholder,
            value=search_value,
            on_change=on_search,
            style=NEU_FILTER_INPUT_STYLE,
            width="100%",
        ),
        width=["100%", "100%", "250px"]
    )

    
    # Action Buttons Container (Right aligned)
    actions = rx.flex(
        *(action_buttons or []),
        gap="3",
        align_items="center",
        justify_content="flex-end"
    )

    # Limpiar button with optional badge
    limpiar_btn = rx.button(
        rx.flex(
            rx.icon(tag="eraser", size=18),
            "Limpiar",
            rx.cond(
                active_filter_count > 0,
                rx.badge(
                    active_filter_count,
                    style=NEU_BADGE_STYLE,
                    background=BRAND_PRIMARY,
                    color="white",
                    margin_left="0.5rem"
                ),
                rx.fragment()
            ),
            align_items="center",
            gap="2"
        ),
        on_click=on_clear,
        style=NEU_BUTTON_STYLE,
        variant="surface",
        color_scheme="gray"
    )

    # Contenedor de filtros para Desktop
    desktop_filter_content = rx.flex(
        search_box,
        *children,
        direction="row",
        wrap="wrap",
        gap="4",
        spacing="3",
        width="100%",
        align_items="flex-end",
    )
    
    # Contenedor de filtros para Mobile
    mobile_filter_content = rx.flex(
        search_box,
        *children,
        direction="column",
        gap="4",
        spacing="3",
        width="100%",
    )
    
    # Drawer para Mobile
    mobile_drawer = rx.drawer.root(
        rx.drawer.trigger(
            rx.button(
                rx.icon("filter", size=18),
                rx.text("Filtros"),
                rx.cond(
                    active_filter_count > 0,
                    rx.badge(
                        active_filter_count,
                        style=NEU_BADGE_STYLE,
                        background=BRAND_PRIMARY,
                        color="white",
                        margin_left="0.5rem"
                    ),
                    rx.fragment()
                ),
                style=NEU_BUTTON_STYLE,
                variant="surface",
                color_scheme="indigo",
                width="100%",
            )
        ),
        rx.drawer.overlay(z_index="1000"),
        rx.drawer.portal(
            rx.drawer.content(
                rx.box(
                    rx.flex(
                        rx.drawer.title(rx.text("Filtros Avanzados", weight="bold")),
                        rx.drawer.close(
                            rx.icon_button(rx.icon("x", size=18), variant="ghost", color_scheme="gray")
                        ),
                        justify_content="space-between",
                        align_items="center",
                        margin_bottom="1.5rem"
                    ),
                    mobile_filter_content,
                    rx.flex(
                        rx.drawer.close(
                            limpiar_btn
                        ),
                        margin_top="2rem",
                        width="100%",
                        justify_content="center"
                    ),
                    padding="1.5rem",
                    background="white",
                ),
                background_color="white",
                top="auto",
                right="0",
                height="auto",
                bottom="0",
                left="0",
                width="100%",
                border_top_left_radius="16px",
                border_top_right_radius="16px",
                z_index="1001",
            )
        ),
        direction="bottom"
    )

    return rx.box(
        # DESKTOP VIEW
        rx.flex(
            rx.box(
                desktop_filter_content,
                width="100%"
            ),
            rx.flex(
                limpiar_btn,
                actions,
                gap="4",
                align_items="center",
                justify_content="space-between",
                width="100%",
                margin_top="1rem"
            ),
            direction="column",
            width="100%",
            display=rx.breakpoints(initial="none", md="flex")
        ),
        # MOBILE VIEW
        rx.flex(
            rx.box(
                mobile_drawer,
                width="100%",
            ),
            rx.flex(
                actions,
                gap="3",
                align_items="center",
                justify_content="space-between",
                width="100%",
                margin_top="1rem"
            ),
            direction="column",
            width="100%",
            display=rx.breakpoints(initial="flex", md="none")
        ),
        style=NEU_FILTER_BAR_STYLE,
        **props
    )
