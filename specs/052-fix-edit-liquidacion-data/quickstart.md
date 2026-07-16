# Quickstart Validation: Corrección de Carga de Datos en Edición de Liquidaciones

**Date**: 2026-07-13
**Feature**: 052-fix-edit-liquidacion-data

## Prerequisites

- PostgreSQL database accessible ( Railway or local)
- Application running in dev mode (`reflex run --env dev`)
- At least one asesor with multiple active contracts in the database
- Browser open to the Liquidación de Asesores module

## Validation Scenarios

### Scenario 1: Verify Fix - New Liquidación Edit Loads Complete Data

**Purpose**: Confirm that a newly generated liquidación loads all properties and discounts in the edit modal.

**Steps**:
1. Navigate to Liquidación de Asesores module
2. Click "Generación Masiva" for period 2026-07 (or current period)
3. Wait for generation to complete
4. In the grid, locate the liquidación for an asesor with 3+ active contracts
5. Click "Editar" on that liquidación
6. Count the properties shown in the modal
7. Count the discounts shown in the modal

**Expected Outcome**:
- Properties count matches the number of active contracts for that asesor
- Discounts include at least "descuento 2.00% Seguro" and "descuento 4x1000" (if applicable)
- All values (canon, commission %, commission amount) are populated correctly

**Database Verification**:
```sql
-- Replace :liquidacion_id with the actual ID
SELECT COUNT(*) as propiedades FROM LIQUIDACIONES_CONTRATOS WHERE ID_LIQUIDACION_ASESOR = :liquidacion_id;
SELECT COUNT(*) as descuentos FROM DESCUENTOS_ASESORES WHERE ID_LIQUIDACION_ASESOR = :liquidacion_id;
```

### Scenario 2: Verify Fix - Historical Liquidación Still Works

**Purpose**: Confirm no regression on liquidaciones that already work correctly.

**Steps**:
1. Navigate to Liquidación de Asesores module
2. Filter by period 2026-05 (or any historical period known to work)
3. Click "Editar" on a liquidación
4. Verify all properties and discounts are loaded

**Expected Outcome**:
- Same behavior as before the fix
- No missing data
- No UI glitches

### Scenario 3: Verify Fix - Single Property Asesor

**Purpose**: Confirm fix works for edge case of asesor with only one property.

**Steps**:
1. Find or create an asesor with exactly 1 active contract
2. Generate liquidación for that asesor
3. Click "Editar"
4. Verify 1 property and associated discounts are shown

**Expected Outcome**:
- 1 property shown correctly
- Discounts shown correctly (may be 0 if no discounts apply)

### Scenario 4: Verify Fix - Multiple Discounts

**Purpose**: Confirm all discount types are persisted and loaded.

**Steps**:
1. Generate a liquidación for an asesor with 3+ contracts
2. Click "Editar"
3. Verify the following discounts exist:
   - "descuento 2.00% Seguro" (auto-generated)
   - "descuento 4x1000" (auto-generated)
4. Add a manual discount (e.g., type "Préstamo", description "Anticipo", value $100,000)
5. Save the liquidación
6. Re-open the edit modal
7. Verify all 3 discounts are shown

**Expected Outcome**:
- Auto-generated discounts persist correctly
- Manual discount persists correctly
- Total discounts recalculated correctly

### Scenario 5: Verify Migration (if applicable)

**Purpose**: Confirm that the migration script reconstructs missing data for affected liquidaciones.

**Steps**:
1. Identify a liquidación from period 2026-07 that was affected (missing properties/discounts)
2. Run the migration script
3. Query the database to verify records exist
4. Open the edit modal for that liquidación
5. Verify all properties and discounts are now shown

**Expected Outcome**:
- LIQUIDACIONES_CONTRATOS records exist for the liquidación
- DESCUENTOS_ASESORES records exist for the liquidación
- Edit modal shows complete data
- Referential integrity is maintained

### Scenario 6: Verify No Regression - Save and Re-edit

**Purpose**: Confirm that saving an edit preserves all data.

**Steps**:
1. Open a liquidación in edit mode
2. Note the current properties and discounts
3. Modify the observaciones field
4. Save the liquidación
5. Re-open the edit modal
6. Verify all original properties and discounts are still present
7. Verify the observaciones change was saved

**Expected Outcome**:
- All data preserved after save
- Only modified fields changed
- No data loss on re-edit

## Validation Commands

### Database Queries for Verification

```sql
-- Count properties for a liquidación
SELECT COUNT(*) FROM LIQUIDACIONES_CONTRATOS WHERE ID_LIQUIDACION_ASESOR = ?;

-- Count discounts for a liquidación
SELECT COUNT(*) FROM DESCUENTOS_ASESORES WHERE ID_LIQUIDACION_ASESOR = ?;

-- Compare: liquidaciones with 0 properties but should have contracts
SELECT l.ID_LIQUIDACION_ASESOR, l.ID_ASESOR, l.PERIODO_LIQUIDACION,
       (SELECT COUNT(*) FROM LIQUIDACIONES_CONTRATOS lc WHERE lc.ID_LIQUIDACION_ASESOR = l.ID_LIQUIDACION_ASESOR) as propiedades,
       (SELECT COUNT(*) FROM DESCUENTOS_ASESORES d WHERE d.ID_LIQUIDACION_ASESOR = l.ID_LIQUIDACION_ASESOR) as descuentos
FROM LIQUIDACIONES_ASESORES l
WHERE l.PERIODO_LIQUIDACION = '2026-07'
AND l.ESTADO_LIQUIDACION != 'Anulada'
ORDER BY l.ID_LIQUIDACION_ASESOR;

-- Find affected liquidaciones (0 properties, should have > 0)
SELECT l.ID_LIQUIDACION_ASESOR, l.ID_ASESOR, l.PERIODO_LIQUIDACION
FROM LIQUIDACIONES_ASESORES l
WHERE NOT EXISTS (
    SELECT 1 FROM LIQUIDACIONES_CONTRATOS lc 
    WHERE lc.ID_LIQUIDACION_ASESOR = l.ID_LIQUIDACION_ASESOR
)
AND l.ESTADO_LIQUIDACION != 'Anulada'
AND l.ID_CONTRATO_A IS NULL;  -- Multi-contrato liquidations
```

## Success Criteria Verification

| Criterion | How to Verify |
|-----------|---------------|
| SC-001: 2026-07 liquidación shows correct data | Open edit modal, count properties/discounts, compare with DB |
| SC-002: 100% of liquidaciones show complete data | Test 5+ liquidaciones across different periods |
| SC-003: Properties count matches DB (±0) | Run SQL count query, compare with UI count |
| SC-004: Discounts count matches DB (±0) | Run SQL count query, compare with UI count |
| SC-005: No regressions | Test historical liquidaciones that worked before |
| SC-006: New generation persists correctly | Generate new liquidación, immediately verify DB records |
| SC-007: Migration records pass validation | Run migration, verify referential integrity |
