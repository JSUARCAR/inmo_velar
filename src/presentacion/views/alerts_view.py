"""
Centro de Alertas (Drawer) - Inmobiliaria Velar
Panel lateral de notificaciones.
"""

import flet as ft
import threading
import time
from src.presentacion.theme import colors


class AlertsView(ft.NavigationDrawer):
    """Drawer de notificaciones con carga asíncrona."""
    
    def __init__(self, servicio_alertas=None, servicio_recibos=None, servicio_dashboard=None, servicio_liquidacion_asesores=None, on_dismiss=None):
        super().__init__()
        
        self.servicio_alertas = servicio_alertas
        self.servicio_recibos = servicio_recibos
        self.servicio_dashboard = servicio_dashboard
        self.servicio_liquidacion_asesores = servicio_liquidacion_asesores
        self.on_dismiss = on_dismiss
        self.position = ft.NavigationDrawerPosition.END
        self.width = 400
        self.shadow_color = "black"
        
        # Estado
        self.alertas = []
        self.cargando = False
        
        # Contenedor de lista de alertas
        self.lista_alertas_container = ft.Column(spacing=15, scroll=ft.ScrollMode.AUTO, expand=True)
        self.loading_indicator = ft.Column(
            [
                ft.ProgressRing(color=colors.PRIMARY),
                ft.Text("Buscando notificaciones...", color=colors.TEXT_SECONDARY, size=12)
            ], 
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            visible=False
        )

        
        # Contenido del Drawer
        self.controls = [
            ft.Container(
                content=ft.Column(
                    [
                        # Header
                        ft.Row(
                            [
                                ft.Text(
                                    "Notificaciones",
                                    size=20,
                                    weight=ft.FontWeight.BOLD,
                                    color=colors.TEXT_PRIMARY
                                ),
                                ft.Row([
                                    ft.IconButton(
                                        ft.Icons.REFRESH,
                                        tooltip="Actualizar",
                                        on_click=lambda _: self.cargar_alertas()
                                    ),
                                    ft.IconButton(
                                        ft.Icons.CLOSE,
                                        on_click=lambda _: self._close_drawer()
                                    )
                                ], spacing=0)
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                        ),
                        
                        ft.Divider(),
                        
                        # Loading e indicador
                        ft.Container(content=self.loading_indicator, alignment=ft.alignment.center),

                        # Lista de alertas
                        self.lista_alertas_container
                    ],
                    spacing=15,
                    expand=True
                ),
                padding=20,
                expand=True
            )
        ]
        
        # Cargar alertas iniciales
        self.cargar_alertas()
        
    def cargar_alertas(self):
        """Inicia la carga asíncrona de alertas."""
        self.cargando = True
        self.loading_indicator.visible = True
        self.lista_alertas_container.visible = False
        self.update_safe()
        
        threading.Thread(target=self._fetch_data_thread, daemon=True).start()

    def update_safe(self):
        """Actualiza el control verificando si está montado en la página."""
        if self.page:
            self.update()

    def _fetch_data_thread(self):
        """Lógica de obtención de datos en segundo plano."""
        try:
            if not self.servicio_alertas:
                self._schedule_ui_update([], error="Servicios no configurados")
                return
            
            # Obtener todas las alertas (operación pesada)
            alertas = self.servicio_alertas.obtener_alertas(
                self.servicio_recibos, 
                self.servicio_dashboard,
                self.servicio_liquidacion_asesores
            )
            
            self._schedule_ui_update(alertas, error=None)
            
        except Exception as e:
            print(f"Error cargando alertas: {e}")
            self._schedule_ui_update([], error=str(e))

    def _schedule_ui_update(self, alertas, error):
        """Programa la actualización de la UI."""
        # Validar Page antes de proceder (anti race-condition)
        if not self.page:
            return
            
        self.alertas = alertas
        self._render_alertas(error)
        self.cargando = False
        self.loading_indicator.visible = False
        self.lista_alertas_container.visible = True
        self.update_safe()

    def _render_alertas(self, error):
        """Renderiza la lista de alertas."""
        self.lista_alertas_container.controls.clear()
        
        if error:
            self.lista_alertas_container.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.ERROR_OUTLINE, color=colors.ERROR),
                        ft.Text(f"Error: {error}", color=colors.ERROR)
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    alignment=ft.alignment.center
                )
            )
            return

        if not self.alertas:
            self.lista_alertas_container.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.NOTIFICATIONS_OFF_OUTLINED, size=48, color=colors.TEXT_DISABLED),
                        ft.Text("No hay notificaciones nuevas", color=colors.TEXT_DISABLED)
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    alignment=ft.alignment.center,
                    padding=20
                )
            )
        else:
            # Agrupar y crear Tiles
            grupos = {
                "Contratos por Vencer": [],
                "Recibos Vencidos": [],
                "Ajustes IPC": [],
                "Liquidaciones": [],
                "Otros": []
            }
            
            for alerta in self.alertas:
                tipo = alerta.get('tipo', '')
                item = self._crear_item_alerta(alerta)
                
                if tipo in ['ContratoMandatoVencimiento', 'ContratoArrendamientoVencimiento']:
                    grupos["Contratos por Vencer"].append(item)
                elif tipo == 'ReciboVencido':
                    grupos["Recibos Vencidos"].append(item)
                elif tipo == 'AjusteIPC':
                    grupos["Ajustes IPC"].append(item)
                elif tipo == 'LiquidacionPendiente':
                    grupos["Liquidaciones"].append(item)
                else:
                    grupos["Otros"].append(item)
            
            for titulo, items in grupos.items():
                if items:
                    # Configuración visual de grupos
                    icono_grupo = ft.Icons.NOTIFICATION_IMPORTANT
                    color_grupo = colors.PRIMARY
                    initially_expanded = False
                    
                    if titulo == "Contratos por Vencer":
                        icono_grupo = ft.Icons.HOME_WORK
                        initially_expanded = True 
                    elif titulo == "Recibos Vencidos":
                        icono_grupo = ft.Icons.RECEIPT_LONG
                        color_grupo = colors.ERROR
                        initially_expanded = True
                    elif titulo == "Ajustes IPC":
                        icono_grupo = ft.Icons.TRENDING_UP
                        color_grupo = colors.SUCCESS
                    elif titulo == "Liquidaciones":
                        icono_grupo = ft.Icons.HANDSHAKE
                        color_grupo = colors.WARNING
                    
                    tile = ft.ExpansionTile(
                        title=ft.Text(f"{titulo} ({len(items)})", weight=ft.FontWeight.BOLD),
                        leading=ft.Icon(icono_grupo, color=color_grupo),
                        controls=items,
                        initially_expanded=initially_expanded,
                        text_color=colors.TEXT_PRIMARY,
                        icon_color=colors.PRIMARY,
                        collapsed_text_color=colors.TEXT_SECONDARY,
                        collapsed_icon_color=colors.TEXT_SECONDARY,
                    )
                    self.lista_alertas_container.controls.append(tile)

    def _crear_item_alerta(self, alerta):
        """Helper para crear el control visual de una alerta individual."""
        # Determinar estilo
        color = colors.INFO
        icono = ft.Icons.INFO
        tipo = alerta.get('tipo')
        
        if alerta.get('prioridad') == 'alta':
            color = colors.ERROR
            icono = ft.Icons.WARNING_AMBER_ROUNDED
        elif tipo == 'ReciboVencido':
            color = colors.ERROR
            icono = ft.Icons.RECEIPT_LONG
        elif tipo == 'ContratoMandatoVencimiento':
            icono = ft.Icons.DOCUMENT_SCANNER
            if alerta.get('prioridad') == 'media': color = colors.WARNING
        elif tipo == 'ContratoArrendamientoVencimiento':
            icono = ft.Icons.HOME_WORK
             # Ya viene con prioridad ajustada desde el servicio
            if alerta.get('prioridad') == 'media': color = colors.WARNING
            elif alerta.get('prioridad') == 'baja': color = colors.INFO
        elif tipo == 'AjusteIPC':
            icono = ft.Icons.TRENDING_UP
            color = colors.SUCCESS
            if alerta.get('prioridad') == 'alta': color = colors.WARNING
        elif tipo == 'LiquidacionPendiente':
            color = colors.WARNING
            icono = ft.Icons.HANDSHAKE

        return ft.Container(
            content=ft.Row(
                [
                    ft.Container(
                        content=ft.Icon(icono, color=color, size=20),
                        bgcolor=ft.Colors.with_opacity(0.1, color),
                        padding=8,
                        border_radius=5
                    ),
                    ft.Column(
                        [
                            ft.Text(alerta.get('titulo', ''), weight=ft.FontWeight.BOLD, size=13),
                            ft.Text(alerta.get('mensaje', ''), size=11, color=colors.TEXT_SECONDARY, no_wrap=False),
                            ft.Text(str(alerta.get('fecha', '')), size=10, color=colors.TEXT_DISABLED),
                        ],
                        spacing=2,
                        expand=True
                    )
                ],
                alignment=ft.MainAxisAlignment.START,
                vertical_alignment=ft.CrossAxisAlignment.START
            ),
            padding=ft.padding.only(left=20, right=10, top=10, bottom=10),
            border=ft.border.only(bottom=ft.border.BorderSide(1, colors.BORDER_DEFAULT)),
            bgcolor=colors.BACKGROUND
        )

    def _close_drawer(self):
        """Cierra el drawer."""
        self.open = False
        if self.on_dismiss:
            self.on_dismiss()
        self.update()
