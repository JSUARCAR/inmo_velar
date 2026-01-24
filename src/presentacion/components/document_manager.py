import flet as ft
from src.aplicacion.servicios.servicio_documental import ServicioDocumental
import base64
import os
import threading

class DocumentManager(ft.Column):
    def __init__(self, entidad_tipo: str, entidad_id: str, page: ft.Page, **kwargs):
        super().__init__(**kwargs)
        self.entidad_tipo = entidad_tipo
        self.entidad_id = entidad_id
        self.page = page
        self.servicio = ServicioDocumental()
        
        # FilePicker configured for both selection and upload
        self.file_picker = ft.FilePicker(
            on_result=self._on_file_result,
            on_upload=self._procesar_subida_web
        )
        
        # FIX: FilePicker MUST be in overlay for events to work correctly, especially upload
        if self.file_picker not in self.page.overlay:
            self.page.overlay.append(self.file_picker)
            self.page.update()
        
        # UI Elements
        if not isinstance(self.page, ft.Page):
             pass  # print(">>> WARNING [DocumentManager]: 'page' argument is not an ft.Page instance.") [OpSec Removed]

        # UI Elements
        self.tabla_docs = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Archivo")),
                ft.DataColumn(ft.Text("Descripción")),
                ft.DataColumn(ft.Text("Ver.")),
                ft.DataColumn(ft.Text("Fecha")),
                ft.DataColumn(ft.Text("Acciones")),
            ],
            rows=[]
        )

        # Defines structure
        self.controls = [
            ft.Row([
                ft.Text("Documentos Adjuntos", style=ft.TextThemeStyle.TITLE_MEDIUM),
                ft.Row([
                    ft.Text(ref=ft.Ref[ft.Text](), visible=False), # Placeholder for progress
                    ft.IconButton(ft.Icons.UPLOAD_FILE, tooltip="Adjuntar Archivo", on_click=lambda _: self.abrir_dialogo_carga())
                ])
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Row([self.tabla_docs], scroll=ft.ScrollMode.AUTO),
            # self.file_picker # REMOVED: Moved to overlay
        ]

    def abrir_dialogo_carga(self):
        self.file_picker.pick_files(allow_multiple=False)
    
    def did_mount(self):
        """Lifecycle method called when component is mounted."""
        self.cargar_documentos()
    
    def cargar_documentos(self):
        """Carga la lista de documentos desde la BD y actualiza la tabla."""
        try:
            documentos = self.servicio.listar_documentos(self.entidad_tipo, self.entidad_id)
            
            # Clear existing rows
            self.tabla_docs.rows.clear()
            
            # Populate rows
            for doc in documentos:
                # created_at is a string from database, extract date part if it's a timestamp
                fecha_str = str(doc.created_at)[:10] if doc.created_at else ""
                
                self.tabla_docs.rows.append(
                    ft.DataRow(cells=[
                        ft.DataCell(ft.Text(doc.nombre_archivo)),
                        ft.DataCell(ft.Text(doc.descripcion or "")),
                        ft.DataCell(ft.Text(str(doc.version))),
                        ft.DataCell(ft.Text(fecha_str)),
                        ft.DataCell(ft.Row([
                            ft.IconButton(
                                icon=ft.Icons.DOWNLOAD,
                                tooltip="Descargar",
                                on_click=lambda _, id=doc.id: self.descargar_documento(id)
                            ),
                            ft.IconButton(
                                icon=ft.Icons.DELETE,
                                tooltip="Eliminar",
                                on_click=lambda _, id=doc.id: self.eliminar_documento(id)
                            )
                        ]))
                    ])
                )
            
            # Update UI
            if self.tabla_docs.page:
                self.tabla_docs.update()
        except Exception as e:
            pass  # print(f"[ERROR] cargar_documentos: {e}") [OpSec Removed]

    def _on_file_result(self, e: ft.FilePickerResultEvent):
        if not e.files:
            return
            
        self.archivo_temporal = e.files[0]
        self.mostrar_modal_descripcion()

    def mostrar_modal_descripcion(self):
        txt_descripcion_local = ft.TextField(label="Descripción del archivo", expand=True)
        
        def confirmar_subida(e):
            self.descripcion_temporal = txt_descripcion_local.value
            
            # Close dialog
            if hasattr(self.page, 'close'):
                self.page.close(self.dlg_desc)
            else:
                self.dlg_desc.open = False
                self.page.update()
            
            # Show loading
            self.page.snack_bar = ft.SnackBar(ft.Text("Procesando archivo..."), bgcolor="blue")
            self.page.snack_bar.open = True
            self.page.update()

            if self.archivo_temporal.path:
                # MODO ESCRITORIO
                threading.Thread(target=self._procesar_subida_directa).start()
            else:
                # MODO WEB - Use signed upload URL
                pass  # print(f"[DEBUG] Iniciando carga Web para: {self.archivo_temporal.name}") [OpSec Removed]
                upload_url = self.page.get_upload_url(self.archivo_temporal.name, 60)
                upload_file = ft.FilePickerUploadFile(
                    name=self.archivo_temporal.name,
                    upload_url=upload_url
                )
                self.file_picker.upload([upload_file])

        self.dlg_desc = ft.AlertDialog(
            title=ft.Text("Confirmar Subida"),
            content=ft.Column([
                ft.Text(f"Archivo: {self.archivo_temporal.name}"),
                txt_descripcion_local
            ], tight=True),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda _: self.page.close(self.dlg_desc)),
                ft.TextButton("Subir", on_click=confirmar_subida)
            ]
        )
        
        if hasattr(self.page, 'open'):
            self.page.open(self.dlg_desc)
        else:
            self.page.dialog = self.dlg_desc
            self.dlg_desc.open = True
            self.page.update()

    def _procesar_subida_directa(self):
        """Sube archivo leyendo directamente del path (Escritorio)."""
        try:
            pass  # print(f"[DEBUG] Subida Directa: {self.archivo_temporal.path}") [OpSec Removed]
            with open(self.archivo_temporal.path, "rb") as f:
                contenido = f.read()
            self._guardar_documento(contenido)
        except Exception as e:
            self._mostrar_error(f"Error leyendo archivo local: {e}")

    def _procesar_subida_web(self, e: ft.FilePickerUploadEvent):
        """Sube archivo leyendo del directorio temporal de uploads (Web)."""
        try:
            upload_dir = "uploads" 
            file_path = os.path.join(upload_dir, e.file_name)
            
            # Enhanced debugging
            pass  # print(f"[DEBUG] === UPLOAD EVENT DEBUG ===") [OpSec Removed]
            pass  # print(f"[DEBUG] Event: {e}") [OpSec Removed]
            pass  # print(f"[DEBUG] File name: {e.file_name}") [OpSec Removed]
            pass  # print(f"[DEBUG] Progress: {e.progress}") [OpSec Removed]
            pass  # print(f"[DEBUG] Error (if any): {e.error}") [OpSec Removed]
            pass  # print(f"[DEBUG] Looking for file at: {file_path}") [OpSec Removed]
            pass  # print(f"[DEBUG] Upload dir exists: {os.path.exists(upload_dir)}") [OpSec Removed]
            if os.path.exists(upload_dir):
                pass  # print(f"[DEBUG] Upload dir contents: {os.listdir(upload_dir)}") [OpSec Removed]
            else:
                pass  # print(f"[DEBUG] Upload dir NOT FOUND") [OpSec Removed]
            pass  # print(f"[DEBUG] === END DEBUG ===") [OpSec Removed]
            
            if os.path.exists(file_path):
                with open(file_path, "rb") as f:
                    contenido = f.read()
                
                # Cleanup
                try:
                   os.remove(file_path)
                except:
                   pass
                    
                self._guardar_documento(contenido)
            else:
                 self._mostrar_error(f"Error: Archivo no encontrado en servidor ({file_path})")

        except Exception as ex:
             self._mostrar_error(f"Error procesando subida web: {ex}")

    def _guardar_documento(self, contenido):
        """Llama al servicio para guardar el documento."""
        try:
            self.servicio.subir_documento(
                self.entidad_tipo,
                self.entidad_id,
                self.archivo_temporal.name,
                contenido,
                self.descripcion_temporal
            )
            self._mostrar_exito("Documento cargado exitosamente")
            self.cargar_documentos() # Recargar lista
        except Exception as e:
            pass # _mostrar_error handled inside exception? No, calling it now
            self._mostrar_error(f"Error guardando documento: {e}")

    def _mostrar_exito(self, mensaje):
        self.page.snack_bar = ft.SnackBar(ft.Text(mensaje), bgcolor="green")
        self.page.snack_bar.open = True
        self.page.update()

    def _mostrar_error(self, mensaje):
        pass  # print(f"[ERROR] {mensaje}") [OpSec Removed]
        self.page.snack_bar = ft.SnackBar(ft.Text(str(mensaje)), bgcolor="red")
        self.page.snack_bar.open = True
        self.page.update()

    def descargar_documento(self, id_documento):
        doc = self.servicio.descargar_documento(id_documento)
        if doc and doc.contenido:
            # En Flet Desktop, guardar archivo
            # Usar FilePicker.save_file? 
            # O simplemente guardar en carpeta tmp y abrir?
            import os
            import tempfile
            import subprocess
            
            try:
                # Crear archivo temporal
                fd, path = tempfile.mkstemp(suffix=f".{doc.extension}")
                with os.fdopen(fd, 'wb') as tmp:
                    tmp.write(doc.contenido)
                
                # Intentar abrir con el sistema operativo
                if os.name == 'nt': # Windows
                    os.startfile(path)
                else: # Linux/Mac (no estamos en ese entorno pero por compatibilidad)
                    subprocess.call(('xdg-open', path))
                    
                self.page.open(ft.SnackBar(ft.Text(f"Archivo abierto: {doc.nombre_archivo}")))
            except Exception as e:
                self.page.open(ft.SnackBar(ft.Text(f"Error al abrir archivo: {e}"), bgcolor="red"))

    def eliminar_documento(self, id_documento):
        def confirmar_eliminar(e):
            self.dlg_eliminar.open = False
            self.page.update()
            
            # Close dialog properly
            if hasattr(self.page, 'close'):
                self.page.close(self.dlg_eliminar)
            
            try:
                self.servicio.eliminar_documento(id_documento)
                self.page.open(ft.SnackBar(ft.Text("Documento eliminado"), bgcolor="green"))
                self.cargar_documentos()
            except Exception as ex:
                 self.page.open(ft.SnackBar(ft.Text(f"Error al eliminar: {ex}"), bgcolor="red"))

        self.dlg_eliminar = ft.AlertDialog(
            title=ft.Text("Confirmar Eliminación"),
            content=ft.Text("¿Está seguro de eliminar este documento?"),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda _: self.page.close(self.dlg_eliminar)),
                ft.TextButton("Eliminar", on_click=confirmar_eliminar, style=ft.ButtonStyle(color="red"))
            ]
        )
        
        if hasattr(self.page, 'open'):
            self.page.open(self.dlg_eliminar)
        else:
            self.page.dialog = self.dlg_eliminar
            self.dlg_eliminar.open = True
            self.page.update()
