# Implementation Plan: Reporte de Liquidaciones - Datos del Propietario y Contrato de Mandato

**Branch**: `054-reporte-liquidaciones-datos-propietario` | **Date**: 2026-07-13 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/054-reporte-liquidaciones-datos-propietario/spec.md`

## Summary

Ampliar el Reporte de Liquidaciones con 7 nuevas columnas: 2 de datos del propietario (NUMERO_DOCUMENTO_PROPIETARIO, TELEFONO_PROPIETARIO) y 5 de información bancaria del Contrato de Mandato (BANCO, NUMERO_CUENTA, TIPO_CUENTA, NOMBRE_CONSIGNATARIO, DOCUMENTO_CONSIGNATARIO). La implementación requiere modificar la consulta SQL en el repositorio, propagar los cambios a través de la capa de servicios y estado, y verificar la exportación CSV.

## Technical Context

**Language/Version**: Python 3.11+

**Primary Dependencies**: Reflex (UI framework), psycopg2 (PostgreSQL driver), Pydantic (DTOs)

**Storage**: PostgreSQL (dual SQLite/PostgreSQL via DatabaseManager)

**Testing**: pytest

**Target Platform**: Linux server (Railway deployment)

**Project Type**: web application (Reflex full-stack)

**Performance Goals**: No more than 10% increase in report generation time

**Constraints**: Clean Architecture (Dominio → Aplicación → Infraestructura → Presentación), PostgreSQL native queries only, 100% Spanish codebase

**Scale/Scope**: Medium-sized real estate management application, ~50 existing specs

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| Clean Architecture layers | PASS | Changes in repositorio → servicio → state → page (unidirectional) |
| PostgreSQL native queries | PASS | Using `%s` placeholders, raw SQL with psycopg2 |
| 100% Spanish | PASS | All new code/comments will be in Spanish |
| snake_case naming | PASS | Column aliases follow existing pattern |
| Type Hints | PASS | All function signatures will include type hints |
| No SQLite in new code | PASS | Only modifying PostgreSQL queries |
| Atomic changes | PASS | Changes isolated to report module |
| Contract-First | PASS | Interface defined before implementation |

**Gate Result**: PASS - No violations detected.

## Project Structure

### Documentation (this feature)

```text
specs/054-reporte-liquidaciones-datos-propietario/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   └── report-liquidaciones.md
└── tasks.md             # Phase 2 output (not created by /speckit-plan)
```

### Source Code (repository root)

```text
src/
├── dominio/entidades/           # Entity definitions (no changes needed)
│   ├── liquidacion.py
│   ├── contrato_mandato.py      # Already has banking fields
│   ├── propietario.py
│   └── persona.py               # Already has telefono_principal
├── aplicacion/servicios/
│   └── servicio_reportes.py     # MODIFY: Pass through new columns
├── infraestructura/persistencia/
│   └── repositorio_reportes.py  # MODIFY: Add 7 columns to SQL query
└── presentacion_reflex/
    ├── state/
    │   └── reportes_state.py    # MODIFY: Add sanitization for new columns
    └── pages/
        └── reportes.py          # NO CHANGE: Dynamic column rendering
```

**Structure Decision**: Existing Clean Architecture structure maintained. Changes flow through: repositorio_reportes.py → servicio_reportes.py → reportes_state.py. The UI page (reportes.py) requires NO changes because it dynamically renders columns from the data dictionary keys.

## Complexity Tracking

No violations requiring justification. All changes follow existing patterns.
