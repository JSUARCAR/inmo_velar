# 🎯 PLAN MAESTRO ÉLITE - MÓDULO RECAUDOS
## Sistema Velar - Inmobiliaria Inmobiliaria Velar SAS
### Versión: 1.0.0 | Fecha: 2026-04-03

---

## 📋 RESUMEN EJECUTIVO

Este documento define la hoja de ruta completa para la refactorización de élite del módulo de Recaudos,
aplicando principios de **Clean Architecture**, **Domain-Driven Design** y **Patrones Empresariales**.

**Alcance:** Entidades, Repositorios, Servicios de Aplicación, Estados Reflex, Tests y Limpieza Legacy

**Esfuerzo estimado:** 18 horas | **Prioridad:** CRÍTICA

---

## 🔴 DIAGNÓSTICO ACTUAL

### Problemas Identificados

| # | Problema | Gravedad | Impacto |
|---|----------|----------|---------|
| 1 | Queries SQL en State (violación Clean Architecture) | CRÍTICA | Acoplamiento directo a BD |
| 2 | Usuario "admin" hardcodeado | ALTA | Falla seguridad RBAC |
| 3 | Sin Value Objects tipados | ALTA | Magic strings en código |
| 4 | Sin tests unitarios | ALTA | Riesgo regresiones |
| 5 | Views Flet legacy presentes | MEDIA | Código obsoleto sin uso |
| 6 | Validaciones duplicadas (entidad + state) | MEDIA | Mantenimiento difícil |
| 7 | Código duplicado en servicio_financiero | MEDIA | DRY violado |

### Inventario de Archivos Actuales

```
MÓDULO RECAUDOS - ESTADO ACTUAL
═══════════════════════════════════════════════════════════════

CAPA DE DOMINIO
├── src/dominio/entidades/recaudo.py              [65 líneas] ✓
├── src/dominio/entidades/recaudo_concepto.py     [45 líneas] ✓
└── src/dominio/interfaces/repositorio_recaudo.py [18 líneas] ✓

CAPA DE APLICACIÓN
├── src/aplicacion/servicios/servicio_recaudo.py  [99 líneas] ✓
└── src/aplicacion/servicios/servicio_financiero.py [414 líneas] ⚠️

CAPA DE INFRAESTRUCTURA
├── src/infraestructura/persistencia/
│   └── repositorio_recaudo.py                   [438 líneas] ⚠️

CAPA DE PRESENTACIÓN (Reflex)
├── src/presentacion_reflex/pages/recaudos.py      [414 líneas]
├── src/presentacion_reflex/state/recaudos_state.py [748 líneas] ⚠️
└── src/presentacion_reflex/components/recaudos/
    ├── modal_form.py                             [303 líneas]
    └── detail_modal.py                           [260 líneas]

LEGACY (A ELIMINAR)
├── src/presentacion/views/recaudo_form_view.py   [506 líneas] ❌
├── src/presentacion/views/recaudos_list_view.py  [416 líneas] ❌
└── scripts/diagnostico/*.py                      [varios] ❌
```

---

## 🎯 ARQUITECTURA OBJETIVO

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        CAPA DE PRESENTACIÓN                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────────────┐  │
│  │ pages/recaudos  │  │  State Limpio   │  │    Components/Mixins       │  │
│  │    (Vista)      │◀─│  (Delegación)   │─▶│   (UI Reutilizable)        │  │
│  └─────────────────┘  └────────┬────────┘  └─────────────────────────────┘  │
└─────────────────────────────────┼─────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        CAPA DE APLICACIÓN                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │                      ServicioRecaudo                                  │  │
│  │  • registrar_pago()      • aplicar_pago()                           │  │
│  │  • reversar_pago()       • generar_masivo()                        │  │
│  │  • obtener_detalle()      • listar()                                │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────┬─────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           CAPA DE DOMINIO                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│  ┌────────────────┐  ┌────────────────────┐  ┌────────────────────────────┐ │
│  │ Recaudo        │  │ RecaudoConcepto   │  │ IRepositorioRecaudo       │ │
│  │ (Entidad)      │  │ (Entidad)          │  │ (Puerto/Interface)         │ │
│  └────────────────┘  └────────────────────┘  └────────────────────────────┘ │
│                                                                            │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │                    VALUE OBJECTS / CONSTANTES                           │ │
│  │  MetodoPago (Enum) | EstadoRecaudo (Enum) | TipoConcepto (Enum)      │ │
│  │  Dinero (Value Object) | Periodo (Value Object) | AuditInfo            │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────┬─────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        CAPA DE INFRAESTRUCTURA                              │
├─────────────────────────────────────────────────────────────────────────────┤
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │                  RepositorioRecaudo                                   │  │
│  │  Implementación PostgreSQL (Producción) / SQLite (Desarrollo)        │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                                                            │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │                  SERVICIOS EXTERNOS                                   │  │
│  │  • ServicioPDF (ReciboRecaudoElite)                                  │  │
│  │  • ServicioDocumentos (DocumentosStateMixin)                          │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 📦 FASE 1: VALUE OBJECTS Y CONSTANTES
### Prioridad: CRÍTICA | Esfuerzo: 2h

### 1.1 Crear Archivo de Constantes

**Archivo:** `src/dominio/constantes/recaudo.py`

```python
"""
Constantes y Enums del Dominio de Recaudos.
Sistema Velar - Inmobiliaria Velar SAS
"""
from enum import Enum
from typing import Final

class MetodoPago(str, Enum):
    """Métodos de pago válidos para un recaudo."""
    EFECTIVO: Final = "Efectivo"
    TRANSFERENCIA: Final = "Transferencia"
    PSE: Final = "PSE"
    CONSIGNACION: Final = "Consignación"
    
    @classmethod
    def valores(cls) -> list[str]:
        return [e.value for e in cls]
    
    @classmethod
    def requiere_referencia(cls, metodo: "MetodoPago") -> bool:
        return metodo != cls.EFECTIVO

class EstadoRecaudo(str, Enum):
    """Estados posibles de un recaudo."""
    PENDIENTE: Final = "Pendiente"
    APLICADO: Final = "Aplicado"
    REVERSADO: Final = "Reversado"
    
    @classmethod
    def valores(cls) -> list[str]:
        return [e.value for e in cls]
    
    def puede_editarse(self) -> bool:
        return self == EstadoRecaudo.PENDIENTE
    
    def puede_aplicarse(self) -> bool:
        return self == EstadoRecaudo.PENDIENTE
    
    def puede_reversarse(self) -> bool:
        return self == EstadoRecaudo.APLICADO

class TipoConcepto(str, Enum):
    """Tipos de concepto que puede incluir un recaudo."""
    CANON: Final = "Canon"
    ADMINISTRACION: Final = "Administración"
    MORA: Final = "Mora"
    SERVICIOS: Final = "Servicios"
    OTRO: Final = "Otro"
    
    @classmethod
    def valores(cls) -> list[str]:
        return [e.value for e in cls]
```

### 1.2 Crear Value Objects

**Archivo:** `src/dominio/value_objects/periodo.py`

```python
"""
Value Object: Periodo
Representa un período en formato YYYY-MM.
"""
from dataclasses import dataclass
from datetime import date
from typing import Final

@final
@dataclass(frozen=True)
class Periodo:
    """Período inmutable en formato YYYY-MM."""
    valor: str
    
    def __post_init__(self):
        if len(self.valor) != 7 or self.valor[4] != "-":
            raise ValueError(f"Formato de período inválido: {self.valor}. Use YYYY-MM")
        try:
            año = int(self.valor[:4])
            mes = int(self.valor[5:])
            if not (1900 <= año <= 2100 and 1 <= mes <= 12):
                raise ValueError(f"Fecha inválida: {self.valor}")
        except ValueError as e:
            raise ValueError(f"Período inválido: {self.valor}") from e
    
    @classmethod
    def actual(cls) -> "Periodo":
        hoy = date.today()
        return cls(f"{hoy.year}-{hoy.month:02d}")
    
    @classmethod
    def desde_fecha(cls, fecha: date) -> "Periodo":
        return cls(f"{fecha.year}-{fecha.month:02d}")
    
    @property
    def año(self) -> int:
        return int(self.valor[:4])
    
    @property
    def mes(self) -> int:
        return int(self.valor[5:])
```

**Archivo:** `src/dominio/value_objects/audit_info.py`

```python
"""
Value Object: AuditInfo
Información de auditoría para entidades.
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

@final
@dataclass(frozen=True)
class AuditInfo:
    """Información de auditoría inmutable."""
    created_at: datetime = field(default_factory=datetime.now)
    created_by: Optional[str] = None
    updated_at: Optional[datetime] = None
    updated_by: Optional[str] = None
    
    def con_update(self, usuario: str) -> "AuditInfo":
        return AuditInfo(
            created_at=self.created_at,
            created_by=self.created_by,
            updated_at=datetime.now(),
            updated_by=usuario
        )
```

### 1.3 Refactorizar Entidades

**Archivo:** `src/dominio/entidades/recaudo.py` (REFACTORIZAR)

```python
"""
Entidad de Dominio: Recaudo
Representa un pago recibido del inquilino a la inmobiliaria.
"""
from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Optional, List
from src.dominio.constantes.recaudo import MetodoPago, EstadoRecaudo
from src.dominio.value_objects.audit_info import AuditInfo

@final
@dataclass(frozen=True)
class Recaudo:
    """
    Entidad que representa un pago recibido del inquilino.
    
    Business Rules:
    - Valor total debe ser > 0
    - Referencia bancaria es obligatoria para métodos electrónicos
    - NO se permiten pagos parciales (debe cubrir el monto completo del concepto)
    - SÍ se permiten pagos anticipados (múltiples meses)
    """
    id_recaudo: Optional[int] = None
    id_contrato_a: int = 0
    fecha_pago: date = field(default_factory=date.today)
    valor_total: int = 0
    metodo_pago: MetodoPago = MetodoPago.EFECTIVO
    referencia_bancaria: Optional[str] = None
    estado: EstadoRecaudo = EstadoRecaudo.PENDIENTE
    observaciones: Optional[str] = None
    audit: AuditInfo = field(default_factory=AuditInfo)
    
    def __post_init__(self):
        if self.valor_total <= 0:
            raise ValueError("El valor del recaudo debe ser mayor a cero")
        
        if MetodoPago.requiere_referencia(self.metodo_pago) and not self.referencia_bancaria:
            raise ValueError("La referencia bancaria es obligatoria para pagos electrónicos")
    
    @property
    def esta_aplicado(self) -> bool:
        return self.estado == EstadoRecaudo.APLICADO
    
    @property
    def esta_reversado(self) -> bool:
        return self.estado == EstadoRecaudo.REVERSADO
    
    def cambiar_estado(self, nuevo_estado: EstadoRecaudo, usuario: str) -> "Recaudo":
        if not self.estado.puede_editarse():
            raise ValueError(f"No se puede modificar un recaudo en estado {self.estado.value}")
        
        if nuevo_estado == EstadoRecaudo.APLICADO and not self.estado.puede_aplicarse():
            raise ValueError("Solo se pueden aplicar pagos en estado Pendiente")
        
        if nuevo_estado == EstadoRecaudo.REVERSADO and not self.estado.puede_reversarse():
            raise ValueError("Solo se pueden reversar pagos en estado Aplicado")
        
        return Recaudo(
            id_recaudo=self.id_recaudo,
            id_contrato_a=self.id_contrato_a,
            fecha_pago=self.fecha_pago,
            valor_total=self.valor_total,
            metodo_pago=self.metodo_pago,
            referencia_bancaria=self.referencia_bancaria,
            estado=nuevo_estado,
            observaciones=self.observaciones,
            audit=self.audit.con_update(usuario)
        )
```

---

## 📦 FASE 2: INTERFACES Y DTOs
### Prioridad: CRÍTICA | Esfuerzo: 1h

### 2.1 Expandir Interface de Repositorio

**Archivo:** `src/dominio/interfaces/repositorio_recaudo.py` (REFACTORIZAR)

```python
"""
Interface (Puerto): Repositorio de Recaudos.
Definición del contrato para persistencia de pagos.
"""
from abc import ABC, abstractmethod
from typing import List, Optional, Protocol, TypeVar
from src.dominio.entidades.recaudo import Recaudo
from src.dominio.entidades.recaudo_concepto import RecaudoConcepto
from src.dominio.constantes.recaudo import EstadoRecaudo

T = TypeVar("T")

class PaginatedResult(Protocol[T]):
    items: List[T]
    total: int
    page: int
    page_size: int
    total_pages: int

@dataclass(frozen=True)
class FiltrosRecaudo:
    estado: Optional[EstadoRecaudo] = None
    fecha_desde: Optional[str] = None
    fecha_hasta: Optional[str] = None
    id_contrato: Optional[int] = None
    busqueda: Optional[str] = None
    page: int = 1
    page_size: int = 25

class IRepositorioRecaudo(ABC):
    """Puerto abstracto para repositorio de recaudos."""
    
    @abstractmethod
    def obtener_por_id(self, id_recaudo: int) -> Optional[Recaudo]:
        raise NotImplementedError
    
    @abstractmethod
    def listar_por_contrato(self, id_contrato_a: int) -> List[Recaudo]:
        raise NotImplementedError
    
    @abstractmethod
    def listar_paginado(self, filtros: FiltrosRecaudo) -> PaginatedResult[Recaudo]:
        raise NotImplementedError
    
    @abstractmethod
    def crear(self, recaudo: Recaudo, conceptos: List[RecaudoConcepto]) -> Recaudo:
        raise NotImplementedError
    
    @abstractmethod
    def actualizar(self, recaudo: Recaudo, usuario: str) -> None:
        raise NotImplementedError
    
    @abstractmethod
    def cambiar_estado(self, id_recaudo: int, nuevo_estado: EstadoRecaudo, usuario: str) -> None:
        raise NotImplementedError
    
    @abstractmethod
    def eliminar(self, id_recaudo: int) -> None:
        raise NotImplementedError
    
    @abstractmethod
    def obtener_conceptos(self, id_recaudo: int) -> List[RecaudoConcepto]:
        raise NotImplementedError
    
    @abstractmethod
    def crear_masivo(self, items: List[tuple[Recaudo, List[RecaudoConcepto]]]) -> int:
        raise NotImplementedError
```

### 2.2 Crear DTOs de Aplicación

**Archivo:** `src/aplicacion/esquemas/recaudo.py`

```python
"""
DTOs para el módulo de Recaudos.
Esquemas de entrada/salida para la capa de aplicación.
"""
from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator
from src.dominio.constantes.recaudo import MetodoPago, TipoConcepto

class ComandoRegistrarPago(BaseModel):
    """Comando para registrar un nuevo pago."""
    id_contrato_a: int = Field(gt=0)
    fecha_pago: date
    valor_total: int = Field(gt=0)
    metodo_pago: MetodoPago
    referencia_bancaria: Optional[str] = None
    tipo_concepto: TipoConcepto
    periodo: str = Field(pattern=r"^\d{4}-\d{2}$")
    observaciones: Optional[str] = None
    
    @field_validator("referencia_bancaria")
    @classmethod
    def validar_referencia(cls, v, info):
        # Validación contextual
        return v

class ComandoGenerarMasivo(BaseModel):
    """Comando para generación masiva de pagos."""
    periodo: str = Field(pattern=r"^\d{4}-\d{2}$")
    usuario: str

class RecaudoDTO(BaseModel):
    """DTO para representación de recaudo."""
    id_recaudo: int
    id_contrato_a: int
    codigo_contrato: str
    direccion: str
    matricula: str
    arrendatario: str
    fecha_pago: str
    valor_total: int
    valor_total_view: str
    metodo_pago: str
    referencia: str
    estado: str
    observaciones: str

class RecaudoDetalleDTO(BaseModel):
    """DTO para detalle completo de recaudo."""
    id_recaudo: int
    id_contrato: int
    direccion: str
    matricula: str
    arrendatario: str
    fecha_pago: str
    valor_total: int
    valor_total_view: str
    metodo_pago: str
    referencia: str
    estado: str
    observaciones: str
    created_at: str
    created_by: str
    conceptos: List[dict]

class ResultadoGeneracionMasiva(BaseModel):
    """Resultado de generación masiva."""
    generados: int
    omitidos_por_duplicidad: int
    periodo: str

class ResultadoOperacion(BaseModel):
    """Resultado estándar de operación."""
    exito: bool
    mensaje: str
    id_recaudo: Optional[int] = None
```

---

## 📦 FASE 3: SERVICIO DE APLICACIÓN
### Prioridad: ALTA | Esfuerzo: 3h

### 3.1 Refactorizar Servicio

**Archivo:** `src/aplicacion/servicios/servicio_recaudo.py` (REFACTORIZAR)

```python
"""
Servicio de Aplicación para Recaudos.
Orquesta la lógica de negocio y coordinación con infraestructura.
"""
from datetime import datetime, date
from typing import List, Optional
from dataclasses import dataclass, field
from src.dominio.constantes.recaudo import MetodoPago, EstadoRecaudo, TipoConcepto
from src.dominio.entidades.recaudo import Recaudo
from src.dominio.entidades.recaudo_concepto import RecaudoConcepto
from src.dominio.interfaces.repositorio_recaudo import (
    IRepositorioRecaudo, 
    FiltrosRecaudo,
    PaginatedResult
)
from src.dominio.value_objects.audit_info import AuditInfo
from src.aplicacion.esquemas.recaudo import (
    ComandoRegistrarPago,
    RecaudoDTO,
    RecaudoDetalleDTO,
    ResultadoGeneracionMasiva,
    ResultadoOperacion
)

@dataclass
class ServicioRecaudo:
    """Servicio de aplicación para gestionar pagos de arrendatarios."""
    
    _repo: IRepositorioRecaudo
    
    def registrar_pago(self, comando: ComandoRegistrarPago, usuario: str) -> Recaudo:
        """
        Registra un nuevo pago.
        
        Args:
            comando: Datos del pago a registrar
            usuario: Usuario que realiza la operación
            
        Returns:
            Entidad Recaudo creada
            
        Raises:
            ValueError: Si los datos son inválidos
        """
        recaudo = Recaudo(
            id_recaudo=None,
            id_contrato_a=comando.id_contrato_a,
            fecha_pago=comando.fecha_pago,
            valor_total=comando.valor_total,
            metodo_pago=comando.metodo_pago,
            referencia_bancaria=comando.referencia_bancaria,
            estado=EstadoRecaudo.PENDIENTE,
            observaciones=comando.observaciones,
            audit=AuditInfo(created_by=usuario)
        )
        
        concepto = RecaudoConcepto(
            tipo_concepto=comando.tipo_concepto,
            periodo=comando.periodo,
            valor=comando.valor_total
        )
        
        return self._repo.crear(recaudo, [concepto])
    
    def aplicar_pago(self, id_recaudo: int, usuario: str) -> ResultadoOperacion:
        """
        Aplica un pago pendiente.
        
        Args:
            id_recaudo: ID del recaudo a aplicar
            usuario: Usuario que realiza la operación
            
        Returns:
            ResultadoOperacion con el resultado
        """
        recaudo = self._repo.obtener_por_id(id_recaudo)
        
        if not recaudo:
            return ResultadoOperacion(
                exito=False,
                mensaje=f"Recaudo {id_recaudo} no encontrado"
            )
        
        if not recaudo.estado.puede_aplicarse():
            return ResultadoOperacion(
                exito=False,
                mensaje=f"Solo se pueden aplicar pagos en estado Pendiente. Estado actual: {recaudo.estado.value}"
            )
        
        self._repo.cambiar_estado(id_recaudo, EstadoRecaudo.APLICADO, usuario)
        
        return ResultadoOperacion(
            exito=True,
            mensaje=f"Pago #{id_recaudo} aplicado exitosamente",
            id_recaudo=id_recaudo
        )
    
    def reversar_pago(self, id_recaudo: int, usuario: str) -> ResultadoOperacion:
        """
        Revierte un pago aplicado.
        
        Args:
            id_recaudo: ID del recaudo a reversar
            usuario: Usuario que realiza la operación
            
        Returns:
            ResultadoOperacion con el resultado
        """
        recaudo = self._repo.obtener_por_id(id_recaudo)
        
        if not recaudo:
            return ResultadoOperacion(
                exito=False,
                mensaje=f"Recaudo {id_recaudo} no encontrado"
            )
        
        if not recaudo.estado.puede_reversarse():
            return ResultadoOperacion(
                exito=False,
                mensaje=f"Solo se pueden reversar pagos en estado Aplicado. Estado actual: {recaudo.estado.value}"
            )
        
        self._repo.cambiar_estado(id_recaudo, EstadoRecaudo.REVERSADO, usuario)
        
        return ResultadoOperacion(
            exito=True,
            mensaje=f"Pago #{id_recaudo} reversado",
            id_recaudo=id_recaudo
        )
    
    def generar_masivo(self, periodo: str, usuario: str, db_manager) -> ResultadoGeneracionMasiva:
        """
        Genera pagos masivos para contratos activos sin recaudo en el período.
        
        Args:
            periodo: Período en formato YYYY-MM
            usuario: Usuario que realiza la operación
            db_manager: Gestor de base de datos para consulta de contratos
            
        Returns:
            ResultadoGeneracionMasiva con el resumen de la operación
        """
       hoy = date.today()
        
        query_contratos = """
            SELECT ID_CONTRATO_A, CANON_ARRENDAMIENTO
            FROM CONTRATOS_ARRENDAMIENTOS
            WHERE ESTADO_CONTRATO_A = 'Activo'
        """
        
        with db_manager.obtener_conexion() as conn:
            cursor = db_manager.get_dict_cursor(conn)
            cursor.execute(query_contratos)
            contratos = cursor.fetchall()
        
        ids_facturados = self._repo.obtener_ids_contratos_con_recaudo(periodo)
        items = []
        omitidos = 0
        
        for contrato in contratos:
            id_contrato = contrato["ID_CONTRATO_A"]
            
            if id_contrato in ids_facturados:
                omitidos += 1
                continue
            
            canon = contrato["CANON_ARRENDAMIENTO"]
            if not canon or canon <= 0:
                continue
            
            recaudo = Recaudo(
                id_contrato_a=id_contrato,
                fecha_pago=hoy,
                valor_total=canon,
                metodo_pago=MetodoPago.EFECTIVO,
                estado=EstadoRecaudo.PENDIENTE,
                observaciones=f"Generación masiva - {periodo}",
                audit=AuditInfo(created_by=usuario)
            )
            
            concepto = RecaudoConcepto(
                tipo_concepto=TipoConcepto.CANON,
                periodo=periodo,
                valor=canon
            )
            
            items.append((recaudo, [concepto]))
        
        generados = self._repo.crear_masivo(items)
        
        return ResultadoGeneracionMasiva(
            generados=generados,
            omitidos_por_duplicidad=omitidos,
            periodo=periodo
        )
    
    def listar(self, filtros: FiltrosRecaudo) -> PaginatedResult[Recaudo]:
        """Lista recaudos con filtros y paginación."""
        return self._repo.listar_paginado(filtros)
    
    def obtener_detalle(self, id_recaudo: int) -> Optional[RecaudoDetalleDTO]:
        """Obtiene el detalle completo de un recaudo."""
        recaudo = self._repo.obtener_por_id(id_recaudo)
        if not recaudo:
            return None
        
        conceptos = self._repo.obtener_conceptos(id_recaudo)
        
        return RecaudoDetalleDTO(
            id_recaudo=recaudo.id_recaudo,
            id_contrato=recaudo.id_contrato_a,
            # ... campos adicionales de joined query
            conceptos=[{"tipo": c.tipo_concepto.value, "periodo": c.periodo, "valor": c.valor} for c in conceptos]
        )
```

---

## 📦 FASE 4: STATE REFLEX
### Prioridad: ALTA | Esfuerzo: 4h

### 4.1 Refactorizar State

**Archivo:** `src/presentacion_reflex/state/recaudos_state.py` (REFACTORIZAR)

```python
"""
Estado de Presentación para Gestión de Recaudos.
Delegación completa a Servicio de Aplicación.
"""
from datetime import datetime, date
from typing import Any, Dict, List, Optional
import reflex as rx
from src.dominio.constantes.recaudo import MetodoPago, EstadoRecaudo
from src.dominio.interfaces.repositorio_recaudo import FiltrosRecaudo
from src.aplicacion.esquemas.recaudo import (
    ComandoRegistrarPago,
    RecaudoDTO,
    ResultadoOperacion
)
from src.aplicacion.servicios.servicio_recaudo import ServicioRecaudo
from src.infraestructura.persistencia.database import db_manager
from src.infraestructura.persistencia.repositorio_recaudo import RepositorioRecaudo
from src.presentacion_reflex.state.documentos_mixin import DocumentosStateMixin
from src.presentacion_reflex.utils.formatters import format_currency

def _crear_servicio() -> ServicioRecaudo:
    repo = RepositorioRecaudo(db_manager)
    return ServicioRecaudo(repo)

class RecaudosState(DocumentosStateMixin):
    """
    Estado centralizado para gestión de recaudos.
    Toda la lógica de negocio se delega al Servicio de Aplicación.
    """
    
    # Paginación
    current_page: int = 1
    page_size: int = 25
    total_items: int = 0
    
    # Datos
    resultados: List[Dict[str, Any]] = []
    recaudo_actual: Optional[Dict[str, Any]] = None
    is_loading: bool = False
    error_message: str = ""
    
    # Filtros
    search_text: str = ""
    filter_estado: str = "Todos"
    filter_fecha_desde: str = ""
    filter_fecha_hasta: str = ""
    
    # Opciones
    estado_options: List[str] = ["Todos"] + EstadoRecaudo.valores()
    contratos_options: List[Dict[str, Any]] = []
    
    # Combobox
    contrato_search: str = ""
    contrato_menu_open: bool = False
    contrato_selected_label: str = ""
    
    # Modales
    show_form_modal: bool = False
    show_detail_modal: bool = False
    is_editing: bool = False
    form_data: Dict[str, Any] = {}
    
    # Servicio (inyectado)
    _servicio: ServicioRecaudo = rx.MagicVar(default_factory=_crear_servicio)
    
    # ==================== CICLO DE VIDA ====================
    
    @rx.event(background=True)
    async def on_load(self):
        async with self:
            self.is_loading = True
        
        try:
            yield RecaudosState.load_filter_options
            yield RecaudosState.load_data
        finally:
            async with self:
                self.is_loading = False
    
    @rx.event(background=True)
    async def load_filter_options(self):
        query = """
        SELECT 
            ca.ID_CONTRATO_A,
            p.DIRECCION_PROPIEDAD,
            per.NOMBRE_COMPLETO,
            ca.CANON_ARRENDAMIENTO
        FROM CONTRATOS_ARRENDAMIENTOS ca
        INNER JOIN PROPIEDADES p ON ca.ID_PROPIEDAD = p.ID_PROPIEDAD
        INNER JOIN ARRENDATARIOS arr ON ca.ID_ARRENDATARIO = arr.ID_ARRENDATARIO
        INNER JOIN PERSONAS per ON arr.ID_PERSONA = per.ID_PERSONA
        WHERE ca.ESTADO_CONTRATO_A = 'Activo'
        ORDER BY p.DIRECCION_PROPIEDAD
        """
        
        with db_manager.obtener_conexion() as conn:
            cursor = db_manager.get_dict_cursor(conn)
            cursor.execute(query)
            rows = cursor.fetchall()
        
        contratos = [
            {
                "id": str(row["ID_CONTRATO_A"]),
                "texto": f"ID:{row['ID_CONTRATO_A']} - {row['DIRECCION_PROPIEDAD']} ({row['NOMBRE_COMPLETO']})",
                "canon": row["CANON_ARRENDAMIENTO"],
            }
            for row in rows
        ]
        
        async with self:
            self.contratos_options = contratos
    
    @rx.event(background=True)
    async def load_data(self):
        """Carga datos usando el servicio de aplicación."""
        async with self:
            self.is_loading = True
            self.error_message = ""
        
        try:
            filtros = FiltrosRecaudo(
                estado=self._parse_estado(self.filter_estado),
                fecha_desde=self.filter_fecha_desde or None,
                fecha_hasta=self.filter_fecha_hasta or None,
                busqueda=self.search_text or None,
                page=self.current_page,
                page_size=self.page_size
            )
            
            resultado = self._servicio.listar(filtros)
            
            async with self:
                self.resultados = [
                    self._to_dict(item) for item in resultado.items
                ]
                self.total_items = resultado.total
                self.is_loading = False
                
        except Exception as e:
            async with self:
                self.error_message = str(e)
                self.is_loading = False
    
    # ==================== HELPERS ====================
    
    def _parse_estado(self, estado: str) -> Optional[EstadoRecaudo]:
        if estado == "Todos":
            return None
        return EstadoRecaudo(estado)
    
    def _to_dict(self, recaudo) -> Dict[str, Any]:
        return {
            "id_recaudo": recaudo.id_recaudo,
            "valor_total_view": format_currency(recaudo.valor_total),
            # ... campos adicionales
        }
    
    def _get_usuario_actual(self) -> str:
        """Obtiene el usuario actual del contexto de autenticación."""
        # TODO: Integrar con AuthState
        return "admin"
    
    # ==================== ACCIONES CRUD ====================
    
    @rx.event
    def open_create_modal(self):
        self.is_editing = False
        self.show_form_modal = True
        self.form_data = {
            "fecha_pago": date.today().isoformat(),
            "metodo_pago": MetodoPago.TRANSFERENCIA.value,
            "tipo_concepto": "Canon",
            "periodo": date.today().strftime("%Y-%m"),
        }
        self.contrato_search = ""
        self.contrato_selected_label = ""
        self.error_message = ""
    
    @rx.event(background=True)
    async def open_edit_modal(self, id_recaudo: int):
        recaudo = self._servicio._repo.obtener_por_id(id_recaudo)
        if not recaudo:
            async with self:
                self.error_message = "Recaudo no encontrado"
            return
        
        if not recaudo.estado.puede_editarse():
            async with self:
                self.error_message = "Solo se pueden editar pagos en estado Pendiente"
            return
        
        async with self:
            self.is_editing = True
            self.show_form_modal = True
            self.form_data = {
                "id_recaudo": id_recaudo,
                "valor_total": recaudo.valor_total,
                "metodo_pago": recaudo.metodo_pago.value,
                # ... campos adicionales
            }
    
    @rx.event(background=True)
    async def save(self, form_data: Dict):
        async with self:
            self.is_loading = True
            self.error_message = ""
        
        try:
            comando = ComandoRegistrarPago(**form_data)
            self._servicio.registrar_pago(comando, self._get_usuario_actual())
            
            async with self:
                self.show_form_modal = False
                self.form_data = {}
            
            yield rx.toast.success("Recaudo guardado exitosamente")
            yield RecaudosState.load_data
            
        except ValueError as e:
            async with self:
                self.error_message = str(e)
        finally:
            async with self:
                self.is_loading = False
    
    # ==================== ACCIONES DE ESTADO ====================
    
    @rx.event(background=True)
    async def aplicar_pago(self, id_recaudo: int):
        async with self:
            self.is_loading = True
        
        try:
            resultado = self._servicio.aplicar_pago(id_recaudo, self._get_usuario_actual())
            
            if resultado.exito:
                yield rx.toast.success(resultado.mensaje)
            else:
                yield rx.toast.error(resultado.mensaje)
            
            yield RecaudosState.load_data
            
        finally:
            async with self:
                self.is_loading = False
    
    @rx.event(background=True)
    async def reversar_pago(self, id_recaudo: int):
        async with self:
            self.is_loading = True
        
        try:
            resultado = self._servicio.reversar_pago(id_recaudo, self._get_usuario_actual())
            
            if resultado.exito:
                yield rx.toast.warning(resultado.mensaje)
            else:
                yield rx.toast.error(resultado.mensaje)
            
            yield RecaudosState.load_data
            
        finally:
            async with self:
                self.is_loading = False
    
    # ==================== GENERACIÓN MASIVA ====================
    
    @rx.event(background=True)
    async def generar_masivo(self):
        async with self:
            self.is_loading = True
            self.error_message = ""
        
        try:
            periodo = date.today().strftime("%Y-%m")
            resultado = self._servicio.generar_masivo(
                periodo, 
                self._get_usuario_actual(),
                db_manager
            )
            
            msg = f"Se generaron {resultado.generados} recaudos."
            if resultado.omitidos_por_duplicidad > 0:
                msg += f" {resultado.omitidos_por_duplicidad} omitidos por duplicidad."
            
            yield rx.toast.success(msg)
            yield RecaudosState.load_data
            
        except Exception as e:
            async with self:
                self.error_message = str(e)
        finally:
            async with self:
                self.is_loading = False
```

---

## 📦 FASE 5: TESTS
### Prioridad: MEDIA | Esfuerzo: 6h

### 5.1 Estructura de Tests

```
tests/
├── dominio/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_recaudo.py
│   ├── test_recaudo_concepto.py
│   └── test_constantes_recaudo.py
├── aplicacion/
│   ├── __init__.py
│   ├── conftest.py
│   └── test_servicio_recaudo.py
└── integracion/
    ├── __init__.py
    └── test_repositorio_recaudo.py
```

### 5.2 Tests de Dominio

**Archivo:** `tests/dominio/test_recaudo.py`

```python
"""
Tests unitarios para la entidad Recaudo.
"""
import pytest
from datetime import date
from src.dominio.entidades.recaudo import Recaudo
from src.dominio.constantes.recaudo import MetodoPago, EstadoRecaudo

class TestRecaudo:
    """Suite de tests para la entidad Recaudo."""
    
    def test_crear_recaudo_valido(self):
        """Test: Crear recaudo con datos válidos."""
        recaudo = Recaudo(
            id_contrato_a=1,
            fecha_pago=date.today(),
            valor_total=1500000,
            metodo_pago=MetodoPago.EFECTIVO
        )
        
        assert recaudo.valor_total == 1500000
        assert recaudo.metodo_pago == MetodoPago.EFECTIVO
        assert recaudo.estado == EstadoRecaudo.PENDIENTE
    
    def test_rechazar_valor_cero(self):
        """Test: Recaudo con valor cero debe fallar."""
        with pytest.raises(ValueError, match="mayor a cero"):
            Recaudo(
                id_contrato_a=1,
                valor_total=0
            )
    
    def test_rechazar_valor_negativo(self):
        """Test: Recaudo con valor negativo debe fallar."""
        with pytest.raises(ValueError, match="mayor a cero"):
            Recaudo(
                id_contrato_a=1,
                valor_total=-100
            )
    
    def test_referencia_obligatoria_para_electronico(self):
        """Test: Transferencia sin referencia debe fallar."""
        with pytest.raises(ValueError, match="referencia bancaria"):
            Recaudo(
                id_contrato_a=1,
                valor_total=1000000,
                metodo_pago=MetodoPago.TRANSFERENCIA
            )
    
    def test_efectivo_sin_referencia_valido(self):
        """Test: Efectivo sin referencia es válido."""
        recaudo = Recaudo(
            id_contrato_a=1,
            valor_total=1000000,
            metodo_pago=MetodoPago.EFECTIVO
        )
        assert recaudo.metodo_pago == MetodoPago.EFECTIVO
    
    def test_cambiar_estado_valido(self):
        """Test: Cambio de Pendiente a Aplicado válido."""
        recaudo = Recaudo(
            id_contrato_a=1,
            valor_total=1000000,
            metodo_pago=MetodoPago.EFECTIVO
        )
        
        aplicados = recaudo.cambiar_estado(EstadoRecaudo.APLICADO, "admin")
        assert aplicados.estado == EstadoRecaudo.APLICADO
        assert aplicados.audit.updated_by == "admin"
    
    def test_inmutabilidad(self):
        """Test: La entidad es inmutable."""
        original = Recaudo(
            id_contrato_a=1,
            valor_total=1000000
        )
        modificado = original.cambiar_estado(EstadoRecaudo.APLICADO, "admin")
        
        assert original.estado == EstadoRecaudo.PENDIENTE
        assert modificado.estado == EstadoRecaudo.APLICADO
        assert original is not modificado
```

### 5.3 Tests de Aplicación

**Archivo:** `tests/aplicacion/test_servicio_recaudo.py`

```python
"""
Tests para el Servicio de Aplicación de Recaudos.
"""
import pytest
from unittest.mock import Mock
from datetime import date
from src.dominio.constantes.recaudo import MetodoPago, EstadoRecaudo
from src.dominio.entidades.recaudo import Recaudo
from src.aplicacion.esquemas.recaudo import ComandoRegistrarPago
from src.aplicacion.servicios.servicio_recaudo import ServicioRecaudo

class TestServicioRecaudo:
    """Suite de tests para ServicioRecaudo."""
    
    @pytest.fixture
    def mock_repo(self):
        return Mock()
    
    @pytest.fixture
    def servicio(self, mock_repo):
        return ServicioRecaudo(mock_repo)
    
    def test_registrar_pago_exitoso(self, servicio, mock_repo):
        """Test: Registrar pago con datos válidos."""
        mock_repo.crear.return_value = Recaudo(
            id_recaudo=1,
            id_contrato_a=1,
            valor_total=1500000
        )
        
        comando = ComandoRegistrarPago(
            id_contrato_a=1,
            fecha_pago=date.today(),
            valor_total=1500000,
            metodo_pago=MetodoPago.EFECTIVO,
            tipo_concepto="Canon",
            periodo="2026-04"
        )
        
        resultado = servicio.registrar_pago(comando, "admin")
        
        assert resultado.id_recaudo == 1
        mock_repo.crear.assert_called_once()
    
    def test_aplicar_pago_no_encontrado(self, servicio, mock_repo):
        """Test: Aplicar pago inexistente."""
        mock_repo.obtener_por_id.return_value = None
        
        resultado = servicio.aplicar_pago(999, "admin")
        
        assert not resultado.exito
        assert "no encontrado" in resultado.mensaje
    
    def test_aplicar_pago_ya_aplicado(self, servicio, mock_repo):
        """Test: Aplicar pago que ya está aplicado."""
        mock_repo.obtener_por_id.return_value = Recaudo(
            id_recaudo=1,
            id_contrato_a=1,
            valor_total=1000000,
            estado=EstadoRecaudo.APLICADO
        )
        
        resultado = servicio.aplicar_pago(1, "admin")
        
        assert not resultado.exito
        assert "Pendiente" in resultado.mensaje
```

---

## 📦 FASE 6: LIMPIEZA LEGACY
### Prioridad: BAJA | Esfuerzo: 2h

### 6.1 Archivos a Eliminar

```bash
# Legacy Flet (OBSOLETOS)
rm src/presentacion/views/recaudo_form_view.py
rm src/presentacion/views/recaudos_list_view.py

# Scripts de diagnóstico (una vez validados)
rm scripts/debug/debug_recaudos_status.py
rm scripts/debug/debug_recaudos_check.py
rm scripts/verify_recaudos_combo.py
rm scripts/add_recaudos_permissions.py
rm scripts/check_syntax_recaudos.py
rm scripts/diagnostico/repositorio_recaudo_sqlite.py.bak

# PDFs de test
rm tests/test_manual_docs/recaudo_1_*.pdf
```

### 6.2 Actualizar Imports

Verificar que no haya referencias a los archivos eliminados en:
- `src/presentacion_reflex/pages/recaudos.py`
- `src/presentacion_reflex/state/recaudos_state.py`
- `src/presentacion_reflex/components/recaudos/__init__.py`

---

## 📊 CRONOGRAMA DE IMPLEMENTACIÓN

```
SEMANA 1
├── Lunes (2h)    │ F1.1: Crear constantes/enums
├── Martes (3h)   │ F1.2: Value Objects (Periodo, AuditInfo)
├── Miércoles (2h)│ F1.3: Refactorizar Entidad Recaudo
├── Jueves (2h)   │ F2.1: Expandir Interface Repositorio
├── Viernes (1h) │ F2.2: Crear DTOs Pydantic
│                 │
│                 │ ENTREGA: Dominio 100% tipado
└─────────────────┴────────────────────────────────

SEMANA 2
├── Lunes (3h)    │ F3: Refactorizar Servicio
├── Martes (4h)   │ F4: State Reflex (delegación)
├── Miércoles (2h)│ F4: Components (modal_form, detail)
├── Jueves (3h)   │ F5.1: Tests Dominio
└── Viernes (3h)  │ F5.2: Tests Aplicación
                  │
                  │ ENTREGA: Código refactorizado
────────────────────────────────────────────────────

SEMANA 3
├── Lunes (4h)    │ F5.3: Tests Integración
├── Martes (2h)   │ F6.1: Limpieza archivos legacy
├── Miércoles (2h)│ F6.2: Actualizar imports
├── Jueves (4h)   │ VALIDACIÓN INTEGRAL
└── Viernes (4h)  │ • check_syntax.py
                  │ • pytest -v
                  │ • reflex run --debug
                  │
                  │ ENTREGA FINAL ✓
────────────────────────────────────────────────────
```

---

## ✅ CHECKLIST DE CALIDAD

### Fase 1: Value Objects
- [ ] `MetodoPago` enum creado
- [ ] `EstadoRecaudo` enum creado  
- [ ] `TipoConcepto` enum creado
- [ ] `Periodo` value object con validación
- [ ] `AuditInfo` value object inmutable
- [ ] `Recaudo` entidad refactorizada con tipos

### Fase 2: Interfaces
- [ ] `IRepositorioRecaudo` expandido
- [ ] `FiltrosRecaudo` DTO creado
- [ ] `PaginatedResult` protocolo definido
- [ ] DTOs de aplicación creados

### Fase 3: Servicio
- [ ] `registrar_pago()` implementado
- [ ] `aplicar_pago()` implementado
- [ ] `reversar_pago()` implementado
- [ ] `generar_masivo()` refactorizado
- [ ] `listar()` con filtros
- [ ] `obtener_detalle()` implementado

### Fase 4: State
- [ ] Queries SQL eliminados del state
- [ ] Delegación total al servicio
- [ ] Usuario actual de AuthState
- [ ] Error handling centralizado

### Fase 5: Tests
- [ ] Tests entidad Recaudo (10+ casos)
- [ ] Tests entidad RecaudoConcepto
- [ ] Tests servicio (mock repo)
- [ ] Tests integración (con DB)

### Fase 6: Limpieza
- [ ] Views Flet eliminadas
- [ ] Scripts diagnóstico eliminados
- [ ] Imports actualizados
- [ ] Documentación actualizada

---

## 🎯 MÉTRICAS DE ÉXITO

| Métrica | Antes | Después | Objetivo |
|---------|-------|---------|----------|
| Type Hints | Parcial | 100% | 100% |
| Magic Strings | 15+ | 0 | 0 |
| Líneas por método (avg) | 45 | <20 | <20 |
| Cobertura tests | 0% | >80% | >80% |
| Violaciones Clean Arch | 8 | 0 | 0 |

---

## 🔗 DEPENDENCIAS

```python
# Requeridos
reflex>=0.7.0
pydantic>=2.0.0
pytest>=8.0.0
pytest-mock>=3.12.0

# Opcionales (para tests)
pytest-cov>=4.0.0
httpx>=0.27.0  # Para tests async
```

---

## 📝 NOTAS

1. **AuthState Integration**: El campo `usuario_actual` debe obtenerse de `AuthState` en lugar de hardcode "admin"

2. **Migración Gradual**: Si el sistema está en producción, implementar por fases:
   - Fase 1-2: Sin impacto (solo tipado)
   - Fase 3: Nuevos métodos, mantener旧的
   - Fase 4: State con feature flag
   - Fase 5-6: Cleanup

3. **Base de Datos**: El repositorio existente es compatible, solo requiere agregar los nuevos métodos de la interface

4. **Backwards Compatibility**: Mantener los métodos existentes del state hasta que los nuevos estén validados

---

**Documento creado:** 2026-04-03  
**Autor:** Sistema Velar - Claude AI  
**Versión:** 1.0.0  
**Estado:** LISTO PARA IMPLEMENTACIÓN
