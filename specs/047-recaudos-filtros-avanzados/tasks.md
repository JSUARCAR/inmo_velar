# Tasks: Filtros Avanzados Recaudos - Pago Contrato y Ciclo Operativo

**Input**: Design documents from `/specs/047-recaudos-filtros-avanzados/`

**Prerequisites**: plan.md, spec.md, data-model.md, contracts/, research.md, quickstart.md

**Tests**: No se incluyen tasks de testing explícito. La validación se realiza por inspección visual y pruebas funcionales manuales según quickstart.md.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3, US4)

---

## Phase 1: Foundational (Bloqueante para ambos filtros)

**Purpose**: Actualizar la interfaz de filtros del dominio y el servicio para soportar multi-select. Ambos filtros (Pago Contrato y Ciclo Operativo) dependen de esta base.

- [ ] T001 Actualizar `FiltrosRecaudo` en `src/dominio/interfaces/repositorio_recaudo.py`: cambiar `dia_pago: Optional[str]` a `dia_pago: Optional[List[str]]` y agregar `ciclo_operativo: Optional[List[str]] = None`
- [ ] T002 [P] Actualizar firma de `listar_paginado` y `contar_con_filtros` en `src/dominio/interfaces/repositorio_recaudo.py` para aceptar los nuevos tipos `Optional[List[str]]`
- [ ] T003 Actualizar `servicio_recaudo.py` en `src/aplicacion/servicios/servicio_recaudo.py` para pasar parámetros `dia_pago` y `ciclo_operativo` como `List[str]` al repositorio

**Checkpoint**: Interfaz de dominio y servicio listas para soportar multi-select en ambos filtros

---

## Phase 2: User Story 1 - Filtro Pago Contrato (Priority: P1) 🎯 MVP

**Goal**: Filtrar recaudos por día de pago numérico del contrato con selección múltiple OR

**Independent Test**: Abrir módulo Recaudos, seleccionar días de pago en el filtro, verificar que la tabla muestra solo registros correspondientes

### Implementation for User Story 1

- [ ] T004 [US1] Actualizar `contar_con_filtros` en `src/infraestructura/persistencia/repositorio_recaudo.py`: reemplazar filtro `dia_pago` single-value por cláusula `IN (...)` con `COALESCE(NULLIF(ca.FECHA_PAGO, ''), EXTRACT(DAY FROM ca.FECHA_INICIO_CONTRATO_A::DATE)::TEXT) IN (%s, %s, ...)`
- [ ] T005 [US1] Actualizar `listar_paginado` en `src/infraestructura/persistencia/repositorio_recaudo.py`: aplicar la misma cláusula `IN (...)` para `dia_pago` en la consulta principal
- [ ] T006 [P] [US1] Actualizar `RecaudosState` en `src/presentacion_reflex/state/recaudos_state.py`: cambiar `filter_dia_pago: str = "Todos"` a `filter_dia_pago: List[str] = []`, actualizar handler `set_filter_dia_pago` para aceptar `List[str]`, actualizar `active_filter_count` para contar filtros activos
- [ ] T007 [US1] Agregar selector multi-select de "Pago Contrato" en `recaudos_toolbar()` dentro de `src/presentacion_reflex/pages/recaudos.py`: usar `rx.select` multi con opciones `dias_pago_options` (1-31), conectar a `RecaudosState.set_filter_dia_pago`
- [ ] T008 [US1] Actualizar `load_recaudos` en `src/presentacion_reflex/state/recaudos_state.py` para construir `FiltrosRecaudo` pasando `dia_pago=self.filter_dia_pago if self.filter_dia_pago else None`

**Checkpoint**: Filtro Pago Contrato funcional con multi-select OR en backend y UI

---

## Phase 3: User Story 2 - Filtro Ciclo Operativo (Priority: P1)

**Goal**: Filtrar recaudos por grupo operativo desde Liquidación de Propietarios con selección múltiple OR

**Independent Test**: Abrir módulo Recaudos, seleccionar grupos operativos en el filtro, verificar que la tabla muestra solo registros del grupo seleccionado

### Implementation for User Story 2

- [ ] T009 [US2] Agregar método `obtener_grupos_operativos` en `src/infraestructura/persistencia/repositorio_recaudo.py`: ejecutar `SELECT DISTINCT GRUPO_OPERATIVO FROM CONTRATOS_MANDATOS WHERE ESTADO_CONTRATO_M = 'ACTIVO' ORDER BY GRUPO_OPERATIVO` y retornar lista de strings formateados como "Grupo X"
- [ ] T010 [US2] Actualizar `contar_con_filtros` en `src/infraestructura/persistencia/repositorio_recaudo.py`: agregar condición `cm.GRUPO_OPERATIVO IN (%s, %s, ...)` cuando `ciclo_operativo` no esté vacío
- [ ] T011 [US2] Actualizar `listar_paginado` en `src/infraestructura/persistencia/repositorio_recaudo.py`: agregar la misma condición `IN (...)` para `ciclo_operativo` en la consulta principal
- [ ] T012 [P] [US2] Actualizar `RecaudosState` en `src/presentacion_reflex/state/recaudos_state.py`: agregar `filter_ciclo_operativo: List[str] = []`, `ciclo_operativo_options: List[str] = ["Todos"]`, handler `set_filter_ciclo_operativo`, método `load_ciclo_operativo_options` que llame al repositorio
- [ ] T013 [US2] Agregar selector multi-select de "Ciclo Operativo" en `recaudos_toolbar()` dentro de `src/presentacion_reflex/pages/recaudos.py`: usar `rx.select` multi con opciones dinámicas `ciclo_operativo_options`, conectar a `RecaudosState.set_filter_ciclo_operativo`
- [ ] T014 [US2] Actualizar `load_recaudos` en `src/presentacion_reflex/state/recaudos_state.py` para pasar `ciclo_operativo=self.filter_ciclo_operativo if self.filter_ciclo_operativo else None` al `FiltrosRecaudo`
- [ ] T015 [US2] Cargar opciones de ciclo operativo al inicializar el módulo: invocar `load_ciclo_operativo_options` en el evento `on_load` o `did_mount` de `RecaudosState`

**Checkpoint**: Filtro Ciclo Operativo funcional con opciones dinámicas, multi-select OR en backend y UI

---

## Phase 4: User Story 3 - Combinación de Filtros (Priority: P2)

**Goal**: Verificar que ambos filtros nuevos se combinan correctamente entre sí y con filtros existentes (AND inter-filtros)

**Independent Test**: Activar múltiples filtros simultáneamente y verificar que los resultados son la intersección correcta

### Implementation for User Story 3

- [ ] T016 [US3] Verificar composición AND en `repositorio_recaudo.py`: asegurar que las condiciones de `dia_pago`, `ciclo_operativo`, `estado`, `fecha_desde`, `fecha_hasta` y `busqueda` se unen con `AND` en la cláusula `WHERE`
- [ ] T017 [US3] Verificar que `active_filter_count` en `recaudos_state.py` cuenta correctamente ambos filtros nuevos como filtros activos cuando tienen valores seleccionados

**Checkpoint**: Combinación de filtros funcionando correctamente con AND inter-filtros

---

## Phase 5: User Story 4 - Experiencia de Usuario Consistente (Priority: P2)

**Goal**: Los nuevos filtros tienen la misma apariencia, comportamiento y patrón de interacción que los filtros existentes

**Independent Test**: Verificar visualmente que los nuevos filtros son indistinguibles de los existentes en estilo y comportamiento

### Implementation for User Story 4

- [ ] T018 [P] [US4] Verificar que los selectores multi-select de ambos filtros usan `styles.NEU_FILTER_SELECT_STYLE` y `styles.NEU_FILTER_LABEL_STYLE` en `recaudos.py`
- [ ] T019 [P] [US4] Verificar que el ancho de los nuevos filtros es consistente con los filtros existentes en `recaudos_toolbar()` (mismo patrón `width=["100%", "100%", "150px"]` o equivalente)
- [ ] T020 [US4] Verificar que el comportamiento de limpieza de filtros (seleccionar "Todos" o deseleccionar todo) resetea el filtro y recarga los datos correctamente

**Checkpoint**: UX visualmente consistente con filtros existentes

---

## Phase 6: Polish & Cross-Cutting

**Purpose**: Validación final, rendimiento y limpieza

- [ ] T021 Ejecutar escenarios de validación de `quickstart.md` (ESC-01 a ESC-09) y verificar que todos pasan
- [ ] T022 [P] Verificar que no hay regresiones en funcionalidad existente: paginación, ordenamiento, búsqueda, filtros previos
- [ ] T023 [P] Verificar que las consultas SQL generadas usan `%s` placeholders (no `?`) y siguen el patrón de la constitución
- [ ] T024 Verificar rendimiento: combinación de múltiples filtros responde en <5 segundos

---

## Dependencies & Execution Order

### Phase Dependencies

- **Foundational (Phase 1)**: Sin dependencias - iniciar inmediatamente
- **US1 (Phase 2)**: Depende de Phase 1 completion
- **US2 (Phase 3)**: Depende de Phase 1 completion (puede correr en paralelo con US1)
- **US3 (Phase 4)**: Depende de US1 y US2 completion
- **US4 (Phase 5)**: Depende de US1 y US2 completion (puede correr en paralelo con US3)
- **Polish (Phase 6)**: Depende de todas las user stories completas

### User Story Dependencies

- **US1 (Pago Contrato)**: Depende solo de Phase 1. Independiente de US2.
- **US2 (Ciclo Operativo)**: Depende solo de Phase 1. Independiente de US1.
- **US3 (Combinación)**: Depende de US1 + US2 (verifica interacción entre ambos).
- **US4 (UX)**: Depende de US1 + US2 (verifica apariencia de ambos).

### Parallel Opportunities

- T001 y T002 pueden correr en paralelo (diferentes partes del mismo archivo)
- T006 y T012 pueden correr en paralelo (diferentes variables del mismo state)
- US1 (Phase 2) y US2 (Phase 3) pueden correr en paralelo si hay capacidad
- T018, T019, T022, T023 pueden correr en paralelo (verificaciones independientes)

---

## Parallel Example: User Story 1 + User Story 2

```bash
# Una vez completada Phase 1, lanzar ambas user stories en paralelo:

# US1 - Pago Contrato:
Task T004: "Actualizar contar_con_filtros para dia_pago IN (...) en repositorio_recaudo.py"
Task T005: "Actualizar listar_paginado para dia_pago IN (...) en repositorio_recaudo.py"
Task T006: "Actualizar RecaudosState filter_dia_pago a List[str]"
Task T007: "Agregar selector multi-select Pago Contrato en recaudos.py"
Task T008: "Actualizar load_recaudos para pasar dia_pago como List[str]"

# US2 - Ciclo Operativo (en paralelo):
Task T009: "Agregar obtener_grupos_operativos en repositorio_recaudo.py"
Task T010: "Actualizar contar_con_filtros para ciclo_operativo IN (...)"
Task T011: "Actualizar listar_paginado para ciclo_operativo IN (...)"
Task T012: "Agregar filter_ciclo_operativo y handler en RecaudosState"
Task T013: "Agregar selector multi-select Ciclo Operativo en recaudos.py"
Task T014: "Actualizar load_recaudos para pasar ciclo_operativo"
Task T015: "Cargar opciones ciclo operativo al inicializar módulo"
```

---

## Implementation Strategy

### MVP First (US1 Only)

1. Completar Phase 1: Foundational
2. Completar Phase 2: User Story 1 (Pago Contrato)
3. **PARAR Y VALIDAR**: Probar filtro Pago Contrato independientemente
4. Desplegar si está listo

### Incremental Delivery

1. Phase 1 → Foundation lista
2. Phase 2 → Filtro Pago Contrato funcional → Validar → Entregar (MVP)
3. Phase 3 → Filtro Ciclo Operativo funcional → Validar → Entregar
4. Phase 4 → Combinación verificada
5. Phase 5 → UX consistente verificada
6. Phase 6 → Polish y validación final

---

## Notes

- [P] tasks = archivos diferentes, sin dependencias entre sí
- [Story] label mapea cada task a su user story para trazabilidad
- Cada user story debe ser completable y testeable independientemente
- Commit después de cada task o grupo lógico
- Detenerse en cualquier checkpoint para validar la story independientemente
- El filtro Pago Contrato ya tiene `filter_dia_pago` y `dias_pago_options` definidos en state; solo necesita upgrade a multi-select y conexión a UI
