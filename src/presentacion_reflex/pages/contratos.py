"""Página de Contratos - Reflex Elite"""
import reflex as rx
from src.presentacion_reflex import styles
from src.presentacion_reflex.components.layout.dashboard_layout import dashboard_layout
from src.presentacion_reflex.state.auth_state import AuthState
from src.presentacion_reflex.state.contratos_state import ContratosState
from src.presentacion_reflex.components.neuro_elements import (
    neuro_input,
    neuro_select_root,
    neuro_button,
    neuro_icon_action_button,
    neuro_badge,
    neuro_panel,
)
from src.presentacion_reflex.components.contratos.contrato_card import contrato_card
from src.presentacion_reflex.components.contratos.contrato_mandato_form import contrato_mandato_form
from src.presentacion_reflex.components.contratos.contrato_arrendamiento_form import contrato_arrendamiento_form
from src.presentacion_reflex.components.contratos.contrato_detail_modal import contrato_detail_modal
from src.presentacion_reflex.components.contratos.ipc_increment_modal import ipc_increment_modal
from src.presentacion_reflex.components.shared.elite_gradient_icon import elite_gradient_icon_labeled
from src.presentacion_reflex.state.pdf_state import PDFState

def render_table_view() -> rx.Component:
    """Tabla de contratos con botones del ciclo flat-raised-inset."""

    def _tabla_acciones(c: dict) -> rx.Component:
        return rx.hstack(
            # Detalle
            neuro_icon_action_button(
                "eye",
                color_scheme="blue",
                size="1",
                tooltip_content="Ver Detalle",
                on_click=lambda: ContratosState.open_detail_modal(
                    c["id_contrato"], c["tipo_contrato"]
                ),
            ),
            # Editar
            rx.cond(
                AuthState.check_action("Contratos", "EDITAR"),
                neuro_icon_action_button(
                    "pencil",
                    color_scheme="gray",
                    size="1",
                    tooltip_content="Editar",
                    on_click=lambda: ContratosState.open_edit_modal(
                        c["id_contrato"], c["tipo_contrato"]
                    ),
                ),
            ),
            # Renovar
            rx.cond(
                AuthState.check_action("Contratos", "RENOVAR"),
                neuro_icon_action_button(
                    "refresh-cw",
                    color_scheme="green",
                    size="1",
                    tooltip_content="Renovar Contrato",
                    disabled=c["estado_contrato"] != "Activo",
                    on_click=lambda: ContratosState.confirm_renewal(
                        c["id_contrato"], c["tipo_contrato"]
                    ),
                ),
            ),
            # IPC — solo Arrendamiento
            rx.cond(
                (c["tipo_contrato"] == "Arrendamiento") &
                AuthState.check_action("Contratos", "IPC"),
                neuro_icon_action_button(
                    "trending-up",
                    color_scheme="cyan",
                    size="1",
                    tooltip_content="Aplicar IPC",
                    disabled=c["estado_contrato"] != "Activo",
                    on_click=lambda: ContratosState.open_ipc_modal(c["id_contrato"]),
                ),
            ),
            # PDF Contrato Oficial
            neuro_icon_action_button(
                "file-check",
                color_scheme="purple",
                size="1",
                tooltip_content="Generar Contrato Oficial",
                on_click=lambda: rx.cond(
                    c["tipo_contrato"] == "Mandato",
                    PDFState.generar_contrato_mandato_elite(c["id_contrato"], False),
                    PDFState.generar_contrato_arrendamiento_elite(c["id_contrato"], False),
                ),
            ),
            # Terminar
            rx.cond(
                AuthState.check_action("Contratos", "TERMINAR"),
                neuro_icon_action_button(
                    "ban",
                    color_scheme="red",
                    size="1",
                    tooltip_content="Terminar Contrato",
                    disabled=c["estado_contrato"] != "Activo",
                    on_click=lambda: ContratosState.toggle_estado(
                        c["id_contrato"], c["tipo_contrato"], c["estado_contrato"]
                    ),
                ),
            ),
            spacing="2",
        )

    return rx.table.root(
        rx.table.header(
            rx.table.row(
                rx.table.column_header_cell("Propiedad"),
                rx.table.column_header_cell("Tipo"),
                rx.table.column_header_cell("Estado"),
                rx.table.column_header_cell("Propietario/Arrendatario"),
                rx.table.column_header_cell("Valor"),
                rx.table.column_header_cell("Fechas"),
                rx.table.column_header_cell("Acciones"),
            )
        ),
        rx.table.body(
            rx.foreach(
                ContratosState.contratos,
                lambda c: rx.table.row(
                    rx.table.cell(
                        rx.vstack(
                            rx.text(c["propiedad_direccion"], weight="bold", size="2"),
                            rx.text(c["propiedad_matricula"], size="1", color=styles.TEXT_SECONDARY),
                            spacing="1",
                        )
                    ),
                    rx.table.cell(
                        neuro_badge(
                            c["tipo_contrato"],
                            color_scheme=rx.cond(c["tipo_contrato"] == "Mandato", "blue", "green"),
                        )
                    ),
                    rx.table.cell(
                        neuro_badge(
                            c["estado_contrato"],
                            color_scheme=rx.cond(c["estado_contrato"] == "Activo", "green", "red"),
                        )
                    ),
                    rx.table.cell(
                        rx.vstack(
                            rx.text(
                                rx.cond(
                                    c["tipo_contrato"] == "Mandato",
                                    c["propietario_nombre"],
                                    c["arrendatario_nombre"]
                                ),
                                size="2",
                            ),
                            rx.text(
                                rx.cond(
                                    c["tipo_contrato"] == "Mandato",
                                    c["propietario_documento"],
                                    c["arrendatario_documento"]
                                ),
                                size="1", color=styles.TEXT_SECONDARY
                            ),
                            rx.cond(
                                c["habitante_nombre"] != "",
                                rx.hstack(
                                    rx.icon("home", size=12, color=styles.TEXT_SECONDARY),
                                    rx.text(c["habitante_nombre"], size="1", color=styles.TEXT_SECONDARY),
                                    spacing="1",
                                    align="center"
                                )
                            ),
                            rx.cond(
                                c["asesor_nombre"] != "",
                                rx.hstack(
                                    rx.icon("headset", size=12, color=styles.TEXT_SECONDARY),
                                    rx.text(c["asesor_nombre"], size="1", color=styles.TEXT_SECONDARY),
                                    spacing="1",
                                    align="center"
                                )
                            ),
                            spacing="1",
                        )
                    ),
                    rx.table.cell(rx.text(f"${c['valor_canon']}", weight="bold")),
                    rx.table.cell(
                        rx.vstack(
                            rx.text(f"Inicia: {c['fecha_inicio']}", size="1"),
                            rx.text(f"Vence: {c['fecha_fin']}", size="1"),
                            spacing="1",
                        )
                    ),
                    rx.table.cell(_tabla_acciones(c)),
                )
            )
        ),
        width="100%",
        class_name="neu-table-elite",
    )

def contratos_page() -> rx.Component:
    """Componente principal de la página de contratos."""
    return rx.fragment(
        rx.toast.provider(),
        dashboard_layout(
            rx.vstack(
                # Encabezado
                rx.box(
                    rx.hstack(
                        elite_gradient_icon_labeled(
                            "file-text",
                            "Gestión de Contratos",
                            description="Administración de mandatos y arrendamientos",
                            size=28,
                            accent="purple",
                        ),
                        rx.spacer(),
                        rx.hstack(
                            rx.cond(
                                AuthState.check_action("Contratos", "CREAR"),
                                rx.hstack(
                                    neuro_button(
                                        rx.icon("plus", size=18),
                                        "Nuevo Mandato",
                                        on_click=ContratosState.open_create_mandato_modal,
                                        variant="surface",
                                        style={"box_shadow": styles.SHADOW_RAISED_ELITE},
                                    ),
                                    neuro_button(
                                        rx.icon("plus", size=18),
                                        "Nuevo Arriendo",
                                        on_click=ContratosState.open_create_arrendamiento_modal,
                                        variant="surface",
                                        style={"box_shadow": styles.SHADOW_RAISED_ELITE},
                                    ),
                                    spacing="3",
                                ),
                            ),
                        ),
                        width="100%",
                        padding="5",
                        align="center",
                    ),
                    width="100%",
                ),

                # Barra de Herramientas (Filtros y Búsqueda)
                neuro_panel(
                    rx.flex(
                        neuro_input(
                            rx.input.slot(rx.icon("search", size=18)),
                            placeholder="Buscar por dirección, nombre o documento...",
                            value=ContratosState.search_text,
                            on_change=ContratosState.set_search,
                            on_key_down=ContratosState.handle_search_key_down,
                            width=rx.breakpoints(initial="100%", md="400px"),
                            style={
                                **{
                                    "box_shadow": styles.SHADOW_INSET_ELITE,
                                }
                            },
                        ),
                        rx.spacer(),
                        rx.hstack(
                            neuro_select_root(
                                rx.foreach(ContratosState.asesores_filter_options, lambda opt: rx.select.item(opt[0], value=opt[1])),
                                value=ContratosState.filter_asesor_id,
                                on_change=ContratosState.set_filter_asesor_id,
                                width="200px",
                                style={"box_shadow": styles.SHADOW_INSET_ELITE, "border_radius": "8px"},
                            ),
                            neuro_select_root(
                                rx.foreach(ContratosState.tipo_options, lambda opt: rx.select.item(opt, value=opt)),
                                value=ContratosState.filter_tipo,
                                on_change=ContratosState.set_filter_tipo,
                                width="160px",
                                style={"box_shadow": styles.SHADOW_INSET_ELITE, "border_radius": "8px"},
                            ),
                            neuro_select_root(
                                rx.foreach(ContratosState.estado_options, lambda opt: rx.select.item(opt, value=opt)),
                                value=ContratosState.filter_estado,
                                on_change=ContratosState.set_filter_estado,
                                width="140px",
                                style={"box_shadow": styles.SHADOW_INSET_ELITE, "border_radius": "8px"},
                            ),
                            neuro_button(
                                rx.cond(ContratosState.is_grid_view, rx.icon("table"), rx.icon("layout-grid")),
                                on_click=ContratosState.toggle_view,
                            ),
                            spacing="3",
                        ),
                        width="100%",
                        flex_direction=rx.breakpoints(initial="column", md="row"),
                        align="center",
                        gap="4",
                    ),
                    width="100%",
                ),

                # Contenido de Datos
                rx.cond(
                    ContratosState.is_loading,
                    rx.center(rx.spinner(size="3"), height="400px", width="100%"),
                    rx.box(
                        rx.cond(
                            ContratosState.total_items == 0,
                            rx.center(
                                rx.vstack(
                                    rx.icon("search-x", size=64, color="var(--gray-6)"),
                                    rx.text("No se encontraron contratos", size="5", weight="bold"),
                                    rx.text("Ajusta los filtros o registra uno nuevo", size="2", color=styles.TEXT_SECONDARY),
                                    spacing="3",
                                    align="center",
                                ),
                                height="400px",
                                width="100%",
                            ),
                            rx.box(
                                rx.cond(
                                    ContratosState.is_grid_view,
                                    rx.grid(
                                        rx.foreach(ContratosState.contratos, contrato_card),
                                        columns=rx.breakpoints(initial="1", sm="2", lg="3"),
                                        gap="8",
                                        width="100%",
                                        padding="4",
                                    ),
                                    render_table_view(),
                                ),
                                width="100%",
                            ),
                        ),
                        width="100%",
                    ),
                ),

                # Paginación
                neuro_panel(
                    rx.hstack(
                        neuro_button(
                            rx.hstack(rx.icon("chevron-left", size=16), rx.text("Anterior")),
                            on_click=ContratosState.prev_page,
                            disabled=ContratosState.current_page == 1,
                        ),
                        rx.text(f"Página {ContratosState.current_page}", weight="medium"),
                        neuro_button(
                            rx.hstack(rx.text("Siguiente"), rx.icon("chevron-right", size=16)),
                            on_click=ContratosState.next_page,
                            disabled=ContratosState.current_page * ContratosState.page_size >= ContratosState.total_items,
                        ),
                        justify="center",
                        width="100%",
                        spacing="4",
                        align="center",
                    ),
                    width="100%",
                ),
                spacing="6",
                width="100%",
                padding_x=["4", "6"],
                padding_bottom="8",
            ),
        ),
        # Modales
        contrato_mandato_form(),
        contrato_arrendamiento_form(),
        contrato_detail_modal(),
        ipc_increment_modal(),
    )

# Ruta protegida
@rx.page(route="/contratos", on_load=[AuthState.require_login, ContratosState.on_load])
def contratos():
    return contratos_page()
