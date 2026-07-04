# Implementation Plan: Eliminar Liquidación de Propietario

**Branch**: `002-eliminar-liquidacion` | **Date**: 2026-06-30 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/002-eliminar-liquidacion/spec.md`

## Summary

Add an "Eliminar Liquidación" action to the Liquidaciones de Propietarios module that performs soft deletion of liquidations not in "Pagada" state, with confirmation dialog, audit trail, permission gating, and document orphaning. The implementation follows existing soft delete patterns (usuarios, personas, propiedades) with a new ELIMINADA boolean column, application-level audit via AUDITORIA_CAMBIOS, and a confirmation dialog with checkbox safety mechanism.

## Technical Context

**Language/Version**: Python 3.11+

**Primary Dependencies**: Reflex >=0.6.0 (UI framework), psycopg2-binary (PostgreSQL), pydantic (validation), python-dateutil

**Storage**: PostgreSQL (via `RepositorioLiquidacionPostgres`)

**Testing**: pytest, pytest-cov

**Target Platform**: Web application (Reflex SPA)

**Project Type**: web-application (Reflex full-stack)

**Performance Goals**: Single deletion completes in <2 seconds (DB transaction + audit insert)

**Constraints**: Soft delete only (no physical DELETE); must use existing AUDITORIA_CAMBIOS table; must integrate with existing permission system via AuthState.check_action()

**Scale/Scope**: Single-module feature within an existing real estate management system (~50 screens)

## Constitution Check

*No constitution file found. Skipping governance gate.*

## Project Structure

### Documentation (this feature)

```text
specs/002-eliminar-liquidacion/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   ├── ui-delete-dialog.md
│   └── service-eliminar-liquidacion.md
└── tasks.md             # Phase 2 output (/speckit.tasks)
```

### Source Code (repository root)

```text
src/
├── dominio/
│   ├── entidades/
│   │   └── liquidacion.py              # ADD eliminada: bool field
│   └── interfaces/
│       └── repositorio_liquidacion.py  # ADD eliminar() to Protocol
├── infraestructura/
│   ├── persistencia/
│   │   ├── repositorio_liquidacion_postgres.py  # ADD eliminar() method + update all queries
│   │   └── database.py                           # ADD migration for ELIMINADA column
│   └── db/migrations/
│       └── migration_add_eliminada_column.sql    # NEW: ALTER TABLE migration
├── aplicacion/
│   └── servicios/
│       └── servicio_financiero.py      # ADD eliminar_liquidacion() method
└── presentacion_reflex/
    ├── state/
    │   └── liquidaciones_state.py      # ADD delete event handlers + state vars
    ├── components/
    │   └── liquidaciones/
    │       ├── delete_confirm_dialog.py  # NEW: confirmation dialog with checkbox
    │       ├── liquidacion_detail_modal.py  # MODIFY: add Eliminar button
    │       └── __init__.py              # MODIFY: export new component
    └── pages/
        └── liquidaciones.py            # MODIFY: add button in table + import dialog

scripts/
└── add_eliminar_permission.py         # NEW: register ELIMINAR permission

tests/
├── unit/
│   └── testEliminarLiquidacion.py     # NEW: unit tests
└── integration/
    └── testEliminarLiquidacionIntegration.py  # NEW: integration tests
```

**Structure Decision**: Single project with existing Reflex architecture. Feature spans 4 layers: domain entity, repository, service, and UI state/components. Follows the exact same pattern as the existing cancelar/reversar features.

## Complexity Tracking

*No constitution violations to justify.*

## Files to Modify/Create

| File | Action | Scope |
|------|--------|-------|
| `src/dominio/entidades/liquidacion.py` | MODIFY | Add `eliminada: bool = False` field |
| `src/dominio/interfaces/repositorio_liquidacion.py` | MODIFY | Add `eliminar()` to Protocol |
| `src/infraestructura/persistencia/repositorio_liquidacion_postgres.py` | MODIFY | Add `eliminar()` method (~30 lines) + update ~12 queries to filter ELIMINADA=FALSE |
| `src/infraestructura/db/migrations/migration_add_eliminada_column.sql` | CREATE | ALTER TABLE LIQUIDACIONES ADD COLUMN ELIMINADA BOOLEAN DEFAULT FALSE |
| `src/aplicacion/servicios/servicio_financiero.py` | MODIFY | Add `eliminar_liquidacion()` method (~40 lines) |
| `src/presentacion_reflex/state/liquidaciones_state.py` | MODIFY | Add 4 event handlers + 3 state vars (~60 lines) |
| `src/presentacion_reflex/components/liquidaciones/delete_confirm_dialog.py` | CREATE | New dialog component (~100 lines) |
| `src/presentacion_reflex/components/liquidaciones/__init__.py` | MODIFY | Add export for delete_confirm_dialog |
| `src/presentacion_reflex/components/liquidaciones/liquidacion_detail_modal.py` | MODIFY | Add "Eliminar" button |
| `src/presentacion_reflex/pages/liquidaciones.py` | MODIFY | Add button in table + import dialog |
| `scripts/add_eliminar_permission.py` | CREATE | Register ELIMINAR permission |
| `tests/unit/testEliminarLiquidacion.py` | CREATE | Unit tests |
| `tests/integration/testEliminarLiquidacionIntegration.py` | CREATE | Integration tests |

## Implementation Order

1. **Database migration**: Create ELIMINADA column migration script
2. **Domain entity**: Add `eliminada` field to `Liquidacion` entity
3. **Repository interface**: Add `eliminar()` to `IRepositorioLiquidacion` Protocol
4. **Repository implementation**: Add `eliminar()` method + update all queries to filter ELIMINADA=FALSE
5. **Service layer**: Add `eliminar_liquidacion()` with validation and audit logging
6. **State management**: Add event handlers in LiquidacionesState
7. **UI Component**: Create delete_confirm_dialog with checkbox
8. **UI Integration**: Add buttons in table and detail modal
9. **Permissions**: Register ELIMINAR action
10. **Tests**: Unit + integration tests

## Risk Assessment

| Risk | Impact | Mitigation |
|------|--------|------------|
| Existing queries don't filter ELIMINADA | High | Audit all ~12 queries in repository; add ELIMINADA=FALSE to each |
| AUDITORIA_CAMBIOS trigger doesn't capture ELIMINADA changes | Medium | Use application-level audit via RepositorioAuditoria (same as personas) |
| Concurrent deletion attempts | Low | DB row-level locking via UPDATE WHERE; idempotent design |
| Missing permission registration | High | Test with non-admin user; verify button visibility |
| Document orphaning breaks references | Medium | Verify document table FK behavior; implement unlink in same transaction |
