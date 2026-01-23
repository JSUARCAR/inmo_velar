import reflex as rx
from src.presentacion_reflex.state.contratos_state import ContratosState
from src.presentacion_reflex.state.auth_state import AuthState
from src.presentacion_reflex.state.pdf_state import PDFState

def contrato_card(contrato: dict) -> rx.Component:
    """
    Tarjeta visual para un contrato (Mandato o Arrendamiento).
    Estilo Elite estandarizado.
    """
    return rx.card(
        rx.vstack(
            # Header: Tipo y Estado
            rx.hstack(
                rx.badge(
                    contrato["tipo"],
                    color_scheme=rx.cond(
                        contrato["tipo"] == "Mandato",
                        "blue",
                        "green",
                    ),
                    radius="full",
                    variant="soft",
                ),
                rx.spacer(),
                rx.badge(
                    contrato["estado"],
                    color_scheme=rx.cond(
                        contrato["estado"] == "Activo",
                        "green",
                        "red",
                    ),
                    variant="surface",
                ),
                width="100%",
                align="center",
            ),
            
            # Info: Propiedad
            rx.vstack(
                rx.text(
                    contrato.get("propiedad", "N/A"),
                    size="3",
                    weight="bold",
                    color="var(--gray-12)",
                ),
                rx.text(
                    f"ID: {contrato['id']}",
                    size="1",
                    color="var(--gray-9)",
                ),
                spacing="1",
                align="start",
            ),
            
            rx.separator(),
            
            # Info: Partes (Propietario / Arrendatario)
            rx.hstack(
                rx.icon("user", size=16, color="var(--blue-9)"),
                rx.vstack(
                    rx.text(
                        contrato.get("propietario", contrato.get("arrendatario", "N/A")),
                        size="2",
                        weight="medium",
                        color="var(--gray-11)",
                    ),
                    rx.text(
                        contrato.get("documento_propietario", contrato.get("documento_arrendatario", "")),
                        size="1",
                        color="var(--gray-9)",
                    ),
                    spacing="0",
                ),
                align="center",
                spacing="2",
            ),
            
            # Info: Fechas y Valor
            rx.grid(
                rx.vstack(
                    rx.text("Inicio", size="1", color="var(--gray-9)"),
                    rx.text(contrato["fecha_inicio"], size="2", weight="medium"),
                    spacing="0",
                ),
                rx.vstack(
                    rx.text("Fin", size="1", color="var(--gray-9)"),
                    rx.text(contrato["fecha_fin"], size="2", weight="medium"),
                    spacing="0",
                ),
                rx.vstack(
                    rx.text("Valor", size="1", color="var(--gray-9)"),
                    rx.text(f"${contrato['canon']:,.0f}", size="2", weight="bold", color="var(--blue-9)"),
                    spacing="0",
                ),
                columns="3",
                width="100%",
                gap="2",
            ),
            
            rx.spacer(),
            
            # Actions Row (Scrollable if many actions)
            rx.scroll_area(
                rx.hstack(
                    # Ver Detalle
                    rx.tooltip(
                        rx.icon_button(
                            rx.icon("eye", size=18),
                            on_click=lambda: ContratosState.open_detail_modal(contrato["id"], contrato["tipo"]),
                            variant="surface",
                            size="2",
                            color_scheme="blue",
                        ),
                        content="Ver Detalle"
                    ),
                    
                    # --- ACCIONES ARRENDAMIENTO ---
                    rx.cond(
                        contrato["tipo"] == "Arrendamiento",
                        rx.hstack(
                             rx.tooltip(
                                rx.icon_button(
                                    rx.icon("file-check", size=18),
                                    on_click=lambda: PDFState.generar_contrato_arrendamiento_elite(contrato["id"], False),
                                    variant="ghost", size="2", color_scheme="purple",
                                ),
                                content="Contrato Oficial"
                             ),
                             rx.cond(
                                AuthState.check_action("Contratos", "IPC"),
                                rx.tooltip(
                                    rx.icon_button(
                                        rx.icon("trending-up", size=18),
                                        on_click=lambda: ContratosState.open_ipc_modal(contrato["id"]),
                                        variant="ghost", size="2", color_scheme="cyan",
                                        disabled=contrato["estado"] != "Activo",
                                    ),
                                    content="Incremento IPC"
                                )
                             ),
                             spacing="1",
                        )
                    ),

                    # --- ACCIONES MANDATO ---
                    rx.cond(
                        contrato["tipo"] == "Mandato",
                         rx.tooltip(
                            rx.icon_button(
                                rx.icon("file-check", size=18),
                                on_click=lambda: PDFState.generar_contrato_mandato_elite(contrato["id"], False),
                                variant="ghost", size="2", color_scheme="purple",
                            ),
                            content="Contrato Oficial"
                         ),
                    ),

                    # Editar
                    rx.cond(
                        AuthState.check_action("Contratos", "EDITAR"),
                        rx.tooltip(
                            rx.icon_button(
                                rx.icon("pencil", size=18),
                                on_click=lambda: ContratosState.open_edit_modal(contrato["id"], contrato["tipo"]),
                                variant="ghost", size="2", color_scheme="gray",
                            ),
                            content="Editar"
                        )
                    ),
                    
                    # Terminar
                    rx.cond(
                        AuthState.check_action("Contratos", "TERMINAR"),
                        rx.tooltip(
                            rx.icon_button(
                                rx.icon("ban", size=18),
                                on_click=lambda: ContratosState.toggle_estado(contrato["id"], contrato["tipo"], contrato["estado"]),
                                variant="ghost", size="2", color_scheme="red",
                                disabled=contrato["estado"] != "Activo",
                            ),
                            content="Terminar"
                        )
                    ),
                    spacing="2",
                    padding_y="1",
                ),
                type="hover",
                scrollbars="horizontal",
                style={"width": "100%"}
            ),
            
            spacing="3",
            height="100%",
            justify="between",
        ),
        padding="4",
        style={
            "background": "var(--card-bg)",
            "border": "1px solid var(--gray-4)",
            "border_radius": "16px",
            "box_shadow": "var(--shadow-sm)",
            "transition": "all 0.2s ease",
            "_hover": {
                "transform": "translateY(-4px)",
                "box_shadow": "var(--shadow-md)",
                "border_color": "var(--blue-6)",
            },
        },
        width="100%",
        min_height="220px",
    )
