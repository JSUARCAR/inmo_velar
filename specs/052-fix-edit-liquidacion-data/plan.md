# Implementation Plan: Corrección de Carga de Datos en Edición de Liquidaciones

**Branch**: `052-fix-edit-liquidacion-data` | **Date**: 2026-07-13 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/052-fix-edit-liquidacion-data/spec.md`

## Summary

Corrección de bug en el módulo Liquidación de Asesores donde la acción Editar no carga la totalidad de Propiedades a Liquidar (contratos asociados) ni los Descuentos Guardados para liquidaciones recién generadas. La investigación de ingeniería inversa revela que el flujo de generación multi-contrato guarda contratos y descuentos en una transacción, pero existen puntos de fallo silencioso en la persistencia que pueden causar datos parciales. La corrección incluye: (1) blindaje de persistencia atómica, (2) verificación de integridad post-generación, (3) script de migración para reconstruir datos faltantes en liquidaciones afectadas.

## Technical Context

**Language/Version**: Python 3.11+

**Primary Dependencies**: Reflex (UI), psycopg2 (PostgreSQL), Pydantic (DTOs)

**Storage**: PostgreSQL (hosted en Railway)

**Testing**: pytest, pruebas manuales en navegador

**Target Platform**: Web application (Railway deployment)

**Project Type**: web-application (Reflex frontend + Python backend)

**Performance Goals**: Restaurar comportamiento correcto existente (sin targets nuevos de performance)

**Constraints**: No introducir regresiones en liquidaciones históricas que funcionan correctamente

**Scale/Scope**: ~50+ asesores, ~200+ liquidaciones/mes, 3-10 propiedades por liquidación

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| Clean Architecture (Dominio → Aplicación → Infraestructura → Presentación) | ✅ PASS | Corrección toca Aplicación (servicio) e Infraestructura (repositorio), sin romper capas |
| Snake_case / PascalCase | ✅ PASS | Nomenclatura existente se mantiene |
| PostgreSQL Native (%s placeholders) | ✅ PASS | Repositorios ya usan %s |
| Spanish-only codebase | ✅ PASS | Todo el código está en español |
| Atomicidad en persistencia | ⚠️ REVIEW | La generación multi-contrato abre transacción pero los descuentos se agregan con `agregar_descuento` que puede abrir transacción propia |
| Zero deferred cleanup | ✅ PASS | Fix es cleanup diferido que ya no puede postergarse |
| Stop-the-line | ✅ PASS | Bug阻塞 funcionalidad core |

## Project Structure

### Documentation (this feature)

```text
specs/052-fix-edit-liquidacion-data/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
└── checklists/
    └── requirements.md  # Quality checklist
```

### Source Code (repository root)

```text
src/
├── dominio/
│   ├── entidades/
│   │   ├── liquidacion_asesor.py      # Entidad LiquidacionAsesor
│   │   ├── descuento_asesor.py        # Entidad DescuentoAsesor
│   │   └── bonificacion_asesor.py     # Entidad BonificacionAsesor
│   └── interfaces/
│       └── repositorio_liquidacion.py # Interface IRepositorioLiquidacion
├── aplicacion/
│   └── servicios/
│       └── servicio_liquidacion_asesores.py  # ServicioLiquidacionAsesores
├── infraestructura/
│   ├── repositorios/
│   │   ├── repositorio_liquidacion_asesor.py   # CRUD liquidaciones + contratos
│   │   ├── repositorio_descuento_asesor.py     # CRUD descuentos
│   │   └── repositorio_bonificacion_asesor.py  # CRUD bonificaciones
│   └── persistencia/
│       └── database.py                          # DatabaseManager
└── presentacion_reflex/
    └── state/
        └── liquidacion_asesores/
            └── form_state.py             # LiquidacionFormState (edit modal)
```

**Structure Decision**: Se mantiene la estructura existente. La corrección toca archivos existentes en las capas de Aplicación, Infraestructura y Presentación.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| (none) | Corrección de bug existente, no nueva arquitectura | N/A |

## Phase 0: Research

**Complete**: [research.md](./research.md)

### Key Findings

1. **Root Cause**: Transaction nesting issue — `agregar_descuento()` opens its own transaction inside the generation transaction, potentially causing discount INSERTs to fail or commit independently.

2. **Missing Table Definition**: `LIQUIDACIONES_CONTRATOS` table is not defined in the main schema file, only referenced in migrations.

3. **JOIN Integrity Risk**: The edit query uses INNER JOINs to multiple tables; if any referenced record is deleted, rows are silently dropped.

4. **Hypothesis H1 (HIGH)**: Nested transaction in `agregar_descuento()` causes discounts to not persist within the generation transaction.

## Phase 1: Design

**Complete**: [data-model.md](./data-model.md), [quickstart.md](./quickstart.md)

### Data Model

4 entities identified with full schema, relationships, and validation rules. See [data-model.md](./data-model.md).

### Fix Strategy

| Layer | Fix | File |
|-------|-----|------|
| Infraestructura | Ensure `guardar_contratos_liquidacion()` and `agregar_descuento()` reuse outer transaction | `repositorio_liquidacion_asesor.py`, `repositorio_descuento_asesor.py` |
| Aplicación | Add post-generation verification step | `servicio_liquidacion_asesores.py` |
| Aplicación | Add resilience in `obtener_detalle_completo()` for partial data | `servicio_liquidacion_asesores.py` |
| Migración | Script to reconstruct missing LIQUIDACIONES_CONTRATOS and DESCUENTOS_ASESORES | New migration file |

### Validation

6 scenarios defined in [quickstart.md](./quickstart.md) covering: new liquidación edit, historical regression, single property, multiple discounts, migration verification, and save/re-edit consistency.
