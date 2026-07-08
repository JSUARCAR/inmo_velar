# Quickstart: Fix Contratos PDF Generation

**Date**: 2026-07-08
**Feature**: 037-fix-contratos-pdf-generation

## Prerequisites

1. Access to the PostgreSQL database (Railway)
2. Access to the application source code
3. Python 3.11+ environment with dependencies installed

## Validation Steps

### Step 1: Verify Current State (Pre-Fix)

```bash
# Connect to PostgreSQL and check if columns exist
psql $DATABASE_URL -c "\d CONTRATOS_MANDATOS" | grep RESPONSABLE_DEPOSITO_ID
psql $DATABASE_URL -c "\d CONTRATOS_ARRENDAMIENTOS" | grep RESPONSABLE_DEPOSITO_ID
```

**Expected**: No output (columns don't exist)

### Step 2: Apply Migration

```bash
# Execute the updated migration
psql $DATABASE_URL -f src/infraestructura/db/migrations/migration_campos_extra_contratos.sql
```

**Expected**: Commands complete without errors

### Step 3: Verify Migration Applied

```bash
# Check columns now exist
psql $DATABASE_URL -c "\d CONTRATOS_MANDATOS" | grep RESPONSABLE_DEPOSITO_ID
psql $DATABASE_URL -c "\d CONTRATOS_ARRENDAMIENTOS" | grep RESPONSABLE_DEPOSITO_ID
```

**Expected**: Output shows `responsable_deposito_id | integer |`

### Step 4: Test Mandato PDF Generation

1. Navigate to Contratos module in the application
2. Locate a Mandato contract (any status)
3. Click "Contrato Oficial" button (purple file-check icon)
4. **Expected**: PDF downloads successfully with all legal clauses

### Step 5: Test Arrendamiento PDF Generation

1. Navigate to Contratos module
2. Locate an Arrendamiento contract
3. Click "Contrato Oficial" button
4. **Expected**: PDF downloads successfully with all 25 clauses

### Step 6: Test Paz y Salvo (Regression Check)

1. Navigate to Contratos module
2. Locate an inactive (terminated) contract
3. Click "Generar Paz y Salvo" button (teal shield-check icon)
4. **Expected**: Certificate downloads successfully with owner, tenant, property details

## Expected Outcomes

| Test | Result | Notes |
|------|--------|-------|
| Migration executes | ✅ PASS | No errors |
| Mandato PDF generates | ✅ PASS | All clauses present |
| Arrendamiento PDF generates | ✅ PASS | All 25 clauses present |
| Paz y Salvo generates | ✅ PASS | No regression |

## Troubleshooting

### Issue: Migration fails with "column already exists"
**Solution**: Columns were already added. Verify with `\d` command.

### Issue: PDF still fails after migration
**Solution**: Check application logs for other errors. The column should now exist.

### Issue: Paz y Salvo fails after fix
**Solution**: This indicates a regression. Check `certificado_template.py` and `servicio_contratos.py` for unintended changes.

## Rollback (if needed)

```sql
-- Remove added columns and constraints
ALTER TABLE CONTRATOS_MANDATOS DROP CONSTRAINT IF EXISTS fk_mandatos_responsable_deposito;
ALTER TABLE CONTRATOS_MANDATOS DROP COLUMN IF EXISTS RESPONSABLE_DEPOSITO_ID;
ALTER TABLE CONTRATOS_MANDATOS DROP COLUMN IF EXISTS ENLACE_VIDEO;

ALTER TABLE CONTRATOS_ARRENDAMIENTOS DROP CONSTRAINT IF EXISTS fk_arrendamientos_responsable_deposito;
ALTER TABLE CONTRATOS_ARRENDAMIENTOS DROP COLUMN IF EXISTS RESPONSABLE_DEPOSITO_ID;
ALTER TABLE CONTRATOS_ARRENDAMIENTOS DROP COLUMN IF EXISTS ENLACE_VIDEO;
```
