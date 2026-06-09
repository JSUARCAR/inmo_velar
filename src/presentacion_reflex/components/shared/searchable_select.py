"""
Componente SearchableSelect - Reflex
Selectores con búsqueda accesibles y alineados con Claude Design System.
"""

import reflex as rx
from typing import Any, List, Union

from src.presentacion_reflex.components.neuro_elements import neuro_button, neuro_input
from src.presentacion_reflex import styles


def searchable_select(
    label: str,
    placeholder: str,
    value_label: Union[rx.Var[str], str],
    search_value: Union[rx.Var[str], str],
    menu_open: Union[rx.Var[bool], bool],
    filtered_options: Union[rx.Var[List[List[str]]], List[List[str]]],
    on_change_search: Any,
    on_toggle_menu: Any,
    on_select: Any,
    is_required: bool = False,
    helper_text: str = "",
    error_text: str = "",
    on_key_down: Any = None,
) -> rx.Component:
    """Componente de selectable con búsqueda accesible.

    Args:
        label: Etiqueta del campo
        placeholder: Texto cuando no hay selección
        value_label: Variable con el texto de la opción seleccionada
        search_value: Variable con el texto de búsqueda actual
        menu_open: Estado de apertura del menú
        filtered_options: Opciones filtradas para mostrar
        on_change_search: Handler al cambiar búsqueda
        on_toggle_menu: Handler al abrir/cerrar menú
        on_select: Handler al seleccionar opción
        is_required: Si el campo es requerido
        helper_text: Texto de ayuda
        error_text: Mensaje de error
        on_key_down: Handler para eventos de teclado

    Returns:
        Componente Reflex
    """
    return rx.vstack(
        rx.hstack(
            rx.text(label, size="2", weight="bold"),
            rx.cond(
                is_required,
                rx.text("*", color="var(--brand-primary)", weight="bold"),
            ),
            spacing="1",
        ),
        rx.popover.root(
            rx.popover.trigger(
                neuro_button(
                    rx.cond(
                        value_label == "",
                        rx.text(
                            placeholder, color="var(--text-tertiary)", weight="regular"
                        ),
                        rx.text(
                            value_label, color="var(--text-primary)", weight="medium"
                        ),
                    ),
                    rx.icon("chevron-down", size=16),
                    variant="surface",
                    width="100%",
                    justify="between",
                    height="44px",
                    padding="0 1rem",
                    border_radius="12px",
                    box_shadow="inset 0px 2px 4px rgba(0,0,0,0.05)",
                    _hover={
                        "box_shadow": "inset 0px 2px 4px rgba(0,0,0,0.05), 0px 0px 0px 1px var(--border-emphasis)",
                    },
                    _focus={
                        "box_shadow": "inset 0px 2px 4px rgba(0,0,0,0.05), 0px 0px 0px 2px var(--brand-primary)",
                        "outline": "none",
                    },
                ),
            ),
            rx.popover.content(
                rx.vstack(
                    neuro_input(
                        placeholder="Buscar...",
                        value=search_value,
                        on_change=on_change_search,
                        on_key_down=on_key_down,
                        width="100%",
                        variant="soft",
                        size="2",
                        padding="0.75rem",
                        border_radius="8px 8px 0 0",
                        border="none",
                        border_bottom="1px solid var(--border-default)",
                        _focus={
                            "outline": "none",
                            "box_shadow": "none",
                        },
                    ),
                    rx.scroll_area(
                        rx.vstack(
                            rx.foreach(
                                filtered_options,
                                lambda opt: rx.cond(
                                    opt[0] != "",
                                    rx.box(
                                        rx.text(
                                            opt[0],
                                            size="2",
                                            weight="medium",
                                            truncate=True,
                                        ),
                                        width="100%",
                                        padding_x="3",
                                        padding_y="2",
                                        _hover={
                                            "background": "var(--bg-hover)",
                                            "cursor": "pointer",
                                        },
                                        on_click=lambda: on_select(opt[1], opt[0]),
                                    ),
                                ),
                            ),
                            width="100%",
                            spacing="0",
                        ),
                        type="auto",
                        scrollbars="vertical",
                        style={"max_height": "200px"},
                        width="100%",
                    ),
                    padding="0",
                    width="100%",
                    min_width="300px",
                    border_radius="12px",
                    box_shadow="0px 4px 24px rgba(0,0,0,0.08)",
                    border="1px solid var(--border-default)",
                    background="var(--bg-panel)",
                ),
                align="start",
                side="bottom",
                side_offset=4,
                avoid_collisions=True,
                style={
                    "pointer_events": "auto",
                    "z_index": styles.Z_POPOVER,
                },
            ),
            open=menu_open,
            on_open_change=on_toggle_menu,
        ),
        rx.cond(
            helper_text != "",
            rx.text(helper_text, size="1", color="var(--text-tertiary)"),
        ),
        rx.cond(
            error_text != "",
            rx.text(error_text, size="1", color="var(--red-9)"),
        ),
        spacing="1",
        width="100%",
        align="start",
    )
