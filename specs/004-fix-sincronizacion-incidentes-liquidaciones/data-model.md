# Data Model: Fix Sincronización Incidentes - Liquidaciones

**Date**: 2026-07-02
**Feature**: 004-fix-sincronizacion-incidentes-liquidaciones

## Entidades Afectadas

### 1. Liquidacion

**Tabla**: `LIQUIDACIONES`
**Campos afectados por el fix**:

| Campo | Tipo | Default | Descripción | Fix Aplicado |
|-------|------|---------|-------------|--------------|
| `VALOR_INCIDENTES` | DECIMAL(12,2) | 0 | Suma de descuentos por incidentes | ✅ Trigger como fuente primaria |
| `NETO_A_PAGAR` | DECIMAL(12,2) | 0 | Neto a pagar al propietario | ✅ Recálculo post-trigger |
| `OBSERVACIONES` | TEXT | NULL | Notas y IDs de incidentes | ✅ Append/remove de IDs |

**Relaciones**:
- `1:N` → `INCIDENTE_LIQUIDACION` (un incidente puede tener múltiples liquidaciones)
- `1:N` → `CUOTA_INCIDENTE` (una liquidación puede tener múltiples cuotas)

**Reglas de Negocio**:
- `NETO_A_PAGAR = TOTAL_INGRESOS - TOTAL_EGRESOS - VALOR_INCIDENTES`
- `VALOR_INCIDENTES` se actualiza SOLO por triggers en BD
- `OBSERVACIONES` debe preservar notas del usuario al agregar IDs de incidentes

---

### 2. Incidente

**Tabla**: `INCIDENTES`
**Campos afectados por el fix**:

| Campo | Tipo | Default | Descripción | Fix Aplicado |
|-------|------|---------|-------------|--------------|
| `ESTADO_PAGO` | VARCHAR(20) | 'Pendiente' | Estado de pago del incidente | ✅ Agregar a UPDATE SQL |

**Estados de Pago**:
- `Pendiente` - Sin liquidaciones asociadas o todas pendientes
- `Asociada` - Al menos una liquidación asociada (no pagada)
- `Parcialmente Pagado` - Al menos una liquidación pagada, otras pendientes
- `Pagado` - Todas las liquidaciones asociadas están pagadas

**Relaciones**:
- `1:1` → `PLAN_PAGO_INCIDENTE` (un incidente tiene un plan de pago activo)
- `1:N` → `INCIDENTE_LIQUIDACION` (un incidente puede asociarse a múltiples liquidaciones)

---

### 3. CuotaIncidente

**Tabla**: `CUOTA_INCIDENTE`
**Campos afectados por el fix**:

| Campo | Tipo | Default | Descripción | Fix Aplicado |
|-------|------|---------|-------------|--------------|
| `ID_LIQUIDACION` | INTEGER | NULL | FK a liquidación asociada | Sin cambio |
| `ESTADO_PAGO` | VARCHAR(20) | 'Pendiente' | Estado de pago de la cuota | Sin cambio |

**Relaciones**:
- `N:1` → `PLAN_PAGO_INCIDENTE` (una cuota pertenece a un plan)
- `N:1` → `LIQUIDACIONES` (una cuota se asocia a una liquidación)

---

### 4. IncidenteLiquidacion

**Tabla**: `INCIDENTE_LIQUIDACION`
**Campos**:

| Campo | Tipo | Default | Descripción | Fix Aplicado |
|-------|------|---------|-------------|--------------|
| `ID_RELACION` | INTEGER | auto | PK | Sin cambio |
| `ID_INCIDENTE` | INTEGER | - | FK a incidente | Sin cambio |
| `ID_LIQUIDACION` | INTEGER | - | FK a liquidación | Sin cambio |
| `NUMERO_CUOTA` | INTEGER | - | Número de cuota | Sin cambio |
| `VALOR_DESCUENTO` | DECIMAL(12,2) | - | Valor del descuento | Sin cambio |

**Constraints**:
- `UNIQUE(ID_INCIDENTE, ID_LIQUIDACION, NUMERO_CUOTA)` - Evita duplicados
- `TRG_INCIDENTE_LIQ_ACTUALIZAR_VALOR_INSERT` - Actualiza VALOR_INCIDENTES en INSERT
- `TRG_INCIDENTE_LIQ_ACTUALIZAR_VALOR_DELETE` - Actualiza VALOR_INCIDENTES en DELETE

---

## Diagrama de Relaciones

```
┌─────────────────┐
│   LIQUIDACIONES │
├─────────────────┤
│ ID_LIQUIDACION  │◄──────────────────────────────────────┐
│ VALOR_INCIDENTES│ (trigger-managed)                      │
│ NETO_A_PAGAR    │ (app-calculated)                       │
│ OBSERVACIONES   │ (append/remove)                        │
└────────┬────────┘                                        │
         │                                                 │
         │ 1:N                                             │
         ▼                                                 │
┌─────────────────┐    N:1    ┌─────────────────┐          │
│INCIDENTE_LIQ    │──────────►│   INCIDENTES    │          │
├─────────────────┤           ├─────────────────┤          │
│ ID_INCIDENTE    │           │ ID_INCIDENTE    │          │
│ ID_LIQUIDACION  │           │ ESTADO_PAGO     │◄─ fix    │
│ NUMERO_CUOTA    │           └────────┬────────┘          │
│ VALOR_DESCUENTO │                    │                    │
└─────────────────┘                    │ 1:1                │
                                       ▼                    │
                              ┌─────────────────┐          │
                              │PLAN_PAGO_       │          │
                              │INCIDENTE        │          │
                              ├─────────────────┤          │
                              │ ID_PLAN_PAGO    │          │
                              │ ID_INCIDENTE    │          │
                              └────────┬────────┘          │
                                       │ 1:N               │
                                       ▼                   │
                              ┌─────────────────┐          │
                              │CUOTA_INCIDENTE  │          │
                              ├─────────────────┤          │
                              │ ID_CUOTA        │          │
                              │ ID_PLAN_PAGO    │          │
                              │ ID_LIQUIDACION  │──────────┘
                              │ ESTADO_PAGO     │
                              └─────────────────┘
```

## Triggers Existentes (Sin Cambios)

### TRG_INCIDENTE_LIQ_ACTUALIZAR_VALOR_INSERT
```sql
-- Se ejecuta al INSERT en INCIDENTE_LIQUIDACION
-- Actualiza VALOR_INCIDENTES en LIQUIDACIONES
UPDATE LIQUIDACIONES 
SET VALOR_INCIDENTES = (
    SELECT COALESCE(SUM(VALOR_DESCUENTO), 0)
    FROM INCIDENTE_LIQUIDACION
    WHERE ID_LIQUIDACION = NEW.ID_LIQUIDACION
)
WHERE ID_LIQUIDACION = NEW.ID_LIQUIDACION;
```

### TRG_INCIDENTE_LIQ_ACTUALIZAR_VALOR_DELETE
```sql
-- Se ejecuta al DELETE en INCIDENTE_LIQUIDACION
-- Actualiza VALOR_INCIDENTES en LIQUIDACIONES
UPDATE LIQUIDACIONES 
SET VALOR_INCIDENTES = (
    SELECT COALESCE(SUM(VALOR_DESCUENTO), 0)
    FROM INCIDENTE_LIQUIDACION
    WHERE ID_LIQUIDACION = OLD.ID_LIQUIDACION
)
WHERE ID_LIQUIDACION = OLD.ID_LIQUIDACION;
```

## Cambios en Repositorios

### RepositorioIncidentesPostgres
**Archivo**: `src/infraestructura/persistencia/repositorio_incidentes_postgres.py`

**Cambio**: Agregar `ESTADO_PAGO` al UPDATE SQL

```sql
-- ANTES:
UPDATE INCIDENTES SET
    ESTADO = %s,
    DESCRIPCION = %s,
    FECHA_MODIFICACION = %s
WHERE ID_INCIDENTE = %s;

-- DESPUÉS:
UPDATE INCIDENTES SET
    ESTADO = %s,
    DESCRIPCION = %s,
    ESTADO_PAGO = %s,
    FECHA_MODIFICACION = %s
WHERE ID_INCIDENTE = %s;
```

### RepositorioLiquidacionPostgres
**Archivo**: `src/infraestructura/persistencia/repositorio_liquidacion_postgres.py`

**Cambio**: Incluir `VALOR_INCIDENTES` en SELECT para obtener valor fresco

```sql
-- AGREGAR AL SELECT:
SELECT 
    ...,
    VALOR_INCIDENTES,
    NETO_A_PAGAR,
    OBSERVACIONES,
    ...
FROM LIQUIDACIONES
WHERE ID_LIQUIDACION = %s;
```

## Validaciones

### Formato de Observaciones
- **Patrón**: `Inc #{id}\nInc #{id}` (uno por línea)
- **Max Longitud**: 500 caracteres (configurable)
- **Duplicados**: No permitidos (misma línea para mismo ID)
- **Orden**: Más reciente primero (al truncar)

### Estados de Pago
- **Transiciones válidas**:
  - `Pendiente` → `Asociada` (al asociar a liquidación no pagada)
  - `Pendiente` → `Pagado` (al asociar a liquidación pagada)
  - `Asociada` → `Parcialmente Pagado` (al pagar algunas liquidaciones)
  - `Asociada` → `Pagado` (al pagar todas las liquidaciones)
  - `Parcialmente Pagado` → `Pagado` (al pagar todas las liquidaciones)
  - Cualquier estado → `Pendiente` (al desasociar todas las liquidaciones)

### Cálculo de NETO_A_PAGAR
```
NETO_A_PAGAR = TOTAL_INGRESOS - TOTAL_EGRESOS - VALOR_INCIDENTES
```
- `TOTAL_INGRESOS`: Suma de todos los ingresos
- `TOTAL_EGRESOS`: Suma de todos los egresos (comisión, IVA, gastos, etc.)
- `VALOR_INCIDENTES`: Suma de descuentos por incidentes (trigger-managed)
