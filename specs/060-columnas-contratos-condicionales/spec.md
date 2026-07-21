# Feature Specification: Columnas Condicionales en Tabla de Contratos

**Feature Branch**: `060-columnas-contratos-condicionales`

**Created**: 2026-07-21

**Status**: Draft

**Input**: User description: "Requiero que la tabla del Módulo de Contratos incorpore una columna que permitan visualizar información adicional, dependiendo del tipo de contrato registrado. Para los Contratos de Mandato, se debe mostrar: Nombre del consignatario, Banco, Número de cuenta. Para los Contratos de Arrendamiento, se debe mostrar: Nombre del codeudor, Teléfono del codeudor."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Visualización de información adicional por tipo de contrato (Priority: P1)

Como usuario del sistema de inmobiliaria, necesito ver información adicional relevante en la tabla de contratos dependiendo del tipo de contrato (Mandato o Arrendamiento), para identificar rápidamente los datos clave de cada contrato sin abrir el detalle.

**Why this priority**: Es la funcionalidad central de la solicitud. Sin ella, el usuario debe abrir cada contrato individualmente para ver información que debería estar visible en la tabla.

**Independent Test**: Puede probarse completamente al cargar la tabla de contratos y verificar que los contratos de Mandato muestran consignatario/banco/cuenta, y los de Arrendamiento muestran codeudor/teléfono.

**Acceptance Scenarios**:

1. **Given** existe un contrato de tipo Mandato con consignatario registrado, **When** se carga la tabla de contratos, **Then** se muestra la columna "Información Adicional" con formato: `"Nombre | Banco | Cuenta"`.
2. **Given** existe un contrato de tipo Arrendamiento con codeudor registrado, **When** se carga la tabla de contratos, **Then** se muestra la columna "Información Adicional" con formato: `"Nombre Codeudor | Teléfono"`.
3. **Given** un contrato de tipo Mandato sin consignatario, **When** se carga la tabla, **Then** la columna "Información Adicional" muestra guiones o texto indicando "No registrado".
4. **Given** un contrato de tipo Arrendamiento sin codeudor, **When** se carga la tabla, **Then** la columna "Información Adicional" muestra guiones o texto indicando "No registrado".
5. **Given** un contrato de tipo Mandato con múltiples consignatarios, **When** se carga la tabla, **Then** se muestra solo el consignatario Designado/Principal.

---

### User Story 2 - Validación de integridad de datos (Priority: P2)

Como administrador del sistema, necesito que antes de implementar las nuevas columnas se valide que la información provenga de las entidades y relaciones correctas en la base de datos, para garantizar la consistencia de los datos mostrados.

**Why this priority**: La integridad de datos es crítica para evitar mostrar información incorrecta o incompleta que pueda generar confusión en el negocio.

**Independent Test**: Puede probarse ejecutando consultas de validación contra la base de datos para verificar que las relaciones entre contratos, consignatarios, bancos y codeudores están correctamente definidas.

**Acceptance Scenarios**:

1. **Given** la implementación está en progreso, **When** se ejecutan las validaciones de datos, **Then** se verifica que cada contrato de Mandato tiene acceso válido a sus campos de consignatario, banco y cuenta.
2. **Given** la implementación está en progreso, **When** se ejecutan las validaciones de datos, **Then** se verifica que cada contrato de Arrendamiento tiene acceso válido a los campos de codeudor y teléfono.
3. **Given** existen relaciones huérfanas en la base de datos, **When** se detectan, **Then** se documentan para su corrección antes del despliegue.

---

### User Story 3 - Consistencia visual y funcional (Priority: P3)

Como usuario del sistema, necesito que las nuevas columnas mantengan la consistencia visual y funcional existente en el módulo de contratos, para tener una experiencia de usuario uniforme.

**Why this priority**: La consistencia visual es importante para la usabilidad pero no bloquea la funcionalidad core.

**Independent Test**: Puede probarse verificando que el estilo, alineación y comportamiento de las nuevas columnas coincide con el patrón existente de la tabla.

**Acceptance Scenarios**:

1. **Given** la tabla de contratos tiene un estilo definido, **When** se agregan las nuevas columnas, **Then** mantienen la misma tipografía, espaciado y formato que las columnas existentes.
2. **Given** la tabla permite ordenamiento, **When** se hace clic en el encabezado de las nuevas columnas, **Then** el ordenamiento funciona correctamente.
3. **Given** la tabla permite filtros, **When** se filtra por tipo de contrato, **Then** las columnas condicionales se muestran u ocultan según corresponda.

---

### Edge Cases

- Qué sucede cuando un contrato de Mandato tiene múltiples consignatarios registrados? → Se muestra **solo el consignatario Designado/Principal**.
- Qué sucede cuando el teléfono del codeudor no tiene formato válido? → Se muestra tal cual está registrado, sin validación de formato en la tabla.
- Qué sucede cuando un contrato tiene tipo no definido (ni Mandato ni Arrendamiento)? → La columna de información adicional permanece vacía o muestra "N/A".
- Cómo se comporta la tabla en dispositivos móviles con columnas adicionales? → Las columnas deben ser responsive y permitir scroll horizontal si es necesario.

## Clarifications

### Session 2026-07-21

- Q: ¿Cómo se deben mostrar los múltiples campos de información adicional en la columna? → A: Formato concatenado con separadores visuales (pipe `|`): `"Nombre | Banco | Cuenta"` o `"Nombre Codeudor | Teléfono"`
- Q: Cuando un contrato de Mandato tiene múltiples consignatarios registrados, ¿cuál debe ser el comportamiento? → A: Mostrar solo el consignatario Designado/Principal
- Q: ¿Cómo debe mostrar la tabla el encabezado de la columna de información adicional cuando hay contratos de ambos tipos? → A: Una sola columna con encabezado genérico "Información Adicional" que muestra datos según tipo de fila

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El sistema MUST agregar una columna condicional a la tabla de contratos con encabezado genérico "Información Adicional" que muestre datos específicos según el tipo de contrato de cada fila.
- **FR-002**: Para contratos de tipo Mandato, la columna MUST mostrar formato concatenado: `"Nombre Consignatario | Banco | Número Cuenta"` usando separadores pipe.
- **FR-003**: Para contratos de tipo Arrendamiento, la columna MUST mostrar formato concatenado: `"Nombre Codeudor | Teléfono"` usando separador pipe.
- **FR-004**: Los datos MUST provenir de las entidades y relaciones correctas en la base de datos (verificar integridad antes de implementar).
- **FR-005**: La columna MUST mostrar un indicador de "No registrado" o guiones cuando los campos estén vacíos.
- **FR-006**: Las nuevas columnas MUST mantener la consistencia visual con el resto de la tabla (tipografía, espaciado, colores).
- **FR-007**: El sistema MUST validar la existencia de las relaciones en la base de datos antes de mostrar los datos.
- **FR-008**: Las columnas MUST ser responsive y funcionar correctamente en diferentes tamaños de pantalla.
- **FR-009**: Para contratos de Mandato con múltiples consignatarios, el sistema MUST mostrar únicamente el consignatario Designado/Principal.

### Key Entities

- **Contrato**: Entidad principal que representa un contrato inmobiliario. Tiene un tipo (Mandato o Arrendamiento) y relaciones con otras entidades según su tipo.
- **Consignatario**: Persona designada para recibir el pago en contratos de Mandato. Relación uno a uno con el contrato.
- **Banco**: Institución financiera donde se realiza el depósito. Relación many-to-one con el contrato a través del consignatario.
- **Cuenta**: Número de cuenta bancaria para depósitos. Atributo del consignatario.
- **Codeudor**: Persona que respalda el crédito en contratos de Arrendamiento. Relación uno a uno con el contrato.
- **Teléfono**: Datos de contacto del codeudor. Atributo del codeudor.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Los usuarios pueden identificar el tipo de contrato y su información adicional relevante en menos de 3 segundos al ver la tabla.
- **SC-002**: El 100% de los contratos de Mandato muestran correctamente la información de consignatario/banco/cuenta cuando existe.
- **SC-003**: El 100% de los contratos de Arrendamiento muestran correctamente la información de codeudor/teléfono cuando existe.
- **SC-004**: No se presentan errores de integridad de datos al mostrar las nuevas columnas.
- **SC-005**: La implementación no afecta el rendimiento de carga de la tabla en más de un 10%.

## Assumptions

- La base de datos actual contiene las entidades Consignatario, Banco y Codeudor con sus relaciones definidas hacia la entidad Contrato.
- Los campos de consignatario, banco, cuenta, codeudor y teléfono ya están siendo capturados en el formulario de creación/edición de contratos.
- El tipo de contrato (Mandato o Arrendamiento) está correctamente definido en la entidad Contrato.
- Los usuarios tienen permisos de lectura para acceder a la información de contratos.
- El diseño actual de la tabla permite agregar columnas sin romper la interfaz existente.
- La información de consignatario y codeudor se almacena en tablas separadas con relaciones外键 hacia la tabla de contratos.
