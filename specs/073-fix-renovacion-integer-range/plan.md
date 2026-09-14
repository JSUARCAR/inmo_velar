# Implementation Plan: Fix `integer out of range` en renovación de contratos

**Branch**: `073-fix-renovacion-integer-range` | **Date**: 2026-09-14 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/073-fix-renovacion-integer-range/spec.md`

## Summary

Desbloquear la renovación del contrato 73 (La Alquería CS 54) y eliminar la
causa raíz: overflow `integer × integer` en la propagación del canon a
liquidaciones futuras. Enfoque: ensanchar el cómputo intermedio a 64 bits en
las 2 expresiones SQL afectadas + validación previa en aplicación con mensaje
operativo (campo + valor) + tests límite y de regresión. Sin migración de
columnas ni backfill (ver `research.md` R1–R5).

## Technical Context

**Language/Version**: Python 3.12

**Primary Dependencies**: Reflex, psycopg2, pytest

**Storage**: PostgreSQL (Railway; SQLite solo legacy, prohibido en lógica nueva)

**Testing**: pytest — suites existentes `tests/unit/test_renovacion_*.py`,
`tests/integration/test_renovacion_*.py`, `test_canon_propiedad_renovacion.py`

**Target Platform**: Servidor Linux (Railway) + desarrollo local

**Project Type**: Web application full-stack (Reflex)

**Performance Goals**: La renovación completa en un solo intento interactivo;
propagación acotada a liquidaciones/recaudos futuros del contrato (sin NFR
estricto en spec — diferido)

**Constraints**: Sin cambiar tipos de columnas; sin recalcular historia;
truncamiento al entero vigente; atomicidad total; idempotencia ante
reintentos y concurrencia; 100% español; placeholders `%s`; cambios atómicos
pequeños

**Scale/Scope**: Rangos garantizados canon ≤ $10.000.000, comisión ≤ 1500;
sobre-máximos se rechazan con mensaje operativo; un único punto SQL a
corregir + validación + tests

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principio (§) | Veredicto |
|---|---|
| Arquitectura por capas — fix en servicio de aplicación + SQL, dominio intacto | PASS |
| PostgreSQL nativo (`%s`, sin `lastrowid`, sin SQLite) | PASS |
| Español 100%, type hints, docstrings Google, sin `except` genérico | PASS (exigido en tareas) |
| Cambios atómicos pequeños, cero deuda diferida | PASS (~2 expresiones SQL + validación + tests) |
| Tests >90% lógica nueva, BD de prueba, suites en verde pre/post | PASS (plan de pruebas en `quickstart.md`) |
| RBAC / seguridad sin cambios | PASS |
| Decisiones con evidencia, sin adivinanza | PASS (`research.md` R1 con H1/H2/H3) |

Post-diseño: sin violaciones; tabla de complejidad vacía por diseño.

## Project Structure

### Documentation (this feature)

```text
specs/073-fix-renovacion-integer-range/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
│   └── propagacion-canon.md
├── checklists/          # /speckit.specify + /speckit.checklist outputs
│   ├── requirements.md
│   └── renovacion.md
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
src/
├── aplicacion/servicios/servicio_contrato_arrendamiento.py  # fix SQL + validación (FR-002/003)
├── presentacion_reflex/state/contratos_state.py              # mapeo mensaje operativo (FR-003)
└── dominio/excepciones/excepciones_base.py                   # excepción de dominio si falta

tests/
├── integration/test_renovacion_propagacion_limite.py         # NUEVO: magnitudes límite
├── integration/test_renovacion_*.py                          # regresión existente
└── unit/test_renovacion_*.py                                 # regresión existente
```

**Structure Decision**: Se respeta la estructura Clean existente; el cambio
vive en la capa de aplicación (servicio + SQL parametrizado) con validación
de dominio y mensaje en presentación. Sin nuevos proyectos ni patrones.

## Complexity Tracking

> Sin violaciones del Constitution Check — tabla vacía por diseño.
