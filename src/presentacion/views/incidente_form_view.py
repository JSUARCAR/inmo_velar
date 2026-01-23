from typing import Callable, Optional
import flet as ft
from src.aplicacion.servicios.servicio_incidentes import ServicioIncidentes
from src.aplicacion.servicios.servicio_propiedades import ServicioPropiedades
from src.aplicacion.servicios.servicio_proveedores import ServicioProveedores

class IncidenteFormView(ft.Column):
    """
    Vista de formulario mejorada para reportar incidentes.
    Incluye validaciones completas, asignación de proveedor y responsable de pago.
    """
    def __init__(self, page: ft.Page, servicio_incidentes: ServicioIncidentes, db_manager, on_navigate: Callable):
        super().__init__(spacing=20, scroll=ft.ScrollMode.AUTO)
        self.page = page
        self.servicio = servicio_incidentes
        self.on_navigate = on_navigate
        self.servicio_propiedades = ServicioPropiedades(db_manager)
        self.servicio_proveedores = ServicioProveedores(db_manager)
        
        self._construir_formulario()
        self.cargar_datos_iniciales()

    def _construir_formulario(self):
        """Construye todos los componentes del formulario."""
        
        # Header
        header = ft.Container(
            content=ft.Row([
                ft.IconButton(
                    icon=ft.Icons.ARROW_BACK,
                    tooltip="Volver",
                    on_click=lambda _: self.on_navigate("incidentes")
                ),
                ft.Text("Reportar Nuevo Incidente", size=24, weight=ft.FontWeight.BOLD),
            ]),
            margin=ft.margin.only(bottom=10)
        )
        
        # Sección: Información del Incidente
        self.dd_propiedad = ft.Dropdown(
            label="Propiedad *",
            options=[],
            width=500,
            hint_text="Seleccione la propiedad afectada"
        )
        
        self.txt_descripcion = ft.TextField(
            label="Descripción del Incidente *",
            multiline=True,
            min_lines=3,
            max_lines=6,
            hint_text="Describa detalladamente el problema o daño",
            width=500
        )
        
        self.dd_prioridad = ft.Dropdown(
            label="Prioridad *",
            options=[
                ft.dropdown.Option("Baja", text="🟢 Baja - No urgente"),
                ft.dropdown.Option("Media", text="🟡 Media - Requiere atención"),
                ft.dropdown.Option("Alta", text="🟠 Alta - Urgente"),
                ft.dropdown.Option("Urgente", text="🔴 Urgente - Emergencia"),
            ],
            value="Media",
            width=240
        )
        
        self.dd_origen = ft.Dropdown(
            label="Origen del Reporte *",
            options=[
                ft.dropdown.Option("Inquilino", text="👤 Inquilino"),
                ft.dropdown.Option("Propietario", text="🏠 Propietario"),
                ft.dropdown.Option("Inmobiliaria", text="🏢 Inmobiliaria"),
            ],
            value="Inquilino",
            width=240
        )
        
        info_section = ft.Container(
            content=ft.Column([
                ft.Text("📋 Información del Incidente", size=16, weight=ft.FontWeight.BOLD),
                ft.Divider(height=10),
                self.dd_propiedad,
                self.txt_descripcion,
                ft.Row([self.dd_prioridad, self.dd_origen], spacing=20),
            ], spacing=15),
            padding=20,
            border=ft.border.all(1, ft.Colors.GREY_300),
            border_radius=10
        )
        
        # Sección: Asignación (Opcional)
        self.dd_responsable_pago = ft.Dropdown(
            label="Responsable de Pago",
            options=[
                ft.dropdown.Option("", text="Sin asignar"),
                ft.dropdown.Option("Inquilino", text="👤 Inquilino"),
                ft.dropdown.Option("Propietario", text="🏠 Propietario"),
                ft.dropdown.Option("Inmobiliaria", text="🏢 Inmobiliaria"),
                ft.dropdown.Option("Aseguradora", text="🛡️ Aseguradora"),
            ],
            value="",
            expand=True,
            hint_text="Opcional"
        )
        
        self.dd_proveedor = ft.Dropdown(
            label="Proveedor Sugerido",
            options=[],
            expand=True,
            hint_text="Opcional - Asignar después"
        )
        
        asignacion_section = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Text("⚙️ Asignación Inicial", size=16, weight=ft.FontWeight.BOLD),
                    ft.Text("(Opcional)", size=12, color=ft.Colors.GREY_600, italic=True)
                ], spacing=10),
                ft.Divider(height=10),
                ft.Row([self.dd_responsable_pago, self.dd_proveedor], spacing=20),
            ], spacing=15),
            padding=20,
            border=ft.border.all(1, ft.Colors.GREY_300),
            border_radius=10
        )
        
        # Sección: Observaciones
        self.txt_observaciones = ft.TextField(
            label="Observaciones Adicionales",
            multiline=True,
            min_lines=2,
            max_lines=4,
            hint_text="Notas internas, referencias, etc.",
            width=500
        )
        
        observaciones_section = ft.Container(
            content=ft.Column([
                ft.Text("📝 Observaciones", size=16, weight=ft.FontWeight.BOLD),
                ft.Divider(height=10),
                self.txt_observaciones,
            ], spacing=15),
            padding=20,
            border=ft.border.all(1, ft.Colors.GREY_300),
            border_radius=10
        )
        
        # Mensaje de error
        self.txt_error = ft.Text("", color=ft.Colors.RED_600, visible=False)
        
        # Botones de acción
        acciones = ft.Row([
            ft.OutlinedButton(
                "Cancelar",
                icon=ft.Icons.CANCEL,
                on_click=lambda _: self.on_navigate("incidentes")
            ),
            ft.ElevatedButton(
                "📤 Reportar Incidente",
                on_click=self.guardar_incidente,
                bgcolor=ft.Colors.BLUE_600,
                color=ft.Colors.WHITE,
                height=45
            ),
        ], alignment=ft.MainAxisAlignment.END, spacing=15)
        
        # Ensamblar formulario
        self.controls = [
            ft.Container(
                content=ft.Column([
                    header,
                    info_section,
                    asignacion_section,
                    observaciones_section,
                    self.txt_error,
                    acciones,
                ], spacing=20),
                width=600,
                padding=20
            )
        ]

    def cargar_datos_iniciales(self):
        """Carga las propiedades y proveedores disponibles."""
        self.cargar_propiedades()
        self.cargar_proveedores()

    def cargar_propiedades(self):
        """Carga la lista de propiedades en el dropdown."""
        try:
            props = self.servicio_propiedades.listar_propiedades()
            self.dd_propiedad.options = [
                ft.dropdown.Option(
                    key=str(p.id_propiedad), 
                    text=f"📍 {p.direccion_propiedad} ({p.matricula_inmobiliaria})"
                ) for p in props
            ]
        except Exception as ex:
            print(f"Error cargando propiedades: {ex}")
            self.dd_propiedad.options = []

    def cargar_proveedores(self):
        """Carga la lista de proveedores en el dropdown."""
        try:
            proveedores = self.servicio_proveedores.listar_proveedores()
            self.dd_proveedor.options = [
                ft.dropdown.Option(key="", text="Sin asignar")
            ] + [
                ft.dropdown.Option(
                    key=str(p.id_proveedor), 
                    text=f"🔧 {p.especialidad} - {p.nombre_completo}"
                ) for p in proveedores
            ]
        except Exception as ex:
            print(f"Error cargando proveedores: {ex}")
            self.dd_proveedor.options = [ft.dropdown.Option(key="", text="Sin asignar")]

    def validar_formulario(self) -> tuple[bool, str]:
        """Valida los campos obligatorios del formulario."""
        if not self.dd_propiedad.value:
            return False, "Debe seleccionar una propiedad"
        
        if not self.txt_descripcion.value or len(self.txt_descripcion.value.strip()) < 10:
            return False, "La descripción debe tener al menos 10 caracteres"
        
        if not self.dd_prioridad.value:
            return False, "Debe seleccionar una prioridad"
        
        if not self.dd_origen.value:
            return False, "Debe seleccionar el origen del reporte"
        
        return True, ""

    def guardar_incidente(self, e):
        """Guarda el incidente después de validar."""
        # Validar
        valido, mensaje_error = self.validar_formulario()
        
        if not valido:
            self.txt_error.value = f"⚠️ {mensaje_error}"
            self.txt_error.visible = True
            self.update()
            return
        
        self.txt_error.visible = False
        
        # Construir datos
        datos = {
            "id_propiedad": int(self.dd_propiedad.value),
            "descripcion": self.txt_descripcion.value.strip(),
            "prioridad": self.dd_prioridad.value,
            "origen_reporte": self.dd_origen.value,
        }
        
        # Agregar campos opcionales si tienen valor
        if self.dd_responsable_pago.value:
            datos["responsable_pago"] = self.dd_responsable_pago.value
        
        if self.dd_proveedor.value:
            datos["id_proveedor"] = int(self.dd_proveedor.value)
        
        try:
            # Guardar incidente
            incidente = self.servicio.reportar_incidente(datos, usuario_sistema="Sistema")
            
            # Mostrar mensaje de éxito
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text(f"✅ Incidente #{incidente.id_incidente} reportado exitosamente"),
                bgcolor=ft.Colors.GREEN_600
            )
            self.page.snack_bar.open = True
            
            # Navegar al listado
            self.on_navigate("incidentes")
            
        except Exception as ex:
            self.txt_error.value = f"❌ Error al guardar: {str(ex)}"
            self.txt_error.visible = True
            self.update()
            
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text(f"Error: {str(ex)}"),
                bgcolor=ft.Colors.RED_600
            )
            self.page.snack_bar.open = True
            self.page.update()
