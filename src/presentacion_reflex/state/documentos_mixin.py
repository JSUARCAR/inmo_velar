import reflex as rx
from typing import List, Dict, Any, Optional
from src.aplicacion.servicios.servicio_documental import ServicioDocumentalElite
import traceback

# Instancia global del servicio (podría inyectarse)
servicio_documental = ServicioDocumentalElite()

class DocumentosStateMixin(rx.State):
    """
    Mixin para gestión de estado de documentos.
    Heredar de este mixin en los states que requieran gestión documental.
    """
    
    # Lista de documentos cargados para la entidad actual
    documentos: List[Dict[str, Any]] = []
    
    # Estado de carga
    is_uploading: bool = False
    upload_progress: int = 0
    
    # Contexto de Entidad (Definido aquí para acceso seguro)
    current_entidad_tipo: str = ""
    current_entidad_id: str = ""
    
    # Tipos requeridos (se llena según la entidad/estado)
    tipos_documento_requeridos: List[str] = []

    async def handle_upload(self, files: List[rx.UploadFile]):
        """
        Maneja la subida de archivos genérica.
        Los states hijos deben implementar handles específicos si requieren lógica extra,
        o configurar `self.current_entidad_tipo` y `self.current_entidad_id` antes.
        """
        self.is_uploading = True
        self.upload_progress = 10
        
        # Estas variables deben ser definidas o sobrescritas por el state hijo
        # O pasadas como argumentos, pero Reflex events son limitados en argumentos complejos
        # Se asume que el state hijo tiene estas propiedades seteadas
        entidad_tipo = getattr(self, "current_entidad_tipo", None)
        entidad_id = getattr(self, "current_entidad_id", None)
        
        pass  # print(f"DEBUG: handle_upload called. Tipo: '{entidad_tipo}', ID: '{entidad_id}'") [OpSec Removed]


        if not entidad_tipo or not entidad_id:
            pass  # print("Error: Entidad tipo/id no definidos para upload") [OpSec Removed]
            self.is_uploading = False
            return
            
        try:
            pass  # print(f"DEBUG: Processing upload. Files count: {len(files)}") [OpSec Removed]
            
            # Usar método optimizado del servicio que incluye validación
            await servicio_documental.procesar_upload_multiple(
                files=files,
                entidad_tipo=entidad_tipo,
                entidad_id=str(entidad_id),
                usuario="USER_APP" # TODO: Obtener usuario real
            )
            
            # Recargar lista
            self.cargar_documentos()
            yield rx.toast.success("Documentos cargados exitosamente")
            
        except ValueError as ve:
            # Errores de validación de negocio
            yield rx.toast.warning(str(ve), duration=5000)
        except Exception as e:
            pass  # print(f"Error subiendo documentos type: {type(e)}") [OpSec Removed]
            pass  # print(f"Error subiendo documentos str: {e}") [OpSec Removed]
            traceback.print_exc()
            yield rx.toast.error(f"Error técnico al subir: {str(e)}")
            
        finally:
            self.is_uploading = False
            self.upload_progress = 0

    def cargar_documentos(self):
        """Carga documentos de la entidad actual."""
        entidad_tipo = getattr(self, "current_entidad_tipo", None)
        entidad_id = getattr(self, "current_entidad_id", None)
        
        if entidad_tipo and entidad_id:
            docs = servicio_documental.listar_documentos(entidad_tipo, str(entidad_id))
            # Serializar para el frontend
            self.documentos = [
                {
                    "id_documento": d.id,
                    "nombre_archivo": d.nombre_archivo,
                    "extension": d.extension,
                    "mime_type": d.mime_type,
                    "version": d.version,
                    "fecha_creacion": str(d.created_at)
                }
                for d in docs
            ]

    def eliminar_documento(self, id_documento: int):
        """Elimina un documento."""
        try:
            servicio_documental.eliminar_documento(id_documento)
            self.cargar_documentos()
            yield rx.toast.success("Documento eliminado")
        except Exception as e:
             yield rx.toast.error(f"Error eliminando documento: {str(e)}")

    @rx.event
    def descargar_documento(self, id_documento: int):
        """Descarga un documento."""
        try:
            doc = servicio_documental.descargar_documento(id_documento)
            if doc and doc.contenido:
                return rx.download(
                    data=doc.contenido,
                    filename=doc.nombre_archivo
                )
            else:
                return rx.toast.error("No se pudo obtener el contenido del documento")
        except Exception as e:
            return rx.toast.error(f"Error al descargar: {str(e)}")
