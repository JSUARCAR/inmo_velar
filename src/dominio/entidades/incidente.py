from dataclasses import dataclass, field, replace
from datetime import datetime
from typing import Optional


@dataclass(frozen=True)
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
    estado_pago: str = (
        "Pendiente"  # Pendiente, Parcialmente Pagado, Pagado
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
    cotizaciones_resumen: Optional[list] = field(default_factory=list)

    # Datos adicionales de relaciones (Optimizacion N+1)
    nombre_propietario: Optional[str] = None
    telefono_propietario: Optional[str] = None
    nombre_inquilino: Optional[str] = None
    telefono_inquilino: Optional[str] = None
    nombre_habitante: Optional[str] = None
    telefono_habitante: Optional[str] = None

    def avanzar_estado(self, nuevo_estado: str, usuario: str) -> "Incidente":
        """
        Validar y ejecutar transiciones de estado devolviendo una nueva instancia.
        Flujo: Reportado -> En Revision -> Cotizado -> Aprobado -> En Reparacion -> Finalizado
        """
        transiciones_validas = {
            "Reportado": [
                "En Revision",
                "Cancelado",
                "Finalizado",
            ],  # Finalizado directo
            "En Revision": [
                "Cotizado",
                "En Reparacion",
                "Cancelado",
                "Finalizado",  # Finalizado directo
            ],
            "Cotizado": ["Aprobado", "Cancelado", "Finalizado"],  # Finalizado directo
            "Aprobado": [
                "En Reparacion",
                "Cancelado",
                "Finalizado",
            ],  # Finalizado directo
            "En Reparacion": ["Finalizado", "Cancelado"],
            "Finalizado": [],  # Estado final
            "Cancelado": [],  # Estado final
        }

        if nuevo_estado not in transiciones_validas.get(self.estado, []):
            raise ValueError(f"No se puede pasar de {self.estado} a {nuevo_estado}")

        cambios = {
            "estado": nuevo_estado,
            "updated_by": usuario,
            "updated_at": datetime.now(),
        }

        if nuevo_estado == "Finalizado":
            cambios["fecha_arreglo"] = datetime.now()
            cambios["dias_sin_resolver"] = 0

        return replace(self, **cambios)

    def calcular_dias_sin_resolver(self) -> int:
        if self.estado in ["Finalizado", "Cancelado"]:
            return 0
        dias = (datetime.now() - self.fecha_incidente).days
        return max(0, dias)
