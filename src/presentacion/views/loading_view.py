"""
Loading View: Pantalla de Carga del Sistema
Muestra el progreso de pre-carga de vistas después del login.
"""

import flet as ft
from src.presentacion.theme import colors


class LoadingView(ft.Container):
    """
    Vista de carga que muestra el progreso de inicialización del sistema.
    """
    
    def __init__(self, page: ft.Page):
        """
        Inicializa la vista de carga.
        
        Args:
            page: Página de Flet
        """
        self.page = page
        
        # Componentes de la UI
        self._crear_componentes()
        
        # Inicializar el Container
        super().__init__(
            content=self._contenido_principal,
            expand=True,
            bgcolor=colors.BACKGROUND,
            alignment=ft.alignment.center
        )
    
    def _crear_componentes(self):
        """Crea los componentes visuales de la loading view."""
        
        # Logo/Icono principal
        self.icono = ft.Icon(
            ft.Icons.APARTMENT,
            size=80,
            color=colors.PRIMARY
        )
        
        # Título
        self.titulo = ft.Text(
            "Sistema de Gestión Inmobiliaria",
            size=28,
            weight=ft.FontWeight.BOLD,
            color=colors.TEXT_PRIMARY,
            text_align=ft.TextAlign.CENTER
        )
        
        # Subtítulo
        self.subtitulo = ft.Text(
            "Cargando Sistema...",
            size=16,
            color=colors.TEXT_SECONDARY,
            text_align=ft.TextAlign.CENTER
        )
        
        # Barra de progreso
        self.progress_bar = ft.ProgressBar(
            width=400,
            height=8,
            value=0,
            color=colors.PRIMARY,
            bgcolor=colors.SURFACE,
            border_radius=4
        )
        
        # Texto de porcentaje
        self.texto_porcentaje = ft.Text(
            "0%",
            size=14,
            weight=ft.FontWeight.BOLD,
            color=colors.PRIMARY,
            text_align=ft.TextAlign.CENTER
        )
        
        # Texto de estado (qué se está cargando)
        self.texto_estado = ft.Text(
            "Inicializando...",
            size=13,
            color=colors.TEXT_SECONDARY,
            text_align=ft.TextAlign.CENTER,
            italic=True
        )
        
        # Spinner animado
        self.spinner = ft.ProgressRing(
            width=20,
            height=20,
            stroke_width=2,
            color=colors.PRIMARY
        )
        
        # Contenedor de progreso
        contenedor_progreso = ft.Container(
            content=ft.Column(
                [
                    self.progress_bar,
                    ft.Container(height=8),
                    self.texto_porcentaje,
                    ft.Container(height=16),
                    ft.Row(
                        [
                            self.spinner,
                            ft.Container(width=8),
                            self.texto_estado
                        ],
                        alignment=ft.MainAxisAlignment.CENTER
                    )
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=0
            ),
            width=400,
            padding=20,
            bgcolor=colors.SURFACE,
            border_radius=12,
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=10,
                color=ft.Colors.with_opacity(0.1, ft.Colors.BLACK),
                offset=ft.Offset(0, 4)
            )
        )
        
        # Contenido principal
        self._contenido_principal = ft.Column(
            [
                self.icono,
                ft.Container(height=24),
                self.titulo,
                ft.Container(height=8),
                self.subtitulo,
                ft.Container(height=40),
                contenedor_progreso
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=0
        )
    
    def actualizar_progreso(self, porcentaje: int, mensaje: str):
        """
        Actualiza la barra de progreso y el mensaje de estado.
        
        Args:
            porcentaje: Porcentaje de progreso (0-100)
            mensaje: Mensaje descriptivo del estado actual
        """
        # Validar porcentaje
        porcentaje = max(0, min(100, porcentaje))
        
        # Actualizar componentes
        self.progress_bar.value = porcentaje / 100
        self.texto_porcentaje.value = f"{porcentaje}%"
        self.texto_estado.value = mensaje
        
        # Si llegó al 100%, cambiar el ícono del spinner por un check
        if porcentaje >= 100:
            self.spinner.visible = False
            self.subtitulo.value = "¡Sistema Listo!"
            self.subtitulo.color = colors.SUCCESS
        
        # Actualizar la vista
        self.update()


def crear_loading_view(page: ft.Page) -> LoadingView:
    """
    Factory function para crear la vista de carga.
    
    Args:
        page: Página de Flet
        
    Returns:
        Instancia de LoadingView
    """
    return LoadingView(page)
