import reflex as rx

from src.presentacion_reflex.components.layout.dashboard_layout import dashboard_layout
from src.presentacion_reflex.components.personas.modal_form import modal_persona
from src.presentacion_reflex.components.personas.person_card import person_card
from src.presentacion_reflex.state.auth_state import AuthState
from src.presentacion_reflex.state.personas_state import PersonasState


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
                    lambda r: rx.badge(
                        r,
                        color_scheme=rx.match(
                            r,
                            ("Propietario", "blue"),
                            ("Arrendatario", "green"),
                            ("Asesor", "purple"),
                            ("Codeudor", "orange"),
                            ("Proveedor", "cyan"),
                            "gray",
                        ),
                        variant="soft",
                        margin_right="1",
                    ),
                )
            )
        ),
        rx.table.cell(
            rx.badge(
                persona["estado"],
                color_scheme=rx.cond(persona["estado"] == "Activo", "green", "red"),
                variant="soft",
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
                            rx.icon("trash-2", size=16),
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
    return rx.fragment(
        rx.toast.provider(),
        dashboard_layout(
            rx.vstack(
                # Modal Component
                modal_persona(),
                # --- Elite Header with Gradient ---
                rx.box(
                    rx.hstack(
                        rx.vstack(
                            rx.heading(
                                "Gestión de Personas",
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
                                "Administre propietarios, arrendatarios y asesores con facilidad.",
                                color="var(--gray-10)",
                                size="3",
                            ),
                            rx.hstack(
                                rx.icon("users", size=18, color="var(--gray-9)"),
                                rx.text(
                                    f"Total: {PersonasState.total_items} personas",
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
                        rx.cond(
                            AuthState.check_action("Personas", "CREAR"),
                            rx.tooltip(
                                rx.button(
                                    rx.icon("plus", size=18),
                                    "Nueva Persona",
                                    size="3",
                                    on_click=PersonasState.open_create_modal,
                                    style={
                                        "background": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
                                        "color": "white",
                                    },
                                    _hover={
                                        "transform": "scale(1.05)",
                                        "box_shadow": "0 4px 12px rgba(102, 126, 234, 0.4)",
                                    },
                                    transition="all 0.2s ease",
                                ),
                                content="Crear nueva persona",
                            ),
                        ),
                        width="100%",
                        padding="5",
                        align="center",
                    ),
                    width="100%",
                    padding_bottom="2",
                    border_radius="12px",
                    style={
                        "background": "linear-gradient(135deg, rgba(102, 126, 234, 0.05) 0%, rgba(118, 75, 162, 0.05) 100%)",
                        "backdrop_filter": "blur(10px)",
                    },
                ),
                # --- Elite Toolbar ---
                rx.card(
                    rx.hstack(
                        # Search bar with enhanced styling
                        rx.input(
                            rx.input.slot(rx.icon("search", size=18)),
                            placeholder="Buscar por nombre o documento...",
                            value=PersonasState.search_query,
                            on_change=PersonasState.set_search,
                            size="3",
                            width="320px",
                            style={
                                "transition": "all 0.3s ease",
                            },
                            _focus={
                                "box_shadow": "0 0 0 3px rgba(102, 126, 234, 0.2)",
                            },
                        ),
                        # Role filter with icon
                        rx.select(
                            [
                                "Todos",
                                "Propietario",
                                "Arrendatario",
                                "Codeudor",
                                "Asesor",
                                "Proveedor",
                            ],
                            value=PersonasState.filtro_rol,
                            on_change=PersonasState.set_filtro_rol,
                            size="3",
                        ),
                        # Date filters
                        rx.input(
                            type="date",
                            placeholder="Desde",
                            on_change=PersonasState.set_fecha_inicio,
                            size="3",
                        ),
                        rx.input(
                            type="date",
                            placeholder="Hasta",
                            on_change=PersonasState.set_fecha_fin,
                            size="3",
                        ),
                        rx.spacer(),
                        # View toggle button
                        rx.tooltip(
                            rx.button(
                                rx.icon(
                                    rx.cond(
                                        PersonasState.view_mode == "table", "layout-grid", "table"
                                    ),
                                    size=18,
                                ),
                                on_click=PersonasState.toggle_view_mode,
                                variant="soft",
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
                            rx.button(
                                rx.icon("file-spreadsheet", size=16),
                                "Exportar",
                                color_scheme="green",
                                variant="soft",
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
                                rx.icon("refresh-cw", size=16),
                                variant="ghost",
                                size="3",
                                on_click=PersonasState.load_personas,
                                _hover={
                                    "transform": "rotate(180deg)",
                                },
                                transition="transform 0.3s ease",
                            ),
                            content="Recargar",
                        ),
                        padding="4",
                        width="100%",
                        align="center",
                        spacing="3",
                    ),
                    width="100%",
                    style={
                        "background": "var(--color-panel-solid)",
                    },
                ),
                # --- Content Area: Table or Cards View ---
                rx.cond(
                    PersonasState.is_loading,
                    rx.center(
                        rx.vstack(
                            rx.spinner(size="3", color="purple"),
                            rx.text("Cargando personas...", size="2", color="var(--gray-10)"),
                            spacing="2",
                        ),
                        padding="8",
                    ),
                    rx.cond(
                        PersonasState.view_mode == "table",
                        # TABLE VIEW - Improved
                        rx.card(
                            rx.box(
                                rx.table.root(
                                    rx.table.header(
                                        rx.table.row(
                                            rx.table.column_header_cell(
                                                "Nombre", style={"font-weight": "600"}
                                            ),
                                            rx.table.column_header_cell(
                                                "Documento", style={"font-weight": "600"}
                                            ),
                                            rx.table.column_header_cell(
                                                "Contacto", style={"font-weight": "600"}
                                            ),
                                            rx.table.column_header_cell(
                                                "Fecha Creación", style={"font-weight": "600"}
                                            ),
                                            rx.table.column_header_cell(
                                                "Roles", style={"font-weight": "600"}
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
                                                            p["nombre"], weight="medium", size="2"
                                                        ),
                                                        align="center",
                                                        spacing="3",
                                                    )
                                                ),
                                                rx.table.cell(
                                                    rx.text(
                                                        p["documento"],
                                                        size="2",
                                                        color="var(--gray-11)",
                                                    )
                                                ),
                                                rx.table.cell(
                                                    rx.vstack(
                                                        rx.hstack(
                                                            rx.icon(
                                                                "mail",
                                                                size=12,
                                                                color="var(--gray-9)",
                                                            ),
                                                            rx.text(p["correo"], size="1"),
                                                            spacing="1",
                                                        ),
                                                        rx.hstack(
                                                            rx.icon(
                                                                "phone",
                                                                size=12,
                                                                color="var(--gray-9)",
                                                            ),
                                                            rx.text(
                                                                p["contacto"],
                                                                size="1",
                                                                color="gray",
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
                                                        color="var(--gray-10)",
                                                    )
                                                ),
                                                rx.table.cell(
                                                    rx.box(
                                                        rx.foreach(
                                                            p["roles"],
                                                            lambda r: rx.badge(
                                                                rx.hstack(
                                                                    rx.icon(
                                                                        rx.match(
                                                                            r,
                                                                            ("Propietario", "home"),
                                                                            (
                                                                                "Arrendatario",
                                                                                "user-check",
                                                                            ),
                                                                            ("Asesor", "briefcase"),
                                                                            ("Codeudor", "shield"),
                                                                            ("Proveedor", "tool"),
                                                                            "user",
                                                                        ),
                                                                        size=12,
                                                                    ),
                                                                    rx.text(r, size="1"),
                                                                    spacing="1",
                                                                    align="center",
                                                                ),
                                                                color_scheme=rx.match(
                                                                    r,
                                                                    ("Propietario", "blue"),
                                                                    ("Arrendatario", "green"),
                                                                    ("Asesor", "purple"),
                                                                    ("Codeudor", "orange"),
                                                                    ("Proveedor", "cyan"),
                                                                    "gray",
                                                                ),
                                                                variant="soft",
                                                                margin_right="1",
                                                                margin_bottom="1",
                                                            ),
                                                        )
                                                    )
                                                ),
                                                rx.table.cell(
                                                    rx.badge(
                                                        p["estado"],
                                                        color_scheme=rx.cond(
                                                            p["estado"] == "Activo", "green", "red"
                                                        ),
                                                        variant="soft",
                                                        size="2",
                                                    )
                                                ),
                                                rx.table.cell(
                                                    rx.hstack(
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
                                                                        "background": "var(--accent-3)",
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
                                                                    rx.icon("trash-2", size=16),
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
                                                        spacing="1",
                                                    )
                                                ),
                                                _hover={
                                                    "background": "var(--gray-2)",
                                                },
                                                style={
                                                    "transition": "background 0.2s ease",
                                                },
                                            ),
                                        ),
                                    ),
                                    width="100%",
                                    variant="surface",
                                ),
                                width="100%",
                                overflow_x="auto",
                            ),
                            padding="0",
                            width="100%",
                        ),
                        # CARDS VIEW - New
                        rx.box(
                            rx.cond(
                                PersonasState.total_items > 0,
                                rx.box(
                                    rx.foreach(PersonasState.personas, person_card),
                                    display="grid",
                                    grid_template_columns=[
                                        "repeat(1, 1fr)",  # mobile
                                        "repeat(1, 1fr)",  # small tablet
                                        "repeat(2, 1fr)",  # tablet
                                        "repeat(3, 1fr)",  # desktop
                                    ],
                                    gap="9",
                                    width="100%",
                                    padding="4",
                                ),
                                # Empty state for cards
                                rx.center(
                                    rx.vstack(
                                        rx.icon("users", size=48, color="var(--gray-8)"),
                                        rx.heading(
                                            "No hay personas", size="5", color="var(--gray-11)"
                                        ),
                                        rx.text(
                                            "Crea tu primera persona haciendo clic en el botón superior",
                                            color="var(--gray-10)",
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
                rx.card(
                    rx.hstack(
                        rx.button(
                            rx.icon("chevron-left", size=16),
                            "Anterior",
                            on_click=PersonasState.prev_page,
                            disabled=PersonasState.page == 1,
                            variant="soft",
                            size="3",
                            _hover={
                                "transform": "translateX(-2px)",
                            },
                            transition="transform 0.2s ease",
                        ),
                        rx.vstack(
                            rx.text(
                                f"Página {PersonasState.page} de {PersonasState.total_pages}",
                                size="3",
                                weight="medium",
                            ),
                            rx.text(
                                f"Mostrando {(PersonasState.page - 1) * PersonasState.page_size + 1}-"
                                f"{rx.cond(PersonasState.page * PersonasState.page_size > PersonasState.total_items, PersonasState.total_items, PersonasState.page * PersonasState.page_size)} "
                                f"de {PersonasState.total_items}",
                                size="1",
                                color="var(--gray-10)",
                            ),
                            spacing="0",
                            align="center",
                        ),
                        rx.button(
                            "Siguiente",
                            rx.icon("chevron-right", size=16),
                            on_click=PersonasState.next_page,
                            disabled=PersonasState.page >= PersonasState.total_pages,
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
                padding="6",
                width="100%",
                spacing="4",
            )
        ),
    )
