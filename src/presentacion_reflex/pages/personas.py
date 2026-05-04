import reflex as rx

from src.presentacion_reflex.components.table_utils import header_cell_sortable
from src.presentacion_reflex.components.layout.dashboard_layout import dashboard_layout
from src.presentacion_reflex.components.personas.modal_form import modal_persona
from src.presentacion_reflex.components.personas.modal_detalles import modal_detalles
from src.presentacion_reflex.components.personas.person_card import person_card
from src.presentacion_reflex.state.auth_state import AuthState
from src.presentacion_reflex.state.personas_state import PersonasState
from src.presentacion_reflex.components.neuro_elements import neuro_input, neuro_select_root, neuro_button, neuro_spinner, neuro_badge
from src.presentacion_reflex import styles


def persona_row(persona: dict) -> rx.Component:
    """Fila individual de la tabla de personas."""

    # Generar badges de roles

    # Nota: rx.foreach interno para roles simple
    return rx.table.row(
        rx.table.cell(
            rx.hstack(
                rx.avatar(fallback=persona["nombre"][:2], size="2", radius="full"),
                rx.text(persona["nombre"], weight="bold"),
                align="center",
                spacing="2",
            )
        ),
        rx.table.cell(persona["documento"]),
        rx.table.cell(
            rx.vstack(
                rx.text(persona["correo"], size="1"),
                rx.text(persona["contacto"], size="1", color="gray"),
                spacing="0",
                align="start",
            )
        ),
        rx.table.cell(persona["fecha_creacion"]),
        rx.table.cell(
            rx.box(
                rx.foreach(
                    persona["roles"],
                    lambda r: rx.box(
                        r,
                        color=rx.match(
                            r,
                            ("Propietario", "var(--blue-9)"),
                            ("Arrendatario", "var(--green-9)"),
                            ("Asesor", "var(--purple-9)"),
                            ("Codeudor", "var(--orange-9)"),
                            ("Proveedor", "var(--cyan-9)"),
                            "var(--gray-9)",
                        ),
                        background=styles.BG_PANEL,
                        border_radius="20px",
                        padding="2px 10px",
                        box_shadow=styles.NEU_INSET,
                        margin_right="1",
                        font_size="0.75rem",
                        font_weight="bold",
                        display="inline-block",
                    ),
                )
                                    )
                                ),
        rx.table.cell(
            rx.box(
                persona["estado"],
                color=rx.cond(persona["estado"] == "Activo", "var(--green-9)", "var(--red-9)"),
                background=styles.BG_PANEL,
                border_radius="20px",
                padding="2px 10px",
                box_shadow=styles.NEU_INSET_LIGHT,
                font_size="0.75rem",
                font_weight="bold",
                display="inline-block",
            )
        ),
        rx.table.cell(
            rx.hstack(
                rx.cond(
                    AuthState.check_action("Personas", "EDITAR"),
                    rx.tooltip(
                        rx.icon_button(
                            rx.icon("pencil", size=16),
                            variant="ghost",
                            size="2",
                            on_click=lambda: PersonasState.open_edit_modal(persona),
                        ),
                        content="Editar persona",
                    ),
                ),
                rx.cond(
                    AuthState.check_action("Personas", "ELIMINAR"),
                    rx.tooltip(
                        rx.icon_button(
                            rx.icon("trash_2", size=16),
                            variant="ghost",
                            color_scheme="red",
                            size="2",
                            # Pendiente: Implementar delete con confirmación
                        ),
                        content="Eliminar persona",
                    ),
                ),
                spacing="2",
            )
        ),
    )


@rx.page(route="/personas", on_load=[AuthState.require_login, PersonasState.load_personas])
def personas_page() -> rx.Component:
    pass  # print("\n🌐 === PERSONAS PAGE RENDERING ===") [OpSec Removed]
    pass  # print("✅ Toast provider will be included in this page") [OpSec Removed]
    return rx.box(
        dashboard_layout(
            rx.vstack(
                # Modal Component
                modal_persona(),
                modal_detalles(),
                # --- Elite Header with Neumorphism ---
                rx.box(
                    rx.flex(
                        rx.vstack(
                            rx.heading(
                                "Gestión de Personas",
                                size="8",
                                weight="bold",
                                color=styles.TEXT_PRIMARY,
                            ),
                            rx.text(
                                "Administre propietarios, arrendatarios y asesores con facilidad.",
                                color=styles.TEXT_SECONDARY,
                                size="3",
                            ),
                            rx.hstack(
                                rx.icon("users", size=18, color=styles.TEXT_TERTIARY),
                                rx.text(
                                    "Total: ",
                                    PersonasState.total_items,
                                    " personas",
                                    size="2",
                                    weight="medium",
                                    color=styles.TEXT_SECONDARY,
                                ),
                                spacing="2",
                                align="center",
                            ),
                            # KPI Indicators
                            rx.hstack(
                                rx.badge(rx.icon("home", size=14), "Propietarios ", PersonasState.kpi_propietarios, color_scheme="blue", radius="full", size="2", variant="surface"),
                                rx.badge(rx.icon("key", size=14), "Arrendatarios ", PersonasState.kpi_arrendatarios, color_scheme="green", radius="full", size="2", variant="surface"),
                                rx.badge(rx.icon("briefcase", size=14), "Asesores ", PersonasState.kpi_asesores, color_scheme="purple", radius="full", size="2", variant="surface"),
                                rx.badge(rx.icon("handshake", size=14), "Codeudores ", PersonasState.kpi_codeudores, color_scheme="orange", radius="full", size="2", variant="surface"),
                                rx.badge(rx.icon("truck", size=14), "Proveedores ", PersonasState.kpi_proveedores, color_scheme="cyan", radius="full", size="2", variant="surface"),
                                spacing="3",
                                wrap="wrap",
                                margin_top="2"
                            ),
                            spacing="1",
                            align="start",
                        ),
                        rx.cond(
                            AuthState.check_action("Personas", "CREAR"),
                            rx.tooltip(
                                neuro_button(
                                    rx.icon("plus", size=18),
                                    "Nueva Persona",
                                    size="3",
                                    on_click=PersonasState.open_create_modal,
                                    width=["100%", "100%", "auto"],
                                    style={
                                        "color": styles.ACCENT_COLOR,
                                        "font_weight": "bold",
                                    },
                                ),
                                content="Crear nueva persona",
                            ),
                        ),
                        flex_direction=rx.breakpoints(initial="column", md="row"),
                        align=rx.breakpoints(initial="start", md="center"),
                        justify="between",
                        spacing="4",
                        width="100%",
                        padding="5",
                    ),
                    width="100%",
                    style=styles.NEU_PANEL_STYLE,
                ),
                # --- Elite Toolbar ---
                rx.card(
                    rx.flex(
                        # Search bar with enhanced styling
                        neuro_input(
                            rx.input.slot(rx.icon("search", size=18)),
                            placeholder="Buscar por nombre o documento...",
                            value=PersonasState.search_query,
                            on_change=PersonasState.set_search,
                            on_key_down=PersonasState.handle_search_key_down,
                            size="3",
                            width=["100%", "100%", "320px"],
                        ),
                        # Role filter with icon
                        neuro_select_root(
                            [
                                rx.select.item("Todos", value="Todos"),
                                rx.select.item("Propietario", value="Propietario"),
                                rx.select.item("Arrendatario", value="Arrendatario"),
                                rx.select.item("Codeudor", value="Codeudor"),
                                rx.select.item("Asesor", value="Asesor"),
                                rx.select.item("Proveedor", value="Proveedor"),
                            ],
                            value=PersonasState.filtro_rol,
                            on_change=PersonasState.set_filtro_rol,
                            placeholder="Filtrar por Rol",
                            width=["100%", "100%", "200px"],
                        ),
                        # Date filters
                        neuro_input(
                            type="date",
                            placeholder="Desde",
                            on_change=PersonasState.set_fecha_inicio,
                            size="3",
                            width=["100%", "100%", "auto"],
                        ),
                        neuro_input(
                            type="date",
                            placeholder="Hasta",
                            on_change=PersonasState.set_fecha_fin,
                            size="3",
                            width=["100%", "100%", "auto"],
                        ),
                        # View toggle button
                        rx.hstack(
                            rx.tooltip(
                                rx.icon_button(
                                    rx.cond(
                                        PersonasState.view_mode == "table",
                                        rx.icon("layout_grid", size=18),
                                        rx.icon("table", size=18),
                                    ),
                                    on_click=PersonasState.toggle_view_mode,
                                    variant="ghost",
                                    style=styles.NEU_BUTTON_STYLE,
                                    size="3",
                                    color_scheme="gray",
                                ),
                                content=rx.cond(
                                    PersonasState.view_mode == "table",
                                    "Cambiar a vista de cards",
                                    "Cambiar a vista de tabla",
                                ),
                            ),
                            # Export button
                            rx.tooltip(
                                rx.icon_button(
                                    rx.icon("file_spreadsheet", size=18),
                                    color_scheme="green",
                                    variant="ghost",
                                    style=styles.NEU_BUTTON_STYLE,
                                    on_click=PersonasState.exportar_csv,
                                    size="3",
                                    _hover={
                                        "transform": "scale(1.05)",
                                    },
                                    transition="all 0.2s ease",
                                ),
                                content="Exportar a Excel",
                            ),
                            # Refresh button
                            rx.tooltip(
                                rx.icon_button(
                                    rx.icon("refresh_cw", size=18),
                                    variant="ghost",
                                    style=styles.NEU_BUTTON_STYLE,
                                    size="3",
                                    on_click=PersonasState.load_personas,
                                    _hover={
                                        "transform": "rotate(180deg)",
                                    },
                                    transition="transform 0.3s ease",
                                ),
                                content="Recargar",
                            ),
                            width=["100%", "100%", "auto"],
                            justify=rx.breakpoints(initial="between", md="start"),
                            spacing="3",
                        ),
                        padding="4",
                        width="100%",
                        align="center",
                        direction=rx.breakpoints(initial="column", md="row"),
                        wrap="wrap",
                        spacing="3",
                    ),
                    width="100%",
                    variant="ghost",
                    style={
                        "background": styles.BG_PANEL,
                        "box_shadow": styles.NEU_SHADOW,
                        "border": "none",
                        "border_radius": "16px",
                    },
                ),
                # --- Content Area: Table or Cards View ---
                rx.cond(
                    PersonasState.is_loading,
                    rx.center(
                        rx.vstack(
                            neuro_spinner(size="3"),
                            rx.text("Cargando personas...", size="2", color="var(--gray-10)"),
                            spacing="2",
                        ),
                        padding="8",
                    ),
                    rx.cond(
                        PersonasState.view_mode == "table",
                        # TABLE VIEW - Improved with Neumorphism and Transparency
                        rx.card(
                            rx.box(
                                rx.table.root(
                                    rx.table.header(
                                        rx.table.row(
                                            header_cell_sortable("Nombre", "nombre", PersonasState.sort_by, PersonasState.sort_order, PersonasState.toggle_sort),
                                            header_cell_sortable("Documento", "documento", PersonasState.sort_by, PersonasState.sort_order, PersonasState.toggle_sort),
                                            header_cell_sortable("Contacto", "email", PersonasState.sort_by, PersonasState.sort_order, PersonasState.toggle_sort),
                                            header_cell_sortable("Fecha Creación", "creado", PersonasState.sort_by, PersonasState.sort_order, PersonasState.toggle_sort),
                                            rx.table.column_header_cell(
                                                "Roles", style={"font-weight": "700", "color": styles.TEXT_PRIMARY, "background": "transparent"}
                                            ),
                                            header_cell_sortable("Estado", "estado", PersonasState.sort_by, PersonasState.sort_order, PersonasState.toggle_sort),
                                            rx.table.column_header_cell(
                                                "Acciones", style={"font-weight": "700", "color": styles.TEXT_PRIMARY, "background": "transparent"}
                                            ),
                                            style={"background": "transparent"}
                                        ),
                                    ),
                                    rx.table.body(
                                        rx.foreach(
                                            PersonasState.personas,
                                            lambda p: rx.table.row(
                                                rx.table.cell(
                                                    rx.hstack(
                                                        rx.avatar(
                                                            fallback=p["nombre"][:2],
                                                            size="3",
                                                            radius="full",
                                                            color_scheme=rx.cond(
                                                                p["roles"].length() > 0,
                                                                rx.match(
                                                                    p["roles"][0],
                                                                    ("Propietario", "blue"),
                                                                    ("Arrendatario", "green"),
                                                                    ("Asesor", "purple"),
                                                                    ("Codeudor", "orange"),
                                                                    ("Proveedor", "cyan"),
                                                                    "gray",
                                                                ),
                                                                "gray",
                                                            ),
                                                        ),
                                                        rx.text(
                                                            p["nombre"], weight="bold", size="2", color=styles.TEXT_PRIMARY
                                                        ),
                                                        align="center",
                                                        spacing="3",
                                                    )
                                                ),
                                                rx.table.cell(
                                                    rx.text(
                                                        p["documento"],
                                                        size="2",
                                                        color=styles.TEXT_SECONDARY,
                                                        weight="medium",
                                                    )
                                                ),
                                                rx.table.cell(
                                                    rx.vstack(
                                                        rx.hstack(
                                                            rx.icon(
                                                                "mail",
                                                                size=12,
                                                                color=styles.TEXT_TERTIARY,
                                                            ),
                                                            rx.text(p["correo"], size="1", color=styles.TEXT_SECONDARY),
                                                            spacing="1",
                                                        ),
                                                        rx.hstack(
                                                            rx.icon(
                                                                "phone",
                                                                size=12,
                                                                color=styles.TEXT_TERTIARY,
                                                            ),
                                                            rx.text(
                                                                p["contacto"],
                                                                size="1",
                                                                color=styles.TEXT_TERTIARY,
                                                            ),
                                                            spacing="1",
                                                        ),
                                                        spacing="1",
                                                        align="start",
                                                    )
                                                ),
                                                rx.table.cell(
                                                    rx.text(
                                                        p["fecha_creacion"],
                                                        size="2",
                                                        color=styles.TEXT_TERTIARY,
                                                    )
                                                ),
                                                rx.table.cell(
                                                    rx.box(
                                                        rx.foreach(
                                                            p["roles"],
                                                            lambda r: neuro_badge(
                                                                r,
                                                                color_scheme=rx.match(
                                                                    r,
                                                                    ("Propietario", "blue"),
                                                                    ("Arrendatario", "green"),
                                                                    ("Asesor", "violet"),
                                                                    ("Codeudor", "orange"),
                                                                    ("Proveedor", "cyan"),
                                                                    "gray",
                                                                ),
                                                                style={"margin_right": "4px", "margin_bottom": "4px"},
                                                            ),
                                                        )
                                                    )
                                                ),
                                                rx.table.cell(
                                                    neuro_badge(
                                                        p["estado"],
                                                        color_scheme=rx.cond(
                                                            p["estado"] == "Activo", "green", "red"
                                                        ),
                                                    )
                                                ),
                                                rx.table.cell(
                                                    rx.hstack(
                                                        rx.tooltip(
                                                            rx.icon_button(
                                                                rx.icon("eye", size=16),
                                                                variant="ghost",
                                                                size="2",
                                                                on_click=lambda: PersonasState.open_details_modal(p),
                                                                _hover={
                                                                    "background": styles.ACCENT_BG_SOFT,
                                                                    "color": styles.ACCENT_COLOR,
                                                                },
                                                            ),
                                                            content="Ver detalles completos",
                                                        ),
                                                        rx.cond(
                                                            AuthState.check_action(
                                                                "Personas", "EDITAR"
                                                            ),
                                                            rx.tooltip(
                                                                rx.icon_button(
                                                                    rx.icon("pencil", size=16),
                                                                    variant="ghost",
                                                                    size="2",
                                                                    on_click=lambda: PersonasState.open_edit_modal(
                                                                        p
                                                                    ),
                                                                    _hover={
                                                                        "background": styles.ACCENT_BG_SOFT,
                                                                        "color": styles.ACCENT_COLOR,
                                                                    },
                                                                ),
                                                                content="Editar persona",
                                                            ),
                                                        ),
                                                        rx.cond(
                                                            AuthState.check_action(
                                                                "Personas", "ELIMINAR"
                                                            ),
                                                            rx.tooltip(
                                                                rx.icon_button(
                                                                    rx.icon("trash_2", size=16),
                                                                    variant="ghost",
                                                                    color_scheme="red",
                                                                    size="2",
                                                                    _hover={
                                                                        "background": "var(--red-3)",
                                                                    },
                                                                ),
                                                                content="Eliminar persona",
                                                            ),
                                                        ),
                                                        spacing="3",
                                                    )
                                                ),
                                                _hover={
                                                    "background": styles.BG_HOVER,
                                                },
                                                style={
                                                    "transition": "background 0.2s ease",
                                                    "background": "transparent",
                                                },
                                            ),
                                        ),
                                    ),
                                    width="100%",
                                    variant="ghost",
                                    style={"background": "transparent"},
                                ),
                                width="100%",
                                overflow_x="auto",
                                background="transparent",
                            ),
                            width="100%",
                            variant="ghost",
                            style={
                                **styles.NEU_PANEL_STYLE,
                                "box_shadow": styles.NEU_MODAL_SHADOW,
                                "background": styles.BG_PANEL,
                            },
                        ),
                        # Nota: neuro_table_container gestiona el overflow-x para móviles
                        # CARDS VIEW - New
                        rx.box(
                            rx.cond(
                                PersonasState.total_items > 0,
                                rx.grid(
                                    rx.foreach(PersonasState.personas, person_card),
                                    columns=rx.breakpoints(initial="1", sm="1", md="2", lg="3"),
                                    gap="6",
                                    width="100%",
                                    padding="4",
                                ),
                                # Empty state for cards
                                rx.center(
                                    rx.vstack(
                                        rx.icon("users", size=48, color=styles.TEXT_TERTIARY),
                                        rx.heading(
                                            "No hay personas", size="5", color=styles.TEXT_PRIMARY
                                        ),
                                        rx.text(
                                            "Crea tu primera persona haciendo clic en el botón superior",
                                            color=styles.TEXT_SECONDARY,
                                        ),
                                        spacing="2",
                                    ),
                                    padding="8",
                                ),
                            ),
                            width="100%",
                        ),
                    ),
                ),
                # --- Premium Pagination ---
                # --- Premium Pagination (neuro_button) ---
                rx.box(
                    rx.flex(
                        neuro_button(
                            rx.icon("chevron_left", size=16),
                            "Anterior",
                            on_click=PersonasState.prev_page,
                            disabled=PersonasState.page == 1,
                            size="3",
                        ),
                        rx.vstack(
                            rx.text(
                                "Página ",
                                PersonasState.page,
                                " de ",
                                PersonasState.total_pages,
                                size="3",
                                weight="medium",
                                color=styles.TEXT_PRIMARY,
                            ),
                            rx.text(
                                "Mostrando ",
                                (PersonasState.page - 1) * PersonasState.page_size + 1,
                                "-",
                                rx.cond(
                                    PersonasState.page * PersonasState.page_size
                                    > PersonasState.total_items,
                                    PersonasState.total_items,
                                    PersonasState.page * PersonasState.page_size,
                                ),
                                " de ",
                                PersonasState.total_items,
                                size="1",
                                color=styles.TEXT_TERTIARY,
                            ),
                            spacing="0",
                            align="center",
                        ),
                        neuro_button(
                            "Siguiente",
                            rx.icon("chevron_right", size=16),
                            on_click=PersonasState.next_page,
                            disabled=PersonasState.page >= PersonasState.total_pages,
                            size="3",
                        ),
                        justify="center",
                        width="100%",
                        padding="4",
                        align="center",
                        spacing="4",
                        wrap="wrap",
                    ),
                    width="100%",
                    style=styles.NEU_PANEL_STYLE,
                ),
                padding="6",
                width="100%",
                spacing="4",
            )
        ),
    )
