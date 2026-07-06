# Implementation Plan: Auditoría y Restauración de Componentes UI

**Branch**: `026-restore-ui-components` | **Date**: 2026-07-05 | **Spec**: [spec.md](file:///C:/Users/PC/OneDrive/Desktop/inmobiliaria%20velar/PYTHON-REFLEX/specs/026-restore-ui-components/spec.md)

**Input**: Feature specification from `/specs/026-restore-ui-components/spec.md`

## Summary

Auditar y reemplazar componentes de UI obsoletos o no estandarizados (inputs y botones) en 14 módulos clave de la plataforma por los componentes estandarizados `neuro_floating_input`, `neuro_floating_select`, `neuro_button` y `neuro_icon_action_button` implementando tooltips descriptivos inferidos y el comportamiento fallback para componentes complejos.

## Technical Context

**Language/Version**: Python 3.12

**Primary Dependencies**: Reflex 0.8.x

**Storage**: PostgreSQL

**Testing**: Mypy, Ruff, Black, manual visual validation

**Target Platform**: Navegador web (Despliegue en Railway)

**Project Type**: Web Application

**Performance Goals**: N/A (Mantenimiento de UI, rendimiento mejorado al usar CSS puro para labels en lugar de estado condicional de Python)

**Constraints**: Respetar `Z_TOOLTIP=1100` y transiciones definidas en `styles.py`.

**Scale/Scope**: 14 archivos/módulos en `src/presentacion_reflex/components/`.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Arquitectura**: UI (Presentación). Cumple con aislamiento de capas.
- **Tipado explícito**: Todos los componentes y kwargs seguirán usando type hints.
- **Limpieza de variables**: No hay filtración de secrets.
- **Validación final local**: Prevista en los comandos de quickstart (Reflex dev mode).

## Project Structure

### Documentation (this feature)

```text
specs/026-restore-ui-components/
├── plan.md              
├── research.md          
├── data-model.md        
├── quickstart.md        
└── contracts/           
```

### Source Code (repository root)

```text
src/
└── presentacion_reflex/
    ├── components/
    │   ├── asambleas/
    │   ├── contratos/
    │   ├── dashboard/
    │   ├── desocupaciones/
    │   ├── incidentes/
    │   ├── liquidacion_asesores/
    │   ├── liquidaciones/
    │   ├── personas/
    │   ├── propiedades/
    │   ├── proveedores/
    │   ├── recaudos/
    │   ├── recibos/
    │   ├── seguros/
    │   └── usuarios/
    └── views/
```

**Structure Decision**: El proyecto mantiene su estructura centralizada de módulos bajo `presentacion_reflex/components/` siguiendo la arquitectura limpia estipulada en la constitución. No se introducen nuevas capas estructurales, sino refactorización in-place.

## Complexity Tracking

N/A
