# Feature Specification: Corrección de Carga de Datos en Edición de Liquidaciones

**Feature Branch**: `052-fix-edit-liquidacion-data`

**Created**: 2026-07-13

**Status**: Draft

**Input**: User description: "Ingeniería inversa sobre el módulo Liquidación de Asesores para identificar y corregir la causa raíz de una inconsistencia en la carga de información al utilizar la acción Editar. La acción Editar no carga la totalidad de las Propiedades a Liquidar ni los Descuentos Guardados para liquidaciones recién generadas, mientras que liquidaciones históricas (ej. período 2026-05) sí cargan correctamente."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Edición de Liquidación Recién Creada con Carga Completa (Priority: P1)

Un asesor ejecutivo genera una nueva liquidación mensual para un asesor específico. Al presionar la acción "Editar" sobre esa liquidación recién generada, el sistema debe cargar y mostrar en el modal de edición la **totalidad** de las Propiedades a Liquidar y **todos** los Descuentos Guardados que fueron registrados durante el proceso de generación, exactamente como se persistieron en la base de datos.

**Why this priority**: Esta es la funcionalidad núcleo que está rota. Sin ella, la integridad de los datos de liquidación se compromete y los usuarios no pueden confiar en la información que el sistema presenta.

**Independent Test**: Se puede probar completamente generando una liquidación nueva para un asesor con múltiples propiedades y uno o más descuentos, y luego verificando que la acción Editar muestra todos los registros. La prueba es independiente porque solo requiere el módulo de liquidaciones.

**Acceptance Scenarios**:

1. **Given** una liquidación recién generada para un asesor con 3 propiedades y 2 descuentos, **When** el usuario hace clic en "Editar", **Then** el modal carga mostrando las 3 propiedades y los 2 descuentos completos.

2. **Given** una liquidación recién generada para un asesor con una única propiedad y sin descuentos, **When** el usuario hace clic en "Editar", **Then** el modal carga mostrando la propiedad y un estado vacío de descuentos.

3. **Given** una liquidación recién generada para un asesor con múltiples propiedades y múltiples descuentos, **When** el usuario hace clic en "Editar", **Then** la cantidad de Propiedades a Liquidar y Descuentos Guardados en el modal coincide exactamente con lo persistido en PostgreSQL.

---

### User Story 2 - Edición de Liquidaciones Históricas con Consistencia (Priority: P1)

Un asesor ejecutivo accede a liquidaciones generadas en períodos anteriores (ej. 2026-05) y utiliza la acción "Editar". El sistema debe mantener el comportamiento correcto actual: cargar la totalidad de las propiedades y descuentos sin omisiones.

**Why this priority**: Las liquidaciones históricas actualmente funcionan correctamente. La corrección no debe introducir regresiones que comprometan este comportamiento establecido.

**Independent Test**: Se puede probar abriendo el modal de edición de liquidaciones históricas verificando que la información se carga completa, sin cambios respecto al comportamiento actual.

**Acceptance Scenarios**:

1. **Given** una liquidación histórica con 5 propiedades y 3 descuentos, **When** el usuario hace clic en "Editar", **Then** el modal carga mostrando las 5 propiedades y los 3 descuentos sin cambios respecto al comportamiento actual.

2. **Given** múltiples liquidaciones de diferentes períodos, **When** se editan secuencialmente, **Then** cada una muestra exactamente sus propias propiedades y descuentos sin cruzar datos entre períodos.

---

### User Story 3 - Validación de Consistencia End-to-End (Priority: P2)

Un auditor o asesor ejecutivo necesita verificar que la información visible en la interfaz de edición de una liquidación corresponda exactamente con lo almacenado en la base de datos PostgreSQL, sin omisiones ni inconsistencias entre las capas del sistema.

**Why this priority**: La confianza en la integridad de datos entre PostgreSQL, el backend y la UI es fundamental para la toma de decisiones financieras basadas en las liquidaciones.

**Independent Test**: Se puede probar inspeccionando la respuesta de la API para una liquidación y comparando campo por campo con lo que se renderiza en el modal de edición.

**Acceptance Scenarios**:

1. **Given** una liquidación persistida en PostgreSQL con N propiedades y M descuentos, **When** se ejecuta la acción Editar, **Then** la respuesta de la API contiene exactamente N propiedades y M descuentos, y la UI renderiza la misma cantidad sin omisiones.

2. **Given** una liquidación editada y guardada, **When** se vuelve a abrir el modal de edición, **Then** se muestra la información actualizada coincidente con el nuevo estado en PostgreSQL.

---

### User Story 4 - Edición de Liquidaciones con Diferentes Volumenes de Datos (Priority: P2)

Un asesor ejecutivo maneja liquidaciones con variaciones en la cantidad de propiedades y descuentos. La acción Editar debe funcionar de manera consistente sin importar si el asesor tiene una única propiedad o múltiples, y con uno, varios o ningún descuento.

**Why this priority**: La corrección debe ser robusta ante diferentes escenarios de volumen de datos, no solo el caso específico reportado.

**Independent Test**: Se puede probar generando liquidaciones con diferentes combinaciones de propiedades (1, 5, 10+) y descuentos (0, 1, 5+) y verificando que la carga es completa en todos los casos.

**Acceptance Scenarios**:

1. **Given** una liquidación con exactamente 1 propiedad y 0 descuentos, **When** se accede a Editar, **Then** se muestra la propiedad y un estado vacío de descuentos.

2. **Given** una liquidación con 10+ propiedades y 5+ descuentos, **When** se accede a Editar, **Then** se muestran todas las propiedades y todos los descuentos sin truncamiento ni omisión.

3. **Given** una liquidación con propiedades que tienen diferentes estados de selección, **When** se accede a Editar, **Then** el estado de selección de cada propiedad se mantiene fiel al registrado durante la generación.

---

### User Story 5 - Persistencia Correcta durante la Generación (Priority: P1)

Durante el proceso de generación de una nueva liquidación, el sistema debe garantizar que **toda** la información generada (propiedades seleccionadas, montos, descuentos) sea persistida correctamente en la base de datos antes de confirmar la operación al usuario.

**Why this priority**: Si la persistencia falla durante la generación, ninguna cantidad de corrección en la capa de edición resolverá el problema. La integridad comienza en el momento del guardado.

**Independent Test**: Se puede probar generando una liquidación y verificando directamente en la base de datos que todos los registros esperados existen con los valores correctos.

**Acceptance Scenarios**:

1. **Given** un proceso de generación de liquidación con propiedades y descuentos seleccionados, **When** se confirma la generación, **Then** todos los registros de propiedades y descuentos se insertan exitosamente en PostgreSQL sin errores silenciosos.

2. **Given** una generación de liquidación que encuentra un error de persistencia parcial, **When** se detecta la falla, **Then** el sistema reporta el error al usuario y no muestra la liquidación como generada exitosamente.

### Edge Cases

- ¿Qué sucede cuando un asesor tiene propiedades con datos incompletos (ej. monto en cero o nulo) al momento de generar la liquidación?
- ¿Cómo maneja el sistema la edición concurrente de una misma liquidación por dos usuarios simultáneamente?
- ¿Qué ocurre si la conexión a PostgreSQL se interrumpe durante el proceso de generación de una liquidación?
- ¿Cómo se comporta la edición cuando una propiedad asociada a la liquidación ha sido dada de baja o eliminada después de la generación?
- Si la investigación revela que la liquidación 2026-07 tiene datos faltantes en la base de datos, ¿cómo se reconstruyen esos registros sin afectar la integridad referencial de las tablas relacionadas?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El sistema MUST persistir **toda** la información generada durante la creación de una liquidación (todas las propiedades seleccionadas con sus montos, y todos los descuentos registrados) en la base de datos PostgreSQL, garantizando atomicidad en la operación.
- **FR-002**: La acción Editar MUST recuperar de PostgreSQL **la totalidad** de las Propiedades a Liquidar asociadas a la liquidación, sin omisiones ni filtrado parcial.
- **FR-003**: La acción Editar MUST recuperar de PostgreSQL **la totalidad** de los Descuentos Guardados registrados para la liquidación, sin omisiones ni filtrado parcial.
- **FR-004**: La respuesta de la API que alimenta el modal de edición MUST contener exactamente los mismos datos que están almacenados en PostgreSQL para la liquidación solicitada.
- **FR-005**: La interfaz de usuario del modal de edición MUST renderizar la totalidad de los datos recibidos desde la API sin truncamiento, paginación oculta o filtrado adicional.
- **FR-006**: No MUST existir diferencias de comportamiento entre liquidaciones históricas y liquidaciones recién generadas cuando ambas cumplan las mismas condiciones funcionales (mismo número de propiedades, mismos descuentos, mismo período).
- **FR-007**: El sistema MUST validar la integridad de los datos persistidos durante la generación, reportando errores explícitos al usuario si la persistencia parcial ocurre.
- **FR-009**: Si la investigación revela que liquidaciones existentes tienen datos faltantes en la base de datos (no solo ausentes en la recuperación), el sistema MUST incluir un script de migración para reconstruir los registros faltantes, garantizando que la liquidación 2026-07 y cualquier otra afectada muestren los datos correctos.
- **FR-008**: La edición de una liquidación existente MUST preserve la integridad de los datos originales, permitiendo modificaciones solo sobre los campos habilitados para edición.

### Key Entities

- **Liquidación**: Representación mensual de comisiones y pagos para un asesor en un período específico (YYYY-MM). Contiene el estado de la liquidación, el asesor asociado y el período operativo.
- **Propiedad a Liquidar**: Cada unidad inmobiliaria incluida en una liquidación, con su monto, estado de selección y relación con el contrato/propiedad original. Puede haber múltiples propiedades por liquidación.
- **Descuento Guardado**: Cada descuento registrado durante la generación o edición de una liquidación, con su monto, concepto y relación con la liquidación. Puede haber múltiples descuentos o ninguno.
- **Asesor**: Persona cuyas comisiones se liquidan. Un asesor puede tener múltiples liquidaciones (una por período) y cada liquidación puede incluir múltiples propiedades.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: La liquidación del período 2026-07 para CRISTIAN JAMIOY muestra exactamente las mismas Propiedades a Liquidar y los mismos Descuentos Guardados que fueron registrados durante su generación, verificable tanto en la UI como en PostgreSQL.
- **SC-002**: 100% de las liquidaciones editadas (históricas y nuevas) muestran la totalidad de propiedades y descuentos persistidos, sin excepción.
- **SC-003**: La cantidad de Propiedades a Liquidar en el modal de edición coincide exactamente (±0) con la cantidad de registros en la tabla correspondiente de PostgreSQL para cada liquidación.
- **SC-004**: La cantidad de Descuentos Guardados en el modal de edición coincide exactamente (±0) con la cantidad de registros en la tabla correspondiente de PostgreSQL para cada liquidación.
- **SC-005**: No se introducen regresiones funcionales: las liquidaciones que funcionaban correctamente antes de la corrección continúan funcionando con el mismo comportamiento.
- **SC-006**: El proceso de generación de nuevas liquidaciones persiste correctamente el 100% de los datos seleccionados, verificable por auditoría directa en PostgreSQL.
- **SC-007**: Si se ejecuta migración de datos para liquidaciones afectadas, todos los registros reconstruidos pasan la validación de integridad referencial y son visibles en la UI de edición con la misma cantidad de propiedades y descuentos que durante la generación original.

## Clarifications

### Session 2026-07-13

- Q: Si la investigación revela que la liquidación 2026-07 tiene datos faltantes directamente en la base de datos (no solo ausentes en la recuperación), ¿el alcance de la corrección debe incluir migración de datos? → A: Incluir migración de datos para liquidaciones afectadas (2026-07 y cualquier otra con datos faltantes).

## Assumptions

- La estructura de la base de datos PostgreSQL contiene tablas separadas para liquidaciones, propiedades a liquidar y descuentos guardados, con relaciones de integridad referencial entre ellas.
- El backend (API) expone un endpoint específico para cargar los datos de edición de una liquidación por su identificador.
- La interfaz de usuario (Reflex) consume la respuesta del endpoint y renderiza los datos en un modal de edición.
- El comportamiento correcto de las liquidaciones históricas (ej. período 2026-05) sirve como referencia de validación para las liquidaciones problemáticas (ej. período 2026-07).
- Las diferencias de comportamiento no están relacionadas con cambios en la estructura de la base de datos entre períodos, sino con la lógica de persistencia o recuperación de datos.
- El problema es reproducible de forma consistente con el caso del asesor CRISTIAN JAMIOY en el período 2026-07.
