# Quickstart: Fix Payment Status Synchronization

**Date**: 2026-07-07
**Feature**: 033-fix-payment-sync-incidentes

## Overview

This guide provides validation scenarios to verify the payment status synchronization fix works correctly.

## Prerequisites

1. Running instance of the Inmobiliaria Velar system
2. Test database with:
   - At least one property with an associated incident
   - The incident has an active payment plan with cuotas
   - At least one cuota is associated with a liquidación in "Aprobada" state
3. User logged in with payment permissions

## Validation Scenarios

### Scenario 1: Single Payment Sync (P1)

**Goal**: Verify that marking a single liquidación as paid updates the incident payment status

**Steps**:
1. Navigate to Liquidaciones module
2. Find a liquidación in "Aprobada" state that is associated with an incident
3. Click "Registrar Pago" button
4. Fill in payment form:
   - Fecha de Pago: Today's date
   - Método de Pago: "Transferencia"
   - Referencia: "TEST-001"
5. Click "Guardar"

**Expected Results**:
- [ ] Liquidación status changes to "Pagada"
- [ ] Associated cuota status changes from "Pendiente" to "Pagada"
- [ ] Incident payment status updates to "Pagado" (if all cuotas paid) or "Parcialmente Pagado"
- [ ] Incident card badge shows correct status (green/blue)
- [ ] No page reload required

**Verification Commands**:
```sql
-- Check liquidación status
SELECT ESTADO_LIQUIDACION FROM LIQUIDACIONES 
WHERE ID_LIQUIDACION = <liquidacion_id>;

-- Check cuota status
SELECT ESTADO_PAGO FROM CUOTA_INCIDENTE 
WHERE ID_LIQUIDACION = <liquidacion_id>;

-- Check incident status
SELECT ESTADO_PAGO FROM INCIDENTE 
WHERE ID_INCIDENTE = <incidente_id>;
```

### Scenario 2: Bulk Payment Sync (P2)

**Goal**: Verify that bulk payment updates all affected incident statuses

**Steps**:
1. Navigate to Liquidaciones module
2. Select a property owner with multiple liquidaciones
3. Click "Pago Masivo" button
4. Fill in payment form:
   - Período: Current month
   - Fecha de Pago: Today's date
   - Método de Pago: "Efectivo"
   - Referencia: "BULK-001"
5. Click "Guardar"

**Expected Results**:
- [ ] All "Aprobada" liquidaciones change to "Pagada"
- [ ] All associated cuotas change to "Pagada"
- [ ] All affected incidents update their payment status
- [ ] Toast message shows correct count: "Se registraron X pagos correctamente"

### Scenario 3: Payment Reversal Sync (P2)

**Goal**: Verify that reversing a payment updates the incident payment status

**Steps**:
1. Navigate to Liquidaciones module
2. Find a liquidación in "Pagada" state
3. Click "Reversar" button
4. Confirm the reversal

**Expected Results**:
- [ ] Liquidación status changes to "En Proceso"
- [ ] Associated cuota status changes from "Pagada" to "Asociada"
- [ ] Incident payment status recalculates correctly
- [ ] Incident card badge updates accordingly

### Scenario 4: Error Handling (P1)

**Goal**: Verify that sync errors don't break the payment process

**Steps**:
1. Simulate a database error (e.g., disconnect during payment)
2. Attempt to register a payment

**Expected Results**:
- [ ] Payment fails with appropriate error message
- [ ] No partial state changes
- [ ] System remains stable

## Testing Commands

### Run Unit Tests
```bash
pytest tests/unit/test_servicio_estado_pago.py -v
pytest tests/unit/test_servicio_financiero.py -v
```

### Run Integration Tests
```bash
pytest tests/integration/test_payment_sync.py -v
```

### Manual Database Verification
```sql
-- Find liquidaciones with associated incidents
SELECT 
    l.ID_LIQUIDACION,
    l.ESTADO_LIQUIDACION,
    c.ID_CUOTA,
    c.ESTADO_PAGO,
    i.ID_INCIDENTE,
    i.ESTADO_PAGO as INCIDENTE_ESTADO_PAGO
FROM LIQUIDACIONES l
JOIN CUOTA_INCIDENTE c ON c.ID_LIQUIDACION = l.ID_LIQUIDACION
JOIN PLAN_PAGO_INCIDENTE p ON c.ID_PLAN_PAGO = p.ID_PLAN_PAGO
JOIN INCIDENTE i ON p.ID_INCIDENTE = i.ID_INCIDENTE
WHERE l.ESTADO_LIQUIDACION = 'Pagada'
  AND c.ESTADO_PAGO != 'Pagada';
-- This query should return 0 rows after fix
```

## Success Criteria Validation

- [ ] **SC-001**: 100% of liquidaciones marked as "Pagada" correctly update incident payment status
- [ ] **SC-002**: Incident payment status reflects in UI within 2 seconds
- [ ] **SC-003**: 100% of payment reversals correctly update incident payment status
- [ ] **SC-004**: Bulk payments correctly sync all affected incident statuses
- [ ] **SC-005**: No state updates lost due to sync errors

## Troubleshooting

### Issue: Incident status not updating after payment
1. Check browser console for errors
2. Verify `ServicioEstadoPagoAutomatico` is being called
3. Check database for `CUOTA_INCIDENTE.ID_LIQUIDACION` is set
4. Verify `LIQUIDACIONES.ESTADO_LIQUIDACION` is 'Pagada'

### Issue: Bulk payment not syncing incidents
1. Verify `marcar_como_pagada_masiva()` calls sync for each liquidación
2. Check logs for any exceptions in sync code
3. Verify each liquidación has associated cuotas

### Issue: Reversal not updating incident status
1. Verify `confirmar_reversar()` calls `revertir_estado_pago_por_liquidacion()`
2. Check that cuota `ESTADO_PAGO` is changed back to 'Asociada'
3. Verify incident status recalculates correctly
