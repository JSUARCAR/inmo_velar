# Implementation Plan: fix-filtro-ciclo-ui

**Branch**: `feature/013-fix-filtro-ciclo-ui` | **Date**: 2026-07-04 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/013-fix-filtro-ciclo-ui/spec.md`

## Summary

Esta característica corrige un bug en la consulta SQL de liquidaciones donde el filtro por "Ciclo Operativo" fallaba por un alias incorrecto de base de datos (`prop` en vez de `p`). Adicionalmente, soluciona un problema visual de superposición de componentes en la sección de filtros avanzados en pantallas móviles, asegurando que cada filtro ocupe el 100% del ancho mediante un rediseño del layout con Flexbox en Reflex.

## Technical Context

**Language/Version**: Python 3.11+ (Reflex)

**Primary Dependencies**: Reflex, Psycopg2 (PostgreSQL)

**Storage**: PostgreSQL

**Testing**: Validación CI manual y testing End-to-End visual (`check_syntax.py`, `reflex export`).

**Target Platform**: Web (Desktop & Mobile)

**Project Type**: Web Application

**Performance Goals**: < 2 segundos de respuesta en base de datos.

**Constraints**: El diseño debe seguir el Claude Design System (Neumorfismo).

**Scale/Scope**: Limitado al módulo de Liquidaciones y la barra de filtros avanzados.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Arquitectura Limpia**: Se respeta la capa de persistencia (`repositorio_liquidacion_postgres.py`) para el ajuste SQL y la capa de presentación (`liquidaciones.py`) para los estilos UI. No se viola la unidireccionalidad.
- **Tipos y Nomenclatura**: Uso de tipado explícito, `snake_case` y convención de placeholders de PostgreSQL (`%s`).
- **Sanitización y UI**: Los estilos se apegarán a `BASE_STYLE` y se evitarán anchos fijos que rompan responsividad en pantallas móviles.

## Project Structure

### Documentation (this feature)

```text
specs/013-fix-filtro-ciclo-ui/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
└── quickstart.md        # Phase 1 output
```

### Source Code (repository root)

```text
src/
├── infraestructura/
│   └── persistencia/
│       └── repositorio_liquidacion_postgres.py  # Fix de query SQL
└── presentacion_reflex/
    └── pages/
        └── liquidaciones.py  # Fix de UI/Responsive
```

**Structure Decision**: El proyecto es una aplicación Web (Reflex) que sigue Clean Architecture. La estructura refleja las modificaciones necesarias en Infraestructura (Base de datos) y Presentación (UI). No hay nuevas entidades ni DTOs afectados, por lo que el impacto estructural es mínimo.
