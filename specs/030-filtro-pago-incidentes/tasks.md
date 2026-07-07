# Tasks: filtro-pago-incidentes

**Input**: Design documents from `specs/030-filtro-pago-incidentes/`

**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, quickstart.md

**Tests**: No se solicitan explícitamente tests en la especificación. Se omiten tareas de test.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: No se requiere crear nueva estructura de proyecto. La infraestructura ya existe y los archivos a modificar están identificados.

- [X] T001 Verificar que el campo `estado_pago` ya existe en la entidad `IncidenteDict` en src/presentacion_reflex/state/incidentes_state.py (línea 41: `estado_pago: str = "Pendiente"`)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Crear el método de backend que extrae los estados de pago dinámicos desde PostgreSQL y exponer el parámetro `estado_pago` en la cadena de filtrado (Repositorio → Servicio).

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T002 Agregar método `obtener_estados_pago_disponibles() -> List[str]` en src/infraestructura/persistencia/repositorio_incidentes_postgres.py que ejecute `SELECT DISTINCT` sobre el estado de pago de las liquidaciones asociadas a incidentes (usando `%s` y conexiones existentes)
- [X] T003 Agregar parámetro `estado_pago: Optional[str] = None` al método `listar_con_filtros()` en src/infraestructura/persistencia/repositorio_incidentes_postgres.py y modificar la cláusula WHERE para incluir un filtro condicional con subconsulta EXISTS hacia la tabla de liquidaciones
- [X] T004 Agregar parámetro `estado_pago: Optional[str] = None` al método `listar_con_filtros()` en src/aplicacion/servicios/servicio_incidentes.py y pasarlo al repositorio
- [X] T005 Agregar método `obtener_estados_pago() -> List[str]` en src/aplicacion/servicios/servicio_incidentes.py que delegue al nuevo método del repositorio

**Checkpoint**: Backend listo para recibir el filtro de estado de pago desde la capa de presentación.

---

## Phase 3: User Story 1 - Filtrar Incidentes por Estado de Pago (Priority: P1) 🎯 MVP

**Goal**: Agregar un ComboBox "Estado de Pago del Incidente" en la sección de Filtros y conectarlo con el backend para filtrar la tabla de incidentes.

**Independent Test**: Abrir módulo Incidentes → Desplegar filtros → Seleccionar un estado de pago → Verificar que la tabla se actualice mostrando solo los incidentes con ese estado.

### Implementation for User Story 1

- [X] T006 [US1] Agregar variable de estado `filter_estado_pago: str = ""` y `estados_pago_options: List[str] = []` en la clase `IncidentesState` en src/presentacion_reflex/state/incidentes_state.py
- [X] T007 [US1] Agregar método `set_filter_estado_pago(self, value: str)` que actualice la variable y dispare `load_incidentes` en src/presentacion_reflex/state/incidentes_state.py
- [X] T008 [US1] Modificar método `on_load()` para invocar la carga de estados de pago disponibles (`yield IncidentesState.load_estados_pago()`) en src/presentacion_reflex/state/incidentes_state.py
- [X] T009 [US1] Agregar método `load_estados_pago()` como `@rx.event(background=True)` que llame a `ServicioIncidentes.obtener_estados_pago()` y actualice `estados_pago_options` en src/presentacion_reflex/state/incidentes_state.py
- [X] T010 [US1] Modificar método `load_incidentes()` para pasar `self.filter_estado_pago` (si no vacío) al servicio `listar_con_filtros(estado_pago=...)` en src/presentacion_reflex/state/incidentes_state.py
- [X] T011 [US1] Agregar un `neuro_floating_select` con label "Estado de Pago" en la función `_filter_bar()` en src/presentacion_reflex/pages/incidentes.py, usando `IncidentesState.estados_pago_options`, `IncidentesState.filter_estado_pago` y `IncidentesState.set_filter_estado_pago`

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently.

---

## Phase 4: User Story 2 - Combinar Filtro de Pago con Otros Filtros (Priority: P2)

**Goal**: Garantizar que el filtro de estado de pago se combine correctamente con los filtros existentes (prioridad, estado, búsqueda) y se mantenga consistente con paginación y ordenamiento.

**Independent Test**: Seleccionar un estado de pago Y un estado (ej. "Aprobado") → Verificar que los resultados cumplan ambas condiciones. Navegar páginas y verificar persistencia.

### Implementation for User Story 2

- [X] T012 [US2] Verificar que el parámetro `estado_pago` se propaga correctamente cuando se combina con los demás filtros (`busqueda`, `prioridad`, `estado`) en la llamada desde `load_incidentes()` en src/presentacion_reflex/state/incidentes_state.py
- [X] T013 [US2] Verificar que al cambiar de página (`prev_page`, `next_page`) o al cambiar el orden (`toggle_sort`) el filtro `filter_estado_pago` se mantiene activo y se pasa al servicio en src/presentacion_reflex/state/incidentes_state.py
- [X] T014 [US2] Verificar que el ComboBox vacío ("") no aplica filtro (comportamiento implícito) y que la limpieza del filtro restaura la vista completa, conforme al edge case documentado en spec.md

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently.

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Asegurar calidad visual, consistencia UI y validación end-to-end.

- [X] T015 [P] Verificar que el nuevo ComboBox respeta los estilos del Claude Design System (floating labels, tooltips, paddings) alineado con los demás filtros en src/presentacion_reflex/pages/incidentes.py
- [X] T016 Ejecutar la validación del quickstart.md (Escenarios 1–4) con la aplicación corriendo en `reflex run --env dev`
- [X] T017 [P] Actualizar ESTADO_TAREAS.md reflejando la nueva funcionalidad implementada

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Sin dependencias - verificación inmediata.
- **Foundational (Phase 2)**: Depende de Phase 1. T002→T003→T004→T005 en secuencia (cada uno depende del anterior).
- **User Story 1 (Phase 3)**: Depende de Phase 2 completa. T006-T007 pueden ser paralelos, T08-T11 en secuencia.
- **User Story 2 (Phase 4)**: Depende de Phase 3 (US1 funcional).
- **Polish (Phase 5)**: Depende de Phase 3 y Phase 4 completas.

### User Story Dependencies

- **User Story 1 (P1)**: Puede iniciar tras Phase 2 - Sin dependencias de otras historias.
- **User Story 2 (P2)**: Depende de US1 funcional ya que valida la integración del filtro con otros filtros.

### Within Each User Story

- State variables antes de métodos de state
- Métodos de state antes de componentes UI
- Backend (repositorio → servicio) antes de frontend (state → page)

### Parallel Opportunities

- T002 y T003 modifican el mismo archivo (repositorio) → deben ser secuenciales.
- T006 y T007 pueden desarrollarse en paralelo (variables y método setter del state).
- T015 y T017 son independientes → pueden ejecutarse en paralelo.

---

## Parallel Example: User Story 1

```bash
# Launch state variable setup tasks in parallel:
Task: "T006 - Agregar filter_estado_pago y estados_pago_options en IncidentesState"
Task: "T007 - Agregar set_filter_estado_pago en IncidentesState"

# Then sequential:
Task: "T008 - Modificar on_load para cargar estados"
Task: "T009 - Crear load_estados_pago"
Task: "T010 - Modificar load_incidentes para pasar el filtro"
Task: "T011 - Agregar ComboBox en UI"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Verificar campo `estado_pago` existente
2. Complete Phase 2: Backend (Repositorio + Servicio)
3. Complete Phase 3: User Story 1 (State + UI)
4. **STOP and VALIDATE**: Ejecutar quickstart.md Escenarios 1-3
5. Deploy/demo if ready

### Incremental Delivery

1. Phase 1 + Phase 2 → Backend listo
2. Phase 3 (US1) → Filtro funcional end-to-end → Validar MVP
3. Phase 4 (US2) → Combinación robusta con otros filtros → Validar
4. Phase 5 → Polish visual y documentación

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Archivos principales impactados: `repositorio_incidentes_postgres.py`, `servicio_incidentes.py`, `incidentes_state.py`, `incidentes.py` (page)
- El campo `estado_pago` ya existe en `IncidenteDict` (línea 41), lo que simplifica la integración
- Usar estrictamente `%s` para placeholders PostgreSQL y `RETURNING id` si aplica
- Commit after each task or logical group
