# Tasks: Corrección del flujo de inicio de sesión (spinner infinito)

**Input**: Design documents from `specs/077-fix-login-spinner/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: La constitución y el spec exigen TDD (tests solicitados): unit de excepciones/mensajes y de mixin, integración con BD de prueba, E2E Playwright con evidencia (Q3).

**Organization**: Tasks grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization y toolchain de validación

- [X] T001 [P] Crear y cambiar al branch `bugfix/077-fix-login-spinner` (git switch -c bugfix/077-fix-login-spinner) desde `feat/desarrollo-experto-elite` (la rama `develop` no existe en este repo; fechar el commit base con `git log --oneline -3`)
- [X] T002 [P] Verificar toolchain local: `reflex==0.8.28.post1`, `pytest`, `ruff`/`black`/`mypy`, `playwright@^1.60` (npm install) y `.env` de dev con `DATABASE_URL` de BD de prueba

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Evidencia STOP-THE-LINE + modelo de errores tipados y límites de recurso que TODAS las user stories necesitan.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T003 [P] Ejecutar el repro E2E existente (`node tests/e2e/login_visible.spec.mjs` con `TEST_USER`/`TEST_PASSWORD`) y registrar evidencia "antes": URL final, estado del botón, consola del navegador, eventos WebSocket y traza `[AUTH_DEBUG]`; guardar captura "antes"; documentar el hallazgo confirmado (Hallazgos 1–4 de research.md) en el artefacto de la feature (FR-001/SC-008, STOP-THE-LINE)
- [X] T004 [P] Crear errores tipados de dominio `ErrorCredencialesInvalidas`, `ErrorUsuarioInactivo`, `ErrorRecurso`, `ErrorPoliticaIntentos` en `src/dominio/excepciones/excepciones_base.py` (sin dependencias externas, docstrings Google). `ErrorRecurso` DEBE aceptar un discriminador opcional `codigo_recurso` (`RED | BACKEND | BD | INESPERADO`) para que el mapeo de T028/T021 sea determinista (hallazgo B1 del analyze)
- [X] T005 [P] Crear `src/dominio/excepciones/resultado_autenticacion.py` con `ExitoAutenticacion(usuario, sesion)` y el resultado tipado de autenticación (data-model.md §Errores tipados). Re-exportar desde aquí las 4 excepciones de `excepciones_base.py` para mantener una sola fuente de verdad y evitar imports duplicados (hallazgo I4 del analyze: plan.md fijó aquí las clases de error; la fuente es `excepciones_base.py`)
- [X] T006 [P] Parametrizar `statement_timeout` (y opcionalmente `lock_timeout`) en `pg_config` de `src/infraestructura/persistencia/database.py` vía `DB_STATEMENT_TIMEOUT` (default 5000 ms, UPPER_SNAKE, sin magic numbers) — research.md Hallazgo 4
- [X] T007 [P] Añadir `LOGIN_OPERATION_DEADLINE_SECONDS` (default 12) a la configuración/env (`src/infraestructura/configuracion/settings.py` y `.env`) y un helper de deadline de operación en `src/aplicacion/servicios/servicio_autenticacion.py` que produzca `ErrorRecurso(codigo_recurso="BACKEND")` al expirar (data-model.md §Configuración; FR-009). El helper solo lee el reloj del sistema; NO es un temporizador de interfaz (contracts/flujo_login.md punto 10)
- [X] T008 Verificar símbolos nuevos antes de tocar la app: `python -c "from src.presentacion_reflex.styles import BASE_STYLE"` (Regla de Build) y `python -m compileall src/dominio src/aplicacion`

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Login válido que finaliza la carga y llega al panel (Priority: P1) 🎯 MVP

**Goal**: El login con credenciales válidas termina el ciclo de carga, redirige a `/dashboard` y el panel renderiza con permisos; el indicador del botón solo refleja la operación en curso.

**Independent Test**: E2E con credenciales válidas: el botón termina el spinner, el evento llega a desenlace (traza backend), la sesión persiste y `/dashboard` carga sin volver a `/login` (US1, SC-001/SC-004).

### Tests for User Story 1 ⚠️ primero (rojo) segun TDD

- [X] T009 [P] [US1] Unit test (sin I/O): `login()` con éxito termina el generador y deja `login_in_progress=False` e `is_loading` según contrato (False en ruta de éxito cuando el redirect es el desenlace final) en `tests/unit/test_login_exito.py`. Incluir aserción de control de concurrencia: un segundo envío mientras `login_in_progress=True` NO lanza una segunda `autenticar()` (edge "doble clic", spec; hallazgo G3 del analyze)
- [X] T010 [P] [US1] Unit test (sin I/O): `require_login_background` restablece `is_loading` (`end_navigation_generation()`) en TODAS sus rutas (válido→continúa; inválido→redirige; error transitorio→fallback) en `tests/unit/test_proteccion_rutas.py`
- [X] T011 [P] [US1] Integration test con BD de prueba: login válido persiste sesión en BD y emite cookie `_s` (token 8 h) en `tests/integration/test_auth_login.py`. Incluir caso de migración transparente de hash SHA256 legacy→Bcrypt durante el login (edge spec; FR-010; hallazgo U2 del analyze)
- [X] T012 [P] [US1] E2E test: login válido redirige a `/dashboard`, botón sin spinner, consola limpia en `tests/e2e/login_valido.spec.mjs`. Registrar medición del tiempo credencial→panel (assert de umbral < 5 s local; el compare de < 10 s desplegado se confirma en T036) (SC-002; hallazgo U1 del analyze)

### Implementation for User Story 1

- [X] T013 [P] [US1] Añadir señal dedicada `login_in_progress: bool` en `src/presentacion_reflex/state/auth_state.py` (única fuente del `loading` del botón; data-model.md §Estados runtime)
- [X] T014 [P] [US1] Corregir `require_login_background` en `src/presentacion_reflex/state/auth_state.py`: emparejar `start_navigation_generation()` con `end_navigation_generation()` en todas las salidas y emitir `toast`/`redirect` FUERA del `async with self:` (research.md Hallazgos 1 y 3)
- [X] T015 [US1] Reestructurar `login()` en `src/presentacion_reflex/state/auth_state.py`: ruta de éxito con `login_in_progress=False`, cookies `_s`/`_r` en el mismo delta que el `rx.redirect("/dashboard")` y desenlace terminal garantizado; guard de concurrencia: si `login_in_progress=True` el handler retorna sin segunda autenticación; toda excepción no tipada se envuelve en `ErrorRecurso(codigo_recurso="INESPERADO")` (research.md Hallazgo 2; contracts/flujo_login.md)
- [X] T016 [US1] Enlazar el botón "Acceder al Panel" a `loading=AuthState.login_in_progress` en `src/presentacion_reflex/pages/login.py` (desvinculado de `is_loading`)
- [X] T017 [US1] Integration test (artefacto verificable de FR-006, hallazgo U4 del analyze): en `tests/integration/test_auth_login.py` verificar que el `on_load` de `/dashboard` con sesión válida valida la sesión (`_validate_session`), carga permisos del rol y NO redirige a `/login` (sin vuelta); caso con sesión inválida → redirige a `/login`

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently (MVP)

---

## Phase 4: User Story 2 - Credenciales inválidas que muestran error y restablecen la carga (Priority: P1)

**Goal**: Los fallos de credenciales (incorrectas, inexistentes, usuario inactivo) terminan con texto canónico y spinner restablecido, sin filtrar detalles técnicos.

**Independent Test**: E2E con contraseña incorrecta y usuario inexistente: mensaje canónico visible y `login_in_progress=False`; usuario inactivo muestra "El usuario se encuentra inactivo." (US2, SC-005).

### Tests for User Story 2 ⚠️ primero (rojo) segun TDD

- [X] T018 [P] [US2] Unit test (sin I/O): mapeo `ErrorCredencialesInvalidas`→"Credenciales inválidas. Verifique usuario y contraseña." y `ErrorUsuarioInactivo`→"El usuario se encuentra inactivo." en `tests/unit/test_mensajes_error.py` (catálogo `contracts/errores_autenticacion.md`)
- [X] T019 [P] [US2] E2E test: contraseña incorrecta y usuario inexistente muestran texto canónico y restablecen el spinner en `tests/e2e/login_invalido.spec.mjs`. Registrar medición del tiempo respuesta→spinner restablecido (assert < 2 s, SC-005; hallazgo U1 del analyze)

### Implementation for User Story 2

- [X] T020 [US2] Distinguir desenlaces en `src/aplicacion/servicios/servicio_autenticacion.py`: elevar `ErrorUsuarioInactivo` vs `ErrorCredencialesInvalidas` en `autenticar()` y verificar que la migración de hash SHA256→Bcrypt no altera el desenlace (research.md Hallazgo 5; data-model.md; edge migración; FR-010)
- [X] T021 [US2] Mapear errores tipados a los textos del catálogo canónico (`contracts/errores_autenticacion.md`) y restablecer `login_in_progress=False` en `src/presentacion_reflex/state/auth_state.py` (el discriminador `codigo_recurso` de T004 resuelve red vs BD cuando T028 lo consuma)
- [ ] T022 [US2] Garantizar zero-leak: `error_message` NUNCA se llena con `str(excepcion)`/detalle técnico; log seguro del desenlace sin credenciales (FR-011)

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Fallos de red / Backend / Base de Datos manejados sin cuelgue (Priority: P2)

**Goal**: Ante falla de BD, backend sin respuesta o excepción inesperada, el login termina con mensaje canónico y estado de carga restablecido, SIN temporizador de UI: el desenlace proviene del resultado real (límites de recurso).

**Independent Test**: Simular indisponibilidad de BD/backend durante el envío: el evento termina con el texto canónico correspondiente y `/login` no queda colgado, dentro del deadline de recurso (US3, SC-006).

### Tests for User Story 3 ⚠️ primero (rojo) segun TDD

- [X] T023 [P] [US3] Unit test (sin I/O): el deadline de operación expirado produce `ErrorRecurso(codigo_recurso="BACKEND")` (mensaje canónico red/backend) en `tests/unit/test_deadline_recurso.py`
- [X] T024 [P] [US3] Integration test con BD de prueba: BD simulada no disponible → desenlace terminal + `login_in_progress=False` en `tests/integration/test_auth_errores.py` (simulación vía mock del pool/`query` o `DB_STATEMENT_TIMEOUT` mínimo; sin afectar datos reales)
- [X] T025 [P] [US3] E2E test: backend/BD sin respuesta y excepción inesperada terminan con texto canónico y spinner restablecido en `tests/e2e/login_fallos.spec.mjs`

### Implementation for User Story 3

- [X] T026 [US3] Aplicar el deadline de operación de login (`LOGIN_OPERATION_DEADLINE_SECONDS`) como excepción tipada `ErrorRecurso` en `src/presentacion_reflex/state/auth_state.py`/`src/aplicacion/servicios/servicio_autenticacion.py` (helper de T007; FR-009)
- [X] T027 [US3] Confirmar que `DB_STATEMENT_TIMEOUT` convierte una consulta colgada en error real (no desenlace silencioso) y propagarlo como `ErrorRecurso(codigo_recurso="BD")` en `src/aplicacion/servicios/servicio_autenticacion.py` (T006; FR-009)
- [X] T028 [US3] Mapear red/backend sin respuesta → "No se pudo conectar con el servidor. Verifique su conexión e intente de nuevo." (`ErrorRecurso.codigo_recurso` en `RED`/`BACKEND`) y BD no disponible → "El servicio no está disponible en este momento. Intente de nuevo." (`codigo_recurso="BD"`) (FR-009; contracts/errores_autenticacion.md) en `src/presentacion_reflex/state/auth_state.py`

**Checkpoint**: All user stories should now be independently functional

---

## Phase 6: User Story 4 - Cuidado y cierre: RBAC y sin regresiones (Priority: P2)

**Goal**: La corrección NO altera RBAC, logout, sesión expirada, rutas protegidas ni rate limiting; se garantizan 0 regresiones y no existe ningún timeout artificial ni ocultamiento del spinner.

**Independent Test**: Matriz de regresión de autenticación (login válido/inválido, logout, sesión expirada, ruta protegida sin sesión, RBAC por rol, bloqueo por 5 intentos) toda en verde (US4, SC-007).

### Tests for User Story 4 ⚠️ primero (rojo) segun TDD

- [X] T029 [P] [US4] E2E regression test: logout limpia cookies/estado y redirige a `/login`; sesión expirada redirige con mensaje sin loop; ruta protegida sin sesión → `/login` en `tests/e2e/regresion_sesion.spec.mjs`
- [X] T030 [P] [US4] E2E RBAC test: Admin accede a módulos; usuario con rol restringido no accede, en `tests/e2e/regresion_rbac.spec.mjs` (requiere credenciales del usuario restringido definidas en `.env`/config, ver T036)
- [X] T031 [P] [US4] E2E rate limiting test: más de 5 intentos fallidos desde la misma IP → bloqueo con "Demasiados intentos. Intente de nuevo en 15 minutos." y spinner restablecido en `tests/e2e/regresion_ratelimit.spec.mjs`. **IMPORTANTE (hallazgo G1 del analyze)**: ejecutar SOLO contra el entorno local/dev (el rate limit es en memoria de proceso); NUNCA contra el desplegado Railway en la misma tanda que T019/T025/T036, para no bloquear la IP real del runner 15 min

### Implementation for User Story 4

- [X] T032 [US4] Verificar que la corrección no altera la lógica RBAC ni el rate limiting en `src/aplicacion/servicios/servicio_permisos.py` y en el bloqueo por intentos de `login()` (FR-007/FR-008; solo se garantiza que no produzcan cuelgues)
- [X] T033 [US4] Auditoría final anti-mitigantes: confirmar en `src/presentacion_reflex/state/auth_state.py` y `src/presentacion_reflex/pages/login.py` que NO existe ningún temporizador de interfaz ni ocultamiento del spinner (FR-002; US4 scenario 5)

**Checkpoint**: All user stories should now be independently functional

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Observabilidad segura, validación final completa (local + desplegada) y cierre de la feature.

- [X] T034 [P] Implementar logging seguro FR-011 en `src/presentacion_reflex/state/auth_state.py`: eventos `[AUTH_DEBUG]` de inicio/desenlace con el formato de `contracts/errores_autenticacion.md` (código, desenlace, usuario sin hash, transitorio; zero-leak)
- [X] T035 [P] Ejecutar suite de calidad completa con verificación de cobertura (hallazgo C1 del analyze): `pytest tests/unit tests/integration -q --cov=src/dominio --cov=src/aplicacion --cov-report=term-missing` confirmando dominio 100% y lógica nueva >90% (constitucion §5), `ruff check src/`, `black --check src/`, `mypy src/`, `python scripts/check_syntax.py` (path correcto del repo; quickstart quedó obsoleto) y `node tests/e2e/login_valido.spec.mjs tests/e2e/login_invalido.spec.mjs tests/e2e/login_fallos.spec.mjs tests/e2e/regresion_*.spec.mjs`
- [X] T036 Validación desplegada bloqueante (Q2): ejecutar la matriz de los 10 puntos contra `https://inmovelar-production.up.railway.app` con credenciales reales de prueba (Admin activo, rol restringido — crearlos/definirlos en config antes; incluye roles/permisos y el usuario inactivo/inexistente de US2) y registrar capturas antes/después + traza; confirmar SC-002/SC-005 en el entorno desplegado (< 10 s y < 2 s) (quickstart.md §Matriz)
- [X] T037 Documentar la causa raíz confirmada (SC-008): punto exacto del flujo donde la operación quedaba bloqueada, repro antes/después, actualizar `research.md`/artefacto de la feature y `ESTADO_TAREAS.md` (convenciones semver/conventional commits)
- [X] T038 [P] Cierre de branch: `git status` limpio, commit convencional (`fix(auth): ...`), push y verificación del despliegue en Railway

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories (diagnóstico con evidencia y errores tipados/limites primero)
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User stories pueden avanzar en serie por prioridad (US1 → US2 → US3 → US4); US1 y US2 son P1
- **Polish (Final Phase)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P1)**: Can start after Foundational (Phase 2); reutiliza errores tipados (T004/T005) y el mapeo de mensajes
- **User Story 3 (P2)**: Can start after Foundational (Phase 2); depende de límites de recurso (T006/T007 y del `codigo_recurso` de T004)
- **User Story 4 (P2)**: Can start after Foundational (Phase 2); valida no-regresión sobre US1–US3 completadas

### Within Each User Story

- Tests MUST be written and FAIL before implementation (TDD, constitución §5/§13)
- Errores tipados y resultado → servicio → handler de estado → UI
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- All tests for a user story marked [P] can run in parallel
- Different user stories can be worked on in parallel by different team members
- **ADVERTENCIA**: T013–T016 editan `auth_state.py`/`login.py` (US1), T021/T022 (US2) y T028 (US3) también tocan `auth_state.py` → NO ejecutar en paralelo tareas que escriban el mismo archivo; serializar por fase de user story
- **ADVERTENCIA rate limiting (G1)**: T019 (fallo de credenciales), T031 (bloqueo por intentos) y T025/T036 (fallos de red) comparten el rate limit en memoria si corren contra el mismo proceso; ejecutar T031 contra un proceso local aislado

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together (TDD, red first):
Task: "Unit test login exitoso en tests/unit/test_login_exito.py"
Task: "Unit test proteccion de rutas en tests/unit/test_proteccion_rutas.py"
Task: "Integration test login con BD en tests/integration/test_auth_login.py"
Task: "E2E login valido en tests/e2e/login_valido.spec.mjs"

# Then implementation (T013/T014 en paralelo; T015/T016/T017 en serie sobre los mismos archivos):
Task: "T013 login_in_progress en auth_state.py"
Task: "T014 require_login_background en auth_state.py"  (NO junto con T015: mismo archivo)
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories; diagnóstico con evidencia incluido)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: E2E login válido /dashboard + traza + consola limpia (SC-001)
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo
4. Add User Story 3 → Test independently → Deploy/Demo
5. Add User Story 4 → Test independently (regresión completa) → Deploy/Demo
6. Polish: matriz completa local + desplegada (Q2) → closure (SC-008)

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together (diagnóstico evidencia en T003 es una sola persona)
2. Once Foundational is done:
   - Developer A: User Story 1 (P1)
   - Developer B: User Story 2 (P1) — después de T004/T005
   - Developer C: User Story 3 (P2)
3. Stories complete and integrate independently (serializar escrituras sobre `auth_state.py`)

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing (TDD, constitución §5)
- Phase 2 T003 es la evidencia STOP-THE-LINE (constitución §13): no corregir hasta confirmar la causa raíz
- Respetar la Regla de Build: verificar símbolos nuevos (T008) antes de tocar `auth_state.py`/`login.py`
- Commit after each task or logical group; convención `fix(auth): ...`
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
- **Hallazgos del analyze incorporados**: C1 (cobertura en T035), B1 (`codigo_recurso` en T004/T028), I4 (fuente de errores = `excepciones_base.py`) , G1 (T031 solo local), U1 (medición SC-002/SC-005 en T012/T019/T036), U2 (migración hash en T011/T020), U4 (T017 como test de integración), G3 (guard de concurrencia en T009/T015), I1 (base branch real), I2 (path correcto de `scripts/check_syntax.py`)