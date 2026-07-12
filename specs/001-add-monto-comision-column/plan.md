# Implementation Plan: Agregar Columna MONTO COMISIÓN a Liquidaciones

**Branch**: `feature/add-monto-comision-column` | **Date**: 2026-07-11 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/001-add-monto-comision-column/spec.md`

## Summary

Exponer la columna `COMISION_MONTO` (ya existente en la tabla `LIQUIDACIONES`) en la UI de la tabla de liquidaciones, posicionada entre CANON e IVA COMISIÓN. Incluye formateo COP, ordenamiento, tooltip con porcentaje de comisión, y scroll horizontal. No requiere migración de BD ni cambios en el cálculo del NETO A PAGAR (el campo ya se usa en la fórmula).

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: Reflex 0.6.x (UI), psycopg2 (PostgreSQL)
**Storage**: PostgreSQL (campo `COMISION_MONTO` ya existe en tabla `LIQUIDACIONES`)
**Testing**: pytest, Reflex render tests
**Target Platform**: Web (Railway deployment)
**Project Type**: Web application (Reflex + PostgreSQL)
**Performance Goals**: < 1s carga de tabla con scroll horizontal
**Constraints**: 100% Español, Clean Architecture, sin edit del MONTO COMISIÓN (solo display)
**Scale/Scope**: ~18 columnas en tabla, datos de liquidaciones mensuales

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| Clean Architecture (Capas) | PASS | Cambios en Persistencia → Dominio → UI, sin dependencias circulares |
| 100% Español | PASS | Nombres de variables, comentarios y UI en español |
| Type Hints obligatorios | PASS | Se mantendrán en todos los cambios |
| PostgreSQL Native (%s) | PASS | Sin cambios en queries SQL existentes, solo se agrega campo al SELECT |
| Sin Flet/SQLite | PASS | Proyecto ya migrado a Reflex/PostgreSQL |
| Design System | PASS | Se usa format_currency() existente y sistema de badges |
| Commits Conventional | PASS | feat(presentacion): agregar columna MONTO COMISIÓN |

**No violations detected. No justification needed.**

## Project Structure

### Documentation (this feature)

```text
specs/001-add-monto-comision-column/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── checklists/
│   └── requirements.md  # Quality checklist
└── tasks.md             # Phase 2 output (/speckit-tasks)
```

### Source Code (repository root)

```text
src/
├── dominio/
│   └── entidades/
│       └── liquidacion.py              # Entity (NO changes needed - comision_monto exists)
├── infraestructura/
│   └── persistencia/
│       └── repositorio_liquidacion_postgres.py  # ADD comision_monto to SELECT + sort
├── presentacion_reflex/
│   ├── pages/
│   │   └── liquidaciones.py            # ADD column header + cell + tooltip
│   ├── state/
│   │   └── liquidaciones_state.py      # ADD comision_monto fields to LiquidacionDict
│   └── utils/
│       └── formatters.py               # NO changes (format_currency reused)
```

**Structure Decision**: Cambios distribuidos en 3 archivos bajo la estructura Clean Architecture existente. Sin nuevos directorios ni archivos.

## Complexity Tracking

> No Constitution Check violations. No complexity tracking needed.

## Phase 0: Research

### Research Items

1. **Campo COMISION_MONTO en BD**: Ya existe como `INTEGER NOT NULL DEFAULT 0` en la tabla `LIQUIDACIONES`. No requiere migración.

2. **Campo COMISION_PORCENTAJE**: Almacenado como entero base 10000 (ej. 1500 = 15.00%). Necesario para el tooltip. Ya se incluye en el entity `Liquidacion` pero NO en el query `listar_paginado`.

3. **Formato COP**: `format_currency()` en `utils/formatters.py` ya formatea como `$X.XXX.XXX` (pesos colombianos, sin decimales). Reutilizable directamente.

4. **Scroll horizontal**: La tabla actual usa `rx.table.root`. El scroll horizontal se implementa envolviendo la tabla en un `rx.scroll_area` o usando `overflow_x="auto"` en el contenedor.

5. **Tooltips**: La tabla ya usa `rx.tooltip` para botones de acción. Se puede aplicar el mismo patrón a celdas de datos.

## Phase 1: Design & Contracts

### Data Model (data-model.md)

#### Entity: Liquidacion (existent, no changes)

| Field | DB Column | Type | Notes |
|-------|-----------|------|-------|
| comision_monto | COMISION_MONTO | INTEGER | Ya existe, DEFAULT 0 |
| comision_porcentaje | COMISION_PORCENTAJE | INTEGER | Base 10000 (1500 = 15%) |

#### State Model: LiquidacionDict (changes needed)

Add to existing Pydantic model:

```python
comision_monto: float
comision_monto_view: str
comision_porcentaje: float  # For tooltip calculation
```

### Interface Contracts

#### Repository Contract (IRepositorioLiquidacion)

No changes to interface. Internal implementation changes:
- `listar_paginado`: Add `l.COMISION_MONTO` to SELECT, add `comision_monto` to sort whitelist
- `listar_agrupadas_por_propietario_paginado`: Add `SUM(l.COMISION_MONTO)` to aggregation

#### UI Contract

Column spec:
- **Position**: Between CANON and IVA COMISIÓN (index 5, 0-based)
- **Header**: "Monto Comisión" (sortable, sort_key: `"comision_monto"`)
- **Cell**: Right-aligned, formatted as `$X.XXX.XXX`
- **Tooltip**: `"XX.XX% sobre canon"` (derived from `comision_porcentaje / 100`)
- **NULL handling**: Display as `$0` (same as zero)

### Quickstart Validation (quickstart.md)

1. Ejecutar `reflex run --env dev`
2. Navegar a `/liquidaciones`
3. Verificar columna "Monto Comisión" visible entre Canon e IVA Comisión
4. Verificar formateo COP ($X.XXX.XXX) en celdas
5. Verificar ordenamiento asc/desc al hacer click en header
6. Verificar tooltip con porcentaje al pasar cursor
7. Verificar scroll horizontal en viewport reducido
8. Verificar que NETO A PAGAR no cambia para registros existentes

## Files to Modify (ordered by dependency)

### 1. `src/infraestructura/persistencia/repositorio_liquidacion_postgres.py`

**Changes:**
- `listar_paginado` (lines 1601-1766): Add `l.COMISION_MONTO` to SELECT, add `comision_monto` to `SORT_COLUMNS` whitelist
- `listar_agrupadas_por_propietario_paginado` (lines 889-1117): Add `SUM(l.COMISION_MONTO) AS comision_monto` to aggregation, add to sort whitelist
- Both methods: Include `comision_porcentaje` in result for tooltip

### 2. `src/presentacion_reflex/state/liquidaciones_state.py`

**Changes:**
- `LiquidacionDict` (lines 12-48): Add `comision_monto: float`, `comision_monto_view: str`, `comision_porcentaje: float`
- `load_liquidaciones` (lines 309-404): Add `format_currency()` call for `comision_monto`, calculate percentage display

### 3. `src/presentacion_reflex/pages/liquidaciones.py`

**Changes:**
- `liquidaciones_table` (lines 327-519): Add column header after Canon, add cell rendering with tooltip
- `liquidaciones_table_agrupada` (lines 522-700): Add column header after Canon Total, add cell rendering
- Scroll horizontal: Wrap table in scrollable container
