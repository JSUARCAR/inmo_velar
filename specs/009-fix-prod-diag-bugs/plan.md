# Implementation Plan: fix-prod-diag-bugs

**Branch**: `009-fix-prod-diag-bugs` | **Date**: 2026-07-03 | **Spec**: [spec.md](file:///C:/Users/PC/OneDrive/Desktop/inmobiliaria%20velar/PYTHON-REFLEX/specs/009-fix-prod-diag-bugs/spec.md)

**Input**: Feature specification from `/specs/009-fix-prod-diag-bugs/spec.md`

## Summary

Resolución de tres incidentes críticos en producción mediante: 1) Implementación de paginación server-side para estabilizar la tabla de Incidentes, 2) Saneamiento de datos nulos y manejo defensivo para rehabilitar el modal de Liquidaciones, y 3) Inyección de `pointer-events: auto` en los estilos globales (Radix UI) para permitir la interacción con el botón Eliminar.

## Technical Context

**Language/Version**: Python 3.12 (Reflex framework)

**Primary Dependencies**: Reflex (UI & State), SQLAlchemy (ORM), Pydantic (DTOs), FastAPI (Backend routing)

**Storage**: PostgreSQL (Entorno productivo Railway)

**Testing**: Pytest E2E (Playwright headed mode)

**Target Platform**: Web application (Frontend SPA + Backend Worker en Railway)

**Project Type**: Plataforma transaccional Inmobiliaria

**Performance Goals**: TTI < 3s, Prevención absoluta de desbordamiento por websocket JSON serialization.

**Constraints**: Manejo obligatorio de nulos en Pydantic y actualización en cascada. 

**Scale/Scope**: Tablas de Incidentes y Liquidaciones con crecimiento asimétrico local vs prod.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] **Capa de Dominio aislada**: Las validaciones de paginación o saneamiento no deben romper la pureza de `src/dominio/`.
- [x] **Tipado Estricto**: Pydantic debe manejar `Optional[T]` adecuadamente.
- [x] **Zero Guessing**: Se definieron estrategias explícitas (Paginación + Backfill DB)
- [x] **Radix UI Portal Override**: Mandato explícito del ítem 16 cumplido: `pointer-events: auto` en `BASE_STYLE`.

## Project Structure

### Documentation (this feature)

```text
specs/009-fix-prod-diag-bugs/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
└── tasks.md
```

### Source Code (repository root)

```text
src/
├── aplicacion/
│   ├── dtos/                # Modificación de DTOs para manejo de Optional y Paginación
│   └── servicios/           # Scripts de backfill / saneamiento de base de datos
├── infraestructura/
│   └── repositorios/        # Consultas de paginación (limit, offset) en SQLAlchemy
├── presentacion_reflex/
│   ├── estados/             # Reflex states (paginación, manejo defensivo)
│   ├── componentes/         # Controles de paginación en UI
│   └── styles.py            # Modificación de BASE_STYLE (pointer-events)
└── scripts/
    └── diagnostico/         # Script de ejecución de saneamiento DB
```

**Structure Decision**: Se mantiene la arquitectura de capas estricta, aplicando la paginación a través de Repositorios (Infraestructura) hacia Estados (Presentación).

## Complexity Tracking

N/A
