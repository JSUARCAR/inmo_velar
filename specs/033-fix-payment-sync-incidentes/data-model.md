# Data Model: Fix Payment Status Synchronization

**Date**: 2026-07-07
**Feature**: 033-fix-payment-sync-incidentes

## Entities

### INCIDENTE

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| ID_INCIDENTE | SERIAL | PRIMARY KEY | Unique identifier |
| ID_PROPIEDAD | INTEGER | FK → PROPIEDADES | Property reference |
| ID_TIPO_INCIDENTE | INTEGER | FK → TIPO_INCIDENTE | Incident type |
| ESTADO | VARCHAR(20) | NOT NULL | Estado del incidente (Abierto, En Proceso, Cerrado) |
| ESTADO_PAGO | VARCHAR(20) | NOT NULL | Estado de pago (Pendiente, Parcialmente Pagado, Pagado) |
| DESCRIPCION | TEXT | | Descripción del incidente |
| FECHA_REGISTRO | TIMESTAMP | DEFAULT NOW() | Fecha de registro |

**Business Rules**:
- ESTADO_PAGO se actualiza automáticamente cuando cambia el estado de una liquidación asociada
- ESTADO_PAGO depende del estado de las cuotas del plan de pago

### PLAN_PAGO_INCIDENTE

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| ID_PLAN_PAGO | SERIAL | PRIMARY KEY | Unique identifier |
| ID_INCIDENTE | INTEGER | FK → INCIDENTE | Incident reference |
| ESTADO | VARCHAR(20) | NOT NULL | Estado del plan (Activo, Completado, Cancelado) |
| MONTO_TOTAL | DECIMAL(12,2) | NOT NULL | Monto total del plan |
| NUMERO_CUOTAS | INTEGER | NOT NULL | Número de cuotas |
| FECHA_CREACION | TIMESTAMP | DEFAULT NOW() | Fecha de creación |

**Relationships**:
- One PLAN_PAGO_INCIDENTE belongs to one INCIDENTE
- One PLAN_PAGO_INCIDENTE has many CUOTA_INCIDENTE

### CUOTA_INCIDENTE

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| ID_CUOTA | SERIAL | PRIMARY KEY | Unique identifier |
| ID_PLAN_PAGO | INTEGER | FK → PLAN_PAGO_INCIDENTE | Plan reference |
| NUMERO_CUOTA | INTEGER | NOT NULL | Número de cuota |
| MONTO | DECIMAL(12,2) | NOT NULL | Monto de la cuota |
| ESTADO_PAGO | VARCHAR(20) | NOT NULL | Estado de pago (Pendiente, Asociada, Pagada) |
| ID_LIQUIDACION | INTEGER | FK → LIQUIDACIONES | Liquidación asociada (nullable) |
| FECHA_PAGO | DATE | | Fecha de pago (cuando ESTADO_PAGO = 'Pagada') |

**State Transitions**:
```
Pendiente → Asociada (cuando se asocia a una liquidación)
Asociada → Pagada (cuando la liquidación se marca como pagada)
Pagada → Asociada (cuando se revierte el pago de la liquidación)
```

**Business Rules**:
- ESTADO_PAGO se actualiza cuando la liquidación asociada cambia de estado
- ID_LIQUIDACION se establece cuando la cuota se asocia a una liquidación

### LIQUIDACIONES

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| ID_LIQUIDACION | SERIAL | PRIMARY KEY | Unique identifier |
| ID_PROPIEDAD | INTEGER | FK → PROPIEDADES | Property reference |
| PERIODO | VARCHAR(7) | NOT NULL | Período (YYYY-MM) |
| ESTADO_LIQUIDACION | VARCHAR(20) | NOT NULL | Estado (En Proceso, Aprobada, Pagada, Cancelada) |
| MONTO_TOTAL | DECIMAL(12,2) | NOT NULL | Monto total |
| FECHA_PAGO | DATE | | Fecha de pago |
| METODO_PAGO | VARCHAR(50) | | Método de pago |
| REFERENCIA_PAGO | VARCHAR(100) | | Referencia de pago |

**State Transitions**:
```
En Proceso → Aprobada (cuando se aprueba)
Aprobada → Pagada (cuando se registra el pago)
Pagada → En Proceso (cuando se revierte)
```

**Business Rules**:
- Cuando ESTADO_LIQUIDACION cambia a 'Pagada', se deben actualizar las cuotas asociadas
- Cuando ESTADO_LIQUIDACION se revierte, se deben recalcular los estados de pago

### INCIDENTE_LIQUIDACION

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| ID_RELACION | SERIAL | PRIMARY KEY | Unique identifier |
| ID_INCIDENTE | INTEGER | FK → INCIDENTE | Incident reference |
| ID_LIQUIDACION | INTEGER | FK → LIQUIDACIONES | Liquidation reference |
| MONTO_APLICADO | DECIMAL(12,2) | | Monto aplicado |

**Relationships**:
- Junction table linking INCIDENTES to LIQUIDACIONES
- Used to find all incidents associated with a liquidation

## Relationships

```
INCIDENTE (1) ──── (1) PLAN_PAGO_INCIDENTE
PLAN_PAGO_INCIDENTE (1) ──── (N) CUOTA_INCIDENTE
CUOTA_INCIDENTE (N) ──── (1) LIQUIDACIONES [via ID_LIQUIDACION]
INCIDENTE (N) ──── (N) LIQUIDACIONES [via INCIDENTE_LIQUIDACION]
```

## Query Patterns

### Find all cuotas for a liquidation
```sql
SELECT * FROM CUOTA_INCIDENTE 
WHERE ID_LIQUIDACION = %s
```

### Count paid cuotas for a plan
```sql
SELECT 
    COUNT(c.ID_CUOTA) as total_con_liq,
    SUM(CASE WHEN l.ESTADO_LIQUIDACION = 'Pagada' THEN 1 ELSE 0 END) as total_pagadas
FROM CUOTA_INCIDENTE c
JOIN LIQUIDACIONES l ON c.ID_LIQUIDACION = l.ID_LIQUIDACION
WHERE c.ID_PLAN_PAGO = %s
```

### Find incidents associated with a liquidation
```sql
SELECT * FROM INCIDENTE_LIQUIDACION 
WHERE ID_LIQUIDACION = %s
```

## Validation Rules

1. **CUOTA_INCIDENTE.ESTADO_PAGO** must be one of: 'Pendiente', 'Asociada', 'Pagada'
2. **LIQUIDACIONES.ESTADO_LIQUIDACION** must be one of: 'En Proceso', 'Aprobada', 'Pagada', 'Cancelada'
3. **INCIDENTE.ESTADO_PAGO** must be one of: 'Pendiente', 'Parcialmente Pagado', 'Pagado'
4. **CUOTA_INCIDENTE.ID_LIQUIDACION** can be NULL (cuota not yet associated)
5. When **CUOTA_INCIDENTE.ESTADO_PAGO** = 'Pagada', **CUOTA_INCIDENTE.FECHA_PAGO** must be set
