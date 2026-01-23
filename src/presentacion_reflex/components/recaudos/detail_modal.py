"""Modal de detalle para recaudos (pagos de arrendatarios)."""

import reflex as rx
from src.presentacion_reflex.state.recaudos_state import RecaudosState


def modal_detalle_recaudo() -> rx.Component:
    """Modal para ver detalle de un recaudo."""
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title("Detalle del Recaudo"),
            
            rx.dialog.description(
                "Información completa del pago registrado.",
                size="2",
                margin_bottom="16px",
            ),
            
            # Contenido del detalle
            rx.cond(
                RecaudosState.recaudo_actual,
                rx.vstack(
                    # Información del contrato
                    rx.card(
                        rx.vstack(
                            rx.text("Información del Contrato", size="3", weight="bold", color="blue"),
                            rx.separator(),
                            rx.hstack(
                                rx.vstack(
                                    rx.text("Propiedad", size="1", color="gray"),
                                    rx.text(RecaudosState.recaudo_actual["direccion"], weight="medium"),
                                    align="start",
                                    flex="1",
                                ),
                                rx.vstack(
                                    rx.text("Matrícula", size="1", color="gray"),
                                    rx.text(RecaudosState.recaudo_actual["matricula"], weight="medium"),
                                    align="start",
                                    flex="1",
                                ),
                                width="100%",
                            ),
                            rx.hstack(
                                rx.vstack(
                                    rx.text("Arrendatario", size="1", color="gray"),
                                    rx.text(RecaudosState.recaudo_actual["arrendatario"], weight="medium"),
                                    align="start",
                                    flex="1",
                                ),
                                rx.vstack(
                                    rx.text("ID Contrato", size="1", color="gray"),
                                    rx.text(RecaudosState.recaudo_actual["id_contrato"], weight="medium"),
                                    align="start",
                                    flex="1",
                                ),
                                width="100%",
                            ),
                            spacing="3",
                            width="100%",
                        ),
                        width="100%",
                    ),
                    
                    # Información del pago
                    rx.card(
                        rx.vstack(
                            rx.text("Información del Pago", size="3", weight="bold", color="green"),
                            rx.separator(),
                            rx.hstack(
                                rx.vstack(
                                    rx.text("Fecha de Pago", size="1", color="gray"),
                                    rx.text(RecaudosState.recaudo_actual["fecha_pago"], weight="medium"),
                                    align="start",
                                    flex="1",
                                ),
                                rx.vstack(
                                    rx.text("Valor Total", size="1", color="gray"),
                                    rx.text(
                                        f"${RecaudosState.recaudo_actual['valor_total']:,}",
                                        weight="bold",
                                        color="green",
                                        size="4",
                                    ),
                                    align="start",
                                    flex="1",
                                ),
                                width="100%",
                            ),
                            rx.hstack(
                                rx.vstack(
                                    rx.text("Método de Pago", size="1", color="gray"),
                                    rx.badge(RecaudosState.recaudo_actual["metodo_pago"], variant="soft"),
                                    align="start",
                                    flex="1",
                                ),
                                rx.vstack(
                                    rx.text("Estado", size="1", color="gray"),
                                    rx.match(
                                        RecaudosState.recaudo_actual["estado"],
                                        ("Pendiente", rx.badge("Pendiente", color_scheme="yellow", variant="solid")),
                                        ("Aplicado", rx.badge("Aplicado", color_scheme="green", variant="solid")),
                                        ("Reversado", rx.badge("Reversado", color_scheme="red", variant="solid")),
                                        rx.badge(RecaudosState.recaudo_actual["estado"], color_scheme="gray"),
                                    ),
                                    align="start",
                                    flex="1",
                                ),
                                width="100%",
                            ),
                            rx.cond(
                                RecaudosState.recaudo_actual["referencia"] != "",
                                rx.vstack(
                                    rx.text("Referencia Bancaria", size="1", color="gray"),
                                    rx.text(RecaudosState.recaudo_actual["referencia"], weight="medium"),
                                    align="start",
                                    width="100%",
                                ),
                            ),
                            rx.cond(
                                RecaudosState.recaudo_actual["observaciones"] != "",
                                rx.vstack(
                                    rx.text("Observaciones", size="1", color="gray"),
                                    rx.text(RecaudosState.recaudo_actual["observaciones"]),
                                    align="start",
                                    width="100%",
                                ),
                            ),
                            spacing="3",
                            width="100%",
                        ),
                        width="100%",
                    ),
                    
                    # Auditoría
                    rx.card(
                        rx.vstack(
                            rx.text("Auditoría", size="2", weight="bold", color="gray"),
                            rx.separator(),
                            rx.hstack(
                                rx.text("Creado por:", size="1", color="gray"),
                                rx.text(RecaudosState.recaudo_actual["created_by"], size="1"),
                                rx.text("el", size="1", color="gray"),
                                rx.text(RecaudosState.recaudo_actual["created_at"], size="1"),
                                spacing="2",
                            ),
                            spacing="2",
                            width="100%",
                        ),
                        width="100%",
                    ),
                    
                    # Botón Cerrar
                    rx.hstack(
                        rx.dialog.close(
                            rx.button(
                                "Cerrar",
                                variant="soft",
                                size="2",
                            ),
                        ),
                        justify="end",
                        width="100%",
                    ),
                    
                    spacing="4",
                    width="100%",
                ),
                rx.center(
                    rx.spinner(size="3"),
                    min_height="200px",
                ),
            ),
            
            max_width="650px",
            padding="24px",
        ),
        open=RecaudosState.show_detail_modal,
        on_open_change=RecaudosState.close_modal,
    )
