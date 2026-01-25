import reflex as rx

from src.presentacion_reflex.state.desocupaciones_state import DesocupacionesState


def modal_form() -> rx.Component:
    """Formulario modal para crear desocupación."""
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title("Iniciar Proceso de Desocupación"),
            rx.dialog.description(
                "Seleccione un contrato activo y una fecha programada para la entrega."
            ),
            rx.cond(
                DesocupacionesState.error_message != "",
                rx.callout.root(
                    rx.callout.icon(),
                    rx.callout.text(DesocupacionesState.error_message),
                    color_scheme="red",
                    role="alert",
                    width="100%",
                ),
            ),
            rx.flex(
                rx.text("Contrato", weight="bold", margin_bottom="4px"),
                rx.select.root(
                    rx.select.trigger(placeholder="Seleccione el contrato...", width="100%"),
                    rx.select.content(
                        rx.foreach(
                            DesocupacionesState.contratos_candidatos,
                            lambda x: rx.select.item(x["texto"], value=x["id"]),
                        )
                    ),
                    on_change=DesocupacionesState.set_id_contrato,
                    name="id_contrato",
                ),
                rx.text("Fecha Programada", weight="bold", margin_bottom="4px", margin_top="1em"),
                rx.input(
                    type="date",
                    name="fecha_programada",
                    on_change=DesocupacionesState.set_fecha_programada,
                    width="100%",
                ),
                rx.text(
                    "Observaciones Iniciales", weight="bold", margin_bottom="4px", margin_top="1em"
                ),
                rx.text_area(
                    placeholder="Notas adicionales...",
                    name="observaciones",
                    on_change=DesocupacionesState.set_observaciones,
                    width="100%",
                ),
                direction="column",
                spacing="3",
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
                ),
                spacing="3",
                margin_top="1.5em",
                justify="end",
            ),
            width="450px",
        ),
        open=DesocupacionesState.modal_create_open,
        on_open_change=DesocupacionesState.set_modal_create_open,
    )
