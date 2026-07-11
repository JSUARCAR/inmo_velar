# Implementation Plan: Ciclo Operativo en Módulo Recaudos

**Branch**: `045-ciclo-operativo-recaudos` | **Date**: 2026-07-11 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/045-ciclo-operativo-recaudos/spec.md`

## Summary

Agregar una columna "Ciclo Operativo" a la tabla principal del módulo Recaudos. El valor se obtiene del campo `GRUPO_OPERATIVO` de la tabla `CONTRATOS_MANDATOS`, accedido mediante un JOIN adicional en la consulta SQL del repositorio. El cambio afecta 4 archivos en capas Infraestructura, Aplicación y Presentación. No se modifican entidades de dominio ni esquemas de base de datos.

## Technical Context

**Language/Version**: Python 3.11+

**Primary Dependencies**: Reflex (framework UI), Pydantic (DTOs), psycopg2 (PostgreSQL driver)

**Storage**: PostgreSQL (sin cambios en schema)

**Testing**: Pruebas manuales + validación visual en navegador

**Target Platform**: Web (desktop + mobile responsive)

**Project Type**: Web application (Reflex + PostgreSQL)

**Performance Goals**: Incremento máximo 10% en tiempo de carga de la tabla de Recaudos

**Constraints**: Sin cambios en schema de BD, sin modificaciones a entidades de dominio, display-only

**Scale/Scope**: ~44 features existentes, módulo Recaudos con ~20 recaudos visibles por página

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| Clean Architecture (Dominio → Aplicación → Infraestructura → Presentación) | PASS | Campo se agrega en DTO (Aplicación), query en Repositorio (Infraestructura), UI en Presentación. Dominio no se toca. |
| 100% Español | PASS | Nombres de columnas, valores y comentarios en español |
| PostgreSQL Native (placeholders %s) | PASS | JOIN usa sintaxis PostgreSQL nativa |
| Contract-First (DTOs/Tipos antes de lógica) | PASS | RecaudoDTO se actualiza antes de la implementación lógica |
| Zero Deferred Cleanup | PASS | No se introduce deuda técnica |
| Sin dependencias circulares | PASS | Cambio es unidireccional: Repositorio → DTO → UI |

**Post-Phase 1 Re-check**: Todos los gates permanecen en PASS.

## Project Structure

### Documentation (this feature)

```text
specs/045-ciclo-operativo-recaudos/
├── plan.md              # Este archivo
├── research.md          # Fase 0: Investigación técnica
├── data-model.md        # Fase 1: Modelo de datos
├── quickstart.md        # Fase 1: Guía de validación
├── contracts/           # Fase 1: Contratos UI
│   └── ui-table-column.md
└── tasks.md             # Fase 2: Tareas (generado por /speckit-tasks)
```

### Source Code (archivos a modificar)

```text
src/
├── infraestructura/persistencia/
│   └── repositorio_recaudo.py          # JOIN + SELECT + mapeo dict
├── aplicacion/esquemas/
│   └── recaudo.py                       # RecaudoDTO + RecaudoMapper
├── presentacion_reflex/pages/
│   └── recaudos.py                      # Columna UI en tabla
└── presentacion_reflex/state/
    └── recaudos_state.py                # Sin cambios (dict se pasa completo)
```

**Structure Decision**: Se modifica la estructura existente siguiendo Clean Architecture. Los cambios son quirúrgicos en 3 archivos (Repositorio, DTO, UI Page). No se crean archivos nuevos ni se modifica la entidad de dominio.

## Complexity Tracking

No hay violaciones de constitución. Cambio de complejidad baja — display puro sobre consulta existente.
