# Data Model: Estandarización de Filtros Avanzados con Floating Labels

**Date**: 2026-07-05
**Feature**: 017-advanced-filters-floating-labels

## Entity Analysis

This feature is purely a **UI/presentation layer change**. No database entities, relationships, or data structures are modified.

### Existing Entities (Unchanged)

The following state variables remain completely unchanged:

| Module | State Variables | Type |
|--------|----------------|------|
| Personas | `search_query`, `filtro_rol`, `filtro_fecha_desde`, `filtro_fecha_hasta`, `mostrar_inactivos`, `filtro_sin_contrato` | str, str, str, str, bool, bool |
| Propiedades | `search_text`, `filter_tipo`, `filter_disponibilidad`, `solo_activas` | str, str, str, bool |
| Contratos | `search_text`, `filter_tipo`, `filter_estado`, `filter_asesor_id`, `filter_sin_arrendamiento` | str, str, str, str, bool |
| Liquidaciones | `search_text`, `filter_periodo`, `filter_estado`, `filter_ciclo`, `filter_asesor` | str, str, str, str, str |
| Liq. Asesores | `search_text`, `filter_estado`, `filter_periodo`, `filter_asesor` | str, str, str, str |
| Recaudos | `search_text`, `filter_contrato_id`, `filter_estado`, `filter_fecha_desde`, `filter_fecha_hasta` | str, str, str, str, str |
| Desocupaciones | `filter_estado` | str |
| Incidentes | `search_text`, `filter_prioridad`, `filter_estado` | str, str, str |
| Seguros | `search_text`, `filter_estado` | str, str |
| Recibos | `search_text`, `filter_servicio`, `filter_estado` | str, str, str |
| Saldos a Favor | `filter_tipo`, `filter_estado` | str, str |
| Usuarios | `search_text`, `filter_rol`, `filter_estado` | str, str, str |
| Reportes | `search_text`, `selected_report_id`, dynamic filter vars | str, str, various |

### Data Flow (Unchanged)

```
User Input → Component (value/on_change) → State Variable → Filter Logic → Table/List Update
```

The only change is the **Component** layer: `neuro_input`/`neuro_select_root` → `neuro_floating_input`/`neuro_floating_select`. The state binding interface (`value`/`on_change`) is identical.

## Validation Rules (Unchanged)

No validation rules change. All existing filter validation remains intact:
- Empty strings trigger "show all" behavior
- Select options filter by exact match
- Date ranges filter by comparison

## State Transitions (Unchanged)

No state transitions change. Filter states remain:
- `idle` → `filtering` (when user types/selects)
- `filtering` → `idle` (when filter is cleared)
