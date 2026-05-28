"""
Modal Neumórfico para Renovación de Contratos (Mandatos y Arrendamientos).
"""

import reflex as rx
from src.presentacion_reflex.state.contratos_state import ContratosState
from src.presentacion_reflex.components.neuro_elements import neuro_button, neuro_input, neuro_badge
import src.presentacion_reflex.styles as styles

def modal_renovacion_contrato() -> rx.Component:
    """Modal para confirmar y ejecutar la renovación de un contrato."""
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title(
                rx.hstack(
                    rx.icon("refresh-cw", size=24, color="var(--green-9)"),
                    rx.text("Renovar Contrato", weight="bold"),
                    align="center",
                    spacing="2",
                )
            ),
            rx.dialog.description(
                "Revise la proyección de la renovación. Puede ajustar la nueva fecha de vencimiento si lo requiere. "
                "Esta operación cerrará el ciclo actual del contrato e iniciará uno nuevo de manera automática.",
                margin_bottom="1.5rem",
                color="var(--gray-11)",
            ),

            # Error message
            rx.cond(
                ContratosState.error_message != "",
                rx.callout(
                    ContratosState.error_message,
                    icon="alert-triangle",
                    color_scheme="red",
                    margin_bottom="1rem",
                ),
            ),

            rx.cond(
                ContratosState.renewal_loading_proyeccion,
                rx.center(rx.spinner(size="3"), height="150px"),
                rx.cond(
                    ContratosState.renewal_proyeccion.contains("error"),
                    # Visor de Error en Proyección
                    rx.callout(
                        ContratosState.renewal_proyeccion["error"],
                        icon="alert-triangle",
                        color_scheme="ruby",
                        margin_y="1rem",
                        width="100%",
                    ),
                    # Vista Normal de Proyecciones
                    rx.vstack(
                        # KPIs View of Proyecciones
                        rx.grid(
                            # Canon Anterior
                            rx.box(
                                rx.text("Canon Anterior", size="1", color="var(--gray-11)", weight="medium"),
                                rx.text(
                                    f"${ContratosState.renewal_proyeccion['canon_actual'].to(str)}",
                                    weight="bold",
                                    size="4",
                                ),
                                padding="3",
                                border_radius="8px",
                                bg="var(--gray-3)",
                                style={"box_shadow": styles.SHADOW_INSET_ELITE},
                            ),
                            # Nuevo Canon / Incremento
                            rx.box(
                                rx.text("Nuevo Canon Proyectado", size="1", color="var(--gray-11)", weight="medium"),
                                rx.hstack(
                                    rx.text(
                                        f"${ContratosState.renewal_proyeccion['canon_nuevo'].to(str)}",
                                        weight="bold",
                                        size="4",
                                        color="var(--green-11)",
                                    ),
                                    rx.cond(
                                        ContratosState.renewal_proyeccion.contains("aplica_ipc") & ContratosState.renewal_proyeccion["aplica_ipc"].to(bool),
                                        neuro_badge(f"{ContratosState.renewal_proyeccion['porcentaje_ipc'].to(str)}% IPC", color_scheme="cyan", size="1"),
                                    ),
                                ),
                                padding="3",
                                border_radius="8px",
                                bg="var(--green-3)",
                                style={"box_shadow": styles.SHADOW_INSET_ELITE},
                            ),
                            columns="2",
                            spacing="3",
                            width="100%",
                            margin_bottom="1rem",
                        ),

                        # Nueva Fecha de Fin (Editable)
                        rx.vstack(
                            rx.text("Nueva Fecha de Vencimiento", size="2", weight="bold"),
                            neuro_input(
                                rx.input.slot(rx.icon("calendar")),
                                type="date",
                                value=ContratosState.renewal_nueva_fecha_fin,
                                on_change=ContratosState.set_renewal_fecha_fin,
                                width="100%",
                            ),
                            rx.cond(
                                ContratosState.renewal_proyeccion.contains("mensaje"),
                                rx.text(ContratosState.renewal_proyeccion["mensaje"], size="1", color="var(--blue-11)"),
                            ),
                            spacing="1",
                            width="100%",
                        ),
                        spacing="4",
                        width="100%",
                    )
                ),
            ),

            # Buttons
            rx.flex(
                rx.dialog.close(
                    neuro_button(
                        "Cancelar",
                        variant="soft",
                        color_scheme="gray",
                        on_click=ContratosState.cancel_renewal,
                    )
                ),
                rx.cond(
                    ContratosState.renewal_proyeccion.contains("error"),
                    rx.box(display="none"), # Oculta el botón de confirmación si hay error en la proyección
                    neuro_button(
                        rx.cond(
                            ContratosState.is_loading, rx.spinner(size="1"), rx.text("Confirmar Renovación")
                        ),
                        color_scheme="green",
                        on_click=ContratosState.execute_renewal,
                        disabled=ContratosState.is_loading | ContratosState.renewal_loading_proyeccion,
                    ),
                ),
                spacing="3",
                margin_top="1.5rem",
                justify="end",
            ),
            max_width="550px",
            style={"box_shadow": styles.SHADOW_RAISED_ELITE, "border_radius": "16px", "background": "var(--gray-2)"},
        ),
        open=ContratosState.show_renewal_confirm,
        on_open_change=lambda _: ContratosState.cancel_renewal(),
    )
