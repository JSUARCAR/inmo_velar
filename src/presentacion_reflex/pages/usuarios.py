
import reflex as rx
from src.presentacion_reflex.components.layout.dashboard_layout import dashboard_layout
from src.presentacion_reflex.state.usuarios_state import UsuariosState
from src.presentacion_reflex.components.usuarios import modal_form
from src.presentacion_reflex.components.usuarios.gestion_permisos import gestion_permisos_modal
from src.presentacion_reflex.state.auth_state import AuthState

def filtros_bar() -> rx.Component:
    return rx.flex(
        rx.input(
            placeholder="Buscar usuario...",
            on_change=UsuariosState.set_search,
            width="300px",
            icon="search",
        ),
        rx.select.root(
            rx.select.trigger(placeholder="Rol"),
            rx.select.content(
                rx.select.group(
                    rx.select.item("Todos", value="Todos"),
                    rx.select.item("Administrador", value="Administrador"),
                    rx.select.item("Asesor", value="Asesor"),
                    rx.select.item("Operativo", value="Operativo"),
                )
            ),
            value=UsuariosState.filter_role,
            on_change=lambda val: UsuariosState.set_filter_role(val)
        ),
        rx.select.root(
            rx.select.trigger(placeholder="Estado"),
            rx.select.content(
                rx.select.group(
                    rx.select.item("Todos", value="Todos"),
                    rx.select.item("Activo", value="Activo"),
                    rx.select.item("Inactivo", value="Inactivo"),
                )
            ),
            value=UsuariosState.filter_status,
            on_change=lambda val: UsuariosState.set_filter_status(val)
        ),
        rx.spacer(),
        rx.cond(
            AuthState.check_action("Usuarios", "CREAR"),
            rx.button(
                rx.icon("user_plus"),
                "Nuevo Usuario",
                on_click=UsuariosState.open_create_modal,
            )
        ),
        width="100%",
        gap="3",
        align="center",
        wrap="wrap",
        padding_bottom="4",
    )

def usuarios_table() -> rx.Component:
    return rx.table.root(
        rx.table.header(
            rx.table.row(
                rx.table.column_header_cell("Usuario"),
                rx.table.column_header_cell("Rol"),
                rx.table.column_header_cell("Estado"),
                rx.table.column_header_cell("Último Acceso"),
                rx.table.column_header_cell("Acciones", text_align="right"),
            )
        ),
        rx.table.body(
            rx.foreach(
                UsuariosState.usuarios,
                lambda u: rx.table.row(
                    rx.table.cell(u["nombre_usuario"], font_weight="bold"),
                    rx.table.cell(
                        rx.badge(u["rol"], variant="soft", color_scheme="blue")
                    ),
                    rx.table.cell(
                        rx.badge(
                            u["estado_label"], 
                            color_scheme=rx.cond(u["estado_usuario"], "green", "gray")
                        )
                    ),
                    rx.table.cell(u["ultimo_acceso"]),
                    rx.table.cell(
                        rx.hstack(
                            rx.cond(
                                AuthState.check_action("Usuarios", "EDITAR"),
                                rx.tooltip(
                                    rx.switch(
                                        checked=u["estado_usuario"],
                                        on_change=lambda val: UsuariosState.toggle_status(u["id_usuario"], u["estado_usuario"]),
                                        color_scheme="green",
                                        style={
                                            "&[data-state='unchecked']": {
                                                "background_color": "#FFA500 !important",
                                                "border": "1px solid #FFA500 !important",
                                            }
                                        },
                                        cursor="pointer",
                                    ),
                                    content="Activar/Desactivar usuario"
                                )
                            ),
                            # Botón de permisos (solo para roles != Administrador)
                            rx.cond(
                                (u["rol"] != "Administrador") & AuthState.check_action("Usuarios", "EDITAR"),
                                rx.tooltip(
                                    rx.icon_button(
                                        rx.icon("shield-check", size=16),
                                        size="2",
                                        variant="ghost",
                                        color_scheme="violet",
                                        on_click=lambda: UsuariosState.open_permissions_modal(u["rol"]),
                                    ),
                                    content="Gestionar permisos del rol"
                                ),
                            ),
                            rx.cond(
                                AuthState.check_action("Usuarios", "EDITAR"),
                                rx.tooltip(
                                    rx.icon_button(
                                        rx.icon("pencil", size=16),
                                        size="2",
                                        variant="ghost",
                                        on_click=lambda: UsuariosState.open_edit_modal(u)
                                    ),
                                    content="Editar usuario"
                                )
                            ),
                            justify="end",
                            spacing="2"
                        ),
                        text_align="right"
                    ),
                )
            )
        ),
        width="100%",
        variant="surface",
    )

def usuarios_content() -> rx.Component:
    return rx.vstack(
        rx.heading("Gestión de Usuarios", size="6"),
        rx.text("Administre el acceso y roles del sistema.", color="gray"),
        rx.divider(),
        filtros_bar(),
        rx.cond(
            UsuariosState.is_loading,
            rx.center(rx.spinner()),
            usuarios_table(),
        ),
        modal_form(),
        gestion_permisos_modal(),  # Modal de gestión de permisos
        spacing="5",
        padding="6",
        width="100%",
        align="stretch"
    )

@rx.page(route="/usuarios", title="Usuarios | Inmobiliaria Velar", on_load=UsuariosState.load_users)
def usuarios_page() -> rx.Component:
    return dashboard_layout(usuarios_content())
