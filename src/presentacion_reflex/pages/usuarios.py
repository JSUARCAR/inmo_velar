import reflex as rx

from src.presentacion_reflex.components.layout.dashboard_layout import dashboard_layout
from src.presentacion_reflex.components.usuarios import modal_form
from src.presentacion_reflex.components.usuarios.gestion_permisos import gestion_permisos_modal
from src.presentacion_reflex.state.auth_state import AuthState
from src.presentacion_reflex.state.usuarios_state import UsuariosState


def filtros_bar() -> rx.Component:
    return rx.flex(
        rx.input(
            placeholder="Buscar usuario...",
            on_change=UsuariosState.set_search,
            width=["100%", "300px"],
            icon="search",
        ),
        rx.flex(
            rx.select.root(
                rx.select.trigger(placeholder="Rol", width=["100%", "auto"]),
                rx.select.content(
                    rx.select.group(
                        rx.select.item("Todos", value="Todos"),
                        rx.select.item("Administrador", value="Administrador"),
                        rx.select.item("Asesor", value="Asesor"),
                        rx.select.item("Operativo", value="Operativo"),
                    )
                ),
                value=UsuariosState.filter_role,
                on_change=lambda val: UsuariosState.set_filter_role(val),
                width=["100%", "auto"],
            ),
            rx.select.root(
                rx.select.trigger(placeholder="Estado", width=["100%", "auto"]),
                rx.select.content(
                    rx.select.group(
                        rx.select.item("Todos", value="Todos"),
                        rx.select.item("Activo", value="Activo"),
                        rx.select.item("Inactivo", value="Inactivo"),
                    )
                ),
                value=UsuariosState.filter_status,
                on_change=lambda val: UsuariosState.set_filter_status(val),
                width=["100%", "auto"],
            ),
            spacing="3",
            width=["100%", "auto"],
            flex_direction=["column", "row"],
        ),
        rx.spacer(),
        rx.cond(
            AuthState.check_action("Usuarios", "CREAR"),
            rx.button(
                rx.icon("user_plus"),
                "Nuevo Usuario",
                on_click=UsuariosState.open_create_modal,
                width=["100%", "auto"],
            ),
        ),
        width="100%",
        gap="3",
        align="center",
        wrap="wrap",
        padding_bottom="4",
        flex_direction=["column", "row"],
    )


def usuario_card(u: dict) -> rx.Component:
    """Card individual para vista móvil de usuarios."""
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.avatar(fallback=u["nombre_usuario"][:2].upper(), radius="full", size="3"),
                rx.vstack(
                    rx.text(u["nombre_usuario"], weight="bold", size="3"),
                    rx.badge(u["rol"], variant="soft", color_scheme="blue"),
                    spacing="1",
                ),
                rx.spacer(),
                rx.badge(
                    u["estado_label"],
                    color_scheme=rx.cond(u["estado_usuario"], "green", "gray"),
                ),
                width="100%",
                align="center",
            ),
            rx.divider(),
            rx.hstack(
                rx.text("Último acceso:", size="1", color="gray"),
                rx.text(u["ultimo_acceso"], size="1"),
                justify="between",
                width="100%",
            ),
            rx.hstack(
                rx.cond(
                    AuthState.check_action("Usuarios", "EDITAR"),
                    rx.hstack(
                        rx.text("Estado:", size="2", weight="medium"),
                        rx.switch(
                            checked=u["estado_usuario"],
                            on_change=lambda val: UsuariosState.toggle_status(
                                u["id_usuario"], u["estado_usuario"]
                            ),
                            color_scheme="green",
                        ),
                        align="center",
                        spacing="2",
                    ),
                ),
                rx.spacer(),
                rx.hstack(
                    rx.cond(
                        (u["rol"] != "Administrador")
                        & AuthState.check_action("Usuarios", "EDITAR"),
                        rx.icon_button(
                            rx.icon("shield-check", size=18),
                            variant="surface",
                            color_scheme="violet",
                            on_click=lambda: UsuariosState.open_permissions_modal(u["rol"]),
                        ),
                    ),
                    rx.cond(
                        AuthState.check_action("Usuarios", "EDITAR"),
                        rx.icon_button(
                            rx.icon("pencil", size=18),
                            variant="surface",
                            on_click=lambda: UsuariosState.open_edit_modal(u),
                        ),
                    ),
                    spacing="2",
                ),
                width="100%",
                align="center",
                padding_top="2",
            ),
            spacing="3",
            width="100%",
        ),
        width="100%",
    )


def usuarios_card_list() -> rx.Component:
    return rx.vstack(
        rx.foreach(UsuariosState.usuarios, usuario_card),
        spacing="3",
        width="100%",
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
                    rx.table.cell(rx.badge(u["rol"], variant="soft", color_scheme="blue")),
                    rx.table.cell(
                        rx.badge(
                            u["estado_label"],
                            color_scheme=rx.cond(u["estado_usuario"], "green", "gray"),
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
                                        on_change=lambda val: UsuariosState.toggle_status(
                                            u["id_usuario"], u["estado_usuario"]
                                        ),
                                        color_scheme="green",
                                        style={
                                            "&[data-state='unchecked']": {
                                                "background_color": "#FFA500 !important",
                                                "border": "1px solid #FFA500 !important",
                                            }
                                        },
                                        cursor="pointer",
                                    ),
                                    content="Activar/Desactivar usuario",
                                ),
                            ),
                            # Botón de permisos (solo para roles != Administrador)
                            rx.cond(
                                (u["rol"] != "Administrador")
                                & AuthState.check_action("Usuarios", "EDITAR"),
                                rx.tooltip(
                                    rx.icon_button(
                                        rx.icon("shield-check", size=16),
                                        size="2",
                                        variant="ghost",
                                        color_scheme="violet",
                                        on_click=lambda: UsuariosState.open_permissions_modal(
                                            u["rol"]
                                        ),
                                    ),
                                    content="Gestionar permisos del rol",
                                ),
                            ),
                            rx.cond(
                                AuthState.check_action("Usuarios", "EDITAR"),
                                rx.tooltip(
                                    rx.icon_button(
                                        rx.icon("pencil", size=16),
                                        size="2",
                                        variant="ghost",
                                        on_click=lambda: UsuariosState.open_edit_modal(u),
                                    ),
                                    content="Editar usuario",
                                ),
                            ),
                            justify="end",
                            spacing="2",
                        ),
                        text_align="right",
                    ),
                ),
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
            rx.box(
                # Desktop View (Table)
                rx.box(
                    usuarios_table(),
                    display=["none", "none", "block", "block", "block"],
                    width="100%",
                ),
                # Mobile View (Cards)
                rx.box(
                    usuarios_card_list(),
                    display=["block", "block", "none", "none", "none"],
                    width="100%",
                ),
                width="100%",
            ),
        ),
        modal_form(),
        gestion_permisos_modal(),  # Modal de gestión de permisos
        spacing="5",
        padding="6",
        width="100%",
        align="stretch",
    )


@rx.page(
    route="/usuarios",
    title="Usuarios | Inmobiliaria Velar",
    on_load=[AuthState.require_login, UsuariosState.load_users],
)
def usuarios_page() -> rx.Component:
    return dashboard_layout(usuarios_content())
