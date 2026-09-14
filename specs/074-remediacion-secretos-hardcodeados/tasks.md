# Tasks: Remediación de Credenciales Hardcodeadas y Datos Sensibles Expuestos

**Input**: Design documents from `/specs/074-remediacion-secretos-hardcodeados/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md

**Tests**: Se incluyen únicamente donde la Constitución §5 los exige (lógica nueva de validación) y donde la spec exige evidencia verificable (FR-016). No es un flujo TDD estricto.

**Organization**: Tareas agrupadas por historia de usuario (US-01…US-05 de spec.md) para permitir implementación y prueba independientes.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Puede ejecutarse en paralelo (archivos distintos, sin dependencias pendientes)
- **[Story]**: Historia de usuario a la que pertenece la tarea (US1…US5)
- Todas las tareas incluyen rutas de archivo exactas

## Path Conventions

- Proyecto único: rutas relativas a la raíz del repositorio (`config/`, `scripts/`, `tests/`, `.github/`, `docs/`, `assets/`).
- Los valores comprometidos nunca se reproducen en descripciones, archivos ni evidencia: se referencian por hallazgo (`H-01`…`H-03`).

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Aislar el trabajo y preparar herramientas y estructura de evidencia.

- [ ] T001 Crear la rama `074-remediacion-secretos-hardcodeados` desde `main` y confirmar que el working tree solo contiene cambios propios (no incluir `image.png` ni archivos locales ajenos a la iniciativa)
- [ ] T002 [P] Verificar herramientas de remediación (`gitleaks version`, `git filter-repo --version`) e instalar `git-filter-repo` si falta; dejar constancia en `docs/security/INVENTARIO_REMEDIACION_074.md`
- [ ] T003 [P] Crear los directorios `docs/security/` y `docs/decisions/`
- [ ] T004 [P] Ejecutar la línea base de coincidencias sobre los archivos trackeados usando la lista protegida (sin imprimir ni versionar literales) y anotar totales por hallazgo para contrastar con los Apéndices A–C de la auditoría

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Inventario enmascarado y mapa de configuración, requeridos por todas las historias.

**⚠️ CRITICAL**: Ninguna historia puede comenzar hasta completar esta fase.

- [ ] T005 Crear `docs/security/INVENTARIO_REMEDIACION_074.md` conforme a `specs/074-remediacion-secretos-hardcodeados/contracts/inventario-hallazgos.md` (secciones Resumen, Hallazgos `H-01`…`H-03`, Ubicaciones, PII, Evidencia y Estado de criterios SC)
- [ ] T006 [P] Poblar las ubicaciones `U-###` desde los Apéndices A/B/C de la auditoría y la línea base de T004, sin reproducir valores
- [ ] T007 [P] Listar entornos y consumidores afectados por las credenciales (local, Railway, CI, scripts) según `specs/074-remediacion-secretos-hardcodeados/contracts/configuracion-credenciales.md` y registrarlos en el inventario
- [ ] T008 Verificar que `docs/security/INVENTARIO_REMEDIACION_074.md` no contiene literales (escaneo con reglas generalizadas) y registrar evidencia `E-###`

**Checkpoint**: Inventario y contrato de configuración listos; las historias pueden comenzar.

---

## Phase 3: User Story 1 (US-01) - Revocación y rotación de las credenciales expuestas (Priority: P1) 🎯 MVP

**Goal**: Invalidar las tres credenciales expuestas y dejar constancia verificable de la rotación y de la continuidad del servicio.

**Independent Test**: Intentar autenticarse/conectarse con los valores comprometidos debe fallar; la aplicación y los scripts autorizados operan con los valores nuevos inyectados desde configuración externa.

- [ ] T009 [US1] Documentar el procedimiento de rotación (pasos, responsables, ventana, rollback) en `docs/security/ROTACION_CREDENCIALES_074.md`
- [ ] T010 [P] [US1] Actualizar la configuración externa de cada entorno con las credenciales nuevas (variables de Railway, `.env` local no versionado, secretos de CI) sin exponer valores
- [ ] T011 [P] [US1] Rotar la credencial de la cuenta administradora y registrar evidencia `E-###` (fecha y responsable)
- [ ] T012 [P] [US1] Rotar la contraseña de la base de datos y verificar la conectividad de la aplicación
- [ ] T013 [P] [US1] Rotar o eliminar la credencial de la cuenta de prueba según la confirmación de privilegios
- [ ] T014 [US1] Verificar que los valores comprometidos ya no autentican (administrador, base de datos y cuenta de prueba) y registrar evidencia
- [ ] T015 [US1] Revisar los registros de acceso desde 2026-05-25 y documentar hallazgos y acciones tomadas (FR-015) en `docs/security/INVENTARIO_REMEDIACION_074.md`
- [ ] T016 [US1] Verificar la continuidad operativa (inicio de sesión, generación de PDF y liquidaciones) y registrar evidencia (SC-004)

**Checkpoint**: Las credenciales expuestas están invalidadas y el servicio continúa operativo.

---

## Phase 4: User Story 2 (US-02) - Eliminación de credenciales hardcodeadas del código y la documentación (Priority: P1)

**Goal**: Cero literales y cero fallbacks inseguros en archivos versionados, con fallo explícito cuando falta configuración.

**Independent Test**: Búsqueda estática sin coincidencias y ejecución de un consumidor sin variables que falla con mensaje accionable.

- [ ] T017 [US2] Endurecer `rxconfig.py` eliminando cualquier construcción de URL con contraseña por defecto y exigiendo configuración externa (FR-002/FR-004)
- [ ] T018 [US2] Añadir validadores fail-fast de credenciales en `src/infraestructura/configuracion/settings.py` siguiendo el patrón de `secret_key` (FR-004)
- [ ] T019 [P] [US2] Crear pruebas unitarias de los validadores en `tests/unit/test_settings_credenciales.py` (variable ausente ⇒ aborta con mensaje y sin exponer valores)
- [ ] T020 [P] [US2] Eliminar fallbacks literales en `config/shared_db_config.py`, `config/rxconfig.py` y `config/sanitize_credentials.py`
- [ ] T021 [P] [US2] Eliminar fallbacks literales en `migraciones/database_config.py`, `migraciones/postgres_config.py`, `migraciones/migrate_to_postgresql.py`, `migraciones/verify_connection.py`, `migraciones/run_checklist.py`, `migraciones/sync_schema_columns.py`, `migraciones/create_bonificaciones_table.py`, `migraciones/inspect_migration_conflict.py`, `migraciones/migrate_postgres_local_to_railway.py`, `migraciones/extract_missing_ddl.py`, `migraciones/fix_schema_and_migrate_final.py` y `migraciones/retry_full_migration_v2.py`
- [ ] T022 [P] [US2] Eliminar fallbacks literales en `scripts/empty_tables.py`, `scripts/unblock_admin.py`, `scripts/create_permissions_tables.py`, `scripts/apply_fix.py`, `scripts/apply_fix_v2.py`, `scripts/apply_audit_final.py`, `scripts/apply_audit_full.py`, `scripts/verify_fix.py`, `scripts/verify_schema.py`, `scripts/verify_local_postgres.py`, `scripts/generate_triggers.py`, `scripts/debug_sql.py`, `scripts/test_simple_trigger.py`, `scripts/create_ipc_table.py`, `scripts/create_bonif_table.py`, `scripts/diagnose_codeudor_35.py`, `scripts/list_local_schema.py`, `scripts/list_local_booleans.py`, `scripts/extract_local_views.py`, `scripts/check_permissions_tables.py`, `scripts/apply_legal_rep_migration_standalone.py` y `scripts/force_clean_incidentes.py` (usar configuración externa sin valores por defecto)
- [ ] T023 [P] [US2] Sanear la documentación expuesta en `migraciones/README_MIGRACION.md`, `migraciones/REPORTE_MIGRACION.md`, `migraciones/CHECKLIST_VERIFICACION.md`, `migraciones/GUIA_RAPIDA.txt` y `migraciones/AGREGAR_A_ENV.txt` sustituyendo valores por marcadores y nombres de variables
- [ ] T024 [P] [US2] Parametrizar credenciales en `tests/e2e/conftest.py`, `tests/test_dashboard_row4.py`, `tests/test_playwright_liquidacion_asesores.py`, `tests/test_playwright_filtro_asesores.py`, `playwright_test.py` y `test_login_visible.mjs` mediante variables de entorno sin valores por defecto
- [ ] T025 [P] [US2] Retirar o parametrizar `scripts/diagnostico/test_login_produccion.py`, `scripts/diagnostico/auditoria_reportes.py`, `scripts/diagnostico/auditoria_simple.py`, `scripts/diagnostico/auditoria_detallada.py`, `scripts/diagnostico/auditoria_recaudos_check.py` y `scripts/diagnostico/playwright_test.py`, eliminando del tracking lo que no sea necesario (FR-018)
- [ ] T026 [P] [US2] Actualizar referencias enmascaradas en `docs/superpowers/plans/2026-07-02-incident-liquidation-sync.md`, `specs/007-playwright-validation/quickstart.md`, `specs/008-playwright-prod-diag/quickstart.md`, `specs/009-fix-prod-diag-bugs/quickstart.md`, `specs/040-personas-module-documentation/spec.md`, `specs/040-personas-module-documentation/tasks.md`, `docs/assets/screenshots/Dashboard/README.md` y `docs/assets/screenshots/Personas/README.md`
- [ ] T027 [US2] Verificar cero literales en el árbol con `git grep` y reglas generalizadas, y registrar evidencia `E-###` (SC-001)
- [ ] T028 [US2] Verificar el modo de fallo seguro ejecutando consumidores representativos sin variables y registrar evidencia (FR-004)

**Checkpoint**: El árbol de trabajo versionado no contiene credenciales y la configuración falla de forma segura.

---

## Phase 5: User Story 3 (US-03) - Purga del historial de versiones (Priority: P2)

**Goal**: El historial completo queda libre de los valores comprometidos y de rutas con PII, con coordinación del equipo.

**Independent Test**: Un clon nuevo no contiene los valores ni archivos con PII en ningún commit, rama o etiqueta.

- [ ] T029 [US3] Inventariar ramas, PRs y etiquetas activas y notificar la ventana de reescritura a los colaboradores (FR-009)
- [ ] T030 [US3] Crear un clon espejo de respaldo en `C:\Users\PC\AppData\Local\Temp\opencode\velar-mirror.git` (`git clone --mirror`)
- [ ] T031 [US3] Generar el archivo temporal de reemplazos (literales → `***REMOVED***`) fuera del repositorio y verificar que no queda versionado ni dentro del árbol de trabajo
- [ ] T032 [US3] Ejecutar `git filter-repo --replace-text` sobre el espejo con el archivo de T031
- [ ] T033 [US3] Ejecutar `git filter-repo --invert-paths` sobre el espejo para `assets/exports/`, `assets/pdfs/` y artefactos SQLite locales
- [ ] T034 [US3] Verificar la purga en un clon nuevo (escaneo de historial completo con la configuración protegida y búsquedas en `git log --all -p`) y registrar evidencia (SC-002)
- [ ] T035 [US3] Reescribir el remoto (force-push coordinado con la protección de rama), publicar la guía de re-clonado y confirmar ramas reconciliadas o descartadas (SC-007)
- [ ] T036 [US3] Registrar en `docs/security/INVENTARIO_REMEDIACION_074.md` la evidencia completa de la purga (fechas, responsables y resultados)

**Checkpoint**: El historial remoto está purgado y el equipo notificado/re-clonado.

---

## Phase 6: User Story 4 (US-04) - Prevención de reincidencia mediante detección automatizada (Priority: P2)

**Goal**: El gate de CI detecta los patrones comprometidos con denylista protegida y bloquea fusiones de forma fail-closed.

**Independent Test**: Un señuelo introducido en una rama de prueba hace fallar el check; un cambio limpio pasa.

- [ ] T037 [US4] Crear `.gitleaks.toml` versionado con reglas generalizadas (fallback de `DB_PASSWORD`, DSN con credenciales, variables `PASSWORD/CONTRASEÑA` literales y `fill()` de Playwright) sin allowlists para el informe ni para la configuración, y eliminar el `gitleaks.toml` local que contiene literales
- [ ] T038 [US4] Actualizar `.github/workflows/security-scan.yml` para exigir el secreto `GITLEAKS_KNOWN_LEAKS_REGEX`, componer la configuración final en `$RUNNER_TEMP/gitleaks-protegido.toml` y ejecutar el escaneo vía `GITLEAKS_CONFIG` con comportamiento fail-closed
- [ ] T039 [US4] Configurar el secreto protegido y el check requerido `security-scan` en la protección de la rama `main` (tarea operativa; registrar en el inventario)
- [ ] T040 [US4] Redactar `docs/decisions/ADR-074-estrategia-escaneo-secretos.md` con contexto, decisión, alternativas y consecuencias
- [ ] T041 [US4] Ejecutar la prueba controlada de reintroducción con un señuelo en una rama temporal y registrar evidencia (SC-005)
- [ ] T042 [US4] Verificar que el gate bloquea la fusión (check en `failure`) y registrar evidencia (SC-010)

**Checkpoint**: La reincidencia queda prevenida y verificada de extremo a extremo.

---

## Phase 7: User Story 5 (US-05) - Higiene de datos personales versionados (Priority: P3)

**Goal**: Los archivos con datos personales reales dejan de estar versionados y solo existe dato sintético en pruebas.

**Independent Test**: El árbol y el historial no contienen archivos con PII; un archivo nuevo en rutas sensibles no se rastrea.

- [ ] T043 [US5] Retirar del tracking `assets/exports/*.csv` y `assets/pdfs/*.pdf` mediante `git rm --cached`
- [ ] T044 [P] [US5] Añadir patrones a `.gitignore` para `assets/exports/`, `assets/pdfs/` y artefactos de base de datos locales, verificando que no afectan rutas legítimas
- [ ] T045 [US5] Trasladar las copias operativas necesarias a almacenamiento controlado fuera del repositorio y documentar el destino en `docs/security/INVENTARIO_REMEDIACION_074.md` (FR-010)
- [ ] T046 [P] [US5] Documentar la política de datos sintéticos/anonimizados y ajustar los fixtures de prueba para no usar datos reales (FR-012)
- [ ] T047 [US5] Verificar ausencia de PII en árbol e historial y registrar evidencia (SC-006; depende de T033/T034)

**Checkpoint**: No queda información personal real versionada en ninguna versión.

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Cierre, documentación y verificación final.

- [ ] T048 [P] Actualizar la documentación operativa (README y guías de despliegue) con variables por nombre y ejemplos enmascarados (FR-006)
- [ ] T049 [P] Ejecutar los gates locales de calidad: `python check_syntax.py`, `mypy`, `ruff`, `black --check` y `pytest`
- [ ] T050 Ejecutar los 7 escenarios de `specs/074-remediacion-secretos-hardcodeados/quickstart.md` y registrar los resultados en el inventario (SC-008)
- [ ] T051 Cerrar formalmente `specs/066-security-hardening-remediation/` actualizando su estado cuando el inventario esté en cero (FR-017)
- [ ] T052 Verificar SC-001…SC-011 en `docs/security/INVENTARIO_REMEDIACION_074.md` y crear el commit convencional `fix(security): remediar credenciales expuestas y purgar historial`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: sin dependencias; puede empezar de inmediato.
- **Foundational (Phase 2)**: depende de Setup; **bloquea** todas las historias.
- **US-01 (Phase 3, P1)**: tras Foundational; sin dependencias de otras historias.
- **US-02 (Phase 4, P1)**: tras Foundational; independiente, pero debe completarse **antes** de la purga (US-03) para no reintroducir valores en commits nuevos.
- **US-03 (Phase 5, P2)**: depende de T043 (US-05, retiro del árbol) y de US-02; operación destructiva coordinada.
- **US-04 (Phase 6, P2)**: independiente; T039 (check requerido) debe habilitarse **después** de US-02 para no bloquear trabajo con hallazgos legítimos.
- **US-05 (Phase 7, P3)**: T043–T046 pueden ejecutarse antes de US-03; T047 depende de T033/T034.
- **Polish (Phase 8)**: depende de todas las historias deseadas.

### User Story Dependencies

- **US-01 (P1)**: sin dependencias entre historias.
- **US-02 (P1)**: sin dependencias entre historias.
- **US-03 (P2)**: requiere US-02 completo y T043; integra el retiro de PII en el historial.
- **US-04 (P2)**: sin dependencias; su prueba de reintroducción asume el gate configurado.
- **US-05 (P3)**: independiente para el árbol; su verificación histórica depende de US-03.

### Within Each User Story

- Documentación/estructura antes de la acción destructiva (p. ej., T009 antes de T011–T013; T029–T031 antes de T032–T033).
- Implementación antes de verificación y evidencia.
- Registrar evidencia inmediatamente al completar cada verificación.

### Parallel Opportunities

- Setup: T002, T003 y T004 en paralelo.
- Foundational: T006 y T007 en paralelo.
- US-02: T019–T026 en paralelo (archivos distintos); T020–T026 por lotes de directorio.
- US-01: T010–T013 en paralelo (sistemas distintos).
- US-05: T044 y T046 en paralelo.

---

## Parallel Example: User Story 2

```text
# Lote A (código y configuración):
T019 tests/unit/test_settings_credenciales.py
T020 config/*.py
T021 migraciones/*.py

# Lote B (documentación y pruebas):
T022 scripts/*.py
T023 migraciones/*.md|*.txt
T024 tests/** y playwright

# Lote C (referencias):
T025 scripts/diagnostico/*
T026 docs/** y specs/**
```

---

## Implementation Strategy

### MVP First (US-01 + US-02)

Ambas historias son P1. Para un MVP realista con valor inmediato:

1. Completar Phase 1 (Setup) y Phase 2 (Foundational).
2. Completar US-01 (rotación): detiene el riesgo activo de acceso a producción.
3. Completar US-02 (eliminación en árbol): corta la fuente de la fuga.
4. **STOP and VALIDATE**: ejecutar los escenarios 1, 2 y 7 de `quickstart.md`.

### Incremental Delivery

1. US-01 → validar rechazo de credenciales antiguas y continuidad (MVP de seguridad).
2. US-02 → validar cero literales y fail-fast.
3. US-05 (árbol) → US-03 (historial) → validar clon nuevo sin PII ni secretos.
4. US-04 → validar detección, bloqueo de fusión y prueba de reintroducción.
5. Polish → cierre de 066 y evidencia final.

### Parallel Team Strategy

- Persona A: US-01 (operación) + US-03 (purga coordinada).
- Persona B: US-02 (código/documentación) + US-05 (datos).
- Persona C: US-04 (CI/escáner) + ADR y verificación.

---

## Notes

- [P] = archivos distintos, sin dependencias pendientes.
- Los literales comprometidos no se escriben en ningún artefacto de esta iniciativa (ni en tareas, notas o evidencia).
- `image.png` (eliminado en el working tree) y el `gitleaks.toml` local no forman parte de los commits de esta iniciativa salvo lo indicado en T037.
- Commit después de cada tarea o grupo lógico, con mensajes convencionales `fix(security)` / `chore(security)`.
- Detener el avance ante cualquier desviación en la verificación (Constitución §13, Stop-the-line).
