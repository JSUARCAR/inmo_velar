# Implementation Tasks: bugfix-liquidaciones-incidentes

**Feature**: bugfix-liquidaciones-incidentes
**Total Tasks**: 3
**Tasks per Story**: US1: 3
**Parallel Opportunities**: T001 and T002 can be done together or in parallel.

## MVP Scope
User Story 1 provides the complete fix for the regression, resolving the silent failures during incident data fetching for liquidations.

## Dependencies
- US1 (Fix Incident Visualization & Selection Modal) -> None

---

## Phase 1: Setup
*No setup tasks required. Project infrastructure is already in place.*

---

## Phase 2: Foundational
*No foundational tasks required.*

---

## Phase 3: [US1] Diagnóstico y Visualización de Incidentes en Edición de Liquidación

**Story Goal**: Fix the KeyError exceptions caused by PostgreSQL lowercasing unquoted identifiers, restoring the incident visualization in the edit modal and the proper deployment of the selection modal.
**Independent Test Criteria**: Open a liquidation with incidents in the UI. The edit modal should list the incidents properly, and the "Seleccionar Incidentes" modal should open without errors.

### Implementation Tasks

- [x] T001 [US1] Fix dictionary key case in `cargar_incidentes_asociados` by converting uppercase keys (e.g., `row["ID_INCIDENTE"]`) to lowercase or using `.get()` in `src/presentacion_reflex/state/liquidaciones_state.py`
- [x] T002 [US1] Fix dictionary key case for `row_prop["ID_PROPIEDAD"]` and query results in `open_seleccion_incidentes_modal` in `src/presentacion_reflex/state/liquidaciones_state.py`
- [x] T003 [US1] Clean up `modal_seleccion_incidentes.py` to remove inline `pointer_events` / `z_index` if they conflict with `BASE_STYLE` rules in `src/presentacion_reflex/components/liquidaciones/modal_seleccion_incidentes.py`

---

## Phase 4: Polish & Cross-Cutting Concerns

*No specific polish tasks required.*
