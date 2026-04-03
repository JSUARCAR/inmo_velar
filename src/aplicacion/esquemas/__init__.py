"""
Paquete de esquemas (DTOs) de la capa de aplicación.
Re-exporta los esquemas base de autenticación para compatibilidad.
"""

from typing import Optional, List, Dict, Any
from datetime import date
from pydantic import BaseModel, ConfigDict, Field


class EsquemaBase(BaseModel):
    """Configuración base para todos los esquemas."""

    model_config = ConfigDict(from_attributes=True)


class RecaudoReporteDTO(BaseModel):
    """DTO para reporte de recaudos."""

    id_recaudo: int
    id_contrato_a: int
    direccion_inmueble: str
    matricula: Optional[str] = None
    nombre_arrendatario: str
    telefono_arrendatario: Optional[str] = None
    email_arrendatario: Optional[str] = None
    fecha_pago: str
    valor_total: int
    metodo_pago: str
    referencia_bancaria: Optional[str] = None
    estado_recaudo: str
    periodo_facturado: Optional[str] = None
    observaciones: Optional[str] = None
    created_at: Optional[str] = None


class FiltrosReporteRecaudos(BaseModel):
    """Filtros para el reporte de recaudos."""

    estado: Optional[str] = Field(
        default="Todos", description="Filtro por estado del recaudo"
    )
    metodo_pago: Optional[str] = Field(
        default="Todos", description="Filtro por método de pago"
    )
    periodo_inicio: Optional[str] = Field(
        default=None, pattern=r"^\d{4}-\d{2}$", description="Período inicial YYYY-MM"
    )
    periodo_fin: Optional[str] = Field(
        default=None, pattern=r"^\d{4}-\d{2}$", description="Período final YYYY-MM"
    )
    busqueda: Optional[str] = None


class InformeRecaudosInput(BaseModel):
    """DTO para generar informe PDF de recaudos."""

    periodo_inicio: str = Field(
        ..., pattern=r"^\d{4}-\d{2}$", description="Período inicial YYYY-MM"
    )
    periodo_fin: str = Field(
        ..., pattern=r"^\d{4}-\d{2}$", description="Período final YYYY-MM"
    )
    filtros: Optional[FiltrosReporteRecaudos] = None


class ResumenRecaudosDTO(BaseModel):
    """Resumen financiero para informe de recaudos."""

    total_recaudos: int = 0
    total_aplicados: int = 0
    total_pendientes: int = 0
    total_reversados: int = 0
    cantidad_registros: int = 0


class TotalesMetodoPagoDTO(BaseModel):
    """Totales agrupados por método de pago."""

    cantidad: int = 0
    valor: int = 0


class InformeRecaudosDetalleDTO(BaseModel):
    """Detalle de un recaudo para el informe PDF."""

    id_recaudo: int
    fecha_pago: str
    direccion: str
    arrendatario: str
    valor_total: int
    metodo_pago: str
    estado: str
    periodo: Optional[str] = None


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
