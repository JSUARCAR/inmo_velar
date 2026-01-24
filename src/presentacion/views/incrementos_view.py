"""
Vista: Proyección y Aplicación de Incrementos IPC
Permite buscar contratos próximos a vencer y aplicar incrementos masivos.
"""

import flet as ft
from datetime import datetime, timedelta
import threading

class IncrementosView(ft.Container):
    def __init__(self, page: ft.Page, servicio_contratos, usuario_actual):
        super().__init__(expand=True, padding=20)
        self.page_ref = page
        self.servicio = servicio_contratos
        self.usuario = usuario_actual
        
        # Estado
        self.fecha_inicio = datetime.now().replace(day=1) # Primer día del mes
        # Último día del mes actual (simple approx: primer día + 32 días -> replace day 1 - 1 day)
        next_month = self.fecha_inicio + timedelta(days=32)
        self.fecha_fin = next_month.replace(day=1) - timedelta(days=1)
        
        self.resultados = []
        self.seleccionados = set() # Set de IDs seleccionados
        
        # UI Refs
        self.tabla_ref = ft.Ref[ft.DataTable]()
        self.loading = ft.ProgressBar(width=400, color="blue", visible=False)
        self.txt_fecha_inicio = ft.Ref[ft.TextField]()
        self.txt_fecha_fin = ft.Ref[ft.TextField]()
        self.btn_aplicar = ft.Ref[ft.ElevatedButton]()
        
        # Pickers
        self.dp_inicio = ft.DatePicker(
            on_change=self.on_fecha_inicio_change,
            first_date=datetime(2020, 1, 1),
            last_date=datetime(2030, 12, 31)
        )
        self.dp_fin = ft.DatePicker(
            on_change=self.on_fecha_fin_change,
            first_date=datetime(2020, 1, 1),
            last_date=datetime(2030, 12, 31)
        )
        
        # MAIN LAYOUT
        self.content = ft.Column([
            self._build_header(),
            ft.Divider(),
            self._build_filters(),
            ft.Divider(),
            ft.Container(content=self.loading, alignment=ft.alignment.center),
            self._build_table_container(),
        ])

    def did_mount(self):
        # Inicializar fechas en UI
        self.txt_fecha_inicio.current.value = self.fecha_inicio.strftime("%Y-%m-%d")
        self.txt_fecha_fin.current.value = self.fecha_fin.strftime("%Y-%m-%d")
        self.update()
        
        # Cargar datos iniciales
        self.cargar_proyeccion()

    def _build_header(self):
        return ft.Row([
            ft.Icon(ft.Icons.TRENDING_UP, size=32, color=ft.Colors.BLUE),
            ft.Column([
                ft.Text("Incrementos de Canon (IPC)", size=24, weight=ft.FontWeight.BOLD),
                ft.Text("Proyección y aplicación de incrementos anuales", color="grey"),
            ])
        ])

    def _build_filters(self):
        return ft.Row([
            ft.Container(
                content=ft.TextField(
                    ref=self.txt_fecha_inicio,
                    label="Vencimiento Desde",
                    width=150,
                    read_only=True,
                    suffix=ft.IconButton(ft.Icons.CALENDAR_MONTH, on_click=lambda e: self.page_ref.open(self.dp_inicio))
                )
            ),
            ft.Container(
                content=ft.TextField(
                    ref=self.txt_fecha_fin,
                    label="Vencimiento Hasta",
                    width=150,
                    read_only=True,
                    suffix=ft.IconButton(ft.Icons.CALENDAR_MONTH, on_click=lambda e: self.page_ref.open(self.dp_fin))
                )
            ),
            ft.ElevatedButton(
                "Proyectar",
                icon=ft.Icons.SEARCH,
                on_click=lambda e: self.cargar_proyeccion()
            ),
            ft.VerticalDivider(),
            ft.ElevatedButton(
                "Aplicar Seleccionados",
                ref=self.btn_aplicar,
                icon=ft.Icons.DONE_ALL,
                bgcolor=ft.Colors.GREEN,
                color=ft.Colors.WHITE,
                on_click=self.aplicar_incrementos,
                disabled=True
            )
        ], spacing=20)

    def _build_table_container(self):
        return ft.Column(
            controls=[
                ft.Row(
                    [
                        ft.DataTable(
                            ref=self.tabla_ref,
                            columns=[
                                ft.DataColumn(ft.Checkbox(on_change=self.toggle_all)),
                                ft.DataColumn(ft.Text("Propiedad")),
                                ft.DataColumn(ft.Text("Inquilino")),
                                ft.DataColumn(ft.Text("Vence")),
                                ft.DataColumn(ft.Text("Canon Actual"), numeric=True),
                                ft.DataColumn(ft.Text("IPC %"), numeric=True),
                                ft.DataColumn(ft.Text("Nuevo Canon"), numeric=True),
                                ft.DataColumn(ft.Text("Incremento"), numeric=True),
                            ],
                            rows=[],
                            border=ft.border.all(1, ft.Colors.GREY_300),
                            border_radius=10,
                            vertical_lines=ft.BorderSide(1, ft.Colors.GREY_200),
                            horizontal_lines=ft.BorderSide(1, ft.Colors.GREY_200),
                        )
                    ],
                    scroll=ft.ScrollMode.AUTO, # Horizontal scroll
                    expand=True
                )
            ],
            expand=True,
            scroll=ft.ScrollMode.AUTO # Vertical scroll
        )

    # --- DATOS & LÓGICA ---

    def cargar_proyeccion(self):
        self.loading.visible = True
        self.tabla_ref.current.visible = False
        self.btn_aplicar.current.disabled = True
        self.seleccionados.clear()
        self.update()
        
        f_ini = self.txt_fecha_inicio.current.value
        f_fin = self.txt_fecha_fin.current.value
        
        threading.Thread(target=self._fetch_data, args=(f_ini, f_fin), daemon=True).start()

    def _fetch_data(self, ini, fin):
        try:
            self.resultados = self.servicio.listar_arrendamientos_por_vencimiento(ini, fin)
            self._update_ui()
        except Exception as e:
            self._show_error(f"Error cargando proyección: {e}")

    def _update_ui(self):
        rows = []
        for item in self.resultados:
            # Checkbox individual
            chk = ft.Checkbox(
                value=item['id'] in self.seleccionados,
                on_change=lambda e, i=item['id']: self.toggle_one(i, e.control.value)
            )
            
            rows.append(ft.DataRow(cells=[
                ft.DataCell(chk),
                ft.DataCell(ft.Text(item['propiedad'], size=12, width=150, overflow=ft.TextOverflow.ELLIPSIS, tooltip=item['propiedad'])),
                ft.DataCell(ft.Text(item['arrendatario'], size=12)),
                ft.DataCell(ft.Text(item['fecha_vencimiento'])),
                ft.DataCell(ft.Text(f"${item['canon_actual']:,.0f}")),
                ft.DataCell(ft.Text(f"{item['ipc_porcentaje']}%", color="blue", weight="bold")),
                ft.DataCell(ft.Text(f"${item['canon_proyectado']:,.0f}", weight="bold")),
                ft.DataCell(ft.Text(f"+${item['incremento_valor']:,.0f}", color="green", size=11)),
            ]))
            
        if not self.resultados:
             rows.append(ft.DataRow(cells=[ft.DataCell(ft.Text("No se encontraron contratos venciendo en este periodo.")) for _ in range(8)]))

        self.tabla_ref.current.rows = rows
        self.tabla_ref.current.visible = True
        self.loading.visible = False
        self._update_btn_aplicar()
        self.update()

    # --- SELECCIÓN ---
    
    def toggle_all(self, e):
        checked = e.control.value
        if checked:
            self.seleccionados = {item['id'] for item in self.resultados}
        else:
            self.seleccionados.clear()
        
        # Actualizar checkboxes visualmente
        for row in self.tabla_ref.current.rows:
            if isinstance(row.cells[0].content, ft.Checkbox):
                row.cells[0].content.value = checked
        
        self._update_btn_aplicar()
        self.update()

    def toggle_one(self, uid, checked):
        if checked:
            self.seleccionados.add(uid)
        else:
            self.seleccionados.discard(uid)
        self._update_btn_aplicar()
        self.update() # Refrescar estado botón

    def _update_btn_aplicar(self):
        self.btn_aplicar.current.disabled = len(self.seleccionados) == 0
        self.btn_aplicar.current.text = f"Aplicar ({len(self.seleccionados)})"

    # --- ACCIONES ---

    def aplicar_incrementos(self, e):
        if not self.seleccionados: return
        
        def confirm_action(e):
            self.page_ref.close(dlg)
            self._ejecutar_aplicacion()

        dlg = ft.AlertDialog(
            title=ft.Text("Confirmar Incrementos"),
            content=ft.Text(f"¿Está seguro de renovar {len(self.seleccionados)} contratos aplicando el IPC actual?"),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: self.page_ref.close(dlg)),
                ft.ElevatedButton("Confirmar", on_click=confirm_action, bgcolor="green", color="white")
            ]
        )
        self.page_ref.open(dlg)

    def _ejecutar_aplicacion(self):
        self.loading.visible = True
        self.update()
        
        threading.Thread(target=self._process_application, daemon=True).start()

    def _process_application(self):
        exitos = 0
        errores = []
        for uid in self.seleccionados:
            try:
                self.servicio.renovar_arrendamiento(uid, self.usuario.nombre_usuario)
                exitos += 1
            except Exception as e:
                errores.append(f"ID {uid}: {str(e)}")
        
        # Finalizar
        self.cargar_proyeccion() # Recargar tabla
        
        msg = f"Proceso finalizado. Exitos: {exitos}. Errores: {len(errores)}"
        if errores:
            pass  # print(f"Errores en masivo: {errores}") [OpSec Removed]
        
        self._show_snack(msg, color="green" if not errores else "orange")

    # --- UTILS ---

    def on_fecha_inicio_change(self, e):
        if self.dp_inicio.value:
            self.txt_fecha_inicio.current.value = self.dp_inicio.value.strftime("%Y-%m-%d")
            self.update()

    def on_fecha_fin_change(self, e):
        if self.dp_fin.value:
            self.txt_fecha_fin.current.value = self.dp_fin.value.strftime("%Y-%m-%d")
            self.update()

    def _show_error(self, msg):
        self.loading.visible = False
        self.update()
        self._show_snack(msg, color="red")

    def _show_snack(self, msg, color="green"):
        self.page_ref.snack_bar = ft.SnackBar(ft.Text(msg), bgcolor=color)
        self.page_ref.snack_bar.open = True
        self.page_ref.update()

def build_incrementos_view(page, servicio_contratos, usuario_actual):
    return IncrementosView(page, servicio_contratos, usuario_actual)
