# Tasks: Rediseño Estado de Cuenta PDF Liquidaciones

**Input**: Design documents from `/specs/057-redisejo-estado-cuenta-pdf/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/template-contract.md, quickstart.md

**Tests**: No se solicitan tests explícitos en la especificación.

**Organization**: Tareas agrupadas por user story para implementación y prueba independiente.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Ejecutable en paralelo (diferentes archivos, sin dependencias)
- **[Story]**: User story a la que pertenece la tarea (US1, US2, US3, US4, US5)
- Incluir rutas exactas de archivo en las descripciones

---

## Phase 1: Fundacional (Transformadores de Datos)

**Purpose**: Actualizar los transformadores en `pdf_state.py` para pasar los campos correctos al template. Estas tareas SON REQUERIDAS antes de cualquier user story del template.

**CRITICAL**: Ninguna user story del template puede comenzar hasta que esta fase esté completa.

- [X] T001 [US1] Actualizar transformador individual: cambiar `detalle["incidente"] = gastos_rep + otros_egr` por `detalle["incidentes"] = valor_incidentes` en `src/presentacion_reflex/state/pdf_state.py` (línea ~954)
- [X] T002 [US1] Agregar campo `comision_porcentaje` al dict `detalle` en `_transform_individual_to_pdf_format()` en `src/presentacion_reflex/state/pdf_state.py` (línea ~948)
- [X] T003 [US3] Reestructurar dict `resumen` en `_transform_individual_to_pdf_format()` con nuevos campos: `comision_monto`, `comision_porcentaje`, `iva_comision`, `gastos_administracion`, `gastos_servicios`, `pago_predial`, `valor_incidentes` en `src/presentacion_reflex/state/pdf_state.py` (líneas ~971-979)
- [X] T004 [US1] Actualizar transformador consolidado: cambiar `incidente = gastos_rep + otros_egr` por `incidentes = valor_incidentes` en `_transform_consolidated_to_pdf_format()` en `src/presentacion_reflex/state/pdf_state.py` (línea ~1054)
- [X] T005 [US3] Reestructurar dict `resumen` en `_transform_consolidated_to_pdf_format()` con los mismos nuevos campos que el transformador individual en `src/presentacion_reflex/state/pdf_state.py`

**Checkpoint**: Transformadores actualizados — el template ahora recibe los datos correctos para todas las stories.

---

## Phase 2: User Story 1 - Columna INCIDENTES + User Story 2 - Eliminar Fila TOTAL (Priority: P1) MVP

**Goal**: La columna INCIDENTES aparece siempre en el detalle financiero, y la fila TOTAL se elimina completamente.

**Independent Test**: Generar PDF de liquidación con `valor_incidentes = 50000` y verificar que la columna INCIDENTES muestra `$50.000` y que no existe fila TOTAL.

### Implementation for User Story 1 + 2

- [X] T006 [US1] Eliminar la condicional `if mostrar_incidentes:` en `_add_detalle_propiedades()` — agregar "INCIDENTES" directamente a la lista `headers` después de "OTRO" en `src/infraestructura/servicios/pdf_elite/templates/estado_cuenta_elite.py` (líneas ~287-289)
- [X] T007 [US1] Actualizar acceso de `d["incidente"]` a `d["incidentes"]` en el loop de filas de datos en `_add_detalle_propiedades()` en `src/infraestructura/servicios/pdf_elite/templates/estado_cuenta_elite.py` (línea ~329)
- [X] T008 [US1] Eliminar la condicional `if mostrar_incidentes:` del loop de filas de datos — agregar `d.get("incidentes", 0)` directamente en `src/infraestructura/servicios/pdf_elite/templates/estado_cuenta_elite.py` (líneas ~331-332)
- [X] T009 [US1] Eliminar variable `mostrar_incidentes` y la acumulación `t_incidentes` en `_add_detalle_propiedades()` en `src/infraestructura/servicios/pdf_elite/templates/estado_cuenta_elite.py` (líneas ~304-309)
- [X] T010 [US2] Eliminar completamente la bloque de la fila TOTAL en `_add_detalle_propiedades()` (líneas ~340-353) en `src/infraestructura/servicios/pdf_elite/templates/estado_cuenta_elite.py`

**Checkpoint**: User Stories 1 y 2 funcionales — columna INCIDENTES siempre visible, fila TOTAL eliminada.

---

## Phase 3: User Story 3 - Reorganización del Resumen Financiero (Priority: P1)

**Goal**: El Resumen Financiero muestra 8 conceptos en el orden: Total Ingresos → Comisión (X%) → IVA 19% → Administración → Servicios → Predial → Incidentes → NETO A PAGAR.

**Independent Test**: Generar PDF con todos los conceptos y verificar el orden y formato de cada fila.

### Implementation for User Story 3

- [X] T011 [US3] Reemplazar las filas actuales del resumen en `_add_resumen_financiero()` por las 8 filas en el nuevo orden en `src/infraestructura/servicios/pdf_elite/templates/estado_cuenta_elite.py` (líneas ~374-382)
- [X] T012 [US3] Implementar formato `Comisión ({X}%)` usando `comision_porcentaje / 100` en la fila de Comisión del resumen en `src/infraestructura/servicios/pdf_elite/templates/estado_cuenta_elite.py`
- [X] T013 [US3] Mantener NETO A PAGAR como fila destacada con `highlight_totals=True` en `_add_resumen_financiero()` en `src/infraestructura/servicios/pdf_elite/templates/estado_cuenta_elite.py` (líneas ~385-391)

**Checkpoint**: User Story 3 funcional — Resumen Financiero reorganizado con 8 conceptos.

---

## Phase 4: User Story 4 - Eliminación del Código QR (Priority: P2)

**Goal**: El Código QR no aparece en el Estado de Cuenta PDF. El encabezado se redistribuye correctamente.

**Independent Test**: Generar PDF y verificar que no existe ningún elemento QR ni espacio en blanco residual.

### Implementation for User Story 4

- [X] T014 [US4] Eliminar la línea `self.enable_verification_qr("estado", data["estado_id"])` en el método `generate()` de `src/infraestructura/servicios/pdf_elite/templates/estado_cuenta_elite.py` (línea ~85)

**Checkpoint**: User Story 4 funcional — QR eliminado, encabezado redistribuido.

---

## Phase 5: User Story 5 - Sección de Observaciones (Priority: P2)

**Goal**: La sección OBSERVACIONES aparece siempre en el PDF, mostrando el contenido completo o un mensaje por defecto si está vacío.

**Independent Test**: Generar PDF con observaciones largas y verificar que se muestra completo. Generar PDF sin observaciones y verificar que aparece el mensaje por defecto.

### Implementation for User Story 5

- [X] T015 [US5] Eliminar la condicional `if "observaciones" in data and data["observaciones"]:` en `_add_notas()` en `src/infraestructura/servicios/pdf_elite/templates/estado_cuenta_elite.py` (línea ~411)
- [X] T016 [US5] Agregar lógica para mostrar mensaje por defecto "Sin observaciones registradas." cuando `observaciones` es None o string vacío en `_add_notas()` en `src/infraestructura/servicios/pdf_elite/templates/estado_cuenta_elite.py`

**Checkpoint**: User Story 5 funcional — Observaciones siempre visibles.

---

## Phase 6: Validación y Pulido

**Purpose**: Verificar que todos los cambios funcionan correctamente y no hay regresiones.

- [X] T017 Ejecutar verificación de sintaxis: `python -m py_compile src/infraestructura/servicios/pdf_elite/templates/estado_cuenta_elite.py`
- [X] T018 Ejecutar verificación de sintaxis: `python -m py_compile src/presentacion_reflex/state/pdf_state.py`
- [X] T019 Ejecutar escenarios de validación del quickstart.md (Escenarios 1-8)
- [X] T020 Verificar que la generación por lotes (ZIP) hereda todos los cambios correctamente
- [X] T021 Ejecutar `reflex run --env dev` y generar PDFs de prueba desde la UI

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Fundacional)**: Sin dependencias — puede iniciar inmediatamente
- **Phase 2 (US1+US2)**: Depende de Phase 1 — BLOQUEA todas las stories del template
- **Phase 3 (US3)**: Depende de Phase 1 — puede ejecutarse en paralelo con Phase 2
- **Phase 4 (US4)**: Depende de Phase 1 — puede ejecutarse en paralelo con Phase 2 y 3
- **Phase 5 (US5)**: Depende de Phase 1 — puede ejecutarse en paralelo con Phase 2, 3 y 4
- **Phase 6 (Validación)**: Depende de todas las phases anteriores

### User Story Dependencies

- **US1 (Columna INCIDENTES)**: Depende de Phase 1 (transformadores)
- **US2 (Eliminar Fila TOTAL)**: Depende de Phase 1, independiente de US1 pero se ejecuta junto a ella
- **US3 (Resumen Financiero)**: Depende de Phase 1, independiente de US1/US2
- **US4 (Eliminar QR)**: Depende de Phase 1, independiente de US1/US2/US3
- **US5 (Observaciones)**: Depende de Phase 1, independiente de US1/US2/US3/US4

### Within Each User Story

- Transformadores (Phase 1) ANTES del template
- Core implementation ANTES de validación
- Story completa antes de siguiente prioridad

### Parallel Opportunities

- Phase 1 (transformadores) es sequential — un solo archivo
- US1+US2, US3, US4, US5 son independientes entre sí — pueden ejecutarse en paralelo
- Validación (Phase 6) es el último paso

---

## Parallel Example: User Stories del Template

```bash
# Después de completar Phase 1 (transformadores), las stories del template son independientes:

# US1+US2 (método _add_detalle_propiedades):
Task: "Eliminar condicional mostrar_incidentes y fila TOTAL en estado_cuenta_elite.py"

# US3 (método _add_resumen_financiero):
Task: "Reorganizar 8 filas del resumen en estado_cuenta_elite.py"

# US4 (método generate):
Task: "Eliminar enable_verification_qr en estado_cuenta_elite.py"

# US5 (método _add_notas):
Task: "Mostrar siempre sección OBSERVACIONES en estado_cuenta_elite.py"
```

---

## Implementation Strategy

### MVP First (US1 + US2)

1. Completar Phase 1: Transformadores
2. Completar Phase 2: US1 + US2 (Columna INCIDENTES + Eliminar TOTAL)
3. **PARAR Y VALIDAR**: Probar US1+US2 independientemente
4. Desplegar/demostrar si está listo

### Incremental Delivery

1. Phase 1 + Phase 2 → Transformadores + Detalle Financiero listo (MVP!)
2. Agregar Phase 3 → Resumen Financiero reorganizado → Probar → Desplegar
3. Agregar Phase 4 → QR eliminado → Probar → Desplegar
4. Agregar Phase 5 → Observaciones siempre visibles → Probar → Desplegar
5. Cada story agrega valor sin romper las anteriores

### Parallel Team Strategy

Con múltiples desarrolladores:

1. Equipo completa Phase 1 (transformadores) junto
2. Una vez Phase 1 lista:
   - Desarrollador A: Phase 2 (US1+US2)
   - Desarrollador B: Phase 3 (US3)
   - Desarrollador C: Phase 4 (US4) + Phase 5 (US5)
3. Stories completan e integran independientemente

---

## Notes

- [P] tasks = diferentes archivos, sin dependencias
- [Story] label vincula tarea a user story para trazabilidad
- Cada user story debe ser completable y testeable independientemente
- Commit después de cada tarea o grupo lógico
- Parar en cualquier checkpoint para validar story independientemente
- No hay tests explícitos en la especificación — validación visual por quickstart.md
