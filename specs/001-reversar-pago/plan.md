# Implementation Plan: Reversar Pago de Liquidación

**Branch**: `001-reversar-pago` | **Date**: 2026-06-30 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/001-reversar-pago/spec.md`

## Summary

Add a "Reversar Pago" action to the Liquidaciones de Propietarios module that transitions a liquidation from "Pagada" to "Aprobada", clears payment fields, records an audit trail with mandatory motivo, and supports both individual and selective bulk operations. The implementation extends existing reversal patterns with idempotent behavior and permission-gated UI.

## Technical Context

**Language/Version**: Python 3.11+

**Primary Dependencies**: Reflex >=0.6.0 (UI framework), psycopg2-binary (PostgreSQL), pydantic (validation), python-dateutil

**Storage**: PostgreSQL (via `RepositorioLiquidacionPostgres`)

**Testing**: pytest, pytest-cov

**Target Platform**: Web application (Reflex SPA)

**Project Type**: web-application (Reflex full-stack)

**Performance Goals**: Single reversal completes in <2 seconds (DB transaction + audit insert)

**Constraints**: No database schema changes; must use existing AUDITORIA_CAMBIOS trigger pattern; no modifications to existing triggers

**Scale/Scope**: Single-module feature within an existing real estate management system (~50 screens)

## Constitution Check

*No constitution file found. Skipping governance gate.*

## Project Structure

### Documentation (this feature)

```text
specs/001-reversar-pago/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   ├── ui-reverse-pago-dialog.md
│   └── service-reversar-pago.md
└── tasks.md             # Phase 2 output (/speckit.tasks)
```

### Source Code (repository root)

```text
src/
├── dominio/
│   ├── entidades/
│   │   └── liquidacion.py              # NO CHANGES (entity unchanged)
│   └── interfaces/
│       └── repositorio_liquidacion.py  # ADD reversar_pago() to Protocol
├── infraestructura/
│   └── persistencia/
│       └── repositorio_liquidacion_postgres.py  # ADD reversar_pago() method
├── aplicacion/
│   └── servicios/
│       └── servicio_financiero.py      # ADD reversar_pago_liquidacion() method
└── presentacion_reflex/
    ├── state/
    │   └── liquidaciones_state.py      # ADD reverse_pago event handlers
    ├── components/
    │   └── liquidaciones/
    │       ├── reverse_pago_confirm_dialog.py  # NEW: confirmation dialog
    │       └── liquidacion_detail_modal.py     # MODIFY: add reversar_pago button
    └── pages/
        └── liquidaciones.py            # MODIFY: add button in table + import dialog

tests/
├── unit/
│   └── test_entidades/
│       └── test_reversar_pago.py       # NEW: unit tests
├── integration/
│   └── test_reversar_pago_integration.py  # NEW: integration tests
└── dominio/
    └── test_reversar_pago_domain.py    # NEW: domain tests
```

**Structure Decision**: Single project with existing Reflex architecture. Feature spans 4 layers: domain interface, repository, service, and UI state/components.

## Complexity Tracking

*No constitution violations to justify.*

## Files to Modify/Create

| File | Action | Scope |
|------|--------|-------|
| `src/dominio/interfaces/repositorio_liquidacion.py` | MODIFY | Add `reversar_pago()` to Protocol |
| `src/infraestructura/persistencia/repositorio_liquidacion_postgres.py` | MODIFY | Add `reversar_pago()` method (~40 lines) |
| `src/aplicacion/servicios/servicio_financiero.py` | MODIFY | Add `reversar_pago_liquidacion()` method (~30 lines) |
| `src/presentacion_reflex/state/liquidaciones_state.py` | MODIFY | Add 4 event handlers + 3 state vars |
| `src/presentacion_reflex/components/liquidaciones/reverse_pago_confirm_dialog.py` | CREATE | New dialog component (~80 lines) |
| `src/presentacion_reflex/components/liquidaciones/liquidacion_detail_modal.py` | MODIFY | Add "Reversar Pago" button |
| `src/presentacion_reflex/pages/liquidaciones.py` | MODIFY | Add button in table, import dialog |
| `scripts/add_liquidaciones_permissions.py` | MODIFY | Register REVERSAR_PAGO permission |
| `tests/unit/test_entidades/test_reversar_pago.py` | CREATE | Unit tests |
| `tests/integration/test_reversar_pago_integration.py` | CREATE | Integration tests |

## Implementation Order

1. **Repository layer**: `reversar_pago()` in interface + implementation
2. **Service layer**: `reversar_pago_liquidacion()` with validation
3. **State management**: Event handlers in LiquidacionesState
4. **UI Component**: Confirmation dialog
5. **UI Integration**: Buttons in table and detail modal
6. **Permissions**: Register REVERSAR_PAGO action
7. **Tests**: Unit + integration tests

## Risk Assessment

| Risk | Impact | Mitigation |
|------|--------|------------|
| Audit trigger doesn't capture all fields | Medium | Verify trigger behavior; explicit audit insert for motivo |
| Concurrent reversal attempts | Low | DB row-level locking via UPDATE WHERE |
| Missing permission registration | High | Test with non-admin user; verify button visibility |
