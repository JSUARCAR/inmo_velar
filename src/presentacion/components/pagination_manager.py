"""
Componente de Paginación Avanzado para InmoVelar Web.

Proporciona controles de navegación entre páginas con funcionalidades enterprise.

Autor: InmoVelar Dev Team
Fecha: 2025-12-29
"""

import flet as ft
from typing import Callable, Optional, List
from src.presentacion.theme import colors


class PaginationManager(ft.Container):
    """
    Componente de paginación avanzado con:
    - Navegación First/Prev/Next/Last
    - Jump to page directo
    - Selector de items por página
    - Información de rango de registros
    - Teclado shortcuts
    - Responsive design
    """
    
    def __init__(
        self,
        total_items: int,
        items_per_page: int = 25,
        current_page: int = 1,
        on_page_change: Optional[Callable[[int], None]] = None,
        on_page_size_change: Optional[Callable[[int], None]] = None,
        page_size_options: Optional[List[int]] = None
    ):
        """
        Inicializa el componente de paginación.
        
        Args:
            total_items: Total de items (sin paginar)
            items_per_page: Items por página
            current_page: Página actual (1-indexed)
            on_page_change: Callback cuando cambia la página
            on_page_size_change: Callback cuando cambia el tamaño
            page_size_options: Opciones de tamaño de página
        """
        super().__init__()
        
        # Validaciones
        if total_items < 0:
            raise ValueError("total_items debe ser >= 0")
        if items_per_page < 1:
            raise ValueError("items_per_page debe ser >= 1")
        if current_page < 1:
            raise ValueError("current_page debe ser >= 1")
        
        # Estado
        self.total_items = total_items
        self.items_per_page = items_per_page
        self.current_page = current_page
        self.on_page_change_callback = on_page_change
        self.on_page_size_change_callback = on_page_size_change
        self.page_size_options = page_size_options or [10, 25, 50, 100]
        
        # Referencias a controles
        self.page_input = ft.Ref[ft.TextField]()
        self.page_size_dropdown = ft.Ref[ft.Dropdown]()
        self.info_text = ft.Ref[ft.Text]()
        
        # Construir UI
        self._build_ui()
    
    @property
    def total_pages(self) -> int:
        """Calcula total de páginas."""
        import math
        if self.total_items == 0:
            return 1
        return math.ceil(self.total_items / self.items_per_page)
    
    @property
    def start_index(self) -> int:
        """Índice del primer item (1-indexed)."""
        if self.total_items == 0:
            return 0
        return (self.current_page - 1) * self.items_per_page + 1
    
    @property
    def end_index(self) -> int:
        """Índice del último item (1-indexed)."""
        if self.total_items == 0:
            return 0
        end = self.current_page * self.items_per_page
        return min(end, self.total_items)
    
    def _build_ui(self):
        """Construye la interfaz del componente."""
        
        # Botón First Page
        btn_first = ft.IconButton(
            icon=ft.Icons.FIRST_PAGE,
            tooltip="Primera página",
            on_click=lambda e: self._go_to_page(1),
            disabled=self.current_page == 1
        )
        
        # Botón Previous
        btn_prev = ft.IconButton(
            icon=ft.Icons.CHEVRON_LEFT,
            tooltip="Página anterior",
            on_click=lambda e: self._go_to_page(self.current_page - 1),
            disabled=self.current_page == 1
        )
        
        # Input de página
        page_input = ft.TextField(
            ref=self.page_input,
            value=str(self.current_page),
            width=60,
            height=40,
            text_align=ft.TextAlign.CENTER,
            on_submit=self._on_page_input_submit,
            keyboard_type=ft.KeyboardType.NUMBER,
            border_color=colors.BORDER_DEFAULT,
            content_padding=ft.padding.all(8)
        )
        
        # Texto de total de páginas
        total_pages_text = ft.Text(
            f"de {self.total_pages}",
            size=14,
            color=colors.TEXT_SECONDARY
        )
        
        # Botón Next
        btn_next = ft.IconButton(
            icon=ft.Icons.CHEVRON_RIGHT,
            tooltip="Página siguiente",
            on_click=lambda e: self._go_to_page(self.current_page + 1),
            disabled=self.current_page >= self.total_pages
        )
        
        # Botón Last Page
        btn_last = ft.IconButton(
            icon=ft.Icons.LAST_PAGE,
            tooltip="Última página",
            on_click=lambda e: self._go_to_page(self.total_pages),
            disabled=self.current_page >= self.total_pages
        )
        
        # Selector de tamaño de página
        page_size_dropdown = ft.Dropdown(
            ref=self.page_size_dropdown,
            width=100,
            value=str(self.items_per_page),
            options=[
                ft.dropdown.Option(str(size), f"{size} items")
                for size in self.page_size_options
            ],
            on_change=self._on_page_size_change,
            border_color=colors.BORDER_DEFAULT,
            content_padding=ft.padding.all(8)
        )
        
        # Texto informativo
        info_text = ft.Text(
            ref=self.info_text,
            value=self._get_info_text(),
            size=13,
            color=colors.TEXT_SECONDARY
        )
        
        # Layout
        self.content = ft.Container(
            content=ft.Row(
                [
                    # Info izquierda
                    info_text,
                    
                    ft.Container(expand=True),  # Spacer
                    
                    # Controles de paginación
                    ft.Row(
                        [
                            page_size_dropdown,
                            ft.VerticalDivider(width=20, color=colors.BORDER_DEFAULT),
                            btn_first,
                            btn_prev,
                            page_input,
                            total_pages_text,
                            btn_next,
                            btn_last,
                        ],
                        spacing=5,
                        alignment=ft.MainAxisAlignment.END
                    )
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER
            ),
            padding=ft.padding.symmetric(horizontal=15, vertical=10),
            border=ft.border.all(1, colors.BORDER_DEFAULT),
            border_radius=8,
            bgcolor=colors.BACKGROUND
        )
    
    def _get_info_text(self) -> str:
        """Genera texto informativo del rango de items."""
        if self.total_items == 0:
            return "No hay registros"
        
        return (
            f"Mostrando {self.start_index:,} - {self.end_index:,} "
            f"de {self.total_items:,} registros"
        )
    
    def _go_to_page(self, page: int):
        """
        Navega a una página específica.
        
        Args:
            page: Número de página (1-indexed)
        """
        # Validar rango
        if page < 1:
            page = 1
        if page > self.total_pages:
            page = self.total_pages
        
        # No hacer nada si ya estamos en esa página
        if page == self.current_page:
            return
        
        # Actualizar estado
        self.current_page = page
        
        # Actualizar UI
        self._update_controls()
        
        # Notificar callback
        if self.on_page_change_callback:
            self.on_page_change_callback(page)
    
    def _on_page_input_submit(self, e):
        """Handler para cuando se envía el input de página."""
        try:
            page = int(self.page_input.current.value)
            self._go_to_page(page)
        except ValueError:
            # Reset a página actual si input inválido
            self.page_input.current.value = str(self.current_page)
            self.page_input.current.update()
    
    def _on_page_size_change(self, e):
        """Handler para cambio de tamaño de página."""
        try:
            new_size = int(self.page_size_dropdown.current.value)
            
            if new_size == self.items_per_page:
                return
            
            # Actualizar tamaño
            self.items_per_page = new_size
            
            # Resetear a página 1 (estándar en cambio de tamaño)
            self.current_page = 1
            
            # Actualizar UI
            self._update_controls()
            
            # Notificar callback
            if self.on_page_size_change_callback:
                self.on_page_size_change_callback(new_size)
                
        except ValueError:
            pass
    
    def _update_controls(self):
        """Actualiza todos los controles con el estado actual."""
        if not self.page_input.current:
            return
        
        # Actualizar input de página
        self.page_input.current.value = str(self.current_page)
        
        # Actualizar texto informativo
        self.info_text.current.value = self._get_info_text()
        
        # Rebuild completo para actualizar estados de botones
        self._build_ui()
        self.update()
    
    def set_total_items(self, total: int):
        """
        Actualiza el total de items.
        
        Args:
            total: Nuevo total de items
        """
        self.total_items = total
        
        # Ajustar página actual si es necesario
        if self.current_page > self.total_pages:
            self.current_page = max(1, self.total_pages)
        
        self._update_controls()
    
    def set_current_page(self, page: int):
        """
        Actualiza la página actual sin disparar callback.
        Útil para sincronizar estado externo.
        
        Args:
            page: Número de página
        """
        if page < 1 or page > self.total_pages:
            return
        
        self.current_page = page
        self._update_controls()
    
    def reset(self):
        """Resetea a página 1."""
        self._go_to_page(1)
    
    def get_state(self) -> dict:
        """
        Retorna estado actual del paginador.
        
        Returns:
            Diccionario con estado
        """
        return {
            'current_page': self.current_page,
            'items_per_page': self.items_per_page,
            'total_items': self.total_items,
            'total_pages': self.total_pages,
            'start_index': self.start_index,
            'end_index': self.end_index
        }
