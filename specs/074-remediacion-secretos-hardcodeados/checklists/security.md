# Checklist de Requisitos de Seguridad: Remediación de Credenciales Hardcodeadas y Datos Sensibles Expuestos

**Purpose**: Validar la calidad (completitud, claridad, consistencia y medición) de los requisitos de la spec en las áreas de secretos en árbol/fail-fast y detección automatizada en CI, desde la perspectiva de quien ejecuta la remediación
**Created**: 2026-09-14
**Feature**: [spec.md](../spec.md)
**Enfoque**: secretos en árbol + configuración externa/fail-fast · detección automatizada en CI
**Profundidad**: estándar

## Completitud — Secretos en árbol y configuración externa

- [x] CHK001 ¿Está definido con precisión el alcance de "cero ocurrencias" (archivos, tipos de artefactos y rutas incluidas o excluidas)? [Completeness, Spec §FR-003]
- [x] CHK002 ¿Se documenta el inventario de referencia (credenciales comprometidas y sus ubicaciones conocidas) y quién lo mantiene actualizado? [Completeness, Spec §FR-001, §Assumptions]
- [x] CHK003 ¿Se define qué cuenta como "configuración externa al control de versiones" (variables de entorno, gestor de secretos u otro) para evitar interpretaciones divergentes entre operadores? [Clarity, Spec §FR-002]
- [x] CHK004 ¿Se especifica que el fallo por configuración ausente debe identificar la variable faltante, sin exponer valores ni continuar con supuestos? [Clarity, Spec §FR-004]
- [x] CHK005 ¿Están definidos los requisitos de documentación operativa (qué configuración requiere cada componente) sin reimprimir valores reales? [Completeness, Spec §FR-006]
- [x] CHK006 ¿Se define el destino de los scripts de diagnóstico que apuntan a entornos reales (retiro, reubicación o configuración externa)? [Completeness, Spec §FR-005, §FR-018]
- [x] CHK007 ¿Es consistente la exigencia de "sin valores por defecto" en aplicación, pruebas y scripts? [Consistency, Spec §FR-002, §FR-005]

## Completitud y claridad — Detección automatizada en CI

- [x] CHK008 ¿Están especificados los patrones que las reglas de detección deben cubrir (valores comprometidos y patrones genéricos de credenciales incrustadas)? [Completeness, Spec §FR-013]
- [x] CHK009 ¿Se definen los eventos obligatorios de ejecución del escaneo (push y PR a ramas principales) sin admitir omisión? [Clarity, Spec §FR-013, §Historia 4]
- [x] CHK010 ¿Está definido el comportamiento de bloqueo ante un hallazgo y la prohibición de excepciones para los valores comprometidos? [Completeness, Spec §FR-014]
- [x] CHK011 ¿Se define la política de falsos positivos: valores señuelo permitidos, límites de excepciones y su justificación? [Clarity, Spec §FR-014, §Edge Cases]
- [x] CHK012 ¿Se define el procedimiento para resolver un falso positivo en un cambio limpio sin desactivar las reglas? [Coverage, Spec §Historia 4, escenario 2]
- [x] CHK013 ¿Es objetivamente medible la eficacia del escaneo (prueba controlada de reintroducción con detección del 100 %)? [Measurability, Spec §SC-005]
- [x] CHK014 ¿Se define la acción operativa cuando el escaneo no está disponible o falla (bloquear o continuar) y su registro? [Coverage, Gap]

## Criterios de aceptación y medición

- [x] CHK015 ¿El criterio para declarar "cero ocurrencias" en árbol e historial es objetivo y reproducible? [Measurability, Spec §SC-001, §SC-002]
- [x] CHK016 ¿Existe un criterio de aceptación explícito para el modo de fallo seguro del código cuando falta configuración? [Measurability, Spec §FR-004]
- [x] CHK017 ¿Los umbrales operativos (plazos, porcentajes, resultados) son consistentes entre requisitos funcionales y criterios de éxito? [Consistency, Spec §SC-003, §SC-007]
- [x] CHK018 ¿Está definida la evidencia mínima que operaciones debe registrar y conservar para demostrar cumplimiento? [Completeness, Spec §FR-016, §SC-008]

## Casos límite y cobertura

- [x] CHK019 ¿Se define el tratamiento del informe de auditoría que contiene los literales (enmascarado previo o exclusión del control de versiones)? [Edge Case, Spec §FR-003, §Edge Cases]
- [x] CHK020 ¿Se aborda la replicación de los valores comprometidos en documentación externa al repositorio (runbooks, wikis, correos)? [Coverage, Gap]
- [x] CHK021 ¿Se define cómo verificar operativamente el inventario si el informe de auditoría no está versionado? [Assumption, Spec §Assumptions]
- [x] CHK022 ¿Se especifican los requisitos de datos sintéticos o señuelos para pruebas, de modo que no generen hallazgos recurrentes ni bloqueos indebidos? [Coverage, Spec §FR-012]

## Dependencias, responsables y supuestos

- [x] CHK023 ¿Están validadas las dependencias operativas (acceso y administración de reglas del escáner, capacidad de bloquear fusiones)? [Dependency, Spec §Assumptions]
- [x] CHK024 ¿Están asignados los responsables de cada verificación operativa (búsqueda, escaneo, autorización de excepciones, evidencia)? [Completeness, Spec §FR-016, §Assumptions]
- [x] CHK025 ¿Se documenta la disponibilidad de los registros de acceso y el plan alterno si no existen? [Dependency, Spec §FR-015, §Assumptions]

## Ambigüedades, conflictos y trazabilidad

- [x] CHK026 ¿La identificación de los "valores comprometidos" por hallazgo (sin reimprimir literales) es inequívoca para quien ejecuta la verificación? [Ambiguity, Spec §Key Entities]
- [x] CHK027 ¿Existe conflicto entre excluir credenciales de toda documentación y documentar la configuración requerida? [Conflict, Spec §FR-003, §FR-006]
- [x] CHK028 ¿Se establece una matriz de trazabilidad entre historias, requisitos y criterios de éxito para la ejecución? [Traceability, Gap]

## Notes

- Este checklist evalúa los requisitos escritos, no la implementación: cada ítem pregunta si la spec define, cuantifica o hace medible un aspecto.
- Los ítems marcados `[Gap]` señalan requisitos ausentes que, de confirmarse, deben incorporarse a `spec.md` (o descartarse explícitamente del alcance).
- Generado sin `plan.md` ni `tasks.md` (aún no existen); recalibrar contra el plan cuando se cree.
- Referencia de trazabilidad: secciones `FR-###`, `SC-###`, Historias, Casos límite y Supuestos de `spec.md`.
