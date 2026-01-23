"""
Página de Seguros - Reflex
Gestión de seguros de arrendamiento y pólizas con filtros y CRUD completo.
"""

import reflex as rx
from src.presentacion_reflex.state.seguros_state import SegurosState
from src.presentacion_reflex.state.auth_state import AuthState
from src.presentacion_reflex.components.layout.dashboard_layout import dashboard_layout
from src.presentacion_reflex.components.seguros import modal_seguro, modal_poliza, modal_detalle_seguro


def seguros_page() -> rx.Component:
    """
    Página principal de Seguros con filtros y CRUD.
    """
    
    return dashboard_layout(
        rx.vstack(
            # Header
            rx.vstack(
                rx.text("Inicio > Seguros", size="2", color="gray.10"),
                rx.heading("Gestión de Seguros", size="8"),
                spacing="1",
                margin_bottom="6",
            ),
            
            # Search bar
            rx.hstack(
                rx.input(
                    placeholder="Buscar seguro por nombre...",
                    value=SegurosState.search_text,
                    on_change=SegurosState.set_search,
                    width="100%",
                ),
                rx.button(
                    rx.icon("search", size=18),
                    on_click=SegurosState.search_seguros,
                    size="3",
                ),
                spacing="2",
                width="100%",
                margin_bottom="3",
            ),
            
            # Filtros y Acciones
            rx.hstack(
                # Filtro Estado
                rx.select(
                    ["Todos", "Activos", "Inactivos"],
                    placeholder="Estado",
                    value=SegurosState.filter_estado,
                    on_change=SegurosState.set_filter_estado,
                    size="2",
                ),
                
                rx.spacer(),
                
                # Nueva Póliza
                rx.cond(
                    AuthState.check_action("Seguros", "CREAR"),
                    rx.button(
                        rx.icon("file-plus", size=18),
                        "Nueva Póliza",
                        on_click=SegurosState.open_create_poliza_modal,
                        size="3",
                        variant="soft",
                        color_scheme="blue",
                    )
                ),
                
                # Nuevo Seguro
                rx.cond(
                    AuthState.check_action("Seguros", "CREAR"),
                    rx.button(
                        rx.icon("plus", size=18),
                        "Nuevo Seguro",
                        on_click=SegurosState.open_create_seguro_modal,
                        size="3",
                    )
                ),
                
                spacing="3",
                width="100%",
                margin_bottom="4",
                wrap="wrap",
            ),
            
            # Contador
            rx.text(
                rx.cond(
                    SegurosState.total_items > 0,
                    f"{SegurosState.total_items} seguros encontrados",
                    "0 seguros encontrados"
                ),
                size="2",
                color="gray.11",
                margin_bottom="3",
            ),
            
            # Loading / Error / Content
            rx.cond(
                SegurosState.is_loading,
                rx.center(
                    rx.vstack(
                        rx.spinner(size="3"),
                        rx.text("Cargando seguros...", color="gray.11"),
                        spacing="3",
                    ),
                    padding="50px",
                ),
                rx.cond(
                    SegurosState.error_message != "",
                    rx.callout(
                        SegurosState.error_message,
                        icon="circle_alert",
                        color_scheme="red",
                        role="alert",
                    ),
                    rx.cond(
                        SegurosState.seguros.length() == 0,
                        rx.center(
                            rx.vstack(
                                rx.icon("shield", size=60, color="gray.8"),
                                rx.text("No se encontraron seguros", size="4", color="gray.11"),
                                rx.text("Crea un nuevo seguro para comenzar", size="2", color="gray.10"),
                                spacing="3",
                            ),
                            padding="50px",
                        ),
                        # Tabla de Seguros
                        rx.table.root(
                            rx.table.header(
                                rx.table.row(
                                    rx.table.column_header_cell("Nombre del Seguro"),
                                    rx.table.column_header_cell("Porcentaje"),
                                    rx.table.column_header_cell("Fecha Inicio"),
                                    rx.table.column_header_cell("Estado"),
                                    rx.table.column_header_cell("Acciones"),
                                ),
                            ),
                            rx.table.body(
                                rx.foreach(
                                    SegurosState.seguros,
                                    lambda seguro: rx.table.row(
                                        rx.table.cell(
                                            rx.text(
                                                seguro["nombre_seguro"],
                                                weight="bold",
                                            )
                                        ),
                                        rx.table.cell(
                                            rx.badge(
                                                f"{seguro['porcentaje_seguro']}%",
                                                color_scheme="blue",
                                            )
                                        ),
                                        rx.table.cell(
                                            rx.cond(
                                                seguro["fecha_inicio_seguro"] != "",
                                                seguro["fecha_inicio_seguro"],
                                                "N/A"
                                            )
                                        ),
                                        rx.table.cell(
                                            rx.badge(
                                                rx.cond(
                                                    seguro["estado_seguro"],
                                                    "Activo",
                                                    "Inactivo"
                                                ),
                                                color_scheme=rx.cond(
                                                    seguro["estado_seguro"],
                                                    "green",
                                                    "gray"
                                                ),
                                            )
                                        ),
                                        rx.table.cell(
                                            rx.hstack(
                                                # Ver Detalle
                                                rx.tooltip(
                                                    rx.icon_button(
                                                        rx.icon("eye", size=22),
                                                        size="2",
                                                        variant="soft",
                                                        color_scheme="blue",
                                                        on_click=lambda: SegurosState.open_detail_modal(seguro["id_seguro"]),
                                                    ),
                                                    content="Ver detalle"
                                                ),
                                                # Editar
                                                rx.cond(
                                                    AuthState.check_action("Seguros", "EDITAR"),
                                                    rx.tooltip(
                                                        rx.icon_button(
                                                            rx.icon("square-pen", size=22),
                                                            size="2",
                                                            variant="soft",
                                                            on_click=lambda: SegurosState.open_edit_seguro_modal(seguro["id_seguro"]),
                                                        ),
                                                        content="Editar seguro"
                                                    )
                                                ),
                                                # Toggle Estado
                                                rx.cond(
                                                    AuthState.check_action("Seguros", "EDITAR"),
                                                    rx.tooltip(
                                                        rx.icon_button(
                                                            rx.icon(
                                                                rx.cond(
                                                                    seguro["estado_seguro"],
                                                                    "shield-off",
                                                                    "shield-check"
                                                                ),
                                                                size=22
                                                            ),
                                                            size="2",
                                                            variant="soft",
                                                            color_scheme=rx.cond(
                                                                seguro["estado_seguro"],
                                                                "red",
                                                                "green"
                                                            ),
                                                            on_click=lambda: SegurosState.toggle_estado_seguro(seguro["id_seguro"], seguro["estado_seguro"]),
                                                        ),
                                                        content=rx.cond(
                                                            seguro["estado_seguro"],
                                                            "Desactivar seguro",
                                                            "Activar seguro"
                                                        )
                                                    )
                                                ),
                                                spacing="1",
                                            )
                                        ),
                                    ),
                                ),
                            ),
                            width="100%",
                        ),
                    ),
                ),
            ),
            
            # Modales
            modal_seguro(),
            modal_poliza(),
            modal_detalle_seguro(),
            
            spacing="4",
            width="100%",
            padding="20px",
        )
    )


# Ruta protegida
@rx.page(route="/seguros", on_load=[AuthState.require_login, SegurosState.on_load])
def seguros():
    return seguros_page()
