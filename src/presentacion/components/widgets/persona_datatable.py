"""
Componente: DataTable de Personas
Tabla optimizada para listar personas con acciones inline.
"""

import flet as ft
from typing import List, Callable, Optional
from src.presentacion.theme import colors
from src.presentacion.components.widgets.role_badge import RoleBadge
from src.aplicacion.servicios import PersonaConRoles


class PersonaDataTable(ft.Column):
    """
    DataTable para mostrar personas con sus roles y acciones.
    
    Args:
        personas: Lista de PersonaConRoles a mostrar
        on_edit: Callback al hacer clic en Editar (recibe id_persona)
        on_toggle_estado: Callback al cambiar estado activo/inactivo (recibe id_persona, nuevo_estado)
    """
    
    def __init__(
        self, 
        personas: List[PersonaConRoles],
        on_edit: Optional[Callable[[int], None]] = None,
        on_toggle_estado: Optional[Callable[[int, bool], None]] = None
    ):
        super().__init__()
        self.personas = personas
        self.on_edit = on_edit or (lambda id: None)
        self.on_toggle_estado = on_toggle_estado or (lambda id, estado: None)
        
        # Configurar estilos
        self.spacing = 0
        self.expand = True
        self.scroll = ft.ScrollMode.AUTO  # Permitir scroll vertical
        
        # Construir tabla (envuelta en Row para scroll horizontal)
        self.controls = [
            ft.Row(
                [self._construir_tabla()],
                scroll=ft.ScrollMode.AUTO,
                expand=True
            )
        ]
    
    def _construir_tabla(self) -> ft.DataTable:
        """Construye el DataTable con las personas."""
        
        # Columnas
        columnas = [
            ft.DataColumn(ft.Text("Nombre", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Documento", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Celular", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Correo", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Roles", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Activo", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Acciones", weight=ft.FontWeight.BOLD)),
        ]
        
        # Filas
        filas = [self._crear_fila(persona) for persona in self.personas]
        
        return ft.DataTable(
            columns=columnas,
            rows=filas,
            border=ft.border.all(1, colors.BORDER_DEFAULT),
            border_radius=8,
            vertical_lines=ft.border.BorderSide(1, colors.BORDER_DEFAULT),
            horizontal_lines=ft.border.BorderSide(1, colors.BORDER_DEFAULT),
            heading_row_color=colors.SURFACE,
            heading_row_height=50,
            data_row_max_height=70,
        )
    
    def _crear_fila(self, persona: PersonaConRoles) -> ft.DataRow:
        """Crea una fila del DataTable para una persona."""
        return ft.DataRow(
            cells=[
                # Nombre
                ft.DataCell(ft.Text(
                    persona.nombre_completo,
                    size=14,
                    weight=ft.FontWeight.W_500
                )),
                
                # Documento
                ft.DataCell(ft.Text(
                    persona.numero_documento,
                    size=13
                )),
                
                # Celular
                ft.DataCell(ft.Text(
                    persona.telefono_principal or "-",
                    size=13
                )),
                
                # Correo
                ft.DataCell(ft.Text(
                    persona.correo_principal or "-",
                    size=13,
                    overflow=ft.TextOverflow.ELLIPSIS,
                    max_lines=1
                )),
                
                # Roles (badges)
                ft.DataCell(
                    ft.Row(
                        [RoleBadge(rol, small=True) for rol in persona.roles],
                        spacing=5,
                        wrap=True
                    )
                ),
                
                # Estado (Switch)
                ft.DataCell(
                    ft.Switch(
                        value=persona.esta_activa,
                        active_color=colors.SUCCESS,
                        inactive_thumb_color=colors.ERROR,
                        on_change=lambda e, id_p=persona.persona.id_persona: self.on_toggle_estado(id_p, e.control.value)
                    )
                ),
                
                # Acciones
                ft.DataCell(
                    ft.Row(
                        [
                            ft.IconButton(
                                icon=ft.Icons.EDIT,
                                icon_size=18,
                                tooltip="Editar",
                                icon_color=colors.PRIMARY,
                                on_click=lambda e, id_p=persona.persona.id_persona: self.on_edit(id_p)
                            )
                        ],
                        spacing=5
                    )
                ),
            ]
        )
    
    def actualizar_datos(self, nuevas_personas: List[PersonaConRoles]):
        """Actualiza la tabla con nuevas personas."""
        self.personas = nuevas_personas
        self.controls = [
            ft.Row(
                [self._construir_tabla()],
                scroll=ft.ScrollMode.AUTO,
                expand=True
            )
        ]
        self.update()
