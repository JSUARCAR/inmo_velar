"""
Componente: Property DataTable
Tabla para mostrar listado de propiedades con acciones.
"""

from typing import Callable, List

import reflex as rx

from src.dominio.entidades.propiedad import Propiedad
from src.presentacion.theme import colors


class PropertyDataTable(ft.Column):
    """
    Tabla de propiedades con columnas de información y acciones.
    """

    def __init__(
        self,
        propiedades: List[Propiedad],
        on_edit: Callable[[int], None],
        on_toggle_disponibilidad: Callable[[int, int], None],
    ):
        super().__init__()
        self.propiedades = propiedades
        self.on_edit = on_edit
        self.on_toggle_disponibilidad = on_toggle_disponibilidad

        # Configurar estilos
        self.spacing = 0
        self.expand = True
        self.scroll = ft.ScrollMode.AUTO

        # Construir tabla
        self.controls = [ft.Row([self._construir_tabla()], scroll=ft.ScrollMode.AUTO, expand=True)]

    def formato_moneda(self, valor):
        """Formatea número como moneda colombiana."""
        if valor is None:
            return "N/A"
        return f"${valor:,.0f}".replace(",", ".")

    def crear_badge_disponibilidad(self, disponible: bool) -> ft.Container:
        """Crea un badge visual para disponibilidad."""
        return ft.Container(
            content=ft.Text(
                "Disponible" if disponible else "Ocupada",
                size=11,
                weight=ft.FontWeight.BOLD,
                color=ft.Colors.WHITE,
            ),
            padding=ft.padding.symmetric(horizontal=6, vertical=2),
            bgcolor=colors.SUCCESS if disponible else colors.TEXT_DISABLED,
            border_radius=4,
        )

    def _construir_tabla(self) -> ft.DataTable:
        """Construye el DataTable con las propiedades."""

        # Crear filas de la tabla
        rows = []

        for prop in self.propiedades:
            disponible = prop.disponibilidad_propiedad == 1

            # Handler para toggle
            def make_toggle_handler(prop_id, disp):
                def handler(e):
                    nueva_disp = 0 if disp == 1 else 1
                    self.on_toggle_disponibilidad(prop_id, nueva_disp)

                return handler

            # Handler para editar
            def make_edit_handler(prop_id):
                def handler(e):
                    self.on_edit(prop_id)

                return handler

            row = ft.DataRow(
                cells=[
                    # Matrícula
                    ft.DataCell(
                        ft.Text(
                            prop.matricula_inmobiliaria,
                            size=13,
                            color=colors.TEXT_PRIMARY,
                            weight=ft.FontWeight.W_500,
                        )
                    ),
                    # Tipo
                    ft.DataCell(
                        ft.Container(
                            content=ft.Text(
                                prop.tipo_propiedad, size=12, color=colors.TEXT_SECONDARY
                            ),
                            padding=ft.padding.symmetric(horizontal=6, vertical=2),
                            border=ft.border.all(1, colors.BORDER_DEFAULT),
                            border_radius=4,
                        )
                    ),
                    # Dirección
                    ft.DataCell(
                        ft.Text(
                            (
                                prop.direccion_propiedad[:40] + "..."
                                if len(prop.direccion_propiedad) > 40
                                else prop.direccion_propiedad
                            ),
                            size=12,
                            color=colors.TEXT_SECONDARY,
                            overflow=ft.TextOverflow.ELLIPSIS,
                        )
                    ),
                    # Disponibilidad
                    ft.DataCell(self.crear_badge_disponibilidad(disponible)),
                    # Área
                    ft.DataCell(
                        ft.Text(f"{prop.area_m2:.0f} m²", size=12, color=colors.TEXT_SECONDARY)
                    ),
                    # Características (hab/baños/parq)
                    ft.DataCell(
                        ft.Row(
                            [
                                ft.Icon(ft.Icons.BED, size=12, color=colors.TEXT_DISABLED),
                                ft.Text(
                                    str(prop.habitaciones or 0),
                                    size=11,
                                    color=colors.TEXT_SECONDARY,
                                ),
                                ft.Icon(ft.Icons.BATHTUB, size=12, color=colors.TEXT_DISABLED),
                                ft.Text(str(prop.bano or 0), size=11, color=colors.TEXT_SECONDARY),
                                ft.Icon(
                                    ft.Icons.DIRECTIONS_CAR, size=12, color=colors.TEXT_DISABLED
                                ),
                                ft.Text(
                                    str(prop.parqueadero or 0), size=11, color=colors.TEXT_SECONDARY
                                ),
                            ],
                            spacing=4,
                            tight=True,
                        )
                    ),
                    # Precio Venta
                    ft.DataCell(
                        ft.Text(
                            self.formato_moneda(prop.valor_venta_propiedad),
                            size=12,
                            color=colors.TEXT_PRIMARY,
                            weight=(
                                ft.FontWeight.BOLD
                                if prop.valor_venta_propiedad
                                else ft.FontWeight.NORMAL
                            ),
                        )
                    ),
                    # Acciones
                    ft.DataCell(
                        ft.Row(
                            [
                                ft.IconButton(
                                    icon=ft.Icons.EDIT,
                                    icon_size=18,
                                    icon_color=colors.PRIMARY,
                                    tooltip="Editar",
                                    on_click=make_edit_handler(prop.id_propiedad),
                                ),
                                ft.IconButton(
                                    icon=ft.Icons.SWAP_HORIZ,
                                    icon_size=18,
                                    icon_color=colors.SUCCESS if disponible else colors.WARNING,
                                    tooltip="Cambiar disponibilidad",
                                    on_click=make_toggle_handler(
                                        prop.id_propiedad, prop.disponibilidad_propiedad
                                    ),
                                ),
                            ],
                            spacing=0,
                            tight=True,
                        )
                    ),
                ]
            )
            rows.append(row)

        # Crear tabla
        return ft.DataTable(
            columns=[
                ft.DataColumn(
                    ft.Text(
                        "Matrícula", weight=ft.FontWeight.BOLD, size=13, color=colors.TEXT_PRIMARY
                    )
                ),
                ft.DataColumn(
                    ft.Text("Tipo", weight=ft.FontWeight.BOLD, size=13, color=colors.TEXT_PRIMARY)
                ),
                ft.DataColumn(
                    ft.Text(
                        "Dirección", weight=ft.FontWeight.BOLD, size=13, color=colors.TEXT_PRIMARY
                    )
                ),
                ft.DataColumn(
                    ft.Text(
                        "Disponibilidad",
                        weight=ft.FontWeight.BOLD,
                        size=13,
                        color=colors.TEXT_PRIMARY,
                    )
                ),
                ft.DataColumn(
                    ft.Text("Área", weight=ft.FontWeight.BOLD, size=13, color=colors.TEXT_PRIMARY)
                ),
                ft.DataColumn(
                    ft.Text(
                        "Caract.", weight=ft.FontWeight.BOLD, size=13, color=colors.TEXT_PRIMARY
                    )
                ),
                ft.DataColumn(
                    ft.Text(
                        "Precio Venta",
                        weight=ft.FontWeight.BOLD,
                        size=13,
                        color=colors.TEXT_PRIMARY,
                    )
                ),
                ft.DataColumn(
                    ft.Text(
                        "Acciones", weight=ft.FontWeight.BOLD, size=13, color=colors.TEXT_PRIMARY
                    )
                ),
            ],
            rows=rows,
            border=ft.border.all(1, colors.BORDER_DEFAULT),
            border_radius=8,
            vertical_lines=ft.BorderSide(1, colors.BORDER_DEFAULT),
            horizontal_lines=ft.BorderSide(1, colors.BORDER_DEFAULT),
            heading_row_color=ft.Colors.with_opacity(0.05, colors.PRIMARY),
            heading_row_height=45,
            data_row_min_height=50,
            data_row_max_height=60,
        )
