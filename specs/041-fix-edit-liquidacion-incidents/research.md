# Research: Fix Edit Liquidación Incidents Loading

**Feature**: 041-fix-edit-liquidacion-incidents
**Date**: 2026-07-10

## Research Tasks

### R1: Root Cause Analysis — Why incidents don't display in edit modal

**Decision**: The edit modal only shows `valor_incidentes` (monetary total), not individual incidents.

**Rationale**: Traced the complete data flow:
1. `open_edit_modal(id_liquidacion)` calls `servicio.obtener_detalle_liquidacion_ui(id_liquidacion)`
2. This delegates to `repo_liquidacion.obtener_datos_para_pdf(id_liquidacion)` (line 1232)
3. The SQL query returns `l.*` from LIQUIDACIONES, which includes `VALOR_INCIDENTES` and `OBSERVACIONES`
4. The mapping (line 1339, 1342) correctly returns these fields
5. `open_edit_modal` populates `form_data` with `valor_incidentes` and `observaciones` (lines 656-657)
6. The edit form displays `valor_incidentes` as a numeric field and `observaciones` as a textarea

**The problem**: There is NO code to fetch and display the LIST of individual incidents associated with the liquidation via the `INCIDENTE_LIQUIDACION` join table. The modal only shows the aggregate monetary value.

**Alternatives considered**:
- Alternative A: Fetch incidents inside `open_edit_modal` and store in a new state var → **Selected** (cleanest separation of concerns)
- Alternative B: Modify `obtener_datos_para_pdf` to include incident list → Rejected (violates Out of Scope: no persistence layer changes)
- Alternative C: Create a new API endpoint → Rejected (unnecessary complexity for a frontend-only fix)

### R2: How to fetch associated incidents for display

**Decision**: Add a new event handler `cargar_incidentes_asociados(id_liquidacion)` that queries the `INCIDENTE_LIQUIDACION` join table and joins with `INCIDENTES` to get descriptions.

**Rationale**: The repository `RepositorioIncidenteLiquidacionPostgres.obtener_por_liquidacion(id_liquidacion)` already exists and returns `List[IncidenteLiquidacion]` objects. However, it only returns relationship data (id_incidente, valor_descuento, etc.), not the incident descriptions. We need to either:
1. Use the existing method + a second query to get incident details, OR
2. Write a direct SQL query in the state handler that JOINs both tables

**Selected approach**: Option 2 — Direct SQL query in the state handler, similar to the pattern used in `open_seleccion_incidentes_modal` (line 2083-2122). This avoids modifying the repository layer (Out of Scope) and follows existing patterns.

### R3: Observations field — Is it actually broken?

**Decision**: The observations field likely works correctly. The user may be confused by the incidents field being empty.

**Rationale**: 
- `observaciones` is loaded into `form_data` at line 656: `"observaciones": str(liquidacion.get("observaciones", ""))`
- The textarea at line 194-200 uses `default_value=LiquidacionesState.form_data["observaciones"]`
- If the DB has a non-null OBSERVACIONES value, it should display

**However**, there's a potential issue: if `observaciones` is `None` in the DB, `str(None)` becomes the string `"None"`, which would display incorrectly. The code does `str(liquidacion.get("observaciones", ""))` which returns `""` only if the key is missing, not if the value is `None`.

**Fix**: Change to `str(liquidacion.get("observaciones") or "")` to handle `None` values correctly.

### R4: How to display incidents in the edit modal

**Decision**: Add a read-only table/list below the "Seleccionar Incidentes" button showing currently associated incidents.

**Rationale**: The edit modal should show what's already associated so the user can verify. The existing `modal_seleccion_incidentes.py` shows AVAILABLE incidents for association. We need a SEPARATE display for ALREADY ASSOCIATED incidents.

**Design**:
- New state var: `incidentes_asociados_liquidacion: List[Dict[str, Any]]` — populated when modal opens
- New state var: `loading_incidentes_asociados: bool` — loading indicator
- New event handler: `cargar_incidentes_asociados(id_liquidacion)` — fetches via SQL JOIN
- UI: A simple table/list showing: ID, Descripción, Estado, Estado Pago, Valor Descuento
- The "Seleccionar Incidentes" button remains for ADDING new incidents

### R5: State variable management for associated incidents

**Decision**: Store associated incidents in a new state var `incidentes_asociados_liquidacion` on `LiquidacionesState`.

**Rationale**: Following the existing pattern where modal-related data is stored on the state (e.g., `seleccion_incidentes_disponibles`, `seleccion_incidentes_seleccionados`). The new var will be:
- Populated in `open_edit_modal` after loading the liquidation detail
- Cleared in `close_modal` when the modal closes
- Displayed in the edit form component

**Alternatives considered**:
- Alternative A: Store on LiquidacionesState → **Selected** (consistent with existing patterns)
- Alternative B: Create a separate state class → Rejected (overkill for this scope)

## Summary of Decisions

| Decision | Choice | Impact |
|----------|--------|--------|
| Root cause | Missing incident list display, not a data loading bug | Requires new UI component + state handler |
| Fetch approach | Direct SQL in state handler (no repo changes) | Out of Scope preserved |
| Observations fix | Handle None → empty string | Small code fix in open_edit_modal |
| Display design | Read-only table of associated incidents | New UI section in edit modal |
| State management | New vars on LiquidacionesState | Consistent with existing patterns |
