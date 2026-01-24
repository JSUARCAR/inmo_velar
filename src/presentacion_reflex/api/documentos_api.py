
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse, JSONResponse
from typing import List, Optional
import io

from src.aplicacion.servicios.servicio_documental import ServicioDocumentalElite
from src.aplicacion.servicios.procesador_documentos_async import ProcesadorDocumentosAsync
from src.dominio.servicios.validador_documentos import ValidadorDocumentos

# Crear Router de FastAPI
documentos_router = APIRouter(prefix="/api/documentos", tags=["Documentos"])

# Servicios
servicio_documental = ServicioDocumentalElite()
procesador_async = ProcesadorDocumentosAsync()

@documentos_router.post("/upload/{entidad_tipo}/{entidad_id}")
async def upload_documento(
    entidad_tipo: str, 
    entidad_id: str, 
    file: UploadFile = File(...),
    usuario: str = Form("API_USER")
):
    """
    Endpoint para subir un documento.
    Incluye validación síncrona y procesamiento (compresión) asíncrono opcional.
    """
    try:
        content = await file.read()
        
        # 1. Validar
        validacion = ValidadorDocumentos.validar_archivo_generico(
            entidad_tipo=entidad_tipo,
            nombre_archivo=file.filename,
            tamano_bytes=len(content)
        )
        
        if not validacion["valido"]:
            raise HTTPException(status_code=400, detail=validacion["mensaje"])
            
        # 2. Subir (Síncrono por ahora para garantizar persistencia inmediata)
        # TODO: Implementar optimización asíncrona real si se desea delay
        doc = servicio_documental.subir_documento(
            entidad_tipo=entidad_tipo,
            entidad_id=entidad_id,
            nombre_archivo=file.filename,
            contenido_bytes=content,
            usuario=usuario
        )
        
        return {"status": "success", "id": doc.id, "filename": doc.nombre_archivo}
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

@documentos_router.get("/list/{entidad_tipo}/{entidad_id}")
async def listar_documentos(entidad_tipo: str, entidad_id: str):
    """Lista metadatos de documentos de una entidad."""
    docs = servicio_documental.listar_documentos(entidad_tipo, entidad_id)
    return [
        {
            "id": d.id,
            "filename": d.nombre_archivo,
            "version": d.version,
            "created_at": d.created_at,
            "size_kb": d.tamanio_kb
        }
        for d in docs
    ]

@documentos_router.get("/download/{documento_id}")
async def descargar_documento(documento_id: int):
    """Descarga el contenido de un documento."""
    doc = servicio_documental.descargar_documento(documento_id)
    
    if not doc or not doc.contenido:
        raise HTTPException(status_code=404, detail="Documento no encontrado")
        
    disposition = "inline" if "image" in doc.mime_type or "pdf" in doc.mime_type else "attachment"
    
    return StreamingResponse(
        io.BytesIO(doc.contenido),
        media_type=doc.mime_type,
        headers={"Content-Disposition": f"{disposition}; filename={doc.nombre_archivo}"}
    )
