---
description: "Task list template for feature implementation"
---

# Tasks: playwright-prod-diag

**Input**: Design documents from `specs/008-playwright-prod-diag/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, quickstart.md

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `tests/` at repository root
- Path structure defined in `plan.md`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] T001 Crear el directorio aislado para las pruebas de diagnóstico `tests/diagnostics/` si no existe
- [X] T002 Crear archivo base `tests/diagnostics/__init__.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T003 Implementar fixtures de Playwright (`page`) e inyección de credenciales desde entorno (`PLAYWRIGHT_PROD_USER`/`PLAYWRIGHT_PROD_PASS`) en `tests/diagnostics/conftest.py`
- [X] T004 Implementar la interceptación global de red y logs JS (`page.on('response')`, `page.on('console')`) dentro de `tests/diagnostics/conftest.py` para reportes de diagnóstico

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Validación del Plan de Pago en Incidentes (Priority: P1) 🎯 MVP

**Goal**: El sistema debe permitir validar en producción que el flujo de Plan de Pagos en el módulo de Incidentes muestre las cuotas correctas, con el valor asociado a la cotización y un estado consistente con la base de datos, para la propiedad "CONJ CIUDADELA COMFENALCO MZ H CS 29".

**Independent Test**: Ejecutar específicamente la prueba y ver si el plan de pago carga en la interfaz (headed mode).

### Implementation for User Story 1

- [X] T005 [US1] Crear el archivo base de pruebas E2E `tests/diagnostics/test_prod_diag.py`
- [X] T006 [US1] Implementar el método de prueba `test_validacion_plan_pago` dentro de `tests/diagnostics/test_prod_diag.py` enfocado en el DOM de Incidentes.

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Validación del botón Seleccionar Incidentes (Priority: P1)

**Goal**: El sistema debe permitir diagnosticar el comportamiento del botón "Seleccionar Incidentes" dentro del modal de edición de liquidaciones para la propiedad "Calle Falsa 123 - Test Renov".

**Independent Test**: Ejecutar y verificar si el modal renderiza el botón interactivo.

### Implementation for User Story 2

- [X] T007 [US2] Implementar el método de prueba `test_seleccion_incidentes` en `tests/diagnostics/test_prod_diag.py` para el flujo de liquidaciones.

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Validación de la acción Eliminar (Priority: P1)

**Goal**: Verificar y diagnosticar la funcionalidad de eliminación en el módulo de Liquidaciones para el entorno Sandbox.

**Independent Test**: Ejecutar la prueba y verificar si la solicitud HTTP DELETE es disparada al hacer clic.

### Implementation for User Story 3

- [X] T008 [US3] Implementar el método de prueba `test_eliminar_liquidacion_sandbox` en `tests/diagnostics/test_prod_diag.py`.

**Checkpoint**: All user stories should now be independently functional

---

## Phase 6: User Story 4 - Diagnóstico Comparativo Local vs Producción (Priority: P1)

**Goal**: Realizar un análisis exhaustivo del entorno para documentar las causas de las asimetrías de funcionalidad.

**Independent Test**: Revisión de los logs emitidos.

### Implementation for User Story 4

- [X] T009 [US4] Crear y preparar el documento de reporte `specs/008-playwright-prod-diag/diagnostico.md` para consolidar hallazgos.

---

## Phase N: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [X] T010 Run quickstart.md validation (`pytest tests/diagnostics/test_prod_diag.py --headed --slowmo=500 -v -s`)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Polish (Final Phase)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - No dependencies
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - No dependencies
- **User Story 4 (P4)**: Debe ejecutarse después de que las US1, US2 y US3 hayan arrojado resultados (fallos o éxitos de red).

### Within Each User Story

- Pruebas antes de la refactorización
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- US2 y US3 pueden programarse de manera simultánea en el mismo script ya que son funciones independientes de Pytest.

---

## Parallel Example: User Story 2 & 3

```bash
# Pueden desarrollarse ambas pruebas al mismo tiempo:
Task: "Implementar el método de prueba test_seleccion_incidentes en tests/diagnostics/test_prod_diag.py"
Task: "Implementar el método de prueba test_eliminar_liquidacion_sandbox en tests/diagnostics/test_prod_diag.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Ejecutar `test_validacion_plan_pago` y diagnosticar.

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently
3. Add User Story 2 → Test independently
4. Add User Story 3 → Test independently
5. Consolidar US4 documentando todos los hallazgos de red capturados.
