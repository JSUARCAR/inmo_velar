# Implementation Plan: Disponibilidad de Acciones por Estado - Liquidacion Asesores

**Branch**: `038-liquidacion-asesores-actions` | **Date**: 2026-07-08 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/038-liquidacion-asesores-actions/spec.md`

## Summary

Implementar lógica de disponibilidad de acciones basada en estado para el módulo Liquidacion Asesores. Acción Eliminar solo para Pendiente (soft delete), acción Reversar solo para estados diferentes de Pendiente (Aprobada→Pendiente, Pagada→Aprobada, Anulada→Pendiente). Validación en frontend, backend y base de datos.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: Reflex (v0.6.x), Pydantic, psycopg2
**Storage**: SQLite (actual) / PostgreSQL (producción)
**Testing**: pytest
**Target Platform**: Web (Reflex frontend + FastAPI backend)
**Project Type**: Web application (full-stack)
**Performance Goals**: < 2 segundos respuesta UI
**Constraints**: Soft delete, integridad referencial, auditoría
**Scale/Scope**: ~100-500 liquidaciones/mes

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| Clean Architecture (Dominio→Aplicación→Infraestructura→Presentación) | ✅ PASS | Métodos nuevos seguirán esta capa |
| snake_case variables/funciones | ✅ PASS | Convención existente |
| Type Hints obligatorios | ✅ PASS | Ya implementado en codebase |
| PostgreSQL (no SQLite en producción) | ⚠️ INFO | Repo actual usa SQLite; producción será PostgreSQL |
| Zero deferred cleanup | ✅ PASS | Cambios atómicos |
| Spec-Driven Development | ✅ PASS | Feature spec completa |

**Gate Result**: PASS - No violations requiring justification.

## Project Structure

### Documentation (this feature)

```text
specs/038-liquidacion-asesores-actions/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   └── service-contracts.md
└── tasks.md             # Phase 2 output (/speckit.tasks)
```

### Source Code (repository root)

```text
src/
├── dominio/entidades/
│   └── liquidacion_asesor.py          # Entity (add reverse methods)
├── aplicacion/servicios/
│   └── servicio_liquidacion_asesores.py # Service (add eliminar/reversar)
├── infraestructura/repositorios/
│   └── repositorio_liquidacion_asesor.py # Repository (add eliminar/reversar SQL)
└── presentacion_reflex/
    ├── state/liquidacion_asesores/
    │   └── form_state.py              # State (add action handlers)
    └── pages/
        └── liquidacion_asesores.py    # Page (add action buttons)
```

**Structure Decision**: Proyecto existente con arquitectura en capas. Cambios en las 4 capas (dominio, aplicación, infraestructura, presentación).

## Complexity Tracking

> No constitution violations requiring justification.
