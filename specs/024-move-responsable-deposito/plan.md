# Implementation Plan: move-responsable-deposito

**Branch**: `[024-move-responsable-deposito]` | **Date**: 2026-07-05 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/024-move-responsable-deposito/spec.md`

## Summary

Migrar la funcionalidad del campo "Responsable del Depósito" para que sea eliminada del Contrato de Mandato y se implemente exclusivamente en el Contrato de Arrendamiento. Esto involucra eliminar la columna en la tabla de Mandatos (descartando datos previos), agregarla en Arrendamientos y trasladar la lógica de UI, State y repositorios correspondientes, asegurando la preselección de asesores inactivos si ya estaban asignados históricamente.

## Technical Context

**Language/Version**: Python 3.12+ (Reflex)

**Primary Dependencies**: Reflex, Pydantic, psycopg2

**Storage**: PostgreSQL

**Testing**: pytest, Playwright (UI)

**Target Platform**: Web application (Railway)

**Project Type**: Web-service / Internal Tool (Inmobiliaria Velar)

**Performance Goals**: N/A (Standard CRUD operations)

**Constraints**: PostgreSQL native placeholders (`%s`), Clean Architecture strict adherence, zero Flet/SQLite references.

**Scale/Scope**: 1 UI Modal removal, 1 UI Modal addition, 2 Repositories updated, 1 DB Migration.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Dependencias Unidireccionales**: Sí (Dominio no será modificado, excepto atributos en entidades; Persistencia e UI dependerán de Dominio).
- **PostgreSQL Native**: Sí, se usará `RETURNING id` y `%s`.
- **Nomenclatura**: Sí, variables `snake_case` (ej. `responsable_deposito_id`).
- **Validación en Fronteras**: Sí, los formularios de UI enviarán datos limpios.

## Project Structure

### Documentation (this feature)

```text
specs/024-move-responsable-deposito/
├── plan.md              # This file (/speckit.plan command output)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
src/
├── dominio/
│   └── entidades/
│       ├── contrato_mandato.py
│       └── contrato_arrendamiento.py
├── aplicacion/
│   └── servicios/
│       ├── servicio_contratos.py
│       ├── servicio_contrato_mandato.py
│       └── servicio_contrato_arrendamiento.py
├── infraestructura/
│   └── persistencia/
│       ├── repositorio_contrato_mandato_postgres.py
│       └── repositorio_contrato_arrendamiento_postgres.py
└── presentacion_reflex/
    ├── state/
    │   └── contratos_state.py
    └── components/
        └── contratos/
            ├── formulario_contrato_mandato.py
            ├── formulario_contrato_arrendamiento.py
            └── modal_detalle_contrato.py
```

**Structure Decision**: El proyecto sigue la Clean Architecture dictada por la constitución. Intervendremos en todas las capas para trasladar este atributo, así como en un archivo de migración en la base de datos (generalmente scripts SQL que deben correrse).
