from typing import Optional
from pydantic import BaseModel


class DatosAdicionalesCambioEstado(BaseModel):
    costo_anterior: Optional[int] = None
    costo_nuevo: Optional[int] = None
    prioridad_anterior: Optional[str] = None
    prioridad_nueva: Optional[str] = None


class DatosAdicionalesCotizacion(BaseModel):
    id_cotizacion: int
    id_proveedor: int
    valor_total: int
    valor_materiales: int
    valor_mano_obra: int


class DatosAdicionalesAprobacion(BaseModel):
    id_cotizacion_aprobada: int
    id_proveedor: int
    costo_incidente: int
    aprobado_por: str


class DatosAdicionalesCancelacion(BaseModel):
    motivo: str
    costo_incidente: Optional[int] = None


class DatosAdicionalesAsignacionProveedor(BaseModel):
    id_proveedor: int
    nombre_proveedor: Optional[str] = None
