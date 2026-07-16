# Feature Specification: Fix ID Seguro - Personas

**Feature Branch**: `bugfix/055-fix-id-seguro-personas`

**Created**: 2026-07-15

**Status**: Draft

**Input**: User description: "Realiza un proceso de ingeniería inversa sobre el módulo de Personas, específicamente en el flujo de creación de una Nueva Persona. Se ha identificado una novedad funcional al seleccionar el rol de Arrendatario. Al intentar seleccionar un valor en el campo ID Seguro (combobox/select), el sistema genera un error que impide continuar con el proceso de registro. Por favor, analiza el flujo completo de la funcionalidad, incluyendo la carga de datos, las validaciones del frontend, la lógica del backend y las relaciones con la base de datos, con el fin de identificar la causa raíz del problema."

## Clarifications

### Session 2026-07-15

- Q: ¿Este fix aplica exclusivamente al campo ID Seguro del rol Arrendatario, o hay otros roles con campos condicionales que también podrían tener el mismo tipo de error? → A: Solo Arrendatario — El fix se limita al campo ID Seguro cuando el rol es Arrendatario.

- Q: ¿Cuál es el error específico que se produce? → A: Error de jerarquía de componentes Radix UI: `PopoverPortal must be used within Popover`. El componente Select/Combobox se renderiza fuera del contexto de Popover requerido por Radix UI.

- Q: Cuando el usuario selecciona "Arrendatario", ¿el combobox debe mostrar un indicador de carga mientras obtiene los tipos de seguro, o se cargan de forma síncrona/inmediata? → A: Carga síncrona — El combobox se puebla inmediatamente sin indicador de carga.

- Q: ¿El formulario de nueva persona se renderiza dentro de un Dialog/Modal, o es una página/vista independiente? → A: Dialog/Modal — El formulario se abre como modal superpuesto a la lista de personas. Esto confirma la causa raíz: el Select dentro del Dialog pierde el contexto de Popover.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Crear Persona con rol Arrendatario (Priority: P1)

Como usuario del sistema inmobiliario, necesito poder crear una persona con el rol de **Arrendatario** seleccionando un valor válido en el campo **ID Seguro** (combobox), para poder completar el registro sin errores.

**Why this priority**: Es la funcionalidad principal reportada con error. Sin esta corrección, el flujo de creación de personas queda bloqueado para arrendatarios, impidiendo la operación core del módulo.

**Independent Test**: Se puede probar abriendo el formulario de nueva persona, seleccionando el rol "Arrendatario" y verificando que el combobox de ID Seguro carga correctamente los valores y permite la selección sin errores de renderizado.

**Acceptance Scenarios**:

1. **Given** el usuario está en el formulario de nueva persona, **When** selecciona el rol "Arrendatario", **Then** el campo ID Seguro se habilita y muestra las opciones disponibles (tipos de seguro) correctamente sin errores de consola.

2. **Given** el campo ID Seguro está visible con opciones cargadas, **When** el usuario selecciona un valor válido del combobox, **Then** la selección se registra sin errores y el formulario permite continuar.

3. **Given** el usuario completa todos los campos obligatorios incluyendo ID Seguro, **When** presiona "Guardar", **Then** la persona se crea exitosamente en el sistema con el tipo de seguro registrado.

---

### User Story 2 - Renderizado correcto del combobox ID Seguro (Priority: P1)

Como sistema, necesito renderizar el componente Select/Combobox de ID Seguro dentro de la jerarquía correcta de componentes Radix UI para evitar errores de `PopoverPortal`.

**Why this priority**: El error reportado (`PopoverPortal must be used within Popover`) indica un problema de jerarquía de componentes, no de carga de datos. Este es el fix principal.

**Independent Test**: Se puede probar verificando que la consola del navegador no muestra errores de Radix UI al renderizar el combobox de ID Seguro.

**Acceptance Scenarios**:

1. **Given** el formulario de nueva persona está renderizado, **When** se selecciona el rol "Arrendatario", **Then** el combobox ID Seguro se renderiza dentro del contexto de Popover correcto sin errores y se puebla inmediatamente con los tipos de seguro disponibles.

2. **Given** el combobox ID Seguro está renderizado con opciones, **When** el usuario abre el dropdown de opciones, **Then** el PopoverPortal se muestra correctamente adjunto al Popover padre.

3. **Given** el combobox está en cualquier estado (cerrado, abierto, con selección), **When** se inspecciona la consola del navegador, **Then** no hay errores de `PopoverPortal must be used within Popover`.

---

### User Story 3 - Validación y persistencia del campo ID Seguro (Priority: P2)

Como sistema, necesito validar que el valor seleccionado en ID Seguro sea un identificador válido y persistirlo correctamente en la base de datos al crear la persona.

**Why this priority**: La validación y persistencia garantizan la integridad de los datos. Un error aquí causaría datos inconsistentes en producción.

**Independent Test**: Se puede probar enviando el formulario con un ID Seguro válido y verificando que el registro se crea correctamente en la base de datos con el campo asociado.

**Acceptance Scenarios**:

1. **Given** el usuario selecciona un ID Seguro válido, **When** envía el formulario, **Then** el sistema valida que el ID corresponde a un registro existente y persiste la relación.

2. **Given** el usuario intenta enviar el formulario sin seleccionar ID Seguro, **When** el campo es obligatorio para el rol Arrendatario, **Then** el sistema muestra un mensaje de validación indicando que el campo es requerido.

3. **Given** la persona se crea exitosamente, **When** se consulta el registro en la base de datos, **Then** el campo ID Seguro contiene el valor seleccionado correctamente vinculado a la persona.

---

### Edge Cases

- ¿Qué sucede cuando la tabla de tipos de seguro está vacía? El sistema debe mostrar un mensaje "No hay opciones disponibles" en el combobox.

- ¿Qué ocurre si el usuario cambia el rol de Arrendatario a otro rol después de haber seleccionado un ID Seguro? El campo debe deshabilitarse o limpiarse según las reglas de negocio.

- ¿Qué sucede si el ID Seguro seleccionado es eliminado de la base de datos mientras el formulario está abierto? El sistema debe detectar la inconsistencia al momento de guardar.

- ¿Qué ocurre si el componente Select se renderiza dentro de un Dialog o Modal? Se debe garantizar que la jerarquía de Popover/Portal sea correcta en todos los contextos de renderizado (ver constitución §16).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El sistema DEBE renderizar el componente Select/Combobox de ID Seguro dentro de la jerarquía correcta de componentes Radix UI (Popover → PopoverPortal).

- **FR-002**: El combobox DEBE mostrar los tipos de seguro disponibles con su identificador y nombre descriptivo.

- **FR-003**: El sistema DEBE validar que el valor seleccionado en ID Seguro corresponde a un registro válido en la tabla de tipos de seguro.

- **FR-004**: El campo ID Seguro DEBE ser obligatorio cuando el rol seleccionado es "Arrendatario".

- **FR-005**: El sistema DEBE persistir correctamente la relación entre la persona y el tipo de seguro en la base de datos.

- **FR-006**: El sistema DEBE mostrar mensajes de error claros cuando la consulta de tipos de seguro falle.

- **FR-007**: El sistema DEBE cargar los tipos de seguro de forma síncrona (sin indicador de carga) dado que el catálogo contiene pocos registros.

- **FR-008**: El campo ID Seguro DEBE deshabilitarse o limpiarse cuando el rol cambia de "Arrendatario" a otro rol.

- **FR-009**: La consola del navegador DEBE estar libre de errores de `PopoverPortal must be used within Popover` al interactuar con el combobox.

### Key Entities

- **Persona**: Entidad principal del módulo. Contiene datos personales básicos (nombre, identificación, contacto) y está asociada a uno o más roles.

- **Rol**: Define la función de la persona en el sistema (Propietario, Arrendatario, Asesor, etc.). Determina qué campos adicionales son requeridos.

- **Tipo Seguro**: Catálogo de tipos de seguro disponibles (ej: todo riesgo, contra terceros, etc.). Se muestra en el combobox ID Seguro cuando el rol es Arrendatario.

- **ID Seguro**: Referencia al tipo de seguro seleccionado para una persona con rol Arrendatario. Es un campo condicional basado en el rol.

- **Dialog/Modal**: Contenedor del formulario de nueva persona. El error ocurre porque el Select/Combobox de ID Seguro intenta renderizar su PopoverPortal fuera del contexto del Dialog padre.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: El 100% de los usuarios pueden completar el formulario de nueva persona con rol Arrendatario sin errores en el campo ID Seguro.

- **SC-002**: El combobox ID Seguro carga las opciones en menos de 2 segundos después de seleccionar el rol Arrendatario.

- **SC-003**: No se reportan errores de `PopoverPortal must be used within Popover` en la consola del navegador después de la corrección.

- **SC-004**: La tasa de éxito en la creación de personas con rol Arrendatario alcanza el 100% cuando todos los campos obligatorios están completos.

- **SC-005**: Los mensajes de error son claras y permiten al usuario identificar y resolver el problema sin asistencia técnica.

## Assumptions

- La tabla de tipos de seguro (o catálogo equivalente) existe en la base de datos y contiene registros válidos.

- El módulo de Personas ya tiene implementada la lógica de roles y campos condicionales.

- El error reportado es de jerarquía de componentes Radix UI (`PopoverPortal must be used within Popover`), confirmado por el usuario.

- La causa raíz es que el Select/Combobox de ID Seguro se renderiza dentro de un Dialog/Modal, y el PopoverPortal pierde el contexto del Popover padre (ver constitución §16 sobre gestión de Portals).

- El campo ID Seguro es específico para el rol Arrendatario y no aplica a otros roles.

- El sistema actual ya cuenta con la infraestructura necesaria para realizar consultas a la base de datos y renderizar componentes de formulario.

- El usuario tiene permisos de escritura en el módulo de Personas para crear registros.

## Out of Scope

- Corrección de errores en otros roles além de Arrendatario.
- Modificaciones a la estructura de la base de datos.
- Cambios en la lógica de negocio de tipos de seguro.
- Optimización de rendimiento de la carga de datos (ya cumple con < 2 segundos).
