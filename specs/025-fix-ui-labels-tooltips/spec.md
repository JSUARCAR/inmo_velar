# Feature Specification: Restablecer Etiquetas Flotantes y Tooltips

**Feature Branch**: `[025-fix-ui-labels-tooltips]`

**Created**: 2026-07-05

**Status**: Draft

**Input**: User description: "Identifico que los siguientes cambios no se encuentran reflejados en el sistema, a pesar de que fueron solicitados e implementados previamente: * La implementación de las Floating Labels (Etiquetas Flotantes) ya no se visualiza. Solicito validar por qué esta funcionalidad dejó de estar disponible y garantizar que sea restablecida en todos los módulos donde fue implementada, respetando el comportamiento definido y las mejores prácticas de UI/UX. * Asimismo, identifico que los tooltips de los botones tampoco se encuentran implementados. Valida esta situación y garantiza que todos los botones incorporen un tooltip descriptivo, consistente y accesible, conforme a los requerimientos funcionales previamente establecidos."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Etiquetas Flotantes (Priority: P1)

Como usuario del sistema, necesito que los campos de entrada de datos muestren etiquetas flotantes para poder identificar qué información debo ingresar sin perder contexto al hacer foco en el campo.

**Why this priority**: Es una funcionalidad previamente establecida y afecta a todos los formularios del sistema, impactando directamente en la experiencia de usuario (UX).

**Independent Test**: Can be fully tested by navigating to any module with a form, interacting with an input field, and observing the floating label behavior.

**Acceptance Scenarios**:

1. **Given** un formulario con campos de texto vacío, **When** el usuario hace foco (click) en un campo, **Then** la etiqueta debe desplazarse hacia arriba (flotar) suavemente y el campo debe permitir la entrada de datos.
2. **Given** un campo de texto que ya contiene información, **When** el formulario se renderiza o el usuario quita el foco, **Then** la etiqueta debe permanecer en la posición flotante superior.
3. **Given** un campo de texto en el que el usuario ha borrado todo el contenido, **When** el usuario quita el foco, **Then** la etiqueta debe regresar a su posición original (dentro del campo).

---

### User Story 2 - Tooltips en Botones (Priority: P2)

Como usuario del sistema, necesito ver un tooltip descriptivo cuando paso el cursor sobre un botón, para entender su función antes de hacer clic.

**Why this priority**: Mejora la accesibilidad y el entendimiento de las acciones disponibles, especialmente para botones con iconos o textos cortos, resolviendo una regresión reportada.

**Independent Test**: Can be fully tested by hovering over buttons across different modules and verifying the tooltip appearance and content.

**Acceptance Scenarios**:

1. **Given** cualquier botón interactivo en la interfaz, **When** el usuario pasa el cursor por encima (hover) durante una fracción de segundo, **Then** un tooltip descriptivo debe aparecer, explicando la acción que realiza el botón.
2. **Given** que el tooltip está visible, **When** el usuario retira el cursor del botón, **Then** el tooltip debe desaparecer.

### Edge Cases

- What happens when el texto del tooltip es muy largo? El tooltip debe ajustarse correctamente y no desbordar la pantalla o cortar el texto.
- How does system handle el comportamiento en dispositivos móviles (donde no hay hover)? En caso de aplicar, las acciones principales deben seguir siendo comprensibles, y el tooltip puede activarse mediante long-press (o mantenerse fuera del alcance de la experiencia móvil, según la librería UI usada).
- What happens when los campos de formulario son de un tipo especial (select, datepicker)? Las floating labels deben comportarse de forma coherente con la implementación original, adaptándose a las particularidades de cada tipo de control de Reflex.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST renderizar floating labels (etiquetas flotantes) en los inputs de todos los formularios de la aplicación.
- **FR-002**: System MUST mantener el estado flotante de la etiqueta si el input contiene un valor (texto o selección).
- **FR-003**: System MUST integrar la funcionalidad de floating labels respetando el "Claude/Anthropic Design System" y las mejores prácticas UI/UX.
- **FR-004**: System MUST mostrar un tooltip descriptivo y accesible en todos los botones de acción principales y secundarios.
- **FR-005**: System MUST asegurar que la solución implementada para floating labels y tooltips sea robusta y no genere conflictos con otros componentes Reflex (z-index, pointer-events, según las reglas del proyecto).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% de los formularios principales restauran la funcionalidad de Floating Labels con transiciones suaves y comportamiento predecible.
- **SC-002**: 100% de los botones de acción cuentan con tooltips descriptivos integrados correctamente, sin generar errores de accesibilidad ni visuales (ej. problemas de z-index).
- **SC-003**: No se presentan regresiones visuales en otros elementos de la interfaz durante la navegación general.
- **SC-004**: Los cambios son compatibles y estables en la compilación y ejecución de Reflex.

## Assumptions

- La librería Reflex y el diseño base soportan implementaciones para tooltips, así como la configuración CSS necesaria (transitions/transformations) para las etiquetas flotantes.
- Los módulos afectados ya cuentan con los textos adecuados para los tooltips (solo falta su habilitación técnica).
- La regresión ocurrió debido a actualizaciones de componentes base (como en estilos o los wrappers customizados), por lo que centralizar las correcciones en dichos componentes solucionará el problema en toda la aplicación.
