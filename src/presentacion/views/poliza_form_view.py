"""
Vista: Formulario de Nueva Póliza
Permite asignar un seguro a un contrato de arrendamiento.
"""

import flet as ft
from datetime import datetime, timedelta
from src.infraestructura.persistencia.database import DatabaseManager
from src.aplicacion.servicios.servicio_seguros import ServicioSeguros
from src.presentacion.theme import colors

def crear_poliza_form_view(page: ft.Page, on_guardar, on_cancelar):
    
    # Servicios
    db_manager = DatabaseManager()
    servicio = ServicioSeguros(db_manager)
    usuario = "admin" # TODO: Tomar usuario real
    
    # Datos para dropdowns
    seguros = servicio.listar_seguros_activos()
    contratos = servicio.listar_contratos_candidatos()
    
    # --- Controles ---
    
    dd_contrato = ft.Dropdown(
        label="Contrato de Arrendamiento *",
        options=[
            ft.dropdown.Option(
                key=str(c['ID_CONTRATO_A']),
                text=f"{c['DIRECCION']} - {c['INQUILINO']}"
            ) for c in contratos
        ],
        expand=True,
        hint_text="Seleccione un contrato activo..."
    )
    
    dd_seguro = ft.Dropdown(
        label="Producto de Seguro *",
        options=[
            ft.dropdown.Option(
                key=str(s.id_seguro),
                text=f"{s.nombre_seguro} ({s.obtener_porcentaje_decimal()}%)"
            ) for s in seguros
        ],
        expand=True
    )
    
    txt_numero_poliza = ft.TextField(
        label="Número de Póliza (Opcional)",
        hint_text="Ej: POL-123456"
    )

    # Fechas
    today = datetime.now()
    next_year = today + timedelta(days=365)
    
    date_inicio = ft.DatePicker(
        first_date=datetime(2020, 1, 1),
        last_date=datetime(2035, 12, 31),
        on_change=lambda e: actualizar_fechas()
    )
    
    date_fin = ft.DatePicker(
        first_date=datetime(2020, 1, 1),
        last_date=datetime(2035, 12, 31),
        on_change=lambda e: actualizar_fechas()
    )
    
    txt_fecha_inicio = ft.TextField(label="Vigencia Desde *", read_only=True, width=160, value=today.strftime("%Y-%m-%d"))
    txt_fecha_fin = ft.TextField(label="Vigencia Hasta *", read_only=True, width=160, value=next_year.strftime("%Y-%m-%d"))

    def actualizar_fechas():
        if date_inicio.value:
            txt_fecha_inicio.value = date_inicio.value.strftime("%Y-%m-%d")
        if date_fin.value:
            txt_fecha_fin.value = date_fin.value.strftime("%Y-%m-%d")
        page.update()

    def guardar(e):
        if not dd_contrato.value:
            mostrar_error("Debe seleccionar un contrato.")
            return
        if not dd_seguro.value:
            mostrar_error("Debe seleccionar un seguro.")
            return
        if not txt_fecha_inicio.value or not txt_fecha_fin.value:
            mostrar_error("Las fechas son obligatorias.")
            return

        try:
            servicio.crear_poliza(
                id_contrato=int(dd_contrato.value),
                id_seguro=int(dd_seguro.value),
                fecha_inicio=txt_fecha_inicio.value,
                fecha_fin=txt_fecha_fin.value,
                numero_poliza=txt_numero_poliza.value or "",
                usuario=usuario
            )
            on_guardar()
            mostrar_exito("Póliza asignada exitosamente.")
        except Exception as ex:
            mostrar_error(str(ex))

    def mostrar_error(msg):
        page.snack_bar = ft.SnackBar(ft.Text(msg), bgcolor=colors.ERROR)
        page.snack_bar.open = True
        page.update()

    def mostrar_exito(msg):
        page.snack_bar = ft.SnackBar(ft.Text(msg), bgcolor=colors.SUCCESS)
        page.snack_bar.open = True
        page.update()

    return ft.Container(
        padding=30,
        content=ft.Column([
            ft.Text("Asignar Seguro a Contrato", size=24, weight="bold"),
            ft.Divider(),
            dd_contrato,
            dd_seguro,
            ft.Row([
                ft.Column([
                    ft.Text("Inicio Vigencia"),
                    ft.Row([txt_fecha_inicio, ft.IconButton(ft.Icons.CALENDAR_MONTH, on_click=lambda e: page.open(date_inicio))])
                ]),
                ft.Column([
                    ft.Text("Fin Vigencia"),
                    ft.Row([txt_fecha_fin, ft.IconButton(ft.Icons.CALENDAR_MONTH, on_click=lambda e: page.open(date_fin))])
                ])
            ], spacing=20),
            txt_numero_poliza,
            ft.Divider(height=20, color="transparent"),
            ft.Row([
                ft.ElevatedButton("Cancelar", on_click=lambda e: on_cancelar(), bgcolor=colors.SECONDARY),
                ft.ElevatedButton("Guardar Póliza", on_click=guardar, bgcolor=colors.PRIMARY, color="white"),
            ], alignment=ft.MainAxisAlignment.END)
        ], scroll=ft.ScrollMode.AUTO)
    )
