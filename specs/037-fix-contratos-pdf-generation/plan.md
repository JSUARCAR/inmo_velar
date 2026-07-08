# Implementation Plan: Fix Contratos PDF Generation

**Branch**: `037-fix-contratos-pdf-generation` | **Date**: 2026-07-08 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/037-fix-contratos-pdf-generation/spec.md`

## Summary

Corregir error de PostgreSQL `column cm.responsable_deposito_id does not exist` que impide la generación de PDFs para Contratos de Mandato y Arrendamiento. La causa raíz es que la migración `migration_campos_extra_contratos.sql` nunca fue ejecutada, y además está incompleta (no agrega `RESPONSABLE_DEPOSITO_ID` a `CONTRATOS_ARRENDAMIENTOS`). Solución: actualizar la migración, ejecutarla, y mejorar el manejo de errores en la UI.

## Technical Context

**Language/Version**: Python 3.11+

**Primary Dependencies**: Reflex (UI), psycopg2 (PostgreSQL driver), ReportLab (PDF generation), num2words (number conversion)

**Storage**: PostgreSQL (Railway)

**Testing**: Verificación manual (1 Mandato + 1 Arrendamiento + 1 Paz y Salvo)

**Target Platform**: Web application (Linux server + browser)

**Project Type**: Web application (Full Stack - Reflex frontend + Python backend)

**Performance Goals**: < 5 segundos generación de PDF

**Constraints**: PostgreSQL nativo, Clean Architecture, 100% español

**Scale/Scope**: ~500 contratos activos, ~2000 contratos históricos

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Princípio | Status | Notas |
|-----------|--------|-------|
| Clean Architecture (Dominio → Aplicación → Infraestructura → Presentación) | ✅ PASS | Fix en capas Infraestructura (migración) y Presentación (error handling), sin violación de dependencias |
| PostgreSQL Native (placeholders %s, RETURNING id) | ✅ PASS | Migración usa SQL estándar, consultas existentes ya usan %s |
| Idioma 100% Español | ✅ PASS | Código, documentación y mensajes de error en español |
| snake_case / PascalCase | ✅ PASS | Nomenclatura existente correcta |
| Type Hints obligatorios | ✅ PASS | Repositorio y servicio ya tienen type hints |
| No `except Exception as e` genérico | ✅ PASS | Manejo de errores específico en PDF state |
| Cambios Atómicos (~100 líneas) | ✅ PASS | Fix: ~15 líneas migración + ~20 líneas error handling |
| Stop-the-Line | ✅ PASS | Bug crítico bloqueador, prioridad máxima |
| Spec-Driven Development | ✅ PASS | Especificación completada |

**Gate Result**: PASS — No violations detected.

## Project Structure

### Documentation (this feature)

```text
specs/037-fix-contratos-pdf-generation/
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
│   └── entidades/
│       ├── contrato_arrendamiento.py          # Entidad con responsable_deposito_id
│       └── contrato_mandato.py                # Entidad con responsable_deposito_id
├── aplicacion/
│   └── servicios/
│       └── servicio_contratos.py              # ← ARCHIVO A MODIFICAR (queries)
├── infraestructura/
│   ├── persistencia/
│   │   ├── repositorio_contrato_arrendamiento_postgres.py  # ← VERIFICAR
│   │   └── repositorio_contrato_mandato_postgres.py        # ← VERIFICAR
│   └── db/
│       └── migrations/
│           └── migration_campos_extra_contratos.sql  # ← ARCHIVO A MODIFICAR
└── presentacion_reflex/
    └── state/
        └── pdf_state.py                       # ← ARCHIVO A MODIFICAR (error handling)
```

**Structure Decision**: Fix distribuido en 3 capas:
1. **Infraestructura**: Migración SQL para agregar columnas faltantes
2. **Aplicación**: Verificar queries en servicio
3. **Presentación**: Mejorar manejo de errores en UI

## Complexity Tracking

> No violations — no justification needed.
