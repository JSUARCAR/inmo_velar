# ESTADO DE TAREAS — Sistema Velar

> Documento de seguimiento dinámico (Constitución §5). Actualizar tras cada hito.

## Feature activa: 072-renovacion-contratos-debug

**Estado**: Implementación completa — 31/31 tareas `[x]` (T001–T026 + Fase 6 T027–T031). Validación final: SC-003 69 passed, 0 failed.
**Última actualización**: 2026-09-13

### Resumen por fase

| Fase | Alcance | Estado |
|------|---------|--------|
| Fase 1 (Setup) | Causas raíz: NULLIF Q1–Q6, `calcular_fecha_inicio_renovacion` (+1 día), `ContratoNoRenovableError`, helper IPC | ✅ T001–T006 |
| Fase 2 (US1, P1) | Renovación normal: IPC condicional, propagación, auditoría, caché, multi-mandato, PDF (SC-004), canon propiedad (FR-010) | ✅ T007–T017 |
| Fase 3 (US2, P2) | Renovaciones consecutivas + idempotencia DB-backed | ✅ T018–T019 |
| Fase 4 (US3, P2) | Fechas límite (31-Dic, 28/29-Feb, fin-de-mes) | ✅ T020–T021 |
| Fase 5 (Pulido) | Atomicidad (SC-001), concurrencia sin deadlocks (CHK032), regresión SC-003 (61 passed), quickstart E1–E12, gates §5 | ✅ T022–T026 |
| Phase 6 (Convergence) | Hallazgos de converge: higiene raíz, docs dinámicos, cobertura rama `sumar_meses`, test FR-012, desviación black | ✅ T027–T031 |

### Validación

- SC-001: 47 tests de renovación verdes (E1–E12).
- SC-003: suite quickstart `-k "renovacion or liquidaciones or recaudos or contrato"` → 61 passed, 0 failed.
- Gates T026: compileall PASS · mypy 0 errores nuevos vs baseline · ruff PASS (archivos feature) · reflex export PASS · black/cobertura con desviaciones preexistentes documentadas en tasks.md T026.

### Deuda conocida (preexistente, fuera de alcance 072)

- 10 fallos en suite completa `tests/unit tests/integration` (financiero ×4, personas ×1, propiedades ×5): fixture SQLite sin columna `eliminada`.
- black: 74/410 archivos de `src` sin formatear (repo nunca fue black-formateado).
- Cobertura paquetes: dominio 64.86% / aplicación 30.78% vs umbrales §5 (brecha legacy).

## Features recientes completadas

| Fecha | Feature | Estado |
|-------|---------|--------|
| 2026-09-13 | 072-renovacion-contratos-debug | Implementada (pendiente commit) |
| 2026-09-14 | 073-fix-renovacion-integer-range | Implementada (TDD): causa `canon×comisión` int4 en propagación; fix `::BIGINT` + validador dos niveles + `ValorFueraDeRangoError`; T005/T011 verdes; T010 caso-73 pendiente de operador en producción |
| 2026-05-10 | 063-fix-canon-propagation | Completada (predecesora de 072) |
