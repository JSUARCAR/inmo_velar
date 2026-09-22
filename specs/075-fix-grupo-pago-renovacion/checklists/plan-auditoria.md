# Requirements & Design Quality Checklist: Diseño del plan, auditoría y datos TEST (Feature 075)

**Purpose**: Validar como gate pre-implementación la calidad, completitud, consistencia y verificabilidad de los requisitos y artefactos de diseño (spec, plan, research, data-model, contratos, quickstart) para la feature 075.
**Created**: 2026-09-21
**Feature**: [spec.md](../spec.md) | Plan: [plan.md](../plan.md)

**Note**: Prueba unitaria de requisitos y diseño (no de implementación). Cada ítem evalúa lo escrito en los artefactos; ninguno verifica comportamiento del sistema.

## Trazabilidad Spec ↔ Plan

- [x] CHK001 ¿Cada requisito funcional (FR-001..FR-013) tiene al menos un componente, artefacto o paso del plan que lo cubra? [Completeness, Spec §FR-001..FR-013, Plan §Summary]
- [x] CHK002 ¿Cada criterio de éxito (SC-001..SC-006) tiene estrategia de verificación declarada en el plan, quickstart o pruebas previstas? [Completeness, Spec §SC-001..SC-006, quickstart]
- [x] CHK003 ¿Los escenarios de usuario P1-P3 están reflejados en pruebas unitarias/integración identificadas por archivo? [Coverage, Spec §US1-4, Plan §Project Structure]
- [x] CHK004 ¿Los límites de alcance (sin cambios de esquema, sin recalcular historia financiera, performance fuera de alcance) están declarados en spec y plan de forma consistente? [Consistency, Spec §Assumptions, Plan §Constraints]
- [x] CHK005 ¿Las rutas de código del plan corresponden a archivos reales del repositorio y no a placeholders? [Clarity, Plan §Project Structure]
- [x] CHK006 ¿Los tres hallazgos de causa raíz del spec están mapeados a decisiones de research y a cambios concretos del plan? [Traceability, Spec §Hallazgo, research.md R1-R4]

## Calidad de Decisiones y Contratos

- [x] CHK007 ¿Cada decisión de research.md declara la alternativa descartada y la razón del descarte? [Completeness, research.md R1-R9]
- [x] CHK008 ¿La herencia del período del arriendo por el mandato (R2) está justificada explícitamente contra FR-001 y FR-005 sin contradecirlos? [Consistency, Spec §FR-001, §FR-005; research R2]
- [x] CHK009 ¿Los límites de los tramos V2 (28-7, 8-17, 18-27) están enunciados sin huecos ni solapes en todos los artefactos donde aparecen? [Clarity, data-model §5, contracts/contratos-dominio.md]
- [x] CHK010 ¿El contrato de dominio especifica precondiciones, postcondiciones e invariantes de la calculadora, incluida la tabla de verdad? [Completeness, contracts/contratos-dominio.md]
- [x] CHK011 ¿El contrato de errores de UI define excepción y mensaje visible para cada modo de fallo relevante? [Completeness, contracts/servicios-renovacion.md §5]
- [x] CHK012 ¿Las firmas y nombres de métodos son consistentes entre plan, data-model, contratos y research? [Consistency, Plan, data-model §4, contracts]
- [x] CHK013 ¿La regla de "última renovación" (orden y desempate) está definida de forma determinística y única en research, data-model y contratos? [Clarity, research R7, data-model §4, contracts/servicios-renovacion.md §3]
- [x] CHK014 ¿El plan documenta el cambio estructural de atomicidad de la renovación de mandato y su justificación de causa raíz? [Completeness, research R3, Plan §Summary]
- [x] CHK015 ¿Está definida la secuencia commit → invalidación de caché → tolerancia de fallo en los contratos de ambos servicios? [Clarity, Spec §FR-012, contracts/servicios-renovacion.md §1-2]
- [x] CHK016 ¿Los artefactos distinguen la superficie de runtime (servicios/UI) de la operativa (script), incluyendo su modo de despliegue? [Clarity, Plan §Project Structure, contracts/cli-remediacion.md]
- [x] CHK017 ¿La unificación de la creación de arriendos a tramos V2 está trazada a FR-003 con sus efectos declarados? [Consistency, research R9, Spec §FR-003]

## Modelo de Datos y Reglas

- [x] CHK018 ¿El data-model documenta todas las entidades, campos y formatos tocados por la feature, incluido el reporte de auditoría? [Completeness, data-model §1-3, §7]
- [x] CHK019 ¿Las reglas de validación (solo ACTIVO, canon, derivados, grupo/día válidos) tienen comportamiento esperado o excepción definida? [Completeness, data-model §6]
- [x] CHK020 ¿Se definen los valores prohibidos (grupo 0 o vacío) y su tratamiento en renovación y auditoría? [Clarity, Spec §FR-007, data-model §6]
- [x] CHK021 ¿Las transiciones de estado permitidas y excluidas (renovar/auditar solo ACTIVO) están documentadas y son consistentes entre secciones? [Consistency, data-model §1-2, §6]
- [x] CHK022 ¿Se declara la estrategia de acceso y el volumen (sin N+1) que justifica la viabilidad del enfoque de auditoría? [Non-Functional, data-model §8, research R5]

## Operación de Auditoría y Remediación

- [x] CHK023 ¿El contrato del CLI define invocación, flags, precondiciones, postcondiciones y garantías? [Completeness, contracts/cli-remediacion.md]
- [x] CHK024 ¿El modo por defecto de solo lectura y la exigencia de `--commit` explícito están especificados sin ambigüedad? [Clarity, Spec §FR-010, contracts/cli-remediacion.md §Invocación]
- [x] CHK025 ¿El alcance (mandatos y arrendamientos ACTIVOS; excluye finalizados/cancelados; sin ejecución automática) es consistente entre spec, research y CLI? [Consistency, Spec §FR-009/§FR-010, research R5, contracts]
- [x] CHK026 ¿El contenido mínimo del reporte (fecha efectiva, valores antes/después, acción) y su destino están definidos? [Completeness, Spec §FR-009, §SC-002, data-model §7, contracts §Comportamiento]
- [x] CHK027 ¿El rollback total de la remediación ante fallo está especificado como garantía del CLI y del plan? [Coverage, Spec §Edge Cases, contracts §Comportamiento]
- [x] CHK028 ¿Los códigos de salida y el manejo de errores de entorno (sin conexión) están definidos? [Clarity, contracts §Códigos de salida]
- [x] CHK029 ¿La herencia de período del mandato (R2) está reflejada en el algoritmo de auditoría descrito en data-model y CLI? [Consistency, data-model §4, research R2, contracts]
- [x] CHK030 ¿El contrato del CLI especifica actualizar solo filas con discrepancia real y ser idempotente en segunda corrida? [Measurability, contracts §Comportamiento, §Postcondiciones]

## Datos TEST y Limpieza

- [x] CHK031 ¿El quickstart define marcadores únicos y verificaciones de ausencia de datos TEST para todas las tablas afectadas? [Completeness, Spec §FR-013, §SC-005, quickstart §6]
- [x] CHK032 ¿Se enumeran todas las entidades derivadas de prueba a limpiar (contratos, propiedades, liquidaciones, recaudos, renovaciones, personas y relaciones)? [Completeness, Spec §FR-013, quickstart §6]
- [x] CHK033 ¿La verificación de limpieza es objetiva (conteos esperados = 0), automatizable en la suite y distingue datos TEST de datos reales? [Measurability, Spec §SC-005, quickstart §6]
- [x] CHK034 ¿Existe criterio explícito de fallo de la feature si quedan registros huérfanos generados por las pruebas? [Acceptance Criteria, Spec §SC-005, Plan tests]
- [x] CHK035 ¿El plan declara la dependencia de una base de pruebas segura con guarda `DATABASE_URL` para integración? [Dependency, Plan §Testing, quickstart §Prerrequisitos]

## Escenarios, Bordes y Ambigüedades Residuales

- [x] CHK036 ¿Los escenarios de fallo, rollback y reintento tienen requisitos y verificación definidos sin ambigüedad? [Coverage, Spec §US3, §Edge Cases, Plan tests]
- [x] CHK037 ¿Los bordes de fecha (cambio de año, 28/29-feb, fin de mes) declaran el grupo y día esperados? [Edge Case, Spec §Edge Cases, data-model §5]
- [x] CHK038 ¿Los artefactos de diseño no introducen reglas nuevas no aprobadas (p. ej. grupo 0 para arriendos) que contradigan el spec? [Conflict, Spec §FR-003/§FR-007, research R9]
- [x] CHK039 ¿El plan enumera los controles de calidad pre-commit a ejecutar (sintaxis, tipado, lint, formato, suites de regresión)? [Completeness, Plan §Constitution Check]

## Notes

- Check items off as completed: `[x]`
- Add comments or findings inline
- Items are numbered sequentially for easy reference
- Traceabilidad: 39/39 ítems referencian al menos una sección, artefacto o marcador de calidad.
- Complementa (no reemplaza) los gates previos: `requirements.md` (calidad general del spec) y `renovacion-grupo-pago.md` (dominio de integridad transaccional y reglas de grupo).
- Evaluación 2026-09-21 (gate pre-implementación): 39/39 ítems pasan contra spec, plan, research, data-model, contratos y quickstart. Brecha detectada y resuelta durante la evaluación: CHK002 (SC-006 no tenía estrategia de verificación) → se añadió la sección 7 "Seguimiento post-release (SC-006)" al quickstart con las consultas de conteo esperado 0.
