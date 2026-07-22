# Implementation Plan: Ingeniería Inversa - Sincronización Contratos, Liquidaciones y Recaudos

**Branch**: `061-reverse-engineer-contracts-sync` | **Date**: 2026-07-22 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/061-reverse-engineer-contracts-sync/spec.md`

## Summary

Realizar ingeniería inversa sobre los módulos de Contratos, Liquidaciones de Propietarios y Recaudos para validar la correcta ejecución e integración de las reglas de negocio entre estos componentes. El entregable principal es un script repeatable que genera un informe de texto estructurado con pass/fail por criterio de éxito, ejecutable después de cada cambio de código.

## Technical Context

**Language/Version**: Python 3.11+

**Primary Dependencies**: Reflex 0.6+, Pydantic 2.5+, psycopg2-binary 2.9+, pytest 7.4+

**Storage**: PostgreSQL (prohibido SQLite en código nuevo)

**Testing**: pytest con pytest-cov para cobertura

**Target Platform**: Linux server (Railway deployment)

**Project Type**: Web application (Reflex frontend + FastAPI backend)

**Performance Goals**: Scripts de validación deben ejecutarse en < 30 segundos

**Constraints**: 100% español, Clean Architecture, sin placeholders, sin referencias Flet

**Scale/Scope**: Módulos financieros core: ContratosArrendamiento, ContratosMandatos, Liquidaciones, Recaudos

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| 100% Español | ✅ PASS | Todo el código y documentación en español |
| PostgreSQL Only | ✅ PASS | Sin SQLite en código nuevo |
| Clean Architecture | ✅ PASS | Respetar capas Dominio → Aplicación → Infraestructura |
| No Flet References | ✅ PASS | Sin referencias Flet |
| Type Hints | ✅ PASS | Obligatorios en todas las firmas |
| Google Style Docstrings | ✅ PASS | Para servicios clave |
| No Placeholders | ✅ PASS | Sin implementaciones temporales |
| RBAC | ⚠️ N/A | Scripts de validación no requieren RBAC |
| Testing > 90% | ✅ PASS | Tests para validación de integridad |

**Gate Result**: PASS - No violations detected

## Project Structure

### Documentation (this feature)

```text
specs/061-reverse-engineer-contracts-sync/
├── spec.md              # Feature specification
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
└── tasks.md             # Phase 2 output (/speckit.tasks)
```

### Source Code (repository root)

```text
src/
├── dominio/
│   └── entidades/
│       ├── contrato_arrendamiento.py
│       ├── contrato_mandato.py
│       ├── renovacion_contrato.py
│       ├── liquidacion.py
│       └── recaudo.py
├── aplicacion/
│   └── servicios/
│       ├── servicio_contrato_arrendamiento.py
│       ├── servicio_contrato_mandato.py
│       ├── servicio_financiero.py
│       └── servicio_recaudo.py
├── infraestructura/
│   └── repositorios/
│       ├── repositorio_liquidacion_postgres.py
│       ├── repositorio_recaudo.py
│       └── repositorio_renovacion_postgres.py
└── scripts/
    ├── recalcular_contratos_elite.py
    └── recalculate_totals.py

tests/
├── integration/
│   └── test_sincronizacion_contratos.py  # NEW: Tests de integración
├── unit/
│   └── test_validacion_cascada.py        # NEW: Tests de cascada
└── verification/
    └── audit_sincronizacion.py           # NEW: Script de auditoría
```

**Structure Decision**: Se mantiene la estructura existente de Clean Architecture. Los nuevos archivos de validación se agregan en `tests/integration/`, `tests/unit/` y `tests/verification/` según corresponda.

## Complexity Tracking

> No violations to justify - Constitution Check passed cleanly.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| N/A | N/A | N/A |
