# Implementation Plan: Filtros Avanzados Recaudos - Pago Contrato y Ciclo Operativo

**Branch**: `047-recaudos-filtros-avanzados` | **Date**: 2026-07-11 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/047-recaudos-filtros-avanzados/spec.md`

## Summary

Incorporar dos nuevos filtros avanzados en el módulo Recaudos: **Pago Contrato** (día de pago numérico del contrato, multi-select OR) y **Ciclo Operativo** (grupo operativo desde Liquidación de Propietarios, multi-select OR). El filtro Pago Contrato ya existe parcialmente en el state pero no está conectado a la UI; necesita upgrade a multi-select. El filtro Ciclo Operativo es completamente nuevo. Ambos filtros se compondrán con AND entre sí y con los filtros existentes.

## Technical Context

**Language/Version**: Python 3.11+

**Primary Dependencies**: Reflex (UI framework), PostgreSQL (database), psycopg2 (driver)

**Storage**: PostgreSQL

**Testing**: pytest, pruebas de renderizado Reflex

**Target Platform**: Web application (Railway deployment)

**Project Type**: web-application

**Performance Goals**: Combined filter queries <5s para 10,000 registros

**Constraints**: Clean Architecture (Dominio → Aplicación → Infraestructura → Presentación), PostgreSQL nativo (%s placeholders), 100% español

**Scale/Scope**: Módulo Recaudos existente con ~6 archivos a modificar

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Regla | Estado | Notas |
|-------|--------|-------|
| Clean Architecture (capas unidireccionales) | ✅ PASS | Cambios en Presentación → Dominio → Infraestructura, sin violaciones |
| PostgreSQL nativo (%s placeholders) | ✅ PASS | Queries existentes usan %s; nuevos filtros seguirán patrón |
| Naming (snake_case/PascalCase) | ✅ PASS | Nuevas variables y funciones seguirán convención |
| 100% Español | ✅ PASS | Todo el código y documentación en español |
| Mutaciones atómicas (Reflex) | ✅ PASS | State changes serán atómicas |
| Sin Flet/SQLite | ✅ PASS | No se introduce ninguna referencia a Flet o SQLite |
| Type Hints obligatorios | ✅ PASS | Todas las firmas nuevas incluirán type hints |
| RBAC | ✅ PASS | Filtros son de solo lectura; no requieren roles adicionales |

**Resultado**: Todos los gates pasan. No hay violaciones que justificar.

## Project Structure

### Documentation (this feature)

```text
specs/047-recaudos-filtros-avanzados/
├── plan.md              # Este archivo
├── research.md          # Fase 0: decisiones técnicas
├── data-model.md        # Fase 1: modelo de datos y joins
├── quickstart.md        # Fase 1: guía de validación
├── contracts/           # Fase 1: contratos de interfaz
└── tasks.md             # Fase 2: tareas (/speckit-tasks)
```

### Source Code (repository root)

```text
src/
├── dominio/
│   └── interfaces/
│       └── repositorio_recaudo.py    # FiltrosRecaudo: agregar List[str] para dia_pago y ciclo_operativo
├── aplicacion/
│   └── servicios/
│       └── servicio_recaudo.py       # Pasar nuevos parámetros de filtro
├── infraestructura/
│   └── persistencia/
│       └── repositorio_recaudo.py    # SQL: IN (...) para multi-select OR
└── presentacion_reflex/
    ├── state/
    │   └── recaudos_state.py         # State: filter_dia_pago List[str], filter_ciclo_operativo List[str]
    ├── pages/
    │   └── recaudos.py               # UI: agregar selectores en toolbar
    └── components/shared/
        └── advanced_filter_bar.py    # Componente: posible multi-select chip
```

**Structure Decision**: Proyecto Reflex existente con Clean Architecture. Los cambios afectan 6 archivos en 4 capas. No se crean nuevos archivos de lógica de negocio; solo se extienden interfaces y consultas existentes.
