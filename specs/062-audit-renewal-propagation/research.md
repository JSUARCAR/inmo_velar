# Research: Auditoría de Propagación de Renovaciones

**Feature**: 062-audit-renewal-propagation
**Date**: 2026-07-22
**Status**: Complete

## Research Tasks Completed

### 1. PostgreSQL Query Patterns

**Decision**: Use raw SQL with psycopg2 following existing repository patterns

**Rationale**:
- Existing repositories use raw SQL with `%s` placeholders (constitution requirement)
- No ORM needed for read-only diagnostic queries
- Direct SQL allows precise control over query optimization

**Alternatives Considered**:
- SQLAlchemy: Rejected - adds unnecessary complexity for read-only queries
- Dataset library: Rejected - not used in existing codebase

**Reference Files**:
- `src/infraestructura/persistencia/repositorio_renovacion_postgres.py`
- `src/infraestructura/persistencia/repositorio_liquidacion_postgres.py`
- `src/infraestructura/persistencia/repositorio_recaudo.py`

### 2. Python AST Analysis

**Decision**: Use `ast` module for static code analysis

**Rationale**:
- Built-in Python module, no external dependencies
- Can parse and analyze Python source code without execution
- Allows identifying function definitions, imports, and code patterns

**Alternatives Considered**:
- `pylint` AST: Rejected - too heavy for targeted analysis
- `black` parser: Rejected - formatting focused, not analysis
- Manual regex: Rejected - fragile and error-prone

**Implementation Pattern**:
```python
import ast
from pathlib import Path

def analyze_python_file(filepath: Path) -> dict:
    """Analyze Python file for design flaws."""
    with open(filepath, 'r', encoding='utf-8') as f:
        tree = ast.parse(f.read())
    # Extract function definitions, imports, etc.
```

### 3. JSON Schema Design

**Decision**: Flexible schema with required fields from FR-010 to FR-014

**Rationale**:
- User chose "Dejar flexible" in clarification D3
- Implementer designs structure based on requirements
- Must include all mandatory fields from functional requirements

**Required Sections**:
1. `metadata` (FR-010): fecha_ejecucion, duracion_segundos, total_procesado
2. `resumen_ejecutivo` (FR-011): total_renovaciones, inconsistencias_encontradas, estado_sincronizacion
3. `inconsistencias` (FR-012): Array of inconsistency objects with causa_raiz
4. `analisis_codigo` (FR-013): Array of code flaws with file, line, description
5. `recomendaciones` (FR-014): Array of prioritized recommendations

**Optional Sections**:
- `contratos_procesados`: List of all contracts audited
- `historial_verificacion`: Historical preservation check results

### 4. Error Handling Patterns

**Decision**: Use domain-specific exceptions per constitution

**Rationale**:
- Constitution §2.2 requires domain-specific exceptions
- Prohibits generic `except Exception as e:` usage
- Must capture and report errors in JSON output

**Implementation Pattern**:
```python
class ErrorConexionBD(Exception):
    """Error de conexión a la base de datos."""
    pass

class ErrorConsultaSQL(Exception):
    """Error en la ejecución de consulta SQL."""
    pass

class ErrorAccesoArchivo(Exception):
    """Error de acceso a archivos del proyecto."""
    pass
```

### 5. File Output Strategy

**Decision**: Save to `scripts/diagnostico/` with timestamp filename

**Rationale**:
- User chose "Archivo local" in clarification D4
- Centralizes diagnostics in one location
- Timestamp ensures unique filenames

**Filename Pattern**:
```
audit_renovaciones_YYYYMMDD_HHMMSS.json
```

**Example**:
```
scripts/diagnostico/audit_renovaciones_20260722_143025.json
```

### 6. Renovation Filtering Strategy

**Decision**: Only audit last renovation per contract in July 2026

**Rationale**:
- User chose "Solo última" in clarification D5
- Focuses on current state, not historical reconstruction
- Simplifies query logic and reduces processing time

**SQL Pattern**:
```sql
WITH ultimas_renovaciones AS (
    SELECT 
        contrato_id,
        MAX(fecha_renovacion) as fecha_ultima_renovacion
    FROM RENOVACIONES_CONTRATOS
    WHERE fecha_renovacion >= '2026-07-01'
      AND fecha_renovacion < '2026-08-01'
    GROUP BY contrato_id
)
SELECT * FROM ultimas_renovaciones
```

### 7. Temporal Comparison Strategy

**Decision**: Compare against periods from today forward

**Rationale**:
- User chose "Relativo a hoy" in clarification D1
- Identifies active inconsistencies affecting current operations
- Not just historical analysis

**SQL Pattern**:
```sql
-- Liquidaciones from today forward
SELECT * FROM LIQUIDACIONES
WHERE fecha >= CURRENT_DATE
  AND contrato_id = %s

-- Recaudos from today forward
SELECT * FROM RECAUDOS
WHERE fecha >= CURRENT_DATE
  AND contrato_id = %s
```

### 8. Code Analysis Target Files

**Decision**: Analyze these specific files for design flaws

**Rationale**:
- These files contain the cascade synchronization logic
- Root causes identified in code analysis phase

**Target Files**:
1. `src/aplicacion/servicios/servicio_contrato_arrendamiento.py`
   - Lines 278-467: Cascade sync logic
   - Line 394+: Renovation handling
   - Issue: Only updates Mandato + Propiedad, not Liquidaciones/Recaudos

2. `src/aplicacion/servicios/servicio_financiero.py`
   - Lines 156-264: Liquidacion generation
   - Line 174: Uses `contrato.canon_mandato`
   - Issue: No awareness of renovation history

3. `src/aplicacion/servicios/servicio_recaudo.py`
   - Lines 493-612: Recaudo generation
   - Line 554: Uses `contrato["CANON_ARRENDAMIENTO"]`
   - Issue: Reads current value, no historical tracking

4. `src/dominio/entidades/renovacion_contrato.py`
   - Has `fecha_inicio_renovacion` field
   - Issue: Field exists but is never used in update logic

## Research Summary

| Area | Decision | Confidence |
|------|----------|------------|
| Database Access | Raw SQL with psycopg2 | HIGH |
| Code Analysis | Python ast module | HIGH |
| JSON Schema | Flexible with required fields | HIGH |
| Error Handling | Domain-specific exceptions | HIGH |
| File Output | Local file with timestamp | HIGH |
| Renovation Filter | Last renovation only | HIGH |
| Temporal Scope | From today forward | HIGH |
| Target Files | 4 specific files identified | HIGH |

## Open Questions

None - all requirements clarified in spec.

## Next Steps

1. Proceed to Phase 1: Design & Contracts
2. Generate data-model.md
3. Generate contracts/
4. Generate quickstart.md
