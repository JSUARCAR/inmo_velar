# Implementation Plan: Fix Edit Liquidación Incidents Loading

**Branch**: `[041-fix-edit-liquidacion-incidents]` | **Date**: 2026-07-10 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/041-fix-edit-liquidacion-incidents/spec.md`

## Summary

The Edit Liquidación modal does not display associated incidents or observations when opened. Root cause analysis reveals two distinct issues:

1. **Incidents field**: The modal only shows a numeric total (`valor_incidentes`), not the list of individual associated incidents. The "Seleccionar Incidentes" button only opens a modal to ADD new incidents, not to VIEW existing ones.
2. **Observations field**: The `observaciones` data IS being loaded into `form_data`, but may not render correctly due to component initialization timing.

The fix requires: (a) adding a read-only display of associated incidents in the edit modal, and (b) verifying the observations field renders correctly.

## Technical Context

**Language/Version**: Python 3.11+

**Primary Dependencies**: Reflex >= 0.6.0 (Radix UI primitives), Pydantic >= 2.5.0

**Storage**: PostgreSQL (production) / SQLite (dev) — no ORM, raw SQL via `DatabaseManager` singleton

**Testing**: Manual testing via Playwright + production validation

**Target Platform**: Web (Linux server, Railway deployment)

**Project Type**: Web application (Reflex full-stack Python)

**Performance Goals**: < 2 seconds modal load time

**Constraints**: No database schema changes. No changes to persistence layer (Out of Scope per spec clarification). Frontend-only fix.

**Scale/Scope**: Single modal component + state handler modification

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

No constitution file found. Skipping gate evaluation.

## Project Structure

### Documentation (this feature)

```text
specs/041-fix-edit-liquidacion-incidents/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
└── tasks.md             # Phase 2 output (NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
src/
├── dominio/
│   └── entidades/
│       ├── liquidacion.py
│       ├── incidente.py
│       └── incidente_liquidacion.py
├── infraestructura/
│   └── persistencia/
│       ├── repositorio_liquidacion_postgres.py
│       ├── repositorio_incidentes_postgres.py
│       └── repositorio_incidente_liq_postgres.py
├── aplicacion/
│   └── servicios/
│       ├── servicio_financiero.py
│       └── servicio_incidente_liquidacion.py
└── presentacion_reflex/
    ├── state/
    │   └── liquidaciones_state.py
    ├── components/
    │   └── liquidaciones/
    │       ├── liquidacion_edit_form.py
    │       └── modal_seleccion_incidentes.py
    └── pages/
        └── liquidaciones.py
```

**Structure Decision**: Existing project structure. Modifications target only:
- `src/presentacion_reflex/components/liquidaciones/liquidacion_edit_form.py` — Add incidents display
- `src/presentacion_reflex/state/liquidaciones_state.py` — Add state var + event handler for loading associated incidents

## Complexity Tracking

No constitution violations. No complexity justifications needed.
