# Tasks: Recaudos - Filtros Avanzados y Ordenamiento de Tabla

**Input**: Design documents from `/specs/015-recaudos-filtros-sort/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, quickstart.md

**Tests**: No se solicitan tests explícitos en la especificación.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Foundational (Verificación de Infraestructura Existente)

**Purpose**: Validar que la infraestructura de filtros, sorting y componentes reutilizables está completa y funcional antes de implementar cambios de UI.

**⚠️ CRITICAL**: No se puede comenzar trabajo de UI hasta que esta fase esté completa.

- [x] T001 Verificar que `RecaudosState.filter_contrato` existe como variable de estado y tiene setter en `src/presentacion_reflex/state/recaudos_state.py`
- [x] T002 Verificar que `FiltrosRecaudo.id_contrato` acepta el campo de contrato en `src/infraestructura/persistencia/repositorio_recaudo.py`
- [x] T003 [P] Verificar que `SORT_COLUMNS` en `src/infraestructura/persistencia/repositorio_recaudo.py` cubre las 8 columnas ordenables (id_recaudo, fecha_pago, fecha_pago_contrato, valor_total, estado, arrendatario, habitante, direccion)
- [x] T004 [P] Verificar que `toggle_sort()` en `src/presentacion_reflex/state/recaudos_state.py` alterna correctamente entre asc/desc y resetea página
- [x] T005 [P] Verificar que `load_filter_options()` en `src/presentacion_reflex/state/recaudos_state.py` carga `contratos_options` y `contratos_select_options` desde la base de datos
- [x] T006 Verificar que `neuro_select_root`, `neuro_input`, `neuro_button` están disponibles en `src/presentacion_reflex/components/neuro_elements.py`

**Checkpoint**: Infraestructura verificada — se puede comenzar implementación de UI.

---

## Phase 2: User Story 1 - Filtro de Pago Contrato (Priority: P1) 🎯 MVP

**Goal**: Incorporar un filtro "Pago Contrato" tipo dropdown (`neuro_select_root`) en la toolbar de Recaudos, cargado desde la base de datos, que filtre la tabla al seleccionar un contrato.

**Independent Test**: Navegar a `/recaudos`, seleccionar un contrato en el dropdown "Pago Contrato", verificar que la tabla muestra solo recaudos de ese contrato.

### Implementation for User Story 1

- [x] T007 [US1] Agregar filtro "Pago Contrato" (`neuro_select_root`) en `recaudos_toolbar()` dentro de `src/presentacion_reflex/pages/recaudos.py` — usar `rx.foreach` sobre `RecaudosState.contratos_select_options` para generar las opciones, con `on_change=RecaudosState.set_filter_contrato`, placeholder "Pago Contrato", width `["100%", "100%", "180px"]`
- [x] T008 [US1] Verificar que `set_filter_contrato` en `src/presentacion_reflex/state/recaudos_state.py` resetea `current_page = 1` y retorna `RecaudosState.load_recaudos` (patrón existente)
- [x] T009 [US1] Validar que el filtro Pago Contrato se mantiene al cambiar otros filtros y al ordenar la tabla

**Checkpoint**: Filtro Pago Contrato funcional y probado independientemente.

---

## Phase 3: User Story 2 - Filtro de Estado (Priority: P1)

**Goal**: Validar que el filtro "Estado" existente funciona correctamente con las opciones: Todos, Pendiente, Vencido, Aplicado, Reversado.

**Independent Test**: Seleccionar cada estado en el dropdown y verificar que la tabla filtra correctamente.

### Implementation for User Story 2

- [x] T010 [US2] Verificar que las opciones del filtro Estado en `recaudos_toolbar()` en `src/presentacion_reflex/pages/recaudos.py` incluyen: Todos, Pendiente, Vencido, Aplicado, Reversado
- [x] T011 [US2] Verificar que `set_filter_estado` en `src/presentacion_reflex/state/recaudos_state.py` resetea `current_page = 1` y retorna `RecaudosState.load_recaudos`
- [x] T012 [US2] Probar filtrado por cada estado individual y verificar resultados en la tabla

**Checkpoint**: Filtro Estado validado y funcional.

---

## Phase 4: User Story 3 - Homologación Visual con Liquidaciones (Priority: P2)

**Goal**: Reorganizar la toolbar de Recaudos para que tenga la misma distribución visual que Liquidaciones (2 grupos: filtros + acciones), agregar botón de limpiar filtros y componente de empty state.

**Independent Test**: Comparar visualmente la toolbar de Recaudos con Liquidaciones y verificar que la distribución, componentes y comportamiento son consistentes.

### Implementation for User Story 3

- [x] T013 [US3] Reorganizar `recaudos_toolbar()` en `src/presentacion_reflex/pages/recaudos.py` — separar en 2 grupos: (1) `rx.flex` con filtros (Search, Pago Contrato, Estado, Fecha Desde, Fecha Hasta) con `gap="5"`, `align="center"`, `flex_wrap="wrap"`; (2) `rx.hstack` con acciones (Registrar Pago, Pagos Masivos, Refresh, Exportar) con `spacing="5"`, `align="center"`, `wrap="wrap"`
- [x] T014 [US3] Agregar botón "Limpiar Filtros" (`neuro_button` con icono "x" o "filter-x") en el grupo de acciones de `recaudos_toolbar()` en `src/presentacion_reflex/pages/recaudos.py`, con `on_click=RecaudosState.clear_filters`
- [x] T015 [US3] Implementar handler `clear_filters()` en `src/presentacion_reflex/state/recaudos_state.py` que restablezca: `search_text=""`, `filter_estado="Todos"`, `filter_contrato=""`, `filter_fecha_desde=""`, `filter_fecha_hasta=""`, `sort_by="fecha_pago"`, `sort_order="desc"`, `current_page=1`, y retorne `RecaudosState.load_recaudos`
- [x] T016 [US3] Agregar componente de empty state (`rx.callout` con icono "search" y mensaje "No se encontraron recaudos") en `recaudos_table()` dentro de `src/presentacion_reflex/pages/recaudos.py`, visible cuando `RecaudosState.recaudos` está vacío y `RecaudosState.is_loading` es False
- [x] T017 [US3] Ajustar estilos de la toolbar de Recaudos para coincidir con Liquidaciones: `padding="1em"`, `background=styles.BG_PANEL`, `border_radius="16px"`, `style={"box_shadow": styles.NEU_SHADOW}`, `gap="6"`, `flex_direction="row"`, `flex_wrap="wrap"`

**Checkpoint**: Toolbar homologada visualmente con Liquidaciones, botón de limpiar filtros y empty state funcionales.

---

## Phase 5: User Story 4 - Ordenamiento de la Tabla (Priority: P2)

**Goal**: Validar que el ordenamiento de la tabla funciona correctamente en todas las columnas aplicables (8 columnas, excluyendo "Método de Pago" y "Acciones").

**Independent Test**: Hacer clic en cada encabezado de columna y verificar que los datos se reorganizan ascendente/descendente, manteniendo filtros y paginación.

### Implementation for User Story 4

- [x] T018 [US4] Verificar que `header_cell_sortable()` en `src/presentacion_reflex/pages/recaudos.py` renderiza correctamente los iconos de sort (chevron-down, chevron-up, chevrons-up-down) para las 8 columnas ordenables
- [x] T019 [US4] Verificar que la columna "Método de Pago" NO tiene `header_cell_sortable` — debe usar `rx.table.column_header_cell` simple sin interacción de sort
- [x] T020 [US4] Verificar que la columna "Acciones" NO tiene `header_cell_sortable` — debe usar `rx.table.column_header_cell` simple sin interacción de sort
- [x] T021 [US4] Probar sort en columnas de tipo fecha (fecha_pago, fecha_pago_contrato) — verificar orden cronológico
- [x] T022 [US4] Probar sort en columnas de tipo numérico (valor_total, id_recaudo) — verificar orden numérico (no lexicográfico)
- [x] T023 [US4] Probar sort en columnas de tipo texto (direccion, arrendatario, habitante, estado) — verificar orden alfabético case-insensitive
- [x] T024 [US4] Verificar que cambiar filtro mantiene el sort activo; verificar que navegar páginas mantiene el sort activo

**Checkpoint**: Ordenamiento funcional en todas las columnas aplicables, con persistencia de filtros y paginación.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Validación final, limpieza y verificación de regresión.

- [x] T025 Ejecutar escenarios de validación de `quickstart.md` (9 escenarios)
- [x] T026 [P] Verificar que no hay errores en consola del navegador al interactuar con filtros y sort
- [x] T027 [P] Verificar responsive behavior — en viewport móvil (<768px), los filtros deben apilar verticalmente
- [x] T028 Verificar que crear/editar/eliminar recaudos no se afectó (regresión)
- [x] T029 Verificar que los botones de acción (Aplicar Pago, Reversar Pago, PDF) siguen funcionando
- [x] T030 Ejecutar linting: `ruff check src/presentacion_reflex/pages/recaudos.py src/presentacion_reflex/state/recaudos_state.py`
- [x] T031 Ejecutar type checking: `mypy src/presentacion_reflex/pages/recaudos.py src/presentacion_reflex/state/recaudos_state.py`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Foundational (Phase 1)**: No dependencies — can start immediately
- **US1 (Phase 2)**: Depends on Phase 1 completion
- **US2 (Phase 3)**: Depends on Phase 1 completion (independiente de US1)
- **US3 (Phase 4)**: Depende de US1 y US2 (agrega components sobre los filtros existentes)
- **US4 (Phase 5)**: Depende de Phase 1 (validación de sort existente)
- **Polish (Phase 6)**: Depende de todas las user stories completas

### User Story Dependencies

- **US1 (Filtro Pago Contrato, P1)**: Solo depende de Foundational
- **US2 (Filtro Estado, P1)**: Solo depende de Foundational (validación, sin cambios de UI)
- **US3 (Homologación Visual, P2)**: Depende de US1 (necesita el filtro Pago Contrato en la toolbar para reorganizar)
- **US4 (Ordenamiento, P2)**: Solo depende de Foundational (validación del sort existente)

### Within Each User Story

- Verificar infraestructura antes de implementar UI
- Implementar componente UI → Verificar handler en State → Validar integración

### Parallel Opportunities

- T003, T004, T005, T006 pueden ejecutarse en paralelo (verificaciones independientes)
- US1 y US2 pueden ejecutarse en paralelo (diferentes filtros, sin dependencia cruzada)
- T026, T027 pueden ejecutarse en paralelo (validaciones independientes)

---

## Parallel Example: User Story 1

```bash
# Verificaciones Fundacionales (paralelo):
Task: "Verificar FiltrosRecaudo.id_contrato en repositorio_recaudo.py"
Task: "Verificar SORT_COLUMNS en repositorio_recaudo.py"
Task: "Verificar toggle_sort() en recaudos_state.py"
Task: "Verificar load_filter_options() en recaudos_state.py"

# Implementación US1:
Task: "Agregar filtro Pago Contrato en recaudos_toolbar() — recaudos.py"
Task: "Verificar set_filter_contrato handler — recaudos_state.py"
```

---

## Implementation Strategy

### MVP First (US1 + US2 Only)

1. Completar Phase 1: Foundational (verificar infraestructura)
2. Completar Phase 2: US1 — Filtro Pago Contrato
3. Completar Phase 3: US2 — Validar Filtro Estado
4. **PARAR y VALIDAR**: Probar filtros funcionalmente
5. Desplegar/demo si está listo

### Incremental Delivery

1. Foundational → Infraestructura verificada
2. US1 + US2 → Filtros funcionales → Desplegar/Demo (MVP!)
3. US3 → Toolbar homologada + limpiar filtros + empty state → Desplegar/Demo
4. US4 → Ordenamiento validado → Desplegar/Demo
5. Polish → Validación final → Release

### Parallel Team Strategy

Con múltiples desarrolladores:

1. Equipo completa Foundational juntos
2. Una vez completado:
   - Dev A: US1 (Filtro Pago Contrato)
   - Dev B: US2 (Validar Filtro Estado) + US4 (Validar Sort)
3. US1 y US2 completos → Dev A comienza US3 (Homologación)
4. Todo completo → Polish juntos

---

## Notes

- [P] tasks = diferentes archivos, sin dependencias
- [Story] label vincula tarea con user story para trazabilidad
- Cada user story debe ser completable y testeable independientemente
- Commit después de cada tarea o grupo lógico
- Parar en cualquier checkpoint para validar la story independientemente
- Solo se modifican 2 archivos: `recaudos.py` y `recaudos_state.py`
- No hay cambios en backend (servicios, repositorios, DTOs)

---

## Convergencia

**Fecha**: 2026-07-05

| Requisito | Estado |
|-----------|--------|
| F1.1 - Pago Contrato filter (neuro_select_root) | ✅ |
| F1.2 - Filtros en grupo flex (homologado) | ✅ |
| F1.3 - Botón Limpiar Filtros | ✅ |
| F2.1 - handler set_filter_contrato() | ✅ |
| F2.2 - load_recaudos() pasa id_contrato | ✅ |
| F2.3 - clear_filters() resetea todo | ✅ |
| F3.1 - callout "No se encontraron recaudos" | ✅ |
| F4.1 - 8 columnas ordenables | ✅ |
| F4.2 - Método y Acciones NO ordenables | ✅ |
| F4.3 - toggle_sort() funcional | ✅ |
| F5.1 - Búsqueda con Enter | ✅ |
| F5.2 - Paginación funcional | ✅ |

**Resultado**: CONVERGED - Todos los requisitos implementados. No se requieren tasks adicionales.
