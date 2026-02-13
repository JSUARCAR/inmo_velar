"""
Componente Shell - Arquitectura de Navegación Optimizada
Mantiene Sidebar y Navbar estáticos, solo actualiza el área de contenido.
Adaptado a Flet moderno (sin UserControl).
"""

import reflex as rx


class Shell(ft.Row):
    """
    Shell de la aplicación que preserva componentes estáticos.
    Hereda de Row para definir su layout principal.
    """

    def __init__(self, sidebar: ft.Control, navbar: ft.Control):
        super().__init__()
        self.sidebar = sidebar
        self.navbar = navbar

        # Configuración del Row principal
        self.spacing = 0
        self.expand = True

        # Contenedor dinámico
        self.content_area = ft.Container(expand=True, bgcolor=ft.Colors.TRANSPARENT)

        # Estructura visual: Sidebar + (Navbar / Content)
        self.controls = [
            self.sidebar,
            ft.Column([self.navbar, self.content_area], spacing=0, expand=True),
        ]

    def update_content(self, new_content: ft.Control):
        """Actualiza SOLO el área de contenido."""
        self.content_area.content = new_content
        self.content_area.update()

    def update_navbar(self, new_navbar: ft.Control):
        """Actualiza el Navbar."""
        # En esta estructura, navbar es controls[1].controls[0]
        # Pero mejor actualizamos la referencia y repintamos
        columna_derecha = self.controls[1]
        columna_derecha.controls[0] = new_navbar
        self.navbar = new_navbar
        columna_derecha.update()
