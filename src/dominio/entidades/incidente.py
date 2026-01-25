from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Incidente:
    id_incidente: Optional[int] = None
    id_propiedad: int = 0
    id_contrato_m: Optional[int] = None
    descripcion_incidente: str = ""
    costo_incidente: int = 0
    fecha_incidente: datetime = field(default_factory=datetime.now)
    prioridad: str = "Media"  # Baja, Media, Alta, Urgente
    origen_reporte: str = "Inquilino"  # Inquilino, Propietario, Inmobiliaria
    responsable_pago: Optional[str] = None  # Inquilino, Propietario, Inmobiliaria
    id_proveedor_asignado: Optional[int] = None
    id_cotizacion_aprobada: Optional[int] = None
    quien_arregla: Optional[str] = None
    aprobado_por: Optional[str] = None
    fecha_arreglo: Optional[datetime] = None
    estado: str = (
        "Reportado"  # Reportado, En Revision, Cotizado, Aprobado, En Reparacion, Finalizado, Cancelado
    )
    dias_sin_resolver: int = 0
    motivo_cancelacion: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    created_by: Optional[str] = None
    updated_at: datetime = field(default_factory=datetime.now)
    updated_by: Optional[str] = None

    # Relaciones - se llenan en consulta
    direccion_propiedad: Optional[str] = None
    nombre_proveedor: Optional[str] = None

    def avanzar_estado(self, nuevo_estado: str, usuario: str) -> None:
        """
        Validar y ejecutar transiciones de estado.
        Flujo: Reportado -> En Revision -> Cotizado -> Aprobado -> En Reparacion -> Finalizado
        """
        transiciones_validas = {
            "Reportado": ["En Revision", "Cancelado"],
            "En Revision": [
                "Cotizado",
                "En Reparacion",
                "Cancelado",
            ],  # En Reparacion si es emergencia sin cotizacion
            "Cotizado": ["Aprobado", "Cancelado"],
            "Aprobado": ["En Reparacion", "Cancelado"],
            "En Reparacion": ["Finalizado", "Cancelado"],
            "Finalizado": [],  # Estado final
            "Cancelado": [],  # Estado final
        }

        if nuevo_estado not in transiciones_validas.get(self.estado, []):
            raise ValueError(f"No se puede pasar de {self.estado} a {nuevo_estado}")

        self.estado = nuevo_estado
        self.updated_by = usuario
        self.updated_at = datetime.now()

        if nuevo_estado == "Finalizado":
            self.fecha_arreglo = datetime.now()
