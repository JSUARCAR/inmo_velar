import flet as ft
import threading
from src.aplicacion.servicios.servicio_proveedores import ServicioProveedores

class ProveedoresListView(ft.Column):
    def __init__(self, page: ft.Page, servicio_proveedores: ServicioProveedores, on_navigate):
        super().__init__(expand=True)
        self.page_ref = page
        self.servicio = servicio_proveedores
        self.on_navigate = on_navigate
        
        self.proveedores = []
        
        self.tabla_proveedores = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("ID")),
                ft.DataColumn(ft.Text("Nombre")),
                ft.DataColumn(ft.Text("Especialidad")),
                ft.DataColumn(ft.Text("Teléfono")),
                ft.DataColumn(ft.Text("Acciones")),
            ],
            rows=[]
        )
        self.loading = ft.ProgressBar(width=400, color="blue", visible=False)

        # UI (adaptado de build)
        self.controls = [
            ft.Row(
                [
                    ft.Text("Gestión de Proveedores", size=24, weight=ft.FontWeight.BOLD),
                    ft.ElevatedButton(
                        "Nuevo Proveedor",
                        icon=ft.Icons.ADD,
                        on_click=lambda _: self.on_navigate("proveedor_form")
                    )
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN
            ),
            ft.Divider(),
            
            # Loading
            ft.Container(content=self.loading, alignment=ft.alignment.center),
            
            ft.Container(
                content=self.tabla_proveedores,
                border=ft.border.all(1, ft.Colors.OUTLINE_VARIANT),
                border_radius=10,
                padding=10,
                visible=True # Inicialmente visible vacío o con loading
            )
        ]

    def did_mount(self):
        self.cargar_datos()
        
    def cargar_datos(self):
        self.loading.visible = True
        self.tabla_proveedores.visible = False
        self.update()
        threading.Thread(target=self._fetch_data, daemon=True).start()

    def _fetch_data(self):
        try:
            self.proveedores = self.servicio.listar_proveedores()
            self._update_table()
        except Exception as e:
            print(f"Error loading proveedores: {e}")
            self.loading.visible = False
            self.update()

    def _update_table(self):
        self.tabla_proveedores.rows = []
        
        for p in self.proveedores:
            # Safely handle potential None values for joined fields
            nombre = p.nombre_completo if hasattr(p, 'nombre_completo') and p.nombre_completo else "Desconocido"
            telefono = p.contacto if hasattr(p, 'contacto') and p.contacto else "N/A"
            
            self.tabla_proveedores.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(p.id_proveedor))),
                        ft.DataCell(ft.Text(nombre)),
                        ft.DataCell(ft.Text(p.especialidad)),
                        ft.DataCell(ft.Text(telefono)),
                        ft.DataCell(ft.Row([
                            ft.IconButton(
                                icon=ft.Icons.EDIT,
                                tooltip="Editar",
                                on_click=lambda e, id=p.id_proveedor: self.on_navigate("proveedor_form", id_proveedor=id)
                            ),
                            ft.IconButton(
                                icon=ft.Icons.DELETE,
                                tooltip="Eliminar",
                                icon_color=ft.Colors.ERROR,
                                on_click=lambda e, id=p.id_proveedor: self.confirmar_eliminacion(id)
                            )
                        ]))
                    ]
                )
            )
        
        self.loading.visible = False
        self.tabla_proveedores.visible = True
        self.update()

    def confirmar_eliminacion(self, id_proveedor):
        def eliminar(e):
            try:
                self.servicio.eliminar_proveedor(id_proveedor)
                self.page_ref.close(dlg)
                self.page_ref.snack_bar = ft.SnackBar(ft.Text("Proveedor eliminado"))
                self.page_ref.snack_bar.open = True
                self.cargar_datos() # Reload async
            except Exception as ex:
                self.page_ref.close(dlg)
                self.page_ref.snack_bar = ft.SnackBar(ft.Text(f"Error: {str(ex)}"))
                self.page_ref.snack_bar.open = True
                self.page_ref.update()
                
        dlg = ft.AlertDialog(
            title=ft.Text("Confirmar eliminación"),
            content=ft.Text("¿Está seguro de eliminar este proveedor?"),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: self.page_ref.close(dlg)),
                ft.TextButton("Eliminar", on_click=eliminar, style=ft.ButtonStyle(color=ft.Colors.ERROR))
            ]
        )
        self.page_ref.open(dlg)
