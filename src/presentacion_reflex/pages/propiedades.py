"""
Página de Propiedades - Reflex
Gestión de inventario inmobiliario con filtros, vista cards/tabla, y paginación.
"""

import reflex as rx
from src.presentacion_reflex.state.propiedades_state import PropiedadesState
from src.presentacion_reflex.state.auth_state import AuthState
from src.presentacion_reflex.components.layout.dashboard_layout import dashboard_layout
from src.presentacion_reflex.components.propiedades.property_card import property_card
from src.presentacion_reflex.components.propiedades.modal_form import modal_propiedad


def propiedades_page() -> rx.Component:
    """
    Página principal de Propiedades con filtros y CRUD.
    """
    
    return rx.fragment(
        rx.toast.provider(),
        dashboard_layout(
         rx.vstack(
            # --- Elite Header ---
            # --- Elite Header with Gradient (Personas Style) ---
            rx.box(
                rx.hstack(
                    rx.vstack(
                        rx.heading(
                            "Gestión de Propiedades", 
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
                            "Inventario inmobiliario y seguimiento de activos", 
                            color="var(--gray-10)",
                            size="3",
                        ),
                        rx.hstack(
                            rx.icon("building-2", size=18, color="var(--gray-9)"),
                            rx.text(
                                f"Total: {PropiedadesState.total_items} propiedades",
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
                        AuthState.check_action("Propiedades", "CREAR"),
                        rx.tooltip(
                            rx.button(
                                rx.icon("plus", size=18),
                                "Nueva Propiedad",
                                size="3",
                                on_click=PropiedadesState.open_create_modal,
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
                            content="Crear nueva propiedad"
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
            
            # --- Main Content Area ---
            rx.vstack(
                # Toolbar Section
                rx.card(
                    rx.hstack(
                        # Search Bar with enhanced styling
                        rx.input(
                            rx.input.slot(rx.icon("search", size=18)),
                            placeholder="Buscar por matrícula, dirección...",
                            value=PropiedadesState.search_text,
                            on_change=PropiedadesState.set_search,
                            size="3",
                            width="320px",
                            style={
                                "transition": "all 0.3s ease",
                            },
                            _focus={
                                "box_shadow": "0 0 0 3px rgba(102, 126, 234, 0.2)",
                            }
                        ),
                        
                        rx.spacer(),
                        
                        # Filters Row
                        rx.select(
                            PropiedadesState.tipos_options,
                            placeholder="Tipo",
                            value=PropiedadesState.filter_tipo,
                            on_change=PropiedadesState.set_filter_tipo,
                            size="3",
                            variant="surface",
                        ),
                        
                        rx.select.root(
                            rx.select.trigger(placeholder="Disponibilidad", variant="surface", size="3"),
                            rx.select.content(
                                rx.select.group(
                                    rx.select.item("Todos", value="Todos"),
                                    rx.select.item("Disponible", value="1"),
                                    rx.select.item("Ocupada", value="0"),
                                )
                            ),
                            value=PropiedadesState.filter_disponibilidad,
                            on_change=PropiedadesState.set_filter_disponibilidad,
                        ),

                        # View Toggle Button (Single Button like Personas)
                        rx.tooltip(
                            rx.button(
                                rx.cond(
                                    PropiedadesState.vista_tipo == "cards",
                                    rx.icon("table", size=18),
                                    rx.icon("layout-grid", size=18)
                                ),
                                on_click=PropiedadesState.toggle_vista,
                                variant="soft",
                                size="3",
                                color_scheme="gray",
                            ),
                            content=rx.cond(
                                PropiedadesState.vista_tipo == "cards",
                                "Cambiar a vista de tabla",
                                "Cambiar a vista de cards"
                            )
                        ),
                        
                        # Export Button (Standardized)
                        rx.tooltip(
                            rx.button(
                                rx.icon("file-spreadsheet", size=16),
                                "Exportar",
                                color_scheme="green",
                                variant="soft",
                                on_click=PropiedadesState.exportar_csv,
                                size="3",
                                _hover={
                                    "transform": "scale(1.05)",
                                },
                                transition="all 0.2s ease",
                            ),
                            content="Exportar a Excel"
                        ),
                        
                        spacing="3",
                        width="100%",
                        align="center",
                        wrap="wrap",
                    ),
                    padding="5",
                    width="100%",
                    style={
                        "backdrop_filter": "blur(12px)",
                        "background": "rgba(255, 255, 255, 0.8)",
                        "border": "1px solid rgba(255, 255, 255, 0.3)",
                    },
                ),
                
                # Stats/Counter
                rx.hstack(
                    rx.text(
                        f"Mostrando {PropiedadesState.propiedades.length()} de {PropiedadesState.total_items} propiedades",
                        size="2",
                        weight="medium",
                        color="var(--gray-10)",
                    ),
                    rx.spacer(),
                    # Toggle solo activas
                    rx.hstack(
                        rx.text("Solo Activas", size="2", color="var(--gray-10)"),
                        rx.switch(
                            checked=PropiedadesState.solo_activas,
                            on_change=PropiedadesState.toggle_solo_activas,
                            size="1",
                            color_scheme="green",
                        ),
                        align="center",
                        spacing="2",
                    ),
                    width="100%",
                    padding_x="2",
                ),

                # Content Area (Grid or Table)
                rx.cond(
                    PropiedadesState.is_loading,
                    rx.center(
                        rx.vstack(
                            rx.spinner(size="3", color="var(--accent-9)"),
                            rx.text("Cargando inventario...", color="var(--gray-10)"),
                            spacing="4",
                        ),
                        height="400px",
                        width="100%",
                    ),
                    rx.box(
                        rx.cond(
                            PropiedadesState.propiedades.length() == 0,
                            rx.center(
                                rx.vstack(
                                    rx.icon("search-x", size=64, color="var(--gray-6)"),
                                    rx.text("No se encontraron propiedades", size="5", weight="bold", color="var(--gray-10)"),
                                    rx.text("Intenta ajustar los filtros o registra una nueva propiedad.", size="3", color="var(--gray-9)"),
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
                                PropiedadesState.vista_tipo == "cards",
                                # Grid View
                                rx.grid(
                                    rx.foreach(
                                        PropiedadesState.propiedades,
                                        lambda prop: property_card(
                                            id_propiedad=prop["id_propiedad"],
                                            matricula=prop["matricula_inmobiliaria"],
                                            direccion=prop["direccion_propiedad"],
                                            tipo=prop["tipo_propiedad"],
                                            municipio=prop["municipio_nombre"],
                                            disponibilidad=prop["disponibilidad"],
                                            valor_canon=prop["valor_canon"],
                                            area_metros=prop["area_metros"],
                                            habitaciones=prop["habitaciones"],
                                            banos=prop["banos"],
                                            parqueadero=prop["parqueadero"],
                                            valor_venta=prop["valor_venta"],
                                            comision_venta=prop["comision_venta"],
                                            codigo_energia=prop["codigo_energia"],
                                            codigo_agua=prop["codigo_agua"],
                                            codigo_gas=prop["codigo_gas"],
                                            on_edit=PropiedadesState.open_edit_modal,
                                            on_toggle_disponibilidad=PropiedadesState.toggle_disponibilidad,
                                        )
                                    ),
                                    columns="3",
                                    gap="9",
                                    width="100%",
                                ),
                                # Table View (Premium)
                                rx.card(
                                    rx.table.root(
                                        rx.table.header(
                                            rx.table.row(
                                                rx.table.column_header_cell("Propiedad"),
                                                rx.table.column_header_cell("Tipo"),
                                                rx.table.column_header_cell("Municipio"),
                                                rx.table.column_header_cell("Estado"),
                                                rx.table.column_header_cell("Canon"),
                                                rx.table.column_header_cell("Venta / Comisión"),
                                                rx.table.column_header_cell("Servicios"),
                                                rx.table.column_header_cell("Acciones"),
                                            ),
                                        ),
                                        rx.table.body(
                                            rx.foreach(
                                                PropiedadesState.propiedades,
                                                lambda prop: rx.table.row(
                                                    rx.table.cell(
                                                        rx.hstack(
                                                            rx.box(
                                                                rx.icon("home", size=20, color="var(--accent-9)"),
                                                                padding="8px",
                                                                background="var(--accent-3)",
                                                                border_radius="8px",
                                                            ),
                                                            rx.vstack(
                                                                rx.text(prop["direccion_propiedad"], weight="bold", size="2"),
                                                                rx.text(prop["matricula_inmobiliaria"], size="1", color="var(--gray-10)"),
                                                                spacing="1",
                                                            ),
                                                            spacing="3",
                                                            align="center",
                                                        )
                                                    ),
                                                    rx.table.cell(
                                                        rx.badge(prop["tipo_propiedad"], variant="surface", color_scheme="blue")
                                                    ),
                                                    rx.table.cell(prop["municipio_nombre"]),
                                                    rx.table.cell(
                                                        rx.badge(
                                                            rx.cond(prop["disponibilidad"] == 1, "Disponible", "Ocupada"),
                                                            color_scheme=rx.cond(prop["disponibilidad"] == 1, "green", "gray"),
                                                            variant="soft",
                                                        )
                                                    ),
                                                    rx.table.cell(
                                                        rx.text(
                                                            f"${prop['valor_canon']:,.0f}",
                                                            weight="bold",
                                                            style={"font_variant_numeric": "tabular-nums"}
                                                        )
                                                    ),
                                                    rx.table.cell(
                                                        rx.vstack(
                                                            rx.text(
                                                                f"${prop['valor_venta']:,.0f}",
                                                                weight="bold",
                                                                size="2",
                                                                style={"font_variant_numeric": "tabular-nums"}
                                                            ),
                                                            rx.text(
                                                                f"(${(prop['valor_venta'].to(float) * prop['comision_venta'].to(float) / 100):,.0f})",
                                                                size="1",
                                                                color="var(--gray-10)",
                                                                style={"font_variant_numeric": "tabular-nums"}
                                                            ),
                                                            spacing="0",
                                                            align="start"
                                                        )
                                                    ),
                                                    rx.table.cell(
                                                        rx.hstack(
                                                            rx.cond(
                                                                prop["codigo_energia"] != "",
                                                                rx.tooltip(
                                                                    rx.icon("zap", size=14, color="var(--yellow-9)"),
                                                                    content=f"Energía: {prop['codigo_energia']}"
                                                                )
                                                            ),
                                                            rx.cond(
                                                                prop["codigo_agua"] != "",
                                                                rx.tooltip(
                                                                    rx.icon("droplet", size=14, color="var(--blue-9)"),
                                                                    content=f"Acueducto: {prop['codigo_agua']}"
                                                                )
                                                            ),
                                                            rx.cond(
                                                                prop["codigo_gas"] != "",
                                                                rx.tooltip(
                                                                    rx.icon("flame", size=14, color="var(--orange-9)"),
                                                                    content=f"Gas: {prop['codigo_gas']}"
                                                                )
                                                            ),
                                                            spacing="2"
                                                        )
                                                    ),
                                                    rx.table.cell(
                                                        rx.hstack(
                                                            rx.cond(
                                                                AuthState.check_action("Propiedades", "EDITAR"),
                                                                rx.hstack(
                                                                    rx.tooltip(
                                                                        rx.icon_button(
                                                                            rx.icon("refresh-ccw", size=16),
                                                                            size="1",
                                                                            variant="ghost",
                                                                            color_scheme="blue",
                                                                            on_click=lambda: PropiedadesState.toggle_disponibilidad(
                                                                                prop["id_propiedad"], 
                                                                                rx.cond(prop["disponibilidad"] == 1, 0, 1)
                                                                            ),
                                                                        ),
                                                                        content="Cambiar Estado"
                                                                    ),
                                                                    rx.tooltip(
                                                                        rx.icon_button(
                                                                            rx.icon("pencil", size=16),
                                                                            size="1",
                                                                            variant="ghost",
                                                                            on_click=lambda: PropiedadesState.open_edit_modal(prop["id_propiedad"]),
                                                                        ),
                                                                        content="Editar"
                                                                    ),
                                                                    spacing="1",
                                                                )
                                                            ),
                                                        )
                                                    ),
                                                ),
                                            ),
                                        ),
                                        variant="surface",
                                        width="100%",
                                    ),
                                    width="100%",
                                ),
                            ),
                        ),
                        width="100%",
                    ),
                ),
                
                # --- Premium Pagination ---
                rx.card(
                    rx.hstack(
                        rx.button(
                            rx.icon("chevron-left", size=16),
                            "Anterior",
                            on_click=PropiedadesState.prev_page,
                            disabled=PropiedadesState.current_page == 1,
                            variant="soft",
                            size="3",
                        ),
                        rx.vstack(
                            rx.text(
                                f"Página {PropiedadesState.current_page}",
                                size="3",
                                weight="medium",
                            ),
                            rx.text(
                                f"Mostrando {(PropiedadesState.current_page - 1) * PropiedadesState.page_size + 1}-"
                                f"{rx.cond((PropiedadesState.current_page * PropiedadesState.page_size) > PropiedadesState.total_items, PropiedadesState.total_items, (PropiedadesState.current_page * PropiedadesState.page_size))} "
                                f"de {PropiedadesState.total_items}",
                                size="1",
                                color="var(--gray-10)",
                            ),
                            spacing="0",
                            align="center",
                        ),
                        rx.button(
                            "Siguiente",
                            rx.icon("chevron-right", size=16),
                            on_click=PropiedadesState.next_page,
                            disabled=(PropiedadesState.current_page * PropiedadesState.page_size) >= PropiedadesState.total_items,
                            variant="soft",
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
                        "background": "var(--color-panel-solid)",
                        "margin_top": "24px",
                    }
                ),

                spacing="6",
                width="100%",
                padding_x=["4", "6"],
                padding_bottom="8",
            ),
            
            # Modal
            modal_propiedad(),
            
            spacing="0",
            width="100%",
         )
        )
    )


# Ruta protegida
@rx.page(route="/propiedades", on_load=[AuthState.require_login, PropiedadesState.on_load])
def propiedades():
    return propiedades_page()
