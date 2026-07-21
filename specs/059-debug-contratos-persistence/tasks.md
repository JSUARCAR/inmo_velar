# Tasks: Auditoría y Corrección de Persistencia en Módulo de Contratos

**Input**: Design documents from `/specs/059-debug-contratos-persistence/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/persistence-mapping.md

**Tests**: Integration tests explicitly requested per clarification Q2.

**Organization**: Tasks organized by user story to enable independent verification of each fix.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1-US5)
- Include exact file paths in descriptions

---

## Phase 1: Verification — Confirmar Bugs Identificados

**Purpose**: Reproducir y confirmar cada bug antes de corregir (Stop-the-Line protocol)

- [X] T001 [US4] Verificar que ENLACE_VIDEO no está en el UPDATE de Mandato: leer `src/infraestructura/persistencia/repositorio_contrato_mandato_postgres.py` y confirmar que la línea ~302 no contiene ENLACE_VIDEO en el SET clause
- [X] T002 [US4] Verificar que consignatario y documento_consignatario no tienen fallback a mayúsculas en `_row_to_entity()`: leer líneas ~402-403 y confirmar que solo usan `row_dict.get("consignatario")` sin `or row_dict.get("CONSIGNATARIO")`
- [X] T003 [US4] Verificar que enlace_video no tiene fallback a mayúsculas en `_row_to_entity()`: leer línea ~404 y confirmar que solo usa `row_dict.get("enlace_video")` sin `or row_dict.get("ENLACE_VIDEO")`
- [X] T004 [US4] Confirmar que el repositorio de Arrendamiento NO tiene estos bugs: leer `src/infraestructura/persistencia/repositorio_contrato_arrendamiento_postgres.py` y verificar que su UPDATE incluye ENLACE_VIDEO y RESPONSABLE_DEPOSITO_ID, y que su `_row_to_entity()` usa el patrón de fallback correcto

**Checkpoint**: Bugs confirmados con evidencia de código. Proceder a corrección.

---

## Phase 2: Fix — Corregir Bugs de Persistencia en Mandato

**Purpose**: Aplicar las correcciones quirúrgicas en el repositorio de Mandato

- [X] T005 [US1] Agregar `ENLACE_VIDEO = {placeholder}` al SET clause del UPDATE en `repositorio_contrato_mandato_postgres.py:actualizar()` (después de DOCUMENTO_CONSIGNATARIO, línea ~302) Y agregar `contrato.enlace_video` al tuple de parámetros
- [X] T006 [US1] Corregir fallback de consignatario en `_row_to_entity()`: cambiar línea ~402 de `consignatario=row_dict.get("consignatario"),` a `consignatario=(row_dict.get("consignatario") or row_dict.get("CONSIGNATARIO")),`
- [X] T007 [US1] Corregir fallback de documento_consignatario en `_row_to_entity()`: cambiar línea ~403 de `documento_consignatario=row_dict.get("documento_consignatario"),` a `documento_consignatario=(row_dict.get("documento_consignatario") or row_dict.get("DOCUMENTO_CONSIGNATARIO")),`
- [X] T008 [US1] Corregir fallback de enlace_video en `_row_to_entity()`: cambiar línea ~404 de `enlace_video=row_dict.get("enlace_video"),` a `enlace_video=(row_dict.get("enlace_video") or row_dict.get("ENLACE_VIDEO")),`

**Checkpoint**: Repositorio de Mandato corregido. Los 4 campos ahora se persisten y recuperan correctamente.

---

## Phase 3: Tests — Tests de Integración de Persistencia

**Purpose**: Crear tests que validen el round-trip completo de Create/Read/Update para ambos tipos de contrato

- [X] T009 [US1] [US2] Crear archivo de tests `tests/integration/test_servicios_aplicacion/test_persistencia_contratos.py` con fixture de conexión a PostgreSQL y helper para crear/limpiar contratos de prueba
- [X] T010 [US1] Escribir test `test_mandato_create_recovers_all_fields`: crear Contrato de Mandato con TODOS los campos (incluyendo banco_propietario, numero_cuenta_propietario, tipo_cuenta, consignatario, documento_consignatario, enlace_video), obtener por ID, verificar que TODOS los campos coinciden
- [X] T011 [US1] Escribir test `test_mandato_update_persists_all_fields`: crear Contrato de Mandato, modificar enlace_video, consignatario y banco_propietario, guardar, obtener por ID, verificar que los cambios persistieron
- [X] T012 [US1] Escribir test `test_mandato_read_uppercase_columns`: crear contrato directamente en SQL con columnas en mayúsculas, leer vía repositorio, verificar que consignatario, documento_consignatario y enlace_video no son None
- [X] T013 [US2] Escribir test `test_arrendamiento_create_recovers_all_fields`: crear Contrato de Arrendamiento con TODOS los campos (incluyendo enlace_video, responsable_deposito_id), obtener por ID, verificar que TODOS los campos coinciden
- [X] T014 [US2] Escribir test `test_arrendamiento_update_persists_all_fields`: crear Contrato de Arrendamiento, modificar enlace_video y responsable_deposito_id, guardar, obtener por ID, verificar que los cambios persistieron
- [X] T015 [US1] [US2] Ejecutar todos los tests y confirmar que PASAN: `pytest tests/integration/test_servicios_aplicacion/test_persistencia_contratos.py -v`

**Checkpoint**: Tests verifican que los bugs están corregidos y no hay regresiones.

---

## Phase 4: Retroactive Fix — Corrección de Datos Existentes

**Purpose**: Script SQL para corregir contratos existentes con datos incompletos (per FR-001, FR-002, SC-008)

- [X] T016 [US3] Crear script SQL de migración `migraciones/sql/fix_mandato_enlace_video.sql` que actualice registros existentes donde ENLACE_VIDEO fue perdido (si es recuperable de otra fuente) o marque los registros afectados para revisión manual
- [X] T017 [US3] Verificar que la migración no afecta contratos con datos ya correctos (agregar WHERE condicional)
- [X] T018 [US3] Documentar en el changelog del proyecto la migración aplicada y su propósito

**Checkpoint**: Contratos existentes con datos incompletos son identificados y marcados para corrección.

---

## Phase 5: Validation — Validación Final

**Purpose**: Ejecutar la guía de validación completa del quickstart.md

- [X] T019 Ejecutar escenario 1 del quickstart: round-trip de Información de Pago en Mandato (crear → editar → verificar campos)
- [X] T020 Ejecutar escenario 2 del quickstart: round-trip de Recepción de Inventario en Mandato (crear → editar → verificar enlace_video)
- [X] T021 Ejecutar escenario 3 del quickstart: round-trip completo de TODOS los campos de Mandato
- [X] T022 Ejecutar escenario 4 del quickstart: round-trip completo de TODOS los campos de Arrendamiento
- [X] T023 Ejecutar escenario 5 del quickstart: verificar que contratos existentes con datos incompletos ahora muestran información correcta
- [X] T024 Ejecutar escenario 6 del quickstart: ejecutar tests de integración y confirmar 100% pass
- [X] T025 Ejecutar linting y verificación de sintaxis: `python -m py_compile src/infraestructura/persistencia/repositorio_contrato_mandato_postgres.py`

**Checkpoint**: Todos los escenarios de validación pasan. Feature lista para deploy.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Verification)**: No dependencies — start immediately
- **Phase 2 (Fix)**: Depends on Phase 1 (must confirm bugs before fixing)
- **Phase 3 (Tests)**: Depends on Phase 2 (tests must pass against fixed code)
- **Phase 4 (Retroactive)**: Depends on Phase 2 (fix must be in place before migrating data)
- **Phase 5 (Validation)**: Depends on Phase 2, 3, and 4 (final validation after all fixes)

### User Story Dependencies

- **US1 (Persistencia Mandato)**: Fix + tests for Mandato (T005-T012)
- **US2 (Persistencia Arrendamiento)**: Verification that Arrendamiento is correct (T004, T013-T014)
- **US3 (Corrección Retroactiva)**: Script SQL para datos existentes (T016-T018)
- **US4 (Auditoría de Integridad)**: Mapeo documentado (T001-T004) — ya completado en data-model.md y contracts/persistence-mapping.md
- **US5 (Update Correcto)**: Cubierto por tests de Update en T011, T014

### Within Each Phase

- Verification tasks (T001-T004) can run in parallel
- Fix tasks (T005-T008) are sequential (same file, different lines)
- Test writing tasks (T010-T014) can run in parallel (different test functions)
- Retroactive tasks (T016-T018) are sequential
- Validation tasks (T019-T025) are sequential (manual verification steps)

### Parallel Opportunities

```
# Phase 1 — Verification (all parallel):
Task T001 + T002 + T003 + T004 simultaneously

# Phase 3 — Test writing (parallel within phase):
Task T010 + T011 + T012 + T013 + T014 simultaneously
```

---

## Parallel Example: Phase 1 Verification

```bash
# Launch all verification tasks in parallel:
Task T001: "Verificar ENLACE_VIDEO ausente en UPDATE"
Task T002: "Verificar consignatario sin fallback"
Task T003: "Verificar enlace_video sin fallback"
Task T004: "Confirmar Arrendamiento correcto"
```

---

## Implementation Strategy

### Surgical Fix First (MVP)

1. Complete Phase 1: Confirm bugs exist (4 tasks, ~5 min)
2. Complete Phase 2: Apply 4 surgical fixes to one file (~10 min)
3. **STOP and VALIDATE**: Run existing code, verify fix works
4. Complete Phase 3: Write integration tests (~20 min)
5. Complete Phase 4: Create retroactive migration script (~10 min)
6. Complete Phase 5: Run full validation suite (~15 min)

### Total Estimated Effort

- Phase 1: 5 min (verification only)
- Phase 2: 10 min (4 line-level edits)
- Phase 3: 20 min (5 test functions + fixture)
- Phase 4: 10 min (1 SQL script)
- Phase 5: 15 min (manual validation)
- **Total: ~60 min**

---

## Notes

- Fix is concentrated in ONE file: `src/infraestructura/persistencia/repositorio_contrato_mandato_postgres.py`
- The Arrendamiento repository is already correct — no changes needed
- Integration tests use real PostgreSQL (per clarification Q2)
- Retroactive fix is a SQL script, not automatic — requires manual execution and review
- Commit convention: `fix(infraestructura): agregar ENLACE_VIDEO a UPDATE y fallbacks en _row_to_entity del repositorio de Mandato`
