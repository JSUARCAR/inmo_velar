# Tasks: Auditoría de Propagación de Renovaciones

**Input**: Design documents from `/specs/062-audit-renewal-propagation/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Tests are OPTIONAL - only included if explicitly requested in the feature specification.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `scripts/diagnostico/`, `tests/verification/` at repository root

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Create project structure: `scripts/diagnostico/` directory
- [x] T002 Create main script file: `scripts/diagnostico/audit_renovaciones_2026.py`
- [x] T003 [P] Add module docstring and version constant

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T004 Implement database connection module with `DATABASE_URL` support
- [x] T005 [P] Implement SQL query execution wrapper (read-only enforcement)
- [x] T006 [P] Implement error handling classes (ErrorConexionBD, ErrorConsultaSQL, ErrorAccesoArchivo)
- [x] T007 [P] Create data model classes (dataclasses for all entities)

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Identificar Inconsistencias de Canon (Priority: P1) 🎯 MVP

**Goal**: Identify all contracts with canon discrepancies between current values and liquidations/recaudos

**Independent Test**: Execute script and verify it identifies all known inconsistencies

### Implementation for User Story 1

- [x] T008 [P] [US1] Implement query to fetch July 2026 renovations (last per contract)
- [x] T009 [P] [US1] Implement query to fetch future liquidaciones for a contract
- [x] T010 [P] [US1] Implement query to fetch future recaudos for a contract
- [x] T011 [P] [US1] Implement query to fetch recaudo conceptos (Canon)
- [x] T012 [US1] Implement liquidacion comparison logic (FR-004)
- [x] T013 [US1] Implement recaudo comparison logic (FR-005)
- [x] T014 [US1] Implement root cause determination for each inconsistency
- [x] T015 [US1] Implement main audit orchestration function

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Generar Informe Estructurado (Priority: P1)

**Goal**: Generate JSON report with metrics, inconsistencies, code analysis, and recommendations

**Independent Test**: Execute script and verify JSON contains all required sections

### Implementation for User Story 2

- [x] T016 [P] [US2] Implement metadata generation (FR-010)
- [x] T017 [P] [US2] Implement executive summary generation (FR-011)
- [x] T018 [P] [US2] Implement inconsistencies detail formatting (FR-012)
- [x] T019 [P] [US2] Implement recommendations generation (FR-014)
- [x] T020 [US2] Implement JSON file output with timestamp naming
- [x] T021 [US2] Integrate all report sections into complete JSON structure

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Analizar Fallas de Diseño (Priority: P2)

**Goal**: Identify specific design flaws in synchronization logic via static code analysis

**Independent Test**: Review code analysis section and verify it identifies real flaws

### Implementation for User Story 3

- [x] T022 [P] [US3] Implement Python AST parser for source file analysis
- [x] T023 [P] [US3] Implement analysis of `servicio_contrato_arrendamiento.py` (cascade sync)
- [x] T024 [P] [US3] Implement analysis of `servicio_financiero.py` (liquidacion generation)
- [x] T025 [P] [US3] Implement analysis of `servicio_recaudo.py` (recaudo generation)
- [x] T026 [US3] Implement code flaw categorization and impact assessment
- [x] T027 [US3] Integrate code analysis into JSON report (FR-013)

**Checkpoint**: User Story 3 complete - code analysis included in report

---

## Phase 6: User Story 4 - Preservación de Históricos (Priority: P2)

**Goal**: Verify historical liquidations/recaudos before July 2026 are unmodified

**Independent Test**: Verify historical records maintain original values

### Implementation for User Story 4

- [x] T028 [P] [US4] Implement query to fetch historical liquidaciones (before July 2026)
- [x] T029 [P] [US4] Implement query to fetch historical recaudos (before July 2026)
- [x] T030 [US4] Implement historical preservation verification logic
- [x] T031 [US4] Integrate historical verification into JSON report

**Checkpoint**: All user stories should now be independently functional

---

## Phase 7: Mandato/Propiedad Sync Verification (Cross-Cutting)

**Goal**: Verify canon synchronization between contracts, mandatos, and properties

**Independent Test**: Execute script and verify sync status is documented

### Implementation

- [x] T032 [P] Implement query to fetch mandato for a contract
- [x] T033 [P] Implement query to fetch propiedad for a mandato
- [x] T034 Implement mandato/propiedad canon comparison logic (FR-006)
- [x] T035 Integrate sync verification into JSON report

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [x] T036 [P] Add command-line argument parsing (optional: output path, verbosity)
- [x] T037 [P] Add progress logging during execution
- [x] T038 Implement comprehensive error handling for all failure scenarios
- [x] T039 Add edge case handling (empty results, missing mandato, cancelled records)
- [x] T040 Run quickstart.md validation scenarios
- [x] T041 Create verification test file: `tests/verification/test_audit_renovaciones.py`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-6)**: All depend on Foundational phase completion
  - User stories can proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2)
- **Cross-Cutting (Phase 7)**: Depends on Foundational phase completion
- **Polish (Phase 8)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P1)**: Can start after Foundational (Phase 2) - May integrate with US1 but should be independently testable
- **User Story 3 (P2)**: Can start after Foundational (Phase 2) - Independent of US1/US2
- **User Story 4 (P2)**: Can start after Foundational (Phase 2) - Independent of US1/US2/US3

### Within Each User Story

- Models before services
- Services before endpoints
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Once Foundational phase completes, all user stories can start in parallel
- All query implementation tasks marked [P] can run in parallel
- Code analysis tasks (T022-T025) can run in parallel

---

## Parallel Example: User Story 1

```bash
# Launch all query implementations together:
Task: "Implement query to fetch July 2026 renovations in scripts/diagnostico/audit_renovaciones_2026.py"
Task: "Implement query to fetch future liquidaciones in scripts/diagnostico/audit_renovaciones_2026.py"
Task: "Implement query to fetch future recaudos in scripts/diagnostico/audit_renovaciones_2026.py"
Task: "Implement query to fetch recaudo conceptos in scripts/diagnostico/audit_renovaciones_2026.py"

# Then implement comparison logic:
Task: "Implement liquidacion comparison logic in scripts/diagnostico/audit_renovaciones_2026.py"
Task: "Implement recaudo comparison logic in scripts/diagnostico/audit_renovaciones_2026.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 + User Story 2)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (Identify Inconsistencies)
4. Complete Phase 4: User Story 2 (Generate Report)
5. **STOP and VALIDATE**: Test script generates valid JSON with inconsistencies
6. Deploy/use if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 + 2 → Test independently → **MVP DELIVERED**
3. Add User Story 3 (Code Analysis) → Test independently → Enhanced report
4. Add User Story 4 (Historical Check) → Test independently → Complete audit
5. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 + 2 (Queries + Report)
   - Developer B: User Story 3 (Code Analysis)
   - Developer C: User Story 4 (Historical Check)
3. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Single file implementation: All code goes in `scripts/diagnostico/audit_renovaciones_2026.py`
- Total tasks: 41
- Estimated effort: 4-6 hours
