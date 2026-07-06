# Implementation Plan: campos-extra-contratos

**Branch**: `[021-campos-extra-contratos]` | **Date**: 2026-07-05 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/021-campos-extra-contratos/spec.md`

**Note**: This template is filled in by the `/speckit-plan` command.

## Summary

Agregar campo 'Enlace de video' (URL válida) en los contratos de Mandato y Arrendamiento, y campo 'Responsable del depósito' (ComboBox dinámico de asesores activos) exclusivo para contratos de Mandato, con soporte y persistencia total en PostgreSQL a través de UI de Reflex y Clean Architecture.

## Technical Context

**Language/Version**: Python 3.11+

**Primary Dependencies**: Reflex, Pydantic, psycopg2 (PostgreSQL driver)

**Storage**: PostgreSQL

**Testing**: pytest, mypy, ruff, black

**Target Platform**: Web App (Reflex), Railway cloud

**Project Type**: Web Application / ERP

**Performance Goals**: Fast UI rendering, DB responses < 1s

**Constraints**: Clean Architecture Élite, Cero Filtraciones, Validaciones estrictas.

**Scale/Scope**: Adición de dos campos, actualización de esquemas DB y componentes UI Reflex.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] Regla de Oro (Dependencias Unidireccionales): Respeta la arquitectura en capas.
- [x] Lingüística: Atributos y funciones en snake_case; UI Components en PascalCase.
- [x] Persistencia: Uso de `%s` y `RETURNING id` para PostgreSQL. No uso de SQLite.
- [x] UI System: Uso de componentes estándar del proyecto.
- [x] Seguridad (Zero Leak): Sin exposición de URLs o usuarios.

## Project Structure

### Documentation (this feature)

```text
specs/021-campos-extra-contratos/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
└── tasks.md             # Phase 2 output (/speckit-tasks command)
```

### Source Code (repository root)

```text
src/
├── dominio/
│   └── (entidades de contrato actualizadas)
├── aplicacion/
│   └── (DTOs y servicios de orquestación actualizados)
├── infraestructura/
│   └── (repositorios de PostgreSQL actualizados)
└── presentacion_reflex/
    └── (modales y componentes de interfaz actualizados)
```

**Structure Decision**: El proyecto mantiene la estructura actual de Clean Architecture descrita en la constitución. Los cambios se localizarán en las rutas correspondientes a contratos de mandato y arrendamiento.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

*No violations found.*
