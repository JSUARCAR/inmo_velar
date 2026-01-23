import reflex as rx
from src.presentacion_reflex.components.layout.dashboard_layout import dashboard_layout
from src.presentacion_reflex.components.proveedores.modal_form import modal_form
from src.presentacion_reflex.state.auth_state import AuthState
from src.presentacion_reflex.state.proveedores_state import ProveedoresState

def proveedores_content() -> rx.Component:
    return rx.vstack(
        # --- Elite Header with Gradient (Personas Style) ---
        rx.box(
            rx.hstack(
                rx.vstack(
                    rx.heading(
                        "Gestión de Proveedores", 
                        size="8",
                        weight="bold",
                        style={
                            "background": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
                            "background_clip": "text",
                            "-webkit-background-clip": "text",
                            "-webkit-text-fill-color": "transparent",
                        }
                    ),
                    rx.text(
                        "Administre los proveedores de servicios y sus especialidades.", 
                        color="var(--gray-10)",
                        size="3",
                    ),
                    rx.hstack(
                        rx.icon("briefcase", size=18, color="var(--gray-9)"),
                        rx.text(
                            f"Total: {ProveedoresState.total_items} proveedores",
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
                    AuthState.check_action("Proveedores", "CREAR"),
                    rx.tooltip(
                        rx.button(
                            rx.icon("plus", size=18),
                            "Nuevo Proveedor",
                            size="3",
                            on_click=ProveedoresState.open_create_modal,
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
                        content="Crear nuevo proveedor"
                    )
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
            }
        ),

        # Toolbar de filtros
        rx.card(
            rx.hstack(
                # Búsqueda
                rx.input(
                    rx.input.slot(rx.icon("search", size=18)),
                    placeholder="Buscar por nombre o especialidad...",
                    value=ProveedoresState.search_text,
                    on_change=ProveedoresState.set_search,
                    width="300px",
                    size="3",
                    style={
                        "transition": "all 0.3s ease",
                    },
                    _focus={
                        "box_shadow": "0 0 0 3px rgba(102, 126, 234, 0.2)",
                    }
                ),
                
                rx.spacer(),
                
                # Filtros
                rx.text("Especialidad:", weight="bold", color="var(--gray-11)"),
                rx.select(
                    ["Todas", "Plomería", "Electricidad", "Gas", "Pintura", "Obra Civil", "Aseo", "Otros"],
                    value=ProveedoresState.filter_especialidad,
                    on_change=ProveedoresState.set_filter_especialidad,
                    size="3",
                    variant="surface",
                ),
                
                # Botón recargar
                rx.tooltip(
                    rx.icon_button(
                        rx.icon("refresh-cw", size=18),
                        variant="ghost",
                        size="3",
                        on_click=ProveedoresState.load_data,
                        _hover={
                            "transform": "rotate(180deg)",
                        },
                        transition="transform 0.3s ease",
                    ),
                    content="Actualizar lista"
                ),
                
                width="100%",
                padding="3",
                align="center",
                spacing="3",
            ),
            width="100%",
            style={
                "background": "var(--color-panel-solid)",
            }
        ),

        # Tabla de datos
        rx.card(
            rx.vstack(
                rx.table.root(
                    rx.table.header(
                        rx.table.row(
                            rx.table.column_header_cell("Proveedor", style={"font-weight": "600"}),
                            rx.table.column_header_cell("Especialidad", style={"font-weight": "600"}),
                            rx.table.column_header_cell("Contacto", style={"font-weight": "600"}),
                            rx.table.column_header_cell("Calificación", style={"font-weight": "600"}),
                            rx.table.column_header_cell("Acciones", align="center", style={"font-weight": "600"}),
                        )
                    ),
                    rx.table.body(
                        rx.foreach(
                            ProveedoresState.proveedores,
                            lambda p: rx.table.row(
                                rx.table.cell(
                                    rx.hstack(
                                        rx.avatar(
                                            fallback=p["nombre"].to_string()[:2].upper(),
                                            radius="full",
                                            size="3",
                                            color_scheme="indigo",
                                            variant="soft",
                                        ),
                                        rx.vstack(
                                            rx.text(p["nombre"], weight="bold", size="2"),
                                            rx.text(p["observaciones"], size="1", color="var(--gray-10)"),
                                            spacing="1"
                                        ),
                                        align="center",
                                        spacing="3",
                                    )
                                ),
                                rx.table.cell(
                                    rx.badge(
                                        p["especialidad"], 
                                        variant="soft", 
                                        radius="full",
                                        color_scheme="blue"
                                    )
                                ),
                                rx.table.cell(
                                    rx.text(p["contacto"], size="2", color="var(--gray-11)")
                                ),
                                rx.table.cell(
                                    rx.hstack(
                                        rx.icon("star", size=16, color="gold", fill="gold"),
                                        rx.text(p["calificacion"], weight="medium"),
                                        align="center",
                                        spacing="1"
                                    )
                                ),
                                rx.table.cell(
                                    rx.hstack(
                                        rx.cond(
                                            AuthState.check_action("Proveedores", "EDITAR"),
                                            rx.tooltip(
                                                rx.icon_button(
                                                    rx.icon("pencil", size=16),
                                                    variant="ghost",
                                                    size="1",
                                                    on_click=lambda: ProveedoresState.open_edit_modal(p)
                                                ),
                                                content="Editar proveedor"
                                            )
                                        ),
                                        rx.cond(
                                            AuthState.check_action("Proveedores", "ELIMINAR"),
                                            rx.tooltip(
                                                rx.icon_button(
                                                    rx.icon("trash-2", size=16),
                                                    variant="ghost",
                                                    size="1",
                                                    color_scheme="red",
                                                    on_click=lambda: ProveedoresState.eliminar_proveedor(p["id_proveedor"])
                                                ),
                                                content="Eliminar proveedor"
                                            )
                                        ),
                                        spacing="2",
                                        justify="center"
                                    )
                                )
                            )
                        )
                    )
                ),
                
                # Estado vacio
                rx.cond(
                    ProveedoresState.total_items == 0,
                    rx.center(
                        rx.vstack(
                            rx.icon("inbox", size=48, color="gray"),
                            rx.text("No se encontraron proveedores", color_scheme="gray"),
                            padding="4"
                        ),
                        width="100%"
                    )
                ),
                
                # Premium Pagination
                rx.card(
                    rx.hstack(
                        rx.button(
                            rx.icon("chevron-left", size=16),
                            "Anterior",
                            on_click=ProveedoresState.prev_page,
                            disabled=ProveedoresState.current_page == 1,
                            variant="soft",
                            size="3",
                            _hover={
                                "transform": "translateX(-2px)",
                            },
                            transition="transform 0.2s ease",
                        ),
                        rx.vstack(
                            rx.text(
                                f"Página {ProveedoresState.current_page}",
                                size="3",
                                weight="medium",
                            ),
                            rx.text(
                                f"Mostrando {(ProveedoresState.current_page - 1) * ProveedoresState.page_size + 1}-"
                                f"{rx.cond(ProveedoresState.current_page * ProveedoresState.page_size > ProveedoresState.total_items, ProveedoresState.total_items, ProveedoresState.current_page * ProveedoresState.page_size)} "
                                f"de {ProveedoresState.total_items}",
                                size="1",
                                color="var(--gray-10)",
                            ),
                            spacing="0",
                            align="center",
                        ),
                        rx.button(
                            "Siguiente",
                            rx.icon("chevron-right", size=16),
                            on_click=ProveedoresState.next_page,
                            disabled=ProveedoresState.current_page * ProveedoresState.page_size >= ProveedoresState.total_items,
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
                    }
                )
            ),
            width="100%"
        ),
        
        # Integrar modal
        modal_form(),
        
        spacing="4",
        width="100%"
    )

@rx.page(route="/proveedores", title="Proveedores | Inmobiliaria Velar", on_load=ProveedoresState.on_load)
def proveedores_page() -> rx.Component:
    return dashboard_layout(proveedores_content())
