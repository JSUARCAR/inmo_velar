# Implementation Plan: Fix Payment Status Synchronization Between Liquidaciones and Incidentes

**Branch**: `033-fix-payment-sync-incidentes` | **Date**: 2026-07-07 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/033-fix-payment-sync-incidentes/spec.md`

## Summary

Fix the payment status synchronization bug between the Liquidaciones and Incidentes modules. When a Liquidación is marked as "Pagada", the associated Incidente's payment plan cuotas and payment status badge are not being updated. The root cause is that `ServicioFinanciero.marcar_liquidacion_pagada()` updates cuota states directly, but `ServicioEstadoPagoAutomatico` is either not being called or is failing silently. Additionally, bulk payments via `marcar_como_pagada_masiva()` do not trigger incident status recalculation at all.

## Technical Context

**Language/Version**: Python 3.11+

**Primary Dependencies**: Reflex 0.6+, Pydantic 2.5+, FastAPI 0.110+, SQLAlchemy (via Reflex ORM)

**Storage**: PostgreSQL (Railway-hosted)

**Testing**: pytest 7.4+, pytest-cov 4.1+

**Target Platform**: Web application (Reflex frontend + FastAPI backend), deployed on Railway

**Project Type**: Web application (DDD architecture: dominio/aplicacion/infraestructura/presentacion_reflex)

**Performance Goals**: UI state update within 2 seconds (SC-002)

**Constraints**: Reflex state management pattern; existing transaction boundaries in `ServicioFinanciero`

**Scale/Scope**: Multi-tenant real estate management system; ~50+ screens; existing codebase with DDD layers

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

No constitution file exists. Skipping constitution check.

## Project Structure

### Documentation (this feature)

```text
specs/033-fix-payment-sync-incidentes/
├── spec.md              # Feature specification
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
└── tasks.md             # Phase 2 output
```

### Source Code (repository root)

```text
src/
├── dominio/                          # Domain entities and value objects
│   └── entidades/
│       ├── incidente.py              # Incidente entity (contains estado_pago)
│       ├── liquidacion.py            # Liquidacion entity (contains estado_liquidacion)
│       └── cuota_incidente.py        # CuotaIncidente entity (contains estado_pago, id_liquidacion)
├── aplicacion/                       # Application services
│   └── servicios/
│       ├── servicio_financiero.py    # marcar_liquidacion_pagada() - updates cuotas
│       └── servicio_estado_pago.py   # ServicioEstadoPagoAutomatico - recalculates incident status
├── infraestructura/                  # Data access layer
│   └── persistencia/
│       └── repositorio_cuota_postgres.py  # obtener_por_liquidacion(), contar_estado_liquidaciones_por_plan()
└── presentacion_reflex/              # UI layer
    ├── state/
    │   ├── liquidaciones_state.py    # marcar_como_pagada(), marcar_como_pagada_masiva()
    │   └── incidentes/
    │       └── incidentes_base.py    # Incidentes state with payment plan data
    └── components/
        ├── liquidaciones/
        │   └── payment_form.py       # Payment form (recently fixed)
        └── incidentes/
            └── modal_plan_pago.py    # Payment plan modal display
```

**Structure Decision**: Existing DDD architecture preserved. Changes confined to:
1. `servicio_financiero.py` - Ensure `ServicioEstadoPagoAutomatico` is called after cuota updates
2. `servicio_estado_pago.py` - Fix `recalcular_estado_pago_incidente()` to read cuota states correctly
3. `liquidaciones_state.py` - Add incident status sync to bulk payment flow
4. `repositorio_cuota_postgres.py` - Verify SQL queries return correct data

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No constitution violations. No complexity tracking needed.
