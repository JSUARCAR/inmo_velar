# Tasks: Liquidación Propietarios Octubre 2026 Invisible

**Input**: Design documents from `/specs/079-fix-liquidacion-oct2026/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Incluidas porque el spec las exige (§5 Pruebas funcionales, SC-005).

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- Repo único: `src/`, `tests/` en la raíz; docs en `specs/079-fix-liquidacion-oct2026/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Verificar entorno y línea base antes de tocar nada

- [X] T001 Verificar runner pytest y imports clave con `python -m pytest tests/aplicacion/test_servicio_financiero_elegibilidad.py -q` y `python -c` de `src.aplicacion.servicios.servicio_financiero` en la raíz del repo
- [X] T002 [P] Tomar snapshot de línea base PG (solo lectura) con conteos por período en `LIQUIDACIONES` vía `src/infraestructura/persistencia/database.py` (testigo `2026-09` = 60, `2026-10` = 0)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Puerta de regresión que BLOQUEA todo lo demás

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T003 Ejecutar suite de regresión existente `tests/aplicacion/test_servicio_financiero_elegibilidad.py` + `tests/dominio/test_liquidacion_asesor.py` y exigir 8 passed
- [X] T004 Reproducir la causa raíz en PG (lectura + llamada controlada): `generar_liquidacion_propietario` debe lanzar `KeyError: 'tiene_arriendo'` pre-fix / pasar post-fix, documentado en `specs/079-fix-liquidacion-oct2026/research.md`

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Masiva octubre 2026 visible en tabla (Priority: P1) 🎯 MVP

**Goal**: La masiva persiste y se muestra sin recarga manual, con filtro sincronizado

**Independent Test**: Masiva en período TEST `2099-12` con 3 propietarios conocidos ⇒ `generadas>0`, tabla recargada, `filter_periodo` en el período generado; re-ejecución ⇒ omitidas

### Tests for User Story 1 ⚠️

- [X] T005 [P] [US1] Verificar en PG TEST que `listar_liquidaciones_paginado` y `listar_liquidaciones_propietarios_paginado` devuelven total 1/1 grupo tras generar en `2099-12` vía `src/aplicacion/servicios/servicio_financiero.py`
- [X] T006 [P] [US1] Verificar idempotencia: segunda ejecución en mismo período TEST cuenta omitidas sin duplicar `UNIQUE(ID_CONTRATO_M, PERIODO)` en `src/aplicacion/servicios/servicio_financiero.py`

### Implementation for User Story 1

- [X] T007 [US1] Aplicar acceso dual a claves dict (`TIENE_ARRIENDO`/`tiene_arriendo`, `ID_CONTRATO_M`, `DIRECCION_PROPIEDAD`) en `src/aplicacion/servicios/servicio_financiero.py` (depende de T004)
- [X] T008 [US1] Aplicar recarga incondicional con `filter_periodo = periodo` y `current_page = 1` en `generar_liquidacion_masiva` en `src/presentacion_reflex/state/liquidaciones_state.py`
- [X] T009 [US1] Validar toast resumen `generadas/omitidas/no elegibles/errores` con motivos en `src/presentacion_reflex/state/liquidaciones_state.py`

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Individual visible inmediatamente (Priority: P1, comparador)

**Goal**: El flujo individual sigue intacto y sirve de comparador contra lógica duplicada

**Independent Test**: Individual en período TEST persiste en `En Proceso` y aparece en ambas vistas al filtrar

- [X] T010 [P] [US2] Verificar que `save_liquidacion → generar_liquidacion_mensual` en `src/presentacion_reflex/state/liquidaciones_state.py` recarga la tabla y no cambió de contrato
- [X] T011 [US2] Comparar conteos individual vs masiva para el mismo período TEST y registrar divergencias en `specs/079-fix-liquidacion-oct2026/research.md`

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Filtros y paginación por período (Priority: P2)

**Goal**: Totales UI coinciden con BD y la paginación es exacta

**Independent Test**: Filtro `2026-09` ⇒ total 60 con páginas 25+25+10; generar en otro período mueve el filtro automáticamente

- [X] T012 [P] [US3] Verificar total y paginación de `2026-09` contra `COUNT(*)` en PG vía `src/infraestructura/persistencia/repositorio_liquidacion_postgres.py`
- [X] T013 [US3] Verificar cambio automático de filtro tras masiva en `src/presentacion_reflex/state/liquidaciones_state.py`

**Checkpoint**: All user stories should now be independently functional

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Cerrar gaps de diseño y dejar el árbol limpio

- [X] T014 [P] Añadir nota LIKE-vs-= en `specs/079-fix-liquidacion-oct2026/contracts/` (cierra CHK009 de diseno.md)
- [X] T015 [P] Añadir a `specs/079-fix-liquidacion-oct2026/quickstart.md` el escenario cero-elegibles y diferimiento explícito de bordes de paginación (cierra CHK015/017/018/019 de diseno.md)
- [X] T016 [P] Fijar versiones y universo TEST en `specs/079-fix-liquidacion-oct2026/plan.md` Technical Context (cierra CHK022/023 de diseno.md)
- [X] T017 Ejecutar `specs/079-fix-liquidacion-oct2026/quickstart.md` completo y exigir limpieza `COUNT LIKE '2099%' = 0` en PG
- [X] T018 Verificar `git status`/`git diff --stat`: solo `src/aplicacion/servicios/servicio_financiero.py`, `src/presentacion_reflex/state/liquidaciones_state.py` y `specs/079-fix-liquidacion-oct2026/` como cambios propios

---

## Phase 7: Convergence

**Purpose**: Cerrar los hallazgos del análisis cruzado sin tarea asignada (código ya converge; resto documental)

- [X] T019 Corregir etiqueta de Phase 4 a Priority P1 en `specs/079-fix-liquidacion-oct2026/tasks.md` per spec Story 2 (partial)
- [X] T020 Reformular SC-003 sin término de implementación en `specs/079-fix-liquidacion-oct2026/spec.md` per análisis B1 (partial)
- [X] T021 Añadir concurrencia idempotente y caso cero-elegibles a `specs/079-fix-liquidacion-oct2026/contracts/evento-masiva.md` per análisis C1 (partial)
- [X] T022 Agregar test automatizado del sync de filtro o justificar manual en `specs/079-fix-liquidacion-oct2026/quickstart.md` per análisis C2 (partial)
- [X] T023 Especificar total 0 en paginación y regla futuro-vs-pasado en `specs/079-fix-liquidacion-oct2026/spec.md` per análisis C3 (partial)
- [X] T024 Fijar término canónico masiva (= por propietario, todos) en `specs/079-fix-liquidacion-oct2026/spec.md` per análisis F2 (partial)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (US1 → US2 → US3)
- **Polish (Final Phase)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P1)**: Can start after Foundational (Phase 2) - Comparador independiente de US1
- **User Story 3 (P2)**: Can start after Foundational (Phase 2) - Independiente de US1/US2

### Within Each User Story

- Tests (included per spec §5) MUST be verified before/alongside implementation
- Service fix (T007) before state fix validation (T008, T009)
- Story complete before moving to next priority

### Parallel Opportunities

- T002 puede correr en paralelo con T001 (lectura vs runner, archivos distintos)
- T005 y T006 en paralelo (mismo servicio, períodos/contratos TEST distintos — coordinar IDs)
- T010, T011, T012 en paralelo (archivos y períodos distintos)
- T014, T015, T016 en paralelo (tres archivos de `specs/079-fix-liquidacion-oct2026/` distintos)

---

## Parallel Example: User Story 1

```bash
# Verificaciones de User Story 1 en paralelo (períodos TEST distintos):
Task: "Verificar consultas individual/agrupada en 2099-12 en src/aplicacion/servicios/servicio_financiero.py" (T005)
Task: "Verificar idempotencia en 2099-11 en src/aplicacion/servicios/servicio_financiero.py" (T006)
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Masiva TEST visible sin recarga manual
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo
4. Add User Story 3 → Test independently → Deploy/Demo
5. Each story adds value without breaking previous stories

### Nota de estado real

T007–T009 ya están aplicadas en el árbol de trabajo y verificadas (TEST `2099-*` con borrado físico, `COUNT = 0`); las tareas sirven como guía ejecutable de re-verificación y para cerrar los gaps de diseño pendientes (T014–T016).

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
