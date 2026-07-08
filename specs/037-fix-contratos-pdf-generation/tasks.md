# Tasks: Fix Contratos PDF Generation

**Feature**: Fix PDF generation errors in the Contratos module
**ID**: 037-fix-contratos-pdf-generation
**Date**: 2026-07-08
**Spec**: [spec.md](./spec.md)
**Plan**: [plan.md](./plan.md)

---

## Task Summary

| Phase | Tasks | Description |
|-------|-------|-------------|
| Phase 1: Setup | 1 | Update migration SQL |
| Phase 2: Foundation | 1 | Execute migration against database |
| Phase 3: Error Handling | 1 | Implement friendly error messages |
| Phase 4: Verification | 3 | Manual testing (Mandato + Arrendamiento + Paz y Salvo) |
| **Total** | **6** | |

---

## Phase 1: Setup

**Goal**: Prepare the migration script with the missing column for CONTRATOS_ARRENDAMIENTOS.

- [x] T001 Update migration file to add `RESPONSABLE_DEPOSITO_ID INTEGER` column and foreign key constraint to `CONTRATOS_ARRENDAMIENTOS` table in `src/infraestructura/db/migrations/migration_campos_extra_contratos.sql`

---

## Phase 2: Foundation

**Goal**: Apply database schema changes required for PDF generation queries.

- [x] T002 Execute updated migration against PostgreSQL database to create `RESPONSABLE_DEPOSITO_ID` column in both `CONTRATOS_MANDATOS` and `CONTRATOS_ARRENDAMIENTOS` tables with foreign key to `ASESORES`

---

## Phase 3: Error Handling

**Goal**: Improve user experience when PDF generation fails by showing friendly messages instead of raw PostgreSQL errors.

- [x] T003 Implement try/except error handling in `src/presentacion_reflex/state/pdf_state.py` for `generar_contrato_mandato_elite()` and `generar_contrato_arrendamiento_elite()` methods to catch exceptions, log technical details, and display user-friendly toast messages

---

## Phase 4: Verification

**Goal**: Validate that all PDF generation types work correctly after the fix.

- [x] T004 Verify Mandato PDF generation by navigating to Contratos module, selecting a Mandato contract, clicking "Contrato Oficial", and confirming PDF downloads with all legal clauses
- [x] T005 Verify Arrendamiento PDF generation by navigating to Contratos module, selecting an Arrendamiento contract, clicking "Contrato Oficial", and confirming PDF downloads with all 25 legal clauses
- [x] T006 Verify Paz y Salvo regression by navigating to Contratos module, selecting an inactive contract, clicking "Generar Paz y Salvo", and confirming certificate downloads with correct data

---

## Dependencies

```
T001 (Setup migration)
  ↓
T002 (Execute migration)
  ↓
T003 (Error handling)
  ↓
T004 + T005 + T006 (Verification - can run in parallel)
```

---

## Parallel Execution Examples

**Verification Phase (T004, T005, T006)**:
These three tasks are independent and can be executed in parallel by different team members or in quick succession:
- T004: Test Mandato PDF
- T005: Test Arrendamiento PDF
- T006: Test Paz y Salvo

---

## Implementation Strategy

### MVP Scope
**T001 + T002**: Update and execute migration (resolves root cause)

### Full Scope
All 6 tasks including error handling and verification

### Rollback Plan
If migration causes issues, execute rollback SQL:
```sql
ALTER TABLE CONTRATOS_MANDATOS DROP CONSTRAINT IF EXISTS fk_mandatos_responsable_deposito;
ALTER TABLE CONTRATOS_MANDATOS DROP COLUMN IF EXISTS RESPONSABLE_DEPOSITO_ID;
ALTER TABLE CONTRATOS_MANDATOS DROP COLUMN IF EXISTS ENLACE_VIDEO;
ALTER TABLE CONTRATOS_ARRENDAMIENTOS DROP CONSTRAINT IF EXISTS fk_arrendamientos_responsable_deposito;
ALTER TABLE CONTRATOS_ARRENDAMIENTOS DROP COLUMN IF EXISTS RESPONSABLE_DEPOSITO_ID;
ALTER TABLE CONTRATOS_ARRENDAMIENTOS DROP COLUMN IF EXISTS ENLACE_VIDEO;
```

---

## Checklist Validation

- [x] All tasks have checkbox format `- [ ]`
- [x] All tasks have sequential Task IDs (T001-T006)
- [x] All tasks have file paths where applicable
- [x] Dependencies clearly defined
- [x] Parallel opportunities identified
- [x] Independent test criteria for each verification task
- [x] MVP scope defined (T001 + T002)
