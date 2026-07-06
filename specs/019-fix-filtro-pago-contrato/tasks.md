# Tasks

## Phase 1: Setup

- [X] T001 Analyze the current flow of the `Pago Contrato` filter in `src/presentacion_reflex/pages/recaudos.py` and `recaudos_state.py`.
- [X] T002 Identify where `id_contrato` is being used instead of `dia_pago` in the UI and state.

## Phase 2: Foundational

- [X] T003 Update `FiltrosRecaudo` DTO in `src/dominio/interfaces/repositorio_recaudo.py` to replace `id_contrato` with `dia_pago`.
- [X] T004 Implement fallback logic in SQL (`COALESCE(NULLIF(ca.FECHA_PAGO, ''), EXTRACT(DAY FROM ca.FECHA_INICIO_CONTRATO_A::DATE)::TEXT) = %s`) in `src/infraestructura/persistencia/repositorio_recaudo.py` `contar_con_filtros`.
- [X] T005 Implement same fallback logic in `src/infraestructura/persistencia/repositorio_recaudo.py` `listar_paginado`.
- [X] T006 Update `src/aplicacion/servicios/servicio_recaudo.py` to pass `dia_pago` instead of `id_contrato`.

## Phase 3: User Story 1 - Filtrar Recaudos por Día de Pago del Contrato

- [X] T007 [US1] Rename `filter_contrato` to `filter_dia_pago` in `src/presentacion_reflex/state/recaudos_state.py`.
- [X] T008 [US1] Change filter options to `["Todos", "1", "2", ... "31"]` instead of a dynamic list of contracts in `recaudos_state.py`.
- [X] T009 [US1] Update `src/presentacion_reflex/pages/recaudos.py` UI to bind to `filter_dia_pago` instead of `filter_contrato`.

## Phase 4: Polish & Cross-Cutting Concerns

- [X] T010 Run `pytest` to ensure no regressions.
