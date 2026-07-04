# Implementation Plan: Fix Sincronización Incidentes - Liquidaciones

**Branch**: `004-fix-sincronizacion-incidentes-liquidaciones` | **Date**: 2026-07-02 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/004-fix-sincronizacion-incidentes-liquidaciones/spec.md`

## Summary

Corregir 5 bugs críticos en la integración entre Incidentes y Liquidaciones de Propietarios: desincronización de NETO_A_PAGAR, sobrescritura de observaciones, pérdida de ESTADO_PAGO en persistencia, y mapeo incorrecto en formulario de edición. La solución mantiene los triggers de BD como fuente primaria y sincroniza la capa de aplicación después.

## Technical Context

**Language/Version**: Python 3.11

**Primary Dependencies**: Reflex (UI), Pydantic (validación), psycopg2-binary (PostgreSQL), pytest (testing)

**Storage**: PostgreSQL ( Railway)

**Testing**: pytest + pytest-cov (>90% cobertura requerida)

**Target Platform**: Web application (Reflex framework)

**Project Type**: Web application (Clean Architecture - 4 capas)

**Performance Goals**: <3s tiempo de respuesta para operaciones de asociación/desasociación

**Constraints**: 
- Sin cambios a schema de base de datos
- Mantener triggers existentes como fuente primaria
- Solo Administradores pueden asociar/desasociar
- 100% español en código y documentación

**Scale/Scope**: ~15 usuarios simultáneos, ~200 liquidaciones/período, ~500 incidentes activos

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principio | Estado | Notas |
|-----------|--------|-------|
| Clean Architecture (Dominio → Aplicación → Infraestructura → Presentación) | ✅ PASS | Fix en capas Aplicación, Infraestructura y Presentación |
| 100% Español | ✅ PASS | Todo el código y documentación en español |
| PostgreSQL Native (placeholders %s) | ✅ PASS | Sin cambios a queries existentes |
| Type Hints obligatorios | ✅ PASS | Se aplicarán en todo código nuevo |
| Docstrings Google Style | ✅ PASS | Servicios clave documentados |
| Excepciones de dominio específicas | ✅ PASS | Sin except Exception genérico |
| Testing >90% cobertura | ✅ PASS | Unit + Integration tests planificados |
| RBAC con decoradores | ✅ PASS | Solo Administradores pueden asociar |
| Commits Conventional Commits | ✅ PASS | fix(backend): ..., fix(frontend): ... |
| Zero Deferred Cleanup | ✅ PASS | Deuda técnica resuelta en el momento |

**Result**: ✅ GATE PASSED - Sin violaciones a la constitución

## Project Structure

### Documentation (this feature)

```text
specs/004-fix-sincronizacion-incidentes-liquidaciones/
├── plan.md              # Este archivo
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
└── tasks.md             # Phase 2 output (no creado por /speckit.plan)
```

### Source Code (repository root)

```text
src/
├── dominio/
│   └── entidades/
│       ├── incidente.py
│       ├── liquidacion.py
│       ├── cuota_incidente.py
│       └── incidente_liquidacion.py
├── aplicacion/
│   └── servicios/
│       ├── servicio_incidente_liquidacion.py  # FIX: lógica de asociación
│       ├── servicio_estado_pago.py            # FIX: persistencia ESTADO_PAGO
│       └── servicio_financiero.py             # FIX: recálculo totales
├── infraestructura/
│   └── persistencia/
│       ├── repositorio_incidentes_postgres.py  # FIX: incluir ESTADO_PAGO en UPDATE
│       ├── repositorio_liquidacion_postgres.py # FIX: incluir VALOR_INCIDENTES
│       └── repositorio_cuota_postgres.py
└── presentacion_reflex/
    └── components/
        ├── liquidacion_edit_form.py   # FIX: mapeo campo Incidentes
        ├── liquidacion_detail_modal.py
        └── liquidaciones_state.py

tests/
├── unit/
│   ├── test_servicio_incidente_liquidacion.py
│   └── test_servicio_estado_pago.py
└── integration/
    ├── test_repositorio_incidentes.py
    └── test_repositorio_liquidacion.py
```

**Structure Decision**: Se mantiene la estructura Clean Architecture existente. Los fixes se aplican en las capas Aplicación (servicios), Infraestructura (repositorios) y Presentación (UI).

## Complexity Tracking

> **No violations to justify** - Todos los principios de constitución se cumplen

## Phase 0: Research

Ver `research.md` para decisiones técnicas detalladas.

## Phase 1: Design

Ver `data-model.md` para modelo de datos actualizado.
Ver `contracts/` para interfaces de servicio.
Ver `quickstart.md` para guía de validación.
