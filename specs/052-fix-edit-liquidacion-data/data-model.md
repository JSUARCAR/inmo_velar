# Data Model: Corrección de Carga de Datos en Edición de Liquidaciones

**Date**: 2026-07-13
**Feature**: 052-fix-edit-liquidacion-data

## Entities

### LiquidacionAsesor

**Table**: `LIQUIDACIONES_ASESORES`

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| ID_LIQUIDACION_ASESOR | INTEGER (PK, SERIAL) | NO | Identificador único |
| ID_CONTRATO_A | INTEGER (FK) | YES | NULL para liquidaciones multi-contrato |
| ID_ASESOR | INTEGER (FK) | NO | Referencia al asesor |
| PERIODO_LIQUIDACION | TEXT | NO | Formato YYYY-MM |
| CANON_ARRENDAMIENTO_LIQUIDADO | BIGINT | NO | Suma de canones de todos los contratos |
| PORCENTAJE_COMISION | INTEGER | NO | Escala 0-10000 (0.00% - 100.00%) |
| COMISION_BRUTA | BIGINT | NO | Calculada: CANON * PORCENTAJE / 10000 |
| TOTAL_DESCUENTOS | BIGINT | NO | Suma de descuentos |
| TOTAL_BONIFICACIONES | BIGINT | NO | Suma de bonificaciones |
| VALOR_NETO_ASESOR | BIGINT | NO | COMISION_BRUTA + BONIFICACIONES - DESCUENTOS |
| ESTADO_LIQUIDACION | TEXT | NO | Pendiente / Aprobada / Pagada / Anulada |
| MODO_COMISION | TEXT | NO | ASESOR / CONTRATO_MANDATO |
| FECHA_CREACION | TEXT | YES | Timestamp de creación |
| FECHA_APROBACION | TEXT | YES | Timestamp de aprobación |
| USUARIO_CREADOR | TEXT | YES | Usuario que creó |
| USUARIO_APROBADOR | TEXT | YES | Usuario que aprobó |
| OBSERVACIONES_LIQUIDACION | TEXT | YES | Notas |
| MOTIVO_ANULACION | TEXT | YES | Motivo si fue anulada |
| ELIMINADA | BOOLEAN | NO | Soft delete flag |
| CREATED_AT | TEXT | NO | Audit timestamp |
| CREATED_BY | TEXT | YES | Audit user |
| UPDATED_AT | TEXT | YES | Audit timestamp |
| UPDATED_BY | TEXT | YES | Audit user |

**Unique Constraint**: `(ID_CONTRATO_A, PERIODO_LIQUIDACION)` — only when ID_CONTRATO_A is NOT NULL

**Validation Rules**:
- PORCENTAJE_COMISION: 0-10000
- COMISION_BRUTA: >= 0
- TOTAL_DESCUENTOS: >= 0
- ESTADO_LIQUIDACION: IN ('Pendiente', 'Aprobada', 'Pagada', 'Anulada')

### LiquidacionContrato (LIQUIDACIONES_CONTRATOS)

**Table**: `LIQUIDACIONES_CONTRATOS`

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| ID_LIQUIDACION_ASESOR | INTEGER (FK) | NO | Referencia a liquidación |
| ID_CONTRATO_A | INTEGER (FK) | NO | Referencia a contrato de arrendamiento |
| CANON_INCLUIDO | BIGINT | NO | Canon del contrato al momento de liquidación |
| COMISION_PORCENTAJE_CONTRATO | INTEGER | NO | % de comisión del contrato (escala 0-10000) |
| COMISION_MONTO_CONTRATO | BIGINT | NO | Monto de comisión calculado |
| CREATED_BY | TEXT | YES | Audit user |

**Relationships**:
- FK → LIQUIDACIONES_ASESORES (ID_LIQUIDACION_ASESOR)
- FK → CONTRATOS_ARRENDAMIENTOS (ID_CONTRATO_A)

**CRITICAL**: This table stores the "Propiedades a Liquidar" shown in the edit modal. If records are missing here, the edit modal shows fewer properties.

### DescuentoAsesor (DESCUENTOS_ASESORES)

**Table**: `DESCUENTOS_ASESORES`

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| ID_DESCUENTO_ASESOR | INTEGER (PK, SERIAL) | NO | Identificador único |
| ID_LIQUIDACION_ASESOR | INTEGER (FK) | NO | Referencia a liquidación |
| TIPO_DESCUENTO | TEXT | NO | Préstamo / Anticipo / Sanción / Ajuste / Otros |
| DESCRIPCION_DESCUENTO | TEXT | NO | Descripción del descuento |
| VALOR_DESCUENTO | INTEGER | NO | Monto del descuento (>= 0) |
| CREATED_AT | TEXT | NO | Audit timestamp |
| CREATED_BY | TEXT | YES | Audit user |
| UPDATED_AT | TEXT | YES | Audit timestamp |
| UPDATED_BY | TEXT | YES | Audit user |

**Relationships**:
- FK → LIQUIDACIONES_ASESORES (ID_LIQUIDACION_ASESOR) ON DELETE CASCADE

**CRITICAL**: This table stores the "Descuentos Guardados" shown in the edit modal. If records are missing here, the edit modal shows fewer discounts.

### BonificacionAsesor (BONIFICACIONES_ASESORES)

**Table**: `BONIFICACIONES_ASESORES`

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| ID_BONIFICACION_ASESOR | INTEGER (PK, SERIAL) | NO | Identificador único |
| ID_LIQUIDACION_ASESOR | INTEGER (FK) | NO | Referencia a liquidación |
| TIPO_BONIFICACION | TEXT | NO | Tipo de bonificación |
| DESCRIPCION_BONIFICACION | TEXT | NO | Descripción |
| VALOR_BONIFICACION | INTEGER | NO | Monto (>= 0) |
| FECHA_REGISTRO | TEXT | YES | Fecha de registro |
| CREATED_AT | TEXT | NO | Audit timestamp |
| CREATED_BY | TEXT | YES | Audit user |

## Relationships Diagram

```
┌─────────────────────┐
│  LIQUIDACIONES_     │
│  ASESORES           │
│  (PK: ID_LIQUIDACION│
│   _ASESOR)          │
└─────────┬───────────┘
          │
          ├──< LIQUIDACIONES_CONTRATOS (Propiedades a Liquidar)
          │    ├── FK → CONTRATOS_ARRENDAMIENTOS
          │    └── Datos: CANON_INCLUIDO, COMISION_PORCENTAJE, COMISION_MONTO
          │
          ├──< DESCUENTOS_ASESORES (Descuentos Guardados)
          │    └── Datos: TIPO, DESCRIPCION, VALOR
          │
          ├──< BONIFICACIONES_ASESORES (Bonificaciones)
          │    └── Datos: TIPO, DESCRIPCION, VALOR
          │
          └──< PAGOS_ASESORES (Pagos)
               └── Datos: FECHA, METODO, VALOR, ESTADO
```

## State Transitions

```
                    ┌──────────┐
                    │ Pendiente│
                    └────┬─────┘
                         │ aprobar()
                         ▼
                    ┌──────────┐
                    │ Aprobada │
                    └────┬─────┘
                         │ marcar_como_pagada()
                         ▼
                    ┌──────────┐
                    │  Pagada  │
                    └──────────┘

                    ┌──────────┐
    Pendiente ────> │ Anulada  │ (anular())
                    └──────────┘

                    ┌──────────┐
    Aprobada ─────> │ Pendiente│ (reversar())
                    └──────────┘

                    ┌──────────┐
    Pagada ───────> │ Aprobada │ (reversar_pago())
                    └──────────┘
```

**Edit Constraint**: Only liquidations in "Pendiente" state can be edited (`puede_editarse` property).

## Migration Considerations

For affected liquidaciones (e.g., 2026-07), the migration script must:

1. Identify liquidaciones where `LIQUIDACIONES_CONTRATOS` has 0 records but the liquidation exists
2. Reconstruct `LIQUIDACIONES_CONTRATOS` records from contract data at generation time
3. Identify liquidaciones where `DESCUENTOS_ASESORES` has 0 records but `TOTAL_DESCUENTOS > 0`
4. Reconstruct discount records (seguro + 4x1000) from canon and contract data
5. Verify referential integrity after reconstruction
