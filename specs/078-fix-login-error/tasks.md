# Tasks: Corrección del error de producción tras el inicio de sesión (TypeError en protección de rutas)

**Input**: Design documents from `/specs/078-fix-login-error/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/proteccion_rutas.md, quickstart.md

**Tests**: El plan exige TDD explícitamente (FR-008; constitución §13 Corregir Raíz → Blindar). Se incluyen tareas de test.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

**Branch**: `bugfix/078-fix-login-error` | **Spec**: [spec.md](spec.md) | **Plan**: [plan.md](plan.md)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Verificar el entorno existente; esta feature NO introduce dependencias ni infraestructura nuevas (cirugía técnica, plan §Technical Context).

No hay proyecto, paquete ni capa nueva que inicializar (plan §Project Structure). Setup mínimo: confirmar prerequisitos y el contrato vigente antes de escribir el test RED.

- [x] T001 Verificar prerequisitos de validación: `python -c "from src.presentacion_reflex.state.auth_state import AuthState"` y `pytest --version` desde la raíz del repo (plan §Technical Context; quickstart §Prerequisitos)
- [x] T002 [P] Confirmar firma del mixin en `src/presentacion_reflex/state/navigation_mixin.py:22` (`end_navigation_generation(self) -> None`, sin argumentos) como fuente de verdad del contrato (research §Hallazgo 1; contract §2)
- [x] T003 [P] Confirmar estado del harness E2E (deuda T042 de la 077): `node --version`, `npm ls playwright @playwright/test` en la raíz, y que `tests/e2e/*.spec.mjs` requieren `playwright` instalado (plan §Notas; quickstart §Comandos; FR-008)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Reescribir en TDD el blindaje del contrato del mixin (tareas de regresión que DEBEN existir antes de codificar el fix) y alinear los tests existentes que codifican la firma errónea (FR-008/FR-010). Esta fase bloquea toda implementación de los User Stories.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Tests (TDD — escribir PRIMERO y ver que FALLEN con el bug presente)

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation** (constitution §13, plan §Notas)

- [x] T004 [P] Crear test de regresión dedicado del contrato del mixin con **método real** (sin mockear `end_navigation_generation`) en `tests/unit/test_regresion_firma_proteccion.py` (nuevo, FR-008): ejecutar `AuthState.require_login_background.fn(state, gen_id)` con `_validate_session` y `validate_generation` controlados, cubriendo los **TRES caminos terminales** del protector y la invariante `is_loading == False` en todos: (1) acceso permitido (`_validate_session` → `True`): termina sin `TypeError`, `end_navigation_generation()` invocado sin argumento; (2) acceso denegado (`_validate_session` → `False`, redirección a `/login`): termina sin `TypeError`, `end_navigation_generation()` invocado sin argumento; (3) generación obsoleta (`validate_generation` → `False` → DROP, con la generación activa ya finalizada e `is_loading == False`): termina sin `TypeError` y `end_navigation_generation` NO se invoca (research §Hallazgo 2; contract §1/§2; data-model §Transiciones; plan §Notas; Clarificación Q→A: 3 caminos)
- [x] T005 [P] Actualizar las aserciones de `tests/unit/test_proteccion_rutas.py:27,37` que codifican la firma errónea: `mock_end.assert_called_with("test-gen-N")` → `mock_end.assert_called_once_with()` (sin argumento) (FR-010; research §Hallazgo 2; quickstart §Corrección)
- [x] T006 [P] Des-mockear el `patch` de `end_navigation_generation` en `tests/integration/test_auth_login.py:106` y validar la invocación real del método, de modo que el test de integración no enmascare el contrato (FR-010 — acción determinista, sin opción de "mantener el patch"; research §Hallazgo 2, línea 58)

**RED esperado (Phase 2 check)**: `pytest tests/unit/test_regresion_firma_proteccion.py -q` FALLA con `TypeError: ... end_navigation_generation() takes 1 positional argument but 2 were given` en los caminos (1) y (2); confirmar RED antes de pasar a Phase 3 (TDD, constitution §13).

---

## Phase 3: User Story 1 - Inicio de sesión válido que llega al panel sin error (Priority: P1) 🎯 MVP

**Goal**: Tras un login con credenciales válidas, el usuario llega a `/dashboard` sin ver "An error occurred. Contact the website administrator." y sin `TypeError` en logs.

**Independent Test**: `pytest tests/unit/test_regresion_firma_proteccion.py tests/unit/test_proteccion_rutas.py -q` en verde SOLO tras aplicar el fix; en el entorno desplegado, un login válido llega a `/dashboard` sin error genérico (SC-001/SC-002).

### Implementation for User Story 1

- [x] T007 [US1] Aplicar la corrección quirúrgica en `src/presentacion_reflex/state/auth_state.py:215`: `self.end_navigation_generation(gen_id)` → `self.end_navigation_generation()` (sin argumento), preservando `validate_generation`/`_validate_session`/`_sync_permissions` y el `async with self` (FR-001/FR-004; research §Hallazgo 5; contract §1)
- [x] T008 [US1] Añadir el log seguro de desenlace (FR-009) en `src/presentacion_reflex/state/auth_state.py` en `require_login_background`, en los dos caminos terminales: `logger.info("Protección de rutas: acceso permitido")` y `logger.warning("Protección de rutas: acceso denegado (redirección a /login)")`, SIN credenciales/token/usuario (contract §3; data-model §Log seguro)
- [x] T009 [US1] Verificar en local con el servidor en modo dev: `reflex run --env dev`, loggear con usuario válido, navegar a `/dashboard` y confirmar cero `TypeError` + log de desenlace `acceso permitido` (FR-001/FR-002; constitution §6/§10; quickstart §Matriz 1)

**Checkpoint**: User Story 1 funcional y verificable de forma independiente (logins válidos → panel sin error).

---

## Phase 4: User Story 2 - Navegación a cualquier ruta protegida con sesión válida sin error (Priority: P1)

**Goal**: Las 18 rutas protegidas cargan sin error genérico ni `TypeError` con sesión válida, incluida la recarga de página, verificado por navegación automatizada sobre el inventario (FR-003/SC-003/SC-005).

**Independent Test**: Navegación E2E Playwright sobre el inventario de rutas protegidas del contract §4 (18 rutas) con sesión válida, con `page.reload()` tras cada visita → cero `TypeError` y cero error genérico en carga y recarga.

### Tests for User Story 2 (TDD/validación) ⚠️

> Los specs E2E se ejecutan por terminal con `node`, cargando `.env` (`dotenv`, package.json devDependencies). Se requiere el harness Playwright (T042 de 077) habilitado en el alcance de esta feature (Clarificación Q4→Opción A; FR-008).

- [x] T010 [P] [US2] Escribir/ampliar el spec E2E de navegación sobre el inventario de rutas protegidas en `tests/e2e/navegacion_rutas_protegidas.spec.mjs` (nuevo): login con `TEST_USER`/`TEST_PASSWORD`, visitar las 18 rutas del contract §4 verificando ausencia de "An error occurred" en cada una, y tras cada visita ejecutar `page.reload()` confirmando ausencia de error genérico y `is_loading == False` (FR-003/SC-003/SC-005 + recarga E2E, Clarificación Q→A; contract §4)
- [x] T011 [US2] Habilitar el harness E2E dentro del alcance de 078: instalar dependencias de `package.json` (`npm install`) y validar ejecución de `node tests/e2e/login_valido.spec.mjs` para desbloquear la deuda T042 de la 077 (plan §Notas; quickstart §Comandos)

### Implementation for User Story 2

- [x] T012 [US2] Ejecutar el spec del inventario del T010 contra el estado **local primero** y confirmar cero `TypeError` y cero pantallas de error en las 18 rutas, sin spinner atascado en la carga ni tras `page.reload()` (SC-003 + SC-005 recarga; la validación contra el entorno desplegado queda en T023; contract §4; quickstart §Matriz 2/5)

**Checkpoint**: User Stories 1 Y 2 funcionan de forma independiente (login y toda la navegación protegida sin error, incluida recarga).

---

## Phase 5: User Story 3 - Sesión expirada que redirige a /login con mensaje (Priority: P2)

**Goal**: Con sesión inválida/vigencia vencida, la ruta protegida redirige a `/login` con "Sesión expirada. Por favor, inicie sesión nuevamente." sin lanzar `TypeError` (FR-005/US3).

**Independent Test**: `pytest` + E2E con token invalidado sobre una ruta protegida → redirección a `/login` con el mensaje canónico y sin excepción.

### Tests for User Story 3 ⚠️

- [x] T013 [P] [US3] Ampliar el test de regresión (`tests/unit/test_regresion_firma_proteccion.py`) con el camino de sesión inválida + generación válida: `_validate_session` → `False` debe producir redirección a `/login` (toast "Sesión expirada. Por favor, inicie sesión nuevamente.") y terminar sin `TypeError` con `end_navigation_generation()` invocado sin argumento e `is_loading == False` (FR-005; Edge Case §2; data-model §Transiciones; complementa el camino (2) de T004)
- [x] T014 [P] [US3] Ampliar `tests/unit/test_regresion_firma_proteccion.py` para el camino de error transitorio de BD en `_validate_session` (retorna `False` sin invalidar sesión): sin excepción y sin `TypeError` (FR-007/FR-005; Edge Case §3; behavior 077 preservado)

### Implementation for User Story 3

- [x] T015 [US3] Verificar el mensaje de sesión expirada y la redirección en local: `reflex run --env dev` con token vencido → `/login` + toast "Sesión expirada. Por favor, inicie sesión nuevamente." sin `TypeError` (FR-005/US3; quickstart §Matriz 7)

**Checkpoint**: User Stories 1, 2 Y 3 funcionan de forma independiente.

---

## Phase 6: User Story 4 - Sin regresiones en los demás flujos que usan el mixin de navegación (Priority: P2)

**Goal**: La corrección no rompe los demás consumidores de `end_navigation_generation()` (`personas_state.py:341`, `alertas_dashboard_state.py:92`) ni el flujo de login corregido por la 077 (FR-006/FR-007).

**Independent Test**: Matriz de regresión de autenticación de 10 puntos de la 077 en verde + flujos de `personas` y `alertas_dashboard` sin cambios (SC-004).

### Tests for User Story 4 ⚠️

- [x] T016 [P] [US4] Ejecutar la suite de tests de autenticación: `pytest tests/integration/test_auth_login.py tests/integration/test_auth_errores.py -q` (ambos archivos existen) para confirmar que ningún cambio en `test_auth_login.py` (T006) rompe flujos de la 077 (FR-007/SC-004)
- [x] T017 [P] [US4] Ejecutar tests de los consumidores del mixin: localizar y correr `pytest` sobre los tests de `personas_state` y `alertas_dashboard_state` (buscar `tests/**/test_*personas*.py`, `tests/**/test_*alertas*.py`) para confirmar `end_navigation_generation()` sin cambios (FR-006; contract §2)

### Implementation for User Story 4

- [x] T018 [US4] Ejecutar la matriz de regresión de autenticación de 10 puntos de la 077 (login válido, inválido/credenciales, usuario inactivo, fallos de red/backend/BD, rate limiting, RBAC, logout, sesión expirada) — usar los specs E2E existentes en `tests/e2e/` (`login_valido`, `login_invalido`, `login_fallos`, `regresion_sesion`, `regresion_rbac`, `regresion_ratelimit`) — en verde (SC-004; contract §5; quickstart §Matriz 6)
- [x] T019 [US4] Verificar `personas_state.py:341` y `alertas_dashboard_state.py:92` siguen invocando `end_navigation_generation()` sin argumento (sin modificaciones) tras el fix (FR-006; contract §2; Chesterton's Fence §12)

**Checkpoint**: Todos los User Stories funcionan de forma independiente y sin regresiones.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Validación final local + desplegada. La validación en el entorno desplegado (Railway, `inmovelar-production`) es **BLOQUEANTE** para cerrar la feature (Clarificación Q4; Assumptions).

- [x] T020 [P] Lint/tipo/format en la ruta tocada y tests (constitución §5): `ruff check src/presentacion_reflex/state/auth_state.py tests/unit/test_proteccion_rutas.py tests/unit/test_regresion_firma_proteccion.py`, `black --check src/presentacion_reflex/state/auth_state.py`, `mypy src/presentacion_reflex/state/auth_state.py`
- [x] T021 Ejecutar la suite completa: `pytest tests/ -q` en verde (FR-008/SC-006; gate §5)
- [x] T022 Confirmar RED→GREEN reproducible: con el test T004 y la versión pre-fix (con `git stash` del fix del T007 o revert temporal) el test FALLA; con el fix en verde — evidencia para el reporte de regresión (constitución §13)
- [x] T023 Validación desplegada BLOQUEANTE: tras desplegar la rama `bugfix/078-fix-login-error` a `inmovelar-production`, verificar SC-001 y SC-003 (incluida la recarga `page.reload()` sobre rutas del inventario, Edge Case 4) vía E2E contra la URL desplegada (`node tests/e2e/navegacion_rutas_protegidas.spec.mjs` con `TEST_USER`), SC-005 (sin spinner atascado, carga y recarga) y el log de desenlace FR-009 + **búsqueda activa** del patrón `TypeError` en los logs de Railway durante la ventana SC-002 (SC-001/SC-002/SC-003/SC-005/FR-009; Clarificación Q→A recarga y búsqueda activa; quickstart §Evidencia)
- [x] T024 Documentar la validación desplegada y adjuntar evidencias (capturas antes/después, logs FR-009, matriz 1-7) en la feature antes de cerrar; SIN dejar archivos de depuración en la raíz del repo (constitución §4/§10; quickstart §Evidencia)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - **BLOCKS** all user stories (el test RED T004/T005/T006 es prerequisito del fix T007)
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - **US1 (Phase 3)**: Solo depende del fix T007 (Fase 2)
  - **US2 (Phase 4)**: Depende de US1 (requiere el fix aplicado) + harness E2E (T011)
  - **US3 (Phase 5)**: Depende de US1 (camino de denegado ya cubierto por el fix)
  - **US4 (Phase 6)**: Depende de US1 (verifica no-regresión del fix)
- **Polish (Final Phase)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: MVP — después de Fase 2, primer incremento verificable
- **User Story 2 (P1)**: Puede empezar tras US1 + Fase 2 (el inventario E2E necesita el fix)
- **User Story 3 (P2)**: Independiente de US2; depende del fix
- **User Story 4 (P2)**: Independiente de US2/US3; depende del fix (matriz 077)

### Within Each User Story

- Tests (cuando existen) MUST be written and FAIL before implementation
- Fix del protector (T007) antes de integración E2E
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- **Phase 2 tests**: T004, T005, T006 marcan [P] — pueden ejecutarse en paralelo (archivos distintos: `test_regresion_firma_proteccion.py` nuevo, `test_proteccion_rutas.py`, `test_auth_login.py`)
- **Setup**: T002 y T003 en paralelo (verificación sin dependencias)
- **US3 tests (T013, T014)**: en paralelo (mismo archivo → secuencial recomendado si solo hay un dev; marcados [P] por independencia lógica de caminos)
- **US4 verificación (T016, T017 y T018, T019)**: pueden ejecutarse en paralelo (specs/tests distintos + verificación estática)

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Phase 1 (setup ligero) + Phase 2 (test RED T004 + alinear T005/T006)
2. Phase 3: fix de 1 línea T007 + log FR-009 T008
3. **STOP and VALIDATE**: `pytest tests/unit/test_regresion_firma_proteccion.py -q` en verde + servidor dev (T009)
4. Deploy si está listo

### Incremental Delivery

1. Fase 2 completa (blindaje en RED) → corrección T007 → US1 en verde (MVP)
2. US2 (inventario E2E con recarga) → SC-003/SC-005
3. US3 (sesión expirada/transitorio) + US4 (matriz 077) → sin regresiones
4. Polish (T020-T024): la validación desplegada BLOQUEANTE cierra la feature

### Parallel Team Strategy

Con un solo desarrollador/IA, seguir el orden secuencial de IDs; con varios, los [P] de la Fase 2 pueden repartirse.

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability (Setup/Foundational/Polish: sin label)
- TDD obligatorio: el test T004 debe fallar con el bug presente (RED) antes de T007 (constitución §13; plan §Notas)
- FR-008 cubre los TRES caminos terminales del protector: permitido, denegado (redirección `/login`) y generación obsoleta (DROP sin llamado a `end_navigation_generation`), todos con `is_loading == False` (Clarificación Q→A; en el DROP, la generación activa ya finalizada — plan §Notas)
- SC-003/SC-005 incluyen la recarga de página (`page.reload()`) sobre el inventario de rutas protegidas con sesión válida (Clarificación Q→A; Edge Case 4)
- SC-002 exige búsqueda ACTIVA del patrón `TypeError` y de las líneas FR-009 en los logs de Railway, no solo ausencia visual (T023; Clarificación Q→A)
- Los tests actuales (`test_proteccion_rutas.py:27,37`, `test_auth_login.py:106`) CODIFICAN la firma errónea y DEBEN alinearse de forma determinista (FR-010; research §Hallazgo 2)
- El mixin NO cambia: `end_navigation_generation()` se invoca sin argumento y es idempotente (FR-001/FR-004; contract §2)
- El log FR-009 es seguro: sin credenciales, token, `nombre_usuario`, cookies (contract §3; Zero Leak §4)
- El harness E2E (T042 de 077) queda dentro del alcance de 078 (FR-008; Clarificación Q4)
- Commit con Conventional Commits tras cada tarea o grupo lógico (`fix(estado): ...`, `test(estado): ...`) — constitución §6
- Evitar: tareas vagas, conflictos en el mismo archivo, dependencias cruzadas que rompan independencia de stories
