# Data Model: Auditoría de Propagación de Renovaciones

**Feature**: 062-audit-renewal-propagation
**Date**: 2026-07-22
**Status**: Complete

## Overview

This document defines the data structures used by the audit script. These are Python dataclasses/dicts, not database entities.

## Core Entities

### 1. RenovacionJulio2026

Represents a contract renovation from July 2026.

```python
@dataclass
class RenovacionJulio2026:
    """Renovación de contrato de arrendamiento en julio 2026."""
    contrato_id: str
    contrato_codigo: str
    arrendatario_nombre: str
    mandato_id: Optional[str]
    propiedad_id: Optional[str]
    canon_anterior: Decimal
    canon_nuevo: Decimal
    fecha_renovacion: datetime
    fecha_inicio_renovacion: Optional[datetime]
    estado: str  # "ACTIVA", "INACTIVA"
```

**Validation Rules**:
- `canon_nuevo` must be > 0
- `fecha_renovacion` must be between 2026-07-01 and 2026-07-31
- `contrato_id` must not be null

**Relationships**:
- Has one `ContratoMandato` (optional)
- Has one `Propiedad` (optional)
- Has many `Liquidacion` (future periods)
- Has many `Recaudo` (future periods)

### 2. InconsistenciaCanon

Represents a canon discrepancy found during audit.

```python
@dataclass
class InconsistenciaCanon:
    """Inconsistencia en el canon de arrendamiento."""
    contrato_id: str
    contrato_codigo: str
    tipo: str  # "LIQUIDACION", "RECAUDO", "MANDATO", "PROPIEDAD"
    entidad_afectada: str
    entidad_id: str
    canon_esperado: Decimal
    canon_encontrado: Decimal
    diferencia: Decimal
    fecha_registro: datetime
    periodo: str  # "2026-07", "2026-08", etc.
    causa_raiz: str
    severidad: str  # "CRITICA", "ALTA", "MEDIA", "BAJA"
```

**Validation Rules**:
- `diferencia` = `canon_encontrado` - `canon_esperado`
- `severidad` determined by `abs(diferencia)`:
  - CRITICA: > 1,000,000
  - ALTA: > 100,000
  - MEDIA: > 10,000
  - BAJA: <= 10,000

**State Transitions**:
- Created → Analyzed → Reported

### 3. FallaDiseno

Represents a design flaw identified in source code.

```python
@dataclass
class FallaDiseno:
    """Falla de diseño identificada en el código fuente."""
    archivo: str
    linea_inicio: int
    linea_fin: Optional[int]
    funcion_clase: str
    descripcion: str
    problema: str
    impacto: str
    recomendacion: str
    categoria: str  # "SINCRONIZACION", "VALIDACION", "MANEJO_ERRORES"
```

**Validation Rules**:
- `linea_inicio` must be > 0
- `archivo` must exist in project
- `descripcion` must be non-empty

**Relationships**:
- Belongs to one source file
- May relate to multiple `InconsistenciaCanon`

### 4. InformeAuditoria

Complete audit report structure.

```python
@dataclass
class InformeAuditoria:
    """Informe completo de auditoría."""
    metadata: MetadataInforme
    resumen_ejecutivo: ResumenEjecutivo
    inconsistencias: List[InconsistenciaCanon]
    analisis_codigo: List[FallaDiseno]
    recomendaciones: List[Recomendacion]
    contratos_procesados: List[RenovacionJulio2026]
    historial_verificacion: Optional[HistorialVerificacion]
```

### 5. MetadataInforme

Execution metadata.

```python
@dataclass
class MetadataInforme:
    """Metadatos de ejecución del script."""
    fecha_ejecucion: datetime
    duracion_segundos: float
    total_renovaciones: int
    total_inconsistencias: int
    total_fallas_diseno: int
    version_script: str
    entorno: str  # "staging", "produccion"
```

### 6. ResumenEjecutivo

Executive summary with key metrics.

```python
@dataclass
class ResumenEjecutivo:
    """Resumen ejecutivo de la auditoría."""
    total_renovaciones: int
    inconsistencias_encontradas: int
    porcentaje_inconsistencias: float
    estado_sincronizacion: str  # "OK", "INCONSISTENTE", "CRITICO"
    contratos_ok: int
    contratos_inconsistentes: int
    contratos_error: int
    monto_total_discrepancia: Decimal
```

### 7. Recomendacion

Prioritized technical recommendation.

```python
@dataclass
class Recomendacion:
    """Recomendación técnica priorizada."""
    prioridad: int  # 1 = highest
    titulo: str
    descripcion: str
    categoria: str  # "CORRECCION_INMEDIATA", "MEJORA", "PREVENCION"
    esfuerzo_estimado: str  # "BAJO", "MEDIO", "ALTO"
    impacto_estimado: str  # "BAJO", "MEDIO", "ALTO"
    archivos_afectados: List[str]
```

### 8. HistorialVerificacion

Historical preservation check results.

```python
@dataclass
class HistorialVerificacion:
    """Resultado de verificación de preservación histórica."""
    liquidaciones_verificadas: int
    liquidaciones_modificadas: int
    recaudos_verificados: int
    recaudos_modificados: int
    integridad: str  # "PRESERVADA", "COMPROMETIDA"
    detalles: List[DetalleHistorial]
```

### 9. DetalleHistorial

Detail of historical modification detected.

```python
@dataclass
class DetalleHistorial:
    """Detalle de modificación histórica detectada."""
    entidad: str  # "LIQUIDACION", "RECAUDO"
    entidad_id: str
    campo: str
    valor_original: Any
    valor_actual: Any
    fecha_modificacion: Optional[datetime]
    contrato_id: str
```

## Database Schema Reference

### Tables Used (Read-Only)

1. **RENOVACIONES_CONTRATOS**
   - `id`, `contrato_id`, `canon_anterior`, `canon_nuevo`, `fecha_renovacion`

2. **CONTRATOS_ARRENDAMIENTOS**
   - `id`, `codigo`, `canon_arrendamiento`, `arrendatario_id`, `mandato_id`

3. **CONTRATOS_MANDATO**
   - `id`, `canon_mandato`, `propiedad_id`

4. **PROPIEDADES**
   - `id`, `canon_arrendamiento_estimado`

5. **LIQUIDACIONES**
   - `id`, `contrato_id`, `canon_bruto`, `fecha`, `estado`

6. **RECAUDOS**
   - `id`, `contrato_id`, `valor_total`, `fecha`, `estado`

7. **RECAUDO_CONCEPTOS**
   - `id`, `recaudo_id`, `concepto`, `valor`

## Relationships Diagram

```
┌─────────────────────┐
│ RENOVACIONES_       │
│ CONTRATOS           │
└─────────┬───────────┘
          │ contrato_id
          ▼
┌─────────────────────┐
│ CONTRATOS_          │
│ ARRENDAMIENTOS      │
└─────────┬───────────┘
          │ mandato_id
          ▼
┌─────────────────────┐
│ CONTRATOS_MANDATO   │
└─────────┬───────────┘
          │ propiedad_id
          ▼
┌─────────────────────┐
│ PROPIEDADES         │
└─────────────────────┘

┌─────────────────────┐
│ LIQUIDACIONES       │──── contrato_id ────┐
└─────────────────────┘                     │
                                            │
┌─────────────────────┐                     │
│ RECAUDOS            │──── contrato_id ────┤
└─────────┬───────────┘                     │
          │ recaudo_id                      │
          ▼                                 │
┌─────────────────────┐                     │
│ RECAUDO_CONCEPTOS   │                     │
└─────────────────────┘                     │
                                            │
                                            ▼
                                   ┌─────────────────────┐
                                   │ CONTRATOS_          │
                                   │ ARRENDAMIENTOS      │
                                   └─────────────────────┘
```

## Validation Summary

| Entity | Required Fields | Optional Fields | Relationships |
|--------|-----------------|-----------------|---------------|
| RenovacionJulio2026 | 7 | 2 | 4 |
| InconsistenciaCanon | 10 | 0 | 1 |
| FallaDiseno | 8 | 1 | 1 |
| InformeAuditoria | 6 | 1 | 4 |
| MetadataInforme | 7 | 0 | 0 |
| ResumenEjecutivo | 8 | 0 | 0 |
| Recomendacion | 7 | 0 | 1 |
| HistorialVerificacion | 5 | 1 | 1 |
| DetalleHistorial | 6 | 1 | 1 |
