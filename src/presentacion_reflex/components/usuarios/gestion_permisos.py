"""
Componente de Gestión de Permisos por Rol
"""

import reflex as rx
from typing import Dict, List, Any
from src.presentacion_reflex.state.usuarios_state import UsuariosState


def permission_checkbox_row(permiso: Any) -> rx.Component:
    """Renderiza una fila con checkbox para un permiso individual."""
    return rx.box(
        rx.checkbox(
            permiso.accion,
            checked=UsuariosState.role_permissions_ids.contains(permiso.id_permiso),
            on_change=lambda _: UsuariosState.toggle_permission(permiso.id_permiso),
            size="2",
        ),
        padding="4px 8px",
    )


def module_permissions_table(module_data: Any) -> rx.Component:
    """Tabla de permisos para un módulo específico."""
    
    # module_data es objeto PermissionModule
    modulo = module_data.name
    permisos = module_data.permissions
    
    # Encontrar permisos por acción - iterar sobre la lista de permisos
    # Nota: Como es Var en tiempo de ejecución, usamos condicionales o mapeo en backend
    # Pero aquí necesitamos representarlo visualmente.
    # Dado que "permisos" es una lista, podemos iterar con foreach para ponerlos en orden
    # O, mejor, como sabemos que son 4 acciones fijas, podemos intentar buscarlas.
    # El problema es que "permisos" es una lista y necesitamos extraer items específicos.
    
    # Solución simplificada: Mostrar todos los permisos del módulo en una fila horizontal
    return rx.table.row(
        rx.table.cell(
            rx.flex(
                rx.text(modulo, weight="medium", size="2"),
                rx.icon_button(
                    rx.icon("check-check", size=14),
                    size="1",
                    variant="ghost",
                    on_click=UsuariosState.toggle_all_module_permissions(modulo),
                    tooltip="Seleccionar/Deseleccionar todos",
                ),
                gap="2",
                align="center",
            ),
            width="200px"
        ),
        # Iterar sobre los permisos de este módulo para mostrarlos
        # Esto asumirá que vienen en orden o simplemente los mostrará todos
        rx.table.cell(
            rx.flex(
                rx.foreach(
                    permisos,
                    lambda p: permission_checkbox_row(p)
                ),
                gap="4",
            ),
            col_span=4 
        )
    )


def category_permissions_section(category_data: Any) -> rx.Component:
    """Sección de permisos por categoría."""
    
    # category_data es objeto PermissionCategory
    return rx.box(
        rx.heading(category_data.category, size="4", margin_bottom="12px"),
        
        rx.table.root(
            rx.table.header(
                rx.table.row(
                    rx.table.column_header_cell("Módulo", width="200px"),
                    rx.table.column_header_cell("Acciones Disponibles"),
                ),
            ),
            rx.table.body(
                rx.foreach(
                    category_data.modules,
                    lambda m: module_permissions_table(m),
                ),
            ),
            variant="surface",
            size="2",
        ),
        margin_bottom="24px",
    )


def preset_buttons() -> rx.Component:
    """Botones de presets rápidos."""
    return rx.flex(
        rx.text("Presets Rápidos:", size="2", weight="medium"),
        rx.button(
            "Asesor Típico",
            size="1",
            variant="soft",
            color_scheme="blue",
            on_click=UsuariosState.apply_preset("asesor"),
        ),
        rx.button(
            "Operativo Típico",
            size="1",
            variant="soft",
            color_scheme="green",
            on_click=UsuariosState.apply_preset("operativo"),
        ),
        rx.button(
            "Solo Lectura",
            size="1",
            variant="soft",
            color_scheme="gray",
            on_click=UsuariosState.apply_preset("solo_lectura"),
        ),
        gap="2",
        align="center",
        wrap="wrap",
    )


def gestion_permisos_modal() -> rx.Component:
    """Modal principal de gestión de permisos."""
    
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title(
                rx.flex(
                    rx.icon("shield-check", size=20),
                    rx.text(f"Gestionar Permisos: {UsuariosState.selected_role_for_permissions}"),
                    gap="2",
                    align="center",
                ),
            ),
            
            rx.dialog.description(
                "Selecciona los permisos que este rol tendrá en el sistema. El rol Administrador siempre tiene acceso total.",
                size="2",
                margin_bottom="16px",
            ),
            
            # Presets
            preset_buttons(),
            
            rx.divider(margin="16px 0"),
            
            # Contenido scrolleable
            rx.scroll_area(
                rx.cond(
                    UsuariosState.is_loading_permissions,
                    rx.flex(
                        rx.spinner(size="3"),
                        rx.text("Cargando permisos...", size="2"),
                        direction="column",
                        align="center",
                        gap="2",
                        padding="32px",
                    ),
                    rx.box(
                        # Permisos por jerarquía
                        rx.foreach(
                            UsuariosState.permissions_hierarchy,
                            lambda item: category_permissions_section(item),
                        ),
                        padding="8px 0",
                    ),
                ),
                max_height="500px",
                scrollbars="vertical",
            ),
            
            # Error message
            rx.cond(
                UsuariosState.permissions_error != "",
                rx.callout(
                    UsuariosState.permissions_error,
                    icon="triangle_alert",
                    color_scheme="red",
                    margin_top="12px",
                ),
            ),
            
            # Botones de acción
            rx.flex(
                rx.dialog.close(
                    rx.button(
                        "Cancelar",
                        variant="soft",
                        color_scheme="gray",
                        on_click=UsuariosState.close_permissions_modal,
                    ),
                ),
                rx.button(
                    rx.cond(
                        UsuariosState.is_loading_permissions,
                        rx.spinner(size="2"),
                        rx.text("Guardar Cambios"),
                    ),
                    on_click=UsuariosState.save_permissions,
                    disabled=UsuariosState.is_loading_permissions,
                ),
                gap="3",
                margin_top="16px",
                justify="end",
            ),
            
            max_width="900px",
            padding="24px",
        ),
        
        open=UsuariosState.show_permissions_modal,
        on_open_change=UsuariosState.close_permissions_modal,
    )
