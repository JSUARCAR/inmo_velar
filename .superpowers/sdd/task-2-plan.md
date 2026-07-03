# Task 2: Update Repository Mapping - Implementation Plan

## Root Cause Analysis

**Problem:** The `obtener_datos_para_pdf()` method in `repositorio_liquidacion_postgres.py` does not include `valor_incidentes` in the mapping dict returned to the frontend.

**Evidence:**
- Database column `VALOR_INCIDENTES` exists in LIQUIDACIONES table (verified: value = 70000 for liquidation #572)
- The query uses `l.*` which selects all columns including `VALOR_INCIDENTES`
- The mapping dict (lines 1192-1243) does not include this field
- Current result: `data.get('valor_incidentes')` returns `None`

**Root Cause:** The mapping was created before the `VALOR_INCIDENTES` column was added to the schema, and was never updated.

## Solution

Add `"valor_incidentes": row.get("VALOR_INCIDENTES") or 0,` to the mapping dict in `obtener_datos_para_pdf()` method, after the `"otros_egr"` line (line 1235).

## Implementation Steps

1. Edit `src/infraestructura/persistencia/repositorio_liquidacion_postgres.py`
2. Add the new mapping line after `"otros_egr": row.get("OTROS_EGRESOS") or 0,`
3. Verify import works
4. Test the method returns correct value for liquidation #572
5. Commit changes

## Verification

```bash
# Test 1: Verify import
python -c "from src.infraestructura.persistencia.repositorio_liquidacion_postgres import RepositorioLiquidacionPostgres; print('OK')"

# Test 2: Verify method returns valor_incidentes
python -c "
from src.infraestructura.persistencia.database import db_manager
from src.infraestructura.persistencia.repositorio_liquidacion_postgres import RepositorioLiquidacionPostgres
repo = RepositorioLiquidacionPostgres(db_manager)
data = repo.obtener_datos_para_pdf(572)
print('valor_incidentes:', data.get('valor_incidentes'))
"
# Expected: valor_incidentes: 70000
```

## Risk Assessment

- **Risk Level:** Low
- **Breaking Changes:** None (adding new field doesn't affect existing fields)
- **Dependencies:** None (isolated change)
