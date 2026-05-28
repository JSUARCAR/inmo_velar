import reflex as rx

from src.presentacion_reflex.state.auth_state import AuthState
from src.presentacion_reflex.state.incidentes_state import IncidentesState
from src.presentacion_reflex.components.neuro_elements import neuro_button
from src.presentacion_reflex import styles


def modal_cancel_incidente() -> rx.Component:
    inc = IncidentesState.cancel_incidente
    estado = inc.get("estado", "")

    return rx.dialog.root(
        rx.dialog.content(
            rx.card(
                rx.vstack(
                    rx.heading("Cancelar Incidente", size="5", color="var(--red-9)"),
                    rx.text(
                        "ID: ",
                        inc.get("id", ""),
                        " | Estado: ",
                        estado,
                        size="2",
                        color="gray",
                        margin_bottom="0.5em",
                    ),
                    rx.callout(
                        "Confirme los detalles antes de cancelar el reporte.",
                        icon="alert-triangle",
                        color_scheme="red",
                        width="100%",
                        margin_bottom="1em",
                    ),
                    rx.divider(margin_y="0.5em"),
                    rx.vstack(
                        rx.text(
                            "Esta seguro que desea cancelar este incidente?",
                            weight="bold",
                            size="3",
                            width="100%",
                        ),
                        rx.text(
                            "Esta accion no se puede deshacer.",
                            size="2",
                            color="gray",
                            width="100%",
                            margin_bottom="1em",
                        ),
                        rx.text(
                            "Motivo de cancelacion (obligatorio)",
                            weight="bold",
                            size="2",
                            margin_bottom="0.5em",
                        ),
                        rx.text_area(
                            placeholder="Ingrese el motivo por el cual desea cancelar el incidente...",
                            on_change=IncidentesState.set_cancel_motivo,
                            value=IncidentesState.cancel_motivo,
                            width="100%",
                            style=styles.NEU_INPUT_STYLE,
                            min_height="100px",
                        ),
                        rx.cond(
                            IncidentesState.cancel_error != "",
                            rx.callout(
                                IncidentesState.cancel_error,
                                icon="alert-triangle",
                                color_scheme="red",
                                width="100%",
                                margin_top="0.5em",
                            ),
                        ),
                        spacing="3",
                        width="100%",
                    ),
                    rx.hstack(
                        neuro_button(
                            "Cerrar",
                            on_click=IncidentesState.close_cancel_modal,
                            variant="soft",
                            color_scheme="gray",
                        ),
                        rx.spacer(),
                        neuro_button(
                            "Confirmar Cancelacion",
                            on_click=IncidentesState.confirmar_cancelacion,
                            loading=IncidentesState.is_loading,
                            color_scheme="red",
                        ),
                        width="100%",
                        margin_top="1em",
                    ),
                    spacing="4",
                    width="100%",
                ),
                width="100%",
                style={"box_shadow": styles.NEU_SHADOW},
            ),
            width="500px",
            max_width="95vw",
            background_color=styles.BG_PANEL,
            style={"border_radius": "24px", "padding": "1.5em"},
        ),
        open=IncidentesState.cancel_modal_open,
        on_open_change=IncidentesState.close_cancel_modal,
    )
