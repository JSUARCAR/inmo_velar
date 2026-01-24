"""
Formulario de Registro de Pago
"""

import reflex as rx
from src.presentacion_reflex.state.liquidaciones_state import LiquidacionesState


def form_field(label: str, name: str, value: str = "", type: str = "text", placeholder: str = "", required: bool = False) -> rx.Component:
    """Campo de formulario reutilizable."""
    return rx.vstack(
        rx.text(label, size="2", weight="medium", color="gray.700"),
        rx.input(
            name=name,
            default_value=value,
            placeholder=placeholder,
            type=type,
            required=required,
            width="100%",
        ),
        spacing="1",
        width="100%",
    )


def payment_form() -> rx.Component:
    """Modal con formulario para registrar pago de liquidación."""
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title("Registrar Pago a Propietario"),
            rx.dialog.description(
                "Ingrese los detalles de la transferencia o pago realizado."
            ),
            
            rx.form.root(
                rx.vstack(
                    # Campos Ocultos
                    rx.input(name="id_liquidacion", value=LiquidacionesState.form_data["id_liquidacion"], type="hidden"),
                    
                    # Campos Fecha
                    form_field("Fecha de Pago", "fecha_pago", LiquidacionesState.form_data["fecha_pago"], type="date", required=True),
                    
                    # Método de Pago
                    rx.vstack(
                        rx.text("Método de Pago", size="2", weight="medium", color="gray.700"),
                        rx.select(
                            ["Transferencia Electrónica", "Consignación", "Cheque", "Efectivo", "Otro"],
                            name="metodo_pago",
                            default_value="Transferencia Electrónica",
                            width="100%",
                        ),
                        spacing="1",
                        width="100%",
                    ),
                    
                    # Referencia
                    form_field("Referencia / Comprobante", "referencia_pago", placeholder="Ej: TRX-123456", required=True),
                    
                    rx.callout(
                        "Esta acción cambiará el estado de la liquidación a 'Pagada' y no se podrá revertir fácilmente.",
                        icon="triangle-alert",
                        color_scheme="yellow",
                    ),
                    
                    rx.divider(margin_y="1em"),
                    
                    # Botones
                    rx.hstack(
                        rx.dialog.close(
                            rx.button("Cancelar", variant="soft", color_scheme="gray", type="button"),
                        ),
                        rx.spacer(),
                        rx.button(
                            rx.hstack(rx.icon("dollar-sign"), "Confirmar Pago"),
                            type="submit",
                            color_scheme="green"
                        ),
                        width="100%",
                    ),
                    spacing="4",
                    width="100%",
                ),
                on_submit=LiquidacionesState.marcar_como_pagada,
            ),
            
            max_width="500px",
        ),
        open=LiquidacionesState.show_payment_modal,
        on_open_change=LiquidacionesState.close_modal,
    )
