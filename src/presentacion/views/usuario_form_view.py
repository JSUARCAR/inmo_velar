"""
Vista de Formulario de Usuario.
Formulario para crear y editar usuarios del sistema.
"""

from typing import Callable, Optional

import reflex as rx

from src.dominio.entidades.usuario import Usuario


def build_usuario_form_view(
    page: ft.Page,
    servicio_configuracion,
    usuario_actual: Usuario,
    on_guardar: Callable,
    on_cancelar: Callable,
    usuario_editar: Optional[Usuario] = None,
) -> ft.Control:
    """
    Construye el formulario para crear o editar un usuario.

    Args:
        page: Página de Flet
        servicio_configuracion: Instancia del ServicioConfiguracion
        usuario_actual: Usuario logueado
        on_guardar: Callback al guardar exitosamente
        on_cancelar: Callback al cancelar
        usuario_editar: Usuario a editar (None para creación)

    Returns:
        Control de Flet con el formulario
    """

    es_edicion = usuario_editar is not None
    titulo = "Editar Usuario" if es_edicion else "Nuevo Usuario"

    # ========================================
    # CAMPOS DEL FORMULARIO
    # ========================================

    txt_nombre_usuario = ft.TextField(
        label="Nombre de Usuario *",
        value=usuario_editar.nombre_usuario if es_edicion else "",
        max_length=50,
        width=400,
        prefix_icon=ft.Icons.PERSON,
        disabled=es_edicion,  # No se puede cambiar el username
        helper_text="El nombre de usuario no se puede modificar" if es_edicion else None,
    )

    txt_contrasena = ft.TextField(
        label="Contraseña *",
        password=True,
        can_reveal_password=True,
        max_length=100,
        width=400,
        prefix_icon=ft.Icons.LOCK,
        visible=not es_edicion,  # Solo visible en creación
        helper_text="Mínimo 6 caracteres",
    )

    txt_confirmar_contrasena = ft.TextField(
        label="Confirmar Contraseña *",
        password=True,
        can_reveal_password=True,
        max_length=100,
        width=400,
        prefix_icon=ft.Icons.LOCK_OUTLINE,
        visible=not es_edicion,  # Solo visible en creación
    )

    dd_rol = ft.Dropdown(
        label="Rol *",
        width=400,
        options=[
            ft.dropdown.Option("Administrador"),
            ft.dropdown.Option("Asesor"),
        ],
        value=usuario_editar.rol if es_edicion else None,
        prefix_icon=ft.Icons.BADGE,
    )

    # ========================================
    # VALIDACIÓN Y GUARDADO
    # ========================================

    txt_error = ft.Text("", color=ft.Colors.RED, size=14, visible=False)

    def validar_formulario() -> Optional[str]:
        """Valida el formulario y retorna mensaje de error o None si es válido."""
        if not txt_nombre_usuario.value or len(txt_nombre_usuario.value.strip()) < 3:
            return "El nombre de usuario debe tener al menos 3 caracteres"

        if not es_edicion:
            if not txt_contrasena.value or len(txt_contrasena.value) < 6:
                return "La contraseña debe tener al menos 6 caracteres"

            if txt_contrasena.value != txt_confirmar_contrasena.value:
                return "Las contraseñas no coinciden"

        if not dd_rol.value:
            return "Debe seleccionar un rol"

        return None

    def handle_guardar(e):
        """Maneja el evento de guardar."""
        error = validar_formulario()
        if error:
            txt_error.value = error
            txt_error.visible = True
            page.update()
            return

        try:
            if es_edicion:
                # Actualizar usuario existente (solo rol)
                servicio_configuracion.actualizar_usuario(
                    id_usuario=usuario_editar.id_usuario,
                    rol=dd_rol.value,
                    usuario_sistema=usuario_actual.nombre_usuario,
                )
                page.snack_bar = ft.SnackBar(
                    ft.Text("Usuario actualizado correctamente"), bgcolor=ft.Colors.GREEN
                )
            else:
                # Crear nuevo usuario
                servicio_configuracion.crear_usuario(
                    nombre_usuario=txt_nombre_usuario.value.strip(),
                    contrasena=txt_contrasena.value,
                    rol=dd_rol.value,
                    usuario_sistema=usuario_actual.nombre_usuario,
                )
                page.snack_bar = ft.SnackBar(
                    ft.Text("Usuario creado correctamente"), bgcolor=ft.Colors.GREEN
                )

            page.snack_bar.open = True
            page.update()
            on_guardar()

        except ValueError as ex:
            txt_error.value = str(ex)
            txt_error.visible = True
            page.update()
        except Exception as ex:
            txt_error.value = f"Error inesperado: {ex}"
            txt_error.visible = True
            page.update()

    def handle_cancelar(e):
        """Maneja el evento de cancelar."""
        on_cancelar()

    # ========================================
    # CONSTRUCCIÓN DEL FORMULARIO
    # ========================================

    return ft.Container(
        padding=20,
        content=ft.Column(
            [
                # Título
                ft.Row(
                    [
                        ft.IconButton(
                            icon=ft.Icons.ARROW_BACK,
                            on_click=handle_cancelar,
                            tooltip="Volver",
                        ),
                        ft.Icon(
                            ft.Icons.PERSON_ADD if not es_edicion else ft.Icons.EDIT,
                            size=32,
                            color=ft.Colors.BLUE,
                        ),
                        ft.Text(titulo, size=28, weight=ft.FontWeight.BOLD),
                    ]
                ),
                ft.Divider(),
                # Contenedor del formulario
                ft.Container(
                    content=ft.Card(
                        content=ft.Container(
                            padding=30,
                            content=ft.Column(
                                [
                                    ft.Text(
                                        "Información del Usuario",
                                        size=18,
                                        weight=ft.FontWeight.BOLD,
                                        color=ft.Colors.BLUE_700,
                                    ),
                                    ft.Divider(height=20),
                                    # Campos
                                    txt_nombre_usuario,
                                    ft.Container(height=10),
                                    txt_contrasena,
                                    ft.Container(height=10),
                                    txt_confirmar_contrasena,
                                    ft.Container(height=10),
                                    dd_rol,
                                    # Mensaje de error
                                    ft.Container(
                                        content=txt_error,
                                        margin=ft.margin.only(top=15),
                                    ),
                                    # Botones
                                    ft.Container(height=20),
                                    ft.Row(
                                        [
                                            ft.ElevatedButton(
                                                text="Cancelar",
                                                icon=ft.Icons.CANCEL,
                                                on_click=handle_cancelar,
                                            ),
                                            ft.ElevatedButton(
                                                text="Guardar",
                                                icon=ft.Icons.SAVE,
                                                bgcolor=ft.Colors.BLUE,
                                                color=ft.Colors.WHITE,
                                                on_click=handle_guardar,
                                            ),
                                        ],
                                        alignment=ft.MainAxisAlignment.END,
                                    ),
                                ]
                            ),
                        ),
                    ),
                    width=500,
                ),
            ]
        ),
    )
