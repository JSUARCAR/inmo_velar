# Implementation Plan: Fix Grupo de Pago Contratos

**Branch**: `feature/067-fix-grupo-pago-contratos` | **Date**: 2026-09-02 | **Spec**: `specs/067-fix-grupo-pago-contratos/spec.md`

**Input**: Feature specification from `specs/067-fix-grupo-pago-contratos/spec.md`

## Summary

Desarrollo de un script de migración PostgreSQL para recalibrar los campos `grupo_operativo` y `fecha_pago` de los contratos de Mandato en estado ACTIVO, asegurando alineación con la nueva lógica (Versión 2.0) en `CalculadoraContratos.calcular_ciclo_pago_mandato`.

## Technical Context

**Language/Version**: Python 3.x (Reflex Backend)

**Primary Dependencies**: `psycopg2` / DB Manager del proyecto, Módulo de Dominio (`CalculadoraContratos`)

**Storage**: PostgreSQL

**Testing**: Ejecución en BD local / Validación de Output Auditado

**Target Platform**: Backend Script (CLI/Local)

**Project Type**: Data Migration Script

**Performance Goals**: Procesar contratos en un único bloque transaccional

**Constraints**: Atomicidad obligatoria (`BEGIN; COMMIT/ROLLBACK`), No afectar contratos históricos/Arrendamientos

**Scale/Scope**: < 1000 contratos activos, script de ejecución única

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Arquitectura**: El script usará `src/dominio/servicios/calculadora_contratos.py` como única fuente de verdad (cumple Clean Architecture).
- **Ingeniería de Datos**: Se usará PostgreSQL y placeholders `%s` si se hace SQL directo, pero idealmente se inyectarán las clases de Repositorio o se usará `db_manager`. (Validar en Fase 0).
- **Atomicidad**: El script debe implementar el manejo transaccional explícito exigido en la sección de Higiene y Calidad.
- **Zero Deferred Cleanup**: Se aplicará y verificará al 100% de registros con anomalías identificados (ID 56, 47, etc).

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)
<!--
  ACTION REQUIRED: Replace the placeholder tree below with the concrete layout
  for this feature. Delete unused options and expand the chosen structure with
  real paths (e.g., apps/admin, packages/something). The delivered plan must
  not include Option labels.
-->

```text
# [REMOVE IF UNUSED] Option 1: Single project (DEFAULT)
src/
├── models/
├── services/
├── cli/
└── lib/

tests/
├── contract/
├── integration/
└── unit/

# [REMOVE IF UNUSED] Option 2: Web application (when "frontend" + "backend" detected)
backend/
├── src/
│   ├── models/
│   ├── services/
│   └── api/
└── tests/

frontend/
├── src/
│   ├── components/
│   ├── pages/
│   └── services/
└── tests/

# [REMOVE IF UNUSED] Option 3: Mobile + API (when "iOS/Android" detected)
api/
└── [same as backend above]

ios/ or android/
└── [platform-specific structure: feature modules, UI flows, platform tests]
```

**Structure Decision**: [Document the selected structure and reference the real
directories captured above]

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |
