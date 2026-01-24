from typing import List, Optional, Dict, Any, Tuple
from src.dominio.entidades.documento import Documento
from src.infraestructura.repositorios.repositorio_documento_sqlite import RepositorioDocumentoSQLite
from src.dominio.constantes.tipos_documento import TIPOS_DOCUMENTO_MODULO
import mimetypes
import io
import reflex as rx

# Tenta importar PIL, manejo de error si no está instaldo
try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

class ServicioDocumental:
    def __init__(self, repositorio: RepositorioDocumentoSQLite = None):
        self.repositorio = repositorio or RepositorioDocumentoSQLite()

    def subir_documento(
        self, 
        entidad_tipo: str, 
        entidad_id: str, 
        nombre_archivo: str, 
        contenido_bytes: bytes, 
        descripcion: str = "",
        usuario: str = "SYSTEM"
    ) -> Documento:
        """
        Sube un documento al sistema. Maneja el versionamiento automático.
        Si ya existe un documento con el mismo nombre para esa entidad,
        se crea una nueva versión y la anterior deja de ser vigente.
        """
        # 1. Determinar número de versión
        ultima_version = self.repositorio.obtener_ultima_version(entidad_tipo, entidad_id, nombre_archivo)
        nueva_version = ultima_version + 1
        
        # 2. Obtener extensión y mime type
        extension = ""
        if "." in nombre_archivo:
            extension = nombre_archivo.split(".")[-1].lower()
        
        mime_type, _ = mimetypes.guess_type(nombre_archivo)
        if not mime_type:
            mime_type = "application/octet-stream"

        # 3. Anular versiones anteriores (si existen)
        if ultima_version > 0:
            self.repositorio.anular_version_anterior(entidad_tipo, entidad_id, nombre_archivo)

        # 4. Crear nuevo documento
        nuevo_doc = Documento(
            entidad_tipo=entidad_tipo,
            entidad_id=str(entidad_id),
            nombre_archivo=nombre_archivo,
            extension=extension,
            mime_type=mime_type,
            descripcion=descripcion,
            contenido=contenido_bytes,
            version=nueva_version,
            es_vigente=True,
            created_by=usuario
        )

        return self.repositorio.crear(nuevo_doc)

    def listar_documentos(self, entidad_tipo: str, entidad_id: str) -> List[Documento]:
        """Retorna lista de documentos vigentes (metadata) para una entidad."""
        return self.repositorio.listar_por_entidad(entidad_tipo, entidad_id)

    def descargar_documento(self, id_documento: int) -> Optional[Documento]:
        """
        Retorna el documento completo con contenido binario.
        Usar solo para descargar/visualizar.
        """
        return self.repositorio.obtener_por_id_con_contenido(id_documento)

    def eliminar_documento(self, id_documento: int):
        """Elimina (lógicamente) un documento."""
        self.repositorio.eliminar_logico(id_documento)


class ServicioDocumentalElite(ServicioDocumental):
    """Extensión del servicio documental con funcionalidades elite."""
    
    def validar_documento_modulo(self, entidad_tipo: str, tipo_documento: str, 
                                archivo_bytes: bytes, filename: str) -> Dict[str, Any]:
        """
        Valida que el documento cumpla con las reglas del módulo y tipo.
        Retorna: {'valido': bool, 'mensaje': str}
        """
        reglas_modulo = TIPOS_DOCUMENTO_MODULO.get(entidad_tipo)
        if not reglas_modulo:
            return {'valido': False, 'mensaje': f"Módulo {entidad_tipo} no configurado"}
            
        reglas_tipo = reglas_modulo.get(tipo_documento)
        if not reglas_tipo:
            return {'valido': False, 'mensaje': f"Tipo de documento {tipo_documento} no válido para {entidad_tipo}"}
            
        # Validar extensión
        ext = "." + filename.split(".")[-1].lower() if "." in filename else ""
        if ext not in reglas_tipo['tipos']:
            return {'valido': False, 'mensaje': f"Tipo de archivo no permitido. Esperado: {', '.join(reglas_tipo['tipos'])}"}
            
        # Validar tamaño
        if len(archivo_bytes) > reglas_tipo['max_size']:
            limit_mb = reglas_tipo['max_size'] / (1024*1024)
            return {'valido': False, 'mensaje': f"El archivo excede el tamaño máximo de {limit_mb:.1f}MB"}
            
        return {'valido': True, 'mensaje': "Documento válido"}

    def generar_thumbnail(self, imagen_bytes: bytes, mime_type: str, 
                         max_size: Tuple[int, int] = (200, 200)) -> Optional[bytes]:
        """Genera thumbnail para imágenes usando PIL."""
        if not HAS_PIL or "image" not in mime_type:
            return None
            
        try:
            img = Image.open(io.BytesIO(imagen_bytes))
            
            # Convertir a RGB si es necesario (ej. PNG transparentes)
            if img.mode in ('RGBA', 'P'):
                img = img.convert('RGB')
                
            img.thumbnail(max_size)
            
            thumb_io = io.BytesIO()
            img.save(thumb_io, format='JPEG', quality=85)
            return thumb_io.getvalue()
        except Exception as e:
            print(f"Error generando thumbnail: {e}")
            return None

    def extraer_texto_ocr(self, imagen_bytes: bytes) -> str:
        """Extrae texto de imágenes usando OCR (Simulado/Future Impl)."""
        # Placeholder para implementación futura con Tesseract
        return ""

    def comprimir_imagen(self, imagen_bytes: bytes, calidad: int = 85) -> bytes:
        """Comprime imagen manteniendo calidad aceptable."""
        if not HAS_PIL:
            return imagen_bytes
            
        try:
             img = Image.open(io.BytesIO(imagen_bytes))
             out_io = io.BytesIO()
             
             # Preservar formato original si es posible, idealmente convertir a WebP o JPEG optimizado
             fmt = img.format if img.format else 'JPEG'
             img.save(out_io, format=fmt, quality=calidad, optimize=True)
             
             compressed = out_io.getvalue()
             # Retornar comprimido solo si es menor
             return compressed if len(compressed) < len(imagen_bytes) else imagen_bytes
        except Exception as e:
            print(f"Error comprimiendo imagen: {e}")
            return imagen_bytes

    async def procesar_upload_multiple(self, files: List[rx.UploadFile], 
                                     entidad_tipo: str, entidad_id: str,
                                     usuario: str) -> List[Documento]:
        """
        Procesa múltiples archivos con validación y optimizaciones.
        """
        from src.dominio.servicios.validador_documentos import ValidadorDocumentos
        
        documentos_procesados = []
        errores = []
        
        # 1. Fase de Lectura y Validación
        files_content = []
        for file in files:
            content = await file.read()
            filename = file.filename
            
            # Validar reglas de negocio
            resultado = ValidadorDocumentos.validar_archivo_generico(
                entidad_tipo=entidad_tipo,
                nombre_archivo=filename,
                tamano_bytes=len(content)
            )
            
            if not resultado['valido']:
                errores.append(f"{filename}: {resultado['mensaje']}")
                continue
                
            files_content.append({
                'filename': filename,
                'content': content
            })
            
        if errores:
            # Si hay errores, no subimos NADA (Atomicidad de lote por UI)
            # O podríamos subir los válidos. Para mejor UX, lanzamos excepción con resumen.
            raise ValueError("Errores de validación:\n" + "\n".join(errores))
            
        # 2. Fase de Procesamiento
        for file_data in files_content:
            doc = self.subir_documento(
                entidad_tipo=entidad_tipo,
                entidad_id=entidad_id,
                nombre_archivo=file_data['filename'],
                contenido_bytes=file_data['content'],
                usuario=usuario
            )
            documentos_procesados.append(doc)
            
        return documentos_procesados
