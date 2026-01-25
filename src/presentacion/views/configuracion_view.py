"""
Vista de Configuración del Sistema.
Gestiona usuarios, IPC y parámetros del sistema mediante pestañas.
Refactorizado a UserControl asíncrono.
Adaptado a Flet moderno (sin UserControl).
"""

import threading
from datetime import datetime
from typing import Callable, Dict

import flet as ft

from src.dominio.entidades.usuario import Usuario


class ConfiguracionView(ft.Container):
    def __init__(
        self,
        page: ft.Page,
        servicio_configuracion,
        usuario_actual: Usuario,
        on_nuevo_usuario: Callable,
        on_editar_usuario: Callable[[int], None],
    ):
        super().__init__(expand=True, padding=10)
        self.page_ref = page
        self.servicio = servicio_configuracion
        self.usuario_actual = usuario_actual
        self.on_nuevo_usuario = on_nuevo_usuario
        self.on_editar_usuario = on_editar_usuario

        # Estado
        self.usuarios_ref = ft.Ref[ft.DataTable]()
        self.ipc_ref = ft.Ref[ft.DataTable]()
        self.auditoria_ref = ft.Ref[ft.DataTable]()
        self.parametros_container_ref = ft.Ref[ft.Column]()
        self.mostrar_inactivos = ft.Ref[ft.Switch]()

        self.loading_usuarios = ft.ProgressBar(width=400, color="blue", visible=False)
        self.loading_ipc = ft.ProgressBar(width=400, color="blue", visible=False)
        self.loading_auditoria = ft.ProgressBar(width=400, color="blue", visible=False)
        self.loading_params = ft.ProgressBar(width=400, color="blue", visible=False)

        self.campos_parametros: Dict[int, ft.TextField] = {}

        # --- UI Construction (adaptado de build) ---

        # Pestaña 1: Usuarios
        tab_usuarios = ft.Tab(
            text="Usuarios",
            icon=ft.Icons.PEOPLE,
            content=ft.Container(
                padding=20,
                content=ft.Column(
                    [
                        ft.Row(
                            [
                                ft.Text("Gestión de Usuarios", size=24, weight=ft.FontWeight.BOLD),
                                ft.Container(expand=True),
                                ft.Row(
                                    [
                                        ft.Text("Mostrar inactivos"),
                                        ft.Switch(
                                            ref=self.mostrar_inactivos,
                                            value=False,
                                            on_change=lambda e: self.cargar_usuarios(),
                                        ),
                                    ]
                                ),
                                ft.ElevatedButton(
                                    text="Nuevo Usuario",
                                    icon=ft.Icons.PERSON_ADD,
                                    bgcolor=ft.Colors.BLUE,
                                    color=ft.Colors.WHITE,
                                    on_click=lambda e: self.on_nuevo_usuario(),
                                ),
                            ]
                        ),
                        ft.Divider(),
                        ft.Container(content=self.loading_usuarios, alignment=ft.alignment.center),
                        ft.Container(
                            content=ft.DataTable(
                                ref=self.usuarios_ref,
                                columns=[
                                    ft.DataColumn(ft.Text("ID")),
                                    ft.DataColumn(ft.Text("Usuario")),
                                    ft.DataColumn(ft.Text("Rol")),
                                    ft.DataColumn(ft.Text("Estado")),
                                    ft.DataColumn(ft.Text("Último Acceso")),
                                    ft.DataColumn(ft.Text("Acciones")),
                                ],
                                rows=[],
                                border=ft.border.all(1, ft.Colors.GREY_300),
                                border_radius=10,
                                vertical_lines=ft.BorderSide(1, ft.Colors.GREY_200),
                                horizontal_lines=ft.BorderSide(1, ft.Colors.GREY_200),
                            ),
                            expand=True,
                        ),
                    ]
                ),
            ),
        )

        # Pestaña 2: IPC
        tab_ipc = ft.Tab(
            text="IPC",
            icon=ft.Icons.TRENDING_UP,
            content=ft.Container(
                padding=20,
                content=ft.Column(
                    [
                        ft.Row(
                            [
                                ft.Text("Configuración de IPC", size=24, weight=ft.FontWeight.BOLD),
                                ft.Container(expand=True),
                                ft.ElevatedButton(
                                    text="Agregar IPC",
                                    icon=ft.Icons.ADD,
                                    bgcolor=ft.Colors.BLUE,
                                    color=ft.Colors.WHITE,
                                    on_click=lambda e: self.mostrar_dialog_nuevo_ipc(),
                                ),
                            ]
                        ),
                        ft.Divider(),
                        ft.Text(
                            "El IPC se usa para calcular el incremento anual en cánones de arrendamiento.",
                            color=ft.Colors.GREY_600,
                            size=14,
                        ),
                        ft.Container(height=10),
                        ft.Container(content=self.loading_ipc, alignment=ft.alignment.center),
                        ft.Container(
                            content=ft.DataTable(
                                ref=self.ipc_ref,
                                columns=[
                                    ft.DataColumn(ft.Text("Año")),
                                    ft.DataColumn(ft.Text("Valor IPC")),
                                    ft.DataColumn(ft.Text("Fecha Publicación")),
                                    ft.DataColumn(ft.Text("Acciones")),
                                ],
                                rows=[],
                                border=ft.border.all(1, ft.Colors.GREY_300),
                                border_radius=10,
                                vertical_lines=ft.BorderSide(1, ft.Colors.GREY_200),
                                horizontal_lines=ft.BorderSide(1, ft.Colors.GREY_200),
                            ),
                            expand=True,
                        ),
                    ]
                ),
            ),
        )

        # Pestaña 3: Parámetros
        tab_parametros = ft.Tab(
            text="Parámetros",
            icon=ft.Icons.SETTINGS,
            content=ft.Container(
                padding=20,
                content=ft.Column(
                    [
                        ft.Row(
                            [
                                ft.Text(
                                    "Parámetros del Sistema", size=24, weight=ft.FontWeight.BOLD
                                ),
                            ]
                        ),
                        ft.Divider(),
                        ft.Text(
                            "Los parámetros con 🔒 no son modificables.",
                            color=ft.Colors.GREY_600,
                            size=14,
                        ),
                        ft.Container(height=10),
                        ft.Container(content=self.loading_params, alignment=ft.alignment.center),
                        ft.Column(
                            ref=self.parametros_container_ref,
                            controls=[],
                            scroll=ft.ScrollMode.AUTO,
                            expand=True,
                        ),
                    ]
                ),
            ),
        )

        # Pestaña 4: Auditoría
        tab_auditoria = ft.Tab(
            text="Auditoría",
            icon=ft.Icons.HISTORY,
            content=ft.Container(
                padding=20,
                content=ft.Column(
                    [
                        ft.Row(
                            [
                                ft.Text("Auditoría de Cambios", size=24, weight=ft.FontWeight.BOLD),
                                ft.Container(expand=True),
                                ft.IconButton(
                                    icon=ft.Icons.REFRESH,
                                    on_click=lambda e: self.cargar_auditoria(),
                                ),
                            ]
                        ),
                        ft.Divider(),
                        ft.Text(
                            "Historial de cambios importantes en el sistema (últimos 100 registros).",
                            color=ft.Colors.GREY_600,
                            size=14,
                        ),
                        ft.Container(height=10),
                        ft.Container(content=self.loading_auditoria, alignment=ft.alignment.center),
                        ft.Column(
                            [
                                ft.DataTable(
                                    ref=self.auditoria_ref,
                                    columns=[
                                        ft.DataColumn(ft.Text("Fecha")),
                                        ft.DataColumn(ft.Text("Usuario")),
                                        ft.DataColumn(ft.Text("Tabla")),
                                        ft.DataColumn(ft.Text("Acción")),
                                        ft.DataColumn(ft.Text("Detalle")),
                                    ],
                                    rows=[],
                                    border=ft.border.all(1, ft.Colors.GREY_300),
                                    border_radius=10,
                                    vertical_lines=ft.BorderSide(1, ft.Colors.GREY_200),
                                    horizontal_lines=ft.BorderSide(1, ft.Colors.GREY_200),
                                )
                            ],
                            scroll=ft.ScrollMode.AUTO,
                            expand=True,
                        ),
                    ]
                ),
            ),
        )

        self.content = ft.Column(
            [
                ft.Container(
                    content=ft.Row(
                        [
                            ft.Icon(ft.Icons.SETTINGS, size=32, color=ft.Colors.BLUE),
                            ft.Text(
                                "Configuración del Sistema", size=28, weight=ft.FontWeight.BOLD
                            ),
                        ]
                    ),
                    margin=ft.margin.only(bottom=10),
                ),
                ft.Tabs(
                    selected_index=0,
                    animation_duration=300,
                    tabs=[tab_usuarios, tab_ipc, tab_parametros, tab_auditoria],
                    expand=True,
                    on_change=self.on_tab_change,
                ),
            ]
        )

    def did_mount(self):
        self.cargar_usuarios()

    # --- Handlers de Pestañas y Carga (Asíncrono) ---

    def on_tab_change(self, e):
        idx = e.control.selected_index
        if idx == 0:
            self.cargar_usuarios()
        elif idx == 1:
            self.cargar_ipc()
        elif idx == 2:
            self.cargar_parametros()
        elif idx == 3:
            self.cargar_auditoria()

    def cargar_usuarios(self):
        self.loading_usuarios.visible = True
        if self.usuarios_ref.current:
            self.usuarios_ref.current.visible = False
        self.update()

        inactivos = (
            self.mostrar_inactivos.current.value if self.mostrar_inactivos.current else False
        )
        threading.Thread(target=self._fetch_usuarios, args=(inactivos,), daemon=True).start()

    def _fetch_usuarios(self, incluir_inactivos):
        try:
            usuarios = self.servicio.listar_usuarios(incluir_inactivos=incluir_inactivos)
            self._update_usuarios_ui(usuarios)
        except Exception as e:
            self._show_error(f"Error cargando usuarios: {e}")

    def _update_usuarios_ui(self, usuarios):
        rows = []
        for u in usuarios:
            estado_color = ft.Colors.GREEN if u.es_activo() else ft.Colors.RED_400
            estado_texto = "Activo" if u.es_activo() else "Inactivo"

            rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(u.id_usuario))),
                        ft.DataCell(ft.Text(u.nombre_usuario)),
                        ft.DataCell(
                            ft.Container(
                                content=ft.Text(u.rol, color="white", size=12),
                                bgcolor=(
                                    ft.Colors.BLUE if u.rol == "Administrador" else ft.Colors.TEAL
                                ),
                                border_radius=5,
                                padding=ft.padding.symmetric(horizontal=8, vertical=4),
                            )
                        ),
                        ft.DataCell(
                            ft.Container(
                                content=ft.Text(estado_texto, color="white", size=12),
                                bgcolor=estado_color,
                                border_radius=5,
                                padding=ft.padding.symmetric(horizontal=8, vertical=4),
                            )
                        ),
                        ft.DataCell(ft.Text(u.ultimo_acceso[:16] if u.ultimo_acceso else "-")),
                        ft.DataCell(
                            ft.Row(
                                [
                                    ft.IconButton(
                                        ft.Icons.EDIT,
                                        icon_color=ft.Colors.BLUE,
                                        tooltip="Editar",
                                        on_click=lambda e, uid=u.id_usuario: self.on_editar_usuario(
                                            uid
                                        ),
                                    ),
                                    ft.IconButton(
                                        ft.Icons.LOCK_RESET,
                                        icon_color=ft.Colors.ORANGE,
                                        tooltip="Resetear",
                                        on_click=lambda e, uid=u.id_usuario: self.mostrar_dialog_reset(
                                            uid
                                        ),
                                    ),
                                    ft.IconButton(
                                        ft.Icons.BLOCK if u.es_activo() else ft.Icons.CHECK_CIRCLE,
                                        icon_color=(
                                            ft.Colors.RED if u.es_activo() else ft.Colors.GREEN
                                        ),
                                        tooltip="Desactivar" if u.es_activo() else "Reactivar",
                                        on_click=lambda e, uid=u.id_usuario, act=u.es_activo(): self.toggle_estado_usuario(
                                            uid, act
                                        ),
                                    ),
                                ]
                            )
                        ),
                    ]
                )
            )

        if self.usuarios_ref.current:
            self.usuarios_ref.current.rows = rows
            self.usuarios_ref.current.visible = True
        self.loading_usuarios.visible = False
        self.update()

    def cargar_ipc(self):
        self.loading_ipc.visible = True
        if self.ipc_ref.current:
            self.ipc_ref.current.visible = False
        self.update()
        threading.Thread(target=self._fetch_ipc, daemon=True).start()

    def _fetch_ipc(self):
        try:
            lista = self.servicio.listar_ipc()
            self._update_ipc_ui(lista)
        except Exception as e:
            self._show_error(f"Error cargando IPC: {e}")

    def _update_ipc_ui(self, lista):
        rows = []
        for ipc in lista:
            rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(ipc.anio), weight="bold")),
                        ft.DataCell(ft.Text(f"{ipc.valor_ipc/100:.2f}%")),
                        ft.DataCell(
                            ft.Text(ipc.fecha_publicacion[:10] if ipc.fecha_publicacion else "-")
                        ),
                        ft.DataCell(
                            ft.IconButton(
                                ft.Icons.EDIT,
                                icon_color=ft.Colors.BLUE,
                                tooltip="Editar",
                                on_click=lambda e, i=ipc: self.mostrar_dialog_editar_ipc(i),
                            )
                        ),
                    ]
                )
            )
        if self.ipc_ref.current:
            self.ipc_ref.current.rows = rows
            self.ipc_ref.current.visible = True
        self.loading_ipc.visible = False
        self.update()

    def cargar_parametros(self):
        self.loading_params.visible = True
        if self.parametros_container_ref.current:
            self.parametros_container_ref.current.visible = False
        self.update()
        threading.Thread(target=self._fetch_params, daemon=True).start()

    def _fetch_params(self):
        try:
            categorias = self.servicio.listar_categorias()
            data = {}
            for cat in categorias:
                data[cat] = self.servicio.listar_por_categoria(cat)
            self._update_params_ui(data)
        except Exception as e:
            self._show_error(f"Error cargando parámetros: {e}")

    def _update_params_ui(self, data):
        self.campos_parametros.clear()
        panels = []

        for cat, params in data.items():
            campos_cat = []
            for p in params:
                txt = ft.TextField(
                    label=p.nombre_parametro.replace("_", " ").title(),
                    value=p.valor_parametro,
                    helper_text=p.descripcion,
                    disabled=not p.es_modificable,
                    read_only=not p.es_modificable,
                    width=300,
                    prefix_icon=ft.Icons.LOCK if not p.es_modificable else None,
                )
                self.campos_parametros[p.id_parametro] = txt
                campos_cat.append(
                    ft.Container(
                        content=ft.Row([txt, ft.Text(f"({p.tipo_dato})", size=12, color="grey")]),
                        margin=ft.margin.only(bottom=10),
                    )
                )

            btn = ft.ElevatedButton(
                "Guardar Configuración",
                icon=ft.Icons.SAVE,
                bgcolor=ft.Colors.BLUE,
                color=ft.Colors.WHITE,
                on_click=lambda e, c=cat, ps=params: self.guardar_categoria(c, ps),
            )
            campos_cat.append(ft.Container(content=btn, margin=ft.margin.only(top=10)))

            panels.append(
                ft.ExpansionPanel(
                    header=ft.ListTile(
                        leading=self.obtener_icono_categoria(cat),
                        title=ft.Text(cat, weight="bold"),
                        subtitle=ft.Text(f"{len(params)} parámetros"),
                    ),
                    content=ft.Container(content=ft.Column(campos_cat, spacing=5), padding=20),
                )
            )

        if self.parametros_container_ref.current:
            self.parametros_container_ref.current.controls = [
                ft.ExpansionPanelList(
                    elevation=1, expand_icon_color=ft.Colors.BLUE, controls=panels
                )
            ]
            self.parametros_container_ref.current.visible = True

        self.loading_params.visible = False
        self.update()

    def cargar_auditoria(self):
        self.loading_auditoria.visible = True
        if self.auditoria_ref.current:
            self.auditoria_ref.current.visible = False
        self.update()
        threading.Thread(target=self._fetch_auditoria, daemon=True).start()

    def _fetch_auditoria(self):
        try:
            logs = self.servicio.listar_auditoria(limit=100)
            self._update_auditoria_ui(logs)
        except Exception as e:
            self._show_error(f"Error cargando auditoría: {e}")

    def _update_auditoria_ui(self, logs):
        rows = []
        for log in logs:
            # Formatear detalle
            detalle = f"Reg: {log.id_registro}"
            if log.campo:
                detalle += f" | {log.campo}: {log.valor_anterior} -> {log.valor_nuevo}"
            elif log.motivo_cambio:
                detalle += f" | Motivo: {log.motivo_cambio}"

            rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(log.fecha_cambio[:19] if log.fecha_cambio else "-")),
                        ft.DataCell(ft.Text(log.usuario)),
                        ft.DataCell(ft.Text(log.tabla)),
                        ft.DataCell(
                            ft.Container(
                                content=ft.Text(log.accion, color="white", size=12),
                                bgcolor=self._get_accion_color(log.accion),
                                border_radius=5,
                                padding=ft.padding.symmetric(horizontal=8, vertical=4),
                            )
                        ),
                        ft.DataCell(ft.Text(detalle, size=12, overflow=ft.TextOverflow.ELLIPSIS)),
                    ]
                )
            )

        if self.auditoria_ref.current:
            self.auditoria_ref.current.rows = rows
            self.auditoria_ref.current.visible = True

        self.loading_auditoria.visible = False
        self.update()

    def _get_accion_color(self, accion):
        if accion == "INSERT":
            return ft.Colors.GREEN
        if accion == "UPDATE":
            return ft.Colors.ORANGE
        if accion == "DELETE":
            return ft.Colors.RED
        return ft.Colors.BLUE

    def _show_error(self, msg):
        self.loading_usuarios.visible = False
        self.loading_ipc.visible = False
        self.loading_params.visible = False
        self.loading_auditoria.visible = False
        self.page_ref.snack_bar = ft.SnackBar(ft.Text(msg), bgcolor="red")
        self.page_ref.snack_bar.open = True
        self.update()

    # --- Acciones y Diálogos ---

    def obtener_icono_categoria(self, cat):
        iconos = {
            "COMISIONES": ft.Icons.PERCENT,
            "IMPUESTOS": ft.Icons.ACCOUNT_BALANCE,
            "VALIDACIONES": ft.Icons.RULE,
            "ALERTAS": ft.Icons.NOTIFICATIONS,
            "OPERACIONES": ft.Icons.SETTINGS,
            "NOTIFICACIONES": ft.Icons.MESSAGE,
            "SISTEMA": ft.Icons.COMPUTER,
        }
        return ft.Icon(iconos.get(cat, ft.Icons.SETTINGS))

    def toggle_estado_usuario(self, uid, activo):
        try:
            if activo:
                self.servicio.desactivar_usuario(uid, self.usuario_actual.nombre_usuario)
            else:
                self.servicio.reactivar_usuario(uid, self.usuario_actual.nombre_usuario)
            self.cargar_usuarios()
        except Exception as e:
            self._show_error(str(e))

    def mostrar_dialog_reset(self, uid):
        txt = ft.TextField(label="Nueva Contraseña", password=True, can_reveal_password=True)

        def confirmar(e):
            try:
                self.servicio.resetear_contrasena(
                    uid, txt.value, self.usuario_actual.nombre_usuario
                )
                self.page_ref.close(dlg)
                self.page_ref.snack_bar = ft.SnackBar(
                    ft.Text("Contraseña reseteada"), bgcolor="green"
                )
                self.page_ref.snack_bar.open = True
                self.page_ref.update()
            except Exception as ex:
                self._show_error(str(ex))

        dlg = ft.AlertDialog(
            title=ft.Text("Resetear"),
            content=txt,
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: self.page_ref.close(dlg)),
                ft.ElevatedButton("Confirmar", on_click=confirmar),
            ],
        )
        self.page_ref.open(dlg)

    def mostrar_dialog_nuevo_ipc(self):
        anio = ft.TextField(label="Año", value=str(datetime.now().year))
        val = ft.TextField(label="Valor %")

        def confirmar(e):
            try:
                self.servicio.agregar_ipc(
                    int(anio.value), int(float(val.value) * 100), self.usuario_actual.nombre_usuario
                )
                self.page_ref.close(dlg)
                self.cargar_ipc()
            except Exception as ex:
                self._show_error(str(ex))

        dlg = ft.AlertDialog(
            title=ft.Text("Nuevo IPC"),
            content=ft.Column([anio, val], tight=True),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: self.page_ref.close(dlg)),
                ft.ElevatedButton("Guardar", on_click=confirmar),
            ],
        )
        self.page_ref.open(dlg)

    def mostrar_dialog_editar_ipc(self, ipc):
        val = ft.TextField(label="Valor %", value=str(ipc.valor_ipc / 100))

        def confirmar(e):
            try:
                self.servicio.actualizar_ipc(
                    ipc.id_ipc,
                    int(float(val.value) * 100),
                    usuario_sistema=self.usuario_actual.nombre_usuario,
                )
                self.page_ref.close(dlg)
                self.cargar_ipc()
            except Exception as ex:
                self._show_error(str(ex))

        dlg = ft.AlertDialog(
            title=ft.Text(f"Editar IPC {ipc.anio}"),
            content=val,
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: self.page_ref.close(dlg)),
                ft.ElevatedButton("Guardar", on_click=confirmar),
            ],
        )
        self.page_ref.open(dlg)

    def guardar_categoria(self, cat, params):
        try:
            valores = {}
            for p in params:
                if p.es_modificable and p.id_parametro in self.campos_parametros:
                    # Acceder al value de forma segura, el ref ya no es necesario si guardamos el objeto control directamente
                    ctrl = self.campos_parametros[p.id_parametro]
                    if ctrl.value != p.valor_parametro:
                        valores[p.id_parametro] = ctrl.value

            if valores:
                cnt = self.servicio.actualizar_parametros_por_categoria(
                    cat, valores, self.usuario_actual.nombre_usuario
                )
                self.page_ref.snack_bar = ft.SnackBar(
                    ft.Text(f"{cnt} parámetros actualizados"), bgcolor="green"
                )
            else:
                self.page_ref.snack_bar = ft.SnackBar(ft.Text("No hay cambios"), bgcolor="orange")
            self.page_ref.snack_bar.open = True
            self.page_ref.update()
        except Exception as e:
            self._show_error(str(e))


def build_configuracion_view(
    page, servicio_configuracion, usuario_actual, on_nuevo_usuario, on_editar_usuario
):
    return ConfiguracionView(
        page, servicio_configuracion, usuario_actual, on_nuevo_usuario, on_editar_usuario
    )
