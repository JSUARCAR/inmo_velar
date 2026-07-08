# Data Model: standardize-advanced-filters

**Date**: 2026-07-07

## Overview

This feature is a **UI-only standardization** — no database schema changes, no new entities, no migrations.

This document describes the **filter state interface** that the new `AdvancedFilterBar` component expects from each module's State class.

## Filter State Interface

Each module must expose the following state variables for the `AdvancedFilterBar` to manage:

### Required State Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `search_text` | `str` | `""` | Search query text |
| `_active_filter_count` | `int` | `0` | Computed count of non-default filter values (read-only) |

### Module-Specific Filter Variables (Examples)

Each module defines its own filter state variables. The `AdvancedFilterBar` does not need to know about them — it only receives the filter components as children.

#### Personas

| Variable | Type | Default |
|----------|------|---------|
| `filtro_rol` | `str` | `"Todos"` |
| `fecha_inicio` | `str` | `""` |
| `fecha_fin` | `str` | `""` |
| `mostrar_inactivos` | `bool` | `False` |
| `filtro_sin_contrato` | `bool` | `False` |

#### Propiedades

| Variable | Type | Default |
|----------|------|---------|
| `filter_tipo` | `str` | `"Todos"` |
| `filter_disponibilidad` | `str` | `"Todos"` |

#### Contratos

| Variable | Type | Default |
|----------|------|---------|
| `filter_asesor_id` | `str` | `"Todos"` |
| `filter_tipo` | `str` | `"Todos"` |
| `filter_estado` | `str` | `"ACTIVO"` |
| `filter_sin_arrendamiento` | `bool` | `False` |

#### Liquidaciones

| Variable | Type | Default |
|----------|------|---------|
| `filter_periodo` | `str` | `"Todos"` |
| `filter_estado` | `str` | `"Todos"` |
| `filter_ciclo_operativo` | `str` | `"Todos"` |
| `filter_asesor_id` | `str` | `"Todos"` |
| `vista_agrupada` | `bool` | `False` |

#### Liquidación de Asesores

| Variable | Type | Default |
|----------|------|---------|
| `filter_periodo` | `str` | `"Todos"` |

#### Recaudos

| Variable | Type | Default |
|----------|------|---------|
| `filter_estado` | `str` | `"Todos"` |
| `filter_fecha_desde` | `str` | `""` |
| `filter_fecha_hasta` | `str` | `""` |

#### Incidentes

| Variable | Type | Default |
|----------|------|---------|
| `filter_prioridad` | `str` | `"Todas"` |
| `filter_estado` | `str` | `"Todos"` |
| `filter_estado_pago` | `str` | `"Todos"` |

## State Transition Rules

- All filter variables reset to their default values when the "Limpiar" button is pressed.
- `search_text` resets to `""`.
- `filtro_*` / `filter_*` variables reset to their default string values.
- Boolean toggles (`mostrar_inactivos`, `vista_agrupada`, etc.) reset to `False`.
- Filter changes trigger automatic data re-fetch (no manual "Apply" button).

## Active Filter Count Calculation

The `AdvancedFilterBar` component will compute `_active_filter_count` by counting how many filter children have non-default values. This is used for the badge on the "Limpiar" button.

Logic:
```
active_count = 0
for each filter child:
    if filter.value != filter.default_value:
        active_count += 1
```
