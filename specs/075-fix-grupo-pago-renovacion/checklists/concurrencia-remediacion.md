# Concurrency Checklist: Remediación ↔ Renovación con compare-and-set (Feature 075)

**Purpose**: Validar como gate pre-implementación que el requisito de concurrencia entre la remediación masiva y las renovaciones (compare-and-set + reporte de filas omitidas) es completo, consistente, medible y está propagado en todos los artefactos.
**Created**: 2026-09-21
**Feature**: [spec.md](../spec.md) | Diseño: [research.md](../research.md) R5, [data-model.md](../data-model.md), [contracts/cli-remediacion.md](../contracts/cli-remediacion.md) | Tareas: [tasks.md](../tasks.md)

**Note**: Prueba unitaria de requisitos y diseño (no de implementación). Cada ítem evalúa lo escrito; ninguno ejecuta ni verifica comportamiento del sistema.

## Definición del Requisito

- [x] CHK001 ¿FR-010 define compare-and-set (condicionar cada UPDATE a que los valores leídos sigan vigentes)? [Completeness, Spec §FR-010]
- [x] CHK002 ¿FR-010 exige omitir y reportar las filas modificadas concurrentemente sin sobrescribirlas? [Completeness, Spec §FR-010]
- [x] CHK003 ¿El caso de borde de renovación concurrente durante la remediación está enunciado? [Coverage, Spec §Edge Cases]
- [x] CHK004 ¿La decisión compare-and-set + reporte quedó registrada en la sesión de clarificación? [Traceability, Spec §Clarifications]
- [x] CHK005 ¿Se declara explícitamente que la operación normal (renovaciones) no se bloquea? [Clarity, Spec §FR-010, §Clarifications]
- [x] CHK006 ¿El requisito cubre ambos tipos de contrato (mandato y arrendamiento) sin excepción? [Coverage, Spec §FR-009, §FR-010]

## Consistencia entre Artefactos

- [x] CHK007 ¿research R5 describe la misma condición de compare-and-set (WHERE con valores leídos) que el spec? [Consistency, research R5, Spec §FR-010]
- [x] CHK008 ¿El contrato del CLI incluye compare-and-set y el reporte de filas omitidas en comportamiento y garantías? [Consistency, contracts/cli-remediacion.md §Comportamiento, §Postcondiciones]
- [x] CHK009 ¿La tarea T015 asigna compare-and-set y el reporte de omitidas? [Traceability, tasks.md T015]
- [x] CHK010 ¿El plan (Summary y refinamientos) refleja la decisión sin contradicción? [Consistency, plan.md]
- [x] CHK011 ¿El modelo de datos define un estado de acción para filas omitidas (`Omitida`)? [Completeness, data-model §7]
- [x] CHK012 ¿El quickstart declara el resultado esperado con filas omitidas en `--commit`? [Coverage, quickstart §3]
- [x] CHK013 ¿Ningún artefacto afirma que la remediación actualiza "todas" las discrepancias sin la condición de concurrencia? [Ambiguity]

## Medibilidad y Verificación

- [x] CHK014 ¿La verificación de concurrencia es objetiva (la fila modificada se omite y aparece reportada)? [Measurability, Spec §FR-010]
- [x] CHK015 ¿Existe una prueba asignada que cubra el caso de concurrencia remediación↔renovación? [Coverage, tasks.md T013]
- [x] CHK016 ¿El reporte distingue claramente `Sin cambio`, `Actualizado` y `Omitida`? [Clarity, data-model §7, contracts/cli-remediacion.md]
- [x] CHK017 ¿Se evita el bloqueo pesimista y la alternativa descartada está justificada? [Consistency, research R5 alternativas]
- [x] CHK018 ¿El rollback total ante fallo se mantiene garantizado con compare-and-set (transacción única)? [Consistency, Spec §FR-010, contracts §Comportamiento]
- [x] CHK019 ¿La idempotencia se mantiene aun con filas omitidas (segunda corrida coherente y omitidas reportadas para revisión)? [Measurability, Spec §SC-002, contracts §Postcondiciones]
- [x] CHK020 ¿Los códigos de salida no cambian por filas omitidas (0 = ejecución exitosa con o sin discrepancias)? [Clarity, contracts/cli-remediacion.md §Códigos de salida]

## Notes

- Check items off as completed: `[x]`
- Add comments or findings inline
- Items are numbered sequentially for easy reference
- Traceabilidad: 20/20 ítems referencian artefactos o marcadores de calidad.
- Complementa (no reemplaza) los gates previos: `requirements.md`, `renovacion-grupo-pago.md`, `plan-auditoria.md`, `tasks-calidad.md` y `remediacion-f1.md`.
- Evaluación 2026-09-21 (gate pre-implementación): 20/20 ítems pasan. Brechas detectadas y resueltas durante la evaluación: CHK011 → `data-model §7` añadió la acción `Omitida (modificada durante la remediación)`; CHK012 → `quickstart §3` declara las filas omitidas; CHK015 → T013 ampliada con el caso de concurrencia; CHK017 → research R5 añadió la alternativa descartada de bloqueo pesimista; CHK019 → contracts §Postcondiciones precisa la idempotencia con filas omitidas.
