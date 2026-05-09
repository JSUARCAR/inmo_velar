"""
DTOs para el módulo de Recaudos.
Esquemas de entrada/salida para la capa de aplicación.
Validaciones estrictas con Pydantic v2.
"""
from datetime import date
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator

from src.dominio.constantes.recaudo import MetodoPago, TipoConcepto


class ComandoRegistrarPago(BaseModel):
    """Comando para registrar un nuevo pago."""
    id_contrato_a: int = Field(gt=0, description="ID del contrato de arrendamiento")
    fecha_pago: date = Field(description="Fecha del pago en formato ISO")
    valor_total: int = Field(gt=0, description="Valor total del pago en pesos")
    metodo_pago: MetodoPago = Field(description="Método de pago utilizado")
    referencia_bancaria: Optional[str] = Field(
        default=None, description="Referencia bancaria (obligatoria si no es efectivo)"
    )
    tipo_concepto: TipoConcepto = Field(
        default=TipoConcepto.CANON, description="Tipo de concepto del pago"
    )
    periodo: str = Field(
        pattern=r"^\d{4}-\d{2}$", description="Período en formato YYYY-MM"
    )
    observaciones: Optional[str] = Field(
        default=None, description="Observaciones opcionales"
    )

    @field_validator("referencia_bancaria")
    @classmethod
    def validar_referencia(cls, v: Optional[str], info) -> Optional[str]:
        """Valida que la referencia no esté vacía si se proporciona."""
        if v is not None and not v.strip():
            return None
        return v


class ComandoActualizarPago(BaseModel):
    """Comando para actualizar un pago existente."""
    fecha_pago: date = Field(description="Fecha del pago en formato ISO")
    valor_total: int = Field(gt=0, description="Valor total del pago en pesos")
    metodo_pago: MetodoPago = Field(description="Método de pago utilizado")
    referencia_bancaria: Optional[str] = Field(
        default=None, description="Referencia bancaria (obligatoria si no es efectivo)"
    )
    tipo_concepto: TipoConcepto = Field(
        default=TipoConcepto.CANON, description="Tipo de concepto del pago"
    )
    periodo: str = Field(
        pattern=r"^\d{4}-\d{2}$", description="Período en formato YYYY-MM"
    )
    observaciones: Optional[str] = Field(
        default=None, description="Observaciones opcionales"
    )

    @field_validator("referencia_bancaria")
    @classmethod
    def validar_referencia(cls, v: Optional[str], info) -> Optional[str]:
        """Valida que la referencia no esté vacía si se proporciona."""
        if v is not None and not v.strip():
            return None
        return v


class ComandoGenerarMasivo(BaseModel):
    """Comando para generación masiva de pagos."""
    periodo: str = Field(
        pattern=r"^\d{4}-\d{2}$", description="Período en formato YYYY-MM"
    )
    usuario: str = Field(min_length=1, description="Usuario que genera los pagos")


class RecaudoDTO(BaseModel):
    """DTO para representación de recaudo en listados."""
    id_recaudo: int
    id_contrato_a: int
    codigo_contrato: str = ""
    direccion: str = ""
    matricula: str = ""
    arrendatario: str = ""
    fecha_pago: str = ""
    valor_total: int = 0
    valor_total_view: str = ""
    metodo_pago: str = ""
    referencia: str = ""
    estado: str = ""
    observaciones: str = ""


class ConceptoDTO(BaseModel):
    """DTO para representación de un concepto de recaudo."""
    tipo: str = ""
    periodo: str = ""
    valor: int = 0
    valor_view: str = ""


class RecaudoDetalleDTO(BaseModel):
    """DTO para detalle completo de recaudo."""
    id_recaudo: int
    id_contrato: int = 0
    direccion: str = ""
    matricula: str = ""
    arrendatario: str = ""
    fecha_pago: str = ""
    valor_total: int = 0
    valor_total_view: str = ""
    metodo_pago: str = ""
    referencia: str = ""
    estado: str = ""
    observaciones: str = ""
    created_at: str = ""
    created_by: str = ""
    conceptos: List[ConceptoDTO] = Field(default_factory=list)


class ResultadoGeneracionMasiva(BaseModel):
    """Resultado de generación masiva de recaudos."""
    generados: int = 0
    omitidos_por_duplicidad: int = 0
    periodo: str = ""


class ResultadoOperacion(BaseModel):
    """Resultado estándar de una operación sobre recaudos."""
    exito: bool = False
    mensaje: str = ""
    id_recaudo: Optional[int] = None
