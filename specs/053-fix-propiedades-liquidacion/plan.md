# Implementation Plan: Fix Propiedades a Liquidar

**Branch**: `053-fix-propiedades-liquidacion` | **Date**: 2026-07-13 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/053-fix-propiedades-liquidacion/spec.md`

## Summary

Corrección del módulo Liquidación de Asesores para garantizar que la generación de una Nueva Liquidación incluya la totalidad de las propiedades con Contratos de Arrendamiento activos asociados al asesor. El problema raíz se localiza en la consulta SQL `obtener_activos_por_asesor()` que utiliza un JOIN INNER entre `CONTRATOS_ARRENDAMIENTOS` y `CONTRATOS_MANDATOS` vía `ID_PROPIEDAD`, excluyendo propiedades que no tienen un contrato mandato activo correspondiente o cuyo enlace no se resuelve correctamente.

## Technical Context

**Language/Version**: Python 3.11+ (Reflex framework)

**Primary Dependencies**: Reflex (UI), psycopg2 (PostgreSQL driver), Pydantic (DTOs/validations)

**Storage**: PostgreSQL

**Testing**: pytest, manual Reflex UI verification

**Target Platform**: Linux server (Railway), browser frontend

**Project Type**: web-service (full-stack Reflex application)

**Performance Goals**: No degradación del tiempo de respuesta actual al generar liquidaciones

**Constraints**: Sin cambios en esquema de BD. Preservar comportamiento existente del módulo.

**Scale/Scope**: Módulo Liquidación de Asesores completo (~15 archivos afectados)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| Clean Architecture (Dominio → Aplicación → Infraestructura → Presentación) | ✅ PASS | Cambios en repositorio (infraestructura), servicio (aplicación) y state (presentación). Sin dependencias circulares. |
| PostgreSQL Native (placeholders %s, RETURNING id) | ✅ PASS | Consultas existentes ya usan %. No se agregan nuevas tablas. |
| Idioma 100% Español | ✅ PASS | Todo el código y documentación en español. |
| snake_case para variables/funciones | ✅ PASS | Convención existente mantenida. |
| Type Hints obligatorios | ✅ PASS | Se preservan los type hints existentes. |
| Zero Deferred Cleanup | ✅ PASS | Se corrige la raíz del bug, no se deja deuda técnica. |
| Cambios Atómicos (~100 líneas) | ✅ PASS | Cambios concentrados en repositorio + servicio + form_state. |
| No Flet/SQLite references | ✅ PASS | Proyecto ya migrado a Reflex/PostgreSQL. |

**Gate Result**: ✅ ALL PASS — Proceed to Phase 0.

## Project Structure

### Documentation (this feature)

```text
specs/053-fix-propiedades-liquidacion/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
└── tasks.md             # Phase 2 output (NOT created by /speckit-plan)
```

### Source Code (repository root)

```text
src/
├── dominio/
│   ├── entidades/
│   │   └── liquidacion_asesor.py          # Entity (review only)
│   └── interfaces/
│       └── repositorio_contrato_arrendamiento.py  # Interface (review only)
├── aplicacion/
│   └── servicios/
│       └── servicio_liquidacion_asesores.py  # Service layer (minor review)
├── infraestructura/
│   └── persistencia/
│       └── repositorio_contrato_arrendamiento_postgres.py  # PRIMARY FIX TARGET
├── presentacion_reflex/
│   ├── state/
│   │   └── liquidacion_asesores/
│   │       └── form_state.py               # State management (secondary fix target)
│   └── components/
│       └── liquidacion_asesores/
│           └── modal_form.py               # UI modal (review for rendering limits)
│   └── pages/
│       └── liquidacion_asesores.py          # Main page (review only)
```

**Structure Decision**: Cambios concentrados en 2-3 archivos principales. No se crean nuevos archivos. La estructura existente del proyecto se preserva.

## Complexity Tracking

No violations to justify. All changes align with existing architecture.
