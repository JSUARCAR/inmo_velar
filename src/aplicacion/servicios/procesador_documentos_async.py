
import asyncio
import io
from typing import Optional, Tuple
from src.aplicacion.servicios.servicio_documental import ServicioDocumentalElite

class ProcesadorDocumentosAsync:
    """
    Servicio para procesamiento asíncrono/background de documentos.
    Maneja tareas pesadas como compresión de imágenes, generación de thumbnails,
    y OCR sin bloquear el hilo principal.
    """
    
    def __init__(self):
        self.servicio_base = ServicioDocumentalElite()

    async def optimizar_imagen_async(self, imagen_bytes: bytes, mime_type: str) -> bytes:
        """
        Versión asíncrona de compresión de imágenes.
        Ejecuta la operación CPU-bound en un executor.
        """
        if "image" not in mime_type:
            return imagen_bytes
            
        loop = asyncio.get_running_loop()
        # Ejecutar en thread pool por defecto
        optimized_bytes = await loop.run_in_executor(
            None, 
            self.servicio_base.comprimir_imagen,
            imagen_bytes
        )
        return optimized_bytes

    async def generar_thumbnail_async(self, imagen_bytes: bytes, mime_type: str) -> Optional[bytes]:
        """
        Versión asíncrona de generación de thumbnails.
        """
        if "image" not in mime_type:
            return None
            
        loop = asyncio.get_running_loop()
        thumb_bytes = await loop.run_in_executor(
            None,
            self.servicio_base.generar_thumbnail,
            imagen_bytes,
            mime_type
        )
        return thumb_bytes

    async def extraer_texto_async(self, documento_bytes: bytes) -> str:
        """
        Extracción de texto (OCR) asíncrona.
        """
        loop = asyncio.get_running_loop()
        texto = await loop.run_in_executor(
            None,
            self.servicio_base.extraer_texto_ocr,
            documento_bytes
        )
        return texto
