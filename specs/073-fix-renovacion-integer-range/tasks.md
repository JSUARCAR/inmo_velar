# Tasks: Fix `integer out of range` en renovación de contratos

**Input**: Design documents from `/specs/073-fix-renovacion-integer-range/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Incluidos — el spec los exige explícitamente (SC-004, escenarios de validación) y la constitución exige >90% de cobertura en lógica nueva.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Línea base verde y entorno de pruebas listo

- [X] T001 Ejecutar baseline de suites de renovación en tests/unit/test_renovacion_*.py y tests/integration/test_renovacion_*.py (deben estar en verde antes del cambio)
- [X] T002 [P] Confirmar entorno de BD de prueba aislado vía DATABASE_URL (nunca producción) para tests/integration/conftest.py

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Excepción de dominio y validador de rango compartidos por todas las historias

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T003 Agregar excepción de dominio por valor fuera de rango (con campo + valor) en src/dominio/excepciones/excepciones_base.py
- [X] T004 [P] Crear validador previo en dos niveles en src/aplicacion/utils/validadores.py (1.º máximos operativos canon/comisión con rechazo operativo; 2.º límite int4 como red de seguridad; falla rápido antes de persistir)

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Renovar el contrato de CS 54, La Alquería (Priority: P1) 🎯 MVP

**Goal**: La renovación del contrato N.º 73 completa sin errores, con IPC aplicado y propagación correcta

**Independent Test**: Renovar solo el contrato N.º 73 (staging/BD prueba con sus magnitudes) y comprobar historial, vigencia, canon, liquidaciones y recaudos futuros

### Tests for User Story 1 ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T005 [P] [US1] Test de integración de propagación límite (canon 2.300.000 × comisión 1000 → 230.000 exacto) en tests/integration/test_renovacion_propagacion_limite.py
- [X] T006 [P] [US1] Test unitario de validación previa y mensaje con campo + valor en tests/unit/test_renovacion_rango.py

### Implementation for User Story 1

- [X] T007 [US1] Ensanchar a 64 bits el cómputo intermedio de comisión e IVA en src/aplicacion/servicios/servicio_contrato_arrendamiento.py (mantener CAST final y truncamiento)
- [X] T008 [US1] Integrar la validación previa del validador en la renovación y propagación en src/aplicacion/servicios/servicio_contrato_arrendamiento.py
- [X] T009 [US1] Mapear la excepción de dominio a mensaje operativo no técnico en src/presentacion_reflex/state/contratos_state.py
- [X] T010 [US1] Ejecutar validación del caso índice (Escenario 3 de quickstart.md) y confirmar cero inconsistencias con verificar_propagacion_canon — ✅ Ejecutado por el operador sin errores (2026-09-14).

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Renovar cualquier contrato sin importar la magnitud (Priority: P2)

**Goal**: Ninguna combinación dentro de los rangos reales (canon ≤ $10.000.000, comisión ≤ 1500) falla por desbordamiento, incluidas consecutivas

**Independent Test**: Renovar contratos de prueba en combinaciones límite y dos renovaciones consecutivas encadenadas

### Tests for User Story 2 ⚠️

- [X] T011 [P] [US2] Test límite extremo (10.000.000 × 1500) y consecutivas encadenadas en tests/integration/test_renovacion_propagacion_limite.py
- [X] T012 [P] [US2] Test de rechazo operativo ante valores sobre-máximos (campo + valor, sin tecnicismos) en tests/unit/test_renovacion_rango.py

### Implementation for User Story 2

- [X] T013 [US2] Aplicar el mismo estándar de validación a la renovación de mandato en src/aplicacion/servicios/servicio_contratos.py (sin cambios SQL propios)
- [X] T014 [US2] Verificar encadenamiento de consecutivas (anterior(n) = nuevo(n-1)) contra tests/integration/test_renovacion_consecutiva.py

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Módulos dependientes consistentes y sin regresiones (Priority: P3)

**Goal**: Propagación consistente en Liquidaciones, Recaudos, Mandato y Propiedades; suites existentes 100% verdes

**Independent Test**: Reporte de propagación con cero inconsistencias + suites de Contratos, Liquidaciones y Recaudos en verde

- [X] T015 [P] [US3] Test de consistencia mandato + canon estimado post-renovación extendiendo tests/integration/test_canon_propiedad_renovacion.py
- [X] T016 [US3] Ejecutar suites completas de Contratos, Liquidaciones y Recaudos en tests/unit/, tests/integration/ y tests/aplicacion/ y confirmar 100% verdes
- [X] T017 [US3] Correr los Escenarios 1–4 de quickstart.md en specs/073-fix-renovacion-integer-range/quickstart.md y adjuntar evidencia

**Checkpoint**: All user stories should now be independently functional

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Calidad, documentación y validación final

- [X] T018 [P] Pasar ruff, black y mypy sobre src/aplicacion/servicios/servicio_contrato_arrendamiento.py, src/aplicacion/servicios/servicio_contratos.py, src/aplicacion/utils/validadores.py y src/dominio/excepciones/excepciones_base.py
- [X] T019 [P] Actualizar documentación dinámica (ESTADO_TAREAS.md y auditoria_GEMINI_CLI.md) con el hito del fix
- [X] T020 Revisar el checklist specs/073-fix-renovacion-integer-range/checklists/renovacion.md contra la implementación y marcar hallazgos
- [X] T021 Validación final end-to-end con specs/073-fix-renovacion-integer-range/quickstart.md antes de merge

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
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Reuses T007/T008 fix; independently testable via T011/T012
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - Verifies US1/US2 outputs; independently testable via T015–T017

### Within Each User Story

- Tests MUST be written and FAIL before implementation
- Foundational helper/exception before story implementation
- Core fix before presentation mapping
- Story complete before moving to next priority

### Parallel Opportunities

- T002 can run in parallel with T001 (entorno vs baseline)
- T004 can run in parallel with T003 (archivos distintos)
- T005 + T006 can run in parallel (archivos de test distintos)
- T011 + T012 can run in parallel (archivos de test distintos)
- T015 can run in parallel with suite execution preparation
- T018 + T019 can run in parallel (lint vs docs)

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together:
Task: "Test de integración de propagación límite en tests/integration/test_renovacion_propagacion_limite.py"
Task: "Test unitario de validación previa en tests/unit/test_renovacion_rango.py"

# Implementation follows sequentially (mismo archivo de servicio):
Task: "Ensanchar cómputo en src/aplicacion/servicios/servicio_contrato_arrendamiento.py"
Task: "Mapear mensaje en src/presentacion_reflex/state/contratos_state.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test User Story 1 independently (caso índice renovable)
5. Deploy/demo if ready (desbloquea al cliente)

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP: forma)
3. Add User Story 2 → Test independently → Deploy/Demo (fondo estructural)
4. Add User Story 3 → Test independently → Deploy/Demo (consistencia total)

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1
   - Developer B: User Story 2 (tests límite, validación mandato)
   - Developer C: User Story 3 (consistencia, suites)
3. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- T007 + T008 tocan el mismo archivo: secuenciales, no paralelas
- T010/T017 exigen BD de prueba o staging, nunca producción
- Commit después de cada tarea o grupo lógico (Conventional Commits, alcance claro)
- Stop at any checkpoint to validate story independently
