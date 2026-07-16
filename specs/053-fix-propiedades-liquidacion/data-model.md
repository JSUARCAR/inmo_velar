# Data Model: Fix Propiedades a Liquidar

**Date**: 2026-07-13

## Entidades Relevantes (sin cambios de esquema)

### CONTRATOS_ARRENDAMIENTOS (ca)

| Campo | Tipo | Notas |
|-------|------|-------|
| ID_CONTRATO_A | SERIAL PK | Identificador único |
| ID_PROPIEDAD | INTEGER FK → PROPIEDADES | Propiedad asociada |
| ID_ARRENDATARIO | INTEGER FK → ARRENDATARIOS | Arrendatario |
| ESTADO_CONTRATO_A | VARCHAR | 'ACTIVO', 'FINALIZADO', 'CANCELADO', 'LEGAL' |
| CANON_ARRENDAMIENTO | INTEGER | Valor mensual del arrendamiento |

### CONTRATOS_MANDATOS (cm)

| Campo | Tipo | Notas |
|-------|------|-------|
| ID_CONTRATO_M | SERIAL PK | Identificador único |
| ID_PROPIEDAD | INTEGER FK → PROPIEDADES | Propiedad asociada |
| ID_ASESOR | INTEGER FK → ASESORES | Asesor asignado |
| ID_PROPIETARIO | INTEGER FK → PROPIETARIOS | Propietario |
| ESTADO_CONTRATO_M | VARCHAR | 'ACTIVO', 'FINALIZADO', 'CANCELADO', 'LEGAL' |
| COMISION_PORCENTAJE_CONTRATO_M | INTEGER | Porcentaje de comisión (escala 0-10000) |

### RELACIÓN CLAVE: ca.ID_PROPIEDAD = cm.ID_PROPIEDAD

Una propiedad puede tener:
- Múltiples CONTRATOS_ARRENDAMIENTOS (históricos, pero solo 1 activo a la vez)
- Múltiples CONTRATOS_MANDATOS (históricos, pero solo 1 activo a la vez)

El JOIN actual produce un cruce cartesiano si hay múltiples contratos mandato para la misma propiedad.

### LIQUIDACIONES_ASESORES (la)

| Campo | Tipo | Notas |
|-------|------|-------|
| ID_LIQUIDACION_ASESOR | SERIAL PK | Identificador único |
| ID_ASESOR | INTEGER FK → ASESORES | Asesor |
| PERIODO_LIQUIDACION | VARCHAR | 'YYYY-MM' |
| ESTADO_LIQUIDACION | VARCHAR | 'Pendiente', 'Aprobada', 'Pagada', 'Anulada' |
| ELIMINADA | BOOLEAN | Soft delete |
| UNIQUE(ID_ASESOR, PERIODO_LIQUIDACION) | CONSTRAINT | Un liquidación por asesor por período |

### LIQUIDACIONES_CONTRATOS (lc)

| Campo | Tipo | Notas |
|-------|------|-------|
| ID_LIQUIDACION_CONTRATO | SERIAL PK | Identificador único |
| ID_LIQUIDACION_ASESOR | INTEGER FK → LIQUIDACIONES_ASESORES | Liquidación padre |
| ID_CONTRATO_A | INTEGER FK → CONTRATOS_ARRENDAMIENTOS | Contrato incluido |
| CANON_INCLUIDO | INTEGER | Canon al momento de liquidación |
| COMISION_PORCENTAJE_CONTRATO | INTEGER | % comisión al momento de liquidación |
| COMISION_MONTO_CONTRATO | INTEGER | Comisión calculada |

## Consulta Corregida (Propuesta)

La consulta `obtener_activos_por_asesor()` debe garantizar que:
1. Se una con el CONTRATO_MANDATO **activo más reciente** para cada propiedad
2. No produzca duplicados por historial de mandatos
3. Incluya propiedades que cumplan ambas condiciones: ca.ACTIVO + cm.ACTIVO + cm.ID_ASESOR = target

```sql
SELECT DISTINCT ON (ca.ID_CONTRATO_A)
    ca.ID_CONTRATO_A, ca.ID_PROPIEDAD, ca.CANON_ARRENDAMIENTO,
    ca.ESTADO_CONTRATO_A, ca.ID_ARRENDATARIO,
    cm.COMISION_PORCENTAJE_CONTRATO_M, cm.ID_CONTRATO_M,
    p.DIRECCION_PROPIEDAD,
    arr.ID_SEGURO, seg.NOMBRE_SEGURO, seg.PORCENTAJE_SEGURO
FROM CONTRATOS_ARRENDAMIENTOS ca
JOIN PROPIEDADES p ON ca.ID_PROPIEDAD = p.ID_PROPIEDAD
JOIN CONTRATOS_MANDATOS cm ON ca.ID_PROPIEDAD = cm.ID_PROPIEDAD
    AND cm.ESTADO_CONTRATO_M = 'ACTIVO'
    AND cm.ID_ASESOR = %s
LEFT JOIN ARRENDATARIOS arr ON ca.ID_ARRENDATARIO = arr.ID_ARRENDATARIO
LEFT JOIN SEGUROS seg ON arr.ID_SEGURO = seg.ID_SEGURO
WHERE ca.ESTADO_CONTRATO_A = 'ACTIVO'
ORDER BY ca.ID_CONTRATO_A, cm.ID_CONTRATO_M DESC
```

**Cambios clave vs. consulta actual**:
- `DISTINCT ON (ca.ID_CONTRATO_A)` + `ORDER BY` evita duplicados por múltiples mandatos
- Condiciones del JOIN movidas a la cláusula ON (más explícito)
- Se preserva la lógica de filtrado por estado ACTIVO en ambas tablas
