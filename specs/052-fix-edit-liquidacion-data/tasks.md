# Tasks: Corrección de Carga de Datos en Edición de Liquidaciones

**Input**: Design documents from `/specs/052-fix-edit-liquidacion-data/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, quickstart.md

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Investigación y Verificación de Causa Raíz

**Purpose**: Confirmar la hipótesis de causa raíz antes de implementar correcciones

- [x] T001 Verificar en PostgreSQL si la liquidación 2026-07 de CRISTIAN JAMIOY tiene registros en LIQUIDACIONES_CONTRATOS (consultar directamente en base de datos)
- [x] T002 Verificar en PostgreSQL si la liquidación 2026-07 de CRISTIAN JAMIOY tiene registros en DESCUENTOS_ASESORES (consultar directamente en base de datos)
- [x] T003 Ejecutar query de diagnóstico: comparar cantidad de propiedades y descuentos entre liquidaciones 2026-05 (funcional) y 2026-07 (no funcional)
- [x] T004 Revisar implementación de `DatabaseManager.transaccion()` en `src/infraestructura/persistencia/database.py` para entender comportamiento de transacciones anidadas
- [x] T005 Revisar implementación de `agregar_descuento()` en `src/aplicacion/servicios/servicio_liquidacion_asesores.py` línea 492 para verificar si abre transacción propia

**Checkpoint**: Causa raíz confirmada — se procede con corrección

---

## Phase 2: Fundacional (Corrección de Atomicidad)

**Purpose**: Corregir el problema de transacciones anidadas que impide la persistencia correcta de descuentos

- [x] T006 Modificar `guardar_contratos_liquidacion()` en `src/infraestructura/repositorios/repositorio_liquidacion_asesor.py` para que acepte un parámetro `conn` opcional de conexión existente, reutilizando la transacción padre en lugar de abrir una nueva
- [x] T007 Modificar `crear()` en `src/infraestructura/repositorios/repositorio_descuento_asesor.py` para que acepte un parámetro `conn` opcional de conexión existente, reutilizando la transacción padre en lugar de abrir una nueva
- [x] T008 Modificar `agregar_descuento()` en `src/aplicacion/servicios/servicio_liquidacion_asesores.py` para pasar la conexión activa del repositorio de liquidación al repositorio de descuentos, evitando transacción anidada
- [x] T009 Modificar `generar_liquidacion_multi_contrato()` en `src/aplicacion/servicios/servicio_liquidacion_asesores.py` para obtener la conexión activa de la transacción y pasarla a `guardar_contratos_liquidacion()` y `agregar_descuento()`
- [x] T010 Agregar verificación post-generación en `generar_liquidacion_multi_contrato()`: después del COMMIT, consultar LIQUIDACIONES_CONTRATOS y DESCUENTOS_ASESORES para confirmar que los registros existen; si faltan, lanzar excepción con detalle del error

**Checkpoint**: La generación de liquidaciones ahora persiste atómicamente contratos y descuentos

---

## Phase 3: User Story 5 - Persistencia Correcta durante la Generación (Priority: P1) 🎯 MVP

**Goal**: Garantizar que toda la información generada durante la creación de una liquidación sea persistida correctamente en PostgreSQL

**Independent Test**: Generar una liquidación nueva y verificar directamente en PostgreSQL que existen registros en LIQUIDACIONES_ASESORES, LIQUIDACIONES_CONTRATOS y DESCUENTOS_ASESORES

### Implementation for User Story 5

- [x] T011 [US5] Crear script de verificación en `scripts/diagnostico/verificar_integridad_liquidacion.py` que reciba un ID de liquidación y valide: (1) existe en LIQUIDACIONES_ASESORES, (2) tiene registros en LIQUIDACIONES_CONTRATOS si es multi-contrato, (3) tiene registros en DESCUENTOS_ASESORES si total_descuentos > 0
- [x] T012 [US5] Agregar logging detallado en `generar_liquidacion_multi_contrato()` para registrar: cantidad de contratos insertados, cantidad de descuentos insertados, y valores calculados (canon_total, comision_bruta, total_descuentos)
- [x] T013 [US5] Ejecutar generación masiva de prueba para un asesor con 3+ contratos y verificar con el script de T011 que todos los registros persisten correctamente

**Checkpoint**: La generación de nuevas liquidaciones persiste correctamente el 100% de los datos

---

## Phase 4: User Story 1 - Edición de Liquidación Recién Creada con Carga Completa (Priority: P1)

**Goal**: La acción Editar carga la totalidad de Propiedades a Liquidar y Descuentos Guardados para liquidaciones recién generadas

**Independent Test**: Generar una liquidación nueva, hacer clic en Editar, y verificar que se muestran todas las propiedades y descuentos

### Implementation for User Story 1

- [x] T014 [US1] Revisar y corregir `obtener_contratos_de_liquidacion()` en `src/infraestructura/repositorios/repositorio_liquidacion_asesor.py` línea 406: verificar que los INNER JOINs no descarten filas silenciosamente si algún registro referenciado fue eliminado
- [x] T015 [US1] Agregar fallback en `obtener_contratos_de_liquidacion()`: si el JOIN con CONTRATOS_ARRENDAMIENTOS no encuentra el contrato (posiblemente eliminado), devolver los datos básicos de LIQUIDACIONES_CONTRATOS sin el JOIN
- [x] T016 [US1] Revisar `open_edit_modal()` en `src/presentacion_reflex/state/liquidacion_asesores/form_state.py` línea 552: verificar que `detalles.get("contratos")` y `detalles.get("descuentos")` se mapean correctamente al UI
- [x] T017 [US1] Agregar logging en `open_edit_modal()` para registrar la cantidad de contratos y descuentos cargados desde el servicio
- [x] T018 [US1] Generar una liquidación nueva para un asesor con 3+ contratos, hacer clic en Editar, y verificar que el modal muestra todas las propiedades y descuentos

**Checkpoint**: La edición de liquidaciones recién creadas carga correctamente toda la información

---

## Phase 5: User Story 2 - Edición de Liquidaciones Históricas con Consistencia (Priority: P1)

**Goal**: Las liquidaciones históricas que funcionaban correctamente continúan funcionando sin regresiones

**Independent Test**: Abrir liquidaciones de períodos anteriores (2026-05) y verificar que la edición carga toda la información

### Implementation for User Story 2

- [x] T019 [US2] Ejecutar pruebas de regresión: abrir modal de edición de 3 liquidaciones históricas de diferentes períodos y verificar que todas cargan propiedades y descuentos correctamente
- [x] T020 [US2] Verificar que las correcciones de T006-T010 no afectan el comportamiento de liquidaciones que ya tenían datos completos en la base de datos
- [x] T021 [US2] Documentar en `specs/052-fix-edit-liquidacion-data/evidencia-regresion.md` los resultados de las pruebas de regresión con capturas de pantalla

**Checkpoint**: No se introducen regresiones en liquidaciones históricas

---

## Phase 6: User Story 3 - Validación de Consistencia End-to-End (Priority: P2)

**Goal**: La información visible en la UI corresponde exactamente con lo almacenado en PostgreSQL

**Independent Test**: Comparar campo por campo la respuesta del servicio con los datos en la UI del modal de edición

### Implementation for User Story 3

- [x] T022 [US3] Crear script de validación end-to-end en `scripts/diagnostico/validar_consistencia_edit.py` que: (1) dado un ID de liquidación, consulte PostgreSQL directamente, (2) ejecute `obtener_detalle_completo()` del servicio, (3) compare las cantidades de contratos, descuentos y bonificaciones
- [x] T023 [US3] Ejecutar el script de validación para al menos 5 liquidaciones de diferentes períodos y documentar resultados
- [x] T024 [US3] Verificar que la serialización en `_liquidacion_to_dict()`, `_descuento_to_dict()` y `_pago_to_dict()` en `src/aplicacion/servicios/servicio_liquidacion_asesores.py` no omite campos relevantes

**Checkpoint**: La información en PostgreSQL, el servicio y la UI están sincronizadas

---

## Phase 7: User Story 4 - Edición con Diferentes Volúmenes de Datos (Priority: P2)

**Goal**: La edición funciona correctamente independientemente de la cantidad de propiedades y descuentos

**Independent Test**: Probar con asesores de 1 propiedad, 5+ propiedades, 0 descuentos, y 5+ descuentos

### Implementation for User Story 4

- [x] T025 [US4] Probar edición de liquidación con asesor de exactamente 1 propiedad y 0 descuentos
- [x] T026 [US4] Probar edición de liquidación con asesor de 10+ propiedades y 5+ descuentos
- [x] T027 [US4] Verificar que el estado de selección de propiedades se mantiene fiel al registrado durante la generación
- [x] T028 [US4] Documentar resultados en `specs/052-fix-edit-liquidacion-data/evidencia-volumenes.md`

**Checkpoint**: La corrección es robusta ante diferentes escenarios de volumen de datos

---

## Phase 8: Migración de Datos para Liquidaciones Afectadas

**Purpose**: Reconstruir datos faltantes en liquidaciones existentes que fueron afectadas por el bug

- [x] T029 Crear script de migración en `migraciones/fix_datos_liquidaciones_afectadas.sql` que: (1) identifique liquidaciones multi-contrato sin registros en LIQUIDACIONES_CONTRATOS, (2) reconstruya los registros basándose en los contratos activos del asesor al momento de la generación
- [x] T030 Agregar lógica al script de migración para reconstruir DESCUENTOS_ASESORES faltantes: calcular seguro (2% del canon) y 4x1000 para cada contrato, e insertar los registros correspondientes
- [x] T031 Ejecutar el script de migración en entorno de staging y verificar que la liquidación 2026-07 de CRISTIAN JAMIOY muestra correctamente todas las propiedades y descuentos (NOTA: Consulta arrojó 0 afectados)
- [x] T032 Ejecutar el script de migración en producción (previa aprobación) (NOTA: 0 afectados)
- [x] T033 Ejecutar script de verificación post-migración para confirmar integridad referencial en todas las liquidaciones afectadas (NOTA: 0 afectados)

**Checkpoint**: Liquidaciones históricas afectadas tienen sus datos reconstruidos

---

## Phase 9: Polish y Validación Final

**Purpose**: Verificación completa y limpieza

- [x] T034 Ejecutar quickstart.md completo: validar los 6 escenarios de prueba definidos
- [x] T035 Verificar que el script de verificación (T011) pasa para todas las liquidaciones del período 2026-07
- [x] T036 Verificar que el script de validación end-to-end (T022) pasa para al menos 10 liquidaciones
- [x] T037 Revisar y limpiar código: eliminar logs de debug, confirmar que no hay código muerto
- [x] T038 Actualizar `ESTADO_TAREAS.md` con el resultado de la corrección

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Investigación)**: No dependencies - start immediately
- **Phase 2 (Fundacional)**: Depends on Phase 1 completion (root cause confirmed) - BLOCKS all user stories
- **Phase 3 (US5)**: Depends on Phase 2 - Persistencia durante generación
- **Phase 4 (US1)**: Depends on Phase 2 - Edición de liquidaciones nuevas
- **Phase 5 (US2)**: Depends on Phase 4 - Validación de regresión
- **Phase 6 (US3)**: Depends on Phase 4 - Validación end-to-end
- **Phase 7 (US4)**: Depends on Phase 4 - Pruebas de volumen
- **Phase 8 (Migración)**: Depends on Phase 2 - Puede ejecutarse en paralelo con Phases 3-7
- **Phase 9 (Polish)**: Depends on all previous phases

### User Story Dependencies

- **US5 (P1)**: Can start after Phase 2 - No dependencies on other stories
- **US1 (P1)**: Can start after Phase 2 - No dependencies on other stories
- **US2 (P1)**: Depends on US1 (need the fix deployed to test regression)
- **US3 (P2)**: Depends on US1 (need the fix to validate end-to-end)
- **US4 (P2)**: Depends on US1 (need the fix to test different volumes)

### Parallel Opportunities

- Phase 1 tasks (T001-T005) can run in parallel
- Phase 2 tasks (T006-T010) are sequential (same files)
- Phase 3 (US5) and Phase 4 (US1) can run in parallel after Phase 2
- Phase 8 (Migración) can run in parallel with Phases 3-7
- Phase 9 validation tasks (T034-T036) can run in parallel

---

## Parallel Example: Phases 3 & 4

```bash
# After Phase 2 completes, launch US5 and US1 in parallel:

# US5 - Persistencia during generation:
Task: "T011 Crear script de verificación de integridad"
Task: "T012 Agregar logging detallado en generación"

# US1 - Edit modal fix:
Task: "T014 Revisar y corregir obtener_contratos_de_liquidacion()"
Task: "T016 Revisar open_edit_modal()"
```

---

## Implementation Strategy

### MVP First (US5 + US1 — P1 stories)

1. Complete Phase 1: Investigación (confirm root cause)
2. Complete Phase 2: Fundacional (fix transaction atomicity)
3. Complete Phase 3: US5 (persistencia durante generación)
4. Complete Phase 4: US1 (edición de liquidaciones nuevas)
5. **STOP and VALIDATE**: Generar liquidación nueva, verificar DB, editar, verificar UI
6. Deploy to staging if validation passes

### Incremental Delivery

1. Phase 1 + Phase 2 → Root cause fixed, atomicity restored
2. Phase 3 + Phase 4 → MVP: new liquidaciones work correctly
3. Phase 5 → Regression testing passes
4. Phase 6 + Phase 7 → End-to-end validation and volume testing
5. Phase 8 → Historical data migrated
6. Phase 9 → Final validation and cleanup

---

## Notes

- This is a bug fix, not a new feature — tasks focus on investigation, correction, and validation
- Phase 1 (Investigation) is critical — do not skip or rush it
- The migration script (Phase 8) should be tested thoroughly in staging before production
- All validation should be documented with evidence (screenshots, query results)
