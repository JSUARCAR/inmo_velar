import reflex as rx
from src.presentacion_reflex.state.recibos_state import RecibosState

def detail_modal() -> rx.Component:
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title("Detalles del Recibo"),
            rx.dialog.description("Información completa del registro."),
            
            rx.vstack(
                rx.grid(
                    rx.vstack(
                        rx.text("Propiedad", weight="bold", size="2"),
                        rx.text(RecibosState.detail_data["propiedad_nombre"], size="3"),
                    ),
                    rx.vstack(
                        rx.text("Servicio", weight="bold", size="2"),
                        rx.text(RecibosState.detail_data["tipo_servicio"], size="3"),
                    ),
                    rx.vstack(
                        rx.text("Período", weight="bold", size="2"),
                        rx.text(RecibosState.detail_data["periodo_recibo"], size="3"),
                    ),
                    rx.vstack(
                        rx.text("Valor", weight="bold", size="2"),
                        rx.text(RecibosState.detail_data["valor_formato"], size="3"),
                    ),
                    rx.vstack(
                        rx.text("Estado", weight="bold", size="2"),
                        rx.badge(
                            RecibosState.detail_data["estado"], 
                            color_scheme=RecibosState.detail_data["clase_estado"]
                        ),
                    ),
                    rx.vstack(
                        rx.text("Fecha Vencimiento", weight="bold", size="2"),
                        rx.text(RecibosState.detail_data["fecha_vencimiento"], size="3"),
                    ),
                    columns="2",
                    spacing="4",
                    width="100%"
                ),
                
                rx.divider(margin_y="2"),
                
                rx.heading("Detalles de Facturación", size="3"),
                rx.grid(
                    rx.vstack(
                        rx.text("Fecha Desde", weight="bold", size="2"),
                        rx.text(RecibosState.detail_data["fecha_desde"], size="3"),
                    ),
                    rx.vstack(
                        rx.text("Fecha Hasta", weight="bold", size="2"),
                        rx.text(RecibosState.detail_data["fecha_hasta"], size="3"),
                    ),
                    rx.vstack(
                        rx.text("Días Facturados", weight="bold", size="2"),
                        rx.text(RecibosState.detail_data["dias_facturados"], size="3"),
                    ),
                    columns="3",
                    spacing="4",
                    width="100%"
                ),
                
                rx.cond(
                    RecibosState.detail_data["estado"] == "Pagado",
                    rx.vstack(
                        rx.divider(margin_y="2"),
                        rx.heading("Información de Pago", size="3"),
                        rx.grid(
                            rx.vstack(
                                rx.text("Fecha Pago", weight="bold", size="2"),
                                rx.text(RecibosState.detail_data["fecha_pago"], size="3"),
                            ),
                            rx.vstack(
                                rx.text("Comprobante", weight="bold", size="2"),
                                rx.text(RecibosState.detail_data["comprobante"], size="3"),
                            ),
                            columns="2",
                            spacing="4",
                            width="100%"
                        )
                    )
                ),

                spacing="4",
                margin_top="4"
            ),

            rx.flex(
                rx.dialog.close(
                    rx.button("Cerrar", variant="soft", color_scheme="gray"),
                ),
                justify="end",
                margin_top="6",
            ),
        ),
        open=RecibosState.show_detail_modal,
        on_open_change=RecibosState.handle_detail_open_change,
    )
