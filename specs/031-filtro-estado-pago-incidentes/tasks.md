# Tasks: Filtro Estado Pago Incidentes

**Input**: Design documents from `/specs/031-filtro-estado-pago-incidentes/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, quickstart.md

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Analizar las referencias cruzadas de `filtros_avanzados.py` y `estado_incidentes.py` con `grep_search`.
- [x] T002 Validar el estado actual del componente de filtros avanzados en la UI.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

- [x] T003 Centralizar las opciones de Estado de Pago desde el dominio en `src/dominio/entidades/cuota_incidente.py` (o en un módulo de constantes de la presentación importando desde el dominio).

---

## Phase 3: User Story 1 - Filtrar incidentes por Estado de Pago (Priority: P1) 🎯 MVP

**Goal**: Permitir al usuario filtrar la lista de incidentes mediante las opciones "Pendiente", "Asociada", "Pagada" o "Todos", mapeando directamente con la entidad `CuotaIncidente`.

**Independent Test**: Modificar el filtro y verificar en consola de backend que el parámetro `estado_pago` se asigna correctamente en el estado y llega a la consulta. Validar en UI que los resultados concuerdan.

### Implementation for User Story 1

- [x] T004 [US1] Actualizar el estado en `src/presentacion_reflex/paginas/incidentes/estado_incidentes.py` para asegurar que `filtro_estado_pago` esté correctamente integrado en la función de filtrado y en la llamada al repositorio.
- [x] T005 [US1] Modificar el componente `ComboBox` en `src/presentacion_reflex/paginas/incidentes/componentes/filtros_avanzados.py` para usar las opciones dinámicas del dominio en lugar del valor estático `"Todos"`.
- [x] T006 [US1] Revisar y actualizar la consulta SQL en la capa de Infraestructura (`src/infraestructura/...` donde se carguen incidentes) para asegurar que se aplique el filtro `estado_pago` en la cláusula WHERE.
- [x] T007 [US1] Ejecutar los escenarios de validación de `quickstart.md` manualmente.

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase N: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [x] T008 [P] Limpiar imports huérfanos o código comentado remanente.
- [x] T009 [P] Comprobar el formateo con Black y Ruff.
- [x] T010 Asegurar que el filtro interactúe sin problemas con otros filtros sin superponerse ni causar bloqueos.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
- **Polish (Final Phase)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- T008 y T009 se pueden ejecutar en paralelo durante la fase final de pulido.

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Deploy/demo if ready
