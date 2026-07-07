# Implementation Plan: Corrección de Selección de Incidentes en Liquidaciones

**Branch**: `001-fix-liquidaciones-incidentes` | **Date**: 2026-07-06 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/001-fix-liquidaciones-incidentes/spec.md`

## Summary

Corrección de bugs en el módulo de Liquidaciones que afectan la funcionalidad de Selección de Incidentes. Los problemas identificados son: (1) el modal muestra incidentes de todas las propiedades en lugar de filtrar por la propiedad de la liquidación, y (2) al editar liquidaciones, los campos Incidentes y Observaciones no cargan valores previamente almacenados. La solución requiere modificar la consulta SQL en el método `open_seleccion_incidentes_modal` para filtrar por ID_PROPIEDAD, y asegurar que el formulario de edición cargue correctamente los datos existentes.

## Technical Context

**Language/Version**: Python 3.11+ / Reflex 0.6.x

**Primary Dependencies**: Reflex (UI framework), PostgreSQL (base de datos), Pydantic (validación de datos)

**Storage**: PostgreSQL (requiere `%s` como placeholder, prohíbe `?`)

**Testing**: pytest, tests de renderizado Reflex

**Target Platform**: Web application (Railway deployment)

**Project Type**: Web application (frontend + backend en un solo proyecto Reflex)

**Performance Goals**: Tiempo de carga del modal < 3 segundos

**Constraints**: 
- Relación 1:N: una liquidación puede tener múltiples incidentes
- Selección múltiple de incidentes en el modal
- Estrategia de última escritura con notificación para edición concurrente
- 100% español en código y documentación
- Arquitectura Clean Architecture (Dominio → Aplicación → Infraestructura → Presentación)
- Prohibido usar Flet o SQLite

**Scale/Scope**: Sistema inmobiliario existente con datos en producción

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| Clean Architecture (Capas unidireccionales) | ✅ PASS | Cambios en Presentación e Infraestructura sin romper dependencias |
| Idioma 100% Español | ✅ PASS | Todo el código y documentación en español |
| PostgreSQL Native (placeholders %s) | ✅ PASS | Consultas SQL usan %s correctamente |
| Mutaciones atómicas en UI | ✅ PASS | Estado maneja listas de forma inmutable |
| RBAC y Seguridad | ✅ PASS | No se requieren cambios en autenticación |
| Testing > 90% cobertura | ⚠️ REQUIRES | Tests unitarios y de integración requeridos |

## Project Structure

### Documentation (this feature)

```text
specs/001-fix-liquidaciones-incidentes/
├── plan.md              # Este archivo
├── research.md          # Fase 0: Investigación y decisiones
├── data-model.md        # Fase 1: Modelo de datos
├── quickstart.md        # Fase 1: Guía de validación
├── contracts/           # Fase 1: Contratos de interfaz
└── tasks.md             # Fase 2: Tareas (no creado por /speckit.plan)
```

### Source Code (repository root)

```text
src/
├── dominio/
│   ├── entidades/
│   │   ├── liquidacion.py
│   │   ├── incidente.py
│   │   └── incidente_liquidacion.py
│   └── interfaces/
│       ├── repositorio_liquidacion.py
│       ├── repositorio_incidentes.py
│       └── repositorio_incidente_liq.py
├── aplicacion/
│   └── servicios/
│       ├── servicio_liquidacion.py
│       ├── servicio_incidentes.py
│       └── servicio_incidente_liquidacion.py
├── infraestructura/
│   └── persistencia/
│       ├── repositorio_liquidacion_postgres.py
│       ├── repositorio_incidentes_postgres.py
│       └── repositorio_incidente_liq_postgres.py
└── presentacion_reflex/
    ├── state/
    │   └── liquidaciones_state.py
    └── components/
        └── liquidaciones/
            ├── modal_seleccion_incidentes.py
            └── liquidacion_edit_form.py
```

**Structure Decision**: Se mantiene la estructura existente del proyecto. Los cambios se concentran en:
- `liquidaciones_state.py`: Corregir consulta SQL y carga de datos
- `modal_seleccion_incidentes.py`: Ajustes menores de UI si es necesario
- `liquidacion_edit_form.py`: Verificar carga de campos

## Complexity Tracking

> **No hay violaciones de constitución que justificar**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| N/A | N/A | N/A |