# Tasks: Corrección de Selección de Incidentes en Liquidaciones

**Input**: Design documents from `/specs/001-fix-liquidaciones-incidentes/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: No se solicitaron tests explícitamente en la especificación. Tests opcionales se marcan con [OPT].

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root
- **Web app**: `backend/src/`, `frontend/src/`
- Paths shown below assume single project - adjust based on plan.md structure

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 Verificar que el proyecto existe y tiene la estructura correcta según plan.md
- [ ] T002 Confirmar que PostgreSQL está configurado y accesible
- [ ] T003 [P] Confirmar que las dependencias de Python están instaladas (Reflex, Pydantic, psycopg2)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T004 Analizar el método `open_seleccion_incidentes_modal` en `src/presentacion_reflex/state/liquidaciones_state.py` para entender la consulta actual
- [ ] T005 Identificar cómo obtener `ID_PROPIEDAD` desde `ID_CONTRATO_M` en la base de datos
- [ ] T006 Verificar la estructura de la tabla `INCIDENTES` y su relación con `PROPIEDADES`
- [ ] T007 Verificar que el método `open_edit_modal` carga correctamente los campos existentes

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Filtrado Correcto de Incidentes por Propiedad (Priority: P1) 🎯 MVP

**Goal**: El modal "Seleccionar Incidentes" muestra únicamente los incidentes de la propiedad de la liquidación

**Independent Test**: Acceder a una liquidación existente, abrir modal de selección de incidentes, verificar que solo aparecen incidentes de la propiedad correcta

### Implementation for User Story 1

- [x] T008 [US1] Modificar `open_seleccion_incidentes_modal` para obtener `ID_CONTRATO_M` desde la liquidación en `src/presentacion_reflex/state/liquidaciones_state.py`
- [x] T009 [US1] Agregar consulta para obtener `ID_PROPIEDAD` desde `CONTRATOS_MANDATOS` usando `ID_CONTRATO_M` en `src/presentacion_reflex/state/liquidaciones_state.py`
- [x] T010 [US1] Modificar la consulta SQL para filtrar incidentes por `ID_PROPIEDAD` en `src/presentacion_reflex/state/liquidaciones_state.py`
- [x] T011 [US1] Agregar validación para manejar el caso donde `ID_PROPIEDAD` no se pueda obtener en `src/presentacion_reflex/state/liquidaciones_state.py`
- [x] T012 [US1] Verificar que el modal muestra el estado vacío correctamente cuando no hay incidentes para la propiedad en `src/presentacion_reflex/components/liquidaciones/modal_seleccion_incidentes.py`

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Carga de Datos al Editar Liquidación (Priority: P1)

**Goal**: Los campos "Incidentes" y "Observaciones" cargan automáticamente la información previamente almacenada

**Independent Test**: Acceder a una liquidación con incidentes y observaciones previos, verificar que los campos muestran los valores guardados

### Implementation for User Story 2

- [x] T013 [US2] Verificar que el campo `valor_incidentes` se carga correctamente en `open_edit_modal` en `src/presentacion_reflex/state/liquidaciones_state.py`
- [x] T014 [US2] Verificar que el campo `observaciones` se carga correctamente en `open_edit_modal` en `src/presentacion_reflex/state/liquidaciones_state.py`
- [x] T015 [US2] Verificar que el formulario de edición muestra los campos cargados en `src/presentacion_reflex/components/liquidaciones/liquidacion_edit_form.py`
- [x] T016 [US2] Agregar indicador visual del número de incidentes asociados en el formulario de edición en `src/presentacion_reflex/components/liquidaciones/liquidacion_edit_form.py`

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Consistencia entre Capas del Sistema (Priority: P2)

**Goal**: Existe consistencia completa entre la información almacenada en la base de datos, la lógica del backend y la interfaz de usuario

**Independent Test**: Insertar datos directamente en la base de datos y verificar que se reflejan en la interfaz, y viceversa

### Implementation for User Story 3

- [x] T017 [US3] Verificar que la consulta de filtrado retorna los datos correctos comparando con la base de datos directamente
- [x] T018 [US3] Verificar que la selección múltiple de incidentes se persiste correctamente en la tabla `INCIDENTE_LIQUIDACION`
- [x] T019 [US3] Verificar que el campo `VALOR_INCIDENTES` en la tabla `LIQUIDACIONES` se actualiza correctamente al asociar/desasociar incidentes
- [x] T020 [US3] Verificar que los datos se sincronizan entre la UI y la base de datos después de guardar

**Checkpoint**: All user stories should now be independently functional

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [x] T021 [P] Ejecutar validación de quickstart.md para verificar todos los escenarios
- [x] T022 [P] Verificar que no hay errores en la consola del navegador
- [x] T023 Verificar que el tiempo de carga del modal es < 3 segundos
- [x] T024 Verificar que los mensajes de error son claros y útiles
- [x] T025 Documentar los cambios realizados en ESTADO_TAREAS.md

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User Story 1 (P1): Can start after Foundational
  - User Story 2 (P1): Can start after Foundational (independent from US1)
  - User Story 3 (P2): Can start after Foundational (independent from US1/US2)
- **Polish (Final Phase)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P1)**: Can start after Foundational (Phase 2) - May integrate with US1 but should be independently testable
- **User Story 3 (P2)**: Can start after Foundational (Phase 2) - May integrate with US1/US2 but should be independently testable

### Within Each User Story

- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Once Foundational phase completes, User Stories 1 and 2 can start in parallel
- Polish tasks marked [P] can run in parallel

---

## Parallel Example: User Story 1

```bash
# Launch all implementation tasks for User Story 1:
Task: "T008 Modificar open_seleccion_incidentes_modal para obtener ID_CONTRATO_M"
Task: "T009 Agregar consulta para obtener ID_PROPIEDAD"
Task: "T010 Modificar consulta SQL para filtrar por ID_PROPIEDAD"
Task: "T011 Agregar validación para manejar ID_PROPIEDAD no disponible"
Task: "T012 Verificar estado vacío del modal"
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
5. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (Filtrado de incidentes)
   - Developer B: User Story 2 (Carga de datos al editar)
3. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence

## File Reference

| File | Purpose | Tasks |
|------|---------|-------|
| `src/presentacion_reflex/state/liquidaciones_state.py` | Estado principal con consultas SQL | T008-T014, T017-T020 |
| `src/presentacion_reflex/components/liquidaciones/modal_seleccion_incidentes.py` | Modal de selección de incidentes | T012 |
| `src/presentacion_reflex/components/liquidaciones/liquidacion_edit_form.py` | Formulario de edición | T015-T016 |