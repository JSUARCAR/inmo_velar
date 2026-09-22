# Implementación Checklist: Liquidación requiere Contrato de Arrendamiento Activo

**Purpose**: Validar la calidad y completitud de los requisitos del plan de implementación (spec + plan + research + contracts + quickstart) como unidad lista para implementar.
**Created**: 2026-09-22
**Feature**: [spec.md](../spec.md)
**Uso**: Autor antes de implementar | Rigor: Completo

**Note**: Esta checklist es generada por `/speckit.checklist` y evalúa la CALIDAD DE LOS REQUISITOS, no la implementación.

## Requisito Completeness (¿Están todos los requisitos documentados?)

- [x] CHK001 ¿Define la spec FR-1..FR-10 un criterio de elegibilidad único y completo (Mandato ACTIVO + Arrendamiento ACTIVO en la misma propiedad)? [Completeness, Spec §FR-001..FR-010]
- [x] CHK002 ¿Está documentada la regla para el caso de múltiples arrendamientos en la misma propiedad (uno activo basta)? [Completeness, Spec §Assumptions, Edge Cases]
- [x] CHK003 ¿Queda cubierta explícitamente la regla para mandatos múltiples por propiedad (evaluación por contrato)? [Completeness, Spec §Edge Cases]
- [x] CHK004 ¿Se documenta qué ocurre con liquidaciones ya existentes de la combinación 1 (omisión por duplicado intacta)? [Completeness, Spec §Edge Cases, Assumptions]
- [x] CHK005 ¿Están definidos los requisitos del reporte de auditoría de solo lectura (campos periodo/propiedad/propietario/motivo y criterios registrados)? [Completeness, Spec §FR-007, contracts/auditoria-elegibilidad.md]
- [x] CHK006 ¿Se especifica la bitácora de creación TEST (entidades e IDs) como insumo formal de la limpieza? [Completeness, Spec §FR-008, data-model.md §Bitácora]
- [x] CHK007 ¿Se define la limpieza de relaciones derivadas huérfanas que apuntan exclusivamente a entidades de la bitácora? [Completeness, Spec §FR-008, Q3]
- [x] CHK008 ¿Están documentadas las responsabilidades por capa (dominio/aplicación/infraestructura/presentación) en el plan? [Completeness, Plan §Project Structure]

## Requisito Claridad (¿Los requisitos son específicos y sin ambigüedad?)

- [x] CHK009 ¿Está el término "MISMA propiedad" precisado con el identificador único (ID_PROPIEDAD) y excluyendo dirección/nombre? [Clarity, Spec §FR-001, Q5]
- [x] CHK010 ¿Se cuantifican los motivos de exclusión en lenguaje de negocio para cada combinación 2–5? [Clarity, Spec §FR-010, contracts/auditoria-elegibilidad.md §Motivo]
- [x] CHK011 ¿Está definido el desglose del resultado masivo (generadas/ya existían/no elegibles/error) sin ambigüedad? [Clarity, Spec §FR-006, contracts/servicio-financiero.md §ResultadoGeneracionPropietario]
- [x] CHK012 ¿Queda clara la base temporal de la auditoría (estado vigente en FECHA_GENERACION) frente al estado actual? [Clarity, Spec §SC-004, Q2, research.md §Decision 6]
- [x] CHK013 ¿Está definido el comportamiento de la limpieza ante un fallo a mitad de ejecución (detención sin tocar el resto)? [Clarity, Spec §FR-008, Q6, contracts/limpieza-test.md §Idempotencia]
- [x] CHK014 ¿Se especifican los rangos definidos de las metas de rendimiento (masiva <30s, auditoría <60s, limpieza <10s)? [Clarity, Plan §Technical Context, research.md §Decision 8]
- [x] CHK015 ¿Está definido el formato de reconstrucción histórica (uso de FECHA_INICIO/FECHA_FIN de mandato y arrendamiento) sin ambigüedad funcional? [Clarity, research.md §Decision 6, Spec §SC-004]

## Requisito Consistencia (¿Los requisitos están alineados y sin conflictos?)

- [x] CHK016 ¿Son consistentes FR-005 (formulario solo elegibles) con FR-004 (misma regla individual/masiva) sin contradicciones? [Consistency, Spec §FR-004, FR-005]
- [x] CHK017 ¿Concuerdan las 5 combinaciones de la matriz con los motivos de exclusión de la auditoría y del contrato? [Consistency, Spec §Matriz, contracts/auditoria-elegibilidad.md §Motivo]
- [x] CHK018 ¿Es coherente la clasificación "no elegibles" (nunca error) entre el servicio, el Value Object y el handler masivo? [Consistency, contracts/servicio-financiero.md, Spec §FR-006]
- [x] CHK019 ¿Coinciden el alcance de la limpieza (solo bitácora) entre FR-008, Q1/Q3/Q6 y el contrato de limpieza? [Consistency, Spec §FR-008, contracts/limpieza-test.md]
- [x] CHK020 ¿Concuerda el plan con la arquitectura de capas de la constitución (dominio sin dependencias, repos sin sufijo _sqlite)? [Consistency, Plan §Constitution Check, constitution.md §2.1]
- [x] CHK021 ¿Son compatibles las métricas del plan con las restricciones del spec (robustez en masiva sin abortar)? [Consistency, Plan §Technical Context, Spec §SC-007]
- [x] CHK022 ¿No hay conflicto entre la política Elite (impuesto_4x1000/seguro en 0) y los requisitos de la liquidación? [Consistency, Spec §Assumptions, src/dominio/entidades/liquidacion.py]

## Criterios de Aceptación / Medibilidad (¿Son medibles los criterios de éxito?)

- [x] CHK023 ¿Se puede medir objetivamente SC-001 (0 generadas en combinaciones 2–5)? [Acceptance Criteria, Spec §SC-001]
- [x] CHK024 ¿Es verificable el SC-002 (10/10: 5 combinaciones × 2 rutas) con criterios concretos? [Acceptance Criteria, Spec §SC-002, quickstart.md §Matriz]
- [x] CHK025 ¿Es medible el SC-003 (conjuntos elegibles idénticos sin discrepancias)? [Acceptance Criteria, Spec §SC-003]
- [x] CHK026 ¿Es verificable el SC-004 (100% auditadas, marca exactas por fecha de generación, 0 modificaciones)? [Acceptance Criteria, Spec §SC-004, contracts/auditoria-elegibilidad.md §Regla de oro]
- [x] CHK027 ¿Es medible el SC-005 (0 registros TEST + 0 huérfanas + datos reales intactos + re-ejecución sin efectos)? [Acceptance Criteria, Spec §SC-005, quickstart.md §Limpieza]
- [x] CHK028 ¿Se puede comprobar el SC-006/SC-007 (causa identificable, cierre mensual sin errores masivos)? [Acceptance Criteria, Spec §SC-006, SC-007]

## Cobertura de Escenarios (¿Se abordan todos los flujos?)

- [x] CHK029 ¿Están cubiertos los 5 casos de la matriz en generación individual (incluida la no aparición en el combobox)? [Coverage, Spec §FR-005, quickstart.md §Ruta A]
- [x] CHK030 ¿Están cubiertos los 5 casos de la matriz en generación masiva (resumen y no-abortación)? [Coverage, Spec §FR-006, quickstart.md §Ruta B]
- [x] CHK031 ¿Está cubierto el flujo de usuario "propietario sin ninguna propiedad elegible" (mensaje informativo, no error genérico)? [Coverage, Spec §Edge Cases]
- [x] CHK032 ¿Están definidos los requisitos para la ejecución de la auditoría sobre el 100% de las liquidaciones históricas? [Coverage, Spec §SC-004]
- [x] CHK033 ¿Queda cubierto el flujo de verificación post-limpieza (0 registros TEST y 0 huérfanas) como requisito de salida? [Coverage, Spec §FR-008, quickstart.md §Limpieza]

## Cobertura de Casos Borde (¿Están definidas las condiciones límite?)

- [x] CHK034 ¿Está definido el comportamiento para una propiedad con arrendamientos múltiples (uno activo habilita)? [Edge Case, Spec §Edge Cases]
- [x] CHK035 ¿Está definido el comportamiento para mandatos múltiples por propiedad (se evalúa por contrato)? [Edge Case, Spec §Edge Cases]
- [x] CHK036 ¿Está cubierta la condición de canon de mandato en 0 con combinación válida (sigue elegible, comisión 0)? [Edge Case, Spec §Edge Cases]
- [x] CHK037 ¿Está cubierta la carrera de condiciones (cambio de estado durante la masiva: rige estado al evaluar)? [Edge Case, Spec §Edge Cases, Assumptions]
- [x] CHK038 ¿Está cubierto el arrendamiento activo en propiedad DIFERENTE a la del mandato (no cuenta)? [Edge Case, Spec §Edge Cases, Q5]
- [x] CHK039 ¿Está definido el comportamiento ante período duplicado/ya existente dentro de la nueva regla? [Edge Case, Spec §Edge Cases]
- [x] CHK040 ¿Está cubierto el caso de periodo con formato inválido (rechazo previo como hoy)? [Edge Case, Spec §Edge Cases]

## Requisitos No Funcionales (Rendimiento, Seguridad, RBAC)

- [x] CHK041 ¿Están especificadas las metas de rendimiento/volumen en el plan (no solo en el spec)? [NFR, Plan §Technical Context, research.md §Decision 8, Q4]
- [x] CHK042 ¿Se especifica la robustez de la masiva (no aborta por exclusiones; solo reporta omitidas/no elegibles)? [NFR, Spec §SC-007]
- [x] CHK043 ¿Se exige la validación de roles/RBAC en los handlers de generación existentes (sin nuevas rutas sin RBAC)? [NFR, Plan §Constitution Check, constitution.md §4]
- [x] CHK044 ¿Se prohíbe explícitamente el uso de placeholders no-%s y sufijos _sqlite en los nuevos artefactos? [NFR, Plan §Technical Context, constitution.md §2.3]

## Dependencias y Supuestos (¿Están documentados y validados?)

- [x] CHK045 ¿Están documentados los supuestos del spec (arrendamiento de OTRA propiedad no habilita; arrendamientos múltiples; liquidaciones históricas no recalculadas)? [Assumption, Spec §Assumptions]
- [x] CHK046 ¿Está documentada la decisión de reconstrucción histórica (intervalo FECHA_INICIO/FECHA_FIN) y sus límites en el research? [Dependency, research.md §Decision 6, contracts/auditoria-elegibilidad.md §Nota técnica]
- [x] CHK047 ¿Se documenta que la limpieza depende de la bitácora de creación y no de patrones de nombres/estado? [Dependency, Spec §FR-008, Q1, contracts/limpieza-test.md §Reglas de seguridad]
- [x] CHK048 ¿Está documentada la dependencia de los repos/funciones existentes (obtener_activo_por_propiedad, EstadoContrato.es_activo, ResultadoGeneracionPropietario)? [Dependency, research.md §Piezas reutilizables]

## Ambiguiedades y Conflictos (¿Queda algo por clarificar?)

- [x] CHK049 ¿Está resuelta toda ambigüedad entre "estado actual" y "estado en fecha de generación" en la auditoría? [Ambiguity, Spec §SC-004, Q2]
- [x] CHK050 ¿Están alineadas las definiciones de "no elegible" entre spec, plan, research y contracts sin conflictos de terminología? [Consistency, Gap, Spec §FR-006, contracts/servicio-financiero.md]
- [x] CHK051 ¿Queda alguna contradicción sin resolver entre la clarificación Q4 (métricas en el plan) y el spec SC-007? [Conflict, Spec §SC-007, Plan §Technical Context]
- [x] CHK052 ¿Se declara explícitamente que la remediación de liquidaciones históricas queda fuera del alcance (decisión de negocio separada)? [Assumption, Spec §Assumptions]
- [x] CHK053 ¿Están identificados y resueltos los casos donde el motivo de exclusión podría ser ambiguo (ej. combinación 5: mandato y arrendamiento)? [Clarity, contracts/auditoria-elegibilidad.md §Motivo]
- [x] CHK054 ¿Se requiere una decisión de diseño final sobre cómo obtener el estado histórico exacto del contrato (si las fechas de cambio no son precisas)? [Gap, research.md §Decision 6]

## Notas

- Marcar como `[x]` los ítems aprobados tras revisar spec/plan/research/contracts.
- Agregar comentarios o hallazgos inline.
- Enlazar a las secciones relevantes (spec §, research §, contract §).
- Los ítems se numeran secuencialmente para fácil referencia.