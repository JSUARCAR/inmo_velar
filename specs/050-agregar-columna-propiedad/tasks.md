# Tasks: Agregar Columna PROPIEDAD a Tabla de Recaudos

**Input**: Design documents from `/specs/050-agregar-columna-propiedad/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: No se solicitaron tests explícitamente en la especificación.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Verificar estado actual y preparar entorno

- [X] T001 Verificar que la columna PROPIEDAD existe en src/presentacion_reflex/pages/recaudos.py línea 259
- [X] T002 Verificar que el campo `direccion` se muestra en el body de la tabla (líneas 292-299)
- [X] T003 [P] Ejecutar `reflex run --env dev` para confirmar que la UI carga sin errores

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Validar que la infraestructura de sorting y filtering funciona correctamente

- [X] T004 Verificar que `header_cell_sortable()` funciona para la columna `direccion` en recaudos.py
- [X] T005 Verificar que `RecaudosState.toggle_sort("direccion")` ordena correctamente
- [X] T006 Verificar que el query SQL incluye JOIN con tabla propiedades en repositorio_recaudo.py

**Checkpoint**: Infraestructura validada - la columna ya existe y funciona

---

## Phase 3: User Story 1 - Visualizar columna PROPIEDAD (Priority: P1) 🎯 MVP

**Goal**: Ver la columna PROPIEDAD en la tabla de recaudos mostrando la dirección de cada propiedad

**Independent Test**: Navegar a /recaudos y verificar que la columna PROPIEDAD está visible con datos correctos

### Implementation for User Story 1

- [X] T007 [US1] Verificar que el header "Propiedad" está en la posición correcta (después de Ciclo Operativo) en recaudos.py:259
- [X] T008 [US1] Verificar que cada fila muestra `rec["direccion"]` correctamente en recaudos.py:292-299
- [X] T009 [US1] Implementar fallback "Sin dirección" cuando `direccion` es NULL en recaudos.py
- [X] T010 [US1] Verificar que la columna es visible por defecto (no oculta por CSS) en recaudos.py
- [X] T011 [US1] Ejecutar `reflex run --env dev` y validar visualmente en navegador

**Checkpoint**: Columna PROPIEDAD visible y funcional en la tabla

---

## Phase 4: User Story 2 - Ordenar por columna PROPIEDAD (Priority: P2)

**Goal**: Poder ordenar la tabla por la columna PROPIEDAD (ascendente/descendente)

**Independent Test**: Hacer clic en el encabezado PROPIEDAD y verificar que la tabla se ordena alfabéticamente

### Implementation for User Story 2

- [X] T012 [US2] Verificar que el encabezado PROPIEDAD tiene `sortable=True` en recaudos.py:259
- [X] T013 [US2] Verificar que `header_cell_sortable()` muestra icono de sort correcto para `direccion`
- [X] T014 [US2] Verificar que `RecaudosState.toggle_sort("direccion")` cambia `sort_by` a "direccion"
- [X] T015 [US2] Verificar que el query SQL aplica `ORDER BY p.direccion` en repositorio_recaudo.py
- [X] T016 [US2] Probar ordenamiento ascendente (A-Z) y descendente (Z-A) en navegador

**Checkpoint**: Ordenamiento por PROPIEDAD funciona correctamente

---

## Phase 5: User Story 3 - Filtrar por PROPIEDAD (Priority: P3)

**Goal**: Poder filtrar la tabla por una o más propiedades específicas

**Independent Test**: Seleccionar una propiedad en el filtro y verificar que solo se muestran sus recaudos

### Implementation for User Story 3

- [X] T017 [US3] Agregar variable `filter_propiedad: List[str] = []` en recaudos_state.py
- [X] T018 [US3] Agregar variable `propiedad_options: List[Dict] = []` en recaudos_state.py
- [X] T019 [US3] Implementar método `load_propiedad_options()` en recaudos_state.py para cargar opciones desde BD
- [X] T020 [US3] Implementar método `set_filter_propiedad(value: str)` en recaudos_state.py
- [X] T021 [US3] Implementar método `toggle_filter_propiedad(value: str)` en recaudos_state.py
- [X] T022 [US3] Actualizar `load_recaudos()` para incluir filtro de propiedad en recaudos_state.py
- [X] T023 [US3] Agregar filtro de propiedad al toolbar en recaudos.py usando `multi_select_popover`
- [X] T024 [US3] Actualizar `FiltrosRecaudo` dataclass para incluir `propiedad_ids` en repositorio_recaudo.py
- [X] T025 [US3] Actualizar query SQL para filtrar por propiedad_id en repositorio_recaudo.py
- [X] T026 [US3] Actualizar `clear_filters()` para incluir limpieza de filtro de propiedad en recaudos_state.py
- [X] T027 [US3] Actualizar `active_filter_count()` para contar filtros de propiedad en recaudos_state.py
- [X] T028 [US3] Probar filtro de propiedad en navegador

**Checkpoint**: Filtrado por PROPIEDAD funciona correctamente

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Mejoras transversales y validación final

- [X] T029 [P] Verificar que la columna es responsiva en diferentes viewports (desktop, tablet, mobile)
- [X] T030 [P] Verificar que el estado de orden y filtros se mantiene al recargar la página
- [X] T031 Verificar performance: tiempo de carga de tabla no aumenta más de 50ms
- [X] T032 Ejecutar `ruff check src/presentacion_reflex/pages/recaudos.py` para verificar linting
- [X] T033 Ejecutar `ruff check src/presentacion_reflex/state/recaudos_state.py` para verificar linting
- [X] T034 Ejecutar validación completa de quickstart.md

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User Story 1 (P1): Can start after Foundational - No dependencies on other stories
  - User Story 2 (P2): Can start after Foundational - May integrate with US1 but independently testable
  - User Story 3 (P3): Can start after Foundational - May integrate with US1/US2 but independently testable
- **Polish (Final Phase)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - May integrate with US1 but independently testable
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - May integrate with US1/US2 but independently testable

### Within Each User Story

- Models before services
- Services before endpoints
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- Tasks T029 and T030 can run in parallel

---

## Parallel Example: User Story 1

```bash
# Launch all verification tasks for User Story 1 together:
Task: "Verificar header Propiedad en posición correcta en recaudos.py:259"
Task: "Verificar que cada fila muestra rec['direccion'] en recaudos.py:292-299"
Task: "Implementar fallback 'Sin dirección' cuando direccion es NULL"
Task: "Verificar que la columna es visible por defecto"
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
   - Developer A: User Story 1 (Visualizar columna)
   - Developer B: User Story 2 (Ordenar columna)
   - Developer C: User Story 3 (Filtrar columna)
3. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing (if tests included)
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence

**Total Tasks**: 34
**User Story 1 (P1)**: 5 tasks (MVP)
**User Story 2 (P2)**: 5 tasks
**User Story 3 (P3)**: 12 tasks
**Setup**: 3 tasks
**Foundational**: 3 tasks
**Polish**: 6 tasks


## Phase 7: Convergence

- [X] T035 Actualizar filtro de propiedad para soportar propiedades sin dirección en UI y SQL per FR-005, FR-006 (partial)
