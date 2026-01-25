from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class HistorialIncidente:
    """
    Entidad para registrar el historial de cambios de estado de un incidente.
    Permite auditoría completa de todas las operaciones realizadas.
    """

    id_historial: Optional[int] = None
    id_incidente: int = 0
    estado_anterior: Optional[str] = None
    estado_nuevo: str = ""
    fecha_cambio: datetime = field(default_factory=datetime.now)
    usuario: str = ""
    comentario: Optional[str] = None
    tipo_accion: str = "CAMBIO_ESTADO"  # CREACION, CAMBIO_ESTADO, COTIZACION_*, etc.
    datos_adicionales: Optional[str] = None  # JSON string para datos extra
    created_at: datetime = field(default_factory=datetime.now)

    # Tipos de acción válidos
    TIPOS_ACCION = [
        "CREACION",
        "CAMBIO_ESTADO",
        "COTIZACION_AGREGADA",
        "COTIZACION_APROBADA",
        "COTIZACION_RECHAZADA",
        "ASIGNACION_PROVEEDOR",
        "MODIFICACION_COSTO",
        "CANCELACION",
    ]

    def to_dict(self) -> dict:
        """Convierte la entidad a diccionario para serialización."""
        return {
            "id_historial": self.id_historial,
            "id_incidente": self.id_incidente,
            "estado_anterior": self.estado_anterior,
            "estado_nuevo": self.estado_nuevo,
            "fecha_cambio": (
                self.fecha_cambio.isoformat()
                if isinstance(self.fecha_cambio, datetime)
                else self.fecha_cambio
            ),
            "usuario": self.usuario,
            "comentario": self.comentario,
            "tipo_accion": self.tipo_accion,
            "datos_adicionales": self.datos_adicionales,
        }
