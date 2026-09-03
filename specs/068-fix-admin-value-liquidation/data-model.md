# Data Model: fix-admin-value-liquidation

No structural schema changes are required for this feature. The database tables remain the same.

## Entities Involved

### 1. `PROPIEDADES`
- **Fields:** `VALOR_ADMINISTRACION`
- **Role:** Source of truth. When updated, triggers the cascade.

### 2. `LIQUIDACIONES`
- **Fields Affected by Cascade:**
  - `GASTOS_ADMINISTRACION`: Updated to new property value (unless manually overridden).
  - `TOTAL_EGRESOS`: Recalculated by substituting old admin value with new one.
  - `NETO_A_PAGAR`: Recalculated based on new `TOTAL_EGRESOS`.
  - `UPDATED_AT`: Set to current timestamp.
  - `UPDATED_BY`: Set to user ID who initiated the property update.
- **Rules:**
  - Update only applies to rows where `ESTADO_LIQUIDACION = 'En Proceso'`.
  - Update only applies to the current active billing cycle (`AND PERIODO = %s`).
  - Manual Override Protection: Row is skipped if `GASTOS_ADMINISTRACION != old_valor_admin`.
