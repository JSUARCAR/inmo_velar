import reflex as rx

from src.presentacion_reflex import styles
from src.presentacion_reflex.state.auth_state import AuthState
from src.presentacion_reflex.state.contratos_state import ContratosState, ContratoDict
from src.presentacion_reflex.state.pdf_state import PDFState
from src.presentacion_reflex.components.neuro_elements import (
    neuro_icon_action_button,
    neuro_badge,
    neuro_divider,
    neuro_panel,
)


def tarjeta_contrato(contrato: ContratoDict) -> rx.Component:
    """
    Tarjeta visual para un contrato (Mandato o Arrendamiento).
    Estilo Elite estandarizado con tipado estricto.
    """
    return neuro_panel(
        rx.vstack(
            # Header: Tipo, Estado y Cumplimiento
            rx.hstack(
                neuro_badge(
                    contrato.tipo_contrato,
                    color_scheme=rx.cond(
                        contrato.tipo_contrato == "Mandato",
                        "blue",
                        "green",
                    ),
                    radius="full",
                ),
                neuro_badge(
                    contrato.estado_cumplimiento,
                    color_scheme=rx.cond(
                        contrato.estado_cumplimiento == "AL_DIA",
                        "green",
                        rx.cond(
                            contrato.estado_cumplimiento == "VENCIDO",
                            "red",
                            "yellow",
                        ),
                    ),
                    radius="full",
                    tooltip=rx.cond(
                        contrato.estado_cumplimiento == "AL_DIA",
                        "Pago al día",
                        rx.cond(
                            contrato.estado_cumplimiento == "VENCIDO",
                            "Pago vencido",
                            "Pago pendiente",
                        ),
                    ),
                ),
                rx.spacer(),
                neuro_badge(
                    contrato.estado_contrato,
                    color_scheme=rx.cond(
                        contrato.estado_contrato == "Activo",
                        "green",
                        "red",
                    ),
                ),
                width="100%",
                align="center",
            ),
            # Info: Propiedad
            rx.vstack(
                rx.text(
                    contrato.propiedad_direccion,
                    size="3",
                    weight="bold",
                    color="var(--gray-12)",
                ),
                neuro_badge(
                    contrato.propiedad_tipo,
                    color_scheme="indigo",
                    size="1",
                    radius="full",
                ),
                rx.hstack(
                    rx.icon("hash", size=14, color="var(--gray-9)"),
                    rx.text(
                        "ID: ",
                        contrato.id_contrato.to_string(),
                        size="1",
                        weight="bold",
                        color="var(--gray-11)",
                    ),
                    align="center",
                    spacing="1",
                ),
                spacing="1",
                align="start",
            ),
            neuro_divider(),
            # Info: Partes (Propietario / Arrendatario)
            rx.hstack(
                rx.icon("user", size=16, color="var(--blue-9)"),
                rx.vstack(
                    rx.text(
                        rx.cond(
                            contrato.tipo_contrato == "Mandato",
                            contrato.propietario_nombre,
                            contrato.arrendatario_nombre,
                        ),
                        size="2",
                        weight="medium",
                        color="var(--gray-11)",
                    ),
                    rx.text(
                        rx.cond(
                            contrato.tipo_contrato == "Mandato",
                            contrato.propietario_documento,
                            contrato.arrendatario_documento,
                        ),
                        size="1",
                        color="var(--gray-9)",
                    ),
                    rx.cond(
                        contrato.habitante_nombre != "",
                        rx.hstack(
                            rx.icon("home", size=12, color="var(--gray-9)"),
                            rx.text(
                                "Habitante: ",
                                contrato.habitante_nombre,
                                size="1",
                                color="var(--gray-10)",
                            ),
                            spacing="1",
                            align="center",
                        ),
                    ),
                    spacing="0",
                ),
                align="center",
                spacing="2",
            ),
            # Info: Asesor
            rx.hstack(
                rx.icon("headset", size=16, color="var(--purple-9)"),
                rx.text(
                    contrato.asesor_nombre,
                    size="2",
                    weight="medium",
                    color="var(--gray-11)",
                ),
                align="center",
                spacing="2",
            ),
            # Info: Fechas y Valor
            rx.grid(
                rx.vstack(
                    rx.text("Inicio", size="1", color="var(--gray-9)"),
                    rx.text(contrato.fecha_inicio, size="2", weight="medium"),
                    spacing="0",
                ),
                rx.vstack(
                    rx.text("Fin", size="1", color="var(--gray-9)"),
                    rx.text(contrato.fecha_fin, size="2", weight="medium"),
                    spacing="0",
                ),
                rx.tooltip(
                    rx.vstack(
                        rx.text("Fecha Pago", size="1", color="var(--gray-9)"),
                        rx.cond(
                            contrato.fecha_pago != "",
                            rx.text(f"Día {contrato.fecha_pago}", size="2", weight="medium"),
                            rx.text("N/R", size="1", color="var(--gray-9)", font_style="italic"),
                        ),
                        spacing="0",
                    ),
                    content=rx.cond(
                        contrato.fecha_pago != "",
                        f"Pago día {contrato.fecha_pago} de cada mes",
                        "Configure la fecha de pago en el detalle del contrato",
                    ),
                ),
                rx.vstack(
                    rx.text("Valor", size="1", color="var(--gray-9)"),
                    rx.text(
                        "$",
                        contrato.valor_canon.to_string(),
                        size="2",
                        weight="bold",
                        color="var(--blue-9)",
                    ),
                    spacing="0",
                ),
                columns="4",
                width="100%",
                gap="2",
            ),
            rx.spacer(),
            # Actions Row (Scrollable if many actions)
            rx.scroll_area(
                rx.hstack(
                    # Ver Detalle
                    neuro_icon_action_button(
                        "eye",
                        on_click=lambda: ContratosState.open_detail_modal(
                            contrato.id_contrato, contrato.tipo_contrato
                        ),
                        color_scheme="blue",
                        tooltip_content="Ver Detalle",
                    ),
                    # --- ACCIONES ARRENDAMIENTO ---
                    rx.cond(
                        contrato.tipo_contrato == "Arrendamiento",
                        rx.hstack(
                            neuro_icon_action_button(
                                "file-check",
                                on_click=lambda: (
                                    PDFState.generar_contrato_arrendamiento_elite(
                                        contrato.id_contrato, False
                                    )
                                ),
                                color_scheme="purple",
                                tooltip_content="Contrato Oficial",
                            ),
                            rx.cond(
                                AuthState.check_action("Contratos", "IPC"),
                                neuro_icon_action_button(
                                    "trending-up",
                                    on_click=lambda: ContratosState.open_ipc_modal(
                                        contrato.id_contrato
                                    ),
                                    color_scheme="cyan",
                                    disabled=contrato.estado_contrato != "Activo",
                                    tooltip_content="Incremento IPC",
                                ),
                            ),
                            spacing="1",
                        ),
                    ),
                    # --- ACCIONES MANDATO ---
                    rx.cond(
                        contrato.tipo_contrato == "Mandato",
                        neuro_icon_action_button(
                            "file-check",
                            on_click=lambda: PDFState.generar_contrato_mandato_elite(
                                contrato.id_contrato, False
                            ),
                            color_scheme="purple",
                            tooltip_content="Contrato Oficial",
                        ),
                    ),
                    # Editar
                    rx.cond(
                        AuthState.check_action("Contratos", "EDITAR"),
                        neuro_icon_action_button(
                            "pencil",
                            on_click=lambda: ContratosState.open_edit_modal(
                                contrato.id_contrato, contrato.tipo_contrato
                            ),
                            color_scheme="gray",
                            tooltip_content="Editar",
                        ),
                    ),
                    # Renovación
                    rx.cond(
                        AuthState.check_action("Contratos", "RENOVAR"),
                        neuro_icon_action_button(
                            "refresh-cw",
                            on_click=lambda: ContratosState.confirm_renewal(
                                contrato.id_contrato, contrato.tipo_contrato
                            ),
                            color_scheme="green",
                            disabled=contrato.estado_contrato != "Activo",
                            tooltip_content="Renovar",
                        ),
                    ),
                    # Terminar
                    rx.cond(
                        AuthState.check_action("Contratos", "TERMINAR"),
                        neuro_icon_action_button(
                            "ban",
                            on_click=lambda: ContratosState.toggle_estado(
                                contrato.id_contrato,
                                contrato.tipo_contrato,
                                contrato.estado_contrato,
                            ),
                            color_scheme="red",
                            disabled=contrato.estado_contrato != "Activo",
                            tooltip_content="Terminar",
                        ),
                    ),
                    spacing="2",
                    padding_y="1",
                ),
                type="hover",
                scrollbars="horizontal",
                style={"width": "100%"},
            ),
            spacing="3",
            height="100%",
            justify="between",
        ),
        padding="4",
        style=styles.NEU_CONTRACT_CARD_STYLE,
        width="100%",
        min_height="220px",
    )
