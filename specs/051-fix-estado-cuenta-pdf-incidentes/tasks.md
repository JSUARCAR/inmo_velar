# Tasks: Fix Estado Cuenta PDF - Incidentes

**Input**: Design documents from `/specs/051-fix-estado-cuenta-pdf-incidentes/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, quickstart.md

**Tests**: No se incluyen tasks de testing explícitos. La validación se realiza con los escenarios de `quickstart.md` después de cada checkpoint.

**Organization**: Las 3 historias de usuario comparten los mismos 3 archivos modificados. Se organizan en fases secuenciales porque cada capa depende de la anterior (Clean Architecture: Persistencia → Aplicación → Infraestructura).

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Verificar que el dominio y la DB están correctos antes de iniciar cambios

- [x] T001 Verificar que `valor_incidentes` existe en la tabla LIQUIDACIONES y tiene datos poblados en PostgreSQL
- [x] T002 Verificar que la entidad `Liquidacion` en `src/dominio/entidades/liquidacion.py` tiene el campo `valor_incidentes` y que `calcular_totales()` lo incluye en el cálculo de `neto_a_pagar`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Corregir la capa de Persistencia para que `valor_incidentes` llegue al mapeo PDF

**⚠️ CRITICAL**: Las fases de historias de usuario no pueden comenzar hasta que esta fase esté completa

- [x] T003 Agregar campo `valor_incidentes` al diccionario `propiedades_formateadas` en `obtener_consolidado_propietario()` dentro de `src/infraestructura/persistencia/repositorio_liquidacion_postgres.py` (línea ~1486-1506). El campo debe ser: `"valor_incidentes": prop.get("VALOR_INCIDENTES") or 0`

**Checkpoint**: Persistencia lista — `valor_incidentes` ahora fluye desde PostgreSQL hasta el mapeo

---

## Phase 3: User Story 1 - Visualización de Incidentes en Estado de Cuenta PDF (Priority: P1) 🎯 MVP

**Goal**: El Estado de Cuenta PDF muestra el valor de Incidentes en el detalle y en el resumen financiero, afectando correctamente el Neto a Pagar.

**Independent Test**: Generar un Estado de Cuenta PDF para una liquidación con incidentes y verificar que el valor aparece en el detalle, en el resumen, y que el Neto a Pagar es correcto.

### Implementation for User Story 1

- [x] T004 [US1] Agregar campo `valor_incidentes` como campo independiente en `mapear_consolidado_a_pdf_elite()` dentro de `src/aplicacion/servicios/servicio_financiero.py` (línea ~756). Agregar después de la línea de `incidente`: `"valor_incidentes": prop.get("valor_incidentes", 0) or 0`. Incluir validación numérica (R6): si no es `int` o `float`, asignar 0.
- [x] T005 [US1] Agregar campo `valor_incidentes` al resumen financiero en `mapear_consolidado_a_pdf_elite()` dentro de `src/aplicacion/servicios/servicio_financiero.py` (línea ~769). Agregar: `"valor_incidentes": datos.get("valor_incidentes", 0) or 0`
- [x] T006 [US1] Agregar columna/línea de "Incidentes" en la tabla de detalle (`_add_detalle_propiedades`) dentro de `src/infraestructura/servicios/pdf_elite/templates/estado_cuenta_elite.py`. Si `valor_incidentes > 0`, mostrar la línea con formato de moneda colombiana. Si es $0, ocultar la línea (FR-005).
- [x] T007 [US1] Agregar línea "(-) Incidentes: $X.XXX" en el resumen financiero (`_add_resumen_financiero`) dentro de `src/infraestructura/servicios/pdf_elite/templates/estado_cuenta_elite.py`. Insertar antes del "Valor Neto" si `valor_incidentes > 0` (FR-006).

**Checkpoint**: User Story 1 completa — El PDF muestra Incidentes en detalle y resumen. Validar con escenarios 1 y 2 de `quickstart.md`.

---

## Phase 4: User Story 2 - Consistencia entre UI y PDF (Priority: P2)

**Goal**: Los valores de Incidentes en la UI coinciden exactamente con los del PDF.

**Independent Test**: Comparar visualmente los valores en la tabla de liquidaciones de la UI con los del PDF para la misma liquidación.

### Implementation for User Story 2

- [x] T008 [US2] Verificar que el mapeo `obtener_datos_para_pdf()` en `src/infraestructura/persistencia/repositorio_liquidacion_postgres.py` (línea ~1390) ya retorna `valor_incidentes` y que el valor coincide con el de la UI. Solo verificación, no requiere cambio de código.
- [x] T009 [US2] Ejecutar escenario 6 de `quickstart.md` (Consistencia UI ↔ PDF) para validar que `valor_incidentes` y `neto_a_pagar` coinciden entre UI y PDF con tolerancia de $0.

**Checkpoint**: User Story 2 completa — UI y PDF son consistentes.

---

## Phase 5: User Story 3 - Regresión y Robustez (Priority: P3)

**Goal**: La corrección no introduce regresiones en otros documentos PDF ni en el módulo de liquidaciones.

**Independent Test**: Generar todos los tipos de PDF del sistema y ejecutar las pruebas de regresión del módulo.

### Implementation for User Story 3

- [x] T010 [US3] Ejecutar escenario 5 de `quickstart.md` (Regresión — Otros tipos de PDF) para verificar que contratos, reportes y otros documentos PDF se generan sin errores ni cambios inesperados.
- [x] T011 [US3] Ejecutar escenario 3 de `quickstart.md` (PDF en lote ZIP) para verificar que el ZIP incluye correctamente el valor de Incidentes en cada PDF individual cuando algunas liquidaciones tienen incidentes y otras no.
- [x] T012 [US3] Ejecutar escenario 4 de `quickstart.md` (Valores grandes y decimales) para verificar el formato de moneda colombiana con valores > $999.999.999 y con decimales redondeados.
- [x] T013 [US3] Ejecutar tests de regresión del módulo de liquidaciones: `pytest tests/ -v --tb=short` y verificar que todos pasan.

**Checkpoint**: Todas las historias completas. Sin regresiones. Validar con todos los escenarios de `quickstart.md`.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Limpieza y validación final

- [x] T014 Ejecutar linting: `ruff check src/` y `mypy src/` para verificar que no hay errores de estilo ni de tipado.
- [x] T015 Ejecutar validación completa de `quickstart.md` (escenarios 1-6) y confirmar que todos pasan.
- [x] T016 Actualizar `ESTADO_TAREAS.md` con el resultado de la implementación.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational (Phase 2) — MVP
- **User Story 2 (Phase 4)**: Depends on Phase 3 (US1 implementation provides the data)
- **User Story 3 (Phase 5)**: Depends on Phase 3 (US1 implementation provides the data)
- **Polish (Phase 6)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) — No dependencies on other stories
- **User Story 2 (P2)**: Depends on US1 implementation (same code paths). Can验证 but no new code needed.
- **User Story 3 (P3)**: Depends on US1 implementation. Regression testing only.

### Within Each User Story

- Persistencia → Aplicación → Infraestructura (dirección Clean Architecture)
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- T001 y T002 pueden ejecutarse en paralelo (diferentes archivos)
- T004 y T005 pueden ejecutarse en paralelo (mismo archivo, diferentes funciones/lineas)
- T006 y T007 pueden ejecutarse en paralelo (diferentes métodos del template)
- T008 y T009 pueden ejecutarse en paralelo (diferentes tipos de validación)

---

## Parallel Example: User Story 1

```bash
# T004 y T005 pueden ejecutarse en paralelo (servicio_financiero.py):
Task: "T004 Agregar valor_incidentes a mapear_consolidado_a_pdf_elite() línea ~756"
Task: "T005 Agregar valor_incidentes al resumen en mapear_consolidado_a_pdf_elite() línea ~769"

# T006 y T007 pueden ejecutarse en paralelo (estado_cuenta_elite.py):
Task: "T006 Agregar columna Incidentes en _add_detalle_propiedades"
Task: "T007 Agregar línea Incidentes en _add_resumen_financiero"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (verificar dominio y DB)
2. Complete Phase 2: Foundational (corregir repositorio)
3. Complete Phase 3: User Story 1 (corregir servicio y template)
4. **STOP y VALIDAR**: Ejecutar escenarios 1 y 2 de quickstart.md
5. El PDF ahora muestra Incidentes correctamente

### Incremental Delivery

1. Setup + Foundational → Persistencia corregida
2. US1 → PDF muestra Incidentes → Validar → **MVP listo**
3. US2 → Verificar consistencia UI-PDF → Deploy
4. US3 → Verificar regresiones → Deploy final
5. Polish → Limpieza y documentación

### Commit Strategy (Cambios Atómicos)

- **Commit 1** (T003): `fix(persistencia): agregar valor_incidentes a obtener_consolidado_propietario`
- **Commit 2** (T004-T005): `fix(servicio): separar valor_incidentes en mapeo PDF elite`
- **Commit 3** (T006-T007): `fix(template): agregar linea de Incidentes en detalle y resumen del PDF`

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Stop at any checkpoint to validate story independently
- The domain entity (`liquidacion.py`) requires NO changes — it's already correct
- The UI (`presentacion_reflex/`) requires NO changes — it already shows `valor_incidentes`
- Legacy `servicio_documentos_pdf.py` is out of scope (documented as technical debt in research.md R5)
