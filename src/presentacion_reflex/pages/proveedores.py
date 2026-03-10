"""
Página de Proveedores - Reflex
Gestión de prestadores de servicios y mantenimiento.
"""

import reflex as rx
from src.presentacion_reflex import styles
from src.presentacion_reflex.components.layout.dashboard_layout import dashboard_layout
from src.presentacion_reflex.state.auth_state import AuthState
from src.presentacion_reflex.state.proveedores_state import ProveedoresState
from src.presentacion_reflex.components.neuro_elements import neuro_input, neuro_button, neuro_select_root


def proveedores_content() -> rx.Component:
    return rx.vstack(
        # --- Elite Header ---
        rx.box(
            rx.hstack(
                rx.vstack(
                    rx.heading(
                        "Directorio de Proveedores",
                        size="8",
                        weight="bold",
                        color=styles.TEXT_PRIMARY,
                    ),
                    rx.text("Gestión de prestadores de servicios y mantenimientos", size="3"),
                    rx.hstack(
                        rx.icon("users", size=18, color="var(--gray-9)"),
                        rx.text(
                            "Total: ", ProveedoresState.total_items, " proveedores",
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
                    AuthState.check_action("Proveedores", "CREAR"),
                    rx.tooltip(
                        neuro_button(
                            rx.hstack(rx.icon("plus", size=18), rx.text("Nuevo Proveedor")),
                            on_click=ProveedoresState.open_modal,
                            size="3",
                        ),
                        content="Registrar nuevo proveedor",
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
        # --- Toolbar ---
        rx.card(
            rx.hstack(
                neuro_input(
                    rx.input.slot(rx.icon("search", size=18)),
                    placeholder="Buscar por nombre, documento o especialidad...",
                    value=ProveedoresState.search_text,
                    on_change=ProveedoresState.set_search,
                    width="400px",
                    size="3",
                ),
                neuro_select_root(
                    rx.foreach(
                        ProveedoresState.especialidad_options,
                        lambda opt: rx.select.item(opt, value=opt),
                    ),
                    value=ProveedoresState.filter_especialidad,
                    on_change=ProveedoresState.set_filter_especialidad,
                    placeholder="Especialidad",
                    width="200px",
                ),
                rx.spacer(),
                neuro_button(
                    rx.icon("refresh-cw", size=16),
                    on_click=ProveedoresState.load_proveedores,
                    size="3",
                ),
                spacing="3",
                width="100%",
                align="center",
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
        # --- Table ---
        rx.cond(
            ProveedoresState.is_loading,
            rx.center(rx.spinner(size="3"), height="300px", width="100%"),
            rx.box(
                rx.cond(
                    ProveedoresState.proveedores.length() == 0,
                    rx.center(
                        rx.vstack(
                            rx.icon("users-round", size=48, color="var(--gray-6)"),
                            rx.text("No se encontraron proveedores", color="var(--gray-10)"),
                            spacing="2",
                        ),
                        height="300px",
                        width="100%",
                    ),
                    rx.card(
                        rx.table.root(
                            rx.table.header(
                                rx.table.row(
                                    rx.table.column_header_cell("Documento"),
                                    rx.table.column_header_cell("Nombre"),
                                    rx.table.column_header_cell("Especialidad"),
                                    rx.table.column_header_cell("Contacto"),
                                    rx.table.column_header_cell("Acciones"),
                                )
                            ),
                            rx.table.body(
                                rx.foreach(
                                    ProveedoresState.proveedores,
                                    lambda p: rx.table.row(
                                        rx.table.cell(p["documento"]),
                                        rx.table.cell(p["nombre"], weight="bold"),
                                        rx.table.cell(
                                            rx.badge(p["especialidad"], color_scheme="blue")
                                        ),
                                        rx.table.cell(
                                            rx.hstack(
                                                rx.icon("phone", size=14, color="var(--gray-9)"),
                                                rx.text(p["telefono"], size="2"),
                                                spacing="2",
                                                align="center",
                                            )
                                        ),
                                        rx.table.cell(
                                            rx.hstack(
                                                rx.tooltip(
                                                    rx.icon_button(
                                                        rx.icon("pencil", size=16),
                                                        variant="ghost",
                                                        on_click=lambda: ProveedoresState.open_edit_modal(
                                                            p["id_proveedor"]
                                                        ),
                                                    ),
                                                    content="Editar Proveedor",
                                                ),
                                                rx.tooltip(
                                                    rx.icon_button(
                                                        rx.icon("trash-2", size=16),
                                                        variant="ghost",
                                                        color_scheme="red",
                                                        on_click=lambda: ProveedoresState.delete_proveedor(
                                                            p["id_proveedor"]
                                                        ),
                                                    ),
                                                    content="Eliminar Proveedor",
                                                ),
                                                spacing="2",
                                            )
                                        ),
                                    ),
                                )
                            ),
                            width="100%",
                            variant="surface",
                        ),
                        width="100%",
                        style={"padding": "0"},
                    ),
                ),
                width="100%",
            ),
        ),
        # --- Pagination ---
        rx.card(
            rx.hstack(
                neuro_button(
                    rx.icon("chevron-left", size=16),
                    rx.text("Anterior", display=rx.breakpoints(initial="none", md="block")),
                    on_click=ProveedoresState.prev_page,
                    disabled=ProveedoresState.current_page == 1,
                    size="3",
                ),
                rx.vstack(
                    rx.text(
                        "Página ", ProveedoresState.current_page,
                        size=rx.breakpoints(initial="2", md="3"),
                        weight="medium",
                        color=styles.TEXT_PRIMARY,
                    ),
                    rx.text(
                        "Mostrando ", (ProveedoresState.current_page - 1) * ProveedoresState.page_size + 1, "-",
                        rx.cond(ProveedoresState.current_page * ProveedoresState.page_size > ProveedoresState.total_items, ProveedoresState.total_items, ProveedoresState.current_page * ProveedoresState.page_size),
                        " de ", ProveedoresState.total_items,
                        size="1",
                        color=styles.TEXT_SECONDARY,
                        display=rx.breakpoints(initial="none", md="block"),
                    ),
                    spacing="0",
                    align="center",
                ),
                neuro_button(
                    rx.text("Siguiente", display=rx.breakpoints(initial="none", md="block")),
                    rx.icon("chevron-right", size=16),
                    on_click=ProveedoresState.next_page,
                    disabled=ProveedoresState.current_page * ProveedoresState.page_size
                    >= ProveedoresState.total_items,
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
        spacing="4",
        width="100%",
        padding="2em",
    )


# --- MODAL ---
from src.presentacion_reflex.components.proveedores.modal_form import (
    modal_proveedor as modal_form,
)


@rx.page(
    route="/proveedores",
    title="Proveedores | Inmobiliaria Velar",
    on_load=[AuthState.require_login, ProveedoresState.load_proveedores],
)
def proveedores_page() -> rx.Component:
    return dashboard_layout(
        rx.box(
            proveedores_content(),
            modal_form(),
            width="100%",
        )
    )
