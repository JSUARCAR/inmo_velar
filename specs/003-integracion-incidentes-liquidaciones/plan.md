# Implementation Plan: Integración Incidentes y Liquidaciones de Propietarios

**Branch**: `003-integracion-incidentes-liquidaciones` | **Date**: 2026-06-30 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/003-integracion-incidentes-liquidaciones/spec.md`

## Summary

Integrar los módulos de Incidentes y Liquidaciones de Propietarios para permitir la gestión del pago de incidentes mediante descuentos aplicados al canon de mandato. La solución incluye: definición de planes de pago por incidente, asociación de cuotas a liquidaciones, cálculo automático del estado de pago, y trazabilidad completa de todas las operaciones financieras.

## Technical Context

**Language/Version**: Python 3.11+

**Primary Dependencies**: 
- Reflex >= 0.6.0 (Framework UI)
- Pydantic >= 2.5.0 (Validación de datos)
- psycopg2-binary >= 2.9.0 (PostgreSQL adapter)
- FastAPI >= 0.110.0 (API endpoints)

**Storage**: PostgreSQL (producción) / SQLite (desarrollo)

**Testing**: pytest >= 7.4.0, pytest-cov >= 4.1.0

**Target Platform**: Web application (Linux server + modern browsers)

**Project Type**: Web application (Reflex framework with Clean Architecture)

**Performance Goals**: 
- < 3 segundos respuesta para operaciones CRUD
- Soporte para 15 usuarios simultáneos
- ~200 liquidaciones por período, ~500 incidentes activos

**Constraints**: 
- Bloqueo pesimista para ediciones concurrentes
- Transacciones atómicas con rollback
- Auditoría completa con IP y sesión

**Scale/Scope**: 
- ~15 usuarios concurrentes
- ~200 liquidaciones por período mensual
- ~500 incidentes activos

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

No constitution file found. Proceeding with standard architecture review.

## Project Structure

### Documentation (this feature)

```text
specs/003-integracion-incidentes-liquidaciones/
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
│   ├── entidades/
│   │   ├── incidente.py          # EXTEND: Add estado_pago attribute
│   │   ├── liquidacion.py        # EXTEND: Add valor_incidentes field
│   │   ├── plan_pago_incidente.py    # NEW: Payment plan entity
│   │   ├── cuota_incidente.py        # NEW: Installment entity
│   │   └── incidente_liquidacion.py  # NEW: Relationship entity
│   ├── interfaces/
│   │   ├── repositorio_plan_pago.py      # NEW: Repository interface
│   │   ├── repositorio_cuota.py          # NEW: Repository interface
│   │   └── repositorio_incidente_liq.py  # NEW: Repository interface
│   └── servicios/
│       └── servicio_financiero.py    # EXTEND: Add payment plan methods
├── infraestructura/
│   └── persistencia/
│       ├── repositorio_plan_pago_postgres.py      # NEW: Repository impl
│       ├── repositorio_cuota_postgres.py          # NEW: Repository impl
│       ├── repositorio_incidente_liq_postgres.py  # NEW: Repository impl
│       ├── repositorio_incidentes_postgres.py     # EXTEND: Add queries
│       └── repositorio_liquidacion_postgres.py    # EXTEND: Add queries
├── aplicacion/
│   └── servicios/
│       ├── servicio_incidentes.py     # EXTEND: Add payment plan methods
│       └── servicio_liquidaciones.py  # EXTEND: Add association methods
└── presentacion_reflex/
    ├── state/
    │   ├── incidentes_state.py      # EXTEND: Add payment plan UI state
    │   └── liquidaciones_state.py   # EXTEND: Add association UI state
    └── components/
        ├── incidentes/
        │   └── modal_plan_pago.py   # NEW: Payment plan modal
        └── liquidaciones/
            └── modal_seleccion_incidentes.py  # NEW: Incident selection modal

tests/
├── unit/
│   ├── test_plan_pago.py           # NEW: Payment plan unit tests
│   ├── test_cuota_incidente.py     # NEW: Installment unit tests
│   └── test_incidente_liquidacion.py  # NEW: Relationship unit tests
├── integration/
│   ├── test_pago_liquidacion_integration.py  # NEW: Integration tests
│   └── test_estado_pago_calculation.py       # NEW: State calculation tests
└── contract/
    └── test_plan_pago_contract.py   # NEW: Contract tests
```

**Structure Decision**: Following existing Clean Architecture pattern with domain/infrastructure/application/presentation layers. New entities and repositories follow established patterns in the codebase.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| N/A | No architectural violations | N/A |

## Phase 0: Research

See `research.md` for detailed findings.

## Phase 1: Design

See `data-model.md`, `contracts/`, and `quickstart.md` for design artifacts.
