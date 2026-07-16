# Tasks: Reporte de Liquidaciones - Datos del Propietario y Contrato de Mandato

**Input**: Design documents from `/specs/054-reporte-liquidaciones-datos-propietario/`

**Prerequisites**: plan.md, spec.md, data-model.md, contracts/report-liquidaciones.md, research.md

**Tests**: No tests requested in feature specification.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T001 Verify current SQL query structure in src/infraestructura/persistencia/repositorio_reportes.py (obtener_reporte_liquidaciones method, lines 259-281)
- [X] T002 Verify entity field mappings: PERSONAS.NUMERO_DOCUMENTO, PERSONAS.TELEFONO_PRINCIPAL, CONTRATOS_MANDATOS.BANCO_PROPIETARIO, CONTRATOS_MANDATOS.NUMERO_CUENTA_PROPIETARIO, CONTRATOS_MANDATOS.TIPO_CUENTA, CONTRATOS_MANDATOS.CONSIGNATARIO, CONTRATOS_MANDATOS.DOCUMENTO_CONSIGNATARIO

**Checkpoint**: Foundation verified - user story implementation can now begin

---

## Phase 2: User Story 1 + 2 - Visualización de información del propietario y contrato (Priority: P1) 🎯 MVP

**Goal**: Agregar las 7 nuevas columnas al Reporte de Liquidaciones: 2 de datos del propietario (NUMERO_DOCUMENTO_PROPIETARIO, TELEFONO_PROPIETARIO) y 5 de información bancaria del Contrato de Mandato (BANCO, NUMERO_CUENTA, TIPO_CUENTA, NOMBRE_CONSIGNATARIO, DOCUMENTO_CONSIGNATARIO)

**Independent Test**: Generar el Reporte de Liquidaciones y verificar que las 7 columnas aparecen correctamente después de NOMBRE_PROPIETARIO con datos consistentes de PostgreSQL

### Implementation for User Story 1 + 2

- [X] T003 [US1][US2] Add 7 new columns to SQL SELECT in src/infraestructura/persistencia/repositorio_reportes.py (obtener_reporte_liquidaciones method):
  - After `per_prop.NOMBRE_COMPLETO AS "Nombre_Propietario"` add:
    - `per_prop.NUMERO_DOCUMENTO AS "NUMERO_DOCUMENTO_PROPIETARIO"`
    - `per_prop.TELEFONO_PRINCIPAL AS "TELEFONO_PROPIETARIO"`
    - `cm.BANCO_PROPIETARIO AS "BANCO"`
    - `cm.NUMERO_CUENTA_PROPIETARIO AS "NUMERO_CUENTA"`
    - `cm.TIPO_CUENTA AS "TIPO_CUENTA"`
    - `cm.CONSIGNATARIO AS "NOMBRE_CONSIGNATARIO"`
    - `cm.DOCUMENTO_CONSIGNATARIO AS "DOCUMENTO_CONSIGNATARIO"`

- [X] T004 [US1][US2] Verify SQL query returns 35 columns (was 28) and column order matches specification: NOMBRE_PROPIETARIO → NUMERO_DOCUMENTO_PROPIETARIO → TELEFONO_PROPIETARIO → BANCO → NUMERO_CUENTA → TIPO_CUENTA → NOMBRE_CONSIGNATARIO → DOCUMENTO_CONSIGNATARIO

- [X] T005 [US1][US2] Verify servicio_reportes.py passes through new columns correctly (no changes expected - headers derived from data[0].keys())

**Checkpoint**: At this point, User Stories 1 AND 2 should be fully functional - report displays all 7 new columns

---

## Phase 3: User Story 3 - Exportación del reporte ampliado (Priority: P2)

**Goal**: Asegurar que la exportación CSV preserva las nuevas columnas con formato correcto (números de cuenta sin truncamiento)

**Independent Test**: Exportar el reporte a CSV y verificar que todas las 7 nuevas columnas aparecen con valores sin truncamiento

### Implementation for User Story 3

- [X] T006 [US3] Add new banking/document columns to Excel sanitization list in src/presentacion_reflex/state/reportes_state.py (_sanitize_value method):
  - Add to the column list that gets Excel text literal formatting: "NUMERO_CUENTA", "NUMERO_DOCUMENTO_PROPIETARIO", "DOCUMENTO_CONSIGNATARIO"

- [X] T007 [US3] Verify CSV export includes all 35 columns with correct headers

- [X] T008 [US3] Verify banking numbers (NUMERO_CUENTA) preserve leading zeros in CSV export

**Checkpoint**: At this point, User Stories 1, 2, AND 3 should all work - report displays new columns and CSV export preserves them correctly

---

## Phase 4: User Story 4 - Consistencia de datos (Priority: P2)

**Goal**: Verificar que la información mostrada en el reporte es idéntica a la almacenada en PostgreSQL

**Independent Test**: Comparar manualmente los valores de 5 registros arbitrarios entre el reporte exportado y las consultas directas a la base de datos

### Implementation for User Story 4

- [X] T009 [US4] Verify data consistency by comparing report values with direct PostgreSQL queries for NUMERO_DOCUMENTO_PROPIETARIO and TELEFONO_PROPIETARIO

- [X] T010 [US4] Verify data consistency by comparing report values with direct PostgreSQL queries for BANCO, NUMERO_CUENTA, TIPO_CUENTA, NOMBRE_CONSIGNATARIO, DOCUMENTO_CONSIGNATARIO

- [X] T011 [US4] Verify no regressions in other reports (Reporte Financiero Consolidado, Reporte de Asesores)

**Checkpoint**: All user stories should now be independently functional and verified

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Final validation and cleanup

- [X] T012 Run syntax validation: python -m py_compile on modified files
- [X] T013 Run linting: ruff check on modified files
- [X] T014 Verify performance: Report generation time within 10% of baseline
- [X] T015 Run quickstart.md validation scenarios

---

## Dependencies & Execution Order

### Phase Dependencies

- **Foundational (Phase 1)**: No dependencies - can start immediately
- **User Story 1 + 2 (Phase 2)**: Depends on Foundational completion - BLOCKS all subsequent work
- **User Story 3 (Phase 3)**: Depends on Phase 2 completion (needs new columns in report)
- **User Story 4 (Phase 4)**: Depends on Phase 2 completion (needs new columns to verify)
- **Polish (Phase 5)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 + 2 (P1)**: Can start after Foundational (Phase 1) - No dependencies on other stories
- **User Story 3 (P2)**: Depends on US1+US2 (needs columns to exist for CSV export)
- **User Story 4 (P2)**: Depends on US1+US2 (needs columns to exist for verification)

### Within Each User Story

- Implementation before verification
- Core SQL changes before sanitization changes
- Story complete before moving to next priority

### Parallel Opportunities

- Phase 1 tasks can run in parallel
- US3 and US4 can run in parallel after Phase 2 completes

---

## Parallel Example: User Story 1 + 2

```bash
# Single task handles both US1 and US2 since they modify the same SQL query:
Task: "Add 7 new columns to SQL SELECT in repositorio_reportes.py"

# Verification tasks can run in parallel:
Task: "Verify SQL query returns 35 columns"
Task: "Verify servicio_reportes.py passes through new columns"
```

---

## Implementation Strategy

### MVP First (User Story 1 + 2 Only)

1. Complete Phase 1: Foundational verification
2. Complete Phase 2: User Story 1 + 2 (add columns to SQL)
3. **STOP and VALIDATE**: Test report displays 7 new columns correctly
4. Deploy/demo if ready

### Incremental Delivery

1. Complete Foundational → Foundation ready
2. Add User Story 1 + 2 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 3 → Test CSV export → Deploy/Demo
4. Add User Story 4 → Verify data consistency → Deploy/Demo
5. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 + 2 (SQL changes)
   - Developer B: Can prepare User Story 3 (sanitization) in parallel
3. After Phase 2 completes:
   - Developer A: User Story 4 (verification)
   - Developer B: User Story 3 (CSV export)

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- US1 and US2 are combined because they modify the same SQL query in the same file
- No test tasks included (not requested in feature specification)
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
