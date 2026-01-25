import flet as ft

from src.aplicacion.servicios.servicio_personas import ServicioPersonas
from src.aplicacion.servicios.servicio_proveedores import ServicioProveedores


class ProveedorFormView(ft.Column):
    def __init__(
        self,
        page: ft.Page,
        servicio_proveedores: ServicioProveedores,
        servicio_personas: ServicioPersonas,
        on_navigate,
        id_proveedor=None,
    ):
        super().__init__(expand=True)
        self.page = page
        self.servicio = servicio_proveedores
        self.servicio_personas = servicio_personas
        self.on_navigate = on_navigate
        self.id_proveedor = id_proveedor
        self.persona_seleccionada = None

        # UI Components
        self.tf_buscar_persona = ft.TextField(
            label="Buscar Persona (Nombre o Documento)",
            suffix_icon=ft.Icons.SEARCH,
            on_submit=self.buscar_persona,
            expand=True,
        )
        self.lv_personas = ft.ListView(height=150, spacing=10)
        self.card_persona = ft.Card(visible=False)

        self.tf_especialidad = ft.TextField(label="Especialidad (ej. Plomero, Electricista)")
        self.slider_calificacion = ft.Slider(min=0, max=5, divisions=10, label="{value}")
        self.tf_observaciones = ft.TextField(label="Observaciones", multiline=True)

        self.btn_guardar = ft.ElevatedButton("Guardar Proveedor", on_click=self.guardar_proveedor)
        self.btn_cancelar = ft.TextButton(
            "Cancelar", on_click=lambda _: self.on_navigate("proveedores")
        )

        self.controls = [
            ft.Text("Registro de Proveedor", size=24, weight=ft.FontWeight.BOLD),
            ft.Divider(),
            # Buscador de personas (solo si es nuevo)
            ft.Container(
                visible=not self.id_proveedor,
                content=ft.Column(
                    [
                        ft.Row(
                            [
                                self.tf_buscar_persona,
                                ft.IconButton(ft.Icons.SEARCH, on_click=self.buscar_persona),
                            ]
                        ),
                        self.lv_personas,
                        self.card_persona,
                    ]
                ),
            ),
            # Datos del proveedor
            ft.Container(
                content=ft.Column(
                    [
                        ft.Text("Datos del Servicio", weight=ft.FontWeight.BOLD),
                        self.tf_especialidad,
                        ft.Text("Calificación Inicial:"),
                        self.slider_calificacion,
                        self.tf_observaciones,
                        ft.Row(
                            [self.btn_guardar, self.btn_cancelar],
                            alignment=ft.MainAxisAlignment.END,
                        ),
                    ]
                ),
                padding=20,
                border=ft.border.all(1, ft.Colors.OUTLINE_VARIANT),
                border_radius=10,
            ),
        ]

    def did_mount(self):
        if self.id_proveedor:
            self.cargar_datos_edicion()

    def buscar_persona(self, e):
        query = self.tf_buscar_persona.value
        if not query:
            return

        resultados = self.servicio_personas.listar_personas(busqueda=query)
        self.lv_personas.controls = []

        for p in resultados:
            self.lv_personas.controls.append(
                ft.ListTile(
                    title=ft.Text(p.nombre_completo),
                    subtitle=ft.Text(f"Doc: {p.numero_documento}"),
                    leading=ft.Icon(ft.Icons.PERSON),
                    on_click=lambda e, per=p: self.seleccionar_persona(per),
                )
            )
        self.update()

    def seleccionar_persona(self, persona):
        self.persona_seleccionada = persona
        self.lv_personas.controls = []
        self.tf_buscar_persona.value = ""

        contenido = ft.Container(
            padding=10,
            content=ft.Column(
                [
                    ft.Text(
                        f"Persona Seleccionada: {persona.nombre_completo}",
                        weight=ft.FontWeight.BOLD,
                    ),
                    ft.Text(f"Documento: {persona.numero_documento}"),
                    ft.TextButton("Cambiar", on_click=lambda _: self.reset_seleccion()),
                ]
            ),
        )
        self.card_persona.content = contenido
        self.card_persona.visible = True
        self.update()

    def reset_seleccion(self):
        self.persona_seleccionada = None
        self.card_persona.visible = False
        self.update()

    def guardar_proveedor(self, e):
        if not self.id_proveedor and not self.persona_seleccionada:
            self.mostrar_error("Debe seleccionar una persona")
            return

        try:
            datos = {
                "id_persona": (
                    self.persona_seleccionada.persona.id_persona
                    if self.persona_seleccionada
                    else None
                ),
                "especialidad": self.tf_especialidad.value,
                "calificacion": self.slider_calificacion.value,
                "observaciones": self.tf_observaciones.value,
            }

            if self.id_proveedor:  # Edición (falta implementar en detalle, asumiendo update simple)
                self.servicio.actualizar_proveedor(self.id_proveedor, datos)
                mensaje = "Proveedor actualizado"
            else:
                self.servicio.crear_proveedor(datos, "admin")
                mensaje = "Proveedor creado exitosamente"

            self.page.snack_bar = ft.SnackBar(ft.Text(mensaje))
            self.page.snack_bar.open = True

            self.on_navigate("proveedores")

        except Exception as ex:
            self.mostrar_error(str(ex))

    def cargar_datos_edicion(self):
        # Lógica para cargar datos si se edita
        prov = self.servicio.obtener_proveedor(self.id_proveedor)
        if prov:
            self.tf_especialidad.value = prov.especialidad
            self.slider_calificacion.value = prov.calificacion
            self.tf_observaciones.value = prov.observaciones
            self.tf_buscar_persona.visible = False  # En edición no cambiamos la persona base
            self.update()

    def mostrar_error(self, mensaje):
        self.page.snack_bar = ft.SnackBar(ft.Text(f"Error: {mensaje}"), bgcolor=ft.Colors.ERROR)
        self.page.snack_bar.open = True
        self.page.update()
