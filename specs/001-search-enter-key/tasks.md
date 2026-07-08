# Tasks: Búsqueda con Tecla ENTER

**Input**: Design documents from `/specs/001-search-enter-key/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: No se incluyen tasks de testing automatizado (no solicitado en spec). Validación manual via quickstart.md.

**Organization**: Tasks agrupados por user story para implementación y testing independiente.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Parallelizable (different files, no dependencies)
- **[Story]**: User story label (US1, US2, US3)
- File paths exactos en descripciones

---

## Phase 1: Setup (Componente Compartido)

**Purpose**: Modificar `advanced_filter_bar` para aceptar `on_key_down`. PREREQUISITO para todos los módulos.

- [X] T001 Agregar parámetro `on_key_down: Callable = None` a la firma de `advanced_filter_bar` en `src/presentacion_reflex/components/shared/advanced_filter_bar.py`
- [X] T002 Modificar la construcción de `rx.input` dentro de `advanced_filter_bar` para pasar `on_key_down` cuando no sea `None` (usar diccionario de props condicional)
- [X] T003 Verificar que `advanced_filter_bar` sin `on_key_down` sigue funcionando igual (backward-compatible)

**Checkpoint**: Componente compartido actualizado. Todos los módulos que usan `advanced_filter_bar` pueden ahora pasar `on_key_down`.

---

## Phase 2: User Story 1 - Búsqueda con ENTER en Personas (Priority: P1) MVP

**Goal**: El módulo de Personas ejecuta la búsqueda al presionar ENTER, con los mismos resultados que el botón.

**Independent Test**: Navegar a `/personas`, escribir "Juan" en "Buscar", presionar ENTER, verificar resultados idénticos a los del botón.

### Implementation for User Story 1

- [X] T004 [P] [US1] Verificar que `PersonasState.handle_search_key_down` existe y es correcto en `src/presentacion_reflex/state/personas_state.py` (línea 391)
- [X] T005 [US1] Conectar `on_key_down=PersonasState.handle_search_key_down` al `advanced_filter_bar` en `src/presentacion_reflex/pages/personas.py` (línea ~367)

**Checkpoint**: Personas permite búsqueda por ENTER. MVP funcional.

---

## Phase 3: User Story 2 - Consistencia Transversal (Priority: P2)

**Goal**: Los 6 módulos restantes ejecutan la búsqueda con ENTER de forma idéntica a Personas.

**Independent Test**: Navegar a cada módulo, escribir un término, presionar ENTER, verificar búsqueda se ejecuta correctamente.

### Implementation for User Story 2

- [X] T006 [P] [US2] Agregar `search_propiedades` y `handle_search_key_down` a `PropiedadesState` en `src/presentacion_reflex/state/propiedades_state.py`
- [X] T007 [P] [US2] Agregar `search_contratos` y `handle_search_key_down` a `ContratosState` en `src/presentacion_reflex/state/contratos_state.py`
- [X] T008 [P] [US2] Agregar `handle_search_key_down` a `LiquidacionFiltrosState` en `src/presentacion_reflex/state/liquidacion_asesores/filtros_state.py`
- [X] T009 [P] [US2] Agregar `search_incidentes` y `handle_search_key_down` a `IncidentesState` en `src/presentacion_reflex/state/incidentes_state.py`
- [X] T010 [P] [US2] Verificar que `LiquidacionesState.handle_search_key_down` existe en `src/presentacion_reflex/state/liquidaciones_state.py` (línea 394)
- [X] T011 [P] [US2] Verificar que `RecaudosState.handle_search_key_down` existe en `src/presentacion_reflex/state/recaudos_state.py` (línea 251)
- [X] T012 [US2] Conectar `on_key_down` al `advanced_filter_bar` en `src/presentacion_reflex/pages/propiedades.py` (línea ~280)
- [X] T013 [US2] Conectar `on_key_down` al `advanced_filter_bar` en `src/presentacion_reflex/pages/contratos.py` (línea ~526)
- [X] T014 [US2] Conectar `on_key_down` al `advanced_filter_bar` en `src/presentacion_reflex/pages/liquidaciones.py` (línea ~132)
- [X] T015 [US2] Conectar `on_key_down` al `advanced_filter_bar` en `src/presentacion_reflex/pages/liquidacion_asesores.py` (línea ~130)
- [X] T016 [US2] Conectar `on_key_down` al `advanced_filter_bar` en `src/presentacion_reflex/pages/recaudos.py` (línea ~77)
- [X] T017 [US2] Conectar `on_key_down` al `advanced_filter_bar` en `src/presentacion_reflex/pages/incidentes.py` (línea ~60)

**Checkpoint**: Los 7 módulos permiten búsqueda por ENTER. Comportamiento uniforme verificado.

---

## Phase 4: User Story 3 - Compatibilidad con Filtros Avanzados (Priority: P3)

**Goal**: La búsqueda por ENTER respeta y combina correctamente con filtros avanzados activos.

**Independent Test**: Activar filtros avanzados en cualquier módulo, presionar ENTER, verificar que los resultados incluyen tanto el término de búsqueda como los filtros.

### Implementation for User Story 3

- [X] T018 [US3] Ejecutar pruebas manuales de combinación ENTER + filtros avanzados en Personas (estado, rol, fechas)
- [X] T019 [US3] Ejecutar pruebas manuales de combinación ENTER + filtros avanzados en Propiedades, Contratos, Liquidaciones
- [X] T020 [US3] Ejecutar pruebas manuales de combinación ENTER + filtros avanzados en Liquidación de Asesores, Recaudos, Incidentes
- [X] T021 [US3] Probar campo vacío + ENTER en todos los módulos (debe mostrar todos los registros o solo filtrados por avanzados)
- [X] T022 [US3] Probar pulsación repetida de ENTER (5 veces rápido) en al menos 3 módulos — verificar sin errores

**Checkpoint**: Compatibilidad con filtros avanzados verificada en los 7 módulos.

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Validación final, limpieza y documentación

- [X] T023 Ejecutar `check_syntax.py` para verificar ausencia de errores de sintaxis
- [X] T024 Ejecutar `ruff` y `black` para verificar formatode código
- [X] T025 Ejecutar quickstart.md validación completa (escenarios V1-V10)
- [X] T026 Verificar consola del navegador limpia (sin errores JS) en los 7 módulos
- [X] T027 Verificar logs del servidor Reflex sin errores durante pruebas de búsqueda

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Sin dependencias — inicia inmediatamente. **BLOQUEA** todos los user stories.
- **US1 (Phase 2)**: Depende de Phase 1 completa.
- **US2 (Phase 3)**: Depende de Phase 1 completa. Puede ejecutarse en paralelo con US1.
- **US3 (Phase 4)**: Depende de US1 y US2 completos (necesita todos los módulos funcionando).
- **Polish (Phase 5)**: Depende de todas las phases anteriores.

### User Story Dependencies

- **US1 (P1)**: Solo necesita Phase 1 (componente compartido). Independiente.
- **US2 (P2)**: Solo necesita Phase 1. Independiente de US1 (pero naturalmente se ejecuta después).
- **US3 (P3)**: Necesita US1 + US2 completos (validación transversal).

### Within Each User Story

- Verificación de código existente ANTES de modificar
- Modificar state ANTES de wiring en página
- Wiring en página como último paso del story

### Parallel Opportunities

- **T004** y **T005** (US1): Paralelizables (verificación vs. wiring)
- **T006-T011** (US2 states): Todos paralelizables (diferentes archivos)
- **T012-T017** (US2 pages): Todos paralelizables (diferentes archivos)

---

## Parallel Example: User Story 2

```bash
# Crear handlers en states (paralelo — diferentes archivos):
Task: "T006 Agregar handler en propiedades_state.py"
Task: "T007 Agregar handler en contratos_state.py"
Task: "T008 Agregar handler en filtros_state.py"
Task: "T009 Agregar handler en incidentes_state.py"

# Verificar handlers existentes (paralelo):
Task: "T010 Verificar handler en liquidaciones_state.py"
Task: "T011 Verificar handler en recaudos_state.py"

# Conectar wiring en pages (paralelo — diferentes archivos):
Task: "T012 Wiring en propiedades.py"
Task: "T013 Wiring en contratos.py"
Task: "T014 Wiring en liquidaciones.py"
Task: "T015 Wiring en liquidacion_asesores.py"
Task: "T016 Wiring en recaudos.py"
Task: "T017 Wiring en incidentes.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Completar Phase 1: Modificar componente compartido
2. Completar Phase 2: Wiring en Personas
3. **PARAR y VALIDAR**: Probar búsqueda por ENTER en Personas
4. Deploy/demo si está listo

### Incremental Delivery

1. Phase 1 → Componente listo
2. Phase 2 → Personas funciona → Deploy/Demo (MVP!)
3. Phase 3 → Los 7 módulos funcionan → Deploy/Demo
4. Phase 4 → Filtros avanzados validados → Deploy/Demo
5. Phase 5 → Polish completo → Release final

### Parallel Team Strategy

Con múltiples desarrolladores:

1. Team completa Phase 1 juntos
2. Una vez Phase 1 lista:
   - Developer A: US1 (Personas)
   - Developer B: US2 (los 6 módulos restantes, en paralelo)
3. Ambos completan → US3 (validación conjunta)
4. Polish final

---

## Notes

- [P] tasks = diferentes archivos, sin dependencias entre sí
- [Story] label mapea cada task al user story para trazabilidad
- Cada user story debe ser completable y testeable independientemente
- Commitear después de cada task o grupo lógico
- Detenerse en cualquier checkpoint para validar el story independientemente
