# Feature Specification: Fix Propiedades a Liquidar

**Feature Branch**: `053-fix-propiedades-liquidacion`

**Created**: 2026-07-13

**Status**: Draft

**Input**: User description: "Ingeniería inversa del módulo Liquidación de Asesores para diagnosticar y corregir la causa raíz por la cual el sistema no incorpora la totalidad de las propiedades que cumplen las condiciones para ser liquidadas durante la generación de una Nueva Liquidación."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Generación correcta de Nueva Liquidación (Priority: P1)

Un asesor inmobiliario selecciona un asesor, define el período de liquidación y genera una Nueva Liquidación. El sistema debe cargar y mostrar TODAS las propiedades con Contratos de Arrendamiento activos que correspondan al asesor seleccionado, incluyéndolas automáticamente en la liquidación generada.

**Why this priority**: Es la funcionalidad core del módulo. Si el sistema no carga todas las propiedades elegibles, la liquidación es incompleta y genera pérdidas financieras para la inmobiliaria y los asesores.

**Independent Test**: Se puede probar seleccionando el asesor CRISTIAN JAMIOY (46 propiedades activas) y verificando que la liquidación del período 2026-07 incluya las 46 propiedades, no solo 2.

**Acceptance Scenarios**:

1. **Given** un asesor con 46 propiedades con Contratos de Arrendamiento activos, **When** se genera una Nueva Liquidación para el período 2026-07, **Then** el sistema incorpora las 46 propiedades en la liquidación generada.
2. **Given** un asesor con un único contrato activo, **When** se genera una Nueva Liquidación, **Then** el sistema incorpora exactamente esa 1 propiedad.
3. **Given** un asesor con contratos activos e inactivos, **When** se genera una Nueva Liquidación, **Then** el sistema incorpora únicamente los contratos activos y excluye los inactivos.
4. **Given** un asesor con contratos ya liquidados para el mismo período, **When** se genera una Nueva Liquidación, **Then** el sistema excluye los contratos ya liquidados e incluye los pendientes.
5. **Given** un asesor con contratos de diferentes períodos operativos, **When** se genera una Nueva Liquidación para un período específico, **Then** el sistema incorpora únicamente los contratos correspondientes al período seleccionado.

---

### User Story 2 - Visualización completa de propiedades en la interfaz (Priority: P1)

El usuario debe visualizar en la interfaz (UI) la totalidad de las propiedades incluidas en la liquidación, sin restricciones de paginación, límites de renderizado o truncamiento que impidan ver todos los registros.

**Why this priority**: Incluso si el backend retorna correctamente todas las propiedades, la UI debe renderizarlas todas para que el usuario pueda verificar y operar con la información completa.

**Independent Test**: Se puede probar seleccionando un asesor con muchas propiedades y verificando que todas se muestran en la interfaz sin necesidad de paginación adicional o scroll oculto.

**Acceptance Scenarios**:

1. **Given** una liquidación con 46 propiedades, **When** el usuario abre la vista de la liquidación, **Then** las 46 propiedades son visibles en la interfaz.
2. **Given** una liquidación con múltiples propiedades, **When** el usuario revisa la lista, **Then** no existen restricciones de paginación que oculten registros.
3. **Given** una liquidación generada, **When** el usuario compara la cantidad de propiedades mostradas en UI con las almacenadas en PostgreSQL, **Then** los valores coinciden exactamente.

---

### User Story 3 - Consistencia entre backend y base de datos (Priority: P2)

La cantidad de propiedades incluidas en la liquidación debe coincidir exactamente con la cantidad de contratos elegibles almacenados en PostgreSQL para el asesor y período correspondiente.

**Why this priority**: Garantiza la integridad de datos entre las capas del sistema y previene discrepancias que puedan causar problemas financieros o de auditoría.

**Independent Test**: Se puede ejecutar una consulta SQL directa en PostgreSQL para contar contratos activos de un asesor y comparar con el conteo retornado por el backend.

**Acceptance Scenarios**:

1. **Given** un asesor con N contratos activos en PostgreSQL, **When** se ejecuta el proceso de generación de liquidación, **Then** la respuesta del backend contiene exactamente N propiedades.
2. **Given** una liquidación generada, **When** se consulta la base de datos, **Then** los registros almacenados coinciden con los enviados al frontend.

---

### User Story 4 - Comportamiento consistente para todos los asesores (Priority: P2)

El proceso de generación de nuevas liquidaciones debe comportarse de manera consistente y predecible para todos los asesores del sistema, sin importar la cantidad de propiedades que tengan asignadas.

**Why this priority**: La solución no debe ser un parche puntual para un caso específico, sino una corrección systemic que beneficie a todos los asesores.

**Independent Test**: Se puede probar con múltiples asesores con diferentes cantidades de propiedades (1, 5, 20, 50+) y verificar que todos obtienen resultados correctos.

**Acceptance Scenarios**:

1. **Given** múltiples asesores con diferentes cantidades de propiedades activas, **When** se generan liquidaciones para cada uno, **Then** cada liquidación incluye la totalidad de propiedades elegibles de su asesor.
2. **Given** un asesor sin contratos activos, **When** se genera una Nueva Liquidación, **Then** el sistema muestra un mensaje indicando que no hay propiedades elegibles.

---

### Edge Cases

- ¿Qué sucede cuando un asesor tiene propiedades con contratos en estado LEGAL? Se deben excluir hasta que estén en estado ACTIVO.
- ¿Cómo maneja el sistema un período de liquidación que no tiene contratos activos para ningún asesor?
- ¿Qué ocurre si un contrato cambia de estado (activo → inactivo) durante el proceso de generación de liquidación?
- ¿Cómo se maneja la concurrente cuando dos usuarios generan liquidaciones para el mismo asesor y período simultáneamente?
- Si un contrato fue liquidado para el mismo período en una liquidación que luego fue eliminada, el contrato SÍ se reincorpora como elegible para una nueva liquidación.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El sistema MUST identificar y recuperar TODOS los contratos de arrendamiento activos asociados a un asesor específico desde PostgreSQL.
- **FR-002**: El sistema MUST incluir automáticamente en la nueva liquidación todos los contratos con estado ACTIVO que no hayan sido liquidados para el mismo período.
- **FR-003**: El sistema MUST excluir únicamente los contratos que realmente no cumplan las reglas de negocio (FINALIZADO, CANCELADO, LEGAL, ya liquidados para el mismo período).
- **FR-004**: El sistema MUST garantizar que la cantidad de propiedades incluidas en la liquidación coincida exactamente con la cantidad de contratos elegibles en PostgreSQL.
- **FR-005**: El sistema MUST presentar en la interfaz la totalidad de las propiedades recuperadas, sin restricciones de renderizado, paginación o límites artificiales.
- **FR-006**: El sistema MUST mantener la integridad de información entre PostgreSQL, el backend y la UI/UX en todo el proceso.
- **FR-007**: El proceso de generación MUST comportarse de manera consistente para todos los asesores del sistema.
- **FR-008**: El sistema MUST preservar el comportamiento existente y no introducir regresiones funcionales en el módulo Liquidación de Asesores.
- **FR-009**: El sistema MUST validar que los contratos no estén ya liquidados para el mismo período antes de incluirlos en una nueva liquidación.
- **FR-010**: El sistema MUST considerar correctamente todos los contratos de arrendamiento activos asociados al asesor, independientemente de su cantidad o distribución.

### Key Entities

- **Asesor**: Representa un asesor inmobiliario. Tiene una relación uno-a-múltiples con Propiedades.
- **Propiedad**: Representa una propiedad inmobiliaria. Tiene múltiples contratos de arrendamiento a lo largo del tiempo (relación 1:N), pero solo un contrato en estado ACTIVO a la vez. Pertenecce a un asesor.
- **Contrato de Arrendamiento**: Acuerdo de alquiler de una propiedad. Tiene un estado (ACTIVO, FINALIZADO, CANCELADO, LEGAL), un período operativo y está asociado a una propiedad.
- **Liquidación**: Registro financiero que agrupa las comisiones de un asesor para un período específico (mensual, ej. 2026-07). Contiene múltiples Propiedades a Liquidar.
- **Propiedad a Liquidar**: Registro intermedio que vincula una propiedad con una liquidación, incluyendo los valores calculados para esa propiedad en el período.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: El asesor CRISTIAN JAMIOY visualiza la totalidad de las 46 propiedades con Contratos de Arrendamiento Activos en la liquidación del período 2026-07.
- **SC-002**: La cantidad de contratos incluidos en la liquidación coincide exactamente con los contratos elegibles almacenados en PostgreSQL (100% de coincidencia).
- **SC-003**: El proceso de generación de nuevas liquidaciones funciona correctamente para el 100% de los asesores del sistema.
- **SC-004**: No se introducen regresiones funcionales en el módulo Liquidación de Asesores (los escenarios existentes continúan funcionando correctamente).
- **SC-005**: La información presentada en la interfaz es consistente con los datos recuperados desde PostgreSQL (0 discrepancias entre backend y UI).
- **SC-006**: El rendimiento del proceso de generación de liquidaciones no se degrada con el incremento en la cantidad de propiedades procesadas.

## Clarifications

### Session 2026-07-13

- Q: Cuando se elimina una liquidación, ¿los contratos que participaron en ella deben volver a ser elegibles? → A: Sí, reincorporar — al eliminar la liquidación, los contratos vuelven a ser elegibles para una nueva liquidación en el mismo período.
- Q: ¿Cuáles son los estados posibles de un Contrato de Arrendamiento? → A: ACTIVO, FINALIZADO, CANCELADO, LEGAL. Solo los contratos en estado ACTIVO son elegibles para liquidación.
- Q: ¿Cuál es la relación entre Propiedad y Contrato de Arrendamiento? → A: 1:N — una propiedad puede tener múltiples contratos históricos, pero solo 1 activo a la vez.
- Q: ¿Qué representa un 'período operativo' en el sistema? → A: Mensual — cada mes es un período (ej. 2026-07).
- Q: ¿Existen reglas de negocio adicionales más allá del estado del contrato para determinar elegibilidad? → A: No — solo se requiere que el contrato esté en estado ACTIVO y no haya sido liquidado en el mismo período.

## Assumptions

- La base de datos PostgreSQL contiene la información correcta de contratos activos para cada asesor.
- Las relaciones entre Asesores, Propiedades y Contratos de Arrendamiento en la base de datos son correctas y están debidamente normalizadas.
- El módulo de Liquidación de Asesores ya existe y tiene funcionalidad básica implementada; este feature es una corrección/optimización, no un desarrollo desde cero.
- Las reglas de negocio para determinar qué contratos son elegibles están definidas y documentadas en el sistema actual.
- El problema identificado (solo 2 de 46 propiedades) es causado por una lógica de filtrado, consulta o renderizado defectuosa, no por datos faltantes en la base de datos.
- No se requieren cambios en la estructura de la base de datos (esquema), solo en la lógica de consulta y/o presentación.
