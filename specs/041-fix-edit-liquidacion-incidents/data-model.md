# Data Model: Fix Edit Liquidación Incidents Loading

**Feature**: 041-fix-edit-liquidacion-incidents
**Date**: 2026-07-10

## Existing Entities (No Schema Changes)

### LIQUIDACIONES (read-only for this feature)

| Column | Type | Notes |
|--------|------|-------|
| ID_LIQUIDACION | INTEGER PK | |
| ID_CONTRATO_M | INTEGER FK | |
| PERIODO | TEXT | YYYY-MM |
| VALOR_INCIDENTES | INTEGER | Aggregate total of incident discounts |
| OBSERVACIONES | TEXT | Free-text observations |
| ESTADO_LIQUIDACION | TEXT | 'En Proceso', 'Aprobada', 'Pagada', 'Cancelada |

### INCIDENTE_LIQUIDACION (read-only for this feature)

| Column | Type | Notes |
|--------|------|-------|
| ID_RELACION | INTEGER PK | |
| ID_INCIDENTE | INTEGER FK → INCIDENTES | |
| ID_LIQUIDACION | INTEGER FK → LIQUIDACIONES | |
| NUMERO_CUOTA | INTEGER | Installment number |
| VALOR_DESCUENTO | INTEGER | Amount discounted |
| ASOCIADO_POR | TEXT | User who associated |
| FECHA_ASOCIACION | TEXT | Timestamp |

### INCIDENTES (read-only for this feature)

| Column | Type | Notes |
|--------|------|-------|
| ID_INCIDENTE | INTEGER PK | |
| DESCRIPCION_INCIDENTE | TEXT | Description |
| COSTO_INCIDENTE | INTEGER | Total cost |
| ESTADO | TEXT | 'Aprobado', 'En Reparacion', 'Finalizado' |
| ESTADO_PAGO | TEXT | 'Pendiente', 'Parcialmente Pagado', 'Pagado' |

## Query for Associated Incidents (New)

When opening the edit modal, the system will execute:

```sql
SELECT 
    il.ID_RELACION,
    il.ID_INCIDENTE,
    il.VALOR_DESCUENTO,
    il.NUMERO_CUOTA,
    il.FECHA_ASOCIACION,
    i.DESCRIPCION_INCIDENTE,
    i.COSTO_INCIDENTE,
    i.ESTADO,
    i.ESTADO_PAGO
FROM INCIDENTE_LIQUIDACION il
INNER JOIN INCIDENTES i ON il.ID_INCIDENTE = i.ID_INCIDENTE
WHERE il.ID_LIQUIDACION = ?
ORDER BY il.FECHA_ASOCIACION
```

**Returns**: List of associated incidents with descriptions, amounts, and states.

## State Variables (New)

Added to `LiquidacionesState`:

| Variable | Type | Default | Purpose |
|----------|------|---------|---------|
| incidentes_asociados_liquidacion | List[Dict] | [] | Stores associated incidents for display in edit modal |
| loading_incidentes_asociados | bool | False | Loading indicator for incidents fetch |

## Data Flow

```
User clicks "Editar" → open_edit_modal(id)
  → obtener_detalle_liquidacion_ui(id) → returns {valor_incidentes, observaciones, ...}
  → populate form_data
  → cargar_incidentes_asociados(id) → SQL JOIN query → populate incidentes_asociados_liquidacion
  → render edit modal with:
      - form_data["valor_incidentes"] (numeric field)
      - form_data["observaciones"] (textarea)
      - incidentes_asociados_liquidacion (read-only table)
```

## Validation Rules

- Associated incidents are read-only in the edit modal (view only)
- "Seleccionar Incidentes" button opens a separate modal for ADDING new associations
- When new incidents are associated, the list refreshes automatically
