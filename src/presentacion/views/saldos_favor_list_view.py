"""
Vista de Lista: Saldos a Favor
Muestra tabla de saldos con filtros y acciones.
Refactorizado a UserControl asíncrono.
Adaptado a Flet moderno (sin UserControl).
"""

import threading
from typing import Any, Callable, Dict, List

import reflex as rx


class SaldosFavorListView(ft.Container):
    def __init__(
        self,
        page: ft.Page,
        servicio_saldos_favor,
        on_nuevo: Callable,
        on_aplicar: Callable[[int], None],
        on_devolver: Callable[[int], None],
        on_eliminar: Callable[[int], None],
        propietarios_data: List[Dict[str, Any]] = None,
        asesores_data: List[Dict[str, Any]] = None,
    ):
        super().__init__(expand=True, padding=24)
        self.page_ref = page
        self.servicio = servicio_saldos_favor
        self.on_nuevo = on_nuevo
        self.on_aplicar = on_aplicar
        self.on_devolver = on_devolver
        self.on_eliminar = on_eliminar

        # Preloaded lookup data (passed from caller usually)
        self.propietarios_dict = {
            p.get("id_propietario"): p.get("nombre", "Desc") for p in (propietarios_data or [])
        }
        self.asesores_dict = {
            a.get("id_asesor"): a.get("nombre", "Desc") for a in (asesores_data or [])
        }

        self.saldos = []

        # Refs
        self.dd_tipo = ft.Ref[ft.Dropdown]()
        self.dd_estado = ft.Ref[ft.Dropdown]()
        self.main_content_ref = ft.Ref[ft.Container]()  # Container principal para swap
        self.txt_pend = ft.Ref[ft.Text]()
        self.txt_res = ft.Ref[ft.Text]()
        self.txt_cant = ft.Ref[ft.Text]()

        # Loading Control (reutilizable)
        self.loading_control = ft.Container(
            content=ft.ProgressBar(width=400, color="blue"), alignment=ft.alignment.center
        )

        # --- Construcción UI (adaptado de build) ---

        filtros = ft.Row(
            [
                ft.Dropdown(
                    ref=self.dd_tipo,
                    label="Tipo Beneficiario",
                    width=200,
                    options=[
                        ft.dropdown.Option("", "Todos"),
                        ft.dropdown.Option("Propietario", "Propietario"),
                        ft.dropdown.Option("Asesor", "Asesor"),
                    ],
                    on_change=lambda e: self.cargar_datos(),
                ),
                ft.Dropdown(
                    ref=self.dd_estado,
                    label="Estado",
                    width=180,
                    options=[
                        ft.dropdown.Option("", "Todos"),
                        ft.dropdown.Option("Pendiente", "Pendiente"),
                        ft.dropdown.Option("Aplicado", "Aplicado"),
                        ft.dropdown.Option("Devuelto", "Devuelto"),
                    ],
                    on_change=lambda e: self.cargar_datos(),
                ),
                ft.Container(expand=True),
                ft.IconButton(
                    icon=ft.Icons.REFRESH,
                    tooltip="Actualizar",
                    on_click=lambda e: self.cargar_datos(),
                ),
                ft.Text(ref=self.txt_cant, value="...", color=ft.Colors.GREY_600),
            ],
            spacing=12,
        )

        self.content = ft.Column(
            [
                ft.Row(
                    [
                        ft.Text("Saldos a Favor", size=28, weight="bold"),
                        ft.Container(expand=True),
                        ft.ElevatedButton(
                            "Nuevo Saldo",
                            icon=ft.Icons.ADD,
                            on_click=lambda e: self.on_nuevo(),
                            style=ft.ButtonStyle(bgcolor=ft.Colors.BLUE_600, color=ft.Colors.WHITE),
                        ),
                    ]
                ),
                ft.Divider(height=20),
                # Resumen
                ft.Row(
                    [
                        ft.Container(
                            content=ft.Column(
                                [
                                    ft.Text("Total Pendiente", color="grey", size=13),
                                    ft.Text(
                                        ref=self.txt_pend,
                                        value="$0",
                                        size=24,
                                        weight="bold",
                                        color="orange",
                                    ),
                                ],
                                spacing=4,
                            ),
                            bgcolor=ft.Colors.ORANGE_50,
                            padding=20,
                            border_radius=12,
                            expand=True,
                        ),
                        ft.Container(
                            content=ft.Column(
                                [
                                    ft.Text("Total Resuelto", color="grey", size=13),
                                    ft.Text(
                                        ref=self.txt_res,
                                        value="$0",
                                        size=24,
                                        weight="bold",
                                        color="green",
                                    ),
                                ],
                                spacing=4,
                            ),
                            bgcolor=ft.Colors.GREEN_50,
                            padding=20,
                            border_radius=12,
                            expand=True,
                        ),
                    ],
                    spacing=16,
                ),
                ft.Container(height=16),
                filtros,
                ft.Container(height=12),
                # Area Principal (Loading o Tabla)
                ft.Container(
                    ref=self.main_content_ref,
                    expand=True,
                    border=ft.border.all(1, ft.Colors.GREY_200),
                    border_radius=8,
                    padding=8,
                ),
            ],
            spacing=8,
            expand=True,
        )

    def did_mount(self):
        self.cargar_datos()

    def cargar_datos(self):
        if self.main_content_ref.current:
            self.main_content_ref.current.content = self.loading_control
            self.main_content_ref.current.update()

        filtros = {"tipo": self.dd_tipo.current.value, "estado": self.dd_estado.current.value}
        threading.Thread(target=self._fetch_data, args=(filtros,), daemon=True).start()

    def _fetch_data(self, filtros):
        try:
            saldos = self.servicio.listar_saldos(
                tipo_beneficiario=filtros["tipo"] or None, estado=filtros["estado"] or None
            )
            self.saldos = saldos

            t_pend = sum(s.valor_saldo for s in saldos if s.estado == "Pendiente")
            t_res = sum(s.valor_saldo for s in saldos if s.estado != "Pendiente")

            self._schedule_ui_update({"pend": t_pend, "res": t_res, "cant": len(saldos)})

        except Exception as e:
            pass  # print(f"Error saldos: {e}") [OpSec Removed]
            self._schedule_ui_update(error=str(e))

    def _schedule_ui_update(self, resumen=None, error=None):
        if error:
            if self.main_content_ref.current:
                self.main_content_ref.current.content = ft.Text(f"Error: {error}", color="red")
                self.main_content_ref.current.update()
            return

        if resumen:
            self.txt_pend.current.value = f"${resumen['pend']:,.0f}"
            self.txt_res.current.value = f"${resumen['res']:,.0f}"
            self.txt_cant.current.value = f"{resumen['cant']} registros"
            self.txt_pend.current.update()
            self.txt_res.current.update()
            self.txt_cant.current.update()

        if self.main_content_ref.current:
            self.main_content_ref.current.content = self._crear_tabla()
            self.main_content_ref.current.update()

    def _crear_tabla(self):
        rows = []
        for s in self.saldos:
            nombre = self.get_nombre_beneficiario(s)
            acciones = []
            if s.esta_pendiente:
                acciones.extend(
                    [
                        ft.IconButton(
                            ft.Icons.CHECK_CIRCLE_OUTLINE,
                            icon_color="green",
                            tooltip="Aplicar",
                            on_click=lambda e, id=s.id_saldo_favor: self.on_aplicar(id),
                        ),
                        ft.IconButton(
                            ft.Icons.REPLY,
                            icon_color="blue",
                            tooltip="Devolver",
                            on_click=lambda e, id=s.id_saldo_favor: self.on_devolver(id),
                        ),
                        ft.IconButton(
                            ft.Icons.DELETE_OUTLINE,
                            icon_color="red",
                            tooltip="Eliminar",
                            on_click=lambda e, id=s.id_saldo_favor: self.on_eliminar(id),
                        ),
                    ]
                )

            rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(s.id_saldo_favor))),
                        ft.DataCell(ft.Text(nombre, max_lines=1)),
                        ft.DataCell(
                            ft.Row(
                                [
                                    ft.Icon(
                                        (
                                            ft.Icons.PERSON
                                            if s.tipo_beneficiario == "Propietario"
                                            else ft.Icons.SUPPORT_AGENT
                                        ),
                                        size=16,
                                    ),
                                    ft.Text(s.tipo_beneficiario),
                                ],
                                spacing=4,
                            )
                        ),
                        ft.DataCell(ft.Text(f"${s.valor_saldo:,.0f}", weight="bold")),
                        ft.DataCell(
                            ft.Text(
                                s.motivo[:30] + "..." if len(s.motivo) > 30 else s.motivo, size=12
                            )
                        ),
                        ft.DataCell(ft.Text(s.fecha_generacion or "-")),
                        ft.DataCell(self.get_estado_chip(s.estado)),
                        ft.DataCell(ft.Row(acciones, spacing=0) if acciones else ft.Text("-")),
                    ]
                )
            )

        return ft.Column(
            [
                ft.DataTable(
                    columns=[
                        ft.DataColumn(ft.Text("ID")),
                        ft.DataColumn(ft.Text("Beneficiario")),
                        ft.DataColumn(ft.Text("Tipo")),
                        ft.DataColumn(ft.Text("Valor")),
                        ft.DataColumn(ft.Text("Motivo")),
                        ft.DataColumn(ft.Text("Fecha")),
                        ft.DataColumn(ft.Text("Estado")),
                        ft.DataColumn(ft.Text("Acciones")),
                    ],
                    rows=rows,
                    border=ft.border.all(1, ft.Colors.GREY_300),
                    border_radius=8,
                )
            ],
            scroll=ft.ScrollMode.AUTO,
        )

    def get_nombre_beneficiario(self, saldo):
        if saldo.tipo_beneficiario == "Propietario":
            return self.propietarios_dict.get(
                saldo.id_propietario, f"Prop. #{saldo.id_propietario}"
            )
        else:
            return self.asesores_dict.get(saldo.id_asesor, f"Asesor #{saldo.id_asesor}")

    def get_estado_chip(self, estado):
        colors = {
            "Pendiente": ("orange", "orange"),
            "Aplicado": ("green", "green"),
            "Devuelto": ("blue", "blue"),
        }
        bg, fg = colors.get(estado, ("grey", "grey"))
        return ft.Container(
            content=ft.Text(estado, color=fg.replace("100", "800"), size=12),
            bgcolor=bg.replace("800", "100"),
            padding=5,
            border_radius=12,
        )


def build_saldos_favor_list_view(
    page,
    servicio_saldos_favor,
    on_nuevo,
    on_aplicar,
    on_devolver,
    on_eliminar,
    propietarios_data=None,
    asesores_data=None,
):
    return SaldosFavorListView(
        page,
        servicio_saldos_favor,
        on_nuevo,
        on_aplicar,
        on_devolver,
        on_eliminar,
        propietarios_data,
        asesores_data,
    )
