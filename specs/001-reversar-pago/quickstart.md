# Quickstart Validation Guide: Reversar Pago

**Feature**: 001-reversar-pago
**Date**: 2026-06-30

## Prerequisites

1. Database running with LIQUIDACIONES and AUDITORIA_CAMBIOS tables
2. At least one liquidation in "Pagada" state
3. User with "REVERSAR_PAGO" permission on "Liquidaciones" module
4. Application running (`reflex run`)

## Validation Scenarios

### V1: Individual Payment Reversal (Happy Path)

**Steps**:
1. Navigate to `/liquidaciones`
2. Find a liquidation in "Pagada" state
3. Click the "Reversar Pago" button (rotate_ccw icon)
4. Verify dialog shows: propietario, dirección, período, monto, fecha de pago
5. Enter a motivo with at least 10 characters
6. Click "Confirmar Reversión"

**Expected**:
- Dialog closes
- Toast shows "Pago reversado exitosamente"
- Liquidation now shows state "Aprobada" in the table
- Payment fields (fecha_pago, metodo_pago, referencia_pago) are cleared

### V2: Idempotency Test

**Steps**:
1. Take a liquidation already in "Aprobada" state
2. Attempt to reverse payment via API or direct state call

**Expected**:
- Operation returns success (no error)
- No changes to the liquidation
- No new audit records beyond the trigger-generated ones

### V3: Invalid State Rejection

**Steps**:
1. Take a liquidation in "En Proceso" state
2. Attempt to reverse payment

**Expected**:
- Operation fails with error message
- Liquidation state unchanged

### V4: Motivo Validation

**Steps**:
1. Open reverse pago confirmation dialog
2. Enter a motivo with less than 10 characters
3. Attempt to confirm

**Expected**:
- Confirm button is disabled or
- Error message: "El motivo debe tener al menos 10 caracteres"
- No reversal executed

### V5: Audit Trail Verification

**Steps**:
1. Execute a payment reversal
2. Query AUDITORIA_CAMBIOS table:
   ```sql
   SELECT * FROM AUDITORIA_CAMBIOS 
   WHERE TABLA = 'LIQUIDACIONES' 
   AND ID_REGISTRO = [reversed_liquidation_id]
   ORDER BY FECHA_CAMBIO DESC;
   ```

**Expected**:
- Records showing ESTADO_LIQUIDACION change: Pagada → Aprobada
- Records showing FECHA_PAGO, METODO_PAGO, REFERENCIA_PAGO cleared
- Record with CAMPO_MODIFICADO = 'MOTIVO_REVERSION'

### V6: Bulk Reversal (Selective)

**Steps**:
1. Owner with 3 liquidations for a period:
   - Liq A: "Pagada"
   - Liq B: "Pagada"
   - Liq C: "Aprobada"
2. Execute bulk reversal for owner+period

**Expected**:
- Liq A: "Pagada" → "Aprobada"
- Liq B: "Pagada" → "Aprobada"
- Liq C: "Aprobada" (unchanged)
- Result: {reversed: 2, ignored: 1}

### V7: Permission Enforcement

**Steps**:
1. Login as user WITHOUT "REVERSAR_PAGO" permission
2. Navigate to `/liquidaciones`
3. View a liquidation in "Pagada" state

**Expected**:
- "Reversar Pago" button is NOT visible in table
- "Reversar Pago" button is NOT visible in detail modal

### V8: Cancel Dialog

**Steps**:
1. Open reverse pago confirmation dialog
2. Click "Cancelar"

**Expected**:
- Dialog closes
- No changes to liquidation
- State variables cleared
