# Tasks: Grupo de pago correcto y atómico en la renovación de contratos

**Input**: Design documents from `/specs/075-fix-grupo-pago-renovacion/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/, quickstart.md

**Tests**: Incluidos — exigidos por la constitución §5 y por los criterios SC-003 (rollback verificable), SC-004 (cero regresiones) y SC-005 (limpieza verificable de datos TEST); además el plan define archivos de prueba explícitos.

**Organization**: Tareas agrupadas por historia de usuario (US1–US4) para implementación y prueba independientes.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Puede ejecutarse en paralelo (archivo distinto, sin dependencias pendientes)
- **[Story]**: Historia de usuario a la que pertenece (US1, US2, US3, US4)
- Rutas de archivo exactas en cada descripción

## Path Conventions

- Proyecto único: `src/`, `tests/`, `scripts/` en la raíz del repositorio (ver plan.md §Project Structure)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Verificar criterios de entrada antes de tocar código

- [X] T001 [P] Ejecutar baseline de calidad: `python scripts/check_syntax.py` y `python -m pytest tests/unit -q`; registrar resultado en verde como criterio de entrada (SC-004)
- [X] T002 [P] Verificar disponibilidad de base de pruebas (`DATABASE_URL`) y la guarda de omisión de integración en `tests/integration/conftest.py`; documentar entorno de la corrida

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Regla única de dominio que bloquea US1 y US2

**⚠️ CRITICAL**: Ninguna historia puede iniciarse hasta completar esta fase

- [X] T003 [P] Crear tests unitarios (en rojo) de la regla unificada V2 en `tests/unit/test_grupo_pago_reglas.py` — bordes 7/8, 17/18, 27/28, 1, 31 y tabla de verdad (Spec §FR-001..FR-003, contracts/contratos-dominio.md)
- [X] T004 Implementar `calcular_grupo_operativo` + constantes de tramo y delegación de `calcular_ciclo_pago_mandato` en `src/dominio/servicios/calculadora_contratos.py` (depende de T003)

**Checkpoint**: Regla única disponible y probada; US1 y US2 pueden comenzar

---

## Phase 3: User Story 1 - Renovación con grupo de pago correcto (Priority: P1) 🎯 MVP

**Goal**: Al renovar un arrendamiento o mandato, el grupo y día de pago corresponden a la fecha efectiva del nuevo período y quedan persistidos; el mandato asociado adopta el período renovado.

**Independent Test**: Renovar un arrendamiento y un mandato activos y verificar en BD `GRUPO_OPERATIVO`/`FECHA_PAGO` del nuevo período, la sincronía del mandato y que el arriendo no se degrada a 0.

### Tests for User Story 1 ⚠️

- [X] T005 [P] [US1] Crear test unitario (en rojo) del mapeo `GRUPO_OPERATIVO` en `tests/unit/test_arriendo_repo_grupo_pago.py` (Spec §FR-007)
- [X] T006 [P] [US1] Crear tests unitarios (en rojo, con mocks) del recálculo en renovación de arriendo y mandato en `tests/unit/test_renovacion_grupo_pago.py` (Spec §FR-004, §FR-005, §FR-006)

### Implementation for User Story 1

- [X] T007 [US1] Mapear `grupo_operativo` en `_row_to_entity` de `src/infraestructura/persistencia/repositorio_contrato_arrendamiento_postgres.py` (depende de T005)
- [X] T008 [US1] Unificar grupo en creación y edición de arriendo con `calcular_grupo_operativo` (día exacto para `fecha_pago`) en `src/aplicacion/servicios/servicio_contrato_arrendamiento.py` (Spec §FR-003)
- [X] T009 [US1] Recalcular `grupo_operativo`/`fecha_pago` en `_ejecutar_renovacion_arrendamiento` y sincronizar el mandato activo adoptando el período renovado en `src/aplicacion/servicios/servicio_contrato_arrendamiento.py` (Spec §FR-004, §FR-005)
- [X] T010 [P] [US1] Extraer `_ejecutar_renovacion_mandato`, recalcular grupo/día y envolver `renovar_mandato` en `db.transaccion()` con invalidación de caché post-commit en `src/aplicacion/servicios/servicio_contrato_mandato.py` (Spec §FR-006, §FR-012)
- [X] T011 [US1] Crear test de integración de persistencia del grupo tras renovar arriendo y mandato en `tests/integration/test_renovacion_grupo_pago_atomico.py` (depende de T007..T010)
- [X] T012 [US1] Ejecutar y dejar en verde las pruebas de US1 (T005, T006, T011) y los tests existentes de renovación (`tests/unit/test_renovacion_ipc.py`, `tests/unit/test_arriendo_sincronizacion.py`)

**Checkpoint**: US1 funcional y verificable de forma independiente (MVP)

---

## Phase 4: User Story 2 - Auditoría y remediación integral (Priority: P1)

**Goal**: Auditar todos los contratos ACTIVOS (mandatos y arrendamientos) y remediar atómicamente los grupos incorrectos, con reporte antes/después e idempotencia.

**Independent Test**: Ejecutar el script en solo lectura (reporte de discrepancias), luego con `--commit`, y una tercera corrida que reporte 0 discrepancias sin tocar historia.

### Tests for User Story 2 ⚠️

- [X] T013 [US2] Crear test de integración (en rojo) de auditoría/remediación en `tests/integration/test_auditoria_grupos_pago.py` (Spec §FR-009, §FR-010), incluidos el caso de herencia (mandato sin renovaciones propias con arriendo renovado, Spec §FR-001, §Edge Cases) y el caso de concurrencia (fila modificada durante la remediación se omite y se reporta, Spec §FR-010, §Edge Cases)

### Implementation for User Story 2

- [X] T014 [US2] Implementar auditoría solo-lectura en `scripts/remediacion/remediar_grupos_pago_v4.py`: extracción masiva con última renovación determinista e herencia de período (R2/R7), cálculo esperado con `CalculadoraContratos`, reporte por consola y CSV en `outputs/` (Spec §FR-009, contracts/cli-remediacion.md)
- [X] T015 [US2] Implementar `--commit` con transacción única, actualización solo de discrepancias reales, compare-and-set (omitir y reportar filas modificadas concurrentemente) y códigos de salida 0/1/2 en `scripts/remediacion/remediar_grupos_pago_v4.py` (Spec §FR-010, contracts/cli-remediacion.md §Comportamiento/§Códigos de salida)
- [X] T016 [US2] Añadir bloque de verificación de huérfanos de TEST (contratos, propiedades, liquidaciones, recaudos, renovaciones, personas = 0) en `tests/integration/test_auditoria_grupos_pago.py` (Spec §FR-013, §SC-005)
- [X] T017 [US2] Ejecutar dry-run → `--commit` → dry-run sobre la base de pruebas y registrar 0 discrepancias, incluidas las filas omitidas por concurrencia si las hubiera (Spec §SC-002)

**Checkpoint**: US1 y US2 funcionan de forma independiente

---

## Phase 5: User Story 3 - Atomicidad y rollback (Priority: P2)

**Goal**: Un fallo en cualquier paso revierte el 100% de la renovación (incluido el grupo), el reintento es seguro y el usuario recibe un mensaje operativo.

**Independent Test**: Inducir un fallo posterior al cálculo del grupo, verificar ausencia total de cambios parciales y reintentar con éxito sin duplicados.

### Tests for User Story 3 ⚠️

- [X] T018 [US3] Crear test de integración (en rojo) de fallo inducido → cero estado parcial y reintento idempotente en `tests/integration/test_renovacion_grupo_pago_atomico.py` (Spec §FR-008, §SC-003)
- [X] T019 [P] [US3] Crear test unitario (en rojo) que verifica que `renovar_mandato` abre transacción gestionada en `tests/unit/test_renovacion_grupo_pago.py` (Spec §FR-008)

### Implementation for User Story 3

- [X] T020 [US3] Alinear el mensaje operativo de rollback ("no se aplicó ningún cambio; es seguro reintentar", sin errores crudos) en `src/presentacion_reflex/state/contratos_state.py` (`execute_renewal`) (Spec §FR-008)
- [ ] T021 [US3] Ejecutar y dejar en verde la suite de atomicidad/concurrencia: T018, T019, `tests/integration/test_renovacion_atomicidad.py`, `tests/integration/test_renovacion_concurrencia.py`

**Checkpoint**: Atomicidad verificada en arriendo y mandato

---

## Phase 6: User Story 4 - Sin regresiones en módulos dependientes (Priority: P3)

**Goal**: Contratos, Liquidaciones de Propietarios, Recaudos y sus filtros siguen funcionando; cero regresiones.

**Independent Test**: Ejecutar las suites existentes de los tres módulos y validar en runtime el filtro por ciclo operativo/día de pago.

- [ ] T022 [US4] Ejecutar las suites existentes de Contratos, Liquidaciones y Recaudos (`python -m pytest tests/unit tests/integration -q`) y registrar 100% verde (Spec §SC-004)
- [ ] T023 [US4] Validar en runtime (quickstart §4) el badge de grupo y los filtros por ciclo operativo/día de pago en Liquidaciones y Recaudos; criterio de aceptación: 0 fallos en las suites y resultados conformes del quickstart §4; corregir las regresiones en los archivos implicados (Spec §FR-011)

**Checkpoint**: Todas las historias funcionales y sin regresiones

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Calidad, evidencia y validación final

- [X] T024 [P] Ejecutar `python scripts/check_syntax.py`, `mypy`, `ruff` y `black` sobre los archivos modificados; medir la cobertura de la lógica nueva con `pytest-cov` y registrar el resultado; corregir hallazgos (constitución §5)
- [X] T025 [P] Ejecutar las verificaciones de limpieza de datos TEST del quickstart §6 y registrar la evidencia (Spec §FR-013, §SC-005)
- [ ] T026 Ejecutar la validación end-to-end del quickstart (secciones 1–3, 5 y 7, incluido el baseline de SC-006 y su seguimiento a 30 días) y registrar resultados; actualizar documentos de la feature si hubo desviaciones (Spec §SC-006)
- [X] T027 [P] Añadir pruebas unitarias de las funciones puras del script (resolución de fecha efectiva y cálculo de discrepancias) en `tests/unit/test_remediacion_grupos_pago.py` (constitución §5, Spec §FR-009, §FR-010)
- [X] T028 [P] Aplicar la migración del trigger `fn_sync_fechas_mandato` a la regla V2 en producción (`CREATE OR REPLACE FUNCTION`, sin esquema ni downtime), verificar el cuerpo y el comportamiento con transacción ROLLBACK, y re-auditar 0 discrepancias (causa raíz de recurrencia, Spec §FR-002)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: sin dependencias
- **Foundational (Phase 2)**: depende de Setup — BLOQUEA US1 y US2
- **US1 (Phase 3)**: depende de Foundational
- **US2 (Phase 4)**: depende de Foundational; independiente de US1
- **US3 (Phase 5)**: depende de US1 (transacción de mandato) y Foundational
- **US4 (Phase 6)**: depende de US1–US3
- **Polish (Phase 7)**: depende de todas las historias

### User Story Dependencies

- **US1 (P1)**: sin dependencias de otras historias — MVP
- **US2 (P1)**: puede ejecutarse en paralelo con US1 tras Foundational
- **US3 (P2)**: requiere US1 (T010) para la transacción de mandato
- **US4 (P3)**: requiere US1–US3 para que las suites reflejen el estado final

### Within Each User Story

- Tests en rojo antes de implementar (TDD declarado en la constitución §5)
- Mapeo de persistencia y dominio antes que servicios; servicios antes que UI
- Historia completa antes de pasar a la siguiente prioridad

### Parallel Opportunities

- Setup: T001 ∥ T002
- Foundational: T003 (test) y en paralelo nada más (T004 depende de T003)
- US1: T005 ∥ T006; T010 ∥ T008–T009 (archivos distintos)
- US2: T013 ∥ T014 (test e implementación en archivos distintos)
- US3: T019 ∥ T018 (archivos distintos)
- Polish: T024 ∥ T025 ∥ T027

---

## Parallel Example: User Story 1

```bash
# Tests en paralelo (archivos distintos):
Task: "Crear test unitario del mapeo GRUPO_OPERATIVO en tests/unit/test_arriendo_repo_grupo_pago.py"
Task: "Crear tests unitarios del recálculo en renovación en tests/unit/test_renovacion_grupo_pago.py"

# Implementaciones en paralelo (servicios distintos):
Task: "Recalcular grupo/día en renovación de arriendo en src/aplicacion/servicios/servicio_contrato_arrendamiento.py"
Task: "Transacción + recálculo en renovación de mandato en src/aplicacion/servicios/servicio_contrato_mandato.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Completar Phase 1: Setup
2. Completar Phase 2: Foundational (CRÍTICO)
3. Completar Phase 3: US1
4. **DETENERSE y VALIDAR**: probar US1 de forma independiente (T012)
5. Desplegar/demostrar si está listo

### Incremental Delivery

1. Setup + Foundational → base lista
2. US1 → validar → MVP (el defecto reportado deja de ocurrir)
3. US2 → dry-run/commit de remediación → activos históricos alineados
4. US3 → atomicidad y rollback verificados
5. US4 → regresión en módulos dependientes
6. Polish → evidencia de calidad y limpieza de TEST

### Parallel Team Strategy

1. Equipo completo: Setup + Foundational
2. Tras Foundational:
   - Dev A: US1 (MVP)
   - Dev B: US2 (script de auditoría/remediación)
3. US1 completo → Dev C puede iniciar US3 (depende de la transacción de mandato)
4. US4 y Polish cierran en secuencia

---

## Notes

- [P] = archivos distintos, sin dependencias pendientes
- Todo dato TEST creado debe eliminarse al finalizar (T016, T025) — condición obligatoria del spec
- No se modifica esquema ni historia financiera cerrada; solo `GRUPO_OPERATIVO` y `FECHA_PAGO` de contratos ACTIVOS
- No ejecutar la remediación con `--commit` contra producción sin revisar antes el reporte dry-run
- Evitar tareas vagas; cada tarea escribe en un archivo exacto y es verificable
