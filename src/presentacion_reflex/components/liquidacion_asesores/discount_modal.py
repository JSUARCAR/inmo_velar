import reflex as rx

from src.presentacion_reflex.state.liquidacion_asesores.form_state import (
    LiquidacionFormState,
)
from src.presentacion_reflex.state.liquidacion_asesores.grid_state import (
    LiquidacionGridState,
)
from src.presentacion_reflex.components.neuro_elements import (
    neuro_floating_input,
    neuro_floating_select,
    neuro_button,
)


def discount_modal() -> rx.Component:
    """Modal para agregar un nuevo descuento."""
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title("Agregar Descuento"),
            rx.dialog.description("Ingrese los detalles del descuento a aplicar."),
            rx.form.root(
                rx.flex(
                    # Tipo
                    neuro_floating_select(
                        label="Tipo de Descuento",
                        value=LiquidacionFormState.discount_form["tipo"],
                        options=[
                            {"label": "Descuento Manual", "value": "Descuento Manual"},
                            {"label": "Anticipo", "value": "Anticipo"},
                            {"label": "Otro", "value": "Otro"},
                        ],
                        on_change=lambda val: LiquidacionFormState.set_discount_field(
                            "tipo", val
                        ),
                        placeholder="Seleccione tipo",
                        disabled=True,
                        width="100%",
                    ),
                    # Descripción
                    neuro_floating_input(
                        label="Descripción",
                        name="descripcion",
                        value=LiquidacionFormState.discount_form["descripcion"],
                        on_change=lambda val: LiquidacionFormState.set_discount_field(
                            "descripcion", val
                        ),
                        width="100%",
                    ),
                    # Valor
                    neuro_floating_input(
                        label="Valor",
                        name="valor",
                        type="number",
                        value=LiquidacionFormState.discount_form["valor"],
                        on_change=lambda val: LiquidacionFormState.set_discount_field(
                            "valor", val
                        ),
                        width="100%",
                    ),
                    direction="column",
                    spacing="4",
                ),
                # Campo oculto eliminado - ID se maneja por estado
                rx.flex(
                    rx.dialog.close(
                        neuro_button(
                            "Cancelar",
                            color_scheme="gray",
                            type="button",
                            on_click=LiquidacionFormState.close_modal,
                            tooltip_content="Cerrar sin guardar",
                        )
                    ),
                    neuro_button(
                        "Guardar Descuento",
                        type="submit",
                        loading=LiquidacionGridState.is_loading,
                        tooltip_content="Guardar el descuento registrado",
                    ),
                    spacing="3",
                    justify="end",
                    margin_top="4",
                ),
                on_submit=LiquidacionFormState.save_descuento,
            ),
            # Error Message
            rx.cond(
                LiquidacionFormState.error_message != "",
                rx.callout(
                    LiquidacionFormState.error_message,
                    icon="triangle-alert",
                    color_scheme="red",
                    role="alert",
                    margin_top="2",
                ),
            ),
        ),
        open=LiquidacionFormState.show_discount_modal,
        on_open_change=LiquidacionFormState.set_show_discount_modal,
    )
