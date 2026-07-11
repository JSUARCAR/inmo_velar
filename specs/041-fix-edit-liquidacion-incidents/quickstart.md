# Quickstart Validation Guide: Fix Edit Liquidación Incidents Loading

**Feature**: 041-fix-edit-liquidacion-incidents
**Date**: 2026-07-10

## Prerequisites

- PostgreSQL database with test data (liquidaciones with associated incidents)
- Application running locally (`reflex run`)
- User authenticated with admin or owner role

## Validation Scenarios

### V1: Associated incidents display when editing

**Setup**: Ensure liquidación L-001 has 2+ associated incidents in `INCIDENTE_LIQUIDACION` table.

1. Navigate to Liquidaciones page
2. Click "Editar" on liquidación L-001 (must be in "En Proceso" state)
3. **Expected**: Modal opens showing:
   - Numeric field "Incidentes" with total value
   - Read-only table listing each associated incident with: ID, Descripción, Estado, Estado Pago, Valor Descuento
   - Textarea "Observaciones" with stored text (or empty if none)

### V2: Single incident display

**Setup**: Ensure liquidación L-002 has exactly 1 associated incident.

1. Open edit modal for L-002
2. **Expected**: Table shows exactly 1 incident row

### V3: No incidents display

**Setup**: Ensure liquidación L-003 has 0 associated incidents.

1. Open edit modal for L-003
2. **Expected**: Table shows "No hay incidentes asociados" or is empty
3. "Seleccionar Incidentes" button is visible (allows adding)

### V4: Observations field loads correctly

**Setup**: Ensure liquidación L-001 has OBSERVACIONES = "Test observation text" in DB.

1. Open edit modal for L-001
2. **Expected**: Textarea shows "Test observation text"
3. Modify text and save
4. Reopen modal
5. **Expected**: Modified text persists

### V5: Observations field handles NULL

**Setup**: Ensure liquidación L-004 has OBSERVACIONES = NULL in DB.

1. Open edit modal for L-004
2. **Expected**: Textarea is empty (not showing "None")

### V6: Data consistency — DB vs UI

**Setup**: Note the `VALOR_INCIDENTES` and `OBSERVACIONES` values in DB for L-001.

1. Open edit modal for L-001
2. **Expected**: 
   - Numeric field shows exact DB value for VALOR_INCIDENTES
   - Textarea shows exact DB value for OBSERVACIONES
   - Associated incidents table matches `INCIDENTE_LIQUIDACION` rows for L-001

### V7: Add incidents then verify display

**Setup**: Liquidación L-005 has 0 incidents.

1. Open edit modal for L-005
2. Click "Seleccionar Incidentes"
3. Select 1 incident and confirm association
4. **Expected**: Modal closes, list refreshes
5. Reopen edit modal for L-005
6. **Expected**: Associated incidents table now shows the added incident

### V8: Regression — create liquidation

1. Create a new liquidación via bulk generation or manual creation
2. **Expected**: No errors, liquidación created successfully

### V9: Regression — approve liquidation

1. Open edit modal for a liquidación in "En Proceso" state
2. Close modal without changes
3. Approve the liquidación
4. **Expected**: State changes to "Aprobada" successfully

## Automated Validation

Run existing test suite to confirm no regressions:

```bash
# If tests exist
python -m pytest tests/ -v

# Manual Playwright validation (if applicable)
# Navigate to production URL and follow V1-V9 scenarios
```

## Success Criteria Validation

| Criterion | How to Verify |
|-----------|---------------|
| SC-001: 100% of liquidations with incidents show correctly | Test V1, V2, V3 with multiple liquidaciones |
| SC-002: No data differences DB/API/UI | Test V6 — compare DB values with UI display |
| SC-003: < 2 second load time | Open edit modal, measure time from click to full render |
| SC-004: No regressions | Test V8, V9 + run full test suite |
| SC-005: Consistent and reliable | Test V4, V5, V7 — multiple open/close cycles |
