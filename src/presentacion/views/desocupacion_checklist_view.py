"""
Vista: Checklist Interactive de Desocupación
Permite completar las tareas del checklist y finalizar la desocupación.
"""

import threading
from typing import Callable

import flet as ft

from src.presentacion.theme import colors


class DesocupacionChecklistView(ft.Container):
    def __init__(
        self, page: ft.Page, servicio_desocupaciones, id_desocupacion: int, on_volver: Callable
    ):
        super().__init__(expand=True, padding=24)
        self.page_ref = page
        self.servicio = servicio_desocupaciones
        self.id_desocupacion = id_desocupacion
        self.on_volver = on_volver

        self.desocupacion = None
        self.tareas = []
        self.progreso_data = None

        # Refs
        self.progress_bar_ref = ft.Ref[ft.ProgressBar]()
        self.progress_text_ref = ft.Ref[ft.Text]()
        self.header_info_ref = ft.Ref[ft.Column]()
        self.checklist_ref = ft.Ref[ft.Column]()
        self.btn_finalizar_ref = ft.Ref[ft.ElevatedButton]()

        # Loading
        self.loading = ft.Column(
            [ft.ProgressBar(width=400), ft.Text("Cargando checklist...")],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )

        # Build initial UI
        self.content = ft.Column(
            [
                ft.Row(
                    [
                        ft.IconButton(
                            icon=ft.Icons.ARROW_BACK,
                            tooltip="Volver",
                            on_click=lambda e: self.on_volver(),
                        ),
                        ft.Text("Checklist de Desocupación", size=28, weight="bold"),
                    ]
                ),
                ft.Divider(height=20),
                # Header with property info (will be populated)
                ft.Container(ref=self.header_info_ref),
                # Progress bar
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Row(
                                [
                                    ft.Text("Progreso:", size=16, weight="bold"),
                                    ft.Container(expand=True),
                                    ft.Text(
                                        ref=self.progress_text_ref,
                                        value="0/8",
                                        size=16,
                                        weight="bold",
                                    ),
                                ]
                            ),
                            ft.ProgressBar(
                                ref=self.progress_bar_ref,
                                value=0,
                                width=600,
                                height=12,
                                color=ft.Colors.GREEN,
                                bgcolor=ft.Colors.GREY_300,
                            ),
                        ],
                        spacing=8,
                    ),
                    bgcolor=ft.Colors.BLUE_50,
                    padding=16,
                    border_radius=12,
                ),
                ft.Container(height=20),
                # Checklist (will be populated)
                ft.Container(ref=self.checklist_ref, expand=True),
                ft.Container(height=20),
                # Botón Finalizar
                ft.ElevatedButton(
                    ref=self.btn_finalizar_ref,
                    text="Finalizar Desocupación",
                    icon=ft.Icons.DONE_ALL,
                    disabled=True,
                    bgcolor=ft.Colors.GREEN,
                    color="white",
                    on_click=self._handle_finalizar,
                ),
            ],
            spacing=8,
            expand=True,
        )

    def did_mount(self):
        self.cargar_datos()

    def cargar_datos(self):
        threading.Thread(target=self._fetch_data, daemon=True).start()

    def _fetch_data(self):
        try:
            self.desocupacion = self.servicio.obtener_desocupacion(self.id_desocupacion)
            self.tareas = self.servicio.obtener_checklist(self.id_desocupacion)
            self.progreso_data = self.servicio.calcular_progreso(self.id_desocupacion)
            self._schedule_ui_update()
        except Exception as e:
            pass  # print(f"Error cargando checklist: {e}") [OpSec Removed]
            self._schedule_ui_update(error=str(e))

    def _schedule_ui_update(self, error=None):
        if error:
            if self.checklist_ref.current:
                self.checklist_ref.current.content = ft.Text(f"Error: {error}", color="red")
                self.checklist_ref.current.update()
            return

        # Update header info
        if self.header_info_ref.current and self.desocupacion:
            self.header_info_ref.current.content = self._build_header()
            self.header_info_ref.current.update()

        # Update progress
        if self.progreso_data:
            if self.progress_bar_ref.current:
                self.progress_bar_ref.current.value = self.progreso_data["porcentaje"] / 100
                self.progress_bar_ref.current.update()

            if self.progress_text_ref.current:
                self.progress_text_ref.current.value = (
                    f"{self.progreso_data['completadas']}/{self.progreso_data['total']}"
                )
                self.progress_text_ref.current.update()

            # Enable/disable finalizar button
            if self.btn_finalizar_ref.current:
                self.btn_finalizar_ref.current.disabled = (
                    not self.progreso_data["puede_finalizar"]
                    or self.desocupacion.estado != "En Proceso"
                )
                self.btn_finalizar_ref.current.update()

        # Update checklist
        if self.checklist_ref.current:
            self.checklist_ref.current.content = self._build_checklist()
            self.checklist_ref.current.update()

    def _build_header(self):
        """Construye el header con información del contrato."""
        return ft.Container(
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Icon(ft.Icons.HOME, color=colors.PRIMARY, size=24),
                            ft.Text(
                                f"Propiedad: {self.desocupacion.direccion_propiedad}",
                                size=16,
                                weight="bold",
                            ),
                        ],
                        spacing=8,
                    ),
                    ft.Row(
                        [
                            ft.Icon(ft.Icons.PERSON, color=colors.PRIMARY, size=24),
                            ft.Text(f"Inquilino: {self.desocupacion.nombre_inquilino}", size=16),
                        ],
                        spacing=8,
                    ),
                    ft.Row(
                        [
                            ft.Icon(ft.Icons.CALENDAR_TODAY, color=colors.PRIMARY, size=24),
                            ft.Text(
                                f"Fecha Programada: {self.desocupacion.fecha_programada}", size=16
                            ),
                        ],
                        spacing=8,
                    ),
                ],
                spacing=8,
            ),
            bgcolor=ft.Colors.WHITE,
            padding=16,
            border_radius=12,
            border=ft.border.all(1, ft.Colors.GREY_200),
        )

    def _build_checklist(self):
        """Construye la lista de tareas con checkboxes."""
        if not self.tareas:
            return ft.Text("No hay tareas", color="grey")

        tarea_widgets = []
        for tarea in self.tareas:
            # Checkbox + Descripción
            checkbox = ft.Checkbox(
                value=tarea.completada,
                disabled=tarea.completada or self.desocupacion.estado != "En Proceso",
                on_change=lambda e, t=tarea: self._handle_toggle_tarea(t, e.control.value),
            )

            # Status icon
            if tarea.completada:
                status_icon = ft.Icon(ft.Icons.CHECK_CIRCLE, color=ft.Colors.GREEN, size=20)
            else:
                status_icon = ft.Icon(
                    ft.Icons.RADIO_BUTTON_UNCHECKED, color=ft.Colors.GREY, size=20
                )

            # Description with strikethrough if completed
            desc_text = ft.Text(
                tarea.descripcion,
                size=14,
                weight="bold" if not tarea.completada else "normal",
                color=ft.Colors.GREY_600 if tarea.completada else ft.Colors.BLACK,
            )

            # Observaciones (if exist)
            obs_widget = None
            if tarea.observaciones:
                obs_widget = ft.Text(
                    f"📝 {tarea.observaciones}", size=12, color=ft.Colors.GREY_600, italic=True
                )

            # Completada info
            completada_info = None
            if tarea.completada:
                completada_info = ft.Text(
                    f"✓ Completada por {tarea.responsable} el {tarea.fecha_completada[:10] if tarea.fecha_completada else ''}",
                    size=11,
                    color=ft.Colors.GREEN_700,
                )

            # Container for this task
            tarea_container = ft.Container(
                content=ft.Column(
                    [
                        ft.Row([checkbox, status_icon, desc_text], spacing=12),
                        obs_widget if obs_widget else ft.Container(),
                        completada_info if completada_info else ft.Container(),
                    ],
                    spacing=4,
                ),
                bgcolor=ft.Colors.GREEN_50 if tarea.completada else ft.Colors.WHITE,
                padding=16,
                border_radius=8,
                border=ft.border.all(
                    1, ft.Colors.GREEN_200 if tarea.completada else ft.Colors.GREY_200
                ),
            )

            tarea_widgets.append(tarea_container)

        return ft.Column(tarea_widgets, spacing=12, scroll=ft.ScrollMode.AUTO)

    def _handle_toggle_tarea(self, tarea, is_checked):
        """Maneja el click en checkbox de tarea."""
        if is_checked:
            # Pedir observaciones opcionales
            txt_obs = ft.Ref[ft.TextField]()

            def confirmar_completar(e):
                self.page_ref.close(dlg)
                try:
                    self.servicio.completar_tarea(
                        tarea.id_tarea,
                        "admin",  # TODO: Get from session
                        txt_obs.current.value if txt_obs.current.value else None,
                    )
                    self.cargar_datos()  # Reload
                except Exception as ex:
                    self.page_ref.snack_bar = ft.SnackBar(
                        content=ft.Text(f"Error: {str(ex)}"), bgcolor="red"
                    )
                    self.page_ref.snack_bar.open = True
                    self.page_ref.update()

            dlg = ft.AlertDialog(
                modal=True,
                title=ft.Text(f"Completar: {tarea.descripcion}"),
                content=ft.Column(
                    [
                        ft.Text("¿Deseas agregar observaciones sobre esta tarea?"),
                        ft.TextField(
                            ref=txt_obs,
                            label="Observaciones (opcional)",
                            multiline=True,
                            min_lines=2,
                            max_lines=4,
                        ),
                    ],
                    tight=True,
                    width=400,
                ),
                actions=[
                    ft.TextButton("Cancelar", on_click=lambda e: self.page_ref.close(dlg)),
                    ft.TextButton("Completar", on_click=confirmar_completar),
                ],
            )
            self.page_ref.open(dlg)

    def _handle_finalizar(self, e):
        """Maneja el click en Finalizar Desocupación."""

        def confirmar(e):
            try:
                self.servicio.finalizar_desocupacion(
                    self.id_desocupacion, "admin"
                )  # TODO: Get from session
                self.page_ref.close(dlg)
                self.page_ref.snack_bar = ft.SnackBar(
                    content=ft.Text(
                        "Desocupación finalizada exitosamente. Contrato marcado como Finalizado."
                    ),
                    bgcolor="green",
                )
                self.page_ref.snack_bar.open = True
                self.page_ref.update()
                self.on_volver()
            except Exception as ex:
                self.page_ref.close(dlg)
                self.page_ref.snack_bar = ft.SnackBar(
                    content=ft.Text(f"Error: {str(ex)}"), bgcolor="red"
                )
                self.page_ref.snack_bar.open = True
                self.page_ref.update()

        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("Finalizar Desocupación"),
            content=ft.Text(
                "¿Estás seguro de finalizar esta desocupación? El contrato será marcado como FINALIZADO y esta acción no se puede deshacer.",
                size=14,
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: self.page_ref.close(dlg)),
                ft.TextButton(
                    "Finalizar", on_click=confirmar, style=ft.ButtonStyle(color=ft.Colors.GREEN)
                ),
            ],
        )
        self.page_ref.open(dlg)


def crear_desocupacion_checklist_view(page, servicio_desocupaciones, id_desocupacion, on_volver):
    return DesocupacionChecklistView(page, servicio_desocupaciones, id_desocupacion, on_volver)
