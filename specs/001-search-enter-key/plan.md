# Implementation Plan: Búsqueda con Tecla ENTER

**Branch**: `001-search-enter-key` | **Date**: 2026-07-08 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/001-search-enter-key/spec.md`

## Summary

Agregar soporte para ejecutar la búsqueda presionando la tecla ENTER en el campo "Buscar" de 7 módulos. El componente compartido `advanced_filter_bar` (used por los 7 módulos) actualmente solo tiene `on_change` en el `rx.input` sin soporte de teclado. La implementación requiere: (1) agregar parámetro `on_key_down` al componente compartido, (2) crear/conectar handlers `handle_search_key_down` en los estados que no lo tienen, y (3) garantizar que ENTER invoque la misma lógica de búsqueda que el botón existente.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: Reflex 0.6.x (framework UI full-stack)
**Storage**: PostgreSQL (no changes needed)
**Testing**: pytest, pruebas de renderizado Reflex
**Target Platform**: Web (desktop + mobile responsive)
**Project Type**: Web application (Reflex full-stack)
**Performance Goals**: Búsqueda响应 instantánea (<200ms percepción usuario)
**Constraints**: Reutilizar lógica existente del botón Buscar, sin duplicar código
**Scale/Scope**: 7 módulos, 1 componente compartido, ~3 archivos de estado a modificar

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| Clean Architecture (capas unidireccionales) | ✅ PASS | Cambio solo en capa de Presentación (UI + State) |
| 100% Español | ✅ PASS | Nombres de funciones y comentarios en español |
| Type Hints obligatorios | ✅ PASS | Se mantienen type hints existentes |
| Mutaciones atómicas en State | ✅ PASS | No se mutan listas/diccionarios in-place |
| Sin referencias a Flet/SQLite | ✅ PASS | Cambio solo en capa Reflex |
| Cambios atómicos (~100 líneas) | ✅ PASS | Cambio pequeño y focalizado |
| Spec-Driven Development | ✅ PASS | Especificación completa antes de implementar |

**Post-Phase 1 Re-check**: Sin violaciones. El cambio es puramente de presentación (UI event handling) sin afectar dominio, aplicación ni infraestructura.

## Project Structure

### Documentation (this feature)

```text
specs/001-search-enter-key/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output (UI contracts)
└── tasks.md             # Phase 2 output (NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
src/presentacion_reflex/
├── components/shared/
│   └── advanced_filter_bar.py    # MODIFICAR: agregar parámetro on_key_down
├── pages/
│   ├── personas.py               # MODIFICAR: wiring on_key_down al input
│   ├── propiedades.py            # MODIFICAR: wiring on_key_down al input
│   ├── contratos.py              # MODIFICAR: wiring on_key_down al input
│   ├── liquidaciones.py          # MODIFICAR: wiring on_key_down al input
│   ├── liquidacion_asesores.py   # MODIFICAR: wiring on_key_down al input
│   ├── recaudos.py               # MODIFICAR: wiring on_key_down al input
│   └── incidentes.py             # MODIFICAR: wiring on_key_down al input
├── state/
│   ├── personas_state.py         # Ya tiene handle_search_key_down (verificar wiring)
│   ├── propiedades_state.py      # AGREGAR: handle_search_key_down
│   ├── contratos_state.py        # AGREGAR: handle_search_key_down + search_contratos
│   ├── liquidaciones_state.py    # Ya tiene handle_search_key_down (verificar wiring)
│   ├── liquidacion_asesores/
│   │   └── filtros_state.py      # AGREGAR: handle_search_key_down
│   ├── recaudos_state.py         # Ya tiene handle_search_key_down (verificar wiring)
│   └── incidentes_state.py       # AGREGAR: handle_search_key_down
```

**Structure Decision**: El proyecto usa estructura de capas Clean Architecture con UI en `presentacion_reflex/`. El cambio es exclusivamente de presentación (componente compartido + wiring en páginas + handlers en state).

## Complexity Tracking

> No violations to justify. Change is minimal and focused.
