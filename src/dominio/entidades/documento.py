from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Union

@dataclass
class Documento:
    """
    Entidad que representa un documento (archivo) adjunto a otra entidad del sistema.
    Almacena tanto la metadata como el contenido binario (BLOB).
    """
    id: Optional[int] = None
    entidad_tipo: str = "" # Ejemplo: 'CONTRATO', 'INCIDENTE'
    entidad_id: str = "" # ID de la entidad relacionada
    nombre_archivo: str = ""
    extension: str = ""
    mime_type: str = ""
    descripcion: str = ""
    contenido: Optional[bytes] = None # BLOB - Puede ser None si se cargó con 'lazy loading'
    version: int = 1
    es_vigente: bool = True
    created_at: Optional[datetime] = None
    created_by: Optional[str] = None
    
    def __post_init__(self):
        if not self.entidad_tipo:
            raise ValueError("El tipo de entidad es obligatorio")
        if not self.entidad_id:
            raise ValueError("El ID de entidad es obligatorio")
        if not self.nombre_archivo:
            raise ValueError("El nombre del archivo es obligatorio")

    @property
    def tamanio_kb(self) -> float:
        """Calcula el tamaño en KB si el contenido está cargado."""
        if self.contenido:
            return len(self.contenido) / 1024.0
        return 0.0

    @property
    def extension_normalizada(self) -> str:
        """Retorna la extensión sin punto y en minúsculas."""
        if self.extension:
            return self.extension.lower().replace('.', '')
        return ""
