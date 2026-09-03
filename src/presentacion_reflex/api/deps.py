from typing import Annotated
from fastapi import Cookie, HTTPException, status, Depends
from src.aplicacion.servicios.servicio_autenticacion import ServicioAutenticacion
from src.infraestructura.repositorios.repositorio_sesion import RepositorioSesion
from src.infraestructura.repositorios.repositorio_usuario import RepositorioUsuario

def get_servicio_autenticacion() -> ServicioAutenticacion:
    return ServicioAutenticacion(RepositorioUsuario(), RepositorioSesion())

async def validar_sesion_api(
    _s: Annotated[str | None, Cookie(alias="_s")] = None,
    servicio_auth: ServicioAutenticacion = Depends(get_servicio_autenticacion)
) -> dict:
    """
    Dependencia de FastAPI para proteger endpoints.
    Extrae la cookie _s, valida la sesión absoluta de 8h, y devuelve el usuario.
    """
    if not _s:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sesión requerida"
        )
    
    try:
        usuario = servicio_auth.validar_sesion(_s)
        return usuario
    except Exception as e:
        # Cualquier fallo de validación de sesión (SesionInvalida) se traduce a 401
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sesión inválida o expirada"
        )
