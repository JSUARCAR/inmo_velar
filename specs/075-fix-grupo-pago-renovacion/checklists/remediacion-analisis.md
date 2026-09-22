# Remediation Consistency Checklist: Hallazgos del análisis (Feature 075)

**Purpose**: Validar como gate pre-implementación que la remediación de los hallazgos del último análisis (C1, D1, A1, B1, C2, T1, F6) quedó completa, consistente y trazable en spec, plan, tasks, contratos y gates, sin redacciones obsoletas.
**Created**: 2026-09-21
**Feature**: [spec.md](../spec.md) | Plan: [plan.md](../plan.md) | Tareas: [tasks.md](../tasks.md)

**Note**: Prueba unitaria de requisitos y diseño (no de implementación). Cada ítem evalúa lo escrito; ninguno ejecuta ni verifica comportamiento del sistema.

## C1 — SC-002 cualificado por concurrencia

- [x] CHK001 ¿SC-002 cualifica "cero discrepancias" con la resolución de las filas omitidas? [Consistency, Spec §SC-002]
- [x] CHK002 ¿T017 alinea su expectativa con las filas omitidas por concurrencia? [Consistency, tasks.md T017]
- [x] CHK003 ¿El contrato del CLI y el data-model son coherentes con el SC-002 cualificado? [Consistency, contracts/cli-remediacion.md §Postcondiciones, data-model §7]

## D1 — Cobertura de pruebas de la lógica nueva (§5)

- [x] CHK004 ¿Existe tarea de pruebas unitarias para las funciones puras del script? [Coverage, tasks.md T027]
- [x] CHK005 ¿T024 mide la cobertura de la lógica nueva con `pytest-cov`? [Completeness, tasks.md T024, constitución §5]
- [x] CHK006 ¿El plan declara la estrategia de cobertura del script y su medición? [Consistency, plan.md §Constitution Check]

## A1 — Duplicación FR-004 / FR-006

- [x] CHK007 ¿FR-006 referencia FR-004 como regla común sin duplicar obligaciones? [Consistency, Spec §FR-004, §FR-006]
- [x] CHK008 ¿Ningún artefacto conserva la redacción duplicada anterior de FR-006? [Ambiguity]

## B1 — Valores inválidos enumerados

- [x] CHK009 ¿Edge Cases define discrepancia como valor ≠ esperado con ejemplos (0, vacío, no numérico, fuera de {1,2,3})? [Clarity, Spec §Edge Cases]
- [x] CHK010 ¿La auditoría/reporte y las validaciones del data-model son coherentes con esa definición? [Consistency, data-model §6, §7]

## C2 — Criterio de aceptación de T023

- [x] CHK011 ¿T023 declara criterio de aceptación explícito (0 fallos en suites + resultados conformes del quickstart §4)? [Measurability, tasks.md T023]
- [x] CHK012 ¿El criterio es consistente con SC-004 y la sección 5 del quickstart? [Consistency, Spec §SC-004, quickstart §5]

## T1 — Terminología de la actualización condicionada

- [x] CHK013 ¿El spec usa de forma consistente "actualización condicionada (compare-and-set)" en FR-010 y Clarifications? [Consistency, Spec §FR-010, §Clarifications]
- [x] CHK014 ¿Los artefactos de diseño usan el mismo concepto sin introducir variantes divergentes? [Consistency, research R5, contracts]

## F6 — Seguimiento de SC-006

- [x] CHK015 ¿SC-006 declara responsable/mecanismo de seguimiento y referencia al quickstart §7? [Completeness, Spec §SC-006]
- [x] CHK016 ¿T026 cubre el baseline y el seguimiento a 30 días de SC-006? [Traceability, tasks.md T026]

## Consistencia Transversal

- [x] CHK017 ¿Las notas de evaluación de los gates existentes reflejan los conteos y cambios actuales (27 tareas)? [Consistency, checklists]
- [x] CHK018 ¿No quedan referencias obsoletas a las redacciones anteriores en spec, tasks o contratos? [Ambiguity]
- [x] CHK019 ¿La remediación no alteró el alcance ni los criterios de éxito (solo precisión)? [Consistency, Spec §US, §SC]
- [x] CHK020 ¿El análisis queda con 0 hallazgos abiertos (C1, D1, A1, B1, C2, T1, F6 cerrados) y verificable? [Completeness]

## Notes

- Check items off as completed: `[x]`
- Add comments or findings inline
- Items are numbered sequentially for easy reference
- Traceabilidad: 20/20 ítems referencian artefactos o marcadores de calidad.
- Complementa (no reemplaza) los gates previos: `requirements.md`, `renovacion-grupo-pago.md`, `plan-auditoria.md`, `tasks-calidad.md`, `remediacion-f1.md` y `concurrencia-remediacion.md`.
- Evaluación 2026-09-21 (gate pre-implementación): 20/20 ítems pasan. Brecha detectada y resuelta durante la evaluación: CHK006 → la fila §5 del Constitution Check en `plan.md` ahora declara las unitarias del script (T027) y la medición de cobertura con `pytest-cov` (T024).
