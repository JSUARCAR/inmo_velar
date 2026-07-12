# Tasks: Agregar Columna MONTO COMISIÓN a Liquidaciones

**Input**: Design documents from `/specs/001-add-monto-comision-column/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md

**Tests**: No se generan tasks de testing (no solicitados en la spec).

**Organization**: Tasks agrupados por user story para implementación y testing independiente.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Ejecutable en paralelo (diferentes archivos, sin dependencias)
- **[Story]**: User story a la que pertenece (US1, US2, US3)
- Incluye rutas exactas de archivo en las descripciones

---

## Phase 1: Foundational (Cambios en Persistencia y Estado)

**Purpose**: Exponer los campos `COMISION_MONTO` y `COMISION_PORCENTAJE` desde la BD hacia el estado de la UI. Estos cambios son prerrequisito bloqueante para TODAS las user stories.

**⚠️ CRITICAL**: Ninguna user story puede implementarse hasta completar esta fase.

- [X] T001 [P] Agregar `l.COMISION_MONTO` y `l.COMISION_PORCENTAJE` al SELECT del query `listar_paginado` en `src/infraestructura/persistencia/repositorio_liquidacion_postgres.py` (líneas 1601-1766)
- [X] T002 [P] Agregar `"comision_monto"` a la whitelist de `SORT_COLUMNS` en el método `listar_paginado` en `src/infraestructura/persistencia/repositorio_liquidacion_postgres.py`
- [X] T003 [P] Agregar `SUM(l.COMISION_MONTO) AS comision_monto` al SELECT del query `listar_agrupadas_por_propietario_paginado` en `src/infraestructura/persistencia/repositorio_liquidacion_postgres.py` (líneas 889-1117)
- [X] T004 [P] Agregar `"comision_monto"` a la whitelist de columnas ordenables en `listar_agrupadas_por_propietario_paginado`
- [X] T005 Agregar campos `comision_monto: float`, `comision_monto_view: str`, `comision_porcentaje: float` al Pydantic model `LiquidacionDict` en `src/presentacion_reflex/state/liquidaciones_state.py` (líneas 12-48)
- [X] T006 Agregar formateo de `comision_monto` con `format_currency()` y cálculo de `comision_porcentaje` en el método `load_liquidaciones` en `src/presentacion_reflex/state/liquidaciones_state.py` (líneas 309-404)

**Checkpoint**: Datos de comisión disponibles en el estado de la UI. Las user stories pueden comenzar.

---

## Phase 2: User Story 1 - Visualizar MONTO COMISIÓN en tabla (Priority: P1) 🎯 MVP

**Goal**: El usuario puede ver la columna "Monto Comisión" en la tabla de liquidaciones individual, posicionada entre Canon e IVA Comisión, con formateo COP y ordenamiento.

**Independent Test**: Navegar a `/liquidaciones`, verificar columna visible entre Canon e IVA Comisión, formateo `$X.XXX.XXX`, ordenamiento asc/desc.

### Implementation for User Story 1

- [X] T007 [US1] Agregar header cell "Monto Comisión" con sort_key `"comision_monto"` en `liquidaciones_table` en `src/presentacion_reflex/pages/liquidaciones.py` (después de Canon, antes de IVA Comisión)
- [X] T008 [US1] Agregar celda de datos `comision_monto_view` con `text_align="right"` en el body de `liquidaciones_table` en `src/presentacion_reflex/pages/liquidaciones.py`
- [X] T009 [US1] Agregar header cell "Monto Comisión" con sort_key `"comision_monto"` en `liquidaciones_table_agrupada` en `src/presentacion_reflex/pages/liquidaciones.py` (después de Canon Total)
- [X] T010 [US1] Agregar celda de datos `comision_monto_view` con `text_align="right"` en el body de `liquidaciones_table_agrupada`

**Checkpoint**: User Story 1 funcional. Columna visible y ordenable en ambas vistas de tabla.

---

## Phase 3: User Story 2 - Verificar NETO A PAGAR con MONTO COMISIÓN (Priority: P2)

**Goal**: Verificar que el NETO A PAGAR ya incorpora el MONTO COMISIÓN como egreso. Este cálculo ya existe en el entity `Liquidacion.calcular_totales()`. Solo requiere verificación visual.

**Independent Test**: Comparar el NETO A PAGAR mostrado con el cálculo manual que incluye la resta de `comision_monto`.

### Implementation for User Story 2

- [X] T011 [US2] Verificar que el query `listar_paginado` retorna `neto` calculado correctamente incluyendo `comision_monto` como egreso (sin cambios en código, solo validación)
- [X] T012 [US2] Verificar en la UI que el valor de `neto_view` coincide con el cálculo `total_ingresos - total_egresos - comision_monto` para al menos 3 registros de prueba

**Checkpoint**: User Story 2 verificada. NETO A PAGAR refleja correctamente el descuento de comisión.

---

## Phase 4: User Story 3 - Tooltip con porcentaje de comisión (Priority: P3)

**Goal**: El usuario puede ver el porcentaje de comisión aplicado al pasar el cursor sobre la columna MONTO COMISIÓN.

**Independent Test**: Pasar cursor sobre celda de MONTO COMISIÓN, verificar tooltip muestra "XX.XX% sobre canon".

### Implementation for User Story 3

- [X] T013 [US3] Envolver celda de `comision_monto_view` en `rx.tooltip` con texto `f"{comision_porcentaje:.2f}% sobre canon"` en `liquidaciones_table` en `src/presentacion_reflex/pages/liquidaciones.py`
- [X] T014 [US3] Envolver celda de `comision_monto_view` en `rx.tooltip` con texto `f"{comision_porcentaje:.2f}% sobre canon"` en `liquidaciones_table_agrupada`

**Checkpoint**: User Story 3 funcional. Tooltip visible al pasar cursor.

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Mejoras que afectan múltiples user stories

- [X] T015 Envolver tabla en contenedor con `overflow_x="auto"` para soportar scroll horizontal en `src/presentacion_reflex/pages/liquidaciones.py`
- [X] T016 Ejecutar `reflex run --env dev` y verificar que la tabla carga sin errores en consola
- [X] T017 Verificar que no hay regresiones en columnas existentes (formato, orden, acciones)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Foundational (Phase 1)**: Sin dependencias - puede iniciar inmediatamente
- **User Story 1 (Phase 2)**: Depende de Foundational (Phase 1)
- **User Story 2 (Phase 3)**: Depende de Foundational (Phase 1) - verificación visual
- **User Story 3 (Phase 4)**: Depende de Foundational (Phase 1) + US1 (Phase 2)
- **Polish (Phase 5)**: Depende de US1 completa

### User Story Dependencies

- **User Story 1 (P1)**: Puede iniciar después de Phase 1 - Sin dependencias en otras stories
- **User Story 2 (P2)**: Puede iniciar después de Phase 1 - Solo verificación, no requiere US1
- **User Story 3 (P3)**: Requiere US1 completa (necesita la celda existente para envolver en tooltip)

### Parallel Opportunities

- T001-T004: Todos paralelos (diferentes métodos en mismo archivo, pero queries independientes)
- T007-T010: Paralelos entre vistas individual y agrupada
- T013-T014: Paralelos entre vistas individual y agrupada

---

## Parallel Example: Foundational Phase

```bash
# Launch all repository changes together:
Task: "T001 Agregar COMISION_MONTO al SELECT de listar_paginado"
Task: "T002 Agregar comision_monto a SORT_COLUMNS"
Task: "T003 Agregar SUM(COMISION_MONTO) a listar_agrupadas"
Task: "T004 Agregar comision_monto a sort whitelist agrupadas"

# Launch state model changes:
Task: "T005 Agregar campos a LiquidacionDict"
Task: "T006 Agregar formateo en load_liquidaciones"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Completar Phase 1: Foundational (T001-T006)
2. Completar Phase 2: User Story 1 (T007-T010)
3. **PARAR y VALIDAR**: Verificar columna visible y ordenable
4. Desplegar/demo si está listo

### Incremental Delivery

1. Foundational → Datos disponibles en UI
2. US1 → Columna visible → Deploy/Demo (MVP!)
3. US2 → Verificación de cálculo → Deploy/Demo
4. US3 → Tooltip → Deploy/Demo
5. Polish → Scroll horizontal → Deploy/Demo

---

## Notes

- [P] tasks = diferentes archivos/métodos, sin dependencias entre sí
- [Story] label vincula cada task a su user story para trazabilidad
- Cada user story debe ser completable y testeable independientemente
- Commit después de cada task o grupo lógico
- El campo `COMISION_MONTO` ya existe en BD - NO se requiere migración
- `format_currency()` ya existe en `utils/formatters.py` - NO se requiere crear
- El cálculo del NETO A PAGAR ya incluye `comision_monto` - solo se verifica
