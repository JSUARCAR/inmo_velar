# Feature Specification: Liquidación de Propietarios requiere Contrato de Arrendamiento Activo

**Feature Branch**: `076-liquidacion-requiere-arrendamiento`

**Created**: 2026-09-22

**Status**: Draft

**Input**: User description: "El proceso de Liquidación de Propietarios debe exigir, además del Contrato de Mandato activo, un Contrato de Arrendamiento activo asociado a la MISMA propiedad para considerar a un propietario elegible para liquidación. Ingeniería inversa del flujo actual de liquidaciones de propietarios, auditoría de datos existentes para identificar casos generados bajo la regla anterior, eliminación total de datos de prueba (TEST) creados durante la validación, y matriz de validación de 5 combinaciones Mandato/Arrendamiento: cualquier combinación que no sea Mandato Activo + Arrendamiento Activo NO genera liquidación."

## Contexto e ingeniería inversa (estado actual verificado)

El criterio de elegibilidad vigente del módulo de Liquidación de Propietarios considera **únicamente** el Contrato de Mandato en estado ACTIVO:

- La generación **individual** selecciona propiedades cuyo mandato figura activo en el formulario.
- La generación **masiva** recorre los contratos de mandato activos del propietario y genera una liquidación por contrato, sin verificar la existencia ni el estado de un Contrato de Arrendamiento en la propiedad.
- La generación **individual directa** valida la existencia del contrato de mandato y la no duplicidad por período, pero **no valida el estado ACTIVO del mandato ni la existencia de un arrendamiento activo**.

La regla de negocio exigida por el cliente es conjunta: **Mandato Activo + Arrendamiento Activo sobre la misma propiedad = elegible**. Cualquier otra combinación no genera liquidación. La regla debe residir en la lógica de negocio (no solo en la interfaz) y aplicar de forma consistente en generación individual y masiva.

## Clarifications

### Session 2026-09-22

- Q: ¿Cuál es el criterio de identificación de los datos TEST para la limpieza? → A: Bitácora de creación durante la validación: lista explícita de IDs creados por entidad y limpieza dirigida por esa lista.
- Q: ¿Con qué base temporal evalúa la auditoría cada liquidación histórica? → A: Contra el estado de Mandato/Arrendamiento vigente en la FECHA DE GENERACIÓN de la liquidación (reconstrucción histórica con fechas registradas).
- Q: ¿Qué alcance tiene la limpieza TEST sobre datos derivados? → A: Limpiar la bitácora + eliminar cualquier relación derivada que apunte EXCLUSIVAMENTE a entidades de la bitácora (huérfanas).
- Q: ¿Qué requisitos de rendimiento/volumen aplican a la generación masiva y a la auditoría? → A: Requisito de robustez en masiva (no abortar por exclusiones, solo reportar omitidas); las métricas de rendimiento y volumen quedan FUERA del spec y se definen en el plan de implementación.
- Q: ¿Cómo se verifica que el arrendamiento es de la MISMA propiedad que el mandato? → A: Por identificador único del inmueble (ID de propiedad): mandato y arrendamiento deben referenciar exactamente el mismo ID; no se acepta coincidencia por dirección o nombre.
- Q: ¿Qué comportamiento debe tener la limpieza TEST si falla a mitad de su ejecución (reversibilidad/recuperación)? → A: Re-ejecutable e idempotente: la limpieza se re-ejecuta tantas veces como sea necesario; ante un error se detiene sin tocar el resto, los registros inexistentes se ignoran y solo elimina lo de la bitácora de creación.
- Q: ¿Qué requisitos de registro/observabilidad aplican a la auditoría para poder reproducir su resultado? → A: Criterios reproducibles sin persistir resultados: cada ejecución registra los criterios utilizados (fecha de reconstrucción histórica, filtro de regla, período) y el reporte es re-generable a demanda con los mismos criterios; no se almacenan copias de resultados.
- Q: ¿Qué fuente de datos se usa para reconstruir el estado de Mandato/Arrendamiento en la fecha de generación durante la auditoría? → A: Reconstrucción aproximada por intervalo de fechas vigente: se considera ACTIVO si la fecha de generación cae dentro de [FECHA_INICIO, FECHA_FIN] vigente del contrato y el estado actual coincide con el esperado; sin historial de cambios de estado ni cambios de esquema.
- Q: ¿La regla de elegibilidad conjunta también aplica a la liquidación de asesores? → A: No: aplica exclusivamente a la Liquidación de Propietarios; la Liquidación de Asesores queda declarada explícitamente fuera del alcance de esta feature y conserva su lógica actual.

## Matriz de elegibilidad (5 combinaciones — alcance de validación obligatorio)

| # | Mandato | Arrendamiento (misma propiedad) | ¿Genera liquidación? |
|---|---------|----------------------------------|----------------------|
| 1 | ACTIVO  | ACTIVO                           | **Sí**               |
| 2 | ACTIVO  | No existe                        | No                   |
| 3 | ACTIVO  | Inactivo / finalizado            | No                   |
| 4 | No activo (inactivo/finalizado/inexistente) | ACTIVO                | No                   |
| 5 | No activo | No existe / inactivo            | No                   |

Las 5 combinaciones son escenarios de prueba obligatorios de esta feature.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Elegibilidad correcta en la generación de liquidaciones (Priority: P1)

Como usuario administrador, quiero que el sistema solo genere liquidaciones de propietarios cuando la propiedad tiene Contrato de Mandato activo **y** Contrato de Arrendamiento activo, para no liquidar comisiones sobre propiedades que no están arrendadas activamente y cumplir con la regla de negocio definida por la inmobiliaria.

**Why this priority**: Es la regla de negocio central de la feature. Sin aplicarla en generación individual y masiva, el sistema sigue liquidando casos que el cliente considera inelegibles; es la corrección de causa raíz.

**Independent Test**: Crear (o identificar) propiedades que cubran las 5 combinaciones de la matriz Mandato/Arrendamiento y ejecutar la generación individual y la masiva para un período: solo la combinación 1 produce liquidación; las combinaciones 2–5 no producen ninguna y quedan fuera de los candidatos.

**Acceptance Scenarios**:

1. **Given** una propiedad con Contrato de Mandato ACTIVO y Contrato de Arrendamiento ACTIVO en la misma propiedad, **When** se genera la liquidación (individual o masiva), **Then** la liquidación se crea correctamente.
2. **Given** una propiedad con Contrato de Mandato ACTIVO sin Contrato de Arrendamiento, **When** se genera la liquidación, **Then** no se crea ninguna liquidación y la propiedad no aparece como candidata.
3. **Given** una propiedad con Contrato de Mandato ACTIVO y Contrato de Arrendamiento inactivo/finalizado, **When** se genera la liquidación, **Then** no se crea ninguna liquidación.
4. **Given** una propiedad con Contrato de Arrendamiento ACTIVO pero sin Contrato de Mandato activo, **When** se genera la liquidación, **Then** no se crea ninguna liquidación.
5. **Given** una propiedad sin Contrato de Mandato activo ni Contrato de Arrendamiento activo, **When** se genera la liquidación, **Then** no se crea ninguna liquidación.
6. **Given** un propietario con varias propiedades de distintas combinaciones, **When** se ejecuta la generación masiva, **Then** solo se generan liquidaciones para las propiedades de la combinación 1, y el resumen refleja generado/omitido/no elegible con exactitud.
7. **Given** la generación individual desde el formulario, **When** se listan las propiedades disponibles, **Then** solo se ofrecen propiedades de la combinación 1.

---

### User Story 2 - Auditoría de liquidaciones históricas bajo la regla anterior (Priority: P2)

Como usuario administrador, quiero un reporte de solo lectura que identifique las liquidaciones ya generadas con la regla anterior (sin exigir arrendamiento activo), para conocer el alcance real del cambio sin alterar datos históricos.

**Why this priority**: El cambio de regla afecta la percepción de los datos existentes; sin auditoría, el negocio no puede validar el impacto ni decidir acciones sobre casos históricos. Es solo lectura: no modifica ni elimina liquidaciones existentes.

**Independent Test**: Ejecutar la auditoría sobre los datos actuales y verificar que el reporte lista, al menos, toda liquidación cuya propiedad no cumplía la combinación Mandato Activo + Arrendamiento Activo al momento de su generación, con período, propiedad, propietario y motivo de inelegibilidad.

**Acceptance Scenarios**:

1. **Given** existe al menos una liquidación histórica generada para una propiedad que hoy no cumple la combinación completa, **When** se ejecuta la auditoría, **Then** esa liquidación aparece en el reporte con su motivo.
2. **Given** el reporte de auditoría, **When** se revisa, **Then** los datos históricos permanecen sin modificación alguna.
3. **Given** liquidaciones que sí cumplen la regla, **When** se ejecuta la auditoría, **Then** no se marcan como afectadas.

---

### User Story 3 - Eliminación total de datos de prueba (Priority: P2)

Como usuario administrador, quiero que al finalizar la validación de esta feature no quede ningún dato TEST en el sistema (contratos, propiedades, liquidaciones, recaudos y relaciones derivadas), para que producción quede limpia y la auditoría opere solo sobre datos reales.

**Why this priority**: Dato contaminado invalida la auditoría y la operación financiera; es un requisito explícito del cliente y condición de cierre de la feature.

**Independent Test**: Tras ejecutar la limpieza, verificar por consulta directa que no permanece ningún registro identificado como TEST en las entidades afectadas ni huérfanos relacionados.

**Acceptance Scenarios**:

1. **Given** se crearon contratos, propiedades, liquidaciones y recaudos de prueba durante la validación, **When** se ejecuta la limpieza, **Then** no queda ningún registro TEST ni relaciones huérfanas.
2. **Given** la limpieza ejecutada, **When** se consulta el sistema, **Then** los datos reales permanecen intactos.

---

### User Story 4 - Consistencia entre generación individual y masiva (Priority: P1)

Como usuario administrador, quiero que ambos caminos de generación apliquen exactamente la misma regla de elegibilidad, para que el resultado no dependa del botón que se use.

**Why this priority**: Si un camino aplica la regla y el otro no, el cierre mensual produce resultados contradictorios y no auditables.

**Independent Test**: Para el mismo conjunto de propiedades y período, comparar el conjunto de liquidaciones producidas por la generación individual y por la masiva: deben coincidir exactamente con la combinación 1.

**Acceptance Scenarios**:

1. **Given** un período determinado, **When** se ejecuta la generación individual para todas las propiedades candidatas y luego la masiva (o viceversa), **Then** ambas rutas producen el mismo conjunto de propiedades elegibles.
2. **Given** una propiedad inelegible según la matriz, **When** se intenta por cualquiera de los dos caminos, **Then** ninguna ruta crea la liquidación.
3. **Given** la regla aplicada, **When** se revisa el mensaje mostrado al usuario en cada ruta, **Then** la causa de exclusión se comunica de forma clara (no elegible: sin arrendamiento activo / sin mandato activo).

---

### Edge Cases

- ¿Propiedad con CONTRATOS DE ARRENDAMIENTO MÚLTIPLES (uno activo, otro finalizado)? → Basta con que exista al menos un arrendamiento ACTIVO en la misma propiedad para ser elegible (combinación 1).
- ¿Propiedad con MÚLTIPLES MANDATOS (uno activo)? → Se evalúa por contrato: solo los mandatos activos de propiedades con arrendamiento activo generan liquidación.
- ¿Arrendamiento activo asociado a una propiedad DIFERENTE de la del mandato? → No cuenta: el arrendamiento debe ser de la MISMA propiedad, verificada por identificador único del inmueble (no por coincidencia de dirección o nombre).
- ¿Contrato que cambia de estado durante la generación masiva (carrera de condiciones)? → La validación de elegibilidad se evalúa al momento de decidir cada generación, no solo al inicio del proceso.
- ¿Canon de mandato en 0 con combinación válida? → Sigue elegible; la liquidación se crea con comisión 0.
- ¿Liquidación ya existente para la combinación 1 en el período? → Comportamiento actual de omisión por duplicado se mantiene (ya existía), sin cambiarla por esta feature.
- ¿Período con formato inválido? → Se rechaza antes de iniciar, como hoy.
- ¿Propietario sin ninguna propiedad elegible en la generación masiva? → Mensaje informativo de "sin propietarios/propiedades elegibles", no error genérico.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El sistema DEBE considerar elegible para liquidación solo la combinación: Contrato de Mandato ACTIVO + Contrato de Arrendamiento ACTIVO sobre la MISMA propiedad, verificada por el IDENTIFICADOR ÚNICO del inmueble (mandato y arrendamiento deben referenciar exactamente el mismo ID de propiedad; no se acepta coincidencia por dirección o nombre).
- **FR-002**: El sistema NO DEBE generar liquidaciones para ninguna de las combinaciones 2 a 5 de la matriz de elegibilidad.
- **FR-003**: La regla DEBE residir en la lógica de negocio del sistema (no únicamente en la interfaz), de modo que no pueda eludirse por ninguna ruta de uso.
- **FR-004**: La generación individual y la generación masiva DEBEN aplicar exactamente la misma regla de elegibilidad, produciendo conjuntos de resultados idénticos para el mismo período y datos.
- **FR-005**: El formulario de generación individual DEBE listar únicamente propiedades que cumplan la combinación elegible.
- **FR-006**: La generación masiva DEBE excluir las propiedades inelegibles y reportar el resultado con claridad (generadas / ya existían / no elegibles / con error), sin fallar masivamente por las exclusiones.
- **FR-007**: El sistema DEBE generar un reporte de auditoría de SOLO LECTURA de liquidaciones históricas creadas bajo la regla anterior, indicando período, propiedad, propietario y motivo de inelegibilidad; la auditoría NO modifica ni elimina datos históricos. Cada ejecución DEBE registrar los criterios utilizados (fecha de reconstrucción histórica, filtro de regla, período) de modo que el reporte sea re-generable a demanda con los mismos criterios, sin persistir copias de resultados. La reconstrucción del estado vigente en la fecha de generación DEBE hacerse por intervalo de fechas: una liquidación se evalúa como ACTIVO si su fecha de generación cae dentro de [FECHA_INICIO, FECHA_FIN] vigente del contrato y el estado actual coincide con el esperado, sin requerir historial de cambios de estado.
- **FR-008**: La feature DEBE incluir la eliminación completa de todos los datos TEST creados durante la validación (contratos, propiedades, liquidaciones, recaudos y relaciones derivadas). La limpieza se dirige por la bitácora de creación y elimina además toda relación derivada que apunte EXCLUSIVAMENTE a entidades de la bitácora; los datos reales NO se tocan. La limpieza DEBE ser **re-ejecutable e idempotente**: ante un error a mitad de ejecución se detiene sin alterar el resto, los registros inexistentes se ignoran y se puede volver a ejecutar sin efectos colaterales.
- **FR-009**: Las 5 combinaciones de la matriz Mandato/Arrendamiento DEBEN quedar cubiertas como escenarios de validación obligatorios antes de cerrar la feature.
- **FR-010**: Los mensajes al usuario cuando una propiedad queda excluida DEBEN explicar la causa en lenguaje de negocio (p. ej., "sin contrato de arrendamiento activo").

### Key Entities *(include if feature involves data)*

- **Propiedad**: Inmueble que puede tener un contrato de mandato y un contrato de arrendamiento; es el punto de unión que determina la elegibilidad conjunta.
- **Contrato de Mandato**: Relación de administración con el propietario; debe estar ACTIVO para habilitar liquidación. Aporta canon y porcentaje de comisión.
- **Contrato de Arrendamiento**: Relación de arrendamiento de la propiedad; debe estar ACTIVO en la MISMA propiedad para habilitar liquidación.
- **Liquidación de Propietario**: Resultado financiero mensual por contrato elegible (comisión, IVA, gastos, incidentes), con estado de proceso/aprobación/pago.
- **Recaudo / Cuota de incidente**: Movimientos financieros asociados a la liquidación y a la propiedad; afectados por la limpieza TEST y por el contexto de la liquidación.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% de las liquidaciones generadas tras el cambio cumplen la combinación Mandato Activo + Arrendamiento Activo en la misma propiedad (0 generadas bajo las combinaciones 2–5).
- **SC-002**: Las 5 combinaciones de la matriz producen el resultado esperado en generación individual y en masiva (10/10 verificaciones correctas: 5 combinaciones × 2 rutas).
- **SC-003**: Para un mismo período y conjunto de datos, la generación individual y la masiva producen conjuntos de propiedades elegibles idénticos (0 discrepancias).
- **SC-004**: El reporte de auditoría cubre el 100% de las liquidaciones históricas del sistema y marca exactamente las que no cumplían la regla **evaluada contra el estado de Mandato/Arrendamiento vigente en la fecha de generación de cada liquidación**, con 0 modificaciones a datos históricos. La evaluación del estado vigente usa la reconstrucción aproximada por intervalo de fechas ([FECHA_INICIO, FECHA_FIN] vigente con estado actual coincidente). El reporte es re-generable a demanda con los mismos criterios registrados en cada ejecución.
- **SC-005**: Después de la limpieza, existen 0 registros identificados como TEST y 0 relaciones huérfanas derivadas; los datos reales permanecen intactos. La limpieza puede re-ejecutarse sin efectos colaterales (idempotente) y ante un fallo a mitad de ejecución detiene el proceso sin tocar el resto.
- **SC-006**: El usuario identifica la causa de exclusión de cada propiedad no elegible sin asistencia técnica (mensajes de negocio claros en ambas rutas).
- **SC-007**: El cierre mensual de liquidaciones puede completarse sin errores masivos, con desglose de resultados confiable (generadas / ya existían / no elegibles / con error); la generación masiva no se aborta por exclusiones y solo reporta omitidas. Las metas de rendimiento y volumen se fijan en el plan de implementación, fuera del alcance del spec.

## Assumptions

- El arrendamiento que habilita la elegibilidad DEBE pertenecer a la MISMA propiedad que el mandato; un arrendamiento activo de otra propiedad no habilita.
- Con arrendamientos múltiples en la misma propiedad, basta UNO ACTIVO (la existencia de arrendamientos finalizados o inactivos paralelos no deshabilita si existe uno activo).
- Los liquidaciones históricas generadas bajo la regla anterior NO se eliminan ni se re-calculan automáticamente: solo se reportan en la auditoría de solo lectura; cualquier remediación futura sería una decisión de negocio separada.
- Se mantienen sin cambio los comportamientos existentes de cálculo financiero (comisión, IVA, gastos, incidentes), de no duplicidad por contrato/período y de omisión de liquidaciones ya existentes.
- Los estados "activo/inactivo" se definen por los estados de contrato ya vigentes en el sistema (ACTIVO frente a inactivo/finalizado), sin inventar nuevos estados.
- La limpieza TEST se dirige por una bitácora de creación: lista explícita de IDs creados por entidad (contratos, propiedades, liquidaciones, recaudos) durante la validación de esta feature, con limpieza dirigida por esa lista; se ejecuta antes del cierre y los datos reales (fuera de la bitácora) no se tocan.
- Si un contrato cambia de estado durante una generación masiva, rige el estado vigente al momento de evaluar cada propiedad.
- La reconstrucción histórica del estado de Mandato/Arrendamiento en la fecha de generación se realiza por intervalo de fechas vigente (fecha de generación dentro de [FECHA_INICIO, FECHA_FIN] y estado actual coincidente); no existe historial de cambios de estado y no se introducen cambios de esquema.
- La elegibilidad conjunta Mandato Activo + Arrendamiento Activo aplica EXCLUSIVAMENTE a la Liquidación de Propietarios; la Liquidación de Asesores queda fuera del alcance de esta feature y conserva su lógica actual.
