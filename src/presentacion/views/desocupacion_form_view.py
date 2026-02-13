"""
Vista: Formulario de Nueva Desocupación
Permite iniciar el proceso de desocupación seleccionando un contrato activo.
"""

import os
import shutil
from datetime import datetime, timedelta
from typing import Callable

import reflex as rx

from src.presentacion.theme import colors


class DesocupacionFormView(ft.Container):
    def __init__(
        self, page: ft.Page, servicio_desocupaciones, on_guardar: Callable, on_cancelar: Callable
    ):
        super().__init__(expand=True, padding=24)
        self.page_ref = page
        self.servicio = servicio_desocupaciones
        self.on_guardar = on_guardar
        self.on_cancelar = on_cancelar

        # Refs
        self.dd_contrato = ft.Ref[ft.Dropdown]()
        self.fecha_programada = ft.Ref[ft.TextField]()
        self.txt_observaciones = ft.Ref[ft.TextField]()

        # DatePicker
        self.date_picker = ft.DatePicker(
            first_date=datetime.now(),
            last_date=datetime.now() + timedelta(days=365),
            on_change=self._on_date_selected,
        )

        # Cargar contratos
        contratos = self._cargar_contratos()

        self.content = ft.Column(
            [
                # Header
                ft.Text("Nueva Desocupación", size=28, weight="bold"),
                ft.Divider(height=20),
                # Form
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Dropdown(
                                ref=self.dd_contrato,
                                label="Contrato a Desocupar *",
                                hint_text="Selecciona el contrato",
                                options=contratos,
                                width=500,
                            ),
                            ft.TextField(
                                ref=self.fecha_programada,
                                label="Fecha Programada de Entrega *",
                                hint_text="YYYY-MM-DD",
                                read_only=True,
                                width=500,
                                suffix=ft.IconButton(
                                    icon=ft.Icons.CALENDAR_MONTH,
                                    icon_color=colors.PRIMARY,
                                    tooltip="Seleccionar fecha",
                                    on_click=lambda e: self.page_ref.open(self.date_picker),
                                ),
                            ),
                            ft.TextField(
                                ref=self.txt_observaciones,
                                label="Observaciones Iniciales",
                                hint_text="Motivo de la desocupación, acuerdos previos, etc.",
                                multiline=True,
                                min_lines=3,
                                max_lines=5,
                                width=500,
                            ),
                            ft.Container(height=20),
                            # Botones
                            ft.Row(
                                [
                                    ft.ElevatedButton(
                                        "Iniciar Desocupación",
                                        icon=ft.Icons.CHECK,
                                        on_click=self._handle_guardar,
                                        bgcolor=colors.PRIMARY,
                                        color="white",
                                    ),
                                    ft.OutlinedButton(
                                        "Cancelar", on_click=lambda e: self.on_cancelar()
                                    ),
                                ],
                                spacing=12,
                            ),
                        ],
                        spacing=16,
                    ),
                    bgcolor=ft.Colors.WHITE,
                    padding=24,
                    border_radius=12,
                    border=ft.border.all(1, ft.Colors.GREY_200),
                ),
            ],
            spacing=8,
        )

    def _cargar_contratos(self):
        """Carga contratos activos disponibles."""
        try:
            contratos_data = self.servicio.listar_contratos_candidatos()
            return [
                ft.dropdown.Option(str(c["id_contrato"]), f"{c['direccion']} - {c['inquilino']}")
                for c in contratos_data
            ]
        except Exception:
            pass  # print(f"Error cargando contratos: {e}") [OpSec Removed]
            return []

    def _on_date_selected(self, e):
        """Callback cuando se selecciona fecha."""
        if e.control.value:
            self.fecha_programada.current.value = e.control.value.strftime("%Y-%m-%d")
            self.fecha_programada.current.update()

    def _show_snackbar(self, page, message, color):
        """Muestra un SnackBar de forma robusta (compatible con versiones)."""
        if not page:
            return

        snack = ft.SnackBar(
            content=ft.Text(message),
            bgcolor=color,
            duration=5000 if color == "green" else 3000,
            action="OK",
        )

        # Intentar método nuevo (Flet 0.21+)
        try:
            page.open(snack)
        except AttributeError:
            # Fallback método antiguo
            page.snack_bar = snack
            page.snack_bar.open = True
            page.update()
        except Exception:
            pass  # print(f"Error mostrando SnackBar: {e}") [OpSec Removed]

    def _handle_guardar(self, e):
        """Valida y guarda la nueva desocupación."""
        current_page = e.page or self.page_ref

        # Validaciones
        if not self.dd_contrato.current.value:
            self._show_snackbar(current_page, "Debes seleccionar un contrato", "red")
            return

        if not self.fecha_programada.current.value:
            self._show_snackbar(current_page, "Debes seleccionar la fecha programada", "red")
            return

        # Crear desocupación
        try:
            pass  # print(f"[DEBUG PDF] Iniciando desocupación para contrato {self.dd_contrato.current.value}") [OpSec Removed]
            nuevo_des = self.servicio.iniciar_desocupacion(
                id_contrato=int(self.dd_contrato.current.value),
                fecha_programada=self.fecha_programada.current.value,
                observaciones=self.txt_observaciones.current.value,
                usuario="admin",  # TODO: Get from session
            )
            pass  # print(f"[DEBUG PDF] Desocupación creada. ID: {nuevo_des.id_desocupacion}") [OpSec Removed]

            # Generar PDF Checklist
            try:
                pass  # print("[DEBUG PDF] Intentando generar PDF...") [OpSec Removed]
                from src.infraestructura.servicios.servicio_documentos_pdf import (
                    ServicioDocumentosPDF,
                )

                servicio_pdf = ServicioDocumentosPDF()

                pass  # print(f"[DEBUG PDF] Recuperando datos para checklist ID: {nuevo_des.id_desocupacion}") [OpSec Removed]
                datos_checklist = self.servicio.obtener_datos_para_checklist(
                    nuevo_des.id_desocupacion
                )
                pass  # print(f"[DEBUG PDF] Datos recuperados: {datos_checklist.keys()}") [OpSec Removed]

                path_pdf = servicio_pdf.generar_checklist_desocupacion(datos_checklist)
                pass  # print(f"[DEBUG PDF] PDF generado exitosamente en: {path_pdf}") [OpSec Removed]

                # --- AUTO-DOWNLOAD (Copiar a Descargas) ---
                try:
                    user_downloads = os.path.join(os.path.expanduser("~"), "Downloads")
                    filename = os.path.basename(path_pdf)
                    dest_path = os.path.join(user_downloads, filename)
                    shutil.copy2(path_pdf, dest_path)
                    pass  # print(f"[DEBUG PDF] Archivo copiado a: {dest_path}") [OpSec Removed]

                    msg_exito = f"Desocupación iniciada. PDF descargado en: {dest_path}"
                except Exception:
                    pass  # print(f"[ERROR PDF] No se pudo copiar a Descargas: {e_copy}") [OpSec Removed]
                    msg_exito = f"Desocupación iniciada. PDF guardado en: {path_pdf}"

            except Exception:
                pass  # print(f"[DEBUG PDF] ERROR CRÍTICO generando PDF: {e_pdf}") [OpSec Removed]
                import traceback

                traceback.print_exc()
                msg_exito = "Desocupación iniciada, pero hubo error generando el PDF."

            self._show_snackbar(current_page, msg_exito, "green")

            self.on_guardar()

        except ValueError as ve:
            self._show_snackbar(current_page, str(ve), "red")
        except Exception as ex:
            self._show_snackbar(current_page, f"Error: {str(ex)}", "red")

    def did_mount(self):
        """Ciclo de vida: Montaje en UI."""
        # Registrar DatePicker en overlay
        if self.date_picker not in self.page_ref.overlay:
            self.page_ref.overlay.append(self.date_picker)
            self.page_ref.update()


def crear_desocupacion_form_view(page, servicio_desocupaciones, on_guardar, on_cancelar):
    return DesocupacionFormView(page, servicio_desocupaciones, on_guardar, on_cancelar)
