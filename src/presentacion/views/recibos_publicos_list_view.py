"""
Vista: Lista de Recibos Públicos
Muestra todos los recibos de servicios públicos (Agua, Luz, Gas, etc.) con filtros.
Refactorizado a UserControl asíncrono.
Adaptado a Flet moderno (sin UserControl).
"""

import threading
from typing import Callable

import reflex as rx


class RecibosPublicosListView(ft.Container):
    def __init__(
        self,
        page: ft.Page,
        servicio_recibos_publicos,
        servicio_propiedades,
        servicio_notificaciones,
        on_nuevo_recibo: Callable,
        on_editar_recibo: Callable[[int], None],
        on_marcar_pagado: Callable[[int], None],
        on_eliminar_recibo: Callable[[int], None],
        on_ver_detalle: Callable[[int], None] = None,
    ):
        super().__init__(expand=True, padding=30)
        self.page_ref = page
        self.servicio = servicio_recibos_publicos
        self.servicio_propiedades = servicio_propiedades
        self.servicio_notificaciones = servicio_notificaciones
        self.on_nuevo_recibo = on_nuevo_recibo
        self.on_editar_recibo = on_editar_recibo
        self.on_marcar_pagado = on_marcar_pagado
        self.on_eliminar_recibo = on_eliminar_recibo
        self.on_ver_detalle = on_ver_detalle

        # Estado
        self.data_recibos = []
        self.cache_propiedades = {}
        self.opciones_propiedades = []

        # Refs
        self.filtro_propiedad = ft.Ref[ft.Dropdown]()
        self.filtro_periodo_desde = ft.Ref[ft.TextField]()
        self.filtro_periodo_hasta = ft.Ref[ft.TextField]()
        self.filtro_tipo_servicio = ft.Ref[ft.Dropdown]()
        self.filtro_estado = ft.Ref[ft.Dropdown]()

        # Container principal de resultados (Loading o Data)
        self.results_container_ref = ft.Ref[ft.Container]()

        self.res_pend = ft.Ref[ft.Text]()
        self.res_venc = ft.Ref[ft.Text]()
        self.res_pagd = ft.Ref[ft.Text]()

        # Loading Control (reutilizable)
        self.loading_control = ft.Container(
            content=ft.ProgressBar(width=400, color="blue"),
            alignment=ft.alignment.center,
            padding=20,
        )

        # --- Construcción UI (adaptado de build) ---

        # Filtros UI
        filtros_section = ft.Container(
            content=ft.Column(
                [
                    ft.Text("Filtros", size=18, weight=ft.FontWeight.BOLD),
                    ft.Divider(height=1, color="#e0e0e0"),
                    ft.ResponsiveRow(
                        [
                            ft.Dropdown(
                                ref=self.filtro_propiedad,
                                col={"sm": 12, "md": 6, "lg": 3},
                                label="Propiedad",
                                hint_text="Cargando...",
                                options=[],  # Async load
                                prefix_icon=ft.Icons.HOME,
                                text_size=14,
                                on_change=lambda e: self.cargar_datos(mantener_opciones=True),
                            ),
                            ft.TextField(
                                ref=self.filtro_periodo_desde,
                                col={"sm": 12, "md": 6, "lg": 2},
                                label="Período Desde",
                                hint_text="YYYY-MM",
                                on_change=lambda e: self.cargar_datos(mantener_opciones=True),
                            ),
                            ft.TextField(
                                ref=self.filtro_periodo_hasta,
                                col={"sm": 12, "md": 6, "lg": 2},
                                label="Período Hasta",
                                hint_text="YYYY-MM",
                                on_change=lambda e: self.cargar_datos(mantener_opciones=True),
                            ),
                            ft.Dropdown(
                                ref=self.filtro_tipo_servicio,
                                col={"sm": 12, "md": 6, "lg": 2},
                                label="Tipo Servicio",
                                hint_text="Todos",
                                options=[
                                    ft.dropdown.Option("Agua"),
                                    ft.dropdown.Option("Luz"),
                                    ft.dropdown.Option("Gas"),
                                    ft.dropdown.Option("Internet"),
                                    ft.dropdown.Option("Teléfono"),
                                    ft.dropdown.Option("Aseo"),
                                    ft.dropdown.Option("Otros"),
                                ],
                                on_change=lambda e: self.cargar_datos(mantener_opciones=True),
                            ),
                            ft.Dropdown(
                                ref=self.filtro_estado,
                                col={"sm": 12, "md": 6, "lg": 2},
                                label="Estado",
                                hint_text="Todos",
                                options=[
                                    ft.dropdown.Option("Todos"),
                                    ft.dropdown.Option("Pendiente"),
                                    ft.dropdown.Option("Pagado"),
                                    ft.dropdown.Option("Vencido"),
                                ],
                                on_change=lambda e: self.cargar_datos(mantener_opciones=True),
                            ),
                        ]
                    ),
                    ft.Row(
                        [
                            ft.ElevatedButton(
                                "Aplicar",
                                icon=ft.Icons.FILTER_ALT,
                                on_click=lambda e: self.cargar_datos(mantener_opciones=True),
                                bgcolor="#4caf50",
                                color="white",
                            ),
                            ft.OutlinedButton(
                                "Limpiar", icon=ft.Icons.CLEAR, on_click=self.limpiar_filtros
                            ),
                        ],
                        spacing=10,
                    ),
                ]
            ),
            bgcolor="white",
            padding=20,
            border_radius=8,
            border=ft.border.all(1, "#e0e0e0"),
        )

        # Resumen Section
        resumen_section = ft.Container(
            content=ft.ResponsiveRow(
                [
                    self._crear_card_resumen(
                        "Total Pendiente", ft.Icons.PENDING_ACTIONS, "#ff9800", self.res_pend
                    ),
                    self._crear_card_resumen(
                        "Total Vencido", ft.Icons.WARNING, "#f44336", self.res_venc
                    ),
                    self._crear_card_resumen(
                        "Total Pagado", ft.Icons.CHECK_CIRCLE, "#4caf50", self.res_pagd
                    ),
                ]
            ),
            padding=ft.padding.only(bottom=20),
        )

        self.content = ft.Column(
            [
                # Breadcrumbs & Header
                ft.Row(
                    [
                        ft.Text("Inicio", size=14, color="#666"),
                        ft.Text(" > ", size=14, color="#666"),
                        ft.Text(
                            "Recibos Públicos", size=14, weight=ft.FontWeight.BOLD, color="#1976d2"
                        ),
                    ]
                ),
                ft.Divider(height=20, color="transparent"),
                ft.Row(
                    [
                        ft.Text("Gestión de Recibos Públicos", size=28, weight=ft.FontWeight.BOLD),
                        ft.Container(expand=True),
                        ft.ElevatedButton(
                            "+ Nuevo Recibo",
                            icon=ft.Icons.ADD,
                            on_click=lambda e: self.on_nuevo_recibo(),
                            bgcolor="#1976d2",
                            color="white",
                            height=45,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                ft.Divider(height=20, color="transparent"),
                resumen_section,
                filtros_section,
                ft.Divider(height=20, color="transparent"),
                # Container Principal para Resultados (Loading / ResumenProp + Tabla)
                ft.Container(ref=self.results_container_ref, expand=True),
            ],
            scroll=ft.ScrollMode.AUTO,
            spacing=0,
        )

    def _crear_card_resumen(self, titulo, icon, color, ref):
        return ft.Container(
            col={"sm": 12, "md": 4},
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Icon(icon, size=40, color=color),
                        ft.Text(titulo, size=14, color="#666"),
                        ft.Text(
                            ref=ref, value="$0", size=24, weight=ft.FontWeight.BOLD, color=color
                        ),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=8,
                ),
                bgcolor="white",
                padding=20,
                border_radius=8,
                border=ft.border.all(2, color),
            ),
        )

    def did_mount(self):
        self.cargar_datos(mantener_opciones=False)

    def limpiar_filtros(self, e):
        self.filtro_propiedad.current.value = None
        self.filtro_periodo_desde.current.value = ""
        self.filtro_periodo_hasta.current.value = ""
        self.filtro_tipo_servicio.current.value = None
        self.filtro_estado.current.value = None
        self.update()
        self.cargar_datos(mantener_opciones=True)

    def cargar_datos(self, mantener_opciones=False):
        # Mostrar Loading
        if self.results_container_ref.current:
            self.results_container_ref.current.content = self.loading_control
            self.results_container_ref.current.update()

        filtros = {
            "propiedad": self.filtro_propiedad.current.value,
            "desde": self.filtro_periodo_desde.current.value,
            "hasta": self.filtro_periodo_hasta.current.value,
            "servicio": self.filtro_tipo_servicio.current.value,
            "estado": self.filtro_estado.current.value,
        }

        threading.Thread(
            target=self._fetch_data, args=(filtros, mantener_opciones), daemon=True
        ).start()

    def _fetch_data(self, filtros, mantener_opciones):
        try:
            # 1. Update vencimientos
            try:
                self.servicio.verificar_vencimientos("sistema")
            except:
                pass

            # 2. Cargar opciones propiedades (primera vez)
            if not mantener_opciones:
                try:
                    municipios = self.servicio_propiedades.obtener_municipios_disponibles()
                    map_m = {m["id"]: m["nombre"] for m in municipios}
                    props = self.servicio_propiedades.listar_propiedades()
                    opciones = []
                    cache_p = {}
                    for p in props:
                        muni = map_m.get(p.id_municipio, "Desc")
                        opciones.append(
                            ft.dropdown.Option(
                                key=str(p.id_propiedad), text=f"{p.direccion_propiedad} - {muni}"
                            )
                        )
                        cache_p[p.id_propiedad] = p.direccion_propiedad

                    self.opciones_propiedades = opciones
                    self.cache_propiedades = cache_p
                except:
                    pass

            # 3. Listar Recibos
            id_prop = int(filtros["propiedad"]) if filtros["propiedad"] else None
            estado = filtros["estado"] if filtros["estado"] != "Todos" else None

            data = self.servicio.listar_con_filtros(
                id_propiedad=id_prop,
                periodo_inicio=filtros["desde"] or None,
                periodo_fin=filtros["hasta"] or None,
                tipo_servicio=filtros["servicio"] or None,
                estado=estado,
            )
            self.data_recibos = data

            # 4. Calcular Resumenes
            t_pend = sum(r.valor_recibo for r in data if r.estado == "Pendiente")
            t_venc = sum(r.valor_recibo for r in data if r.esta_vencido and not r.esta_pagado)
            t_pagd = sum(r.valor_recibo for r in data if r.esta_pagado)

            # 5. Resumen Propiedad (si filtro activo)
            resumen_props = None
            if id_prop:
                recibos_prop = self.servicio.obtener_por_propiedad(id_prop)
                resumen_props = self._calcular_resumen_propiedad(recibos_prop)

            self._schedule_ui_update(
                resumen={"pend": t_pend, "venc": t_venc, "pagd": t_pagd},
                resumen_props=resumen_props,
                update_opciones=not mantener_opciones,
            )

        except Exception as e:
            pass  # print(f"Error recibos: {e}") [OpSec Removed]
            self._schedule_ui_update(error=str(e))

    def _calcular_resumen_propiedad(self, recibos):
        servicios_resumen = {}
        for recibo in recibos:
            tipo = recibo.tipo_servicio
            if tipo not in servicios_resumen:
                servicios_resumen[tipo] = {
                    "total": 0,
                    "pendiente": 0,
                    "vencido": 0,
                    "pagado": 0,
                    "count": 0,
                }

            data = servicios_resumen[tipo]
            data["total"] += recibo.valor_recibo
            data["count"] += 1
            if recibo.esta_pagado:
                data["pagado"] += recibo.valor_recibo
            elif recibo.esta_vencido:
                data["vencido"] += recibo.valor_recibo
            else:
                data["pendiente"] += recibo.valor_recibo
        return servicios_resumen

    def _schedule_ui_update(
        self, resumen=None, resumen_props=None, update_opciones=False, error=None
    ):
        if error:
            if self.results_container_ref.current:
                self.results_container_ref.current.content = ft.Text(f"Error: {error}", color="red")
                self.results_container_ref.current.update()
            return

        # Updates de referencias fuera del results container (filtros/headers)
        if update_opciones:
            self.filtro_propiedad.current.options = self.opciones_propiedades
            self.filtro_propiedad.current.update()

        if resumen:
            self.res_pend.current.value = f"${resumen['pend']:,}"
            self.res_venc.current.value = f"${resumen['venc']:,}"
            self.res_pagd.current.value = f"${resumen['pagd']:,}"
            self.res_pend.current.update()
            self.res_venc.current.update()
            self.res_pagd.current.update()

        # Construir contenido de resultados
        content_results = []

        # 1. Resumen Propiedad (Si aplica)
        if resumen_props:
            filas_res = []
            for s, d in resumen_props.items():
                filas_res.append(
                    ft.DataRow(
                        cells=[
                            ft.DataCell(ft.Text(s)),
                            ft.DataCell(ft.Text(str(d["count"]))),
                            ft.DataCell(ft.Text(f"${d['total']:,}")),
                            ft.DataCell(ft.Text(f"${d['pendiente']:,}")),
                            ft.DataCell(ft.Text(f"${d['vencido']:,}")),
                            ft.DataCell(ft.Text(f"${d['pagado']:,}")),
                        ]
                    )
                )

            tbl_res = ft.DataTable(
                columns=[
                    ft.DataColumn(ft.Text("Servicio")),
                    ft.DataColumn(ft.Text("#")),
                    ft.DataColumn(ft.Text("Total")),
                    ft.DataColumn(ft.Text("Pend")),
                    ft.DataColumn(ft.Text("Venc")),
                    ft.DataColumn(ft.Text("Pag")),
                ],
                rows=filas_res,
                border=ft.border.all(1, "#e0e0e0"),
                border_radius=8,
            )
            content_results.append(
                ft.Container(
                    content=ft.Column(
                        [ft.Text("Resumen de Propiedad", weight="bold", size=16), tbl_res]
                    ),
                    bgcolor="white",
                    padding=20,
                    border_radius=8,
                    border=ft.border.all(1, "#e0e0e0"),
                )
            )
            content_results.append(ft.Divider(height=10, color="transparent"))

        # 2. Main Table
        content_results.append(self._crear_tabla_recibos())

        # Swap content in Results Container
        if self.results_container_ref.current:
            self.results_container_ref.current.content = ft.Column(content_results, spacing=10)
            self.results_container_ref.current.update()

    def _crear_tabla_recibos(self):
        if not self.data_recibos:
            return ft.Container(
                content=ft.Text("No hay recibos", size=16, color="#999"),
                padding=50,
                alignment=ft.alignment.center,
            )

        filas = []
        for rec in self.data_recibos:
            color = {"Pagado": "#4caf50", "Pendiente": "#ff9800", "Vencido": "#f44336"}.get(
                rec.estado, "grey"
            )
            acciones = [
                ft.IconButton(
                    ft.Icons.VISIBILITY,
                    icon_color="#1976d2",
                    tooltip="Ver",
                    on_click=lambda e, id=rec.id_recibo_publico: (
                        self.on_ver_detalle(id) if self.on_ver_detalle else None
                    ),
                )
            ]

            if not rec.esta_pagado:
                acciones.append(
                    ft.IconButton(
                        ft.Icons.EDIT,
                        icon_color="#2196f3",
                        tooltip="Editar",
                        on_click=lambda e, id=rec.id_recibo_publico: self.on_editar_recibo(id),
                    )
                )
                acciones.append(
                    ft.IconButton(
                        ft.Icons.PAYMENT,
                        icon_color="#4caf50",
                        tooltip="Pagar",
                        on_click=lambda e, id=rec.id_recibo_publico: self.on_marcar_pagado(id),
                    )
                )
                acciones.append(
                    ft.IconButton(
                        ft.Icons.DELETE,
                        icon_color="#f44336",
                        tooltip="Eliminar",
                        on_click=lambda e, id=rec.id_recibo_publico: self.on_eliminar_recibo(id),
                    )
                )
            else:
                acciones.append(ft.Icon(ft.Icons.CHECK_CIRCLE, color="#4caf50"))

            filas.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(rec.tipo_servicio)),
                        ft.DataCell(
                            ft.Text(
                                self.cache_propiedades.get(rec.id_propiedad, "N/A")[:20] + "..."
                            )
                        ),
                        ft.DataCell(ft.Text(rec.periodo_recibo)),
                        ft.DataCell(ft.Text(f"${rec.valor_recibo:,}")),
                        ft.DataCell(ft.Text(rec.fecha_vencimiento or "N/A")),
                        ft.DataCell(
                            ft.Container(
                                content=ft.Text(rec.estado, color="white", size=11, weight="bold"),
                                bgcolor=color,
                                padding=5,
                                border_radius=4,
                            )
                        ),
                        ft.DataCell(ft.Row(acciones, spacing=0)),
                    ]
                )
            )

        return ft.Container(
            content=ft.DataTable(
                columns=[
                    ft.DataColumn(ft.Text("Servicio")),
                    ft.DataColumn(ft.Text("Propiedad")),
                    ft.DataColumn(ft.Text("Período")),
                    ft.DataColumn(ft.Text("Valor")),
                    ft.DataColumn(ft.Text("Vence")),
                    ft.DataColumn(ft.Text("Estado")),
                    ft.DataColumn(ft.Text("Acciones")),
                ],
                rows=filas,
                border=ft.border.all(1, "#e0e0e0"),
                border_radius=8,
            ),
            bgcolor="white",
            padding=10,
            border_radius=8,
        )


def crear_recibos_publicos_list_view(
    page,
    servicio_recibos_publicos,
    servicio_propiedades,
    servicio_notificaciones,
    on_nuevo_recibo,
    on_editar_recibo,
    on_marcar_pagado,
    on_eliminar_recibo,
    on_ver_detalle=None,
):
    return RecibosPublicosListView(
        page,
        servicio_recibos_publicos,
        servicio_propiedades,
        servicio_notificaciones,
        on_nuevo_recibo,
        on_editar_recibo,
        on_marcar_pagado,
        on_eliminar_recibo,
        on_ver_detalle,
    )
