import reflex as rx

from src.presentacion_reflex.state.recibos_state import RecibosState


def modal_form() -> rx.Component:
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title(
                rx.cond(
                    RecibosState.is_editing,
                    "Editar Recibo Público",
                    "Registrar Nuevo Recibo",
                )
            ),
            rx.dialog.description("Ingrese los detalles del recibo de servicio público."),
            rx.flex(
                rx.vstack(
                    rx.text("Propiedad", weight="bold"),
                    rx.select.root(
                        rx.select.trigger(placeholder="Seleccione propiedad...", width="100%"),
                        rx.select.content(
                            rx.select.group(
                                rx.foreach(
                                    RecibosState.propiedades_disponibles,
                                    lambda x: rx.select.item(x["label"], value=x["value"]),
                                )
                            )
                        ),
                        value=RecibosState.form_data["id_propiedad"],
                        on_change=lambda val: RecibosState.set_form_field("id_propiedad", val),
                    ),
                    width="100%",
                ),
                rx.vstack(
                    rx.text("Tipo de Servicio", weight="bold"),
                    rx.select.root(
                        rx.select.trigger(placeholder="Seleccione servicio...", width="100%"),
                        rx.select.content(
                            rx.select.group(
                                rx.select.item("Agua", value="Agua"),
                                rx.select.item("Luz", value="Luz"),
                                rx.select.item("Gas", value="Gas"),
                                rx.select.item("Internet", value="Internet"),
                                rx.select.item("Teléfono", value="Teléfono"),
                                rx.select.item("Aseo", value="Aseo"),
                                rx.select.item("Otros", value="Otros"),
                            )
                        ),
                        value=RecibosState.form_data["tipo_servicio"],
                        on_change=lambda val: RecibosState.set_form_field("tipo_servicio", val),
                    ),
                    width="100%",
                ),
                rx.vstack(
                    rx.text("Período (YYYY-MM)", weight="bold"),
                    rx.input(
                        placeholder="Ej: 2025-01",
                        value=RecibosState.form_data["periodo_recibo"],
                        on_change=lambda val: RecibosState.set_form_field("periodo_recibo", val),
                        width="100%",
                    ),
                    width="100%",
                ),
                rx.hstack(
                    rx.vstack(
                        rx.text("Fecha Desde", weight="bold"),
                        rx.input(
                            type="date",
                            value=RecibosState.form_data["fecha_desde"],
                            on_change=lambda val: RecibosState.set_form_field("fecha_desde", val),
                            width="100%",
                        ),
                        width="100%",
                    ),
                    rx.vstack(
                        rx.text("Fecha Hasta", weight="bold"),
                        rx.input(
                            type="date",
                            value=RecibosState.form_data["fecha_hasta"],
                            on_change=lambda val: RecibosState.set_form_field("fecha_hasta", val),
                            width="100%",
                        ),
                        width="100%",
                    ),
                    rx.vstack(
                        rx.text("Días", weight="bold"),
                        rx.input(
                            value=RecibosState.form_data["dias_facturados"],
                            read_only=True,
                            width="100%",
                        ),
                        width="80px",
                    ),
                    width="100%",
                    spacing="2",
                ),
                rx.vstack(
                    rx.text("Valor ($)", weight="bold"),
                    rx.input(
                        type="number",
                        value=RecibosState.form_data["valor_recibo"],
                        on_change=lambda val: RecibosState.set_form_field("valor_recibo", val),
                        width="100%",
                    ),
                    width="100%",
                ),
                rx.vstack(
                    rx.text("Fecha Vencimiento", weight="bold"),
                    rx.input(
                        type="date",
                        value=RecibosState.form_data["fecha_vencimiento"],
                        on_change=lambda val: RecibosState.set_form_field("fecha_vencimiento", val),
                        width="100%",
                    ),
                    width="100%",
                ),
                rx.cond(
                    RecibosState.error_message != "",
                    rx.callout(
                        RecibosState.error_message,
                        icon="triangle_alert",
                        color_scheme="red",
                        role="alert",
                        width="100%",
                    ),
                ),
                direction="column",
                spacing="4",
            ),
            rx.flex(
                rx.dialog.close(
                    rx.button("Cancelar", variant="soft", color_scheme="gray"),
                ),
                rx.button(
                    "Guardar", on_click=RecibosState.save_recibo, loading=RecibosState.is_loading
                ),
                spacing="3",
                margin_top="16px",
                justify="end",
            ),
        ),
        open=RecibosState.show_form_modal,
        on_open_change=RecibosState.handle_form_open_change,
    )
