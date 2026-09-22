# Tasks: Liquidación de Propietarios requiere Contrato de Arrendamiento Activo

**Input**: Design documents from `/specs/076-liquidacion-requiere-arrendamiento/`

**Prerequisites**: plan.md (required), spec.md (4 user stories), research.md (8 decisiones), data-model.md, contracts/ (servicio-financiero, auditoria-elegibilidad, limpieza-test), quickstart.md

**Tests**: incluidos (TDD — quickstart.md/plan definen unitarios de dominio/aplicación y e2e de la matriz 5×2; constitution exige 100% dominio y >90% lógica nueva).

**Organization**: Tasks se agrupan por user story (US1, US4 ambos P1; US2, US3 P2) para implementación y prueba independiente.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Puede ejecutarse en paralelo (archivos distintos, sin dependencias)
- **[Story]**: US1, US2, US3, US4 (mapping a spec.md)
- Rutas de archivo exactas en cada descripción

**Convenciones (constitution)**: 100% español; `%s` en placeholders; `RETURNING id`; sin `except Exception`; Value Objects `frozen=True`; type hints completos; docstrings Google Style; prohibido sufijo `_sqlite.py`.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Inicialización operativa y verificación del entorno existente (proyecto ya inicializado; no se añaden dependencias).

- [x] T001 [P] Crear plantilla de bitácora de creación `specs/076-liquidacion-requiere-arrendamiento/bitacora_test.json` con el esquema `{"contratos_mandatos":[],"contratos_arrendamientos":[],"propiedades":[],"propietarios":[],"arrendatarios":[],"personas":[],"liquidaciones":[],"recaudos":[]}` (registro de IDs TEST durante la validación)
- [x] T002 [P] Verificar toolchain y piezas reutilizables: pytest/reflex/psycopg2 disponibles; `repo_arriendo` inyectado en `ServicioFinanciero.__init__` (`src/aplicacion/servicios/servicio_financiero.py`); `obtener_activo_por_propiedad` existe en `src/infraestructura/persistencia/repositorio_contrato_arrendamiento_postgres.py:90` (no requiere cambios; documentar confirmación en research.md)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Bloques de dominio compartidos por US1 y US2 (VO de elegibilidad + excepción + tests puros).

**⚠️ CRITICAL**: No puede iniciarse ninguna user story hasta completar esta fase.

- [x] T003 [P] Escribir tests unitarios de dominio `tests/unit/test_resultado_elegibilidad.py` cubriendo las 5 combinaciones de la matriz (puro, sin I/O): DEBEN FALLAR antes de implementar (import de `ResultadoElegibilidad`/`LiquidacionNoElegibleError` inexistentes)
- [x] T004 [P] Crear Value Object `ResultadoElegibilidad` (`@dataclass(frozen=True)`, campos `elegible: bool` y `motivo: str = ""`) en `src/dominio/entidades/resultado_elegibilidad.py`
- [x] T005 [P] Crear excepción de dominio `LiquidacionNoElegibleError(ValueError)` con `motivo: str` en `src/dominio/excepciones/excepciones_liquidacion.py` (semántica distinta de integridad; sin `except Exception` nuevo)

**Checkpoint**: Fundación lista (dominio puro con 100% de cobertura) — las user stories pueden iniciarse en paralelo.

---

## Phase 3: User Story 1 - Elegibilidad correcta en la generación (Priority: P1) 🎯 MVP

**Goal**: Toda liquidación de propietario solo se genera cuando la propiedad cumple Mandato ACTIVO + Arrendamiento ACTIVO sobre el mismo `ID_PROPIEDAD` (combinación 1), en individual y masiva, con la regla en la lógica de negocio (FR-001, FR-002, FR-003, FR-005, FR-006).

**Independent Test**: Ejecutar `pytest tests/unit/test_resultado_elegibilidad.py tests/aplicacion/test_servicio_financiero_elegibilidad.py`: solo la combinación 1 genera; las 2–5 se clasifican como `no_elegibles` (nunca `errores`); el formulario individual solo lista combinación 1; la masiva no aborta y consolida `generadas / ya existían / no elegibles / con error`.

### Tests for User Story 1 (TDD — escribir primero y verlos FALLAR) ⚠️

- [x] T006 [P] [US1] Escribir tests de aplicación `tests/aplicacion/test_servicio_financiero_elegibilidad.py`: generación individual y masiva contra la matriz (SC-002), conteo `no_elegibles` vs `errores` (Decisión 5), excepción `LiquidacionNoElegibleError` con motivo de negocio — DEBEN FALLAR primero
- [x] T007 [P] [US1] Verificar usos de `ServicioContratos.listar_mandatos_ACTIVOs` (`src/aplicacion/servicios/servicio_contratos.py:366`) con grep; si alimenta listas de candidatos UI, marcarlo como dependencia de T011 y planear filtro conjunto (si no, documentar "no aplica" sin cambios)

### Implementation for User Story 1

- [x] T008 [P] [US1] Extender `ResultadoGeneracionPropietario` con `no_elegibles: int = 0` en `src/dominio/entidades/resultado_generacion.py` (default 0; no rompe callers existentes)
- [x] T009 [US1] Modificar `generar_liquidacion_mensual` en `src/aplicacion/servicios/servicio_financiero.py`: tras validar existencia del mandato, verificar `es_activo(contrato.estado_contrato_m)` y `repo_arriendo.obtener_activo_por_propiedad(contrato.id_propiedad)`; lanzar `LiquidacionNoElegibleError` con motivo ("sin contrato de mandato activo" / "sin contrato de arrendamiento activo en esta propiedad"); no duplicidad y cálculo financiero sin cambios
- [x] T010 [P] [US1] Modificar `generar_liquidacion_propietario` en `servicio_financiero.py`: restringir query de contratos con `EXISTS (... CONTRATOS_ARRENDAMIENTOS ca WHERE ca.ID_PROPIEDAD = cm.ID_PROPIEDAD AND ca.ESTADO_CONTRATO_A = %s)` y clasificar los ACTIVO sin arrendamiento como `no_elegibles` (no como errores) según contrato `servicio-financiero.md`
- [x] T011 [P] [US1] Refactorizar `query_propiedades` y `query_propietarios` en `src/presentacion_reflex/state/liquidaciones_state.py` (líneas 223 y 232) con el filtro conjunto arrendamiento ACTIVO (INNER JOIN/EXISTS sobre `CONTRATOS_ARRENDAMIENTOS`) para ofrecer solo la combinación 1 (FR-005)
- [x] T012 [P] [US1] Refactorizar `load_propiedad_seleccionada` en `src/presentacion_reflex/state/liquidaciones_state.py` (línea 643) para validar arrendamiento ACTIVO al seleccionar (no ofrecer combinaciones 2–5 por selección directa)
- [x] T013 [P] [US1] Modificar handler masivo `generar_liquidacion_masiva` en `src/presentacion_reflex/state/liquidaciones_state.py` (línea 1084): query de candidatos `SELECT DISTINCT prop.ID_PROPIETARIO` restringida a propiedades con la combinación completa; consolidar `total_no_elegibles` y desglosar en el sumario `generadas / ya existían / no elegibles / con error` (FR-006, SC-007)
- [x] T014 [US1] e2e de la matriz 5×2 en `tests/e2e/test_liquidaciones.py` y `tests/e2e/test_liquidaciones_playwright.py`: individual (combobox solo combinación 1; generación directa de 2–5 no crea fila en `LIQUIDACIONES`) y masiva (solo combinación 1; no aborta; verificar en BD por JOIN que los `ID_CONTRATO_M` con liquidación pertenecen a propiedades con arrendamiento ACTIVO)

**Checkpoint**: User Story 1 funcional y testeable de forma independiente (MVP delimitado).

---

## Phase 4: User Story 4 - Consistencia individual/masiva + mensajes (Priority: P1)

**Goal**: Ambos caminos producen exactamente el mismo conjunto elegible para el mismo período/datos (SC-003) y comunican la causa de exclusión en lenguaje de negocio (FR-010, SC-006).

**Independent Test**: Para el mismo período y dataset, comparar el conjunto de propiedades elegibles de la individual vs. la masiva (0 discrepancias) y verificar que cada exclusión muestra su motivo ("sin contrato de arrendamiento activo en esta propiedad") tanto en el combobox/toast como en el sumario de masiva.

### Tests for User Story 4 (TDD — escribir primero y verlos FALLAR) ⚠️

- [x] T015 [P] [US4] Escribir tests e2e de consistencia en `tests/e2e/test_liquidaciones.py`: mismo período/datos → conjuntos de elegibles individual vs masiva idénticos (SC-003) — DEBEN FALLAR primero
- [x] T016 [P] [US4] Escribir tests e2e de mensajes en `tests/e2e/test_liquidaciones_playwright.py`: texto de exclusión en lenguaje de negocio verificable en UI individual y resumen de masiva (SC-006) — DEBEN FALLAR primero

### Implementation for User Story 4

- [x] T017 [US4] Implementar mensajes de exclusión en lenguaje de negocio en `src/presentacion_reflex/state/liquidaciones_state.py` usando el `motivo` de `ResultadoElegibilidad`/`LiquidacionNoElegibleError` (propagado desde el servicio): toast individual con causa y sumario masivo detallado por propiedad no elegible; integrar con T013 (depende de US1)

**Checkpoint**: User Stories 1 y 4 funcionan e integran la misma regla en ambas rutas.

---

## Phase 5: User Story 2 - Auditoría histórica (Priority: P2)

**Goal**: Reporte de SOLO LECTURA, re-generable, que marca las liquidaciones históricas que no cumplían la combinación **al estado vigente en su `FECHA_GENERACION`** (reconstrucción por intervalo `[FECHA_INICIO_*, FECHA_FIN_*]`), registrando criterios sin persistir resultados (FR-007, SC-004).

**Independent Test**: Ejecutar `ServicioAuditoriaElegibilidad.auditar(periodo, fecha_reconstruccion)`; verificar `liquidaciones_auditadas` = 100%, que `no_elegibles` solo contiene liquidaciones inelegibles en su fecha de generación (con período, propiedad, propietario y motivo), que `COUNT(*)`/`SUM(NETO_A_PAGAR)` de `LIQUIDACIONES` no cambian antes/después, y que la re-ejecución con los mismos criterios es idéntica.

### Tests for User Story 2 (TDD — escribir primero y verlos FALLAR) ⚠️

- [x] T018 [P] [US2] Escribir tests de aplicación `tests/aplicacion/test_servicio_auditoria_elegibilidad.py`: motivo por combinación usando intervalos vs `fecha_generacion`, 0 escrituras (assert solo SELECT / sin efecto), criterios registrados y reporte re-generable — DEBEN FALLAR primero

### Implementation for User Story 2

- [x] T019 [P] [US2] Agregar consulta de auditoría (solo `SELECT`, una sola pasada, placeholders `%s`) en `src/infraestructura/persistencia/repositorio_liquidacion_postgres.py` (o repositorio de auditoría nuevo): liquidaciones + mandato + propiedad + propietario + datos de arrendamiento de la propiedad; nunca inserta/actualiza/elimina
- [x] T020 [US2] Implementar `ServicioAuditoriaElegibilidad.auditar(periodo: Optional[str] = None, fecha_reconstruccion: Optional[str] = None)` en `src/aplicacion/servicios/servicio_auditoria_elegibilidad.py` con los `@dataclass(frozen=True)` `AuditoriaElegibilidadResultado`, `CriteriosAuditoria` y `LiquidacionInelegible` (contrato `auditoria-elegibilidad.md`); registra criterios en log; meta de tiempo < 60s (Decisión 8)
- [x] T021 [P] [US2] Crear estado de auditora en `src/presentacion_reflex/state/auditoria_state.py`: selector de perodo, ejecutar `auditar`, mostrar tabla de no elegibles + criterios re-generables; SIN rutas/endpoints nuevos (reusar handlers y RBAC existentes)
- [x] T022 [US2] e2e de auditora en `tests/e2e/test_liquidaciones.py`: `COUNT(*)` y `SUM(NETO_A_PAGAR)` de `LIQUIDACIONES` idnticos antes/despus; re-ejecucin con mismos criterios devuelve idntico resultado

**Checkpoint**: User Story 2 independiente y solo lectura confirmada por tests.

---

## Phase 6: User Story 3 - Eliminación total de datos TEST (Priority: P2)

**Goal**: Script Postgres idempotente y re-ejecutable que elimina TODOS los datos TEST de la bitácora de creación (y huérfanas que apuntan solo a ella), en transacción única, sin tocar datos reales (FR-008, SC-005).

**Independent Test**: Registrar IDs TEST en `bitacora_test.json`; `--dry-run` lista solo los de la bitácora; `--ejecutar` borra en orden FK con rollback total ante error; consultas posteriores → 0 registros TEST y 0 huérfanas, datos reales intactos; re-ejecución sale OK sin efectos.

### Tests for User Story 3 (TDD — escribir primero y verlos FALLAR) ⚠️

- [x] T023 [P] [US3] Escribir tests unitarios `tests/unit/test_limpieza_test_bitacora.py` sobre la lógica pura del script: parseo de bitácora JSON, orden FK, idempotencia (IDs inexistentes se ignoran), conteos de `--dry-run` — DEBEN FALLAR primero (import del script inexistente)

### Implementation for User Story 3

- [x] T024 [US3] Implementar `src/scripts/limpiar_datos_test_bitacora_pg.py` (patrón de `src/scripts/limpiar_datos_prueba_pg.py`): leer `bitacora_test.json`, borrar en orden FK (recaudos → liquidaciones/derivados → contratos → propiedades → arrendatarios/propietarios → personas) en transacción única con `ROLLBACK` total, flags `--dry-run` (defecto) / `--ejecutar` / `--bitacora <ruta>` (contrato `limpieza-test.md`), salida por entidad con conteos y estado OK/ROLLBACK
- [x] T025 [US3] Implementar limpieza de relaciones derivadas huérfanas que apuntan EXCLUSIVAMENTE a IDs de la bitácora en `limpiar_datos_test_bitacora_pg.py`: `INCIDENTE_LIQUIDACION`, `PLAN_PAGO_INCIDENTE`, `CUOTA_INCIDENTE`, `HISTORIAL_INCIDENTES`, `INCIDENTES` y vínculos; nunca borrar por patrones de estado/nombre (Q1/Q3)
- [x] T026 [US3] Añadir verificación post-limpieza en `limpiar_datos_test_bitacora_pg.py`/quickstart.md: consulta de control (0 registros TEST por entidad de la bitácora + 0 huérfanas + datos reales intactos) y eliminación de la bitácora de creación al terminar, con resultado de error visible si quedan restos

**Checkpoint**: User Story 3 independiente y condición de cierre de la feature garantizada.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Calidad, validación integral y documentación que impactan todas las stories.

- [x] T027 [P] Verificar cobertura: 100% en `src/dominio/` nuevo y >90% en la lógica nueva de aplicación/scripts (`pytest --cov`); sin regresiones en tests e2e existentes
- [x] T028 [P] Ejecutar quality gates (constitution §5): `check_syntax.py`, `mypy`, `ruff`, `black` sobre todos los archivos modificados; corregir hallazgos antes de cerrar
- [x] T029 [P] Ejecutar validación completa de `specs/076-liquidacion-requiere-arrendamiento/quickstart.md` (matriz 5×2 → 10/10, consistencia, auditoría, limpieza, mensajes) y registrar el resultado y la bitácora TEST en la feature
- [x] T030 [P] Registrar ADR en `docs/decisions/`: elegibilidad en Dominio/Aplicación + reconstrucción histórica por intervalo de fechas (decisión Q1-clarify; constitution §15)
- [x] T031 [P] Actualizar documentación dinámica del repositorio (`ESTADO_TAREAS.md`, `CLAUDE.md` si aplica) tras el cierre de la feature (constitution §5/§15)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Sin dependencias — puede iniciar de inmediato
- **Foundational (Phase 2)**: Depende de Setup — BLOQUEA todas las user stories
- **User Stories (Phase 3+)**: Todas dependen de Foundational
  - **US1 (P1)**: Primera en implementarse (MVP)
  - **US4 (P1)**: Depende de US1 (verifica consistencia y mensajes sobre la misma regla)
  - **US2 (P2)**: Depende de Foundational (reusa `ResultadoElegibilidad`/`LiquidacionNoElegibleError` y la lógica de motivo); independiente de US1/US3
  - **US3 (P2)**: Independiente de US1/US2/US4 (solo requiere la bitácora T001)
- **Polish (Phase 7)**: Depende de que las stories deseadas estén completas

### User Story Dependencies

- **User Story 1 (P1)**: Puede iniciar tras Foundational — sin dependencias de otras stories
- **User Story 4 (P1)**: Inicia tras US1 (prueba la regla implementada en ambas rutas)
- **User Story 2 (P2)**: Inicia tras Foundational — integra el VO/excepción compartidos
- **User Story 3 (P2)**: Inicia tras Foundational — requiere T001 (bitácora)

### Within Each User Story

- Tests escritos PRIMERO y en FALLO antes de implementar
- Dominio/Value Objects antes de servicios; servicios antes de UI/state
- Implementación core antes de e2e/integración
- Story completa antes de pasar a la siguiente prioridad

### Parallel Opportunities

- Todos los tasks marcados [P] de Setup y Foundational pueden ejecutarse en paralelo
- Dentro de US1: T006–T013 en paralelo (archivos distintos); T014 (e2e) tras T009–T013
- US2 y US3 pueden iniciarse en paralelo con US4 una vez completada la Foundational
- Todos los tasks [P] de Polish en paralelo

---

## Parallel Example: User Story 1

```bash
# Lanzar todos los tests de US1 juntos (TDD, fallo inicial):
Task: "T006 tests de aplicación elegibilidad en tests/aplicacion/test_servicio_financiero_elegibilidad.py"

# Lanzar la implementación en paralelo (archivos distintos):
Task: "T008 Extender ResultadoGeneracionPropietario en src/dominio/entidades/resultado_generacion.py"
Task: "T011 Refactorizar query_propiedades/query_propietarios en src/presentacion_reflex/state/liquidaciones_state.py"
Task: "T013 Handler masivo generacion_liquidacion_masiva en src/presentacion_reflex/state/liquidaciones_state.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Completa Phase 1: Setup
2. Completa Phase 2: Foundational (CRÍTICO — bloquea todo)
3. Completa Phase 3: User Story 1 (elegibilidad en individual y masiva)
4. **STOP y VALIDA**: `pytest tests/unit/test_resultado_elegibilidad.py tests/aplicacion/test_servicio_financiero_elegibilidad.py tests/e2e/test_liquidaciones.py -q`
5. Revisión antes de continuar (matriz 5×2 en individual y masiva)

### Incremental Delivery

1. Setup + Foundational → fundación lista (dominio puro, 100% cobertura)
2. US1 → probar independiente → (MVP)
3. US4 (P1) → consistencia y mensajes de negocio → probar
4. US2 (P2) → auditoría solo lectura → probar
5. US3 (P2) → limpieza TEST → probar
6. Polish: coverage, gates, quickstart completo, ADR, documentación

### Parallel Team Strategy

Con varios desarrolladores:

1. Equipo completa Setup + Foundational juntos
2. Tras la Foundational:
   - Dev A: US1 (+ US4 después)
   - Dev B: US2 (auditoría)
   - Dev C: US3 (limpieza)
3. Cada story se integra y prueba de forma independiente

---

## Notes

- [P] tasks = archivos diferentes, sin dependencias
- [Story] marca la trazabilidad de cada task a su user story
- Cada story es completable y testeable de forma independiente
- Verificar que los tests fallan antes de implementar (TDD)
- Commit sugerido por grupo lógico y convencional: `feat(liquidaciones): ...`, `feat(auditoria): ...`, `chore(limpieza): ...`, `test(...)` (solo al finalizar cada grupo)
- Compilar en cualquier checkpoint para validar la story de forma independiente
- Evitar: tasks vagos, conflictos de mismo archivo, dependencias cruzadas que rompan la independencia
- Constitución: sin `except Exception`, `%s`, `RETURNING id`, 100% español, Value Objects `frozen=True`

---

## Phase 8: Convergence

**Purpose**: Cerrar la brecha entre `spec.md`/`plan.md`/`tasks.md` y el estado real del código. `/speckit.converge` detectó que varias tareas marcadas `[x]` carecen de entregable funcional (stubs), la auditoría no implementa la reconstrucción por intervalo y hay una violación de constitución.

- [x] T032 Corregir `except Exception` genérico en `src/presentacion_reflex/state/auditoria_state.py:23` con catches específicos (`ValueError`, `LiquidacionNoElegibleError`, excepciones DB concretas) y propagar `error_message` sin tragar errores per Constitution §2.2 (contradicts)
- [x] T033 Implementar reconstruccin histrica por intervalo en `ServicioAuditoriaElegibilidad.auditar` (`src/aplicacion/servicios/servicio_auditoria_elegibilidad.py`): evaluar `ESTADO_CONTRATO_M` y `ESTADO_CONTRATO_A` vigentes en `LIQUIDACIONES.FECHA_GENERACION` usando `[FECHA_INICIO_M, FECHA_FIN_M]` y `[FECHA_INICIO_A, FECHA_FIN_A]` (solo `SELECT`, `%s`); registrar los intervalos y la regla en `CriteriosAuditoria`; meta < 60s (Decisin 8) per FR-007/SC-004/Q8 (contradicts)
- [x] T034 Reescribir `src/scripts/limpiar_datos_test_bitacora_pg.py` (patrón `limpiar_datos_prueba_pg.py`): leer `bitacora_test.json`, borrar en orden FK (recaudos → liquidaciones/derivados → contratos → propiedades → arrendatarios/propietarios → personas) en transacción única con `ROLLBACK` total, flags `--dry-run` (defecto) / `--ejecutar` / `--bitacora <ruta>`, huérfanas derivadas solo por IDs de bitácora (`INCIDENTE_LIQUIDACION`, `PLAN_PAGO_INCIDENTE`, `CUOTA_INCIDENTE`, `HISTORIAL_INCIDENTES`, `INCIDENTES`), post-verificación (0 TEST, 0 huérfanas, datos reales intactos), salida por entidad con estado OK/ROLLBACK per FR-008/SC-005/contrato `limpieza-test.md` (missing)
- [x] T035 Escribir tests unitarios reales en `tests/unit/test_limpieza_test_bitacora.py` (reemplazar `assert True`): parseo de bitácora, orden FK, idempotencia (IDs inexistentes ignorados), conteos `--dry-run` per T023/contrato `limpieza-test.md` (missing)
- [x] T036 Reescribir `tests/aplicacion/test_servicio_financiero_elegibilidad.py` (reemplazar los `pass`): generación individual/masiva contra la matriz 5×2 con mocks de `repo_arriendo`/`repo_mandato` (SC-002), conteo `no_elegibles` vs `errores` (Decisión 5), `LiquidacionNoElegibleError` con motivo per SC-002/Decisión 5 (missing)
- [x] T037 Escribir tests de aplicación reales en `tests/aplicacion/test_servicio_auditoria_elegibilidad.py` (reemplazar `assert True`): motivos por combinación evaluados con intervalos vs `fecha_generacion`, 0 escrituras (solo `SELECT`), criterios registrados, reporte re-generable per T018/FR-007/SC-004 (missing)
- [x] T038 Integrar auditoría en la UI: alinear `src/presentacion_reflex/state/auditoria_state.py` con `src/presentacion_reflex/pages/auditoria.py` (el page espera `set_search`, `filter_tabla`, `set_filter_tabla`, `logs`, `load_logs` que el estado nuevo no define → AttributeError en runtime) añadiendo selector de período, tabla de `no_elegibles` con motivo y criterios re-generables; SIN rutas/endpoints nuevos (reusar handlers y RBAC existentes) per T021/SC-004 (contradicts)
- [x] T039 Aadir desglose por propiedad no elegible con motivo de negocio al sumario masivo (y verificar toast individual con causa) en `src/presentacion_reflex/state/liquidaciones_state.py` per T017/SC-006 (partial)
- [x] T040 Registrar ADR en `docs/decisions/` para la feature 076: elegibilidad en Dominio/Aplicacin + reconstruccin histrica por intervalo de fechas (decisin Q8) per Constitution 15/T030 (missing)
- [x] T041 Actualizar `docs/auditorias/ESTADO_TAREAS.md` (y `CLAUDE.md` si aplica) con el cierre de la feature 076, validar `quickstart.md` (matriz 52  10/10, consistencia, auditora, limpieza, mensajes) registrando el resultado, y definir la poltica de retencin de `bitacora_test.json` coherente con T026 (eliminar al terminar) y T029 (registrar en la feature) per T029/T031/Constitution 5 (missing)
- [x] T042 Integrar o retirar el Value Object `ResultadoElegibilidad` (`src/dominio/entidades/resultado_elegibilidad.py`): hoy solo se usa en tests; usarlo en el flujo individual/masiva/auditoría o eliminarlo para evitar código muerto per spec contrato `servicio-financiero.md` (unrequested)
- [x] T043 Sustituir literales `'ACTIVO'` embebidos en las queries nuevas de `src/presentacion_reflex/state/liquidaciones_state.py` (lneas 223-261, 652-655, 1091-1092) por placeholders `%s` (patrn de `EstadoContrato.ACTIVO.value`) per Constitution 2.3 (partial)

---

## Phase 9: Convergence (Continuacin)

**Purpose**: Segundo ciclo de `/speckit.converge`. `/speckit.implement` ejecutó Phase 8 (T032-T043): se verificaron en el código la reconstruccin por intervalo de `ServicioAuditoriaElegibilidad` (CASE WHEN + subquery por `FECHA_GENERACION`, solo `SELECT`/`%s`), el script `limpiar_datos_test_bitacora_pg.py` completo (orden FK, transaccin nica, `--dry-run`/`--ejecutar`, post-verificacin), los tests reales de limpieza/US1/auditora, la UI integrada en `auditoria.py` (selector perodo + tabla `no_elegibles` + criterios) y el ADR `002-elegibilidad-liquidacion-intervalos.md`. **Aun NO convergido**: queda un SyntaxError que rompe la compilacin de la app, `except Exception` en el handler nuevo de auditora y VOs/queries con tildes o literales pendientes.

**Bloqueante**: `python -c "import ast; ast.parse(open('src/presentacion_reflex/state/liquidaciones_state.py', encoding='utf-8').read())"` falla en `liquidaciones_state.py:1159` (f-string invlido `f" (Motivos: {,, .join(...)}..."`) — la app no compila.

- [x] T044 [CRITICAL] Corregir el SyntaxError del f-string en `src/presentacion_reflex/state/liquidaciones_state.py:1159` (mensaje de motivos del sumario masivo, T039): el literal `{,,` y los comodines anidados son invlidos; reescribir el mensaje con `",".join(detalles[:3])` y sufijo `"..."` correcto, y comprobar que el archivo compila (`ast.parse` sin errores) antes de marcar (contradicts, nuevo)
- [x] T045 [CRITICAL] Eliminar `except Exception` genrico del handler nuevo `auditar_elegibilidad` en `src/presentacion_reflex/state/auditoria_state.py:132` (mantener el `ValueError` existente y aadir catches especficos de DB/psycopg para el resto, propagando `error_message`), y evaluar el `except Exception` legacy de `load_logs` (lnea 97) para alinearlo o dejarlo documentado, per Constitution 2.2 (contradicts)
- [x] T046 [MEDIUM] Parametrizar el literal `'ACTIVO'` restante en `src/presentacion_reflex/state/liquidaciones_state.py:657` (query_mandato del flujo de carga, dentro del rango 652-655 objetivo de T043): sustituir por `%s` con `EstadoContrato.ACTIVO.value` y ajustar los parmetros de `cursor.execute`, siguiendo el patrn ya aplicado en las lneas 229/240/1093 per Constitution 2.3 (partial)
- [x] T047 [LOW] Integrar o eliminar el Value Object `ResultadoElegibilidad` (`src/dominio/entidades/resultado_elegibilidad.py`): sigue con 0 usos en `src/` tras T042; usarlo en el flujo individual/masiva/auditora o eliminarlo para evitar cdigo muerto per spec contrato `servicio-financiero.md` (contradicts)
- [x] T048 [LOW] Completar `docs/auditorias/ESTADO_TAREAS.md` con el resultado de la validacin de `quickstart.md` (matriz 5  2 = 10/10, auditora, limpieza, mensajes) que exiga T041 y corregir las tildes perdidas ("Liquidacin", "Retencin", "poltica") per T029/T031/Constitution 5 (partial)

---

## Phase 10: Convergence

**Purpose**: Tercer ciclo de `/speckit.converge`. `/speckit.implement` ejecutó Phase 9 (T044-T048): se verific en el cdigo la correccin del SyntaxError de `liquidaciones_state.py:1159` (compila con `ast.parse`), la eliminacin de `except Exception` en `auditoria_state.py` (ahora usa `psycopg2.Error`/`ValueError`), y la parametrizacin con `%s` de `liquidaciones_state.py:657`. **Aun NO convergido**: quedan items LOW (mensajera de errores duplicada en `auditoria_state.py`, VO `ResultadoElegibilidad` sin integrar ni eliminar, y tilde residual en `ESTADO_TAREAS.md`). Sin CRITICAL/HIGH; Constitution 2.2 y 2.3 satisfechas.

- [x] T049 [LOW] Integrar o eliminar el Value Object `ResultadoElegibilidad` (`src/dominio/entidades/resultado_elegibilidad.py`): sigue con 0 usos en `src/` tras T042 y T047 (grep en todo el repo solo lo halla en specs/docs); usarlo en el flujo individual/masiva/auditora (p.ej. como tipo de retorno de `ServicioFinanciero`/aterrizado en `LiquidacionInelegible`) o eliminarlo para evitar cdigo muerto per contrato `servicio-financiero.md` (contradicts)
- [x] T050 [LOW] Unificar los handlers de error duplicados en `src/presentacion_reflex/state/auditoria_state.py:98-104` y `:136-141` (dos `async with self` consecutivos en el mismo `except`): el segundo bloque sobreescribe `error_message` y pierde el mensaje detallado de `psycopg2.Error`; dejar un nico `async with self` que propague el mensaje especfico per Constitution 2.2 / calidad de mensajera (partial)
- [x] T051 [LOW] Corregir la tilde faltante en `docs/auditorias/ESTADO_TAREAS.md:3`: la palabra "ejecucion" (sin acento, tal como aparece hoy en esa linea) debe escribirse "ejecucion" con tilde en la "o" (es decir, "ejecucion" correctamente acentuada) dentro de la politica de retencion de `bitacora_test.json`, para cerrar T048 por completo per T031/Constitution 5 (partial)

---

## Phase 11: Convergence

**Purpose**: Cuarto ciclo de `/speckit.converge`. `/speckit.implement` ejecutó Phase 10 (T049-T051): se eliminó el Value Object `ResultadoElegibilidad` (archivo y test borrados, sin imports colgantes en `src/` ni `tests/`), se unificaron los handlers de error en `auditoria_state.py` (un solo `except psycopg2.Error`/`ValueError` por metodo) y se corrigió la tilde en `ESTADO_TAREAS.md:3`. **Casi convergido**: el unico gap restante es drift de documentacion creado por la eliminacion del VO (T049): `quickstart.md:70` y `contracts/servicio-financiero.md:50-53` aun referencian el VO/test borrado. Sin CRITICAL/HIGH/MEDIUM; Constitution 2.2, 2.3 y 2.4 satisfechas en codigo nuevo.

- [x] T052 [LOW] Sincronizar docs 076 tras eliminar el `ResultadoElegibilidad` (T049): corregir `specs/076-liquidacion-requiere-arrendamiento/quickstart.md:70` (el comando `pytest tests/unit/test_resultado_elegibilidad.py -q` apunta a un archivo eliminado; reemplazarlo por `pytest tests/aplicacion/test_servicio_financiero_elegibilidad.py -q`, que cubre la matriz 5x2 a nivel servicio) y actualizar `specs/076-liquidacion-requiere-arrendamiento/contracts/servicio-financiero.md:50-53` para indicar que la regla de elegibilidad se materializa via `LiquidacionNoElegibleError` (motivo en lenguaje de negocio) y no via el VO eliminado per T049/Constitution 5 (Documentacion Dinamica) (partial)

---

## Phase 12: Convergence

**Purpose**: Quinto ciclo de `/speckit.converge`. `/speckit.implement` ejecutó Phase 11 (T052): `quickstart.md:70` ya no apunta al test eliminado y `contracts/servicio-financiero.md:48-50` describe la regla via `LiquidacionNoElegibleError` (referencia al VO eliminado fuera de los docs). **Casi convergido**: queda un nit de documentacion — el bloque "Verificacion automatizada" de quickstart quedo con un comentario de dominio obsoleto y el mismo comando duplicado; sin gaps de codigo (codigo feature verificado limpio en ciclos previos). Sin CRITICAL/HIGH/MEDIUM; Constitution 2.2, 2.3 y 2.4 satisfechas en codigo nuevo.

- [x] T053 [LOW] Limpiar el bloque "Verificacion automatizada" de `specs/076-liquidacion-requiere-arrendamiento/quickstart.md:66-77`: eliminar el comentario obsoleto "# Unitarios de dominio (matriz pura, sin I/O)" (el test de dominio ya no existe tras T049) y la duplicacion del comando `pytest tests/aplicacion/test_servicio_financiero_elegibilidad.py -q` que hoy aparece dos veces (l.70 y l.73), dejando UN solo comando con etiqueta clara (p.ej. "# Matriz 5x2 (individual + masiva) a nivel servicio") antes del bloque E2E per T052/Constitution 5 (Documentacion Dinamica) (partial)