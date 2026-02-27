"""
Página de Contratos - Reflex
Gestión de contratos de mandato y arrendamiento con filtros, CRUD y paginación.
"""

import reflex as rx

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


def contratos_page() -> rx.Component:
    """
    Página principal de Contratos con filtros y CRUD.
    """
    return rx.box(
        # --- Elite Header with Gradient (Personas Style) ---
        rx.box(
            rx.hstack(
                rx.vstack(
                    rx.heading(
                        "Gestión de Contratos",
                        size="8",
                        weight="bold",
                        style={
                            "background": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
                            "background_clip": "text",
                            "-webkit-background-clip": "text",
                            "-webkit-text-fill-color": "transparent",
                        },
                    ),
                    rx.text(
                        "Gestión de contratos de mandato y arrendamiento.",
                        color="var(--gray-10)",
                        size="3",
                    ),
                    rx.hstack(
                        rx.icon("file-text", size=18, color="var(--gray-9)"),
                        rx.text(
                            f"Total: {ContratosState.total_items} contratos",
                            size="2",
                            weight="medium",
                            color="var(--gray-11)",
                        ),
                        spacing="2",
                        align="center",
                    ),
                    spacing="1",
                    align="start",
                ),
                rx.spacer(),
                # Action Buttons (moved from Toolbar to Header for consistency if space allows,
                # but Contratos has multiple create buttons. Sticking to Header info only, keeping actions in toolbar or adapting).
                # Actually, Personas has "New Persona" in header. Contratos has "New Mandato" and "New Arrendamiento".
                # I will keep the header clean and leave actions in toolbar to avoid crowding, or add a Dropdown?
                # For now, just the informational header to match the visual style.
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
        # Toolbar con filtros y acciones
        rx.card(
            rx.hstack(
                # Búsqueda
                rx.input(
                    rx.input.slot(rx.icon("search", size=18)),
                    placeholder="Buscar por propiedad, persona o documento...",
                    value=ContratosState.search_text,
                    on_change=ContratosState.set_search,
                    on_key_down=ContratosState.handle_search_key_down,
                    width="350px",
                    size="3",
                    style={
                        "transition": "all 0.3s ease",
                    },
                    _focus={
                        "box_shadow": "0 0 0 3px rgba(102, 126, 234, 0.2)",
                    },
                ),
                # Filtro Tipo
                rx.select(
                    ContratosState.tipo_options,
                    value=ContratosState.filter_tipo,
                    on_change=ContratosState.set_filter_tipo,
                    placeholder="Tipo",
                    size="3",
                    variant="surface",
                ),
                # Filtro Estado
                rx.select(
                    ContratosState.estado_options,
                    value=ContratosState.filter_estado,
                    on_change=ContratosState.set_filter_estado,
                    placeholder="Estado",
                    size="3",
                    variant="surface",
                ),
                # Filtro Asesor
                rx.select.root(
                    rx.select.trigger(
                        placeholder="Asesor",
                        width="200px",
                        size="3",
                        variant="surface",
                    ),
                    rx.select.content(
                        rx.select.group(
                            rx.select.item("Todos", value="todos"),  # Opción para limpiar filtro
                            rx.foreach(
                                ContratosState.asesores_select_options,
                                lambda opcion: rx.select.item(opcion[0], value=opcion[1]),
                            ),
                        )
                    ),
                    value=ContratosState.filter_asesor_id,
                    on_change=ContratosState.set_filter_asesor,
                ),
                rx.spacer(),
                # Botones de acción
                rx.hstack(
                    rx.tooltip(
                        rx.icon_button(
                            rx.icon(
                                rx.cond(ContratosState.is_grid_view, "table", "layout-grid"),
                                size=18,
                            ),
                            on_click=ContratosState.toggle_view,
                            variant="surface",
                            size="3",
                            color_scheme="gray",
                        ),
                        content=rx.cond(
                            ContratosState.is_grid_view, "Ver como Tabla", "Ver como Tarjetas"
                        ),
                    ),
                    rx.tooltip(
                        rx.button(
                            rx.icon("file-spreadsheet", size=18),
                            "Exportar",
                            on_click=ContratosState.exportar_csv,
                            variant="soft",
                            color_scheme="green",
                            size="3",
                        ),
                        content="Exportar Excel",
                    ),
                    spacing="2",
                ),
                rx.cond(
                    AuthState.check_action("Contratos", "CREAR"),
                    rx.hstack(
                        rx.tooltip(
                            rx.button(
                                rx.icon("plus", size=18),
                                "Mandato",
                                on_click=ContratosState.open_create_mandato_modal,
                                variant="surface",
                                color_scheme="blue",
                                size="3",
                            ),
                            content="Nuevo Contrato de Mandato",
                        ),
                        rx.tooltip(
                            rx.button(
                                rx.icon("plus", size=18),
                                "Arrendamiento",
                                on_click=ContratosState.open_create_arrendamiento_modal,
                                variant="surface",
                                color_scheme="green",
                                size="3",
                            ),
                            content="Nuevo Contrato de Arrendamiento",
                        ),
                        spacing="2",
                    ),
                ),
                rx.tooltip(
                    rx.icon_button(
                        rx.icon("refresh-cw", size=16),
                        on_click=ContratosState.load_contratos,
                        variant="ghost",
                        size="3",
                        _hover={
                            "transform": "rotate(180deg)",
                        },
                        transition="transform 0.3s ease",
                    ),
                    content="Recargar lista",
                ),
                spacing="3",
                align="center",
                width="100%",
                wrap="wrap",
            ),
            width="100%",
            style={
                "background": "var(--color-panel-solid)",
            },
        ),
        # Mensaje de error
        rx.cond(
            ContratosState.error_message != "",
            rx.callout(
                ContratosState.error_message,
                icon="circle-alert",
                color="red",
                role="alert",
                margin_bottom="1rem",
            ),
        ),
        # Loading spinner
        rx.cond(
            ContratosState.is_loading,
            rx.center(
                rx.spinner(size="3"),
                padding="2rem",
            ),
            # Tabla o Grid de contratos
            rx.box(
                rx.cond(
                    ContratosState.contratos.length() > 0,
                    rx.cond(
                        ContratosState.is_grid_view,
                        # VISTA GRID
                        rx.grid(
                            rx.foreach(ContratosState.contratos, contrato_card),
                            columns=rx.breakpoints(initial="1", sm="2", lg="3", xl="4"),
                            spacing="4",
                            width="100%",
                        ),
                        # VISTA TABLA
                        rx.table.root(
                            rx.table.header(
                                rx.table.row(
                                    rx.table.column_header_cell("ID", style={"font-weight": "600"}),
                                    rx.table.column_header_cell(
                                        "Tipo", style={"font-weight": "600"}
                                    ),
                                    rx.table.column_header_cell(
                                        "Tipo Propiedad", style={"font-weight": "600"}
                                    ),
                                    rx.table.column_header_cell(
                                        "Propiedad", style={"font-weight": "600"}
                                    ),
                                    rx.table.column_header_cell(
                                        "Persona", style={"font-weight": "600"}
                                    ),
                                    rx.table.column_header_cell(
                                        "Fecha Inicio", style={"font-weight": "600"}
                                    ),
                                    rx.table.column_header_cell(
                                        "Fecha Fin", style={"font-weight": "600"}
                                    ),
                                    rx.table.column_header_cell(
                                        "Canon/Comisión", style={"font-weight": "600"}
                                    ),
                                    rx.table.column_header_cell(
                                        "Estado", style={"font-weight": "600"}
                                    ),
                                    rx.table.column_header_cell(
                                        "Acciones", style={"font-weight": "600"}
                                    ),
                                ),
                            ),
                            rx.table.body(
                                rx.foreach(
                                    ContratosState.contratos,
                                    lambda contrato: rx.table.row(
                                        rx.table.cell(contrato["id"].to_string()),
                                        rx.table.cell(
                                            rx.badge(
                                                contrato["tipo"],
                                                color_scheme=rx.cond(
                                                    contrato["tipo"] == "Mandato",
                                                    "blue",
                                                    "green",
                                                ),
                                            ),
                                        ),
                                        rx.table.cell(
                                            rx.text(
                                                contrato.get("tipo_propiedad", ""),
                                                size="2",
                                                color="gray",
                                            )
                                        ),
                                        rx.table.cell(
                                            rx.text(
                                                contrato.get("propiedad", "N/A"),
                                                size="2",
                                                weight="medium",
                                            ),
                                        ),
                                        rx.table.cell(
                                            rx.vstack(
                                                rx.text(
                                                    contrato.get(
                                                        "propietario",
                                                        contrato.get("arrendatario", "N/A"),
                                                    ),
                                                    size="2",
                                                    weight="medium",
                                                ),
                                                rx.text(
                                                    contrato.get(
                                                        "documento_propietario",
                                                        contrato.get("documento_arrendatario", ""),
                                                    ),
                                                    size="1",
                                                    color="gray",
                                                ),
                                                spacing="0",
                                                align="start",
                                            ),
                                        ),
                                        rx.table.cell(contrato["fecha_inicio"]),
                                        rx.table.cell(contrato["fecha_fin"]),
                                        rx.table.cell(
                                            rx.text(
                                                "$" + contrato["canon"].to_string(),
                                                weight="bold",
                                            ),
                                        ),
                                        rx.table.cell(
                                            rx.badge(
                                                contrato["estado"],
                                                color_scheme=rx.cond(
                                                    contrato["estado"] == "Activo",
                                                    "green",
                                                    "red",
                                                ),
                                            ),
                                        ),
                                        rx.table.cell(
                                            rx.hstack(
                                                # Ver Detalle
                                                rx.tooltip(
                                                    rx.icon_button(
                                                        rx.icon("eye", size=16),
                                                        on_click=lambda: ContratosState.open_detail_modal(
                                                            contrato["id"], contrato["tipo"]
                                                        ),
                                                        variant="ghost",
                                                        size="2",
                                                        color_scheme="blue",
                                                    ),
                                                    content="Ver detalle",
                                                ),
                                                # Botones PDF Élite (Solo para Arrendamiento)
                                                rx.cond(
                                                    contrato["tipo"] == "Arrendamiento",
                                                    rx.hstack(
                                                        # Botón 1: Contrato Oficial
                                                        rx.tooltip(
                                                            rx.icon_button(
                                                                rx.icon("file-check", size=16),
                                                                on_click=lambda: PDFState.generar_contrato_arrendamiento_elite(
                                                                    contrato["id"], False
                                                                ),
                                                                variant="ghost",
                                                                size="2",
                                                                color_scheme="purple",
                                                                loading=PDFState.generating,
                                                            ),
                                                            content="Contrato Oficial",
                                                        ),
                                                        # Botón 2: Borrador
                                                        rx.tooltip(
                                                            rx.icon_button(
                                                                rx.icon("file-pen-line", size=16),
                                                                on_click=lambda: PDFState.generar_contrato_arrendamiento_elite(
                                                                    contrato["id"], True
                                                                ),
                                                                variant="ghost",
                                                                size="2",
                                                                color_scheme="orange",
                                                                loading=PDFState.generating,
                                                            ),
                                                            content="Borrador",
                                                        ),
                                                        # Botón 3: Paz y Salvo
                                                        rx.tooltip(
                                                            rx.icon_button(
                                                                rx.icon("award", size=16),
                                                                on_click=lambda: PDFState.generar_certificado_paz_y_salvo(
                                                                    contrato["id"],
                                                                    contrato.get(
                                                                        "arrendatario",
                                                                        "Arrendatario",
                                                                    ),
                                                                ),
                                                                variant="ghost",
                                                                size="2",
                                                                color_scheme="green",
                                                                loading=PDFState.generating,
                                                            ),
                                                            content="Paz y Salvo",
                                                        ),
                                                        spacing="1",
                                                    ),
                                                ),
                                                # Botones PDF Élite (Solo para Mandato)
                                                rx.cond(
                                                    contrato["tipo"] == "Mandato",
                                                    rx.hstack(
                                                        # Botón 1: Contrato Oficial
                                                        rx.tooltip(
                                                            rx.icon_button(
                                                                rx.icon("file-check", size=16),
                                                                on_click=lambda: PDFState.generar_contrato_mandato_elite(
                                                                    contrato["id"], False
                                                                ),
                                                                variant="ghost",
                                                                size="2",
                                                                color_scheme="purple",
                                                                loading=PDFState.generating,
                                                            ),
                                                            content="Contrato Oficial",
                                                        ),
                                                        # Botón 2: Borrador
                                                        rx.tooltip(
                                                            rx.icon_button(
                                                                rx.icon("file-pen-line", size=16),
                                                                on_click=lambda: PDFState.generar_contrato_mandato_elite(
                                                                    contrato["id"], True
                                                                ),
                                                                variant="ghost",
                                                                size="2",
                                                                color_scheme="orange",
                                                                loading=PDFState.generating,
                                                            ),
                                                            content="Borrador",
                                                        ),
                                                        # Botón 3: Paz y Salvo
                                                        rx.tooltip(
                                                            rx.icon_button(
                                                                rx.icon("award", size=16),
                                                                on_click=lambda: PDFState.generar_certificado_paz_y_salvo(
                                                                    contrato["id"],
                                                                    contrato.get(
                                                                        "propietario", "Propietario"
                                                                    ),
                                                                ),
                                                                variant="ghost",
                                                                size="2",
                                                                color_scheme="green",
                                                                loading=PDFState.generating,
                                                            ),
                                                            content="Paz y Salvo",
                                                        ),
                                                        spacing="1",
                                                    ),
                                                ),
                                                # Botones Comunes (Editar)
                                                rx.cond(
                                                    AuthState.check_action("Contratos", "EDITAR"),
                                                    rx.tooltip(
                                                        rx.icon_button(
                                                            rx.icon("square-pen", size=16),
                                                            on_click=lambda: ContratosState.open_edit_modal(
                                                                contrato["id"], contrato["tipo"]
                                                            ),
                                                            variant="ghost",
                                                            size="2",
                                                        ),
                                                        content="Editar contrato",
                                                    ),
                                                ),
                                                # Acciones Específicas
                                                rx.cond(
                                                    contrato["tipo"] == "Arrendamiento",
                                                    # SI ES ARRENDAMIENTO: Botón Incremento y Renovación
                                                    rx.hstack(
                                                        rx.cond(
                                                            AuthState.check_action(
                                                                "Contratos", "IPC"
                                                            ),
                                                            rx.tooltip(
                                                                rx.icon_button(
                                                                    rx.icon("trending-up", size=16),
                                                                    on_click=lambda: ContratosState.open_ipc_modal(
                                                                        contrato["id"]
                                                                    ),
                                                                    variant="ghost",
                                                                    size="2",
                                                                    color_scheme="blue",
                                                                    disabled=contrato["estado"]
                                                                    != "Activo",
                                                                ),
                                                                content="Aplicar incremento IPC",
                                                            ),
                                                        ),
                                                        rx.cond(
                                                            AuthState.check_action(
                                                                "Contratos", "RENOVAR"
                                                            ),
                                                            rx.tooltip(
                                                                rx.icon_button(
                                                                    rx.icon("refresh-cw", size=16),
                                                                    on_click=lambda: ContratosState.confirm_renewal(
                                                                        contrato["id"],
                                                                        contrato["tipo"],
                                                                    ),
                                                                    variant="ghost",
                                                                    size="2",
                                                                    color_scheme="cyan",
                                                                    disabled=contrato["estado"]
                                                                    != "Activo",
                                                                ),
                                                                content="Renovar contrato",
                                                            ),
                                                        ),
                                                        spacing="1",
                                                    ),
                                                    # SI ES MANDATO: Botón Ver Propiedad y Renovación
                                                    rx.hstack(
                                                        rx.tooltip(
                                                            rx.icon_button(
                                                                rx.icon("building", size=16),
                                                                # Redirigir a Propiedades (Idealmente filtrando, por ahora lista general)
                                                                on_click=rx.redirect(
                                                                    "/propiedades"
                                                                ),
                                                                variant="ghost",
                                                                size="2",
                                                                color_scheme="orange",
                                                            ),
                                                            content="Ir a Propiedades",
                                                        ),
                                                        rx.cond(
                                                            AuthState.check_action(
                                                                "Contratos", "RENOVAR"
                                                            ),
                                                            rx.tooltip(
                                                                rx.icon_button(
                                                                    rx.icon("refresh-cw", size=16),
                                                                    on_click=lambda: ContratosState.confirm_renewal(
                                                                        contrato["id"],
                                                                        contrato["tipo"],
                                                                    ),
                                                                    variant="ghost",
                                                                    size="2",
                                                                    color_scheme="cyan",
                                                                    disabled=contrato["estado"]
                                                                    != "Activo",
                                                                ),
                                                                content="Renovar contrato",
                                                            ),
                                                        ),
                                                        spacing="1",
                                                    ),
                                                ),
                                                # Botones Comunes (Estado)
                                                rx.cond(
                                                    AuthState.check_action("Contratos", "TERMINAR"),
                                                    rx.tooltip(
                                                        rx.icon_button(
                                                            rx.icon(
                                                                rx.cond(
                                                                    contrato["estado"] == "Activo",
                                                                    "ban",
                                                                    "archive",
                                                                ),
                                                                size=16,
                                                            ),
                                                            on_click=lambda: ContratosState.toggle_estado(
                                                                contrato["id"],
                                                                contrato["tipo"],
                                                                contrato["estado"],
                                                            ),
                                                            variant="ghost",
                                                            size="2",
                                                            color_scheme=rx.cond(
                                                                contrato["estado"] == "Activo",
                                                                "red",
                                                                "gray",
                                                            ),
                                                            disabled=contrato["estado"] != "Activo",
                                                        ),
                                                        content=rx.cond(
                                                            contrato["estado"] == "Activo",
                                                            "Terminar contrato",
                                                            "Contrato finalizado",
                                                        ),
                                                    ),
                                                ),
                                                spacing="1",
                                            ),
                                        ),
                                    ),
                                ),
                            ),
                            variant="surface",
                            size="3",
                        ),
                    ),
                    # Mensaje vacío
                    rx.center(
                        rx.vstack(
                            rx.icon("inbox", size=48, color="gray"),
                            rx.text(
                                "No hay contratos para mostrar",
                                size="4",
                                color="gray",
                            ),
                            rx.text(
                                "Crea un nuevo contrato usando los botones superiores",
                                size="2",
                                color="gray",
                            ),
                            spacing="2",
                            align="center",
                        ),
                        padding="4rem",
                    ),
                ),
            ),
        ),
        # Paginación
        # Premium Pagination
        rx.card(
            rx.hstack(
                rx.button(
                    rx.icon("chevron-left", size=16),
                    "Anterior",
                    on_click=ContratosState.prev_page,
                    disabled=ContratosState.current_page == 1,
                    variant="soft",
                    size="3",
                    _hover={
                        "transform": "translateX(-2px)",
                    },
                    transition="transform 0.2s ease",
                ),
                rx.vstack(
                    rx.text(
                        f"Página {ContratosState.current_page}",
                        size="3",
                        weight="medium",
                    ),
                    rx.text(
                        f"Mostrando {(ContratosState.current_page - 1) * ContratosState.page_size + 1}-"
                        f"{rx.cond(ContratosState.current_page * ContratosState.page_size > ContratosState.total_items, ContratosState.total_items, ContratosState.current_page * ContratosState.page_size)} "
                        f"de {ContratosState.total_items}",
                        size="1",
                        color="var(--gray-10)",
                    ),
                    spacing="0",
                    align="center",
                ),
                rx.button(
                    "Siguiente",
                    rx.icon("chevron-right", size=16),
                    on_click=ContratosState.next_page,
                    disabled=ContratosState.current_page * ContratosState.page_size
                    >= ContratosState.total_items,
                    variant="soft",
                    size="3",
                    _hover={
                        "transform": "translateX(2px)",
                    },
                    transition="transform 0.2s ease",
                ),
                justify="center",
                width="100%",
                padding="4",
                align="center",
                spacing="4",
            ),
            width="100%",
            style={
                "background": "var(--color-panel-solid)",
            },
        ),
        # Modales de creación/edición
        contrato_mandato_form(),
        contrato_arrendamiento_form(),
        # Diálogo de Confirmación de Renovación (Enriquecido con proyección)
        rx.dialog.root(
            rx.dialog.content(
                # Encabezado
                rx.hstack(
                    rx.icon("refresh-cw", size=20, color="var(--cyan-9)"),
                    rx.dialog.title(
                        rx.text(
                            "Renovar Contrato — ",
                            rx.cond(
                                ContratosState.selected_contract_type_renew == "Arrendamiento",
                                "Arrendamiento",
                                "Mandato",
                            ),
                            weight="bold",
                        ),
                    ),
                    spacing="2",
                    align="center",
                ),
                rx.separator(size="4", my="3"),
                # Contenido: spinner mientras carga o datos de proyección
                rx.cond(
                    ContratosState.renewal_loading_proyeccion,
                    rx.center(
                        rx.vstack(
                            rx.spinner(size="3"),
                            rx.text("Calculando proyección...", size="2", color="var(--gray-10)"),
                            spacing="3",
                            align="center",
                        ),
                        padding="2rem",
                    ),
                    # --- Proyección cargada ---
                    rx.vstack(
                        # ── Fechas ──────────────────────────────────
                        rx.box(
                            rx.vstack(
                                rx.hstack(
                                    rx.icon("calendar", size=16, color="var(--gray-9)"),
                                    rx.text("Fechas del contrato", weight="bold", size="2"),
                                    spacing="2", align="center",
                                ),
                                rx.grid(
                                    rx.text("Fecha fin actual:", size="2", color="var(--gray-10)"),
                                    rx.badge(
                                        ContratosState.renewal_proyeccion.get("fecha_fin_actual", "—"),
                                        color_scheme="gray",
                                        size="2",
                                    ),
                                    rx.text("Nueva fecha fin:", size="2", weight="medium"),
                                    rx.input(
                                        type="date",
                                        value=ContratosState.renewal_nueva_fecha_fin,
                                        on_change=ContratosState.set_renewal_fecha_fin,
                                        size="2",
                                        variant="surface",
                                        style={"width": "180px"},
                                    ),
                                    columns="2",
                                    gap="2",
                                    align="center",
                                    width="100%",
                                ),
                                spacing="2",
                            ),
                            padding="3",
                            border_radius="8px",
                            style={"background": "var(--gray-2)"},
                            width="100%",
                        ),
                        # ── Bloque IPC (solo arrendamiento) ─────────
                        rx.cond(
                            ContratosState.renewal_proyeccion.get("aplica_ipc", False),
                            rx.box(
                                rx.vstack(
                                    rx.hstack(
                                        rx.icon("trending-up", size=16, color="var(--green-9)"),
                                        rx.text("Incremento IPC", weight="bold", size="2"),
                                        rx.badge(
                                            ContratosState.renewal_proyeccion.get("porcentaje_ipc", 0).to_string() + "%",
                                            color_scheme="green",
                                            size="1",
                                        ),
                                        spacing="2", align="center",
                                    ),
                                    rx.grid(
                                        rx.text("Canon actual:", size="2", color="var(--gray-10)"),
                                        rx.text(
                                            "$ " + ContratosState.renewal_proyeccion.get("canon_actual", 0).to_string(),
                                            size="2",
                                            weight="medium",
                                        ),
                                        rx.text("Nuevo canon:", size="2", color="var(--gray-10)"),
                                        rx.text(
                                            "$ " + ContratosState.renewal_proyeccion.get("canon_nuevo", 0).to_string(),
                                            size="2",
                                            weight="bold",
                                            color="var(--green-11)",
                                        ),
                                        columns="2",
                                        gap="2",
                                        align="center",
                                        width="100%",
                                    ),
                                    spacing="2",
                                ),
                                padding="3",
                                border_radius="8px",
                                style={"background": "var(--green-2)", "border": "1px solid var(--green-5)"},
                                width="100%",
                            ),
                            # Mandato: sin IPC, solo nota informativa
                            rx.callout(
                                "El mandato se renueva con el mismo canon — no aplica incremento de IPC.",
                                icon="info",
                                color="blue",
                                size="1",
                            ),
                        ),
                        # ── Nota edición fecha ───────────────────────
                        rx.text(
                            "💡 Puedes ajustar la nueva fecha fin antes de confirmar.",
                            size="1",
                            color="var(--gray-9)",
                        ),
                        spacing="3",
                        width="100%",
                    ),
                ),
                # ── Botones ──────────────────────────────────────────
                rx.flex(
                    rx.button(
                        "Cancelar",
                        variant="soft",
                        color_scheme="gray",
                        on_click=ContratosState.cancel_renewal,
                        disabled=ContratosState.renewal_loading_proyeccion,
                    ),
                    rx.button(
                        rx.icon("check", size=16),
                        "Confirmar Renovación",
                        color_scheme="cyan",
                        on_click=ContratosState.execute_renewal,
                        disabled=ContratosState.renewal_loading_proyeccion,
                        loading=ContratosState.renewal_loading_proyeccion,
                    ),
                    spacing="3",
                    margin_top="16px",
                    justify="end",
                ),
                style={"max_width": "480px"},
            ),
            open=ContratosState.show_renewal_confirm,
        ),
        # Modal de Detalle
        contrato_detail_modal(),
        # Modal de Incremento IPC
        ipc_increment_modal(),
        width="100%",
        padding="2rem",
    )


# Ruta protegida
@rx.page(route="/contratos", on_load=[AuthState.require_login, ContratosState.on_load])
def contratos() -> rx.Component:
    return rx.fragment(rx.toast.provider(), dashboard_layout(contratos_page()))
