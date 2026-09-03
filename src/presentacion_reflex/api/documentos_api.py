import io

from fastapi import APIRouter, File, HTTPException, UploadFile, Depends
from fastapi.responses import StreamingResponse

from src.aplicacion.servicios.procesador_documentos_async import (
    ProcesadorDocumentosAsync,
)
from src.aplicacion.servicios.servicio_documental import ServicioDocumentalElite
from src.dominio.servicios.validador_documentos import ValidadorDocumentos
from src.presentacion_reflex.api.deps import validar_sesion_api

# Crear Router de FastAPI con dependencia global
documentos_router = APIRouter(
    prefix="/api/documentos", 
    tags=["Documentos"],
    dependencies=[Depends(validar_sesion_api)]
)

# Servicios
servicio_documental = ServicioDocumentalElite()
procesador_async = ProcesadorDocumentosAsync()


@documentos_router.post("/upload/{entidad_tipo}/{entidad_id}")
async def upload_documento(
    entidad_tipo: str,
    entidad_id: str,
    file: UploadFile = File(...),
    usuario = Depends(validar_sesion_api),
):
    """
    Endpoint para subir un documento.
    """
    if not servicio_documental.verificar_acceso_entidad(usuario, entidad_tipo, entidad_id):
        raise HTTPException(status_code=403, detail="Sin acceso al recurso")

    try:
        content = await file.read()

        validacion = ValidadorDocumentos.validar_archivo_generico(
            entidad_tipo=entidad_tipo,
            nombre_archivo=file.filename,
            tamano_bytes=len(content),
        )

        if not validacion["valido"]:
            raise HTTPException(status_code=400, detail=validacion["mensaje"])

        doc = servicio_documental.subir_documento(
            entidad_tipo=entidad_tipo,
            entidad_id=entidad_id,
            nombre_archivo=file.filename,
            contenido_bytes=content,
            usuario=usuario.nombre_usuario if hasattr(usuario, "nombre_usuario") else "API_USER",
        )

        return {"status": "success", "id": doc.id, "filename": doc.nombre_archivo}

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")


@documentos_router.get("/list/{entidad_tipo}/{entidad_id}")
async def listar_documentos(
    entidad_tipo: str, 
    entidad_id: str,
    usuario = Depends(validar_sesion_api)
):
    """Lista metadatos de documentos de una entidad."""
    if not servicio_documental.verificar_acceso_entidad(usuario, entidad_tipo, entidad_id):
        raise HTTPException(status_code=403, detail="Sin acceso al recurso")

    docs = servicio_documental.listar_documentos(entidad_tipo, entidad_id)
    return [
        {
            "id": d.id,
            "filename": d.nombre_archivo,
            "version": d.version,
            "created_at": d.created_at,
            "size_kb": d.tamanio_kb,
        }
        for d in docs
    ]


@documentos_router.get("/download/{documento_id}")
async def descargar_documento(
    documento_id: int,
    usuario = Depends(validar_sesion_api)
):
    """Descarga el contenido de un documento."""
    doc = servicio_documental.descargar_documento(documento_id)

    if not doc or not doc.contenido:
        raise HTTPException(status_code=404, detail="Documento no encontrado")

    if not servicio_documental.verificar_acceso_entidad(usuario, doc.entidad_tipo, doc.entidad_id):
        raise HTTPException(status_code=403, detail="Sin acceso al recurso")

    disposition = (
        "inline" if "image" in (doc.mime_type or "") or "pdf" in (doc.mime_type or "") else "attachment"
    )

    return StreamingResponse(
        io.BytesIO(doc.contenido),
        media_type=doc.mime_type,
        headers={
            "Content-Disposition": f"{disposition}; filename={doc.nombre_archivo}"
        },
    )
