import reflex as rx

from src.presentacion_reflex.state.desocupaciones_state import DesocupacionesState
from src.presentacion_reflex.components.neuro_elements import (
    neuro_floating_input,
    neuro_floating_select,
    neuro_button,
    neuro_text_area,
)
from src.presentacion_reflex import styles


def modal_form() -> rx.Component:
    """Formulario modal para crear desocupación."""
    return rx.dialog.root(
        rx.dialog.content(
            rx.vstack(
                rx.dialog.title("Iniciar Proceso de Desocupación"),
                rx.dialog.description(
                    "Seleccione un contrato activo y una fecha programada para la entrega."
                ),
                rx.cond(
                    DesocupacionesState.error_message != "",
                    rx.callout(
                        DesocupacionesState.error_message,
                        icon="triangle-alert",
                        color_scheme="red",
                        role="alert",
                        width="100%",
                    ),
                ),
                rx.vstack(
                    neuro_floating_select(
                        label="Contrato *",
                        value=DesocupacionesState.form_create_data["id_contrato"],
                        options=rx.foreach(
                            DesocupacionesState.contratos_candidatos,
                            lambda x: rx.select.item(x["texto"], value=x["id"]),
                        ),
                        on_change=DesocupacionesState.set_id_contrato,
                        placeholder="Seleccione el contrato...",
                        width="100%",
                    ),
                    neuro_floating_input(
                        label="Fecha Programada *",
                        type="date",
                        value=DesocupacionesState.form_create_data["fecha_programada"],
                        on_change=DesocupacionesState.set_fecha_programada,
                        width="100%",
                    ),
                    neuro_text_area(
                        label="Observaciones Iniciales",
                        value=DesocupacionesState.form_create_data["observaciones"],
                        on_change=DesocupacionesState.set_observaciones,
                        placeholder="Notas adicionales sobre la entrega...",
                        width="100%",
                    ),
                    spacing="4",
                    width="100%",
                ),
                rx.flex(
                    rx.dialog.close(
                        neuro_button(
                            "Cancelar",
                            variant="soft",
                            color_scheme="gray",
                            on_click=DesocupacionesState.close_create_modal,
                            tooltip_content="Cerrar sin guardar",
                        )
                    ),
                    neuro_button(
                        "Iniciar Desocupación",
                        on_click=DesocupacionesState.create_desocupacion(
                            DesocupacionesState.form_create_data
                        ),
                        loading=DesocupacionesState.is_loading,
                        color_scheme="blue",
                        tooltip_content="Crear nueva desocupación",
                    ),
                    spacing="3",
                    margin_top="1.5em",
                    justify="end",
                    width="100%",
                ),
                spacing="4",
                width="100%",
            ),
            max_width="500px",
            background_color=styles.BG_PANEL,
            style={"border_radius": "24px", "padding": "2em"},
        ),
        open=DesocupacionesState.modal_create_open,
        on_open_change=DesocupacionesState.set_modal_create_open,
    )
