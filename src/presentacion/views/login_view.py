"""
Vista de Login - Inmobiliaria Velar
Pantalla de autenticacion del sistema.
"""

import flet as ft

from src.aplicacion.servicios import ServicioAutenticacion
from src.infraestructura.persistencia.database import DatabaseManager
from src.presentacion.theme import colors as app_colors


def crear_login_view(page: ft.Page, on_login_success):
    """Crea la vista de login."""

    db_manager = DatabaseManager()
    servicio_auth = ServicioAutenticacion(db_manager)

    # Controles
    txt_usuario = ft.TextField(
        label="Usuario",
        prefix_icon=ft.Icons.PERSON_OUTLINE,
        border_color=app_colors.BORDER_DEFAULT,
        focused_border_color=app_colors.PRIMARY,
        border_radius=8,
        text_size=14,
    )

    txt_password = ft.TextField(
        label="Contraseña",
        prefix_icon=ft.Icons.LOCK_OUTLINE,
        password=True,
        can_reveal_password=True,
        border_color=app_colors.BORDER_DEFAULT,
        focused_border_color=app_colors.PRIMARY,
        border_radius=8,
        text_size=14,
    )

    txt_error = ft.Text("", color=app_colors.ERROR, size=12, visible=False)

    loading = ft.ProgressRing(visible=False, width=30, height=30)

    def handle_login(e):
        """Maneja el evento de login."""
        # Limpiar error anterior
        txt_error.visible = False
        txt_error.value = ""

        # Validar campos
        if not txt_usuario.value or not txt_password.value:
            txt_error.value = "Por favor ingrese usuario y contraseña"
            txt_error.visible = True
            page.update()
            return

        # Mostrar loading
        btn_login.disabled = True
        loading.visible = True
        page.update()

        # Intentar autenticar
        try:
            usuario = servicio_auth.autenticar(txt_usuario.value, txt_password.value)

            if usuario:
                # Login exitoso
                on_login_success(usuario)
            else:
                txt_error.value = "Usuario o contraseña incorrectos"
                txt_error.visible = True

        except Exception as ex:
            import traceback

            traceback.print_exc()
            pass  # print(f"DEBUG: on_login_success type: {type(on_login_success)}") [OpSec Removed]
            txt_error.value = f"Error al iniciar sesión: {str(ex)}"
            txt_error.visible = True

        finally:
            # Ocultar loading
            btn_login.disabled = False
            loading.visible = False
            page.update()

    btn_login = ft.ElevatedButton(
        "Iniciar Sesión",
        icon=ft.Icons.LOGIN,
        bgcolor=app_colors.PRIMARY,
        color=app_colors.TEXT_ON_PRIMARY,
        width=300,
        height=45,
        on_click=handle_login,
    )

    # Card de login
    login_card = ft.Container(
        content=ft.Column(
            [
                # Logo placeholder
                ft.Container(
                    content=ft.Icon(ft.Icons.APARTMENT, size=60, color=app_colors.PRIMARY),
                    alignment=ft.alignment.center,
                    margin=ft.margin.only(bottom=10),
                ),
                # Titulo
                ft.Text(
                    "Inmobiliaria Velar SAS",
                    size=28,
                    weight=ft.FontWeight.BOLD,
                    color=app_colors.TEXT_PRIMARY,
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Text(
                    "Sistema de Gestión Inmobiliario",
                    size=14,
                    color=app_colors.TEXT_SECONDARY,
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Divider(height=30, color=app_colors.BORDER_DEFAULT),
                # Campos
                txt_usuario,
                txt_password,
                # Error
                txt_error,
                # Boton y loading
                ft.Row([btn_login, loading], alignment=ft.MainAxisAlignment.CENTER),
                # Info de credenciales de prueba
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Text(
                                "Credenciales de prueba:",
                                size=11,
                                color=app_colors.TEXT_SECONDARY,
                                weight=ft.FontWeight.BOLD,
                            ),
                            ft.Text(
                                "Usuario: admin | Contraseña: admin123",
                                size=10,
                                color=app_colors.TEXT_SECONDARY,
                            ),
                        ],
                        spacing=2,
                    ),
                    bgcolor=app_colors.SURFACE,
                    border_radius=6,
                    padding=10,
                    margin=ft.margin.only(top=20),
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=15,
        ),
        bgcolor=app_colors.BACKGROUND,
        border_radius=16,
        padding=40,
        width=400,
        shadow=ft.BoxShadow(
            spread_radius=1, blur_radius=20, color="rgba(0, 0, 0, 0.1)", offset=ft.Offset(0, 10)
        ),
    )

    # Contenedor principal centrado
    return ft.Container(
        content=login_card, alignment=ft.alignment.center, expand=True, bgcolor=app_colors.SURFACE
    )
