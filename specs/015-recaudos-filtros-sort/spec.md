# Feature Specification: Recaudos - Filtros Avanzados y Ordenamiento de Tabla

**Feature Branch**: `015-recaudos-filtros-sort`

**Created**: 2026-07-05

**Status**: Draft

**Input**: User description: "Ingeniería inversa del módulo Recaudos para incorporar filtros (Pago Contrato, Estado), homologar Filtros Avanzados con Liquidaciones y habilitar ordenamiento de la tabla."

## Clarifications

### Session 2026-07-05

- Q: ¿Qué tipo de componente UI se usa para el filtro "Pago Contrato"? → A: `neuro_select_root` (dropdown estándar) para mantener la homologación visual con el módulo Liquidaciones.
- Q: ¿Qué componente UI se usa para el estado vacío cuando los filtros no producen resultados? → A: Callout `rx.callout` con icono "search" y mensaje "No se encontraron recaudos", siguiendo el patrón existente en Liquidaciones.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Filtro de Pago Contrato en Filtros Avanzados (Priority: P1)

Como usuario del sistema de recaudos, necesito filtrar los registros de pago por el concepto de "Pago Contrato" para identificar rápidamente los pagos asociados a un contrato específico o a un tipo de pago particular.

**Why this priority**: El filtro de Pago Contrato es un requisito nuevo que no existe actualmente en la barra de filtros del módulo, aunque la variable de estado `filter_contrato` ya está definida en el backend. Este filtro permite al usuario refinar la búsqueda por contrato, lo cual es esencial para la gestión diaria de recaudos.

**Independent Test**: Puede probarse completamente navegando al módulo Recaudos, seleccionando un valor en el filtro "Pago Contrato" y verificando que la tabla muestra únicamente los registros correspondientes.

**Acceptance Scenarios**:

1. **Given** que el usuario está en el módulo Recaudos con la tabla cargada, **When** selecciona un valor en el filtro "Pago Contrato", **Then** la tabla se actualiza mostrando solo los recaudos que coinciden con el contrato seleccionado.
2. **Given** que hay un filtro de Pago Contrato activo, **When** el usuario cambia el valor del filtro, **Then** la tabla se recarga con los nuevos resultados y la paginación se reinicia a la página 1.
3. **Given** que el filtro de Pago Contrato tiene un valor seleccionado, **When** el usuario presiona el botón de limpiar filtros, **Then** el filtro se restablece a "Todos" y la tabla muestra todos los registros.

---

### User Story 2 - Filtro de Estado en Filtros Avanzados (Priority: P1)

Como usuario del sistema de recaudos, necesito filtrar los registros por su estado (Pendiente, Vencido, Aplicado, Reversado) para enfocarme en los pagos que requieren acción inmediata o seguimiento.

**Why this priority**: El filtro de Estado es fundamental para la operación diaria. Los usuarios necesitan ver rápidamente qué pagos están pendientes, cuáles están vencidos y cuáles ya fueron procesados. Actualmente existe un filtro de estado en la barra, pero se debe validar que funcione correctamente y que sus opciones estén homologadas con las del módulo de Liquidaciones.

**Independent Test**: Puede probarse navegando al módulo Recaudos, seleccionando "Pendiente" en el filtro Estado, y verificando que solo aparecen recaudos con estado pendiente.

**Acceptance Scenarios**:

1. **Given** que el usuario está en el módulo Recaudos, **When** selecciona "Pendiente" en el filtro Estado, **Then** la tabla muestra únicamente recaudos con estado Pendiente.
2. **Given** que hay un filtro Estado activo, **When** el usuario selecciona "Todos", **Then** la tabla muestra todos los recaudos independientemente de su estado.
3. **Given** que el filtro Estado está en "Todos", **When** el usuario selecciona un estado específico, **Then** la paginación se reinicia a la página 1 y se muestran los resultados filtrados.

---

### User Story 3 - Homologación visual y funcional de Filtros Avanzados con Liquidaciones (Priority: P2)

Como usuario del sistema, necesito que la sección de Filtros Avanzados del módulo Recaudos tenga la misma apariencia, distribución y comportamiento que la del módulo Liquidaciones para mantener una experiencia de usuario consistente.

**Why this priority**: La consistencia entre módulos reduce la curva de aprendizaje y mejora la eficiencia operativa. Los usuarios que trabajan con ambos módulos no deben encontrar diferencias innecesarias en la distribución, orden o comportamiento de los filtros.

**Independent Test**: Puede probarse comparando visualmente ambas pantallas (Recaudos y Liquidaciones) y verificando que los filtros tienen la misma disposición, componentes y comportamiento de búsqueda/limpieza.

**Acceptance Scenarios**:

1. **Given** que el usuario tiene abierto el módulo Liquidaciones y luego navega a Recaudos, **When** observa la sección de filtros, **Then** la distribución, orden de controles y diseño visual son consistentes entre ambos módulos.
2. **Given** que ambos módulos están abiertos, **When** el usuario compara los filtros de búsqueda, **Then** ambos usan el mismo componente de entrada de texto con el mismo estilo y comportamiento (búsqueda al presionar Enter).
3. **Given** que ambos módulos están abiertos, **When** el usuario compara los filtros tipo dropdown, **Then** ambos usan el mismo componente de selección con el mismo estilo, dimensiones y comportamiento de apertura.
4. **Given** que el usuario aplica un filtro en Recaudos, **When** el filtro se activa, **Then** el comportamiento de recarga es equivalente al de Liquidaciones (recarga inmediata al cambiar dropdown, búsqueda al presionar Enter en el campo de texto).

---

### User Story 4 - Ordenamiento ascendente/descendente de la tabla de Recaudos (Priority: P2)

Como usuario del sistema de recaudos, necesito poder ordenar la información de la tabla haciendo clic en los encabezados de las columnas, para encontrar rápidamente los registros de mayor interés (mayores valores, fechas más recientes, estados específicos, etc.).

**Why this priority**: El ordenamiento de la tabla es una funcionalidad que ya existe parcialmente en el módulo. Se debe validar que funcione correctamente en todas las columnas aplicables y que mantenga el rendimiento con grandes volúmenes de datos.

**Independent Test**: Puede probarse haciendo clic en el encabezado de cada columna de la tabla y verificando que los datos se reorganizan en orden ascendente/descendente, manteniendo los filtros activos y la paginación.

**Acceptance Scenarios**:

1. **Given** que el usuario está en el módulo Recaudos con la tabla cargada, **When** hace clic en el encabezado de la columna "Fecha Pago", **Then** la tabla se reordena por fecha de pago en orden descendente (más reciente primero).
2. **Given** que la tabla está ordenada por "Fecha Pago" descendente, **When** hace clic nuevamente en el encabezado "Fecha Pago", **Then** la tabla se reordena por fecha de pago en orden ascendente (más antiguo primero).
3. **Given** que la tabla está ordenada por una columna, **When** hace clic en el encabezado de otra columna, **Then** la tabla se reordena por la nueva columna en orden descendente y la paginación se reinicia a la página 1.
4. **Given** que hay filtros activos y la tabla está ordenada, **When** el usuario cambia un filtro, **Then** el ordenamiento se mantiene y los resultados filtrados se muestran con el mismo criterio de orden.
5. **Given** que la tabla tiene más de 25 registros, **When** el usuario navega entre páginas, **Then** el ordenamiento se mantiene consistente en todas las páginas.
6. **Given** que el usuario hace clic en el encabezado de la columna "Acciones", **Then** NO se produce ningún ordenamiento (la columna Acciones no es ordenable).
7. **Given** que el usuario ordena por una columna de tipo numérico (Valor), **When** se aplica el orden, **Then** el ordenamiento es numérico (no lexicográfico).

---

### Edge Cases

- ¿Qué sucede cuando el usuario selecciona un filtro de Pago Contrato que no tiene resultados? El sistema debe mostrar un callout `rx.callout` con icono "search" y el mensaje "No se encontraron recaudos" sobre la tabla vacía, siguiendo el patrón de Liquidaciones.
- ¿Cómo maneja el sistema filtros combinados que no producen resultados? La tabla debe mostrarse vacía con un callout `rx.callout` informativo, sin errores.
- ¿Qué sucede cuando el usuario cambia rápidamente entre múltiples filtros? El sistema debe procesar solo el último filtro aplicado (debounce o cancelación de requests anteriores).
- ¿Cómo se comporta el ordenamiento con valores nulos o vacíos en una columna? Los valores nulos deben ordenarse al final tanto en orden ascendente como descendente.
- ¿Qué sucede si el usuario intenta ordenar por una columna mientras la tabla está cargando? El sorting debe desactivarse o ignorarse hasta que la carga se complete.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El sistema MUST incorporar un filtro "Pago Contrato" en la sección de Filtros Avanzados del módulo Recaudos, utilizando el componente `neuro_select_root` con opciones cargadas desde la base de datos (contratos activos).
- **FR-002**: El sistema MUST validar que el filtro "Estado" existente en el módulo Recaudos funcione correctamente con las opciones: Todos, Pendiente, Vencido, Aplicado, Reversado.
- **FR-003**: El sistema MUST presentar los filtros avanzados de Recaudos con la misma distribución visual, orden de controles y componentes que el módulo Liquidaciones, usando `neuro_select_root` para dropdowns y `neuro_input` para el campo de búsqueda.
- **FR-004**: El sistema MUST permitir ordenar la tabla de Recaudos haciendo clic en los encabezados de columna, alternando entre orden ascendente y descendente.
- **FR-005**: El sistema MUST excluir la columna "Acciones" del ordenamiento.
- **FR-006**: El sistema MUST mantener los filtros activos, el criterio de ordenamiento y la paginación al realizar cualquier acción de filtrado u ordenamiento.
- **FR-007**: El sistema MUST usar el componente `neuro_button` para el botón de limpiar filtros, con un icono de "X" o "filter-x" que restablezca todos los filtros a sus valores por defecto.
- **FR-008**: El sistema MUST reiniciar la paginación a la página 1 cada vez que se aplique un filtro o se cambie el criterio de ordenamiento.
- **FR-009**: El sistema MUST deshabilitar la interacción de ordenamiento mientras la tabla está en estado de carga para evitar condiciones de carrera.
- **FR-010**: El sistema MUST ordenar valores numéricos (Valor) numéricamente y no lexicográficamente.
- **FR-011**: El sistema MUST ordenar valores de fecha cronológicamente.
- **FR-012**: El sistema MUST ordenar valores de texto alfabéticamente (case-insensitive).
- **FR-013**: El sistema MUST mostrar valores nulos o vacíos al final de la lista tanto en orden ascendente como descendente.
- **FR-014**: El sistema MUST aplicar los filtros de forma inmediata al cambiar un dropdown (sin botón de confirmación), y aplicar la búsqueda de texto solo al presionar Enter.
- **FR-015**: El sistema MUST mantener el ordenamiento aplicado al navegar entre páginas de la tabla.

### Key Entities

- **Recaudo**: Registro de un pago recibido. Atributos clave: ID, fecha de pago, fecha de pago contrato, propiedad (dirección, matrícula), arrendatario (nombre, teléfono), habitante (nombre, teléfono), valor total, método de pago, estado.
- **FiltrosRecaudo**: Estructura de datos que encapsula todos los filtros aplicables a la consulta de recaudos: estado, fechaDesde, fechaHasta, idContrato, búsqueda, sort_by, sort_order, page, page_size.
- **Contrato de Arrendamiento**: Contrato asociado a un recaudo. Se identifica por ID y tiene fecha de pago asociada.
- **EstadoRecaudo**: Enumeración de estados posibles de un recaudo: Pendiente, Vencido, Aplicado, Reversado.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Los usuarios pueden filtrar recaudos por Pago Contrato en menos de 2 segundos desde la selección del filtro.
- **SC-002**: La distribución visual de filtros de Recaudos es idéntica a la de Liquidaciones (misma cantidad de columnas, mismos componentes, mismo orden).
- **SC-003**: Los usuarios pueden ordenar cualquier columna de la tabla con un solo clic, y los resultados se muestran en menos de 2 segundos.
- **SC-004**: Al cambiar entre filtros de Liquidaciones y Recaudos, los usuarios perciben la misma experiencia de usuario (mismos componentes, mismo comportamiento).
- **SC-005**: El 100% de las columnas excepto "Acciones" son ordenables de forma ascendente y descendente.
- **SC-006**: La paginación, filtros activos y criterio de ordenamiento se mantienen consistentes al navegar entre páginas.
- **SC-007**: El rendimiento de la tabla no se degrada con volúmenes de hasta 10,000 registros (tiempo de carga percepción: < 3 segundos).

## Assumptions

- La variable de estado `filter_contrato` ya existe en `RecaudosState` y está conectada al backend a través de `FiltrosRecaudo.id_contrato`, por lo que la implementación del filtro solo requiere agregar el componente UI.
- El filtro de Estado ya existe en la barra de herramientas de Recaudos con las opciones hardcoded: Todos, Pendiente, Vencido, Aplicado, Reversado. Se validará su correcto funcionamiento.
- La infraestructura de ordenamiento (sort_by, sort_order, toggle_sort, SORT_COLUMNS en el repositorio) ya está implementada y funcionando. Se validará que cubre todas las columnas requeridas.
- Los componentes reutilizables `neuro_select_root`, `neuro_input` y `neuro_button` de `neuro_elements.py` están disponibles y son los mismos usados en Liquidaciones.
- La estructura de la barra de herramientas de Liquidaciones (`liquidaciones_toolbar()`) sirve como referencia de diseño para homologar la de Recaudos (`recaudos_toolbar()`).
- No se requieren cambios en el backend (servicio, repositorio, DTOs) ya que la infraestructura de filtros y ordenamiento ya existe.
- El option set del filtro "Pago Contrato" se cargará de la misma manera que en Liquidaciones: desde la base de datos, consultando contratos activos.

## Out of Scope

- Modificaciones al backend (servicios, repositorios, DTOs) — la infraestructura de filtros y ordenamiento ya existe y es suficiente.
- Cambios en la lógica de negocio o reglas de validación de recaudos.
- Nuevo filtro de "Fecha Desde" / "Fecha Hasta" — ya existen en la toolbar actual y se mantienen.
- Paginación del lado del cliente — se mantiene la paginación server-side existente.
- Exportación de datos — funcionalidad existente no afectada por esta feature.
- Cambios en el módulo de Liquidaciones — solo se usa como referencia de diseño.
