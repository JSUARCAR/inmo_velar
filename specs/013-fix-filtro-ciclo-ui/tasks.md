# Tasks: fix-filtro-ciclo-ui

**Input**: Design documents from `specs/013-fix-filtro-ciclo-ui/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/` at repository root

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure.

- [x] T001 Checkout a la nueva rama de feature `feature/013-fix-filtro-ciclo-ui` (o nombre equivalente) en la raíz del repositorio.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented.

*(No se requieren tareas fundacionales, la base de datos y la vista ya existen)*

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Filtro por Ciclo Operativo Exitoso (Priority: P1) 🎯 MVP

**Goal**: Garantizar que el filtrado por ciclo operativo no produzca error de SQL.

**Independent Test**: Filtrar la tabla desde la UI y observar los registros actualizados sin errores en base de datos (según `quickstart.md`).

### Implementation for User Story 1

- [x] T002 [US1] Modificar la cláusula SQL de filtrado en `src/infraestructura/persistencia/repositorio_liquidacion_postgres.py` cambiando el alias `prop.GRUPO_OPERATIVO` a `p.GRUPO_OPERATIVO` (o el alias local de la tabla Propiedad).

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently.

---

## Phase 4: User Story 2 - Interfaz de Filtros Avanzados Responsiva (Priority: P2)

**Goal**: Evitar la superposición de elementos del filtro avanzado en pantallas móviles y mantener una disposición ordenada usando flexbox.

**Independent Test**: Modificar el tamaño de ventana del navegador y validar que cada filtro ocupa el 100% de la fila en dispositivos móviles y no se superponen elementos.

### Implementation for User Story 2

- [x] T003 [US2] Actualizar las propiedades `width` (ej: `["100%", "100%", "auto"]`) y configuraciones de envoltorio en el componente `liquidaciones_toolbar()` de `src/presentacion_reflex/pages/liquidaciones.py` para asegurar responsividad total por cada input, select y contenedor de botones.

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently.

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [x] T004 [P] Ejecutar validación de `quickstart.md` localmente (`check_syntax.py`, `reflex export` o similar).
- [x] T005 [P] Revisar posibles imports muertos originados por reestructuraciones y asegurar que todo siga el Claude Design System.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: N/A
- **User Stories (Phase 3+)**: Depend on Setup completion.
  - US1 y US2 pueden realizarse en paralelo al modificar archivos diferentes.
- **Polish (Final Phase)**: Depends on all desired user stories being complete.

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Setup - No dependencies on other stories.
- **User Story 2 (P2)**: Can start after Setup - No dependencies on other stories.

### Parallel Opportunities

- US1 y US2 al modificar la infraestructura de datos vs presentación UI pueden ejecutarse en paralelo sin conflictos.

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 3: User Story 1
3. **STOP and VALIDATE**: Test User Story 1 independently

### Incremental Delivery

1. Add User Story 1 → Test independently
2. Add User Story 2 → Test independently
3. Execute Polish phase

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
