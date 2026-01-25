"""
Modal de Confirmación de Finalización
Diseño élite para confirmar acciones críticas.
"""

import reflex as rx

from src.presentacion_reflex.state.desocupaciones_state import DesocupacionesState


def finalize_confirm_modal() -> rx.Component:
    """Modal de confirmación para finalizar proceso."""
    return rx.alert_dialog.root(
        rx.alert_dialog.content(
            rx.alert_dialog.title(
                rx.hstack(
                    rx.icon("shield_check", size=24, color="var(--green-9)"),
                    rx.text("Confirmar Finalización"),
                    align_items="center",
                    spacing="2",
                )
            ),
            rx.alert_dialog.description(
                rx.vstack(
                    rx.text(
                        "¿Está seguro de que desea finalizar este proceso de desocupación?",
                        font_size="1em",
                    ),
                    # Información de la propiedad
                    rx.box(
                        rx.vstack(
                            rx.text(
                                "Propiedad:",
                                font_weight="bold",
                                color="var(--gray-11)",
                                font_size="0.85em",
                            ),
                            rx.text(
                                DesocupacionesState.finalize_info["direccion"], font_weight="medium"
                            ),
                            rx.text(
                                DesocupacionesState.finalize_info["inquilino"],
                                color="var(--gray-10)",
                                font_size="0.9em",
                            ),
                            spacing="1",
                            align_items="start",
                        ),
                        padding="1em",
                        background="var(--gray-3)",
                        border_radius="8px",
                        width="100%",
                        margin_top="1em",
                    ),
                    # Advertencia si hay tareas pendientes (Cierre Forzado)
                    rx.cond(
                        ~DesocupacionesState.finalize_info["puede_finalizar"],
                        rx.callout(
                            rx.vstack(
                                rx.text("⚠️ ADVERTENCIA: Tareas pendientes", font_weight="bold"),
                                rx.text("Hay tareas sin completar. Si continúa, el sistema:"),
                                rx.unordered_list(
                                    rx.list_item("Autocompletará todas las tareas pendientes"),
                                    rx.list_item("Finalizará el contrato inmediatamente"),
                                    rx.list_item("Liberará la propiedad"),
                                    padding_left="1.5em",
                                ),
                                rx.text(
                                    DesocupacionesState.finalize_info["mensaje_validacion"],
                                    font_weight="medium",
                                ),
                                spacing="2",
                            ),
                            icon="triangle_alert",
                            color_scheme="orange",
                            role="alert",
                            width="100%",
                        ),
                        rx.callout(
                            rx.vstack(
                                rx.text("Esta acción realizará lo siguiente:"),
                                rx.unordered_list(
                                    rx.list_item("Marcará el contrato como Finalizado"),
                                    rx.list_item("Liberará la propiedad para nuevos arriendos"),
                                    rx.list_item("Cerrará el proceso de desocupación"),
                                    padding_left="1.5em",
                                ),
                                spacing="2",
                            ),
                            icon="info",
                            color_scheme="blue",
                            width="100%",
                        ),
                    ),
                    spacing="3",
                    width="100%",
                    margin_top="0.5em",
                )
            ),
            rx.flex(
                rx.alert_dialog.cancel(
                    rx.button(
                        "Cancelar",
                        variant="soft",
                        color_scheme="gray",
                        on_click=DesocupacionesState.close_finalize_modal,
                    )
                ),
                rx.alert_dialog.action(
                    rx.button(
                        "Confirmar y Finalizar",
                        color_scheme=rx.cond(
                            ~DesocupacionesState.finalize_info["puede_finalizar"], "orange", "green"
                        ),
                        on_click=DesocupacionesState.confirm_finalize_process,
                    )
                ),
                gap="3",
                justify="end",
                margin_top="1.5em",
            ),
            max_width="500px",
        ),
        open=DesocupacionesState.modal_confirm_finalize_open,
        on_open_change=DesocupacionesState.close_finalize_modal,
    )
