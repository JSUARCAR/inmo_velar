"""
Entidad: Propiedad

Mapeo exacto de la tabla PROPIEDADES.
"""

from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime

@dataclass
class Propiedad:
    """
    Entidad: Propiedad
    Tabla: PROPIEDADES
    
    Columnas:
    - ID_PROPIEDAD
    - MATRICULA_INMOBILIARIA
    - ID_MUNICIPIO (FK)
    - DIRECCION_PROPIEDAD
    - TIPO_PROPIEDAD
    - DISPONIBILIDAD_PROPIEDAD
    - AREA_M2 (REAL)
    - HABITACIONES, BANO, PARQUEADERO (Integers)
    - ESTRATO
    - VALOR_ADMINISTRACION
    - CANON_ARRENDAMIENTO_ESTIMADO
    - VALOR_VENTA_PROPIEDAD
    - COMISION_VENTA_PROPIEDAD
    - OBSERVACIONES_PROPIEDAD
    - CODIGO_ENERGIA, CODIGO_AGUA, CODIGO_GAS (Códigos CIU de servicios públicos - Opcionales)
    - FECHA_INGRESO_PROPIEDAD
    - ESTADO_REGISTRO, MOTIVO_INACTIVACION
    - Audit
    """
    
    id_propiedad: Optional[int] = None
    matricula_inmobiliaria: str = ""
    id_municipio: int = 0
    direccion_propiedad: str = ""
    tipo_propiedad: str = ""
    
    disponibilidad_propiedad: Optional[int] = 1 # 1: Disponible?
    area_m2: float = 0.0
    
    habitaciones: Optional[int] = None
    bano: Optional[int] = None
    parqueadero: Optional[int] = None
    estrato: Optional[int] = None
    
    valor_administracion: Optional[int] = None
    canon_arrendamiento_estimado: Optional[int] = None
    valor_venta_propiedad: Optional[int] = None
    comision_venta_propiedad: Optional[int] = None
    
    observaciones_propiedad: Optional[str] = None
    
    # Códigos CIU (Servicios Públicos)
    # Estos códigos identifican la suscripción ante las empresas de servicios públicos.
    # Se usan para consultar facturas y verificar pagos.
    codigo_energia: Optional[str] = None # NIC / NIU Energía
    codigo_agua: Optional[str] = None    # Referencia de Pago Agua
    codigo_gas: Optional[str] = None     # Referencia de Pago Gas
    
    # Información de Administración (para pagos)
    # Datos de contacto y bancarios de la administración del edificio/conjunto
    telefono_administracion: Optional[str] = None      # Teléfono de contacto administración
    tipo_cuenta_administracion: Optional[str] = None   # "Ahorros" | "Corriente"
    numero_cuenta_administracion: Optional[str] = None # Número de cuenta bancaria
    
    fecha_ingreso_propiedad: Optional[str] = None
    
    estado_registro: Optional[int] = 1
    motivo_inactivacion: Optional[str] = None
    
    created_at: Optional[str] = field(default_factory=lambda: datetime.now().isoformat())
    created_by: Optional[str] = None
    updated_at: Optional[str] = None
    updated_by: Optional[str] = None

    # Transient / UI
    imagen_principal_id: Optional[int] = None
