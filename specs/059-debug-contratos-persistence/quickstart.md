# Quickstart Validation Guide: Contratos Persistence Fix

**Date**: 2026-07-21
**Feature**: 059-debug-contratos-persistence

## Prerequisites

- PostgreSQL database running and accessible
- Python environment with Reflex, psycopg2, pytest installed
- Existing test data (at least 1 Contrato de Mandato in the DB)

## Validation Scenarios

### Scenario 1: Mandato — Información de Pago round-trip

1. Create a new Contrato de Mandato with:
   - All required fields filled
   - Banco: "Bancolombia"
   - Numero Cuenta: "1234567890"
   - Tipo Cuenta: "Ahorros"
   - Consignatario: "Juan Perez"
   - Documento Consignatario: "1234567890"
2. Save and confirm success message
3. Open the same contract in edit mode
4. **Verify**: All 5 payment fields show the values entered in step 1
5. Modify the banco to "Davivienda" and save
6. Re-open in edit mode
7. **Verify**: Banco shows "Davivienda", all other payment fields unchanged

### Scenario 2: Mandato — Recepción de Inventario round-trip

1. Create a new Contrato de Mandato with:
   - All required fields filled
   - Enlace Video: "https://video.example.com/recibo-001"
2. Save and confirm success message
3. Open the same contract in edit mode
4. **Verify**: Enlace Video field shows the URL entered
5. Modify the URL and save
6. Re-open in edit mode
7. **Verify**: Updated URL is displayed

### Scenario 3: Mandato — Full field round-trip

1. Create a Contrato de Mandato filling EVERY field in the form
2. Save
3. Open in edit mode
4. Verify EVERY field contains the original value
5. Modify at least 3 fields across different sections
6. Save
7. Re-open and verify modifications persisted

### Scenario 4: Arrendamiento — Full field round-trip

1. Create a Contrato de Arrendamiento filling EVERY field
2. Save
3. Open in edit mode
4. Verify EVERY field contains the original value
5. Modify enlace_video and responsable_deposito
6. Save
7. Re-open and verify modifications persisted

### Scenario 5: Retroactive fix verification (after migration script)

1. Query DB: `SELECT ENLACE_VIDEO FROM CONTRATOS_MANDATOS WHERE ENLACE_VIDEO IS NOT NULL`
2. Query DB: `SELECT CONSIGNATARIO FROM CONTRATOS_MANDATOS WHERE CONSIGNATARIO IS NOT NULL`
3. Open an existing contract (created before fix) in edit mode
4. **Verify**: Previously lost fields now show correct values

### Scenario 6: Integration tests

```bash
# Run the new persistence tests
pytest tests/integration/test_servicios_aplicacion/test_persistencia_contratos.py -v

# Expected: All tests pass, confirming:
# - Create persists all fields
# - Read recovers all fields
# - Update persists all modified fields
# - Round-trip integrity for both Mandato and Arrendamiento
```

## Files to Modify

| File | Change | Lines |
|------|--------|-------|
| `src/infraestructura/persistencia/repositorio_contrato_mandato_postgres.py` | Add ENLACE_VIDEO to UPDATE SET clause | ~line 302 |
| `src/infraestructura/persistencia/repositorio_contrato_mandato_postgres.py` | Add uppercase fallback for 3 fields in _row_to_entity | ~lines 402-404 |
| `tests/integration/.../test_persistencia_contratos.py` | New integration test file | New |

## Expected Outcome

After applying fixes:
- 100% of Mandato fields persist correctly through Create/Read/Update
- 100% of Arrendamiento fields continue to persist correctly (no regression)
- All integration tests pass
- Existing contracts with lost data can be corrected via retroactive script
