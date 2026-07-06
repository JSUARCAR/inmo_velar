import re
"""Componentes de Floating Label reutilizables.

Proporciona inputs y selects con etiquetas visibles permanentes
que se desplazan al recibir foco o contener datos.
"""

from typing import Callable

import reflex as rx

from src.presentacion_reflex import styles


def floating_input(
    label: str,
    *args,
    value: str | rx.Var,
    on_change: Callable[[str], None] = None,
    error: bool | rx.Var = False,
    placeholder: str = " ",
    disabled: bool = False,
    always_float: bool = False,
    **kwargs,
) -> rx.Component:
    """Input con etiqueta flotante.

    El label se desplaza hacia arriba cuando el campo recibe foco
    o contiene datos, permaneciendo siempre visible.

    Args:
        label: Texto de la etiqueta que se desplaza al recibir foco.
        value: Valor controlado del campo.
        on_change: Callback opcional cuando el valor cambia.
        error: Si True, cambia color de etiqueta a rojo.
        placeholder: Placeholder (usar " " para CSS selector).
        disabled: Si True, campo no interactuable.
        always_float: Si True, el label siempre estará en su estado flotante.
        **kwargs: Props adicionales para rx.input.

    Returns:
        rx.Component: Input con etiqueta flotante.
    """
    input_id = kwargs.pop("id", re.sub(r"[^a-z0-9-]", "", f"fl-{label.lower().replace(' ', '-')}"))

    input_type = kwargs.get("type", "text")
    if input_type in ["date", "datetime-local", "time", "month", "week", "color", "file"]:
        always_float = True

    label_style = {
        "position": "absolute",
        "left": "1rem",
        "top": "50%",
        "transform": "translateY(-50%)",
        "font_size": styles.FL_LABEL_SIZE,
        "color": styles.FL_LABEL_COLOR,
        "transition": styles.FL_TRANSITION,
        "pointer_events": "none",
        "background": "transparent",
        "padding": "0 0.25rem",
        "z_index": "2",
    }

    label_error_style = {
        **label_style,
        "color": styles.FL_LABEL_ERROR_COLOR,
    }

    custom_style = kwargs.pop("style", {})
    input_style = {
        **styles.NEU_INPUT_STYLE,
        "padding_top": "1.25rem",
        "padding_bottom": "0.5rem",
    }
    if isinstance(custom_style, dict):
        input_style.update(custom_style)

    return rx.box(
        rx.input(
            *args,
            id=input_id,
            value=value,
            placeholder=" ",
            disabled=disabled,
            style=input_style,
            class_name="floating-input",
            **(kwargs | {"on_change": on_change} if on_change else kwargs),
        ),
        rx.el.label(
            label,
            html_for=input_id,
            class_name=f"floating-label {'always-float' if always_float else ''}".strip(),
            style=rx.cond(
                error,
                label_error_style,
                label_style,
            ),
        ),
        position="relative",
        width=kwargs.pop("width", "100%"),
    )


def floating_select(
    label: str,
    value: str | rx.Var,
    options: list[dict[str, str]] | rx.Var,
    on_change: Callable[[str], None] = None,
    error: bool | rx.Var = False,
    placeholder: str = "Seleccionar...",
    disabled: bool = False,
    **kwargs,
) -> rx.Component:
    """Select con etiqueta flotante.

    El label se desplaza hacia arriba cuando hay valor seleccionado
    o el campo recibe foco.

    Args:
        label: Texto de la etiqueta flotante.
        value: Valor seleccionado.
        options: Lista de opciones [{"label": "Texto", "value": "valor"}]
                 o Var que evalúe a dicha lista.
        on_change: Callback opcional cuando cambia la selección.
        error: Si True, cambia color de etiqueta a rojo.
        placeholder: Texto cuando no hay selección.
        disabled: Si True, select no interactuable.
        **kwargs: Props adicionales para rx.select.root.

    Returns:
        rx.Component: Select con etiqueta flotante.
    """
    select_id = kwargs.pop("id", re.sub(r"[^a-z0-9-]", "", f"fl-{label.lower().replace(' ', '-')}"))

    label_style = {
        "position": "absolute",
        "left": "1rem",
        "top": "0",
        "transform": "translateY(-50%)",
        "font_size": styles.FL_LABEL_SIZE_TOP,
        "color": styles.FL_LABEL_COLOR,
        "transition": styles.FL_TRANSITION,
        "pointer_events": "none",
        "background": styles.BG_PANEL,
        "padding": "0 0.25rem",
        "z_index": "2",
    }

    label_error_style = {
        **label_style,
        "color": styles.FL_LABEL_ERROR_COLOR,
    }

    trigger_style = {
        **styles.NEU_SELECT_STYLE,
        "padding_top": "1rem",
        "padding_bottom": "0.25rem",
        "height": "48px !important",
    }

    return rx.box(
        rx.select.root(
            rx.select.trigger(
                placeholder=placeholder,
                style=trigger_style,
                id=select_id,
                class_name="floating-input",
            ),
            rx.select.content(
                rx.fragment(*options) if isinstance(options, list) and len(options) > 0 and isinstance(options[0], rx.Component) else options if isinstance(options, rx.Component) else rx.foreach(
                    options,
                    lambda opt: rx.select.item(opt["label"], value=opt["value"]),
                ),
                style={
                    "background": styles.BG_PANEL,
                    "box_shadow": styles.NEU_MODAL_SHADOW,
                    "border_radius": "12px",
                    "pointer_events": "auto",
                    "z_index": styles.Z_POPOVER,
                },
            ),
            value=value,
            disabled=disabled,
            **(kwargs | {"on_change": on_change} if on_change else kwargs),
        ),
        rx.el.label(
            label,
            html_for=select_id,
            class_name="floating-label always-float",
            style=rx.cond(
                error,
                label_error_style,
                label_style,
            ),
        ),
        position="relative",
        width=kwargs.pop("width", "100%"),
    )
