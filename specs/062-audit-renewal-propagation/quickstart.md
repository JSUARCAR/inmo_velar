# Quickstart Validation Guide: Auditoría de Propagación de Renovaciones

**Feature**: 062-audit-renewal-propagation
**Date**: 2026-07-22
**Status**: Complete

## Overview

This guide provides runnable validation scenarios to prove the audit script works end-to-end.

## Prerequisites

### Environment Setup

1. **Python 3.11+** installed
2. **PostgreSQL** accessible via `DATABASE_URL` environment variable
3. **Dependencies** installed:
   ```bash
   pip install psycopg2-binary python-dotenv
   ```

4. **Project structure**:
   ```
   scripts/diagnostico/
   └── audit_renovaciones_2026.py
   ```

### Database Requirements

- Table `RENOVACIONES_CONTRATOS` with July 2026 data
- Table `CONTRATOS_ARRENDAMIENTOS` with active contracts
- Table `LIQUIDACIONES` with future periods
- Table `RECAUDOS` with future periods
- Table `RECAUDO_CONCEPTOS` with concept details

## Validation Scenarios

### Scenario 1: Successful Execution (Happy Path)

**Purpose**: Verify script executes without errors and generates valid JSON.

**Setup**:
```bash
# Set database URL
export DATABASE_URL="postgresql://user:password@host:5432/dbname"

# Navigate to project root
cd /path/to/PYTHON-REFLEX
```

**Command**:
```bash
python scripts/diagnostico/audit_renovaciones_2026.py
```

**Expected Outcome**:
- Script completes in < 30 seconds
- JSON file created in `scripts/diagnostico/` with timestamp
- Output shows: "Informe generado: scripts/diagnostico/audit_renovaciones_20260722_143025.json"

**Validation**:
```bash
# Check file exists
ls -la scripts/diagnostico/audit_renovaciones_2026*.json

# Validate JSON
python -c "import json; json.load(open('scripts/diagnostico/audit_renovaciones_20260722_143025.json'))"
```

### Scenario 2: Inconsistencies Found

**Purpose**: Verify script identifies canon discrepancies.

**Setup**:
- Database has at least 1 contract renovated in July 2026
- Liquidacion exists with canon different from contract canon

**Command**:
```bash
python scripts/diagnostico/audit_renovaciones_2026.py
```

**Expected Outcome**:
- JSON contains `inconsistencias` array with at least 1 entry
- Each inconsistency has `causa_raiz` field populated
- `resumen_ejecutivo.inconsistencias_encontradas` > 0

**Validation**:
```bash
# Check inconsistencies
python -c "
import json
with open('scripts/diagnostico/audit_renovaciones_20260722_143025.json') as f:
    data = json.load(f)
    print(f\"Inconsistencias: {data['resumen_ejecutivo']['inconsistencias_encontradas']}\")
    for inc in data['inconsistencias']:
        print(f\"  - {inc['contrato_codigo']}: {inc['causa_raiz']}\")
"
```

### Scenario 3: Code Analysis

**Purpose**: Verify script analyzes Python source files and identifies design flaws.

**Setup**:
- Source files exist in `src/aplicacion/servicios/`
- Files contain cascade synchronization logic

**Command**:
```bash
python scripts/diagnostico/audit_renovaciones_2026.py
```

**Expected Outcome**:
- JSON contains `analisis_codigo` array with at least 3 entries
- Each entry has `archivo`, `linea_inicio`, `problema`, `recomendacion`
- `metadata.total_fallas_diseno` >= 3

**Validation**:
```bash
# Check code analysis
python -c "
import json
with open('scripts/diagnostico/audit_renovaciones_20260722_143025.json') as f:
    data = json.load(f)
    print(f\"Fallas de diseño: {data['metadata']['total_fallas_diseno']}\")
    for falla in data['analisis_codigo']:
        print(f\"  - {falla['archivo']}:{falla['linea_inicio']}: {falla['problema']}\")
"
```

### Scenario 4: No Renovations Found

**Purpose**: Script handles empty result gracefully.

**Setup**:
- Database has no renovations in July 2026

**Command**:
```bash
python scripts/diagnostico/audit_renovaciones_2026.py
```

**Expected Outcome**:
- Script completes successfully
- JSON generated with `metadata.total_renovaciones` = 0
- `resumen_ejecutivo.estado_sincronizacion` = "OK"

**Validation**:
```bash
# Check empty result
python -c "
import json
with open('scripts/diagnostico/audit_renovaciones_20260722_143025.json') as f:
    data = json.load(f)
    assert data['metadata']['total_renovaciones'] == 0
    print('Empty result handled correctly')
"
```

### Scenario 5: Database Connection Error

**Purpose**: Script handles connection failure gracefully.

**Setup**:
```bash
# Set invalid database URL
export DATABASE_URL="postgresql://invalid:invalid@invalid:5432/invalid"
```

**Command**:
```bash
python scripts/diagnostico/audit_renovaciones_2026.py
```

**Expected Outcome**:
- Script does not crash
- Error JSON generated with `error.tipo` = "ERROR_CONEXION_BD"
- Error message is descriptive

**Validation**:
```bash
# Check error handling
python -c "
import json
with open('scripts/diagnostico/audit_renovaciones_20260722_143025.json') as f:
    data = json.load(f)
    assert 'error' in data
    print(f\"Error captured: {data['error']['tipo']}\")
"
```

### Scenario 6: Historical Preservation Check

**Purpose**: Verify script checks historical records are unmodified.

**Setup**:
- Database has liquidaciones/recaudos before July 2026
- No modifications to historical records

**Command**:
```bash
python scripts/diagnostico/audit_renovaciones_2026.py
```

**Expected Outcome**:
- JSON contains `historial_verificacion`
- `integridad` = "PRESERVADA"
- `liquidaciones_modificadas` = 0
- `recaudos_modificados` = 0

**Validation**:
```bash
# Check historical preservation
python -c "
import json
with open('scripts/diagnostico/audit_renovaciones_20260722_143025.json') as f:
    data = json.load(f)
    hist = data['historial_verificacion']
    assert hist['integridad'] == 'PRESERVADA'
    print('Historical records preserved')
"
```

## Automated Test Suite

Run all validation scenarios:

```bash
# Run pytest suite
pytest tests/verification/test_audit_renovaciones.py -v

# Run specific scenario
pytest tests/verification/test_audit_renovaciones.py::test_successful_execution -v
```

## Success Criteria Verification

| SC | Criterion | How to Verify |
|----|-----------|---------------|
| SC-001 | 100% renovations identified | Check `metadata.total_renovaciones` matches DB count |
| SC-002 | JSON generated in < 30s | Measure execution time |
| SC-003 | 100% inconsistencies have causa_raiz | Validate all inconsistency objects |
| SC-004 | >= 3 code flaws identified | Check `metadata.total_fallas_diseno` |
| SC-005 | Recommendations provided | Check `recomendaciones` array |
| SC-006 | Accurate data | Cross-reference with manual DB queries |
| SC-007 | No errors in staging | Run in staging environment |
| SC-008 | Valid JSON | Parse with `json.loads()` |
| SC-009 | File saved to correct location | Check `scripts/diagnostico/` |
| SC-010 | Multiple renovations handled | Verify only last used |

## Troubleshooting

### Common Issues

1. **ModuleNotFoundError**: Install dependencies with `pip install psycopg2-binary python-dotenv`

2. **Connection refused**: Verify `DATABASE_URL` is correct and PostgreSQL is running

3. **Table not found**: Check table names match exactly (case-sensitive)

4. **Permission denied**: Ensure database user has SELECT permissions on all tables

5. **Timeout**: Check network latency, may need to increase timeout in script

## Performance Benchmarks

| Metric | Target | Acceptable |
|--------|--------|------------|
| Total execution | < 30s | < 60s |
| DB queries | < 10s | < 20s |
| Code analysis | < 5s | < 10s |
| JSON generation | < 1s | < 2s |
| File write | < 1s | < 2s |
