from typing import Callable
import flet as ft
import threading
from src.aplicacion.servicios.servicio_incidentes import ServicioIncidentes
from src.presentacion.components.incident_card import IncidentCard

class IncidentesListView(ft.Column):
    def __init__(self, page: ft.Page, servicio_incidentes: ServicioIncidentes, on_navigate: Callable):
        super().__init__(expand=True, spacing=20)
        self.page_ref = page
        self.servicio = servicio_incidentes
        self.on_navigate = on_navigate
        self.incidentes = []
        
        # Init controls
        self.lbl_title = ft.Text("Gestión de Incidentes", size=24, weight=ft.FontWeight.BOLD)
        self.btn_nuevo = ft.ElevatedButton(
            "Reportar Incidente",
            icon=ft.Icons.ADD,
            on_click=lambda _: self.on_navigate("incidente_reportar")
        )
        
        self.contenedor_incidentes = ft.Row(
            wrap=True,
            spacing=20,
            alignment=ft.MainAxisAlignment.START,
            scroll=ft.ScrollMode.AUTO
        )
        self.loading = ft.ProgressBar(width=400, color="blue", visible=False)

        # Build controls (adaptado de build)
        self.controls = [
            ft.Row([self.lbl_title, ft.Container(expand=True), self.btn_nuevo]),
            ft.Divider(),
            ft.Container(
                content=ft.Column([
                    # Loading container
                    ft.Container(content=self.loading, alignment=ft.alignment.center),
                    
                    # Data container
                    ft.Container(
                        content=self.contenedor_incidentes,
                        expand=True
                    )
                ]),
                expand=True
            )
        ]

    def did_mount(self):
        self.cargar_incidentes(inicial=True)

    def cargar_incidentes(self, inicial: bool = False):
        self.loading.visible = True
        self.contenedor_incidentes.visible = False
        self.update()
        
        threading.Thread(target=self._fetch_data, daemon=True).start()

    def _fetch_data(self):
        try:
            self.incidentes = self.servicio.listar_incidentes()
            self._update_ui()
        except Exception as e:
            pass  # print(f"Error loading incidentes: {e}") [OpSec Removed]
            self.loading.visible = False
            self.update()

    def _update_ui(self):
        self.contenedor_incidentes.controls.clear()
        
        if not self.incidentes:
            self.contenedor_incidentes.controls.append(
                ft.Text("No hay incidentes registrados.", color=ft.Colors.GREY_500)
            )
        else:
            for inc in self.incidentes:
                card = IncidentCard(inc, on_click=self.on_card_click)
                self.contenedor_incidentes.controls.append(card)
        
        self.loading.visible = False
        self.contenedor_incidentes.visible = True
        self.update()

    def on_card_click(self, incidente):
        self.on_navigate("incidente_detalle", id_incidente=incidente.id_incidente)
