# Phase 0: Research

## Unknowns & Clarifications
All ambiguities have been reviewed. The core issue is a data mapping / deserialization regression due to PostgreSQL case-sensitivity rules for unquoted identifiers in raw SQL queries.

## Findings
1. **Case-Sensitivity in `psycopg2.extras.DictCursor`**: 
   - PostgreSQL lowercases all unquoted identifiers (like `ID_INCIDENTE`) in the result set.
   - The queries in `liquidaciones_state.py` for `cargar_incidentes_asociados` and `open_seleccion_incidentes_modal` attempt to access uppercase keys (e.g., `row["ID_INCIDENTE"]`, `row_prop["ID_PROPIEDAD"]`), causing `KeyError`.
   - **Decision**: Update the dictionary access to use lowercase keys (e.g., `row["id_incidente"]`) or use `.get()` with lowercase fallback to ensure compatibility and robustness.

2. **Nested Modals & Pointer Events (Radix UI)**:
   - The user reported the selection/detail modal is not deploying. While the `KeyError` explains why data is empty, if the modal literally doesn't appear, it could be a Radix UI nested dialog issue.
   - The `modal_seleccion_incidentes.py` has an inline style: `style={"pointer_events": "auto", "z_index": styles.Z_POPOVER}`.
   - The project constitution dictates that `pointer-events` overrides must be centralized in `BASE_STYLE`.
   - **Decision**: Ensure that the secondary modal respects the `BASE_STYLE` and that the state correctly triggers its visibility without conflicting with the active edit modal.

3. **Data Integrity & Consistency**:
   - The `cargar_incidentes_asociados` function fails silently (catches `Exception` and empties the list).
   - The `open_seleccion_incidentes_modal` function also fails on `ID_PROPIEDAD` lookup, setting an error state but failing to load incidents.
   - **Decision**: Fix all uppercase dictionary keys in `liquidaciones_state.py` relating to incidents in liquidations.

## Technical Approach
- Modify `liquidaciones_state.py` to fix dictionary key access in `cargar_incidentes_asociados` and `open_seleccion_incidentes_modal`.
- Review `modal_seleccion_incidentes.py` to align its `style` props with the `BASE_STYLE` guidelines.
