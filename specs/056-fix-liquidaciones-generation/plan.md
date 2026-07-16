# Implementation Plan: Corrección Generación de Liquidaciones de Propietarios

**Branch**: `056-fix-liquidaciones-generation` | **Date**: 2026-07-15 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/056-fix-liquidaciones-generation/spec.md`

## Summary

Corregir el flujo de generación de liquidaciones individuales y masivas en el módulo de Liquidaciones de Propietarios. La causa raíz identificada es que `generar_liquidacion_propietario()` lanza `ValueError` cuando todos los contratos ya tienen liquidaciones para el período, y el handler de masiva (`generar_liquidacion_masiva`) clasifica esto como "error" en lugar de "omitido". El fix requiere: (1) modificar el retorno de `generar_liquidacion_propietario` para distinguir entre generadas, omitidas y errores; (2) actualizar el handler masivo para rastrear tres contadores; (3) actualizar el toast de resultado para mostrar la información correcta.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: Reflex (framework UI), psycopg2 (PostgreSQL driver)
**Storage**: PostgreSQL ( Railway)
**Testing**: pytest
**Target Platform**: Linux server (Railway deployment)
**Project Type**: web-application (Full-stack: Reflex frontend + Python backend)
**Performance Goals**: Generación masiva < 30s para 100 propietarios
**Constraints**: Clean Architecture (Dominio → Aplicación → Infraestructura → Presentación)
**Scale/Scope**: ~50 propiedades con contratos activos, ~20 propietarios

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| Clean Architecture (Capas unidireccionales) | ✅ PASS | Cambios en capa Aplicación (servicio) y Presentación (state), sin violar dependencias |
| PostgreSQL Native (PLACEHOLDERS %s) | ✅ PASS | No hay cambios en queries SQL |
| Idioma 100% Español | ✅ PASS | Todo el código y documentación en español |
| Type Hints obligatorios | ✅ PASS | Se mantienen en todas las firmas |
| Excepciones específicas (no `except Exception`) | ⚠️ REVISAR | State handler usa `except Exception` en línea 1113 - se debe refinar |
| Semantic Commits | ✅ PASS | Se usará `fix(liquidaciones): ...` |

## Project Structure

### Documentation (this feature)

```text
specs/056-fix-liquidaciones-generation/
├── plan.md              # Este archivo
├── research.md          # Phase 0: Análisis de causa raíz
├── data-model.md        # Phase 1: Modelo de datos afectado
├── quickstart.md        # Phase 1: Guía de validación
├── contracts/           # Phase 1: Contratos de interfaz
│   └── servicio-financiero.md
└── tasks.md             # Phase 2: Tareas de implementación
```

### Source Code (repository root)

```text
src/
├── aplicacion/servicios/
│   └── servicio_financiero.py          # FIX: generar_liquidacion_propietario()
├── presentacion_reflex/state/
│   └── liquidaciones_state.py          # FIX: generar_liquidacion_masiva()
└── dominio/entidades/
    └── liquidacion.py                  # Sin cambios (modelo estable)
```

**Structure Decision**: Los cambios están concentrados en dos archivos de la arquitectura existente: `servicio_financiero.py` (capa Aplicación) y `liquidaciones_state.py` (capa Presentación). No se crean nuevos archivos ni se modifica la estructura del proyecto.

## Complexity Tracking

> No hay violaciones de constitución que justificar. Los cambios son quirúrgicos dentro de la arquitectura existente.
