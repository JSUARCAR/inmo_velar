"""Modal form para crear/editar recaudos (pagos de arrendatarios)."""

import reflex as rx

from src.presentacion_reflex.state.recaudos_state import RecaudosState
from src.presentacion_reflex.components.neuro_elements import (
    neuro_input,
    neuro_button,
    neuro_select_root,
    neuro_text_area,
)
from src.presentacion_reflex import styles


def searchable_select(
    label: str,
    placeholder: str,
    value_label: rx.Var[str],
    search_value: rx.Var[str],
    menu_open: rx.Var[bool],
    filtered_options: rx.Var[list],
    on_change_search: callable,
    on_toggle_menu: callable,
    on_select: callable,
) -> rx.Component:
    return rx.vstack(
        rx.text(label, size="2", weight="bold", color=styles.TEXT_PRIMARY),
        rx.popover.root(
            rx.popover.trigger(
                neuro_button(
                    rx.hstack(
                        rx.cond(
                            value_label == "",
                            rx.text(placeholder, color=styles.TEXT_TERTIARY),
                            rx.text(value_label, color=styles.TEXT_PRIMARY),
                        ),
                        rx.icon("chevron-down", size=16),
                        width="100%",
                        justify="between",
                    ),
                    width="100%",
                ),
            ),
            rx.popover.content(
                rx.vstack(
                    neuro_input(
                        placeholder="Buscar...",
                        value=search_value,
                        on_change=on_change_search,
                        autofocus=True,
                        width="100%",
                        size="1",
                    ),
                    rx.scroll_area(
                        rx.vstack(
                            rx.foreach(
                                filtered_options,
                                lambda opt: rx.cond(
                                    opt[0] != "",
                                    rx.box(
                                        rx.text(opt[0], size="2"),
                                        width="100%",
                                        padding_x="3",
                                        padding_y="2",
                                        _hover={
                                            "bg": "var(--gray-4)",
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
                    padding="2",
                    width="320px",
                    spacing="2",
                    background=styles.BG_PANEL,
                    style={"box_shadow": styles.NEU_SHADOW, "border": "none"},
                ),
            ),
            open=menu_open,
            on_open_change=on_toggle_menu,
        ),
        spacing="1",
        width="100%",
    )


def modal_recaudo() -> rx.Component:
    """Modal para crear o editar un recaudo."""
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title(
                rx.cond(
                    RecaudosState.is_editing,
                    "Editar Recaudo",
                    "Registrar Nuevo Pago",
                ),
                color=styles.TEXT_PRIMARY,
            ),
            rx.dialog.description(
                "Complete los datos del pago recibido del arrendatar io.",
                size="2",
                margin_bottom="16px",
                color=styles.TEXT_SECONDARY,
            ),
            # Mensaje de Error
            rx.cond(
                RecaudosState.error_message != "",
                rx.callout.root(
                    rx.callout.icon(icon="alert-triangle"),
                    rx.callout.text(RecaudosState.error_message),
                    color="red",
                    size="1",
                    margin_bottom="16px",
                ),
            ),
            # Formulario
            rx.form.root(
                # Campos ocultos reales vía HTML para evitar renderizado de wrappers de Reflex
                rx.html(
                    f'<input type="hidden" name="id_recaudo" value="{RecaudosState.form_data["id_recaudo"]}">'
                ),
                rx.html(
                    f'<input type="hidden" name="id_contrato_a" value="{RecaudosState.form_data["id_contrato_a"]}">'
                ),
                rx.vstack(
                    # Contrato (solo en creación, visualmente)
                    rx.cond(
                        ~RecaudosState.is_editing,
                        searchable_select(
                            "Contrato *",
                            "Seleccione un contrato...",
                            RecaudosState.contrato_selected_label,
                            RecaudosState.contrato_search,
                            RecaudosState.contrato_menu_open,
                            RecaudosState.filtered_contratos_options,
                            RecaudosState.set_contrato_search,
                            RecaudosState.toggle_contrato_menu,
                            RecaudosState.select_contrato,
                        ),
                        # En edición, mostrar como texto informativo
                        rx.vstack(
                            rx.text(
                                "Contrato",
                                size="2",
                                weight="bold",
                                color=styles.TEXT_PRIMARY,
                            ),
                            rx.box(
                                rx.text(
                                    RecaudosState.contrato_selected_label,
                                    size="2",
                                    color=styles.TEXT_SECONDARY,
                                ),
                                padding="3",
                                width="100%",
                                border_radius="12px",
                                background=styles.BG_HOVER,
                                border=f"1px solid {styles.BORDER_DEFAULT}",
                                style={"box_shadow": styles.NEU_INSET},
                            ),
                            width="100%",
                            spacing="1",
                        ),
                    ),
                    # Fecha de Pago
                    rx.vstack(
                        rx.text(
                            "Fecha de Pago *",
                            size="2",
                            weight="bold",
                            color=styles.TEXT_PRIMARY,
                        ),
                        neuro_input(
                            placeholder="YYYY-MM-DD",
                            type="date",
                            name="fecha_pago",
                            default_value=RecaudosState.form_data["fecha_pago"],
                            required=True,
                            size="2",
                            width="100%",
                        ),
                        width="100%",
                        spacing="1",
                    ),
                    # Valor Total
                    rx.vstack(
                        rx.hstack(
                            rx.text(
                                "Valor Total (COP) *",
                                size="2",
                                weight="bold",
                                color=styles.TEXT_PRIMARY,
                            ),
                            rx.tooltip(
                                rx.icon("info", size=15),
                                content="Ingrese el valor numérico sin puntos ni comas. Ejemplo: 1500000",
                            ),
                            spacing="2",
                            align="center",
                        ),
                        neuro_input(
                            placeholder="Ej: 1500000",
                            type="number",
                            name="valor_total",
                            value=RecaudosState.form_data["valor_total"],
                            on_change=lambda v: RecaudosState.set_form_field(
                                "valor_total", v
                            ),
                            required=True,
                            min="1",
                            step="1",
                            size="2",
                            width="100%",
                        ),
                        width="100%",
                        spacing="1",
                    ),
                    # Método de Pago
                    rx.vstack(
                        rx.text(
                            "Método de Pago *",
                            size="2",
                            weight="bold",
                            color=styles.TEXT_PRIMARY,
                        ),
                        neuro_select_root(
                            [
                                rx.select.item("Transferencia", value="Transferencia"),
                                rx.select.item("PSE", value="PSE"),
                                rx.select.item("Consignación", value="Consignación"),
                                rx.select.item("Efectivo", value="Efectivo"),
                            ],
                            name="metodo_pago",
                            value=RecaudosState.form_data["metodo_pago"],
                            on_change=lambda v: RecaudosState.set_form_field(
                                "metodo_pago", v
                            ),
                            width="100%",
                        ),
                        width="100%",
                        spacing="1",
                    ),
                    # Referencia Bancaria
                    rx.vstack(
                        rx.text(
                            "Referencia Bancaria",
                            size="2",
                            weight="bold",
                            color=styles.TEXT_PRIMARY,
                        ),
                        neuro_input(
                            placeholder="Número de transacción o comprobante",
                            name="referencia_bancaria",
                            default_value=RecaudosState.form_data[
                                "referencia_bancaria"
                            ],
                            size="2",
                            width="100%",
                        ),
                        rx.text(
                            "* Obligatoria para métodos electrónicos",
                            size="1",
                            color=styles.TEXT_TERTIARY,
                        ),
                        width="100%",
                        spacing="1",
                    ),
                    # Tipo de Concepto y Período (simplificado)
                    rx.hstack(
                        rx.vstack(
                            rx.text(
                                "Tipo *",
                                size="2",
                                weight="bold",
                                color=styles.TEXT_PRIMARY,
                            ),
                            neuro_select_root(
                                [
                                    rx.select.item("Canon", value="Canon"),
                                    rx.select.item(
                                        "Administración", value="Administración"
                                    ),
                                    rx.select.item("Mora", value="Mora"),
                                    rx.select.item("Servicios", value="Servicios"),
                                    rx.select.item("Otro", value="Otro"),
                                ],
                                name="tipo_concepto",
                                value=RecaudosState.form_data["tipo_concepto"],
                                on_change=lambda v: RecaudosState.set_form_field(
                                    "tipo_concepto", v
                                ),
                                width="100%",
                            ),
                            flex="1",
                            spacing="1",
                        ),
                        rx.vstack(
                            rx.text(
                                "Período *",
                                size="2",
                                weight="bold",
                                color=styles.TEXT_PRIMARY,
                            ),
                            neuro_input(
                                placeholder="YYYY-MM",
                                type="month",
                                name="periodo",
                                default_value=RecaudosState.form_data["periodo"],
                                required=True,
                                size="2",
                                width="100%",
                            ),
                            flex="1",
                            spacing="1",
                        ),
                        width="100%",
                        spacing="3",
                    ),
                    # Observaciones
                    rx.vstack(
                        rx.text(
                            "Observaciones",
                            size="2",
                            weight="bold",
                            color=styles.TEXT_PRIMARY,
                        ),
                        neuro_text_area(
                            placeholder="Notas adicionales sobre este pago...",
                            name="observaciones",
                            default_value=RecaudosState.form_data["observaciones"],
                            size="2",
                            width="100%",
                            min_height="80px",
                        ),
                        width="100%",
                        spacing="1",
                    ),
                    # Botones
                    rx.hstack(
                        rx.dialog.close(
                            neuro_button(
                                "Cancelar",
                                size="2",
                            ),
                        ),
                        neuro_button(
                            rx.cond(
                                RecaudosState.is_loading,
                                rx.spinner(size="1"),
                                rx.cond(
                                    RecaudosState.is_processing_idempotent,
                                    "Procesando...",
                                    "Guardar Pago",
                                ),
                            ),
                            type="submit",
                            size="2",
                            disabled=RecaudosState.is_loading
                            | RecaudosState.is_processing_idempotent,
                        ),
                        spacing="3",
                        justify="end",
                        width="100%",
                        padding_top="2",
                    ),
                    spacing="4",
                    width="100%",
                ),
                on_submit=RecaudosState.save_recaudo,
                reset_on_submit=False,
            ),
            max_width="600px",
            padding="24px",
            background=styles.BG_PANEL,
            style={"border_radius": "16px", "box_shadow": styles.NEU_SHADOW},
        ),
        open=RecaudosState.show_form_modal,
        on_open_change=RecaudosState.close_modal,
    )
