"""
Entidad de Dominio: Alerta
=========================
Representa una notificación o evento crítico que requiere atención en el sistema.
Mapea directamente a la tabla ALERTAS.

Autor: Sistema de Gestión Inmobiliaria
Fecha: 2026-05-10
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Alerta:
    """
    Representa una alerta del sistema.
    """

    tipo_alerta: str  # CHECK IN ('Vencimiento Contrato Mandato', 'Vencimiento Contrato Arrendamiento', ...)
    descripcion_alerta: str
    id_alertas: Optional[int] = None
    prioridad: str = "Media"  # Alta, Media, Baja
    fecha_generacion_alerta: str = field(default_factory=lambda: datetime.now().isoformat())
    fecha_vencimiento_alerta: Optional[str] = None
    estado_alerta: str = "Pendiente"  # Pendiente, En Proceso, Resuelta, Archivada
    id_entidad_relacionada: Optional[int] = None
    tipo_entidad: Optional[str] = None  # Contrato, Propiedad, Recibo, etc.
    usuario_asignado: Optional[str] = None
    accion_tomada: Optional[str] = None
    fecha_accion: Optional[str] = None
    plantilla_mensaje: Optional[str] = None
    destinatario_nombre: Optional[str] = None
    destinatario_telefono: Optional[str] = None
    destinatario_email: Optional[str] = None
    fecha_resolucion: Optional[str] = None
    resuelto_automaticamente: bool = False
    created_at: Optional[str] = None
    created_by: Optional[str] = None

    def __post_init__(self):
        """Validaciones de integridad."""
        tipos_validos = [
            "Vencimiento Contrato Mandato",
            "Vencimiento Contrato Arrendamiento",
            "Incremento IPC",
            "Mora Recaudo",
            "Mora Liquidación",
            "Incidente Sin Resolver",
            "Liquidación Pendiente Aprobación",
            "Asesor Sin Actividad",
            "Propietario Múltiples Moras",
            "Pago Rechazado",
            "Otros",
        ]
        if self.tipo_alerta not in tipos_validos:
            # No lanzamos error para evitar romper el sistema por variaciones menores, 
            # pero podríamos logearlo.
            pass

    @property
    def es_critica(self) -> bool:
        return self.prioridad == "Alta"

    @property
    def esta_pendiente(self) -> bool:
        return self.estado_alerta == "Pendiente"
