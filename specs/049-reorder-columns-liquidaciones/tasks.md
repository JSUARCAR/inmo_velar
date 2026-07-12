# Tasks: Reordenar Columnas Tabla Liquidaciones

**Input**: Design documents from `/specs/049-reorder-columns-liquidaciones/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md

**Tests**: No tests requested. Validación visual y funcional en navegador.

**Organization**: Tasks grouped by user story. This is a pure UI reorder — single file modification.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: No setup required — reordering is a pure presentation change in an existing file.

*Omitted: no new infrastructure, dependencies, or project structure needed.*

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: No foundational tasks — the change is isolated to a single UI file.

*Omitted: no shared infrastructure blocking user stories.*

---

## Phase 3: User Story 1 — Análisis Financiero de Liquidaciones (Priority: P1) 🎯 MVP

**Goal**: Reordenar las 16 columnas de la tabla individual según el orden especificado, eliminando "Propiedad" y moviendo "IVA Comisión" a posición 5.

**Independent Test**: Navegar al módulo Liquidaciones y verificar que las columnas se muestran en el orden: ID → Periodo → Ciclo Operativo → Canon → IVA Comisión → Otros Ingresos → Gastos Admin → Gastos Serv → Gastos Rep → V. Incidentes → Pago Predial → Otros Egresos → Neto a Pagar → Estado Recaudo → Estado → Acciones.

### Implementation for User Story 1

- [X] T001 [US1] Reordenar headers de tabla individual en `src/presentacion_reflex/pages/liquidaciones.py` (líneas 332-349): eliminar celda "Propiedad", mover celda "IVA Comisión" después de "Canon"
- [X] T002 [US1] Reordenar body cells de tabla individual en `src/presentacion_reflex/pages/liquidaciones.py` (líneas 357-513): eliminar celda "Propiedad", mover celda "IVA Comisión" después de "Canon", asegurar que cada celda apunta al `column_id` correcto
- [X] T003 [US1] Verificar que el componente `badge_grupo_pago()` sigue renderizándose correctamente para la columna "Ciclo Operativo" después del reordenamiento

**Checkpoint**: Tabla individual muestra 16 columnas en el orden exacto especificado. "Propiedad" ya no es visible.

---

## Phase 4: User Story 2 — Funcionalidades de Tabla No Afectadas (Priority: P1)

**Goal**: Asegurar que ordenamiento, búsqueda, filtros, paginación y exportación continúan funcionando correctamente después del reordenamiento.

**Independent Test**: Ejecutar cada funcionalidad (ordenamiento por encabezado, búsqueda rápida, filtros avanzados, paginación, exportación PDF) y confirmar que operan sin errores.

### Implementation for User Story 2

- [X] T004 [US2] Verificar que `sort_by` / `sort_order` en `LiquidacionesState` sigue mapeando correctamente a los `column_id` de las columnas reordenadas en `src/presentacion_reflex/state/liquidaciones_state.py`
- [X] T005 [US2] Verificar que `header_cell_sortable()` en `src/presentacion_reflex/pages/liquidaciones.py` sigue funcionando con los `column_id` de las columnas reordenadas
- [X] T006 [US2] Verificar que `fin_column_options` en `src/presentacion_reflex/state/liquidaciones_state.py` sigue mapeando correctamente a los campos de la tabla
- [X] T007 [US2] Verificar que la exportación PDF (`PDFState.generar_estado_cuenta_elite()`) no se ve afectada por el reordenamiento de columnas de la tabla UI

**Checkpoint**: Todas las funcionalidades de tabla operan correctamente. Sin regresiones funcionales.

---

## Phase 5: User Story 3 — Responsividad y Legibilidad (Priority: P2)

**Goal**: Asegurar que la tabla es legible y usable en diferentes resoluciones sin solapamientos ni truncamientos innecesarios.

**Independent Test**: Ajustar ventana a 1920px y 1280px, verificar legibilidad y scroll horizontal.

### Implementation for User Story 3

- [X] T008 [US3] Reordenar headers de tabla agrupada en `src/presentacion_reflex/pages/liquidaciones.py` (líneas 528-545): mover "Total IVA Com." después de "Canon Total" para alinearse con el patrón ingresos → egresos → neto
- [X] T009 [US3] Reordenar body cells de tabla agrupada en `src/presentacion_reflex/pages/liquidaciones.py` (líneas 551-693): mover celda "Total IVA Com." después de "Canon Total"
- [X] T010 [US3] Verificar que la alineación y espaciado de columnas es correcta en resolución 1920px (todas las columnas visibles o con scroll mínimo)
- [X] T011 [US3] Verificar que el scroll horizontal funciona correctamente en resolución 1280px y que la columna "Acciones" es accesible al final

**Checkpoint**: Ambas vistas (individual y agrupada) muestran columnas en el orden correcto. Legibilidad verificada en múltiples resoluciones.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Validación final y limpieza

- [X] T012 Ejecutar validación completa según `specs/049-reorder-columns-liquidaciones/quickstart.md` — todos los escenarios V1-V9
- [X] T013 Verificar consola del navegador limpia durante interacción con tabla reorganizada
- [X] T014 Verificar que no se han introducido imports, variables o código muerto tras el reordenamiento

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Omitted — no setup needed
- **Foundational (Phase 2)**: Omitted — no foundational tasks
- **US1 (Phase 3)**: Can start immediately — no dependencies
- **US2 (Phase 4)**: Depends on US1 completion (T001-T003) — verifies no regresions after reorder
- **US3 (Phase 5)**: Depends on US1 completion (T001-T003) — adds agrupada reorder + responsiveness check
- **Polish (Phase 6)**: Depends on US1, US2, US3 completion

### User Story Dependencies

- **US1 (P1)**: No dependencies — the core reorder work
- **US2 (P1)**: Depends on US1 — verifies functionalities after reorder
- **US3 (P2)**: Depends on US1 — extends reorder to agrupada table + responsiveness

### Parallel Opportunities

- T004, T005, T006, T007 (US2 verification tasks) can run in parallel — all are independent verification checks
- T010, T011 (US3 responsiveness checks) can run in parallel — different resolution checks

---

## Parallel Example: User Story 2

```bash
# Launch all US2 verification tasks together:
Task: "Verificar sort_by/sort_order mapping en liquidaciones_state.py"
Task: "Verificar header_cell_sortable() con column_id reordenados"
Task: "Verificar fin_column_options mapping"
Task: "Verificar exportación PDF no afectada"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete T001-T003 (reorder individual table)
2. **STOP and VALIDATE**: Navegar a Liquidaciones, verificar 16 columnas en orden correcto
3. Deploy si está listo

### Incremental Delivery

1. US1 → Tabla individual reordenada → Validar visualmente → Deploy (MVP)
2. US2 → Verificar funcionalidades → Sin regresiones → Deploy
3. US3 → Reordenar agrupada + responsiveness → Validar → Deploy
4. Polish → Validación final quickstart → Deploy final

### Single Developer Strategy

Con un solo desarrollador:
1. Completar T001-T003 (core reorder) → commit
2. Completar T004-T007 (verificar funcionalidades) → commit
3. Completar T008-T011 (agrupada + responsiveness) → commit
4. Completar T012-T014 (validación final) → commit

---

## Notes

- [P] tasks = different files or independent verification checks
- [Story] label maps task to specific user story for traceability
- All tasks are in `src/presentacion_reflex/pages/liquidaciones.py` except verification tasks that check other files
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- This is a pure UI reorder — no backend, database, or state changes required
