"""
Componente SearchableSelect - Reflex
Selectores con búsqueda accesibles y alineados con Claude Design System.
Usa floating labels para consistencia con el resto del sistema.
"""

import reflex as rx
from typing import Any, List, Union

from src.presentacion_reflex.components.neuro_elements import neuro_input
from src.presentacion_reflex.components.shared.floating_label import floating_input
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
    """Componente de selectable con búsqueda accesible tipo Combobox.

    Usa floating label para el label del campo, consistente con form_field.

    Args:
        label: Etiqueta del campo (se muestra como floating label)
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

    # Input principal con floating label que actúa como Combobox
    combobox_input = floating_input(
        label=label,
        placeholder=placeholder,
        value=rx.cond(
            menu_open,
            search_value,
            rx.cond(value_label != "", value_label, search_value),
        ),
        on_change=lambda val: [on_change_search(val), on_toggle_menu(True)],
        on_focus=lambda: [on_change_search(""), on_toggle_menu(True)],
        on_blur=lambda: on_toggle_menu(False),
        on_key_down=on_key_down,
        width="100%",
        custom_attrs={
            "role": "combobox",
            "aria-expanded": menu_open.to_string(),
            "aria-controls": "opciones-lista",
        },
    )

    # Panel flotante de opciones (Absolute Dropdown)
    dropdown_menu = rx.cond(
        menu_open,
        rx.box(
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
                                # Usamos on_mouse_down en lugar de on_click para evitar el on_blur prematuro del input
                                on_mouse_down=lambda: on_select(opt[1], opt[0]),
                                custom_attrs={"role": "option"},
                            ),
                        ),
                    ),
                    width="100%",
                    spacing="0",
                    id="opciones-lista",
                    custom_attrs={"role": "listbox"},
                ),
                type="auto",
                scrollbars="vertical",
                style={"max_height": "200px"},
                width="100%",
            ),
            position="absolute",
            top="100%",
            left="0",
            width="100%",
            margin_top="4px",
            background="var(--bg-panel)",
            border="1px solid var(--border-default)",
            border_radius="12px",
            box_shadow="0px 4px 24px rgba(0,0,0,0.08)",
            z_index=styles.Z_POPOVER,
            on_mouse_down=rx.prevent_default,
        ),
    )

    return rx.vstack(
        rx.box(
            combobox_input,
            dropdown_menu,
            position="relative",
            width="100%",
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
