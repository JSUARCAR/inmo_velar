import reflex as rx

from src.presentacion_reflex.state.desocupaciones_state import DesocupacionesState
from src.presentacion_reflex.components.neuro_elements import neuro_input, neuro_button, neuro_select_root
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
                        icon="alert-triangle",
                        color_scheme="red",
                        role="alert",
                        width="100%",
                    ),
                ),
                rx.vstack(
                    rx.vstack(
                        rx.text("Contrato *", weight="bold", size="2"),
                        neuro_select_root(
                            rx.foreach(
                                DesocupacionesState.contratos_candidatos,
                                lambda x: rx.select.item(x["texto"], value=x["id"]),
                            ),
                            placeholder="Seleccione el contrato...",
                            on_change=DesocupacionesState.set_id_contrato,
                            name="id_contrato",
                            width="100%",
                        ),
                        spacing="1",
                        width="100%",
                    ),
                    rx.vstack(
                        rx.text("Fecha Programada *", weight="bold", size="2"),
                        neuro_input(
                            type="date",
                            name="fecha_programada",
                            on_change=DesocupacionesState.set_fecha_programada,
                            width="100%",
                        ),
                        spacing="1",
                        width="100%",
                    ),
                    rx.vstack(
                        rx.text("Observaciones Iniciales", weight="bold", size="2"),
                        rx.text_area(
                            placeholder="Notas adicionales sobre la entrega...",
                            name="observaciones",
                            on_change=DesocupacionesState.set_observaciones,
                            width="100%",
                            style=styles.NEU_INPUT_STYLE,
                        ),
                        spacing="1",
                        width="100%",
                    ),
                    spacing="4",
                    width="100%",
                ),
                rx.flex(
                    rx.dialog.close(
                        rx.button(
                            "Cancelar",
                            variant="soft",
                            color_scheme="gray",
                            on_click=DesocupacionesState.close_create_modal,
                        )
                    ),
                    rx.button(
                        "Iniciar Desocupación",
                        on_click=DesocupacionesState.create_desocupacion(
                            DesocupacionesState.form_create_data
                        ),
                        loading=DesocupacionesState.is_loading,
                        color_scheme="blue",
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
