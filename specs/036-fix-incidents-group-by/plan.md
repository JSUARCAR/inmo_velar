# Implementation Plan: Corrección GROUP BY en Módulo Incidentes

**Branch**: `036-fix-incidents-group-by` | **Date**: 2026-07-08 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/036-fix-incidents-group-by/spec.md`

## Summary

Corregir error de PostgreSQL `GROUP BY` en la consulta `listar_con_filtros` del repositorio de incidentes. La columna `cot.cotizaciones` (derivada de un `LEFT JOIN LATERAL`) no forma parte del `GROUP BY` ni está encapsulada en una función de agregación, violando la regla SQL estándar. La solución es eliminar el `GROUP BY` redundante ya que los `LATERAL JOINs` ya manejan la agregación correctamente sin duplicación.

## Technical Context

**Language/Version**: Python 3.11+

**Primary Dependencies**: Reflex (UI), psycopg2 (PostgreSQL driver), Pydantic (DTOs)

**Storage**: PostgreSQL ( Railway)

**Testing**: pytest, pruebas de integración con DB de prueba

**Target Platform**: Web application (Linux server + browser)

**Project Type**: Web application (Full Stack - Reflex frontend + Python backend)

**Performance Goals**: < 3 segundos carga del módulo para 1000 registros

**Constraints**: < 3s p95, PostgreSQL nativo, Clean Architecture

**Scale/Scope**: ~1000 incidentes, ~5000 cotizaciones

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Princípio | Status | Notas |
|-----------|--------|-------|
| Clean Architecture (Dominio → Aplicación → Infraestructura → Presentación) | ✅ PASS | Fix en capa Infraestructura (repositorio), sin violación de dependencias |
| PostgreSQL Native (placeholders %s, RETURNING id) | ✅ PASS | Consulta existente ya usa %s y RETURNING |
| Idioma 100% Español | ✅ PASS | Código y documentación en español |
| snake_case / PascalCase | ✅ PASS | Nomenclatura existente correcta |
| Type Hints obligatorios | ✅ PASS | Repositorio ya tiene type hints |
| No `except Exception as e` genérico | ✅ PASS | Manejo de errores específico |
| Cambios Atómicos (~100 líneas) | ✅ PASS | Fix es un solo método, < 50 líneas |
| Stop-the-Line | ✅ PASS | Bug crítico bloqueador, prioridad máxima |
| Spec-Driven Development | ✅ PASS | Especificación completada |

**Gate Result**: PASS — No violations detected.

## Project Structure

### Documentation (this feature)

```text
specs/036-fix-incidents-group-by/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
└── tasks.md             # Phase 2 output (/speckit.tasks)
```

### Source Code (repository root)

```text
src/
├── dominio/
│   ├── entidades/
│   │   └── incidente.py                    # Entidad Incidente (frozen dataclass)
│   └── interfaces/
│       └── repositorio_incidentes.py       # Interface Protocol
├── aplicacion/
│   └── servicios/
│       └── servicio_incidentes.py          # Servicio de orquestación
├── infraestructura/
│   ├── persistencia/
│   │   └── repositorio_incidentes_postgres.py  # ← ARCHIVO A MODIFICAR
│   └── db/
│       └── schema_incidentes.sql           # Schema PostgreSQL
└── presentacion_reflex/
    └── state/
        └── incidentes/
            ├── incidentes_base.py          # Estado Reflex
            └── incidentes_eventos.py       # Eventos UI
```

**Structure Decision**: Fix localizado en `src/infraestructura/persistencia/repositorio_incidentes_postgres.py`, método `listar_con_filtros`. No requiere cambios en otras capas.

## Complexity Tracking

> No violations — no justification needed.
