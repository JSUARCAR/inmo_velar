"""
Formulario de Registro de Pago
"""

import reflex as rx

from src.presentacion_reflex.state.liquidaciones_state import LiquidacionesState


from src.presentacion_reflex.components.neuro_elements import (
    neuro_floating_input,
    neuro_floating_select,
)

def form_field(
    label: str,
    name: str,
    value: str = "",
    type: str = "text",
    placeholder: str = "",
    required: bool = False,
    on_change=None,
) -> rx.Component:
    """Campo de formulario reutilizable."""
    return rx.box(
        neuro_floating_input(
            label=label,
            value=value,
            name=name,
            placeholder=placeholder,
            type=type,
            required=required,
            on_change=on_change,
            width="100%",
        ),
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
                    rx.input(
                        name="id_liquidacion",
                        value=LiquidacionesState.form_data["id_liquidacion"],
                        type="hidden",
                    ),
                    # Campos Fecha
                    form_field(
                        "Fecha de Pago",
                        "fecha_pago",
                        LiquidacionesState.form_data["fecha_pago"],
                        type="date",
                        required=True,
                        on_change=lambda val: LiquidacionesState.set_form_field("fecha_pago", val),
                    ),
                    # Método de Pago
                    rx.box(
                        neuro_floating_select(
                            label="Método de Pago",
                            value=LiquidacionesState.form_data["metodo_pago"],
                            name="metodo_pago",
                            options=[
                                {"label": "Transferencia Electrónica", "value": "Transferencia Electrónica"},
                                {"label": "Consignación", "value": "Consignación"},
                                {"label": "Cheque", "value": "Cheque"},
                                {"label": "Efectivo", "value": "Efectivo"},
                                {"label": "Otro", "value": "Otro"},
                            ],
                            on_change=lambda val: LiquidacionesState.set_form_field("metodo_pago", val),
                            width="100%",
                        ),
                        width="100%",
                    ),
                    # Referencia
                    form_field(
                        "Referencia / Comprobante",
                        "referencia_pago",
                        LiquidacionesState.form_data["referencia_pago"],
                        placeholder="Ej: TRX-123456",
                        required=True,
                        on_change=lambda val: LiquidacionesState.set_form_field("referencia_pago", val),
                    ),
                    rx.callout(
                        "Esta acción cambiará el estado de la liquidación a 'Pagada' y no se podrá revertir fácilmente.",
                        icon="triangle-alert",
                        color_scheme="yellow",
                    ),
                    rx.divider(margin_y="1em"),
                    # Botones
                    rx.hstack(
                        rx.dialog.close(
                            rx.tooltip(
                                rx.button(
                                    "Cancelar",
                                    variant="soft",
                                    color_scheme="gray",
                                    type="button",
                                ),
                                content="Cerrar sin registrar pago",
                            ),
                        ),
                        rx.spacer(),
                        rx.tooltip(
                            rx.button(
                                rx.hstack(rx.icon("dollar-sign"), "Confirmar Pago"),
                                type="submit",
                                color_scheme="green",
                            ),
                            content="Registrar el pago y cambiar estado a Pagada",
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
