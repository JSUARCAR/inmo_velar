# Implementation Plan: filtro-pago-incidentes

**Branch**: `030-filtro-pago-incidentes` | **Date**: 2026-07-06 | **Spec**: [spec.md](file:///C:/Users/PC/OneDrive/Desktop/inmobiliaria%20velar/PYTHON-REFLEX/specs/030-filtro-pago-incidentes/spec.md)

**Input**: Feature specification from `specs/030-filtro-pago-incidentes/spec.md`

## Summary

Incorporar un nuevo filtro "Estado de Pago del Incidente" en la sección Filtros Avanzados del módulo Incidentes. Las opciones se deducirán dinámicamente según el estado de las liquidaciones asociadas y el filtrado se realizará nativamente en PostgreSQL, respetando el Sistema de Diseño y la Clean Architecture de Inmobiliaria Velar.

## Technical Context

**Language/Version**: Python 3.11+

**Primary Dependencies**: Reflex, psycopg2, Pydantic

**Storage**: PostgreSQL

**Testing**: pytest

**Target Platform**: Aplicación Web (Despliegue en Railway)

**Project Type**: Web Application (Transaccional)

**Performance Goals**: < 1 segundo en consultas con el filtro aplicado.

**Constraints**: Clean Architecture estricta. Cero referencias a SQLite o Flet.

**Scale/Scope**: Módulo interno de gestión de incidentes y liquidaciones.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] **Arquitectura de Capas**: El filtrado ocurre en el Repositorio (Infraestructura), llamado por el Servicio (Aplicación) a petición de la UI (Presentación).
- [x] **Ingeniería de Datos**: Uso exclusivo de `%s` para consultas PostgreSQL.
- [x] **Diseño UI**: Uso de componentes nativos de Reflex adhiriendo al Claude Design System y configuración base de tooltips/floating labels.

## Project Structure

### Documentation (this feature)

```text
specs/030-filtro-pago-incidentes/
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
│   └── servicios/
│       └── servicio_incidentes.py (DTOs y Orquestación)
├── dominio/
│   └── entidades/
│       └── incidente.py (Entidad y Tipos de Estado)
├── infraestructura/
│   └── repositorios/
│       └── repositorio_incidentes.py (Consultas PostgreSQL nativas)
└── presentacion_reflex/
    ├── componentes/
    │   └── filtros_avanzados.py (UI Reflex)
    └── estados/
        └── incidentes_state.py (State Management)
```

**Structure Decision**: El proyecto utiliza un modelo de Clean Architecture centralizado en `src/`. Los cambios atravesarán todas las capas desde UI hasta Infraestructura.

## Complexity Tracking

No se reportan violaciones a la constitución, por lo que no se requiere justificación de complejidad adicional.
