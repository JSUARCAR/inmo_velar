
import reflex as rx
from typing import Callable

def bulk_modal_form(
    is_open: rx.Var,
    on_open_change: Callable,
    form_data: rx.Var,
    on_submit: Callable,
    is_loading: rx.Var,
) -> rx.Component:
    """
    Formulario para generar liquidaciones masivas de asesores.
    
    Args:
        is_open: Estado de apertura del modal
        on_open_change: Event handler para cambiar el estado de apertura
        form_data: Diccionario con datos del formulario (periodo)
        on_submit: Event handler para el envío del formulario
        is_loading: Estado de carga
    """
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title(
                "Generación Masiva de Liquidaciones",
                font_size="20px",
                font_weight="700",
                margin_bottom="1rem"
            ),
            rx.dialog.description(
                "Esta acción generará liquidaciones para TODOS los asesores activos que tengan contratos de arrendamiento vigentes en el período seleccionado.",
                margin_bottom="1.5rem",
                color="gray"
            ),
            
            rx.form.root(
                rx.flex(
                    # Período
                    rx.box(
                        rx.text(
                            "Período a Liquidar (YYYY-MM)", 
                            font_weight="bold", 
                            margin_bottom="0.5rem"
                        ),
                        rx.input(
                            name="periodo",
                            type="month",
                            placeholder="YYYY-MM",
                            required=True,
                            width="100%",
                            default_value=form_data["periodo"],
                            # Nota: En Reflex forms, el value controlado a veces conflictea con input type='month' 
                            # si no se maneja con cuidado, pero usaremos default_value o value según el state.
                        ),
                        width="100%"
                    ),
                    
                    rx.callout(
                        "Nota: Se omitirán los asesores que ya tengan una liquidación generada para este período.",
                        icon="info",
                        color_scheme="blue",
                        size="1",
                        margin_top="1rem"
                    ),

                    # Botones
                    rx.flex(
                        rx.dialog.close(
                            rx.button(
                                "Cancelar", 
                                variant="soft", 
                                color_scheme="gray", 
                                type="button",
                                # No necesitamos on_click explicito para cerrar si usamos rx.dialog.close,
                                # pero si queremos limpiar estado, el on_open_change handlea el cierre.
                                # Dejamos el on_click por si hay logica extra.
                                # En este caso el dialog.close llamara al on_open_change(False) automaticamente.
                            )
                        ),
                        rx.button(
                            rx.cond(
                                is_loading,
                                rx.flex(rx.spinner(size="1"), rx.text("Procesando..."), spacing="2"),
                                "Generar Liquidaciones"
                            ),
                            type="submit",
                            disabled=is_loading,
                        ),
                        spacing="3",
                        justify="end",
                        margin_top="1.5rem",
                        width="100%"
                    ),
                    direction="column",
                    width="100%"
                ),
                on_submit=on_submit,
            ),
            max_width="450px",
        ),
        open=is_open,
        on_open_change=on_open_change,
    )
