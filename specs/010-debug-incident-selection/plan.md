# Implementation Plan: debug-incident-selection

**Branch**: `[010-debug-incident-selection]` | **Date**: 2026-07-04 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/010-debug-incident-selection/spec.md`

## Summary

Diagnosticar y reparar el error en la interfaz de usuario donde el botón "Seleccionar Incidentes" no abre el modal correspondiente en el formulario de edición de Liquidaciones. La solución implicará revisar el estado del componente Reflex, las configuraciones de `pointer-events` / `z-index` en modales anidados y la correcta consulta de datos filtrando incidentes no pagados.

## Technical Context

**Language/Version**: Python 3.11+

**Primary Dependencies**: Reflex

**Storage**: PostgreSQL

**Testing**: Validación manual en entorno local/navegador

**Target Platform**: Navegador Web / Reflex Backend

**Project Type**: Web application

**Performance Goals**: < 2 segundos de tiempo de carga/respuesta del modal.

**Constraints**: Adherencia estricta a convenciones de UI (z-index centralizado, mutaciones atómicas)

**Scale/Scope**: Módulo individual dentro del sistema de administración

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Consolidación Tecnológica**: Reflex/PostgreSQL ✅
- **Estándares UI**: pointer-events y z-index globales ✅
- **Mutaciones Atómicas**: Se revisará que el estado `is_open` mute correctamente ✅
- **Contract-First**: N/A para bugfix puro UI ✅
- **Rendimiento y Zero Leak**: ✅

## Project Structure

### Documentation (this feature)

```text
specs/010-debug-incident-selection/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
└── tasks.md
```

### Source Code (repository root)

```text
src/
└── presentacion_reflex/
    ├── liquidaciones/
    │   ├── estado_liquidaciones.py (o similar, manejador del modal)
    │   └── componentes/
    │       └── modal_incidentes.py (o donde resida el modal)
```

**Structure Decision**: La modificación se limitará al directorio `src/presentacion_reflex/liquidaciones/` u homólogo donde se gestione el componente visual y su estado asociado en Reflex.
