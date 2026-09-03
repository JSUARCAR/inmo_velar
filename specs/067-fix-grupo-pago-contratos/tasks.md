# Tasks: Fix Grupo de Pago Contratos

**Input**: Design documents from `specs/067-fix-grupo-pago-contratos/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, quickstart.md

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Create migration script file structure in `scripts/migraciones/migrar_grupos_mandatos_v2.py`
- [x] T002 Import required core dependencies (`db_manager`, `CalculadoraContratos`, `logger`, `argparse`, `sys`) in `scripts/migraciones/migrar_grupos_mandatos_v2.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T003 Setup CLI argument parsing (`--commit` flag) and logging configuration in `scripts/migraciones/migrar_grupos_mandatos_v2.py`
- [x] T004 Implement database connection handling with `db_manager` (dry-run vs transaction modes) in `scripts/migraciones/migrar_grupos_mandatos_v2.py`

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Recalibración Masiva (Migración) (Priority: P1) 🎯 MVP

**Goal**: Crear el núcleo del script de migración que lee contratos, compara grupos/fechas y actualiza si es necesario en una transacción.

**Independent Test**: Ejecutar `python scripts/migraciones/migrar_grupos_mandatos_v2.py` y verificar el reporte de discrepancias sin que modifique la BD. Ejecutar con `--commit` y validar los cambios en la BD.

### Implementation for User Story 1

- [x] T005 [US1] Implement function `procesar_mandatos(cursor, mode_commit)` in `scripts/migraciones/migrar_grupos_mandatos_v2.py` to `SELECT` active contracts from `CONTRATOS_MANDATOS`
- [x] T006 [US1] Inside `procesar_mandatos`, iterate over contracts, calculate new values using `CalculadoraContratos.calcular_ciclo_pago_mandato` and identify discrepancies in `scripts/migraciones/migrar_grupos_mandatos_v2.py`
- [x] T007 [US1] Inside `procesar_mandatos`, implement the `UPDATE` logic using `executemany` when `mode_commit` is True in `scripts/migraciones/migrar_grupos_mandatos_v2.py`
- [x] T008 [US1] Wire the main execution block to call `procesar_mandatos` using the transactional context in `scripts/migraciones/migrar_grupos_mandatos_v2.py`

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently. The script should identify and repair the 8 broken contracts.

---

## Phase 4: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [x] T009 Run quickstart.md validation locally to verify the ID 56 contract has been fixed.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
- **Polish (Final Phase)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories

### Within Each User Story

- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- Due to the nature of this single-file script task, parallel execution is minimal. Only T001 and T002 can be started concurrently, but they are trivial.

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test User Story 1 independently against staging/local DB.
5. Deploy/Execute on production DB.
