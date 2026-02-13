"""
Componente Card de Recibo Público
Muestra información resumida de un recibo público con acciones rápidas.
"""

from datetime import datetime

import reflex as rx

from src.dominio.entidades.recibo_publico import ReciboPublico
from src.presentacion.theme import colors


class ReciboCard(ft.Card):
    """
    Tarjeta visual para representar un recibo público.

    Args:
        recibo (ReciboPublico): Entidad de dominio con datos del recibo.
        on_edit (callable, optional): Acción al hacer clic en editar.
        on_pay (callable, optional): Acción al hacer clic en pagar (si está pendiente).
        on_delete (callable, optional): Acción al hacer clic en eliminar.
    """

    def __init__(self, recibo: ReciboPublico, on_edit=None, on_pay=None, on_delete=None):
        super().__init__()
        self.recibo = recibo
        self.on_edit = on_edit
        self.on_pay = on_pay
        self.on_delete = on_delete

        # Configuración visual
        self.elevation = 2
        self.surface_tint_color = colors.SURFACE
        self.content = self._build_content()

    def _get_service_icon(self) -> str:
        icons = {
            "Agua": ft.Icons.WATER_DROP_OUTLINED,
            "Luz": ft.Icons.LIGHTBULB_OUTLINE,
            "Gas": ft.Icons.PROPANE_OUTLINED,
            "Internet": ft.Icons.WIFI,
            "Administracion": ft.Icons.ADMIN_PANEL_SETTINGS_OUTLINED,
            "Otro": ft.Icons.RECEIPT_LONG_OUTLINED,
        }
        return icons.get(self.recibo.tipo_servicio, ft.Icons.RECEIPT)

    def _get_status_color(self) -> str:
        if self.recibo.esta_pagado:
            return colors.SUCCESS

        # Verificar vencimiento
        try:
            fecha_vence = datetime.strptime(self.recibo.fecha_vencimiento, "%Y-%m-%d")
            dias_mora = (datetime.now() - fecha_vence).days
            if dias_mora > 0:
                return colors.ERROR
        except:
            pass

        return colors.WARNING

    def _get_status_label(self) -> str:
        if self.recibo.esta_pagado:
            return "PAGADO"

        # Verificar vencimiento
        try:
            fecha_vence = datetime.strptime(self.recibo.fecha_vencimiento, "%Y-%m-%d")
            dias_mora = (datetime.now() - fecha_vence).days
            if dias_mora > 0:
                return f"VENCIDO ({dias_mora}d)"
        except:
            pass

        return "PENDIENTE"

    def _build_content(self):
        color_estado = self._get_status_color()
        label_estado = self._get_status_label()

        # Acciones
        actions = []

        if not self.recibo.esta_pagado and self.on_pay:
            actions.append(
                ft.IconButton(
                    icon=ft.Icons.PAYMENT,
                    icon_color=colors.SUCCESS,
                    tooltip="Registrar Pago",
                    on_click=lambda _: self.on_pay(self.recibo.id_recibo_publico),
                )
            )

        if self.on_edit:
            actions.append(
                ft.IconButton(
                    icon=ft.Icons.EDIT,
                    icon_color=colors.PRIMARY,
                    tooltip="Editar Recibo",
                    on_click=lambda _: self.on_edit(self.recibo.id_recibo_publico),
                )
            )

        if self.on_delete:
            actions.append(
                ft.IconButton(
                    icon=ft.Icons.DELETE_OUTLINE,
                    icon_color=colors.ERROR,
                    tooltip="Eliminar Recibo",
                    on_click=lambda _: self.on_delete(self.recibo.id_recibo_publico),
                )
            )

        return ft.Container(
            content=ft.Column(
                [
                    # Encabezado: Icono + Tipo + Estado
                    ft.Row(
                        [
                            ft.Container(
                                content=ft.Icon(
                                    self._get_service_icon(), color=colors.PRIMARY, size=24
                                ),
                                bgcolor=colors.BACKGROUND,
                                border_radius=8,
                                padding=8,
                            ),
                            ft.Column(
                                [
                                    ft.Text(
                                        self.recibo.tipo_servicio,
                                        weight=ft.FontWeight.BOLD,
                                        size=16,
                                    ),
                                    ft.Text(
                                        self.recibo.periodo_recibo,
                                        color=colors.TEXT_SECONDARY,
                                        size=12,
                                    ),
                                ],
                                spacing=0,
                                expand=True,
                            ),
                            ft.Container(
                                content=ft.Text(
                                    label_estado,
                                    size=10,
                                    color=colors.TEXT_ON_PRIMARY,
                                    weight=ft.FontWeight.BOLD,
                                ),
                                bgcolor=color_estado,
                                border_radius=4,
                                padding=ft.padding.symmetric(horizontal=8, vertical=4),
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    ft.Divider(height=1, color=colors.BORDER_DEFAULT),
                    # Detalles
                    ft.Row(
                        [
                            ft.Column(
                                [
                                    ft.Text("Vencimiento", size=10, color=colors.TEXT_SECONDARY),
                                    ft.Text(
                                        self.recibo.fecha_vencimiento,
                                        size=12,
                                        weight=ft.FontWeight.W_500,
                                    ),
                                ]
                            ),
                            ft.Column(
                                [
                                    ft.Text("Valor", size=10, color=colors.TEXT_SECONDARY),
                                    ft.Text(
                                        f"${self.recibo.valor_recibo:,.0f}",
                                        size=14,
                                        weight=ft.FontWeight.BOLD,
                                        color=colors.PRIMARY,
                                    ),
                                ],
                                horizontal_alignment=ft.CrossAxisAlignment.END,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    # Footer con acciones
                    ft.Row(actions, alignment=ft.MainAxisAlignment.END, visible=bool(actions)),
                ],
                spacing=10,
            ),
            padding=15,
            width=280,  # Ancho fijo para grids
            border_radius=12,
            bgcolor=colors.SURFACE,
            border=ft.border.all(1, colors.BORDER_DEFAULT),
        )
