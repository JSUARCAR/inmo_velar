# Feature Specification: Filtros Avanzados Recaudos - Pago Contrato y Ciclo Operativo

**Feature Branch**: `047-recaudos-filtros-avanzados`

**Created**: 2026-07-11

**Status**: Draft

**Input**: User description: "Incorporar nuevos filtros avanzados (Pago Contrato y Ciclo Operativo) en el módulo Recaudos para ampliar las capacidades de búsqueda y segmentación de la información."

## Clarifications

### Session 2026-07-11

- Q: ¿Cuáles son los valores del enumerable "Pago Contrato" que alimenta la columna y el filtro? → A: La columna Pago Contrato muestra un valor numérico que corresponde al día de pago definido en el contrato de arrendamiento. El filtro debe permitir filtrar por valores numéricos (días).
- Q: ¿El filtro Pago Contrato debe permitir selección múltiple? → A: Sí, selección múltiple con operador OR (varios días de pago simultáneamente).

## User Scenarios & Testing

### User Story 1 - Filtrar recaudos por día de pago del contrato (Priority: P1)

Como usuario del módulo Recaudos, deseo filtrar los recaudos según el día de pago numérico definido en el contrato de arrendamiento, para localizar rápidamente los registros que corresponden a una fecha de pago específica.

**Why this priority**: El filtro de Pago Contrato es esencial para la operación diaria. Los usuarios necesitan segmentar recaudos por el día de pago configurado en el contrato (ej: día 1, día 5, día 15) para gestionar cobros, seguimientos y reportes. Sin este filtro, la búsqueda es manual y propensa a errores.

**Independent Test**: Puede probarse completamente abriendo el módulo Recaudos, ingresando un día de pago en el filtro Pago Contrato, y verificando que la tabla muestra solo los registros correspondientes. Se entrega valor inmediato.

**Acceptance Scenarios**:

1. **Given** que existen recaudos con diferentes días de pago de contrato, **When** el usuario ingresa un valor numérico en el filtro "Pago Contrato", **Then** la tabla de recaudos muestra exclusivamente los registros cuyo contrato tiene ese día de pago configurado.
2. **Given** que el usuario selecciona un valor numérico en el filtro Pago Contrato, **When** se aplica el filtro, **Then** los resultados son consistentes con la columna "Pago Contrato" de la tabla principal (mismo dato numérico).
3. **Given** que el usuario selecciona múltiples valores numéricos en el filtro Pago Contrato (si la arquitectura lo soporta), **When** se aplica el filtro, **Then** la tabla muestra todos los registros que coinciden con cualquiera de los valores seleccionados (operador OR).
4. **Given** que el usuario tiene activos otros filtros avanzados, **When** agrega el filtro Pago Contrato, **Then** los resultados se intersectan correctamente con los demás criterios de búsqueda (operador AND entre filtros).

---

### User Story 2 - Filtrar recaudos por ciclo operativo (Priority: P1)

Como usuario del módulo Recaudos, deseo filtrar los recaudos según el Ciclo Operativo asociado a la Liquidación de Propietarios, para segmentar los registros por grupo operativo (Grupo 1, Grupo 2, Grupo 3, Grupo 4, etc.).

**Why this priority**: El ciclo operativo es un criterio fundamental de segmentación en la gestión inmobiliaria. Permite a los usuarios trabajar con grupos de propiedades de forma organizada, facilitando la planificación de cobros, liquidaciones y reportes por ciclo.

**Independent Test**: Puede probarse completamente abriendo el módulo Recaudos, desplegando el filtro Ciclo Operativo, seleccionando un grupo y verificando que la tabla muestra solo los recaudos correspondientes a ese grupo operativo.

**Acceptance Scenarios**:

1. **Given** que existen recaudos asociados a liquidaciones con diferentes ciclos operativos, **When** el usuario despliega el filtro "Ciclo Operativo", **Then** se muestra un listado de opciones obtenido dinámicamente desde los ciclos operativos configurados en el sistema (Grupo 1, Grupo 2, Grupo 3, Grupo 4, u otros).
2. **Given** que el usuario selecciona un grupo operativo del filtro, **When** se aplica el filtro, **Then** la tabla de recaudos muestra exclusivamente los registros cuya Liquidación de Propietarios asociada tiene el ciclo operativo seleccionado.
3. **Given** que el usuario selecciona múltiples grupos operativos (si la arquitectura lo soporta), **When** se aplica el filtro, **Then** la tabla muestra todos los registros que pertenecen a cualquiera de los grupos seleccionados.
4. **Given** que el valor del ciclo operativo proviene de la Liquidación de Propietarios, **When** se consulta el filtro, **Then** el dato es siempre la fuente oficial y no se utiliza información duplicada o calculada de forma independiente.

---

### User Story 3 - Combinación de filtros avanzados (Priority: P2)

Como usuario del módulo Recaudos, deseo combinar los nuevos filtros (Pago Contrato y Ciclo Operativo) con los filtros avanzados existentes, para realizar búsquedas complejas y precisas que satisfagan múltiples criterios simultáneamente.

**Why this priority**: La capacidad de combinar filtros es crítica para escenarios de uso real donde los usuarios necesitan cruzar criterios (ej: "todos los recaudos del día 15 del Grupo 2"). Sin esta capacidad, los filtros individuales tienen utilidad limitada.

**Independent Test**: Puede probarse seleccionando filtros combinados (ej: Pago Contrato + Ciclo Operativo + filtro existente) y verificando que los resultados son la intersección correcta de todos los criterios.

**Acceptance Scenarios**:

1. **Given** que el usuario tiene activos los filtros de Pago Contrato y Ciclo Operativo, **When** aplica ambos simultáneamente, **Then** la tabla muestra solo los registros que cumplen con ambos criterios.
2. **Given** que el usuario tiene activos filtros existentes y los nuevos filtros, **When** aplica la combinación completa, **Then** los resultados son consistentes y precisos, sin degradación perceptible en el tiempo de respuesta.
3. **Given** que el usuario limpia uno de los filtros activos, **When** se remueve el filtro, **Then** los resultados se actualizan correctamente mostrando los registros que cumplen con los filtros restantes.

---

### User Story 4 - Experiencia de usuario consistente (Priority: P2)

Como usuario del módulo Recaudos, deseo que los nuevos filtros tengan el mismo comportamiento visual y de interacción que los filtros existentes, para mantener una experiencia de usuario coherente y predecible.

**Why this priority**: La consistencia de UX reduce la curva de aprendizaje y evita confusión. Los usuarios deben poder usar los nuevos filtros sin instrucciones adicionales.

**Independent Test**: Verificar visualmente que los nuevos filtros tienen la misma apariencia, comportamiento de apertura/cierre, y patrón de interacción que los filtros existentes.

**Acceptance Scenarios**:

1. **Given** que el usuario visualiza la sección de Filtros Avanzados, **When** observa los nuevos filtros, **Then** tienen la misma distribución visual, tipografía, colores y comportamiento de interacción que los filtros existentes.
2. **Given** que el usuario interactúa con los nuevos filtros, **When** despliega, selecciona o limpia un filtro, **Then** el comportamiento de animación, posicionamiento y respuesta es idéntico al de los filtros existentes.

---

### Edge Cases

- ¿Qué sucede cuando no existen recaudos para un día de pago o ciclo operativo específico? El filtro debe mostrar las opciones disponibles, pero la tabla puede estar vacía con un mensaje apropiado.
- ¿Cómo maneja el sistema cuando la Liquidación de Propietarios asociada a un recaudo no tiene ciclo operativo definido? El registro no debe aparecer al filtrar por Ciclo Operativo.
- ¿Qué sucede cuando el contrato de un recaudo no tiene día de pago configurado? El registro no debe aparecer al filtrar por Pago Contrato con un valor específico.
- ¿Qué sucede cuando se aplican todos los filtros disponibles y no hay resultados coincidentes? Se muestra un estado vacío informativo.
- ¿Cómo responde el sistema cuando se cambian los filtros rápidamente (clicks sucesivos)? Los resultados deben actualizarse sin parpadeos ni estados inconsistentes.

## Requirements

### Functional Requirements

- **FR-001**: System MUST display a "Pago Contrato" filter in the advanced filters section of the Recaudos module.
- **FR-002**: System MUST allow users to filter recaudos by the numeric payment day value (día de pago) configured in the rental contract associated with each recibo.
- **FR-003**: System MUST apply the Pago Contrato filter on the backend query, not as a frontend-only filter.
- **FR-004**: System MUST ensure that Pago Contrato filter results are consistent with the numeric value shown in the "Pago Contrato" column of the main Recaudos table.
- **FR-005**: System MUST display a "Ciclo Operativo" filter in the advanced filters section of the Recaudos module.
- **FR-006**: System MUST populate the Ciclo Operativo filter options dynamically from the operational cycles configured in the system (Grupo 1, Grupo 2, Grupo 3, Grupo 4, etc.).
- **FR-007**: System MUST retrieve the Ciclo Operativo value exclusively from the Liquidación de Propietarios associated with each recibo, not from duplicated or independently calculated data.
- **FR-008**: System MUST apply the Ciclo Operativo filter on the backend query.
- **FR-009**: System MUST support applying both new filters individually and in combination with each other and with existing advanced filters.
- **FR-010**: System MUST maintain existing pagination, sorting, and search behavior when new filters are active.
- **FR-011**: System MUST not introduce performance degradation when multiple filters are applied simultaneously.
- **FR-012**: System MUST maintain visual and interaction consistency with existing advanced filters in the module.
- **FR-013**: System MUST support multi-select for filter options (if the current filter architecture supports it), allowing users to select one or more options per filter.

### Key Entities

- **Recaudo (Collection Record)**: A financial collection record associated with a property, contract, and owner settlement. Key attributes include the numeric payment day from the contract, and linked liquidation.
- **Contrato (Contract)**: A rental agreement associated with properties and collections. Contains the configured payment day (día de pago) as a numeric value.
- **Liquidación de Propietarios (Owner Settlement)**: A settlement record that links collections to operational cycles. Source of truth for the "Ciclo Operativo" value.
- **Ciclo Operativo (Operational Cycle)**: A grouping mechanism (Grupo 1, Grupo 2, etc.) that organizes properties and their associated collections into operational groups.
- **Filtros Avanzados (Advanced Filters)**: The UI section containing search/segmentation criteria that are applied as backend queries to filter the Recaudos table.

## Success Criteria

### Measurable Outcomes

- **SC-001**: Users can locate specific recaudos by payment day in under 10 seconds (vs. current manual inspection of each row).
- **SC-002**: Users can filter recaudos by operational cycle group and see results in under 3 seconds.
- **SC-003**: Combined filter queries (Pago Contrato + Ciclo Operativo + existing filters) return results in under 5 seconds for datasets up to 10,000 records.
- **SC-004**: 100% of filter results match the data stored in PostgreSQL (zero discrepancies between filtered results and raw data).
- **SC-005**: Zero functional regressions in existing Recaudos module functionality (pagination, sorting, search, existing filters).
- **SC-006**: Users can complete filter-based searches without additional training, based on visual consistency with existing filters.

## Assumptions

- The existing advanced filters architecture in the Recaudos module supports adding new filter components without structural changes.
- The "Pago Contrato" column in the main Recaudos table already displays the numeric payment day from the contract; the filter will query against this same value.
- The Ciclo Operativo data is already available through the relationship between Recaudos and Liquidación de Propietarios (confirmed by the existing 045-ciclo-operativo-recaudos feature which added the Ciclo Operativo column).
- The backend query infrastructure supports dynamic filter composition (AND between different filters, OR within multi-select options).
- Multi-select capability for filters is either already supported or can be added following the existing filter pattern.
- The Liquidación de Propietarios table already contains the Ciclo Operativo field and is properly linked to Recaudos.
- Performance impact will be minimal as the new filters add indexed query conditions rather than computational overhead.
