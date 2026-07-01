# Tasks: Eliminar Liquidación de Propietario

**Feature**: 002-eliminar-liquidacion | **Date**: 2026-06-30

## Phase 1: Setup

- [X] T001 Create database migration for ELIMINADA column in src/infraestructura/db/migrations/migration_add_eliminada_column.sql
- [X] T002 Run database migration against PostgreSQL database

## Phase 2: Foundational

- [X] T003 [P] Add `eliminada: bool = False` field to Liquidacion entity in src/dominio/entidades/liquidacion.py
- [X] T004 [P] Add `eliminar()` method to IRepositorioLiquidacion Protocol in src/dominio/interfaces/repositorio_liquidacion.py

## Phase 3: US1 - Eliminar Liquidación Individual

- [X] T005 [US1] Implement `eliminar()` method in RepositorioLiquidacionPostgres in src/infraestructura/persistencia/repositorio_liquidacion_postgres.py
- [X] T006 [US1] Add `eliminar_liquidacion()` method to ServicioFinanciero in src/aplicacion/servicios/servicio_financiero.py
- [X] T007 [US1] Add delete event handlers and state vars to LiquidacionesState in src/presentacion_reflex/state/liquidaciones_state.py
- [X] T008 [US1] Add "Eliminar" button to liquidacion_detail_modal.py in src/presentacion_reflex/components/liquidaciones/liquidacion_detail_modal.py

## Phase 4: US2 - Confirmación con Impacto

- [X] T009 [US2] Create delete_confirm_dialog.py component in src/presentacion_reflex/components/liquidaciones/delete_confirm_dialog.py
- [X] T010 [US2] Export delete_confirm_dialog in __init__.py in src/presentacion_reflex/components/liquidaciones/__init__.py
- [X] T011 [US2] Import and integrate delete dialog in liquidaciones.py in src/presentacion_reflex/pages/liquidaciones.py
- [X] T012 [US2] Add delete button in liquidation table row in src/presentacion_reflex/pages/liquidaciones.py

## Phase 5: US3 - Auditoría Completa

- [X] T013 [US3] Implement audit logging in eliminar_liquidacion() service method in src/aplicacion/servicios/servicio_financiero.py

## Phase 6: US4 - Permisos y Seguridad

- [X] T014 [US4] Create permission registration script in scripts/add_eliminar_permission.py
- [X] T015 [US4] Add permission check to delete button visibility in src/presentacion_reflex/pages/liquidaciones.py

## Phase 7: US5 - Eliminación en Vista Agrupada

- [X] T016 [US5] Add delete button to grouped view detail in src/presentacion_reflex/pages/liquidaciones.py

## Phase 8: Query Filtering & Polish

- [X] T017 Update listar_todas() query to filter ELIMINADA=FALSE in repositorio_liquidacion_postgres.py
- [X] T018 Update listar_por_contrato() query to filter ELIMINADA=FALSE in repositorio_liquidacion_postgres.py
- [X] T019 Update obtener_por_contrato_y_periodo() query to filter ELIMINADA=FALSE in repositorio_liquidacion_postgres.py
- [X] T020 Update listar_por_propietario_y_periodo() query to filter ELIMINADA=FALSE in repositorio_liquidacion_postgres.py
- [X] T021 Update listar_agrupadas_por_propietario_paginado() query to filter ELIMINADA=FALSE in repositorio_liquidacion_postgres.py
- [X] T022 Update contar_con_filtros() query to filter ELIMINADA=FALSE in repositorio_liquidacion_postgres.py
- [X] T023 Update obtener_datos_para_pdf() query to filter ELIMINADA=FALSE in repositorio_liquidacion_postgres.py
- [X] T024 Update obtener_consolidado_propietario() query to filter ELIMINADA=FALSE in repositorio_liquidacion_postgres.py
- [X] T025 Update cancelar_por_propietario_y_periodo() query to filter ELIMINADA=FALSE in repositorio_liquidacion_postgres.py
- [X] T026 Update reversar_por_propietario_y_periodo() query to filter ELIMINADA=FALSE in repositorio_liquidacion_postgres.py
- [X] T027 Update aprobar_por_propietario_y_periodo() query to filter ELIMINADA=FALSE in repositorio_liquidacion_postgres.py
- [X] T028 Update obtener_estado_pago_actual() query to filter ELIMINADA=FALSE in repositorio_liquidacion_postgres.py
- [X] T029 Add document orphaning logic in eliminar_liquidacion() service in src/aplicacion/servicios/servicio_financiero.py
- [ ] T030 Verify and test all queries exclude deleted records
- [X] T031 Run linting and type checks

## Dependencies

```
Phase 1 (Setup) ──► Phase 2 (Foundational) ──► Phase 3 (US1) ──► Phase 4 (US2)
                                                         │
                                                         ├──► Phase 5 (US3)
                                                         │
                                                         └──► Phase 6 (US4)
                                                                  │
                                                                  └──► Phase 7 (US5)
                                                                           │
                                                                           └──► Phase 8 (Polish)
```

## Parallel Opportunities

| Phase | Parallel Tasks |
|-------|----------------|
| Phase 2 | T003, T004 (different files) |
| Phase 3 | None (sequential) |
| Phase 4 | T009, T010 (create then export) |
| Phase 5 | None (sequential) |
| Phase 6 | T014, T015 (script then UI) |
| Phase 7 | None (depends on Phase 4) |
| Phase 8 | T017-T028 (all query updates) |

## Independent Test Criteria

| User Story | Test Criteria |
|------------|---------------|
| US1 | Create liquidation in "En Proceso" state, execute deletion, verify record disappears from table |
| US2 | Open delete dialog, verify summary and financial breakdown displayed, checkbox blocks confirmation |
| US3 | Execute deletion, query AUDITORIA_CAMBIOS table, verify complete audit record |
| US4 | Login without ELIMINAR permission, verify delete button not visible |
| US5 | Open grouped view, delete individual liquidation, verify other liquidations remain |

## MVP Scope

**Recommended MVP**: User Stories 1, 2, 3, 4 (Phase 1-6)
- Core deletion functionality
- Confirmation dialog with safety
- Audit trail
- Permission control

**Full scope**: Add US5 (Phase 7) for grouped view support

## Implementation Strategy

1. **Backend first**: Domain → Repository → Service → State
2. **Frontend second**: Dialog → Table buttons → Detail modal
3. **Query filtering last**: Update all existing queries
4. **Testing throughout**: Manual smoke tests after each phase
