# Quickstart: Validación del Reporte de Liquidaciones Ampliado

**Date**: 2026-07-13

## Prerequisites

1. PostgreSQL database running with test data
2. Python environment with dependencies installed
3. Reflex development server available

## Validation Scenarios

### Scenario 1: Verificar columnas nuevas en el reporte

**Steps**:
1. Start the application: `reflex run --env dev`
2. Navigate to `/reportes`
3. Select "Reporte de Liquidaciones" from the report type dropdown
4. Click "Generar Reporte"

**Expected Outcome**:
- Table displays 35 columns (was 28)
- New columns appear in positions 5-11 after Nombre_Propietario:
  - NUMERO_DOCUMENTO_PROPIETARIO
  - TELEFONO_PROPIETARIO
  - BANCO
  - NUMERO_CUENTA
  - TIPO_CUENTA
  - NOMBRE_CONSIGNATARIO
  - DOCUMENTO_CONSIGNATARIO

### Scenario 2: Validar datos del propietario

**Steps**:
1. In the report, locate a row with a known owner
2. Compare NUMERO_DOCUMENTO_PROPIETARIO with the value in PERSONAS.NUMERO_DOCUMENTO
3. Compare TELEFONO_PROPIETARIO with PERSONAS.TELEFONO_PRINCIPAL

**Expected Outcome**:
- Values match exactly between report and database
- Empty fields show empty string (not "N/A" or null)

### Scenario 3: Validar datos bancarios del contrato

**Steps**:
1. In the report, locate a row with a known contract
2. Compare banking columns with CONTRATOS_MANDATOS table:
   - BANCO = cm.BANCO_PROPIETARIO
   - NUMERO_CUENTA = cm.NUMERO_CUENTA_PROPIETARIO
   - TIPO_CUENTA = cm.TIPO_CUENTA
   - NOMBRE_CONSIGNATARIO = cm.CONSIGNATARIO
   - DOCUMENTO_CONSIGNATARIO = cm.DOCUMENTO_CONSIGNATARIO

**Expected Outcome**:
- All banking values match the contract associated with the liquidation
- Historical contracts show their own banking data, not the current contract

### Scenario 4: Exportación CSV

**Steps**:
1. Generate the report
2. Click "Exportar CSV"
3. Open the downloaded CSV file in Excel

**Expected Outcome**:
- CSV contains all 35 columns
- Banking numbers (NUMERO_CUENTA) preserve leading zeros
- Document numbers (NUMERO_DOCUMENTO_PROPIETARIO) display correctly
- No truncation or data loss

### Scenario 5: Filtros y búsqueda

**Steps**:
1. Generate the report
2. Use the search box to filter by owner name
3. Use the Asesor dropdown to filter by advisor

**Expected Outcome**:
- New columns appear in filtered results
- Search works across all columns including new ones
- Pagination maintains correct column order

### Scenario 6: Datos incompletos

**Steps**:
1. Identify a contract with missing banking info (NULL values)
2. Generate the report

**Expected Outcome**:
- Missing banking fields show empty string
- No errors or exceptions thrown
- Report generates successfully

## Validation Commands

```bash
# Run syntax check
python -m py_compile src/infraestructura/persistencia/repositorio_reportes.py
python -m py_compile src/aplicacion/servicios/servicio_reportes.py
python -m py_compile src/presentacion_reflex/state/reportes_state.py

# Run linting
ruff check src/infraestructura/persistencia/repositorio_reportes.py
ruff check src/aplicacion/servicios/servicio_reportes.py
ruff check src/presentacion_reflex/state/reportes_state.py

# Run type checking
mypy src/infraestructura/persistencia/repositorio_reportes.py
mypy src/aplicacion/servicios/servicio_reportes.py

# Start development server
reflex run --env dev
```

## Success Criteria Checklist

- [ ] Report displays 35 columns (7 new + 28 existing)
- [ ] New owner columns appear after Nombre_Propietario
- [ ] Banking columns appear after owner identification
- [ ] All values match PostgreSQL data exactly
- [ ] CSV export preserves all columns
- [ ] Banking numbers don't truncate in Excel
- [ ] Empty fields show empty string
- [ ] Filters work with new columns
- [ ] No regressions in other reports
- [ ] Performance within 10% of baseline
