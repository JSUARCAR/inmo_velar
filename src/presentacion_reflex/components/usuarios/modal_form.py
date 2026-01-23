
import reflex as rx
from src.presentacion_reflex.state.usuarios_state import UsuariosState

def modal_form() -> rx.Component:
    return rx.dialog.root(
        rx.dialog.content(
             rx.dialog.title(
                rx.cond(
                    UsuariosState.is_editing,
                    "Editar Usuario",
                    "Nuevo Usuario",
                )
            ),
            rx.dialog.description(
                "Gestione el acceso y roles del usuario."
            ),
            rx.flex(
                rx.vstack(
                    rx.text("Usuario", weight="bold"),
                    rx.input(
                        placeholder="nombre.apellido",
                        value=UsuariosState.form_data["nombre_usuario"],
                        on_change=lambda val: UsuariosState.set_form_field("nombre_usuario", val),
                        disabled=UsuariosState.is_editing, # No cambiar username al editar
                        width="100%",
                    ),
                    width="100%",
                ),
                rx.vstack(
                    rx.text("Contraseña", weight="bold"),
                    rx.input(
                        type="password",
                        placeholder=rx.cond(UsuariosState.is_editing, "(Dejar en blanco para mantener)", "Contraseña segura"),
                        value=UsuariosState.form_data["contrasena"],
                        on_change=lambda val: UsuariosState.set_form_field("contrasena", val),
                        width="100%",
                    ),
                    rx.cond(
                        UsuariosState.is_editing,
                        rx.text("Solo ingrese si desea cambiar la contraseña.", size="1", color="gray"),
                    ),
                    width="100%",
                ),
                rx.vstack(
                    rx.text("Rol", weight="bold"),
                    rx.select.root(
                        rx.select.trigger(width="100%"),
                        rx.select.content(
                             rx.select.group(
                                rx.select.item("Administrador", value="Administrador"),
                                rx.select.item("Asesor", value="Asesor"),
                                rx.select.item("Operativo", value="Operativo"),
                             )
                        ),
                        value=UsuariosState.form_data["rol"],
                        on_change=lambda val: UsuariosState.set_form_field("rol", val),
                    ),
                    width="100%",
                ),
                rx.cond(
                    UsuariosState.is_editing,
                    rx.hstack(
                        rx.text("Estado", weight="bold"),
                        rx.switch(
                            checked=UsuariosState.form_data["estado_usuario"],
                            on_change=lambda val: UsuariosState.set_form_field("estado_usuario", val),
                        ),
                        align="center",
                        spacing="3",
                    )
                ),
                rx.cond(
                    UsuariosState.error_message != "",
                    rx.callout(
                        UsuariosState.error_message,
                        icon="triangle_alert",
                        color_scheme="red",
                        role="alert",
                        width="100%"
                    )
                ),
                direction="column",
                spacing="4",
            ),
            rx.flex(
                rx.dialog.close(
                    rx.button("Cancelar", variant="soft", color_scheme="gray"),
                ),
                rx.button(
                    "Guardar", 
                    on_click=UsuariosState.save_user,
                    loading=UsuariosState.is_loading
                ),
                spacing="3",
                margin_top="16px",
                justify="end",
            ),
        ),
        open=UsuariosState.show_form_modal,
        on_open_change=UsuariosState.handle_form_open_change,
    )
