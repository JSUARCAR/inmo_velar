# Implementation Plan: Auditoría de Propagación de Renovaciones

**Branch**: `062-audit-renewal-propagation` | **Date**: 2026-07-22 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/062-audit-renewal-propagation/spec.md`

## Summary

Script Python de solo lectura que audita contratos de arrendamiento renovados en julio 2026, identificando inconsistencias en la propagación del canon hacia Liquidación de Propietarios y Recaudos. El script genera un informe JSON con métricas, detalles de inconsistencias, análisis de código fuente y recomendaciones técnicas. Incluye análisis estático de archivos Python para identificar fallas de diseño en la cascada de sincronización.

## Technical Context

**Language/Version**: Python 3.11+

**Primary Dependencies**:
- `psycopg2` (PostgreSQL adapter)
- `python-dotenv` (environment variable loading)
- `json` (stdlib - JSON generation)
- `datetime` (stdlib - timestamp handling)
- `pathlib` (stdlib - filesystem paths)
- `ast` (stdlib - Python code analysis)
- `os` (stdlib - environment variables)

**Storage**: PostgreSQL (read-only queries via `DATABASE_URL`)

**Testing**: pytest (existing test framework in project)

**Target Platform**: CLI tool (cross-platform: Windows, Linux, macOS)

**Project Type**: Diagnostic CLI script

**Performance Goals**: <30 seconds execution time

**Constraints**:
- Read-only database access (no INSERT/UPDATE/DELETE)
- Must handle connection errors gracefully
- JSON output must be valid and parseable
- File output to `scripts/diagnostico/` with timestamp

**Scale/Scope**: Single script file, ~400-500 lines

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| 100% Español | ✅ PASS | All code, comments, variables in Spanish |
| Clean Architecture | ✅ PASS | Script is standalone diagnostic tool, no architecture violations |
| PostgreSQL Native | ✅ PASS | Uses psycopg2 with %s placeholders |
| Type Hints | ✅ PASS | All function signatures will include type hints |
| Docstrings Google Style | ✅ PASS | All functions will have proper docstrings |
| Zero Guessing | ✅ PASS | All requirements clarified in spec |
| Spec-Driven Development | ✅ PASS | Implementation follows spec exactly |

**Gate Result**: ✅ PASS - No violations detected

## Project Structure

### Documentation (this feature)

```text
specs/062-audit-renewal-propagation/
├── spec.md              # Feature specification (Clarified)
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
└── tasks.md             # Phase 2 output
```

### Source Code (repository root)

```text
scripts/diagnostico/
└── audit_renovaciones_2026.py    # Main audit script (NEW)

tests/verification/
└── test_audit_renovaciones.py    # Validation tests (NEW)
```

**Structure Decision**: Single diagnostic script in `scripts/diagnostico/` following existing audit script patterns (reference: `tests/verification/audit_sincronizacion.py`).

## Complexity Tracking

> No constitution violations detected. No complexity justifications needed.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| N/A | N/A | N/A |

## Research Tasks (Phase 0)

### NEEDS CLARIFICATION Resolved

All requirements clarified in spec via `/speckit.clarify`:
- D1: Temporal scope = from today forward
- D2: Filesystem access included for code analysis
- D3: JSON structure flexible
- D4: Output to local file in `scripts/diagnostico/`
- D5: Only last renovation per contract

### Technology Research

1. **PostgreSQL Query Patterns**: Use existing repository patterns from `src/infraestructura/persistencia/`
2. **Python AST Analysis**: Use `ast` module for static code analysis
3. **JSON Schema Design**: Follow existing audit script patterns
4. **Error Handling**: Use domain-specific exceptions per constitution

## Phase 1: Design & Contracts

### Data Model

See `data-model.md` for complete entity definitions.

Key entities:
- `RenovacionJulio2026`: Renovation records from July 2026
- `InconsistenciaCanon`: Canon discrepancies found
- `FallaDiseno`: Design flaws identified in code
- `InformeAuditoria`: Complete audit report

### Interface Contracts

See `contracts/` directory for:
- SQL query contracts (read-only)
- JSON output schema
- File output contract

### Quickstart Validation

See `quickstart.md` for:
- Prerequisites and setup
- Test scenarios
- Expected outcomes

## Implementation Tasks

### Task 1: Create Audit Script Structure
- Create `scripts/diagnostico/audit_renovaciones_2026.py`
- Add docstrings, type hints, imports
- Implement main function skeleton

### Task 2: Database Connection Module
- Implement PostgreSQL connection using `DATABASE_URL`
- Add connection error handling
- Implement query execution wrapper (read-only)

### Task 3: Renovation Query Module
- Query `RENOVACIONES_CONTRATOS` for July 2026
- Filter to last renovation per contract
- Join with `CONTRATOS_ARRENDAMIENTOS` for current canon

### Task 4: Liquidacion Comparison Module
- Query `LIQUIDACIONES` for future periods
- Compare `canon_bruto` against contract canon
- Identify discrepancies

### Task 5: Recaudo Comparison Module
- Query `RECAUDOS` and `RECAUDO_CONCEPTOS` for future periods
- Compare `valor` against contract canon
- Identify discrepancies

### Task 6: Mandato/Propiedad Sync Module
- Query `CONTRATOS_MANDATO` and `PROPIEDADES`
- Compare canon values across entities
- Identify sync failures

### Task 7: Historical Preservation Check
- Query liquidaciones/recaudos before July 2026
- Verify no modifications detected
- Flag any retroactive changes

### Task 8: Code Analysis Module
- Implement Python AST parser for source files
- Analyze `servicio_contrato_arrendamiento.py`
- Analyze `servicio_financiero.py`
- Analyze `servicio_recaudo.py`
- Identify design flaws in cascade sync

### Task 9: Report Generation Module
- Build JSON structure with all required sections
- Include metadata, summary, inconsistencies, code analysis, recommendations
- Validate JSON output

### Task 10: File Output Module
- Create output directory if not exists
- Generate timestamped filename
- Write JSON file with proper encoding

### Task 11: Integration & Testing
- Integrate all modules
- Test against staging database
- Validate all success criteria

## Critical Path

1. Task 1 → Task 2 → Task 3 → Task 4/5 → Task 9 → Task 10 → Task 11
2. Task 8 can run in parallel with Tasks 3-7

## Estimated Effort

- Total: ~4-6 hours
- Critical path: ~3-4 hours
- Testing: ~1-2 hours
