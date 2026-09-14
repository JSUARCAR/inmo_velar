# Tareas: Renovación de Contratos (Debug de casting de fechas)

**Input**: Documentos de diseño de `/specs/072-renovacion-contratos-debug/`

**Prerequisitos**: plan.md, spec.md, research.md, data-model.md, contracts/servicio-renovacion.md, quickstart.md

**Tests**: Incluidos — exigidos explícitamente en spec (SC-001: 7 casos + atomicidad; SC-003: suite completa 100% verde; SC-004: verificación PDF; FR-010: canon de propiedad) y constitución §5 (cobertura dominio 100%, aplicación >90%).

**Organización**: Tareas agrupadas por historia de usuario (US1 P1, US2 P2, US3 P2) de spec.md

## Formato: `[ID] [P?] [Story] Descripción`

- **[P]**: Puede ejecutarse en paralelo (archivos distintos, sin dependencias)
- **[Story]**: Qué historia de usuario cubre (US1, US2, US3)
- Incluir rutas de archivo exactas en las descripciones

---

## Fase 1: Setup (Infraestructura compartida del fix)

**Propósito**: Corregir causas raíz e infraestructura compartida que bloquean TODAS las historias de usuario

⚠️ **CRÍTICO**: Ningún trabajo de historia de usuario puede comenzar hasta que esta fase esté completa

- [x] T001 [P] Añadir la clase de excepción `ContratoNoRenovableError` heredando de la base de dominio en `src/dominio/excepciones.py` según constitución §2.2 [D5, FR-008]
- [x] T002 [P] Crear el helper `_calcular_incremento_ipc(contrato, ipc_actual)`: retorna `valor_ipc` (como decimal) cuando `duracion_contrato_a >= 12` meses Y existe IPC vigente; si no, `0.0` en `src/aplicacion/servicios/servicio_contrato_arrendamiento.py` [D3]
- [x] T003 Corregir el cast seguro NULLIF en TODAS las queries de propagación (Q1–Q6): reemplazar cada `campo::date` / comparación `campo::date > %s` por `NULLIF(campo,'')::date >= date_trunc('month', %s::date)` en `actualizar_canon_liquidaciones_futuras`, `actualizar_valor_recaudos_futuros` y todas las queries de verificación/integridad en `src/aplicacion/servicios/servicio_contrato_arrendamiento.py` [D1, FR-007]
- [x] T004 [P] Añadir el método estático `calcular_fecha_inicio_renovacion(fecha_fin_original)` en `CalculadoraContratos` (`src/dominio/servicios/calculadora_contratos.py`): parsear `fecha_fin_original[:10]`, retornar `(fecha + timedelta(days=1)).isoformat()` según FR-001 (spec `fecha_fin_original + 1 día`, quickstart E5: 2026-12-31 → 2027-01-01). Fuente única de verdad; NO usar `sumar_meses` para este campo (CHK006) [D2, FR-001]
- [x] T005 Poblar `fecha_inicio_renovacion = CalculadoraContratos.calcular_fecha_inicio_renovacion(fecha_fin_original)` (reemplazando el actual `sumar_meses(fecha_fin_original, 1)` — matemática de meses calendario incorrecta) en la construcción de `RenovacionContrato(...)` en la línea 443 de `src/aplicacion/servicios/servicio_contrato_arrendamiento.py` [D2, FR-001]
- [x] T006 [P] Poblar `fecha_inicio_renovacion = CalculadoraContratos.calcular_fecha_inicio_renovacion(fecha_fin_original)` (mismo fix CHK006 que T005) en la construcción de `RenovacionContrato(...)` en la línea 266 de `src/aplicacion/servicios/servicio_contrato_mandato.py` [D2, FR-001]

**Checkpoint**: Causas raíz corregidas — queries de propagación seguras con NULLIF, `fecha_inicio_renovacion` poblado vía helper `+1 día` en ambos servicios, excepción tipada lista, helper IPC creado. Puede iniciar la implementación de histórias de usuario.

---

## Fase 2: Historia de Usuario 1 — Renovación Normal de Contrato (Prioridad: P1) 🎯 MVP

**Objetivo**: Renovación única completa y correcta con cálculo IPC, propagación a LIQUIDACIONES/RECAUDOS, auditoría solo de filas modificadas, invalidación de caché post-commit, excepción tipada, soporte multi-mandato, verificación de contenido PDF y canon de propiedad actualizado

**Test independiente**: E1 + E2 + E3 + E6 + E7 + E8 + E9 + E10 de `quickstart.md` pasan, más la verificación PDF SC-004 (T010) y el test de canon de propiedad FR-010 (T011)

### Tests de la Historia de Usuario 1

- [x] T007 [P] [US1] Tests unitarios de `_calcular_incremento_ipc`: 7 casos (≥12mo+IPC, <12mo, sin IPC, renovación consecutiva, 31-Dic, 28-Feb bisiesto, sin mandato) en `tests/unit/test_renovacion_ipc.py`
- [x] T008 [P] [US1] Tests unitarios para el cast seguro NULLIF + manejo de fecha vacía (E8) + guard de auditoría solo de filas modificadas (E10) en `tests/unit/test_renovacion_nullif_auditoria.py`
- [x] T009 [P] [US1] Test de integración: flujo completo de renovación E1/E2/E3/E6/E7/E8/E9/E10 (IPC, propagación, auditoría, caché) en `tests/integration/test_renovacion_flujo_completo.py`
- [x] T010 [P] [US1] Test de integración SC-004 (CHK002): los datos del PDF regenerado reflejan el nuevo canon y las fechas corregidas — usar `pdf_state._get_datos_contrato`/el data builder de ServicioContratos usado para el documento y verificar que `canon_nuevo`/`fecha_inicio_renovacion` aparecen tras la renovación en `tests/integration/test_renovacion_pdf_verificacion.py`
- [x] T011 [P] [US1] Test de integración FR-010 (CHK004): tras la renovación de arrendamiento Y tras la renovación de mandato, `canon_arrendamiento_estimado` en `PROPIEDADES` es igual al canon nuevo (los servicios ya lo actualizan en `servicio_contrato_arrendamiento.py:468` / `servicio_contrato_mandato.py:291`) en `tests/integration/test_renovacion_canon_propiedad.py`
- [x] T012 [P] [US1] Test de integración: `ContratoNoRenovableError` se lanza para contrato inactivo/inexistente en `tests/integration/test_renovacion_errores.py`

### Implementación de la Historia de Usuario 1

- [x] T013 [US1] Integrar `ContratoNoRenovableError` (T001) en la validación de renovación y usar `_calcular_incremento_ipc` (T002) para la lógica IPC, reemplazando el código IPC inline en `src/aplicacion/servicios/servicio_contrato_arrendamiento.py`
- [x] T014 [US1] Implementar la query multi-mandato: `SELECT MAX(id_contrato_m) FROM CONTRATOS_MANDATOS WHERE id_contrato_a = %s AND estado = 'ACTIVO'` para sincronizar solo el mandato activo más reciente; continuar sin error si no existe ninguno en `src/aplicacion/servicios/servicio_contrato_arrendamiento.py` [FR-009]
- [x] T015 [US1] Guardar los inserts de `AUDITORIA_PROPAGACION_CANON`: insertar SOLO cuando `canon_nuevo != canon_anterior` Y la fila fue realmente modificada; omitir auditoría con incremento 0% o 0 filas afectadas en `src/aplicacion/servicios/servicio_contrato_arrendamiento.py` [FR-002]
- [x] T016 [US1] Añadir la invalidación de caché post-commit vía `cache_manager.invalidate_cache('cache_estado_cartera')` envuelta en try/except (log de advertencia ante fallo, nunca abortar/rollback) en `src/aplicacion/servicios/servicio_contrato_arrendamiento.py` Y en `src/aplicacion/servicios/servicio_contrato_mandato.py` [FR-012]
- [x] T017 [P] [US1] Añadir el decorador `@idempotent(key_prefix="mandato:renovar")` a `renovar_mandato` en `src/aplicacion/servicios/servicio_contrato_mandato.py` [FR-011]

**Checkpoint**: Historia de Usuario 1 completamente funcional y testeable de forma independiente — renovación con IPC, propagación, excepción tipada, auditoría, caché, multi-mandato, verificación de contenido PDF y canon de propiedad. Casos SC-001 E1–E10 + SC-004 + FR-010 pasan.

---

## Fase 3: Historia de Usuario 2 — Renovaciones Consecutivas (Prioridad: P2)

**Objetivo**: Verificar que las renovaciones consecutivas no generan duplicados; la idempotencia es efectiva entre sesiones/instancias

**Test independiente**: E4 de `quickstart.md` pasa — dos renovaciones consecutivas producen dos filas válidas, sin duplicados

### Tests de la Historia de Usuario 2

- [x] T018 [P] [US2] Test unitario: la clave de idempotencia previene filas duplicadas de `RENOVACIONES_CONTRATOS` para el mismo intento de renovación; verificar las transiciones de estado de `IDEMPOTENCY_KEYS` en `tests/unit/test_renovacion_idempotencia.py`
- [x] T019 [US2] Test de integración: flujo completo de renovación consecutiva E4 (renovar dos veces, verificar la cadena de canon) en `tests/integration/test_renovacion_consecutiva.py`

**Checkpoint**: Historia de Usuario 2 testeable de forma independiente — renovaciones consecutivas seguras, la idempotencia se mantiene

---

## Fase 4: Historia de Usuario 3 — Renovación con Fechas Límite (Prioridad: P2)

**Objetivo**: Verificar que `calcular_fecha_inicio_renovacion` (`+1 día`) y `sumar_meses` manejan correctamente los casos límite: bordes de fin de mes, años bisiestos

**Test independiente**: E5 de `quickstart.md` pasa — 31-Dic → 01-Ene, 28-Feb bisiesto → 29-Feb

### Tests de la Historia de Usuario 3

- [x] T020 [P] [US3] Tests unitarios para `calcular_fecha_inicio_renovacion` (`+1 día`) y casos límite de `sumar_meses`: 2026-12-31→2027-01-01, 2028-02-28 bisiesto→2028-02-29, 31-Ene→28/29-Feb, 30-Nov→31-Dic en `tests/unit/test_renovacion_fechas_limite.py`
- [x] T021 [US3] Test de integración: flujo completo de fechas límite E5 en `tests/integration/test_renovacion_fechas_limite.py`

**Checkpoint**: Historia de Usuario 3 testeable de forma independiente — fechas límite correctas

---

## Fase 5: Pulido y Aspectos Transversales

**Propósito**: Criterio de atomicidad, validación de concurrencia, regresión completa, validación de quickstart, gates de la constitución §5

- [x] T022 Test del criterio de atomicidad: inducir fallo a mitad de transacción (tras actualizar el contrato, antes de la propagación), verificar cero estado parcial en BD (sin filas de auditoría, sin log), reintentar la misma `idempotency_key` se completa exitosamente sin filas duplicadas de `RENOVACIONES_CONTRATOS` (atomicidad SC-001) en `tests/integration/test_renovacion_atomicidad.py`
- [x] T023 Test de concurrencia: dos renovaciones concurrentes (o renovación + escrituras en RECAUDOS/LIQUIDACIONES) sobre el mismo contrato no causan deadlock en PostgreSQL; la transacción se completa o revierte limpiamente (CHK032) en `tests/integration/test_renovacion_concurrencia.py`
- [x] T024 Ejecutar la suite completa de regresión SC-003: `pytest tests/unit tests/integration` con el filtro del quickstart `-k "renovacion or liquidaciones or recaudos or contrato"` — **61 passed, 0 failed** (re-verificado tras el fix de `renovar_mandato`). Fix aplicado en `test_sincronizacion_contratos.py` (`cm.propiedad_id` → `cm.id_propiedad`, columna real inequívoca consultada en information_schema). Nota de discrepancia: `tests/contract` no existe en el repo; el baseline completo `tests/unit tests/integration` arroja 10 fallos preexistentes (financiero ×4, personas ×1, propiedades ×5) causados por un fixture SQLite sin columna `eliminada` y datos de staging, confirmados como no-regresión vía `git stash`/worktree HEAD y ajenos a esta feature.
- [x] T025 Ejecutar la validación de quickstart.md de extremo a extremo: verificar que los 12 escenarios E1–E12 pasan
- [x] T026 Ejecutar los gates de build de la constitución §5 (CHK027): `check_syntax.py`, `mypy`, `ruff`, `black --check`, render/export Reflex (`reflex export --frontend-only --no-zip`) y cobertura `pytest --cov=src/dominio --cov=src/aplicacion` (dominio 100%, aplicación >90%) — todo debe pasar
  - **Resultados**: (1) Sintaxis: `check_syntax.py` no existe en el repo; equivalente `python -m compileall src` → PASS (exit 0). (2) mypy: PASS vs baseline — 132 errores únicos preexistentes en HEAD (worktree temporal), 0 nuevos tras la feature; se corrigió 1 error nuevo introducido (asignación invertida `mandato.canon_mandato = propiedad.canon_arrendamiento_estimado` → restaurada a `propiedad.canon_arrendamiento_estimado = mandato.canon_mandato`, FR-010). (3) ruff: PASS en los 7 archivos de la feature (251 errores preexistentes repo-wide sin config de ruff). (4) black --check: FAIL preexistente — 74/410 archivos de `src` serían reformateados (los 4 de la feature ya fallaban en HEAD); repo nunca fue black-formateado, no se reformatea para evitar diff masivo ajeno a la feature. (5) reflex export --frontend-only --no-zip: PASS (exit 0, solo warnings de iconos/var_state). (6) Cobertura: dominio 64.86% (2453 stmts), aplicación 30.78% (4893 stmts) — brecha 100%/>90% enteramente preexistente del código legacy; el código de la feature está cubierto por 47 tests verdes (SC-001 E1–E12, CHK032, SC-003). SC-003 post-fix: 61 passed, 0 failed.

---

## Dependencias y Orden de Ejecución

### Dependencias de Fase

- **Fase 1 (Setup)**: Sin dependencias — comienza de inmediato; BLOQUEA todas las historias de usuario (T005/T006 dependen de T004)
- **Fase 2 (US1)**: Depende de la Fase 1 — BLOQUEA las Fases 3 y 4
- **Fase 3 (US2)**: Depende de la Fase 2 — puede correr en paralelo con la Fase 4
- **Fase 4 (US3)**: Depende de la Fase 2 — puede correr en paralelo con la Fase 3
- **Fase 5 (Pulido)**: Depende de las Fases 2 + 3 + 4

### Dependencias de Historias de Usuario

- **US1 (P1)**: Inicia tras la Fase 1 — sin dependencias de otras historias (MVP)
- **US2 (P2)**: Inicia tras la Fase 2 (US1) — prueba la idempotencia sobre el flujo ya funcionando
- **US3 (P2)**: Inicia tras la Fase 2 (US1) — prueba las fechas límite sobre el flujo ya funcionando

### Dentro de Cada Fase

- Tests (si existen) se escriben primero y se validan como FALLIDOS antes de implementar (TDD según constitución §5)
- Tareas de implementación secuenciales dentro del mismo archivo para evitar conflictos
- Tareas en archivos distintos marcadas [P] corren en paralelo

### Oportunidades de Paralelismo

**Fase 1 (Setup):**
```
T001 [P] src/dominio/excepciones.py            ←─── puede correr con T002, T004
T002 [P] src/aplicacion/servicios/servicio_contrato_arrendamiento.py (helper IPC)
T004 [P] src/dominio/servicios/calculadora_contratos.py (helper +1 día)
T005 / T006: dependen de T004 — secuenciales dentro del mismo archivo
```

**Fase 2 (US1):**
```
T007 [P] tests/unit/test_renovacion_ipc.py            ←─── tests, independientes
T008 [P] tests/unit/test_renovacion_nullif_auditoria.py  ←─── tests, independientes
T009 [P] tests/integration/test_renovacion_flujo_completo.py  ←─── tests, independientes
T010 [P] tests/integration/test_renovacion_pdf_verificacion.py  ←─── SC-004
T011 [P] tests/integration/test_renovacion_canon_propiedad.py  ←─── FR-010
T012 [P] tests/integration/test_renovacion_errores.py  ←─── tests, independientes
T017 [P] src/aplicacion/servicios/servicio_contrato_mandato.py ←─── @idempotent, archivo independiente
```

**Fases 3 + 4 (tras completar US1):**
```
Fase 3: T018 [P] + T019  ←─── US2, independiente de US3
Fase 4: T020 [P] + T021  ←─── US3, independiente de US2
```

---

## Estrategia de Implementación

### MVP Primero (solo Fases 1 + 2)

1. Completar la Fase 1: causas raíz corregidas (T001–T006)
2. Completar la Fase 2: US1 completamente funcional (T007–T017)
3. **DETENER y VALIDAR**: Ejecutar E1+E2+E3+E6+E7+E8+E9+E10 + SC-004 (T010) + FR-010 (T011) — todo debe pasar
4. Desplegar/demo si está listo

### Entrega Incremental

1. Fase 1 → Fundación lista (NULLIF, helper +1 día, excepción, helper IPC)
2. Fase 2 → MVP US1 (renovación normal) → validar → desplegar/demo
3. Fases 3+4 → US2+US3 (consecutivas + fechas límite) → validar → desplegar/demo
4. Fase 5 → Pulido (atomicidad, concurrencia, regresión, quickstart, gates §5) → validación final

### Estrategia de Equipo en Paralelo

Con múltiples desarrolladores:

1. Desarrollador A: Fase 1 (T001–T006) → luego Fase 2 (T007–T017)
2. Desarrollador B (tras US1): Fase 3 (US2: T018–T019)
3. Desarrollador C (tras US1): Fase 4 (US3: T020–T021)
4. Fase 5: todos los desarrolladores validan juntos

---

## Notas

- Tareas [P] = archivos distintos, sin dependencias de tareas secuenciales de la misma fase
- La etiqueta [Story] mapea la tarea a la historia de usuario para trazabilidad
- Cada historia de usuario es completable y testeable de forma independiente tras la Fase 2 (MVP)
- Commit tras cada tarea o grupo lógico
- Detenerse en cualquier checkpoint para validar la historia de forma independiente
- Constitución §5: tests dominio 100%, aplicación >90% — no negociable
- Constitución §2.2: ContratoNoRenovableError debe ser de dominio tipado, nunca ValueError
- `fecha_inicio_renovacion` = `fecha_fin_original + 1 día` (spec FR-001, quickstart E5); `sumar_meses` aplica SOLO a `fecha_fin_renovacion` (CHK006)
- Rama: working tree (sin rama dedicada especificada por setup-tasks.ps1)

---

## Completion Report — 072-renovacion-contratos-debug

**Estado**: 31/31 tareas `[x]` (T001–T026 + Fase 6: T027–T031). Feature completa y verificada.

### Causas raíz corregidas
1. `ValueError`/`invalid input syntax for type date` por fechas vacías `""::date` → cast seguro `NULLIF(campo,'')::date` en las 6 queries de propagación (FR-007).
2. `fecha_inicio_renovacion` vacía/incorrecta → helper `calcular_fecha_inicio_renovacion` = fin original + 1 día (FR-001).
3. Bordes de fecha (31-Dic, 28/29-Feb, fin-de-mes→fin-de-mes) → `sumar_meses` como fuente única de verdad (FR-003, E5).
4. IPC condicional: aplica solo si `duracion >= 12` y existe IPC vigente; si no, 0% (FR-004).
5. `ValueError` genérico → `ContratoNoRenovableError` tipado de dominio (FR-008, constitución §2.2).

### Capacidad añadida
- Renovación atómica en transacción única con idempotencia (`IDEMPOTENCY_KEYS`, decorador `@idempotent` en `renovar_arrendamiento` y `renovar_mandato`, FR-011); fallo a mitad → rollback total, reintento con misma key completa sin duplicados (SC-001/E11).
- Propagación de canon a mandato activo más reciente (FR-009), canon estimado de propiedad (FR-010), liquidaciones/recaudos futuros con auditoría solo de filas realmente modificadas (FR-002).
- Invalidación de caché post-commit no bloqueante (FR-012).
- Concurrencia sin deadlocks validada (CHK032/E12).

### Evidencia de validación
- SC-001: E1–E12 cubiertos por 55 tests de renovación (47 base + 8 de Fase 6), todos verdes.
- SC-003: suite de regresión (quickstart) **69 passed, 0 failed** (61 en T024 + 8 de Fase 6).
- Gates T026: compileall PASS · mypy 0 errores nuevos (132 baseline) · ruff PASS en archivos feature · reflex export PASS (exit 0) · black y cobertura con brechas 100% preexistentes documentadas en T026.

### Bugs extra detectados y corregidos durante Fase 5
- `bloquear` de idempotencia no re-adquiría keys en estado `failed` → reintento tras fallo hacía polling hasta timeout. Fix: `ON CONFLICT (KEY) DO UPDATE ... WHERE ESTADO='failed'`.
- `renovar_arrendamiento` sin `**kwargs` → TypeError al inyectar `_idempotency_full_key`. Fix: acepta `**kwargs`.
- `logger` undefined en `_invalidar_cache_estado_cartera` (F821, NameError latente). Fix: logger a nivel de módulo.
- Asignación invertida en `renovar_mandato` paso 5 (`mandato.canon_mandato = propiedad...` en vez de `propiedad.canon_arrendamiento_estimado = mandato.canon_mandato`, FR-010). Fix: dirección restaurada.
- Test preexistente `test_cascada_renovacion_canon` usaba columna inexistente `cm.propiedad_id`. Fix: `cm.id_propiedad`.

### Deuda conocida (fuera de alcance, preexistente)
- 10 fallos en suite completa `tests/unit tests/integration` (financiero ×4, personas ×1, propiedades ×5): fixture SQLite sin columna `eliminada` y datos de staging.
- black --check: 74/410 archivos de `src` sin formatear (repo nunca fue black-formateado).
- Cobertura paquetes: dominio 64.86%, aplicación 30.78% vs umbrales constitución (100%/>90%) — brecha legacy.

### Phase 6 (Convergence) — completada 2026-09-13
- T027: scripts huérfanos `fix_*.py` reubicados a `scripts/diagnostico/` (§4).
- T028: documentación dinámica creada/actualizada: `CLAUDE.md` (hito 072, v1.0.2), `ESTADO_TAREAS.md` y `auditoria_GEMINI_CLI.md` nuevos (§5).
- T029: 4 tests de la rama de truncado de `sumar_meses` (`except ValueError`) — dominio nuevo al 100% en las funciones de la feature (L212-213 ya cubierta; verificado con `--cov-report=term-missing`).
- T030: 4 tests FR-012 (`tests/unit/test_renovacion_cache_fr012.py`): orden inicio→commit→invalidación en arrendamiento y tolerancia a fallo de caché en ambos flujos.
- T031: desviaciones de gates (black y cobertura legacy) formalmente justificadas en `plan.md` §Complexity Tracking.
- **Validación final**: suite SC-003 → **69 passed, 0 failed** (61 + 8 tests nuevos).

---

## Phase 6: Convergence

- [x] T027 CRITICAL: Reubicar los scripts de diagnóstico huérfanos de la raíz (`fix_export.py`, `fix_mixin.py`, `fix_mixin2.py`, `fix_personas.py`) a `scripts/diagnostico/` o eliminarlos si ya no son necesarios, restaurando la higiene de raíz per Constitución §4 (contradicts)
- [x] T028 CRITICAL: Actualizar la documentación dinámica tras el hito 072: registrar la finalización de la feature en `CLAUDE.md` y crear/actualizar `ESTADO_TAREAS.md` y `auditoria_GEMINI_CLI.md` per Constitución §5 (missing)
- [x] T029 CRITICAL: Añadir test unitario de la rama de truncado de `sumar_meses` (L212-213 de `src/dominio/servicios/calculadora_contratos.py`: origen NO fin-de-mes con día inválido en mes destino, ej. 2026-01-30 +1 → 2026-02-28 y 2028-01-30 +1 → 2028-02-29) para alcanzar 100% de cobertura del código de dominio nuevo per Constitución §5 / T020 (partial)
- [x] T030 Añadir test que verifique FR-012: `invalidate_cache('cache_estado_cartera')` se invoca tras el commit exitoso de la renovación (arrendamiento y mandato) y su fallo NO aborta ni revierte la transacción (no-bloqueante), validando el paso 3 de quickstart E12 en `tests/unit/test_renovacion_cache_fr012.py` (partial)
- [x] T031 Resolver la desviación del gate `black --check` en los archivos tocados por la feature: ejecutar `black` sobre los 4 archivos que fallan (diff de solo formato) o registrar la justificación formal de la desviación en `plan.md` §Complexity Tracking per Constitución §5 (partial)
