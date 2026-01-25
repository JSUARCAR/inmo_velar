import reflex as rx

from src.presentacion_reflex.state.liquidacion_asesores_state import LiquidacionAsesoresState


def discount_modal() -> rx.Component:
    """Modal para agregar un nuevo descuento."""
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title("Agregar Descuento"),
            rx.dialog.description("Ingrese los detalles del descuento a aplicar."),
            rx.form.root(
                rx.flex(
                    # Tipo
                    rx.box(
                        rx.text("Tipo de Descuento", size="2", weight="bold", margin_bottom="1"),
                        rx.select(
                            ["Descuento Manual", "Anticipo", "Otro"],
                            name="tipo",
                            placeholder="Seleccione tipo",
                            required=True,
                            width="100%",
                            value=LiquidacionAsesoresState.discount_form["tipo"],
                            on_change=lambda val: LiquidacionAsesoresState.set_discount_field(
                                "tipo", val
                            ),
                        ),
                        width="100%",
                    ),
                    # Descripción
                    rx.box(
                        rx.text("Descripción", size="2", weight="bold", margin_bottom="1"),
                        rx.input(
                            name="descripcion",
                            placeholder="Ej: Anticipo de comisión",
                            required=True,
                            width="100%",
                            value=LiquidacionAsesoresState.discount_form["descripcion"],
                            on_change=lambda val: LiquidacionAsesoresState.set_discount_field(
                                "descripcion", val
                            ),
                        ),
                        width="100%",
                    ),
                    # Valor
                    rx.box(
                        rx.text("Valor", size="2", weight="bold", margin_bottom="1"),
                        rx.input(
                            name="valor",
                            placeholder="0",
                            required=True,
                            type="number",
                            min="0",
                            width="100%",
                            value=LiquidacionAsesoresState.discount_form["valor"],
                            on_change=lambda val: LiquidacionAsesoresState.set_discount_field(
                                "valor", val
                            ),
                        ),
                        width="100%",
                    ),
                    direction="column",
                    spacing="4",
                ),
                # Campo oculto eliminado - ID se maneja por estado
                rx.flex(
                    rx.dialog.close(
                        rx.button(
                            "Cancelar",
                            variant="soft",
                            color_scheme="gray",
                            type="button",
                            on_click=LiquidacionAsesoresState.close_discount_modal,
                        )
                    ),
                    rx.button(
                        "Guardar Descuento",
                        type="submit",
                        loading=LiquidacionAsesoresState.is_loading,
                    ),
                    spacing="3",
                    justify="end",
                    margin_top="4",
                ),
                on_submit=LiquidacionAsesoresState.save_descuento,
            ),
            # Error Message
            rx.cond(
                LiquidacionAsesoresState.error_message != "",
                rx.callout(
                    LiquidacionAsesoresState.error_message,
                    icon="triangle_alert",
                    color_scheme="red",
                    role="alert",
                    margin_top="2",
                ),
            ),
        ),
        open=LiquidacionAsesoresState.show_discount_modal,
        on_open_change=LiquidacionAsesoresState.set_show_discount_modal,
    )
