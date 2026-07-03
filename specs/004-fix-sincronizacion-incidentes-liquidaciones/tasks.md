# Tasks: Fix Sincronización Incidentes - Liquidaciones

**Input**: Design documents from `/specs/004-fix-sincronizacion-incidentes-liquidaciones/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Tests solicitados en spec.md - unit tests para lógica de negocio + integration tests para persistencia

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Preparar entorno de desarrollo y verificar estructura existente

- [ ] T001 Verificar que todos los archivos fuente existen según plan.md (src/aplicacion/servicios/, src/infraestructura/persistencia/, src/presentacion_reflex/components/)
- [ ] T002 [P] Ejecutar pytest tests/ para verificar estado actual y documentar tests existentes
- [ ] T003 [P] Ejecutar ruff check src/ para identificar issues existentes

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Implementar funciones utilitarias que serán reutilizadas por todas las user stories

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T004 [P] Crear función `agregar_id_incidente_observaciones()` en src/aplicacion/servicios/servicio_incidente_liquidacion.py
- [x] T005 [P] Crear función `remover_id_incidente_observaciones()` en src/aplicacion/servicios/servicio_incidente_liquidacion.py
- [x] T006 [P] Crear función `truncar_observaciones()` en src/aplicacion/servicios/servicio_incidente_liquidacion.py
- [x] T007 [P] Crear tests unitarios para funciones de observaciones en tests/unit/test_servicio_incidente_liquidacion.py

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Visualización Correcta del Valor de Incidentes (Priority: P1) 🎯 MVP

**Goal**: Que el campo "Incidentes (Plan Pago)" muestre la suma correcta y NETO_A_PAGAR sea consistente

**Independent Test**: Abrir detalle de liquidación con incidentes y verificar valor mostrado = suma de cuotas en BD

### Tests for User Story 1

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T008 [P] [US1] Test unitario para `calcular_totales_con_valor_incidentes` en tests/unit/test_servicio_incidente_liquidacion.py
- [x] T009 [P] [US1] Test de integración para `sincronizacion_neto_a_pagar` en tests/integration/test_repositorio_liquidacion.py

### Implementation for User Story 1

- [x] T010 [US1] Modificar `asociar_incidente()` en src/aplicacion/servicios/servicio_incidente_liquidacion.py para obtener VALOR_INCIDENTES fresco de BD después del trigger
- [x] T011 [US1] Agregar llamada a `calcular_totales()` después de asignar valor_incidentes fresco en src/aplicacion/servicios/servicio_incidente_liquidacion.py
- [x] T012 [US1] Verificar que `obtener_por_id()` en src/infraestructura/persistencia/repositorio_liquidacion_postgres.py incluye VALOR_INCIDENTES y NETO_A_PAGAR en SELECT
- [x] T013 [US1] Ejecutar tests y verificar que pasan

**Checkpoint**: User Story 1 fully functional - NETO_A_PAGAR se calcula correctamente

---

## Phase 4: User Story 2 - Registro Automático de IDs de Incidentes en Observaciones (Priority: P1)

**Goal**: Que las observaciones se actualicen con append al asociar incidentes

**Independent Test**: Asociar múltiples incidentes y verificar observaciones contiene todos los IDs

### Tests for User Story 2

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T014 [P] [US2] Test unitario para `agregar_id_incidente_observaciones` con casos edge en tests/unit/test_servicio_incidente_liquidacion.py
- [x] T015 [P] [US2] Test de integración para `append_observaciones_al_asociar` en tests/integration/test_repositorio_liquidacion.py

### Implementation for User Story 2

- [x] T016 [US2] Modificar `asociar_incidente()` en src/aplicacion/servicios/servicio_incidente_liquidacion.py para llamar `agregar_id_incidente_observaciones()` antes de persistir
- [x] T017 [US2] Asegurar que observaciones del usuario se preservan al agregar ID de incidente
- [x] T018 [US2] Ejecutar tests y verificar que pasan

**Checkpoint**: User Story 2 fully functional - observaciones se actualizan con append

---

## Phase 5: User Story 3 - Persistencia del Estado de Pago del Incidente (Priority: P2)

**Goal**: Que ESTADO_PAGO se persista correctamente en la base de datos

**Independent Test**: Asociar incidente a liquidación pagada y verificar ESTADO_PAGO = 'Pagado' en BD

### Tests for User Story 3

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T019 [P] [US3] Test de integración para `persistencia_estado_pago` en tests/integration/test_repositorio_incidentes.py
- [x] T020 [P] [US3] Test unitario para `recalcular_estado_pago_incidente` en tests/unit/test_servicio_estado_pago.py

### Implementation for User Story 3

- [x] T021 [US3] Modificar `actualizar()` en src/infraestructura/persistencia/repositorio_incidentes_postgres.py para incluir ESTADO_PAGO en UPDATE SQL
- [x] T022 [US3] Verificar que `recalcular_estado_pago_incidente()` en src/aplicacion/servicios/servicio_estado_pago.py llama a `actualizar()` del repositorio

**Checkpoint**: User Story 3 fully functional - ESTADO_PAGO se persiste correctamente

---

## Phase 6: User Story 4 - Desasociación Segura de Incidentes (Priority: P2)

**Goal**: Que al desasociar solo se remueva el ID específico y se recalcule NETO_A_PAGAR

**Independent Test**: Desasociar un incidente de múltiples y verificar observaciones se actualiza correctamente

### Tests for User Story 4

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T024 [P] [US4] Test unitario para `remover_id_incidente_observaciones` con casos edge en tests/unit/test_servicio_incidente_liquidacion.py
- [x] T025 [P] [US4] Test de integración para `desasociar_incidente_con_observaciones` en tests/integration/test_repositorio_liquidacion.py

### Implementation for User Story 4

- [x] T026 [US4] Modificar `desasociar_incidente()` en src/aplicacion/servicios/servicio_incidente_liquidacion.py para obtener VALOR_INCIDENTES fresco de BD después del trigger
- [x] T027 [US4] Agregar llamada a `remover_id_incidente_observaciones()` antes de persistir en src/aplicacion/servicios/servicio_incidente_liquidacion.py
- [x] T028 [US4] Agregar llamada a `calcular_totales()` después de asignar valor_incidentes fresco en src/aplicacion/servicios/servicio_incidente_liquidacion.py

**Checkpoint**: User Story 4 fully functional - desasociación segura funciona correctamente

---

## Phase 7: User Story 5 - Formulario de Edición Correcto (Priority: P2)

**Goal**: Que el campo "Incidentes" se mapee correctamente a valor_incidentes

**Independent Test**: Abrir formulario de edición y verificar campo muestra valor correcto

### Tests for User Story 5

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T030 [P] [US5] Test de integración para `edicion_campo_incidentes` en tests/integration/test_repositorio_liquidacion.py

### Implementation for User Story 5

- [x] T031 [US5] Corregir mapeo de campo en src/presentacion_reflex/components/liquidacion_edit_form.py: cambiar "gastos_reparaciones" por "valor_incidentes"
- [x] T032 [US5] Actualizar `save_liquidacion()` en liquidaciones_state.py para usar campo "valor_incidentes"
- [x] T033 [US5] Actualizar `actualizar_liquidacion()` en servicio_financiero.py para usar campo "valor_incidentes"

**Checkpoint**: User Story 5 fully functional - formulario de edición correcto

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Tests adicionales, documentación y validación final

- [x] T033 [P] Crear script de diagnóstico en scripts/diagnostico/verificar_liquidaciones_inconsistentes.py
- [x] T034 [P] Ejecutar todos los tests unitarios con cobertura: pytest tests/unit/ --cov=src/aplicacion/servicios --cov-report=html
- [x] T035 [P] Ejecutar todos los tests de integración con cobertura: pytest tests/integration/ --cov=src/infraestructura/persistencia --cov-report=html
- [x] T036 Ejecutar validación completa según quickstart.md (6 escenarios)
- [x] T037 Ejecutar ruff check src/ y mypy src/ para verificar calidad de código
- [x] T038 Documentar cambios en CHANGELOG.md o ESTADO_TAREAS.md

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-7)**: All depend on Foundational phase completion
  - US1 (P1) → US2 (P1) → US4 (P2): Secuencia por dependencia de observaciones
  - US3 (P2): Independiente, puede ejecutarse en paralelo con US1/US2
  - US5 (P2): Independiente, puede ejecutarse en paralelo con otros
- **Polish (Phase 8)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P1)**: Can start after Foundational (Phase 2) - Uses utility functions from Phase 2
- **User Story 3 (P2)**: Can start after Foundational (Phase 2) - Independent
- **User Story 4 (P2)**: Depends on US2 (uses remover_id_incidente_observaciones)
- **User Story 5 (P2)**: Can start after Foundational (Phase 2) - Independent

### Within Each User Story

- Tests MUST be written and FAIL before implementation
- Utility functions before services
- Services before UI
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- T002, T003: Can run in parallel (different verification tasks)
- T004, T005, T006, T007: Can run in parallel (different utility functions)
- T008, T009: Can run in parallel (different test types)
- T014, T015: Can run in parallel (different test types)
- T019, T020: Can run in parallel (different test types)
- T024, T025: Can run in parallel (different test types)
- T033, T034, T035: Can run in parallel (different validation tasks)
- US1, US3, US5: Can run in parallel after Foundational (no dependencies between them)

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together:
Task: "Test unitario para calcular_totales_con_valor_incidentes en tests/unit/test_servicio_incidente_liquidacion.py"
Task: "Test de integración para sincronizacion_neto_a_pagar en tests/integration/test_repositorio_liquidacion.py"

# Launch implementation tasks sequentially (dependencies):
Task: "Modificar asociar_incidente() para obtener VALOR_INCIDENTES fresco"
Task: "Agregar llamada a calcular_totales()"
Task: "Verificar obtener_por_id() incluye campos necesarios"
Task: "Ejecutar tests y verificar que pasan"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo
4. Add User Story 3 → Test independently → Deploy/Demo
5. Add User Story 4 → Test independently → Deploy/Demo
6. Add User Story 5 → Test independently → Deploy/Demo
7. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (NETO_A_PAGAR)
   - Developer B: User Story 3 (ESTADO_PAGO)
   - Developer C: User Story 5 (Formulario)
3. After US1/US3/US5 complete:
   - Developer A: User Story 2 (Observaciones append)
   - Developer B: User Story 4 (Desasociación segura)
4. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence

## Total Task Count

- **Phase 1 (Setup)**: 3 tasks
- **Phase 2 (Foundational)**: 4 tasks
- **Phase 3 (US1)**: 6 tasks
- **Phase 4 (US2)**: 5 tasks
- **Phase 5 (US3)**: 5 tasks
- **Phase 6 (US4)**: 6 tasks
- **Phase 7 (US5)**: 3 tasks
- **Phase 8 (Polish)**: 6 tasks

**Total**: 38 tasks
**Parallel opportunities**: 15 tasks marked [P]
