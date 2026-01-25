"""Modal form para crear/editar recaudos (pagos de arrendatarios)."""

import reflex as rx

from src.presentacion_reflex.state.recaudos_state import RecaudosState


def modal_recaudo() -> rx.Component:
    """Modal para crear o editar un recaudo."""
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title(
                rx.cond(
                    RecaudosState.form_data.get("id_recaudo"),
                    "Editar Recaudo",
                    "Registrar Nuevo Pago",
                )
            ),
            rx.dialog.description(
                "Complete los datos del pago recibido del arrendatar io.",
                size="2",
                margin_bottom="16px",
            ),
            # Mensaje de Error
            rx.cond(
                RecaudosState.error_message != "",
                rx.callout.root(
                    rx.callout.icon(icon="triangle_alert"),
                    rx.callout.text(RecaudosState.error_message),
                    color="red",
                    size="1",
                    margin_bottom="16px",
                ),
            ),
            # Formulario
            rx.form.root(
                rx.vstack(
                    # Contrato (solo en creación)
                    rx.cond(
                        ~RecaudosState.form_data.get("id_recaudo"),
                        rx.vstack(
                            rx.text("Contrato *", size="2", weight="bold"),
                            rx.select.root(
                                rx.select.trigger(placeholder="Seleccione un contrato..."),
                                rx.select.content(
                                    rx.foreach(
                                        RecaudosState.contratos_select_options,
                                        lambda option: rx.select.item(option, value=option),
                                    )
                                ),
                                name="id_contrato_a",
                                on_change=RecaudosState.on_contract_change,
                                required=True,
                                size="2",
                                width="100%",
                            ),
                            width="100%",
                        ),
                    ),
                    # Fecha de Pago
                    rx.vstack(
                        rx.text("Fecha de Pago *", size="2", weight="bold"),
                        rx.input(
                            placeholder="YYYY-MM-DD",
                            type="date",
                            name="fecha_pago",
                            default_value=RecaudosState.form_data.get("fecha_pago", ""),
                            required=True,
                            size="2",
                            width="100%",
                        ),
                        width="100%",
                    ),
                    # Valor Total
                    rx.vstack(
                        rx.hstack(
                            rx.text("Valor Total (COP) *", size="2", weight="bold"),
                            rx.tooltip(
                                rx.icon("info", size=15),
                                content="Ingrese el valor numérico sin puntos ni comas. Ejemplo: 1500000",
                            ),
                            spacing="2",
                            align="center",
                        ),
                        rx.input(
                            placeholder="Ej: 1500000",
                            type="number",
                            name="valor_total",
                            value=RecaudosState.form_data.get("valor_total", ""),
                            on_change=lambda v: RecaudosState.set_form_field("valor_total", v),
                            required=True,
                            min="1",
                            step="1",
                            size="2",
                            width="100%",
                        ),
                        width="100%",
                    ),
                    # Método de Pago
                    rx.vstack(
                        rx.text("Método de Pago *", size="2", weight="bold"),
                        rx.select.root(
                            rx.select.trigger(),
                            rx.select.content(
                                rx.select.item("Transferencia", value="Transferencia"),
                                rx.select.item("PSE", value="PSE"),
                                rx.select.item("Consignación", value="Consignación"),
                                rx.select.item("Efectivo", value="Efectivo"),
                            ),
                            name="metodo_pago",
                            default_value=RecaudosState.form_data.get(
                                "metodo_pago", "Transferencia"
                            ),
                            size="2",
                            width="100%",
                        ),
                        width="100%",
                    ),
                    # Referencia Bancaria
                    rx.vstack(
                        rx.text("Referencia Bancaria", size="2", weight="bold"),
                        rx.input(
                            placeholder="Número de transacción o comprobante",
                            name="referencia_bancaria",
                            default_value=RecaudosState.form_data.get("referencia_bancaria", ""),
                            size="2",
                            width="100%",
                        ),
                        rx.text(
                            "* Obligatoria para métodos electrónicos",
                            size="1",
                            color="gray",
                        ),
                        width="100%",
                    ),
                    # Tipo de Concepto y Período (simplificado)
                    rx.hstack(
                        rx.vstack(
                            rx.text("Tipo *", size="2", weight="bold"),
                            rx.select.root(
                                rx.select.trigger(),
                                rx.select.content(
                                    rx.select.item("Canon", value="Canon"),
                                    rx.select.item("Administración", value="Administración"),
                                    rx.select.item("Mora", value="Mora"),
                                    rx.select.item("Servicios", value="Servicios"),
                                    rx.select.item("Otro", value="Otro"),
                                ),
                                name="tipo_concepto",
                                default_value=RecaudosState.form_data.get("tipo_concepto", "Canon"),
                                size="2",
                                width="100%",
                            ),
                            flex="1",
                        ),
                        rx.vstack(
                            rx.text("Período *", size="2", weight="bold"),
                            rx.input(
                                placeholder="YYYY-MM",
                                type="month",
                                name="periodo",
                                default_value=RecaudosState.form_data.get("periodo", ""),
                                required=True,
                                size="2",
                                width="100%",
                            ),
                            flex="1",
                        ),
                        width="100%",
                        spacing="3",
                    ),
                    # Observaciones
                    rx.vstack(
                        rx.text("Observaciones", size="2", weight="bold"),
                        rx.text_area(
                            placeholder="Notas adicionales sobre este pago...",
                            name="observaciones",
                            default_value=RecaudosState.form_data.get("observaciones", ""),
                            size="2",
                            width="100%",
                            rows="3",
                        ),
                        width="100%",
                    ),
                    # Botones
                    rx.hstack(
                        rx.dialog.close(
                            rx.button(
                                "Cancelar",
                                variant="soft",
                                color="gray",
                                size="2",
                            ),
                        ),
                        rx.button(
                            rx.cond(RecaudosState.is_loading, rx.spinner(size="1"), "Guardar Pago"),
                            type="submit",
                            size="2",
                            disabled=RecaudosState.is_loading,
                        ),
                        spacing="3",
                        justify="end",
                        width="100%",
                    ),
                    spacing="4",
                    width="100%",
                ),
                on_submit=RecaudosState.save_recaudo,
                reset_on_submit=False,
            ),
            max_width="600px",
            padding="24px",
        ),
        open=RecaudosState.show_form_modal,
        on_open_change=RecaudosState.close_modal,
    )
