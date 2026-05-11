"""
DTOs para el módulo de Recaudos.
Esquemas de entrada/salida para la capa de aplicación.
Validaciones estrictas con Pydantic v2 e implementación de Mappers.
"""
from datetime import date, datetime
from typing import Any, Dict, List, Optional

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
    id_contrato: int = 0
    codigo_contrato: str = ""
    direccion: str = ""
    matricula: str = ""
    arrendatario: str = ""
    fecha_pago: str = ""
    fecha_pago_contrato: str = "N/A"
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


class EmpresaDTO(BaseModel):
    """DTO para información de la empresa en documentos."""
    nombre: str
    nit: str
    direccion: str
    telefono: str
    email: str
    logo_base64: Optional[str] = None
    website: Optional[str] = None


class RecaudoEnriquecidoPDFDTO(BaseModel):
    """DTO enriquecido para la generación de PDFs Élite."""
    id: int
    periodo: str
    fecha_generacion: str
    estado: str
    propietario: str = "Inmobiliaria Velar"
    documento: str = "N/A"
    direccion_propietario: str = "N/A"
    propiedad: str
    matricula: str
    municipio: str
    departamento: str
    arrendatario: str
    arrendatario_doc: str
    email: str
    telefono: str
    valor_total: int
    canon: int
    otros_ingresos: int = 0
    total_ingresos: int
    comision_pct: float = 0
    comision_monto: int = 0
    iva_comision: int = 0
    impuesto_4x1000: int = 0
    gastos_admin: int = 0
    gastos_serv: int = 0
    gastos_rep: int = 0
    otros_egr: int = 0
    total_egresos: int = 0
    neto_pagar: int
    fecha_pago: str
    metodo_pago: str
    referencia_pago: str
    cuenta_bancaria: str = "No aplica"
    tipo_cuenta: str
    banco: str = "Caja General"
    observaciones: str
    empresa: Optional[EmpresaDTO] = None
    logo_base64: Optional[str] = None
    created_at: str
    created_by: str = "Sistema"


class RecaudoMapper:
    """Mapper encargado de transformar datos entre capas."""

    @staticmethod
    def map_to_dto(row: Dict[str, Any]) -> RecaudoDTO:
        """Transforma una fila del repositorio en un RecaudoDTO."""
        return RecaudoDTO(
            id_recaudo=row.get("id_recaudo", 0),
            id_contrato=row.get("id_contrato", 0),
            codigo_contrato=row.get("codigo_contrato", ""),
            direccion=row.get("direccion", ""),
            matricula=row.get("matricula", ""),
            arrendatario=row.get("arrendatario", ""),
            fecha_pago=row.get("fecha_pago", ""),
            fecha_pago_contrato=row.get("fecha_pago_contrato", "N/A"),
            valor_total=row.get("valor_total", 0),
            metodo_pago=row.get("metodo_pago", ""),
            referencia=row.get("referencia", ""),
            estado=row.get("estado", ""),
            observaciones=row.get("observaciones", ""),
        )

    @staticmethod
    def map_to_pdf_dto(
        rec: Dict[str, Any], empresa: Optional[EmpresaDTO] = None, periodo_fallback: str = ""
    ) -> RecaudoEnriquecidoPDFDTO:
        """Transforma un recaudo enriquecido del repositorio en un RecaudoEnriquecidoPDFDTO."""
        # Extraer período del primer concepto si existe
        periodo_actual = periodo_fallback
        if rec.get("conceptos"):
            periodo_actual = rec["conceptos"][0].get("periodo", periodo_fallback)

        observaciones_final = (
            f"Arrendatario: {rec['nombre_arrendatario']} ({rec['documento_arrendatario']}). "
            f"{rec.get('observaciones', '')}"
        ).strip()

        return RecaudoEnriquecidoPDFDTO(
            id=rec["id_recaudo"],
            periodo=periodo_actual,
            fecha_generacion=rec["fecha_pago"],
            estado=rec["estado_recaudo"],
            propiedad=rec["direccion_propiedad"],
            matricula=rec.get("matricula_inmobiliaria") or "Sin matrícula",
            municipio=rec.get("municipio", "Armenia").upper(),
            departamento=rec.get("departamento", "Quindío").upper(),
            arrendatario=rec["nombre_arrendatario"],
            arrendatario_doc=rec["documento_arrendatario"],
            email=rec.get("email_arrendatario") or "No registrado",
            telefono=rec.get("telefono_arrendatario") or "No registrado",
            valor_total=rec["valor_total"],
            canon=rec["valor_total"],
            total_ingresos=rec["valor_total"],
            neto_pagar=rec["valor_total"],
            fecha_pago=rec["fecha_pago"],
            metodo_pago=rec["metodo_pago"] or "N/A",
            referencia_pago=rec.get("referencia_bancaria") or "N/A",
            tipo_cuenta=rec["metodo_pago"] or "Efectivo",
            observaciones=observaciones_final,
            empresa=empresa,
            logo_base64=empresa.logo_base64 if empresa else None,
            created_at=datetime.now().isoformat(),
        )


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
