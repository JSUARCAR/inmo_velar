import reflex as rx

from src.presentacion_reflex.state.usuarios_state import UsuariosState
from src.presentacion_reflex.components.neuro_elements import (
    neuro_floating_input,
    neuro_floating_select,
    neuro_button,
)
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
            rx.dialog.description(
                "Gestione el acceso y roles del usuario.", color=styles.TEXT_SECONDARY
            ),
            rx.flex(
                neuro_floating_input(
                    label="Usuario",
                    value=UsuariosState.form_data["nombre_usuario"],
                    on_change=lambda val: UsuariosState.set_form_field(
                        "nombre_usuario", val
                    ),
                    disabled=UsuariosState.is_editing,
                    width="100%",
                ),
                rx.vstack(
                    neuro_floating_input(
                        label="Contraseña",
                        type="password",
                        value=UsuariosState.form_data["contrasena"],
                        on_change=lambda val: UsuariosState.set_form_field(
                            "contrasena", val
                        ),
                        width="100%",
                    ),
                    rx.cond(
                        UsuariosState.is_editing,
                        rx.text(
                            "Solo ingrese si desea cambiar la contraseña.",
                            size="1",
                            color=styles.TEXT_TERTIARY,
                        ),
                    ),
                    width="100%",
                    spacing="1",
                ),
                neuro_floating_select(
                    label="Rol",
                    value=UsuariosState.form_data["rol"],
                    options=[
                        {"label": "Administrador", "value": "Administrador"},
                        {"label": "Asesor", "value": "Asesor"},
                        {"label": "Operativo", "value": "Operativo"},
                    ],
                    on_change=lambda val: UsuariosState.set_form_field("rol", val),
                    placeholder="Seleccionar Rol",
                    width="100%",
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
                        icon="triangle-alert",
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
                    neuro_button("Cancelar", size="2", tooltip_content="Cerrar sin guardar"),
                ),
                neuro_button(
                    "Guardar",
                    on_click=UsuariosState.save_user,
                    size="2",
                    tooltip_content="Guardar cambios",
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
