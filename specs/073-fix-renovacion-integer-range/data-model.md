# Data Model: Fix `integer out of range` en renovación

**Feature**: `073-fix-renovacion-integer-range` | **Fecha**: 2026-09-14

**Sin cambios de esquema** (aclaración Q1: sin migración de columnas ni
backfill). Este documento fija entidades, rangos y reglas de validación que la
implementación debe respetar.

## Entidades involucradas (solo lectura/escritura, sin DDL)

### RENOVACIONES_CONTRATOS (escritura: historial)

| Campo | Tipo | Regla |
|---|---|---|
| id_contrato_a / id_contrato_m | integer | Uno informado según tipo |
| tipo_contrato | text | 'Arrendamiento' \| 'Mandato' |
| fecha_inicio_original, fecha_fin_original, fecha_inicio_renovacion, fecha_fin_renovacion, fecha_renovacion | text ISO-8601 | Formato `YYYY-MM-DD` (renovación) |
| canon_anterior, canon_nuevo | integer | 0 < valor ≤ 2.147.483.647; encadenamiento en consecutivas: anterior(n) = nuevo(n-1) |
| porcentaje_incremento | integer | `int(pct_ipc * 100)`; 0 si duración < 12 o sin IPC |
| motivo_renovacion | text | Incluye `% IPC` cuando aplica |

### CONTRATOS_ARRENDAMIENTOS (escritura: contrato renovado)

| Campo | Tipo | Regla |
|---|---|---|
| canon_arrendamiento | integer | Rango soportado: ≤ $10.000.000 (sobre-máximos → rechazo FR-003) |
| duracion_contrato_a | integer | ≥ 12 ⇒ aplica IPC |
| fecha_fin_contrato_a | text | Se extiende a nueva fecha fin |
| estado_contrato_a | text | Debe ser ACTIVO para renovar; la renovación no lo cambia |
| fecha_renovacion_contrato_a | text | Fecha de la renovación (propagación usa su mes) |

### LIQUIDACIONES (escritura: propagación futura)

| Campo | Tipo | Regla |
|---|---|---|
| canon_bruto, total_ingresos, total_egresos, neto_a_pagar | integer | Recalculados con canon nuevo |
| comision_porcentaje | integer | Escala base 10000 (1000 = 10%); rango soportado ≤ 1500 |
| comision_monto, iva_comision | integer | **Derivados**: `trunc(canon × comision / 10000)` e `iva = trunc(comision × 0.19)` si `iva_comision > 0`; el producto intermedio NO debe evaluarse en int4 (R2) |
| fecha_generacion | text | Solo filas con mes ≥ mes de renovación |

### RECAUDOS / RECAUDO_CONCEPTOS (escritura: propagación futura)

| Campo | Tipo | Regla |
|---|---|---|
| recaudos.valor_total, recaudo_conceptos.valor | integer | Concepto 'Canon' = canon nuevo; total = suma de conceptos; solo mes ≥ mes de renovación |

### CONTRATOS_MANDATOS / PROPIEDADES (escritura: sincronización)

| Campo | Tipo | Regla |
|---|---|---|
| contratos_mandatos.canon_mandato, fecha_fin_contrato_m | integer / text | = canon nuevo / nueva fecha fin (mandato activo de la misma propiedad) |
| propiedades.canon_arrendamiento_estimado | integer | = canon nuevo |

### AUDITORIA_PROPAGACION_CANON (escritura: trazabilidad)

| Campo | Tipo | Regla |
|---|---|---|
| canon_anterior, canon_nuevo | numeric | Solo cambios reales (una fila por registro modificado) |

## Validaciones previas a persistir (FR-003)

Gate en dos niveles, en este orden:

1. **Máximos operativos**: canon ≤ $10.000.000, comisión ≤ 1500. Por encima →
   excepción de dominio con **campo + valor** (mensaje operativo no técnico).
2. **Red de seguridad int4**: para todo valor derivado `v` con destino entero,
   si `v > 2.147.483.647` → excepción de dominio con **campo + valor**.

## Transiciones de estado

- Contrato: `ACTIVO --renovar--> ACTIVO` (vigencia extendida, canon nuevo).
  No-ACTIVO ⇒ `ContratoNoRenovableError` (sin cambios).
- Renovación: transacción atómica total o rollback (FR-004); reintento y
  concurrencia idempotentes: un único registro (FR-005).
