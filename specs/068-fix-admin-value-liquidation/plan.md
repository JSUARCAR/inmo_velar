# Implementation Plan: fix-admin-value-liquidation

**Branch**: `fix-admin-value-liquidation` | **Date**: 2026-09-02 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/068-fix-admin-value-liquidation/spec.md`

**Note**: This template is filled in by the `/speckit-plan` command.

## Summary

Implementar sincronización en cascada de `valor_administracion` desde la tabla `PROPIEDADES` hacia `LIQUIDACIONES` en estado "En Proceso" correspondientes al periodo actual, recalculando los totales (`TOTAL_EGRESOS`, `NETO_A_PAGAR = TOTAL_INGRESOS - TOTAL_EGRESOS`) mediante una transacción atómica bajo una política de *Strict Rollback*. La interfaz notificará el número de liquidaciones actualizadas y mantendrá los manual overrides intactos (incluyendo el valor 0).

## Technical Context

<!--
  ACTION REQUIRED: Replace the content in this section with the technical details
  for the project. The structure here is presented in advisory capacity to guide
  the iteration process.
-->

**Language/Version**: Python 3.11+

**Primary Dependencies**: Reflex, psycopg2, Pydantic

**Storage**: PostgreSQL

**Testing**: pytest

**Target Platform**: Linux server (Railway)

**Project Type**: web application

**Performance Goals**: Standard web application latency

**Constraints**: Strict typing, `%s` placeholders, no magic numbers, atomic transactions for financial data

**Scale/Scope**: Moderate

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] **Arquitectura Limpia**: Se mantendrá la independencia de capas. La persistencia (`servicio_propiedades.py`) ejecuta el SQL de actualización.
- [x] **PostgreSQL Native**: Uso exclusivo de `%s` como placeholders en consultas crudas.
- [x] **Transaccionalidad**: La actualización de Propiedad + Liquidación se hará dentro de una transacción `with db_manager.obtener_conexion() as conn:`.
- [x] **Reglas de UI**: La UI (Reflex) respetará el valor traído por BD sin sobreescribirlo silenciosamente si hay un 0 legítimo.

## Project Structure

### Documentation (this feature)

```text
specs/068-fix-admin-value-liquidation/
├── plan.md              # This file (/speckit-plan command output)
├── research.md          # Phase 0 output (/speckit-plan command)
├── data-model.md        # Phase 1 output (/speckit-plan command)
├── quickstart.md        # Phase 1 output (/speckit-plan command)
└── tasks.md             # Phase 2 output (/speckit-tasks command - NOT created by /speckit-plan)
```

### Source Code (repository root)

```text
src/
├── aplicacion/
│   └── servicios/
│       └── servicio_propiedades.py   # Actualización de la BD
└── presentacion_reflex/
    └── state/
        └── liquidaciones_state.py    # UX toast y lógica del modal
```

**Structure Decision**: Modificación directa sobre la arquitectura limpia existente (Servicios de Aplicación para lógica de BD, Presentación Reflex para UI/State). No se añaden nuevas capas ni archivos.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No architecture violations detected.
