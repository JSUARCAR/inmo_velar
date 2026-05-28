import reflex as rx

from src.presentacion_reflex.state.usuarios_state import UsuariosState
from src.presentacion_reflex.components.neuro_elements import neuro_input, neuro_button, neuro_select_root
from src.presentacion_reflex import styles


def modal_form() -> rx.Component:
    """Modal form para crear/editar usuarios."""
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title(
                rx.cond(
                    UsuariosState.is_editing,
                    "Editar Usuario",
                    "Nuevo Usuario",
                ),
                color=styles.TEXT_PRIMARY,
            ),
            rx.dialog.description("Gestione el acceso y roles del usuario.", color=styles.TEXT_SECONDARY),
            rx.flex(
                rx.vstack(
                    rx.text("Usuario", weight="bold", color=styles.TEXT_PRIMARY),
                    neuro_input(
                        placeholder="nombre.apellido",
                        value=UsuariosState.form_data["nombre_usuario"],
                        on_change=lambda val: UsuariosState.set_form_field("nombre_usuario", val),
                        disabled=UsuariosState.is_editing,  # No cambiar username al editar
                        width="100%",
                    ),
                    width="100%",
                    spacing="1",
                ),
                rx.vstack(
                    rx.text("Contraseña", weight="bold", color=styles.TEXT_PRIMARY),
                    neuro_input(
                        type="password",
                        placeholder=rx.cond(
                            UsuariosState.is_editing,
                            "(Dejar en blanco para mantener)",
                            "Contraseña segura",
                        ),
                        value=UsuariosState.form_data["contrasena"],
                        on_change=lambda val: UsuariosState.set_form_field("contrasena", val),
                        width="100%",
                    ),
                    rx.cond(
                        UsuariosState.is_editing,
                        rx.text(
                            "Solo ingrese si desea cambiar la contraseña.", size="1", color=styles.TEXT_TERTIARY
                        ),
                    ),
                    width="100%",
                    spacing="1",
                ),
                rx.vstack(
                    rx.text("Rol", weight="bold", color=styles.TEXT_PRIMARY),
                    neuro_select_root(
                        [
                            rx.select.item("Administrador", value="Administrador"),
                            rx.select.item("Asesor", value="Asesor"),
                            rx.select.item("Operativo", value="Operativo"),
                        ],
                        value=UsuariosState.form_data["rol"],
                        on_change=lambda val: UsuariosState.set_form_field("rol", val),
                        placeholder="Seleccionar Rol",
                        width="100%",
                    ),
                    width="100%",
                    spacing="1",
                ),
                rx.cond(
                    UsuariosState.is_editing,
                    rx.hstack(
                        rx.text("Estado", weight="bold", color=styles.TEXT_PRIMARY),
                        rx.switch(
                            checked=UsuariosState.form_data["estado_usuario"],
                            on_change=lambda val: UsuariosState.set_form_field(
                                "estado_usuario", val
                            ),
                            color_scheme="green",
                        ),
                        align="center",
                        spacing="3",
                    ),
                ),
                rx.cond(
                    UsuariosState.error_message != "",
                    rx.callout(
                        UsuariosState.error_message,
                        icon="alert-triangle",
                        color_scheme="red",
                        role="alert",
                        width="100%",
                    ),
                ),
                direction="column",
                spacing="4",
            ),
            rx.flex(
                rx.dialog.close(
                    neuro_button("Cancelar", size="2"),
                ),
                neuro_button(
                    "Guardar",
                    on_click=UsuariosState.save_user,
                    size="2",
                ),
                padding_top="4",
                justify="end",
                gap="3",
            ),
            max_width="450px",
            background=styles.BG_PANEL,
            style={"border_radius": "16px", "box_shadow": styles.NEU_SHADOW},
        ),
        open=UsuariosState.show_form_modal,
        on_open_change=lambda _: UsuariosState.close_modal(),
    )
