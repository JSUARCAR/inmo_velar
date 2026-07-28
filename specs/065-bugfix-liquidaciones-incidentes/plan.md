# Implementation Plan: bugfix-liquidaciones-incidentes

**Branch**: `[###-bugfix-liquidaciones-incidentes]` | **Date**: 2026-07-27 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/065-bugfix-liquidaciones-incidentes/spec.md`

## Summary

This plan addresses a regression in the Liquidaciones module where associated incidents fail to render in the edit modal, and the modal to select new incidents fails to open properly. Our research isolated the issue to `KeyError` exceptions caused by PostgreSQL lowercasing unquoted identifiers which mismatched the Python dictionary keys used in `liquidaciones_state.py`. We will fix the data fetching and review the Z-index logic in Reflex.

## Technical Context

**Language/Version**: Python 3.11+ (Reflex)

**Primary Dependencies**: Reflex, psycopg2, Postgres

**Storage**: PostgreSQL

**Testing**: Manual validation via Reflex UI

**Target Platform**: Web application (Railway)

**Project Type**: Full-stack Python Web App

**Performance Goals**: N/A (UI state bugfix)

**Constraints**: Must follow Clean Architecture and avoid creating regressions in incident state.

**Scale/Scope**: Impacts all `Liquidacion` records with associated incidents.

## Constitution Check

*GATE: Passed. All architectural and aesthetic tokens align with `CLAUDE.md` and `GEMINI.md` mandates. The bugfix is surgical and directly addresses a silent regression.*

## Project Structure

### Documentation (this feature)

```text
specs/065-bugfix-liquidaciones-incidentes/
├── plan.md              # This file
├── research.md          # Diagnostics & Root Cause
├── data-model.md        # DB Entity mapping
└── quickstart.md        # QA & validation steps
```

### Source Code (repository root)

```text
src/
└── presentacion_reflex/
    ├── components/
    │   └── liquidaciones/
    │       └── modal_seleccion_incidentes.py
    └── state/
        └── liquidaciones_state.py
```

**Structure Decision**: The changes are strictly confined to the Presentation layer, specifically the State controller for liquidations and the component for the incident selection modal. No structural additions are required.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| N/A | N/A | N/A |
