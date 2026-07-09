# Tasks: Disponibilidad de Acciones por Estado - Liquidacion Asesores

**Input**: Design documents from `/specs/038-liquidacion-asesores-actions/`

**Prerequisites**: plan.md, spec.md, data-model.md, contracts/service-contracts.md, research.md

**Tests**: No tests requested in feature specification.

**Organization**: Tasks grouped by user story for independent implementation.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3, US4)
- Exact file paths included in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Migración de base de datos y configuración compartida

- [ ] T001 Crear migración SQL para columna ELIMINADA en LIQUIDACIONES_ASESORES en src/infraestructura/db/migrations/migration_add_eliminada_liquidacion_asesor.sql
- [ ] T002 Ejecutar migración y verificar creación de índice idx_liquidaciones_asesor_eliminada
- [ ] T003 [P] Agregar propiedad `eliminada: bool = False` a entidad LiquidacionAsesor en src/dominio/entidades/liquidacion_asesor.py

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Métodos de servicio y repositorio que TODOS los stories necesitan

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T004 Implementar método `eliminar` en repositorio con soft delete en src/infraestructura/repositorios/repositorio_liquidacion_asesor.py
- [ ] T005 Implementar método `reversar` en repositorio con transiciones de estado en src/infraestructura/repositorios/repositorio_liquidacion_asesor.py
- [ ] T006 Actualizar query `listar_paginado` para filtrar ELIMINADA = FALSE en src/infraestructura/repositorios/repositorio_liquidacion_asesor.py
- [ ] T007 [P] Actualizar query `obtener_metricas_por_filtros` para excluir eliminadas en src/infraestructura/repositorios/repositorio_liquidacion_asesor.py
- [ ] T008 Implementar método `eliminar_liquidacion` en servicio con validación de estado en src/aplicacion/servicios/servicio_liquidacion_asesores.py
- [ ] T009 Implementar método `reversar_liquidacion` en servicio con lógica por estado en src/aplicacion/servicios/servicio_liquidacion_asesores.py
- [ ] T010 Implementar método `obtener_acciones_disponibles` en servicio en src/aplicacion/servicios/servicio_liquidacion_asesores.py

**Checkpoint**: Foundation ready - backend listo para soportar todas las acciones

---

## Phase 3: User Story 1 - Visualización de Acciones según Estado (Priority: P1) 🎯 MVP

**Goal**: La UI muestra Eliminar solo para Pendiente, Reversar para todos los demás estados

**Independent Test**: Navegar a liquidaciones asesores, verificar que Pendiente muestra "Eliminar" y otros estados muestran "Reversar"

### Implementation for User Story 1

- [ ] T011 [US1] Agregar estados de modal para eliminar/reversar en src/presentacion_reflex/state/liquidacion_asesores/form_state.py (show_delete_confirm_modal, show_reverse_modal, liquidacion_id_for_action, reverse_motivo, reverse_motivo_requerido)
- [ ] T012 [US1] Implementar handler `open_delete_confirm_modal` en src/presentacion_reflex/state/liquidacion_asesores/form_state.py
- [ ] T013 [US1] Implementar handler `open_reverse_modal` en src/presentacion_reflex/state/liquidacion_asesores/form_state.py
- [ ] T014 [US1] Implementar handler `close_delete_modal` en src/presentacion_reflex/state/liquidacion_asesores/form_state.py
- [ ] T015 [US1] Implementar handler `close_reverse_modal` en src/presentacion_reflex/state/liquidacion_asesores/form_state.py
- [ ] T016 [US1] Actualizar columna de acciones en tabla para mostrar Eliminar/Reversar condicionalmente en src/presentacion_reflex/pages/liquidacion_asesores.py
- [ ] T017 [US1] Agregar botón Eliminar visible solo para estado Pendiente en src/presentacion_reflex/pages/liquidacion_asesores.py
- [ ] T018 [US1] Agregar botón Reversar visible solo para estados diferentes de Pendiente en src/presentacion_reflex/pages/liquidacion_asesores.py

**Checkpoint**: UI muestra acciones correctas según estado - MVP funcional

---

## Phase 4: User Story 2 - Ejecución Segura de Eliminar (Priority: P1)

**Goal**: Eliminar liquidación Pendiente con confirmación, soft delete y validación de integridad

**Independent Test**: Click Eliminar en Pendiente → modal → confirmar → soft delete → registro desaparece

### Implementation for User Story 2

- [ ] T019 [US2] Implementar handler `eliminar_liquidacion` con llamada a servicio en src/presentacion_reflex/state/liquidacion_asesores/form_state.py
- [ ] T020 [US2] Crear modal de confirmación para Eliminar en src/presentacion_reflex/pages/liquidacion_asesores.py
- [ ] T021 [US2] Integrar modal con handler eliminar_liquidacion en src/presentacion_reflex/pages/liquidacion_asesores.py
- [ ] T022 [US2] Agregar toast de éxito/error para eliminación en src/presentacion_reflex/state/liquidacion_asesores/form_state.py
- [ ] T023 [US2] Recargar grid después de eliminación exitosa en src/presentacion_reflex/state/liquidacion_asesores/form_state.py
- [ ] T024 [US2] Manejar error de integridad referencial (descuentos/pagos existentes) en src/presentacion_reflex/state/liquidacion_asesores/form_state.py

**Checkpoint**: Eliminar funciona end-to-end con validación

---

## Phase 5: User Story 3 - Ejecución Segura de Reversar (Priority: P1)

**Goal**: Reversar liquidación con transiciones correctas y motivo obligatorio para Pagada/Anulada

**Independent Test**: Click Reversar en Aprobada → sin motivo → confirmar → Pendiente. Click en Pagada → con motivo → confirmar → Aprobada

### Implementation for User Story 3

- [ ] T025 [US3] Implementar handler `reversar_liquidacion` con llamada a servicio en src/presentacion_reflex/state/liquidacion_asesores/form_state.py
- [ ] T026 [US3] Crear modal de reversión con campo motivo condicional en src/presentacion_reflex/pages/liquidacion_asesores.py
- [ ] T027 [US3] Implementar validación de motivo mínimo 10 caracteres en UI (botón deshabilitado) en src/presentacion_reflex/pages/liquidacion_asesores.py
- [ ] T028 [US3] Integrar modal con handler reversar_liquidacion en src/presentacion_reflex/pages/liquidacion_asesores.py
- [ ] T029 [US3] Agregar toast de éxito/error para reversión en src/presentacion_reflex/state/liquidacion_asesores/form_state.py
- [ ] T030 [US3] Recargar grid después de reversión exitosa en src/presentacion_reflex/state/liquidacion_asesores/form_state.py

**Checkpoint**: Reversar funciona para todos los estados con validación de motivo

---

## Phase 6: User Story 4 - Validación Backend Reforzada (Priority: P2)

**Goal**: APIs rechazan acciones que no cumplen reglas de estado, incluso con invocación manual

**Independent Test**: Llamada directa a API para eliminar Aprobada → Error 400. Llamada para reversar Pendiente → Error 400

### Implementation for User Story 4

- [ ] T031 [US4] Verificar que método eliminar en servicio valida estado == "Pendiente" en src/aplicacion/servicios/servicio_liquidacion_asesores.py
- [ ] T032 [US4] Verificar que método reversar en servicio valida estado != "Pendiente" en src/aplicacion/servicios/servicio_liquidacion_asesores.py
- [ ] T033 [US4] Verificar que método reversar valida motivo >= 10 chars para Pagada/Anulada en src/aplicacion/servicios/servicio_liquidacion_asesores.py
- [ ] T034 [US4] Verificar que método eliminar valida integridad referencial (descuentos/pagos) en src/aplicacion/servicios/servicio_liquidacion_asesores.py
- [ ] T035 [US4] Verificar que queries de listado excluyen eliminadas en src/infraestructura/repositorios/repositorio_liquidacion_asesor.py

**Checkpoint**: Backend blindado contra acciones inválidas

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Mejoras transversales y verificación final

- [ ] T036 Verificar que todas las queries existentes agregan filtro ELIMINADA = FALSE en src/infraestructura/repositorios/repositorio_liquidacion_asesor.py
- [ ] T037 Ejecutar quickstart.md scenarios de validación
- [ ] T038 Verificar que no existen regressions en flujos existentes (aprobar, anular, pagar)
- [ ] T039 [P] Documentar decisiones técnicas en ESTADO_TAREAS.md

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Phase 1 completion - BLOCKS all user stories
- **User Stories (Phase 3-6)**: All depend on Phase 2 completion
  - US1, US2, US3 are P1 and can proceed in parallel after Phase 2
  - US4 is P2 and can proceed after Phase 2
- **Polish (Phase 7)**: Depends on all user stories being complete

### User Story Dependencies

- **US1 (Visualización)**: Can start after Phase 2 - No dependencies on other stories
- **US2 (Eliminar)**: Can start after Phase 2 - Depends on US1 for modal state structure
- **US3 (Reversar)**: Can start after Phase 2 - Depends on US1 for modal state structure
- **US4 (Validación Backend)**: Can start after Phase 2 - Verifies Phase 2 implementation

### Within Each User Story

- State handlers before UI components
- UI components before integration
- Integration before validation

### Parallel Opportunities

- T001, T002, T003 can run in parallel (Setup)
- T006, T007 can run in parallel (Query updates)
- US1, US2, US3 can run in parallel after Phase 2 (different aspects)
- T031-T035 can run in parallel (Backend verification)

---

## Parallel Example: User Story 1

```bash
# Launch state handlers together:
Task: "T011 Agregar estados de modal en form_state.py"
Task: "T012 Implementar open_delete_confirm_modal en form_state.py"
Task: "T013 Implementar open_reverse_modal en form_state.py"
Task: "T014 Implementar close_delete_modal en form_state.py"
Task: "T015 Implementar close_reverse_modal en form_state.py"

# Launch UI components together:
Task: "T016 Actualizar columna de acciones en liquidacion_asesores.py"
Task: "T017 Agregar botón Eliminar en liquidacion_asesores.py"
Task: "T018 Agregar botón Reversar en liquidacion_asesores.py"
```

---

## Implementation Strategy

### MVP First (US1 + US2 + US3)

1. Complete Phase 1: Setup (migración)
2. Complete Phase 2: Foundational (servicio + repositorio)
3. Complete Phase 3: US1 (UI actions visibility)
4. Complete Phase 4: US2 (Eliminar end-to-end)
5. Complete Phase 5: US3 (Reversar end-to-end)
6. **STOP and VALIDATE**: Test all P1 stories independently
7. Deploy/demo if ready

### Incremental Delivery

1. Setup + Foundational → Backend ready
2. US1 → UI muestra acciones correctas → Demo
3. US2 → Eliminar funciona → Demo
4. US3 → Reversar funciona → Demo
5. US4 → Backend blindado → Production ready

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
