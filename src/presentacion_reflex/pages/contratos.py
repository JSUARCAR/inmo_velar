"""
Página de Contratos - Reflex
Gestión de contratos de mandato y arrendamiento con filtros, CRUD y paginación.
"""

import reflex as rx
from src.presentacion_reflex import styles

from src.presentacion_reflex.components.contratos import (
    contrato_arrendamiento_form,
    contrato_card,
    contrato_detail_modal,
    contrato_mandato_form,
    ipc_increment_modal,
)
from src.presentacion_reflex.components.layout.dashboard_layout import dashboard_layout
from src.presentacion_reflex.state.auth_state import AuthState
from src.presentacion_reflex.state.contratos_state import ContratosState
from src.presentacion_reflex.state.pdf_state import PDFState
from src.presentacion_reflex.components.neuro_elements import neuro_input, neuro_button, neuro_select_root


def contratos_page() -> rx.Component:
    """
    Página principal de Contratos con filtros y CRUD.
    """

    return rx.fragment(
        rx.toast.provider(),
        dashboard_layout(
            rx.vstack(
                # --- Elite Header ---
                rx.box(
                    rx.hstack(
                        rx.vstack(
                            rx.heading(
                                "Gestión de Contratos",
                                size="8",
                                weight="bold",
                                color=styles.TEXT_PRIMARY,
                            ),
                            rx.text("Contratos de arrendamiento y mandato", size="3"),
                            rx.hstack(
                                rx.icon("file-text", size=18, color="var(--gray-9)"),
                                rx.text(
                                    f"Total: {ContratosState.total_items} contratos",
                                    size="2",
                                    weight="medium",
                                    color=styles.TEXT_SECONDARY,
                                ),
                                spacing="2",
                                align="center",
                            ),
                            spacing="1",
                            align="start",
                        ),
                        rx.spacer(),
                        rx.cond(
                            AuthState.check_action("Contratos", "CREAR"),
                            rx.tooltip(
                                neuro_button(
                                    rx.hstack(rx.icon("plus", size=18), rx.text("Nuevo Contrato")),
                                    on_click=ContratosState.open_modal,
                                    size="3",
                                ),
                                content="Crear nuevo contrato",
                            ),
                        ),
                        width="100%",
                        padding="5",
                        align="center",
                    ),
                    width="100%",
                    padding_bottom="2",
                    border_radius="12px",
                    margin_bottom="1.5rem",
                    style={
                        "background": "linear-gradient(135deg, rgba(102, 126, 234, 0.05) 0%, rgba(118, 75, 162, 0.05) 100%)",
                        "backdrop_filter": "blur(10px)",
                    },
                ),
                # --- Toolbar con diseño neumórfico ---
                rx.card(
                    rx.hstack(
                        # Búsqueda
                        neuro_input(
                            rx.input.slot(rx.icon("search", size=18)),
                            placeholder="Buscar por propiedad, persona o documento...",
                            value=ContratosState.search_text,
                            on_change=ContratosState.set_search,
                            on_key_down=ContratosState.handle_search_key_down,
                            width="350px",
                            size="3",
                        ),
                        # Filtro Tipo
                        neuro_select_root(
                            [rx.select.item(opt, value=opt) for opt in ContratosState.tipo_options],
                            value=ContratosState.filter_tipo,
                            on_change=ContratosState.set_filter_tipo,
                            placeholder="Tipo",
                            width="150px",
                        ),
                        # Filtro Estado
                        neuro_select_root(
                            [rx.select.item(opt, value=opt) for opt in ContratosState.estado_options],
                            value=ContratosState.filter_estado,
                            on_change=ContratosState.set_filter_estado,
                            placeholder="Estado",
                            width="150px",
                        ),
                        # Filtro Asesor
                        neuro_select_root(
                            [
                                rx.select.item("Todos", value="todos"),
                                rx.foreach(
                                    ContratosState.asesores_select_options,
                                    lambda opcion: rx.select.item(opcion[0], value=opcion[1]),
                                ),
                            ],
                            value=ContratosState.filter_asesor_id,
                            on_change=ContratosState.set_filter_asesor,
                            placeholder="Asesor",
                            width="200px",
                        ),
                        rx.spacer(),
                        # Botones de acción
                        rx.hstack(
                            rx.tooltip(
                                neuro_button(
                                    rx.icon(
                                        rx.cond(ContratosState.is_grid_view, "table", "layout-grid"),
                                        size=18,
                                    ),
                                    on_click=ContratosState.toggle_view,
                                    size="3",
                                ),
                                content=rx.cond(
                                    ContratosState.is_grid_view,
                                    "Cambiar a vista de tabla",
                                    "Cambiar a vista de cards",
                                ),
                            ),
                            # Export button
                            rx.tooltip(
                                neuro_button(
                                    rx.icon("file-spreadsheet", size=16),
                                    on_click=ContratosState.exportar_csv,
                                    size="3",
                                ),
                                content="Exportar a Excel",
                            ),
                            # Botón para Incrementos IPC (Administrador o Gerencia)
                            rx.cond(
                                AuthState.check_action("Incrementos", "CREAR"),
                                rx.tooltip(
                                    neuro_button(
                                        rx.icon("trending-up", size=18),
                                        on_click=ContratosState.open_ipc_modal,
                                        size="3",
                                    ),
                                    content="Incrementos IPC Anuales",
                                ),
                            ),
                            # Botón Refresh
                            rx.tooltip(
                                neuro_button(
                                    rx.icon("refresh-cw", size=16),
                                    on_click=ContratosState.load_contratos,
                                    size="3",
                                ),
                                content="Recargar",
                            ),
                            spacing="3",
                        ),
                        spacing="3",
                        align="center",
                        width="100%",
                    ),
                    width="100%",
                    style={
                        "background": styles.BG_PANEL,
                        "box_shadow": styles.NEU_SHADOW,
                        "border": "none",
                        "border_radius": "16px",
                        "padding": "1.2rem",
                    },
                ),
                # Stats Summary
                rx.hstack(
                    rx.text(
                        f"Mostrando {ContratosState.contratos.length()} de {ContratosState.total_items} contratos",
                        size="2",
                        weight="medium",
                        color=styles.TEXT_SECONDARY,
                    ),
                    rx.spacer(),
                    # Toggle solo activos
                    rx.hstack(
                        rx.text("Solo Activos", size="2", color=styles.TEXT_SECONDARY),
                        rx.switch(
                            checked=ContratosState.solo_activos,
                            on_change=ContratosState.toggle_solo_activos,
                            size="1",
                            color_scheme="green",
                        ),
                        align="center",
                        spacing="2",
                    ),
                    width="100%",
                    padding_x="2",
                    margin_top="2",
                ),
                # Content Area (Grid or Table)
                rx.cond(
                    ContratosState.is_loading,
                    rx.center(
                        rx.vstack(
                            rx.spinner(size="3", color="var(--accent-9)"),
                            rx.text("Cargando contratos...", color="var(--gray-10)"),
                            spacing="4",
                        ),
                        height="400px",
                        width="100%",
                    ),
                    rx.box(
                        rx.cond(
                            ContratosState.contratos.length() == 0,
                            rx.center(
                                rx.vstack(
                                    rx.icon("file-question", size=64, color="var(--gray-6)"),
                                    rx.text(
                                        "No se encontraron contratos",
                                        size="5",
                                        weight="bold",
                                        color="var(--gray-10)",
                                    ),
                                    rx.text(
                                        "Intenta ajustar los filtros o registra uno nuevo.",
                                        size="3",
                                        color="var(--gray-9)",
                                        text_align="center",
                                    ),
                                    spacing="4",
                                    align="center",
                                ),
                                height="400px",
                                width="100%",
                                border="2px dashed var(--gray-6)",
                                border_radius="16px",
                                background="var(--gray-2)",
                            ),
                            # Result Views
                            rx.cond(
                                ContratosState.is_grid_view,
                                # Grid View
                                rx.grid(
                                    rx.foreach(
                                        ContratosState.contratos,
                                        lambda contrato: contrato_card.contrato_card(
                                            contrato=contrato,
                                            on_edit=ContratosState.open_edit_modal,
                                            on_detail=ContratosState.open_detail_modal,
                                        ),
                                    ),
                                    columns=rx.breakpoints(initial="1", sm="2", lg="3"),
                                    gap="6",
                                    width="100%",
                                ),
                                # Table View (Standardized Premium Table)
                                rx.card(
                                    rx.table.root(
                                        rx.table.header(
                                            rx.table.row(
                                                rx.table.column_header_cell("Contrato / ID"),
                                                rx.table.column_header_cell("Propiedad"),
                                                rx.table.column_header_cell("Personas"),
                                                rx.table.column_header_cell("Fechas"),
                                                rx.table.column_header_cell("Valores"),
                                                rx.table.column_header_cell("Estado"),
                                                rx.table.column_header_cell("Acciones"),
                                            ),
                                        ),
                                        rx.table.body(
                                            rx.foreach(
                                                ContratosState.contratos,
                                                lambda c: rx.table.row(
                                                    # Contrato / ID
                                                    rx.table.cell(
                                                        rx.vstack(
                                                            rx.badge(
                                                                c["tipo_contrato"],
                                                                color_scheme=rx.cond(
                                                                    c["tipo_contrato"] == "Arrendamiento",
                                                                    "blue",
                                                                    "purple"
                                                                ),
                                                                variant="surface"
                                                            ),
                                                            rx.text(f"ID: {c['id_contrato']}", size="1", color="gray"),
                                                            spacing="1",
                                                            align="start"
                                                        )
                                                    ),
                                                    # Propiedad
                                                    rx.table.cell(
                                                        rx.vstack(
                                                            rx.text(c["propiedad_direccion"], weight="bold", size="2"),
                                                            rx.text(c["propiedad_matricula"], size="1", color="gray"),
                                                            spacing="0",
                                                            align="start"
                                                        )
                                                    ),
                                                    # Personas
                                                    rx.table.cell(
                                                        rx.vstack(
                                                            rx.hstack(
                                                                rx.icon("user", size=14, color="var(--blue-9)"),
                                                                rx.text(c["propietario_nombre"], size="2", weight="medium"),
                                                                spacing="1",
                                                                align="center"
                                                            ),
                                                            rx.hstack(
                                                                rx.icon("user-check", size=14, color="var(--green-9)"),
                                                                rx.text(c["arrendatario_nombre"], size="2"),
                                                                spacing="1",
                                                                align="center"
                                                            ),
                                                            spacing="1",
                                                            align="start"
                                                        )
                                                    ),
                                                    # Fechas
                                                    rx.table.cell(
                                                        rx.vstack(
                                                            rx.text(f"Ini: {c['fecha_inicio']}", size="1"),
                                                            rx.text(f"Fin: {c['fecha_fin']}", size="1", weight="bold"),
                                                            spacing="0",
                                                            align="start"
                                                        )
                                                    ),
                                                    # Valores
                                                    rx.table.cell(
                                                        rx.vstack(
                                                            rx.text(f"Canon: ${c['valor_canon']:,.0f}", size="2", weight="bold"),
                                                            rx.text(f"Admin: ${c['valor_administracion']:,.0f}", size="1", color="gray"),
                                                            spacing="0",
                                                            align="start"
                                                        )
                                                    ),
                                                    # Estado
                                                    rx.table.cell(
                                                        rx.badge(
                                                            c["estado_contrato"],
                                                            color_scheme=rx.match(
                                                                c["estado_contrato"],
                                                                ("Activo", "green"),
                                                                ("Vencido", "red"),
                                                                ("Cerrado", "gray"),
                                                                "gray"
                                                            ),
                                                            variant="solid"
                                                        )
                                                    ),
                                                    # Acciones
                                                    rx.table.cell(
                                                        rx.hstack(
                                                            rx.tooltip(
                                                                rx.icon_button(
                                                                    rx.icon("eye", size=16),
                                                                    size="1",
                                                                    variant="ghost",
                                                                    on_click=lambda: ContratosState.open_detail_modal(c["id_contrato"])
                                                                ),
                                                                content="Ver Detalle"
                                                            ),
                                                            rx.tooltip(
                                                                rx.icon_button(
                                                                    rx.icon("pencil", size=16),
                                                                    size="1",
                                                                    variant="ghost",
                                                                    on_click=lambda: ContratosState.open_edit_modal(c["id_contrato"])
                                                                ),
                                                                content="Editar"
                                                            ),
                                                            spacing="1"
                                                        )
                                                    ),
                                                ),
                                            ),
                                        ),
                                        variant="surface",
                                        width="100%",
                                    ),
                                    width="100%",
                                    style={"padding": "0"}, # Table takes full card space
                                ),
                            ),
                        ),
                        width="100%",
                    ),
                    # --- Premium Pagination ---
                    rx.card(
                        rx.hstack(
                            neuro_button(
                                rx.hstack(rx.icon("chevron-left", size=16), rx.text("Anterior")),
                                on_click=ContratosState.prev_page,
                                disabled=ContratosState.current_page == 1,
                                size="3",
                            ),
                            rx.vstack(
                                rx.text(
                                    f"Página {ContratosState.current_page}",
                                    size="3",
                                    weight="medium",
                                    color=styles.TEXT_PRIMARY,
                                ),
                                rx.text(
                                    f"Mostrando {(ContratosState.current_page - 1) * ContratosState.page_size + 1}-"
                                    f"{rx.cond((ContratosState.current_page * ContratosState.page_size) > ContratosState.total_items, ContratosState.total_items, (ContratosState.current_page * ContratosState.page_size))} "
                                    f"de {ContratosState.total_items}",
                                    size="1",
                                    color=styles.TEXT_SECONDARY,
                                ),
                                spacing="0",
                                align="center",
                            ),
                            neuro_button(
                                rx.hstack(rx.text("Siguiente"), rx.icon("chevron-right", size=16)),
                                on_click=ContratosState.next_page,
                                disabled=(
                                    ContratosState.current_page * ContratosState.page_size
                                )
                                >= ContratosState.total_items,
                                size="3",
                            ),
                            justify="center",
                            width="100%",
                            padding="4",
                            align="center",
                            spacing="4",
                        ),
                        width="100%",
                        style={
                            "background": styles.BG_PANEL,
                            "box_shadow": styles.NEU_SHADOW,
                            "border": "none",
                            "border_radius": "16px",
                            "margin_top": "24px",
                        },
                    ),
                    spacing="6",
                    width="100%",
                    padding_x=["4", "6"],
                    padding_bottom="8",
                ),
                # Modales
                contrato_detail_modal.contrato_detail_modal(),
                # El modal_form es dinámico según el tipo
                rx.cond(
                    ContratosState.tipo_form == "Mandato",
                    contrato_mandato_form.modal_form(),
                    contrato_arrendamiento_form.modal_form(),
                ),
                ipc_increment_modal.ipc_increment_modal(),
                spacing="0",
                width="100%",
            )
        ),
    )


# Ruta protegida
@rx.page(route="/contratos", on_load=[AuthState.require_login, ContratosState.on_load])
def contratos():
    return contratos_page()
