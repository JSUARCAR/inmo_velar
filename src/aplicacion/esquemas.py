from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

class EsquemaBase(BaseModel):
    """Configuración base para todos los esquemas."""
    model_config = ConfigDict(from_attributes=True)

class CredencialesAuth(EsquemaBase):
    """Esquema para login."""
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8)

class UsuarioCreate(EsquemaBase):
    """Esquema para creación de usuario."""
    nombre_usuario: str = Field(..., min_length=3, max_length=50)
    contraseña: str = Field(..., min_length=8)
    rol: str
    usuario_sistema: str

class UsuarioUpdate(EsquemaBase):
    """Esquema para actualización de usuario."""
    rol: Optional[str] = None
    estado_usuario: Optional[bool] = None
    ultimo_acceso: Optional[str] = None
    usuario_sistema: str

class CambioPassword(EsquemaBase):
    """Esquema para cambio de contraseña."""
    password_actual: str
    password_nueva: str = Field(..., min_length=8)
