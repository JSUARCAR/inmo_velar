# Tasks: fix-incident-selection-button

**Input**: Design documents from `specs/029-fix-incident-selection-button/`

**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, quickstart.md ✅

**Tests**: No se requieren tests unitarios automatizados. La validación es manual/visual según quickstart.md.

**Organization**: Tareas organizadas por user story para implementación y validación independiente.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Puede ejecutarse en paralelo (archivos diferentes, sin dependencias)
- **[Story]**: User story a la que pertenece (US1, US2, US3)
- Rutas exactas de archivos incluidas

## Phase 1: Setup

**Purpose**: No se requiere setup — la infraestructura existe completamente (repositorios, servicios, componentes UI, tablas BD).

> ⏭️ Fase saltada. Todo el código base ya existe y está operativo.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: No hay prerequisitos bloqueantes — los cambios son directos sobre código existente.

> ⏭️ Fase saltada. No se necesitan nuevas dependencias, esquemas ni infraestructura.

---

## Phase 3: User Story 1 — Corregir Flujo de Asociación de Incidentes en Edición (Priority: P1) 🎯 MVP

**Goal**: Reparar el flujo completo de selección e asociación de incidentes desde el formulario de edición de liquidaciones, corrigiendo el TypeError por parámetro `justificacion` faltante y el leak de conexión BD.

**Independent Test**: Editar una liquidación "En Proceso", hacer clic en "Seleccionar Incidentes", seleccionar uno o más incidentes, confirmar asociación, verificar toast de éxito y persistencia en BD.

### Implementation for User Story 1

- [X] T001 [US1] Refactorizar conexión BD sin context manager en handler `open_seleccion_incidentes_modal` en `src/presentacion_reflex/state/liquidaciones_state.py` (L1973-1998) — Cambiar `conn = dm.obtener_conexion()` por `with dm.obtener_conexion() as conn:` e indentar el bloque de código correspondiente
- [X] T002 [US1] Agregar parámetro `justificacion` faltante en llamada a `servicio.asociar_incidente()` en handler `asociar_incidentes_seleccionados` en `src/presentacion_reflex/state/liquidaciones_state.py` (L2136-2142) — Añadir `justificacion=f"Asociación desde liquidación #{id_liquidacion}"` como sexto argumento
- [ ] T003 [US1] Validación en vivo — Navegar a `/liquidaciones`, editar liquidación "En Proceso", verificar botón "Seleccionar Incidentes" visible, hacer clic, confirmar modal se abre con incidentes, seleccionar uno, asociar, verificar toast de éxito
- [ ] T004 [US1] Verificar persistencia en BD — Consultar `INCIDENTE_LIQUIDACION` para confirmar relación creada, verificar `VALOR_INCIDENTES` actualizado en `LIQUIDACIONES`, verificar cuota asociada en `CUOTA_INCIDENTE`
- [ ] T005 [US1] Verificar consola limpia — Confirmar que no hay TypeError ni errores Python en logs del servidor, ni errores JS en consola del navegador durante todo el flujo

**Checkpoint**: El flujo completo de edición → selección → asociación de incidentes funciona end-to-end ✅

---

## Phase 4: User Story 3 — Persistencia y Consistencia de Datos (Priority: P1)

**Goal**: Garantizar la integridad referencial entre frontend, backend y base de datos PostgreSQL tras la asociación de incidentes.

**Independent Test**: Asociar incidentes, recargar página, verificar que neto refleja descuentos. Reabrir modal, verificar "Ya asociado".

### Implementation for User Story 3

- [ ] T006 [US3] Verificar idempotencia — Reabrir el modal de selección de incidentes en la misma liquidación y confirmar que los incidentes ya asociados aparecen con badge "Ya asociado" y checkbox deshabilitado
- [ ] T007 [US3] Verificar recálculo de neto — Recargar la página de liquidaciones y confirmar que el campo `neto_view` de la liquidación refleja el descuento aplicado
- [ ] T008 [US3] Verificar observaciones — Abrir detalle de la liquidación y confirmar que las observaciones incluyen `Inc #<id_incidente>` como texto

**Checkpoint**: La consistencia datos UI ↔ Backend ↔ BD está garantizada ✅

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Regresión y limpieza

- [ ] T009 Prueba de regresión: Crear nueva liquidación — Verificar que el flujo de creación funciona sin errores (no debe tener botón de incidentes)
- [ ] T010 Prueba de regresión: Aprobar liquidación — Verificar que el flujo de aprobación funciona para liquidaciones "En Proceso"
- [ ] T011 Prueba de regresión: Registrar pago — Verificar que el flujo de pago funciona para liquidaciones "Aprobadas"
- [ ] T012 Prueba de regresión: Eliminar liquidación — Verificar que la eliminación de liquidaciones no pagadas funciona
- [ ] T013 Ejecutar validación quickstart.md completa — Recorrer los 5 escenarios documentados en `specs/029-fix-incident-selection-button/quickstart.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: Saltada — no aplica
- **Phase 2 (Foundational)**: Saltada — no aplica
- **Phase 3 (US1)**: Sin dependencias — inicio inmediato
  - T001 y T002 son **secuenciales** (mismo archivo, bloques diferentes)
  - T003, T004, T005 dependen de T001 + T002
- **Phase 4 (US3)**: Depende de Phase 3 completa
  - T006, T007, T008 son [P] (verificaciones independientes)
- **Phase 5 (Polish)**: Depende de Phase 4 completa
  - T009-T012 son [P] (flujos independientes)
  - T013 es secuencial (depende de todo lo anterior)

### User Story Dependencies

- **US1 (P1)**: Sin dependencias — **es el MVP**
- **US3 (P1)**: Depende de US1 completada (necesita datos para verificar)

### Within Each User Story

- Fix de código (T001-T002) → Validación en vivo (T003-T005)

### Parallel Opportunities

- T001 y T002 están en el mismo archivo pero en bloques no contiguos → se pueden aplicar con `multi_replace_file_content` en una sola operación
- T006, T007, T008 pueden verificarse en paralelo
- T009, T010, T011, T012 son pruebas de regresión independientes

---

## Parallel Example: User Story 1

```text
# Aplicar ambos fixes en una sola operación (mismo archivo, bloques distintos):
Task: T001 + T002 → multi_replace_file_content en src/presentacion_reflex/state/liquidaciones_state.py

# Validaciones en paralelo post-fix:
Task: T003 — Validación visual en navegador
Task: T004 — Verificación SQL directa
Task: T005 — Inspección de logs/consola
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Aplicar T001 + T002 (código) → ~10 líneas cambiadas
2. Ejecutar T003 (validación en vivo)
3. **STOP and VALIDATE**: Si el modal se abre y los incidentes se asocian, el MVP está completo
4. Ejecutar T004-T005 (verificación de persistencia y consola)

### Incremental Delivery

1. US1 (T001-T005) → Fix core funcional → ✅ MVP
2. US3 (T006-T008) → Consistencia validada → ✅ Producción-ready
3. Polish (T009-T013) → Sin regresiones → ✅ Release

---

## Notes

- El fix total es de ~10-15 líneas de código en 1 archivo
- No se crean archivos nuevos ni se modifican esquemas de BD
- La causa raíz es un `TypeError` por firma incompatible (parámetro `justificacion` faltante)
- El secundario es un leak potencial de conexión BD (sin `with`)
- Commit sugerido: `fix(liquidaciones): agregar justificacion faltante en asociacion de incidentes`
