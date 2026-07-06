# Implementation Plan: Auditoría de Tooltips Faltantes

**Branch**: `[023-auditoria-tooltips-faltantes]` | **Date**: 2026-07-05 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/023-auditoria-tooltips-faltantes/spec.md`

## Summary

Auditar visual y a nivel de código el repositorio en búsqueda de botones (`neuro_button`, `rx.button`, `rx.icon_button`) que carezcan del contenedor de tooltip respectivo, e inyectar `neuro_tooltip` en aquellos que correspondan (especialmente botones de íconos o sin etiqueta clara), respetando las directivas globales de Z-Index y comportamiento móvil.

## Technical Context

**Language/Version**: Python 3.11

**Primary Dependencies**: Reflex (Frontend)

**Storage**: N/A

**Testing**: Revisión manual (visual/en código)

**Target Platform**: Web (Escritorio y Móvil)

**Project Type**: Web Application

**Performance Goals**: N/A

**Constraints**: Z-Index en 1100, no obstruir acciones (Pointer-Events), oculto en dispositivos táctiles.

**Scale/Scope**: Revisión de ~15+ módulos de `src/presentacion_reflex/pages`.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **SISTEMA DE DISEÑO**: Asegurar que los tooltips usen `neuro_tooltip` para respetar colores base y fuentes del Claude/Anthropic Design System.
- **VERIFICACIÓN EN NAVEGADOR Y UI**: Evitar sobreescrituras ad-hoc.
- **GESTIÓN DE SUPERPOSICIONES (RADIX UI)**: Mantener `Z_TOOLTIP=1100` y `pointer-events: auto` centralizado en `BASE_STYLE`.

## Project Structure

### Documentation (this feature)

```text
specs/023-auditoria-tooltips-faltantes/
├── plan.md              # This file (/speckit-plan command output)
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
└── tasks.md             # Phase 2 output (/speckit-tasks command)
```

### Source Code (repository root)

```text
src/
└── presentacion_reflex/
    ├── components/
    │   └── neuro_elements.py
    └── pages/
        ├── ... (Módulos a auditar)
```

**Structure Decision**: Se intervendrán directamente los archivos dentro de `src/presentacion_reflex/pages` inyectando código en línea sin crear nuevos módulos de arquitectura.

## Complexity Tracking

No aplica. No hay violaciones ni deudas técnicas generadas por esta tarea.
