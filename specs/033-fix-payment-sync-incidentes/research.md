# Research: Fix Payment Status Synchronization

**Date**: 2026-07-07
**Feature**: 033-fix-payment-sync-incidentes

## Root Cause Analysis

### Issue Summary

When a Liquidación is marked as "Pagada", the associated Incidente's payment status is not being updated correctly. The cuota in the payment plan remains "Pendiente" and the incident's payment badge shows "Pendiente" instead of "Pagado" or "Parcialmente Pagado".

### Code Trace

#### Single Payment Flow

1. **User Action**: User clicks "Registrar Pago" in payment modal
2. **State Handler**: `LiquidacionesState.marcar_como_pagada()` (liquidaciones_state.py:1226)
3. **Service Call**: `ServicioFinanciero.marcar_liquidacion_pagada()` (servicio_financiero.py:333)
4. **Cuota Update**: Direct update of `CUOTA_INCIDENTE.ESTADO_PAGO = 'Pagada'` (servicio_financiero.py:346-348)
5. **Incident Status Sync**: `ServicioEstadoPagoAutomatico.actualizar_estado_pago_por_liquidacion()` (liquidaciones_state.py:1271)

#### Bulk Payment Flow

1. **User Action**: User clicks "Pago Masivo" button
2. **State Handler**: `LiquidacionesState.marcar_como_pagada_masiva()` (liquidaciones_state.py:1069)
3. **Service Call**: `ServicioFinanciero.marcar_liquidacion_propietario_pagada()` (servicio_financiero.py:350)
4. **Loop**: Iterates over liquidaciones, calls `marcar_liquidacion_pagada()` for each
5. **MISSING**: No call to `ServicioEstadoPagoAutomatico` for bulk payments

### Identified Root Causes

#### Root Cause 1: Transaction Boundary Mismatch

**Location**: `servicio_financiero.py:333-348` and `servicio_estado_pago.py:46-102`

`ServicioFinanciero.marcar_liquidacion_pagada()` performs:
1. Update LIQUIDACIONES set ESTADO_LIQUIDACION = 'Pagada'
2. Update CUOTA_INCIDENTE set ESTADO_PAGO = 'Pagada' for each cuota

`ServicioEstadoPagoAutomatico.recalcular_estado_pago_incidente()` reads:
```sql
SELECT 
    COUNT(c.ID_CUOTA) as total_con_liq,
    SUM(CASE WHEN l.ESTADO_LIQUIDACION = 'Pagada' THEN 1 ELSE 0 END) as total_pagadas
FROM CUOTA_INCIDENTE c
JOIN LIQUIDACIONES l ON c.ID_LIQUIDACION = l.ID_LIQUIDACION
WHERE c.ID_PLAN_PAGO = %s
```

**Problem**: The SQL counts based on `LIQUIDACIONES.ESTADO_LIQUIDACION = 'Pagada'`, not `CUOTA_INCIDENTE.ESTADO_PAGO`. If the liquidacion update is not committed before the recount, the count will be stale.

#### Root Cause 2: Silent Error Swallowing

**Location**: `liquidaciones_state.py:1246-1281`

```python
try:
    servicio_estado.actualizar_estado_pago_por_liquidacion(...)
except Exception as e_estado:
    # No fallar el pago principal por error en actualización de estado
    logging.getLogger(__name__).warning(...)
```

**Problem**: Any error in `ServicioEstadoPagoAutomatico` is silently logged but not propagated. The user sees "Pago registrado exitosamente" even if the incident status was not updated.

#### Root Cause 3: Bulk Payment Missing Sync

**Location**: `liquidaciones_state.py:1069-1105`

The `marcar_como_pagada_masiva()` function calls `ServicioFinanciero.marcar_liquidacion_propietario_pagada()` which internally calls `marcar_liquidacion_pagada()` for each liquidacion. However, the incident status sync code (lines 1246-1281) is only in `marcar_como_pagada()`, not in the bulk flow.

#### Root Cause 4: Reversal Missing Sync

**Location**: `liquidaciones_state.py:1345-1372`

The `confirmar_reversar()` function calls `servicio.reversar_liquidacion()` but does NOT call `ServicioEstadoPagoAutomatico.revertir_estado_pago_por_liquidacion()`.

### Decision

**Fix approach**: Modify the codebase to ensure `ServicioEstadoPagoAutomatico` is called after every payment state change, both in single and bulk flows, and handle errors appropriately.

**Rationale**: The current code has the sync logic but it's incomplete and error-prone. The fix should:
1. Add incident status sync to bulk payment flow
2. Add incident status sync to reversal flow
3. Ensure proper error handling that doesn't silently fail
4. Verify the SQL queries are reading the correct data

### Alternatives Considered

1. **Alternative 1**: Change SQL to read `CUOTA_INCIDENTE.ESTADO_PAGO` instead of `LIQUIDACIONES.ESTADO_LIQUIDACION`
   - Rejected: The current logic is correct (count based on liquidacion status), the issue is that the sync is not being triggered

2. **Alternative 2**: Add database trigger to auto-update incident status
   - Rejected: Adds complexity and bypasses business logic layer

3. **Alternative 3**: Use event-driven architecture with pub/sub
   - Rejected: Over-engineering for this specific bug fix

## Technical Findings

### Database Schema

- `CUOTA_INCIDENTE`: Contains `ID_LIQUIDACION` (foreign key) and `ESTADO_PAGO` (Pendiente/Asociada/Pagada)
- `LIQUIDACIONES`: Contains `ESTADO_LIQUIDACION` (En Proceso/Aprobada/Pagada/Cancelada)
- `INCIDENTE_LIQUIDACION`: Junction table linking INCIDENTES to LIQUIDACIONES

### Service Layer

- `ServicioFinanciero`: Handles payment operations
- `ServicioEstadoPagoAutomatico`: Handles incident status recalculation
- Both use `db_manager` for database operations

### State Management

- Reflex state classes manage UI state
- `form_data` dictionary pattern for form submissions
- Background tasks for async operations

## Recommendations

1. **Immediate Fix**: Add incident status sync to bulk payment and reversal flows
2. **Error Handling**: Log detailed errors instead of silently swallowing them
3. **Testing**: Add integration tests for payment sync scenarios
4. **Monitoring**: Add logging to track sync operations
