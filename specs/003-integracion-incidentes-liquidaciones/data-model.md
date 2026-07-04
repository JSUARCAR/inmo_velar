# Data Model: Integración Incidentes y Liquidaciones de Propietarios

**Date**: 2026-06-30
**Feature**: 003-integracion-incidentes-liquidaciones

## Entity Relationship Diagram

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   INCIDENTE     │     │ PLAN_PAGO_       │     │ CUOTA_INCIDENTE │
├─────────────────┤     │ INCIDENTE        │     ├─────────────────┤
│ id_incidente PK │◄───┤ id_plan_pago PK  │◄───┤ id_cuota PK     │
│ id_propiedad    │     │ id_incidente FK  │     │ id_plan_pago FK │
│ costo_incidente │     │ num_cuotas       │     │ numero_cuota    │
│ estado_pago     │     │ valor_cuota      │     │ valor_cuota     │
│ ...             │     │ total_plan       │     │ id_liquidacion  │
└────────┬────────┘     │ estado           │     │ estado_pago     │
         │              │ created_at       │     │ ...             │
         │              └──────────────────┘     └─────────────────┘
         │                        │
         │                        │
         ▼                        ▼
┌─────────────────┐     ┌──────────────────┐
│ INCIDENTE_      │     │   LIQUIDACION    │
│ LIQUIDACION     │     ├─────────────────┤
├─────────────────┤     │ id_liquidacion PK│
│ id_relacion PK  │     │ id_contrato_m    │
│ id_incidente FK │     │ periodo          │
│ id_liquidacion  │     │ valor_incidentes │
│ numero_cuota    │     │ neto_a_pagar     │
│ valor_descuento │     │ estado_liquidacion│
│ ...             │     │ ...              │
└─────────────────┘     └─────────────────┘
```

## Entity Definitions

### 1. INCIDENTE (Extendida)

**Tabla**: INCIDENTES
**Motivo de cambio**: Agregar campo `estado_pago` para tracking financiero

| Campo | Tipo | Nullable | Default | Descripción |
|-------|------|----------|---------|-------------|
| ID_INCIDENTE | INTEGER PK | No | AUTO | Identificador único |
| ID_PROPIEDAD | INTEGER FK | No | - | Referencia a propiedad |
| COSTO_INCIDENTE | INTEGER | No | 0 | Costo aprobado de reparación |
| ESTADO | TEXT | No | 'Reportado' | Estado operativo |
| ESTADO_PAGO | TEXT | Sí | 'Pendiente' | Estado financiero: Pendiente/Parcialmente Pagado/Pagado |
| ... (campos existentes) | | | | |

**Estados de Pago**:
- `Pendiente`: No hay liquidaciones asociadas pagadas
- `Parcialmente Pagado`: Al menos una liquidación pagada, pero no todas
- `Pagado`: Todas las liquidaciones asociadas están pagadas

**Transiciones de Estado de Pago**:
```
Pendiente → Parcialmente Pagado (cuando primera liquidación se paga)
Parcialmente Pagado → Pagado (cuando última liquidación se paga)
Pagado → Parcialmente Pagado (cuando se revierte pago de una liquidación)
Parcialmente Pagado → Pendiente (cuando se revierte pago de única liquidación pagada)
```

---

### 2. LIQUIDACION (Extendida)

**Tabla**: LIQUIDACIONES
**Motivo de cambio**: Agregar campo `valor_incidentes` para descuentos

| Campo | Tipo | Nullable | Default | Descripción |
|-------|------|----------|---------|-------------|
| ID_LIQUIDACION | INTEGER PK | No | AUTO | Identificador único |
| ID_CONTRATO_M | INTEGER FK | No | - | Referencia a contrato mandato |
| VALOR_INCIDENTES | INTEGER | Sí | 0 | Total descuentos por incidentes |
| NETO_A_PAGAR | INTEGER | No | 0 | Neto a pagar (se recalcula) |
| ... (campos existentes) | | | | |

**Regla de Negocio**:
```
NETO_A_PAGAR = TOTAL_INGRESOS - TOTAL_EGRESOS - VALOR_INCIDENTES
```

---

### 3. PLAN_PAGO_INCIDENTE (Nueva)

**Tabla**: PLAN_PAGO_INCIDENTE
**Propósito**: Almacena el plan de pago definido para un incidente

| Campo | Tipo | Nullable | Default | Descripción |
|-------|------|----------|---------|-------------|
| ID_PLAN_PAGO | INTEGER PK | No | AUTO | Identificador único |
| ID_INCIDENTE | INTEGER FK | No | - | Referencia a incidente |
| NUM_CUOTAS | INTEGER | No | - | Número de cuotas del plan |
| VALOR_CUOTA | INTEGER | No | - | Valor de cada cuota |
| TOTAL_PLAN | INTEGER | No | - | Valor total del plan |
| ESTADO | TEXT | No | 'Activo' | Estado: Activo/Completado/Cancelado |
| CREADO_POR | TEXT | No | - | Usuario que creó el plan |
| CREATED_AT | TEXT | No | datetime('now') | Fecha de creación |
| UPDATED_AT | TEXT | Sí | NULL | Última actualización |

**Constraints**:
- `UNIQUE(ID_INCIDENTE)`: Solo un plan activo por incidente
- `CHECK(NUM_CUOTAS > 0)`: Mínimo 1 cuota
- `CHECK(VALOR_CUOTA > 0)`: Cuota debe ser positiva
- `CHECK(TOTAL_PLAN = NUM_CUOTAS * VALOR_CUOTA)`: Integridad de cálculo

**Estados**:
- `Activo`: Plan vigente, puede modificarse si no tiene cuotas asociadas
- `Completado`: Todas las cuotas asociadas a liquidaciones
- `Cancelado`: Plan anulado por el usuario

---

### 4. CUOTA_INCIDENTE (Nueva)

**Tabla**: CUOTA_INCIDENTE
**Propósito**: Representa cada cuota individual del plan de pago

| Campo | Tipo | Nullable | Default | Descripción |
|-------|------|----------|---------|-------------|
| ID_CUOTA | INTEGER PK | No | AUTO | Identificador único |
| ID_PLAN_PAGO | INTEGER FK | No | - | Referencia al plan de pago |
| NUMERO_CUOTA | INTEGER | No | - | Número de la cuota (1, 2, 3...) |
| VALOR_CUOTA | INTEGER | No | - | Valor de esta cuota |
| ID_LIQUIDACION | INTEGER FK | Sí | NULL | Liquidación asociada (NULL = pendiente) |
| ESTADO_PAGO | TEXT | No | 'Pendiente' | Estado: Pendiente/Asociada/Pagada |
| CREATED_AT | TEXT | No | datetime('now') | Fecha de creación |

**Constraints**:
- `UNIQUE(ID_PLAN_PAGO, NUMERO_CUOTA)`: Una cuota por número en cada plan
- `CHECK(NUMERO_CUOTA > 0)`: Numeración positiva

**Estados**:
- `Pendiente`: Cuota creada, sin liquidación asociada
- `Asociada`: Cuota asociada a una liquidación
- `Pagada`: Liquidación asociada está en estado "Pagada"

---

### 5. INCIDENTE_LIQUIDACION (Nueva)

**Tabla**: INCIDENTE_LIQUIDACION
**Propósito**: Tabla de relación entre incidentes y liquidaciones

| Campo | Tipo | Nullable | Default | Descripción |
|-------|------|----------|---------|-------------|
| ID_RELACION | INTEGER PK | No | AUTO | Identificador único |
| ID_INCIDENTE | INTEGER FK | No | - | Referencia a incidente |
| ID_LIQUIDACION | INTEGER FK | No | - | Referencia a liquidación |
| NUMERO_CUOTA | INTEGER | No | - | Cuota del incidente asociada |
| VALOR_DESCUENTO | INTEGER | No | - | Valor del descuento |
| ASOCIADO_POR | TEXT | No | - | Usuario que asoció |
| FECHA_ASOCIACION | TEXT | No | datetime('now') | Fecha de asociación |

**Constraints**:
- `UNIQUE(ID_INCIDENTE, ID_LIQUIDACION, NUMERO_CUOTA)`: Evitar duplicados
- `CHECK(VALOR_DESCUENTO > 0)`: Descuento debe ser positivo

---

### 6. BLOQUEOS_EDICION (Nueva - Opcional)

**Tabla**: BLOQUEOS_EDICION
**Propósito**: Control de concurrencia para ediciones

| Campo | Tipo | Nullable | Default | Descripción |
|-------|------|----------|---------|-------------|
| ID_BLOQUEO | INTEGER PK | No | AUTO | Identificador único |
| TABLA | TEXT | No | - | Nombre de la tabla bloqueada |
| ID_REGISTRO | INTEGER | No | - | ID del registro bloqueado |
| USUARIO | TEXT | No | - | Usuario que bloqueó |
| SESION_ID | TEXT | No | - | ID de sesión |
| FECHA_BLOQUEO | TEXT | No | datetime('now') | Cuándo se bloqueó |
| FECHA_EXPIRACION | TEXT | No | - | Cuándo expira el bloqueo |

**Constraints**:
- `UNIQUE(TABLA, ID_REGISTRO)`: Un solo bloqueo por registro
- Índice en `FECHA_EXPIRACION` para limpieza automática

**Limpieza**: Job periódico elimina bloques expirados (>5 minutos)

---

## State Transitions Diagram

### Incidente - Estado de Pago

```
┌─────────────────────────────────────────────────────────────┐
│                    ESTADO DE PAGO                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────┐    liquidación      ┌──────────────────┐     │
│  │          │    se paga          │                  │     │
│  │ Pendiente│────────────────────►│ Parcialmente     │     │
│  │          │◄────────────────────│ Pagado           │     │
│  │          │    se revierte      │                  │     │
│  └──────────┘    pago             └────────┬─────────┘     │
│       ▲                                     │               │
│       │                                     │ todas         │
│       │ se revierte                         │ liquidaciones │
│       │ última                              │ se pagan      │
│       │ liquidación                         ▼               │
│       │                            ┌──────────────────┐    │
│       └────────────────────────────│                  │    │
│                                    │ Pagado           │    │
│                                    │                  │    │
│                                    └──────────────────┘    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Cuota Incidente - Estado

```
┌─────────────────────────────────────────────────────────────┐
│                     ESTADO DE CUOTA                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────┐    se asocia        ┌──────────────────┐     │
│  │          │    a liquidación    │                  │     │
│  │ Pendiente│────────────────────►│ Asociada         │     │
│  │          │◄────────────────────│                  │     │
│  │          │    se desasocia     └────────┬─────────┘     │
│  └──────────┘                              │               │
│                                            │ liquidación   │
│                                            │ se paga       │
│                                            ▼               │
│                                   ┌──────────────────┐    │
│                                   │                  │    │
│                                   │ Pagada           │    │
│                                   │                  │    │
│                                   └──────────────────┘    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Validation Rules

### PlanPagoIncidente

1. `NUM_CUOTAS` debe ser >= 1
2. `VALOR_CUOTA` debe ser > 0
3. `TOTAL_PLAN` debe ser igual a `NUM_CUOTAS * VALOR_CUOTA`
4. Solo puede existir un plan activo por incidente
5. No se puede modificar un plan si tiene cuotas con `ID_LIQUIDACION` no NULL

### CuotaIncidente

1. `NUMERO_CUOTA` debe ser > 0
2. `VALOR_CUOTA` debe ser > 0
3. `NUMERO_CUOTA` debe ser único dentro del plan
4. `ID_LIQUIDACION` solo puede asignarse si la liquidación está en estado 'En Proceso' o 'Aprobada'

### IncidenteLiquidacion

1. `VALOR_DESCUENTO` debe ser > 0
2. La combinación `(ID_INCIDENTE, ID_LIQUIDACION, NUMERO_CUOTA)` debe ser única
3. El incidente debe tener estado operativo 'Aprobado', 'En Reparacion' o 'Finalizado'
4. El incidente debe tener estado de pago diferente de 'Pagado'
5. La liquidación debe estar en estado 'En Proceso' o 'Aprobada'

## Migration Scripts

```sql
-- Migración 001: Agregar campos a tablas existentes
ALTER TABLE INCIDENTES ADD COLUMN estado_pago TEXT DEFAULT 'Pendiente';
ALTER TABLE LIQUIDACIONES ADD COLUMN valor_incidentes INTEGER DEFAULT 0;

-- Migración 002: Crear tabla PLAN_PAGO_INCIDENTE
CREATE TABLE PLAN_PAGO_INCIDENTE (
    ID_PLAN_PAGO INTEGER PRIMARY KEY AUTOINCREMENT,
    ID_INCIDENTE INTEGER NOT NULL,
    NUM_CUOTAS INTEGER NOT NULL CHECK(NUM_CUOTAS > 0),
    VALOR_CUOTA INTEGER NOT NULL CHECK(VALOR_CUOTA > 0),
    TOTAL_PLAN INTEGER NOT NULL,
    ESTADO TEXT NOT NULL DEFAULT 'Activo',
    CREADO_POR TEXT NOT NULL,
    CREATED_AT TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
    UPDATED_AT TEXT,
    FOREIGN KEY (ID_INCIDENTE) REFERENCES INCIDENTES(ID_INCIDENTE),
    UNIQUE(ID_INCIDENTE)
);

-- Migración 003: Crear tabla CUOTA_INCIDENTE
CREATE TABLE CUOTA_INCIDENTE (
    ID_CUOTA INTEGER PRIMARY KEY AUTOINCREMENT,
    ID_PLAN_PAGO INTEGER NOT NULL,
    NUMERO_CUOTA INTEGER NOT NULL CHECK(NUMERO_CUOTA > 0),
    VALOR_CUOTA INTEGER NOT NULL CHECK(VALOR_CUOTA > 0),
    ID_LIQUIDACION INTEGER,
    ESTADO_PAGO TEXT NOT NULL DEFAULT 'Pendiente',
    CREATED_AT TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
    FOREIGN KEY (ID_PLAN_PAGO) REFERENCES PLAN_PAGO_INCIDENTE(ID_PLAN_PAGO),
    FOREIGN KEY (ID_LIQUIDACION) REFERENCES LIQUIDACIONES(ID_LIQUIDACION),
    UNIQUE(ID_PLAN_PAGO, NUMERO_CUOTA)
);

-- Migración 004: Crear tabla INCIDENTE_LIQUIDACION
CREATE TABLE INCIDENTE_LIQUIDACION (
    ID_RELACION INTEGER PRIMARY KEY AUTOINCREMENT,
    ID_INCIDENTE INTEGER NOT NULL,
    ID_LIQUIDACION INTEGER NOT NULL,
    NUMERO_CUOTA INTEGER NOT NULL,
    VALOR_DESCUENTO INTEGER NOT NULL CHECK(VALOR_DESCUENTO > 0),
    ASOCIADO_POR TEXT NOT NULL,
    FECHA_ASOCIACION TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
    FOREIGN KEY (ID_INCIDENTE) REFERENCES INCIDENTES(ID_INCIDENTE),
    FOREIGN KEY (ID_LIQUIDACION) REFERENCES LIQUIDACIONES(ID_LIQUIDACION),
    UNIQUE(ID_INCIDENTE, ID_LIQUIDACION, NUMERO_CUOTA)
);

-- Migración 005: Crear tabla BLOQUEOS_EDICION (opcional)
CREATE TABLE BLOQUEOS_EDICION (
    ID_BLOQUEO INTEGER PRIMARY KEY AUTOINCREMENT,
    TABLA TEXT NOT NULL,
    ID_REGISTRO INTEGER NOT NULL,
    USUARIO TEXT NOT NULL,
    SESION_ID TEXT NOT NULL,
    FECHA_BLOQUEO TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
    FECHA_EXPIRACION TEXT NOT NULL,
    UNIQUE(TABLA, ID_REGISTRO)
);

-- Índices para performance
CREATE INDEX IDX_CUOTA_PLAN_PAGO ON CUOTA_INCIDENTE(ID_PLAN_PAGO);
CREATE INDEX IDX_CUOTA_LIQUIDACION ON CUOTA_INCIDENTE(ID_LIQUIDACION);
CREATE INDEX IDX_INCIDENTE_LIQ_INCIDENTE ON INCIDENTE_LIQUIDACION(ID_INCIDENTE);
CREATE INDEX IDX_INCIDENTE_LIQ_LIQUIDACION ON INCIDENTE_LIQUIDACION(ID_LIQUIDACION);
CREATE INDEX IDX_BLOQUEOS_EXPIRACION ON BLOQUEOS_EDICION(FECHA_EXPIRACION);
```
