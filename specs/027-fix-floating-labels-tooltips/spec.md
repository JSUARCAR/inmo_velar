# Feature Specification: Corrección de Floating Labels y Tooltips

**Feature Branch**: `027-fix-floating-labels-tooltips`

**Created**: 2026-07-05

**Status**: Draft

**Input**: User description: "Validación integral de Floating Labels y Tooltips en Filtros Avanzados y Modales de todos los módulos"

## Clarifications

### Session 2026-07-05

- Q: ¿Qué temporización de animación deben usar los Floating Labels? → A: Usar timing estándar del sistema: `0.3s cubic-bezier(0.4, 0, 0.2, 1)`
- Q: ¿Cómo debe comportarse el z-index de los tooltips dentro de los modales? → A: Z-tooltip mayor al modal (ej. Z_MODAL + 50) para garantizar visibilidad
- Q: ¿Cómo deben comportarse los floating labels en campos con errores de validación? → A: Label permanece elevado, cambia a color de error, muestra mensaje debajo
- Q: ¿De dónde debe provenir el contenido textual de los tooltips? → A: Archivo de constantes centralizado (ej. `tooltips_text.py`)
- Q: ¿Qué nivel de accesibilidad deben tener los tooltips? → A: Atributos ARIA básicos (`role="tooltip"`, `aria-describedby`)

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Floating Labels funcionales en Filtros Avanzados (Priority: P1)

Como usuario del sistema, al abrir la sección de Filtros Avanzados en cualquier módulo, los labels de los campos de entrada deben mostrarse correctamente como "floating labels" — es decir, el label debe estar posicionado dentro del campo cuando está vacío, y subirse elegantemente al escribir contenido, sin superponerse con el texto ingresado.

**Why this priority**: Los filtros son la primera interacción del usuario con los datos. Si los labels se superponen, el usuario no puede leer qué campo está seleccionando, lo que bloquea la navegación y búsqueda de información.

**Independent Test**: Puede probarse abriendo cualquier módulo (ej. Personas), haciendo clic en "Filtros Avanzados", y verificando que al hacer clic en un campo el label se eleva correctamente sin superponerse con el placeholder o el texto escrito.

**Acceptance Scenarios**:

1. **Given** que el usuario abre los Filtros Avanzados de un módulo, **When** hace clic en un campo de texto, **Then** el label flota hacia arriba con animación suave y el campo muestra su placeholder correctamente.
2. **Given** que el usuario escribe texto en un campo con floating label, **When** el campo tiene contenido, **Then** el label permanece en posición elevada sin superponerse con el texto ingresado.
3. **Given** que el usuario borra el contenido de un campo, **When** el campo queda vacío, **Then** el label regresa a su posición interior original.
4. **Given** que el usuario tiene un campo Select/Combobox en Filtros Avanzados, **When** no ha seleccionado ningún valor, **Then** el label se muestra correctamente sin superponerse con el indicador de dropdown.

---

### User Story 2 - Floating Labels funcionales en Modales (Priority: P1)

Como usuario del sistema, al abrir cualquier modal (ej. "Nueva Liquidación Mensual", "Nueva Persona"), los labels de los campos deben comportarse como floating labels consistentes — elevándose al enfocar el campo y sin superponerse con el contenido de inputs y selects.

**Why this priority**: Los modales contienen formularios críticos de entrada de datos. Si los labels se superponen, el usuario no puede identificar los campos, provocando errores de captura y frustración.

**Independent Test**: Puede probarse abriendo el modal "Nueva Liquidación Mensual" o "Nueva Persona" y verificando que todos los campos tienen floating labels funcionales sin superposiciones.

**Acceptance Scenarios**:

1. **Given** que el usuario abre un modal con formulario, **When** el formulario carga, **Then** todos los campos muestran sus labels en posición interior correcta.
2. **Given** que el usuario hace clic en un campo dentro del modal, **When** el campo recibe foco, **Then** el label flota hacia arriba sin superponerse con el placeholder ni con el valor prellenado (si existe).
3. **Given** que el usuario selecciona un valor en un Select/Combobox dentro del modal, **When** se muestra el valor seleccionado, **Then** el label permanece en posición elevada y el texto del select es completamente legible.
4. **Given** que el usuario cierra y reabre un modal, **When** el modal se reinicializa, **Then** todos los floating labels回归 a su estado inicial correctamente.

---

### User Story 3 - Tooltips funcionales en Filtros Avanzados (Priority: P2)

Como usuario del sistema, al pasar el mouse sobre los iconos de información (ℹ️) en la sección de Filtros Avanzados, debo ver un tooltip con información contextual que me ayude a entender qué hace ese filtro o campo.

**Why this priority**: Los tooltips mejoran la usabilidad al proporcionar ayuda contextual sin saturar la interfaz. Son importantes para la adoptación pero no bloquean la funcionalidad principal.

**Independent Test**: Puede probarse pasando el mouse sobre los iconos de información en los Filtros Avanzados de cualquier módulo y verificando que aparece un tooltip legible.

**Acceptance Scenarios**:

1. **Given** que el usuario está en la sección de Filtros Avanzados, **When** pasa el mouse sobre un icono de información, **Then** aparece un tooltip con texto descriptivo del filtro.
2. **Given** que el tooltip está visible, **When** el usuario mueve el mouse fuera del icono, **Then** el tooltip se oculta correctamente.
3. **Given** que el usuario está en un dispositivo táctil, **When** toca el icono de información, **Then** el tooltip se muestra temporalmente (comportamiento táctil apropiado).

---

### User Story 4 - Tooltips funcionales en Modales (Priority: P2)

Como usuario del sistema, al pasar el mouse sobre los iconos de información dentro de los modales, debo ver tooltips con información contextual relevante sobre el campo o sección.

**Why this priority**: Los tooltips en modales proporcionan guía al usuario durante la captura de datos, reduciendo errores y llamadas de soporte.

**Independent Test**: Puede probarse abriendo cualquier modal y verificando que los iconos de información muestran tooltips al hacer hover.

**Acceptance Scenarios**:

1. **Given** que el usuario tiene un modal abierto con campos que tienen iconos de información, **When** pasa el mouse sobre el icono, **Then** aparece un tooltip descriptivo.
2. **Given** que el tooltip está visible en un modal, **When** el usuario interactúa con otros campos del modal, **Then** el tooltip se cierra automáticamente.

---

### User Story 5 - Consistencia visual entre módulos (Priority: P3)

Como usuario del sistema, el comportamiento de floating labels y tooltips debe ser idéntico en todos los módulos — sin diferencias de animación, color, posición o comportamiento entre módulos.

**Why this priority**: La consistencia visual genera confianza y reduce la curva de aprendizaje. Un usuario que aprende a usar filtros en Personas debe poder usar los mismos filtros en Propiedades sin re-aprender.

**Independent Test**: Puede probarse navegando entre al menos 3 módulos diferentes y comparando visualmente el comportamiento de floating labels y tooltips.

**Acceptance Scenarios**:

1. **Given** que el usuario compara los Filtros Avanzados de Personas y Propiedades, **When** interactúa con los campos de ambos, **Then** el comportamiento de floating labels es idéntico.
2. **Given** que el usuario compara los modales de Liquidaciones y Contratos, **When** abre ambos modales, **Then** los floating labels y tooltips tienen el mismo estilo, animación y comportamiento.

---

### Edge Cases

- ¿Qué sucede cuando un campo tiene valor prellenado al abrir el modal? El label debe mostrarse en posición elevada desde el inicio.
- ¿Qué sucede cuando un Select/Combobox tiene una opción larga que podría superponerse con el label? El label debe mantener su posición y el texto del select debe ser truncado si es necesario.
- ¿Qué sucede cuando el usuario intenta interactuar con un tooltip mientras está escribiendo en un campo? El tooltip debe desaparecer al perder el foco del icono.
- ¿Qué sucede en pantallas pequeñas (tablets) donde el espacio es limitado? Los floating labels deben adaptarse sin romper el layout.
- ¿Qué sucede cuando un modal tiene muchos campos y se necesita scroll? Los floating labels deben funcionar correctamente incluso en campos visibles parcialmente.
- ¿Qué sucede cuando un campo tiene errores de validación? El label debe permanecer elevado, cambiar a color de error y mostrar el mensaje de validación debajo.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Todos los campos de entrada (Input, Select, Combobox, DatePicker) en Filtros Avanzados DEBEN implementar floating labels que se elevan al enfocar el campo.
- **FR-002**: Todos los campos de entrada en modales DEBEN implementar floating labels consistentes con los de Filtros Avanzados.
- **FR-003**: Los floating labels DEBEN usar animación de transición con timing estándar del sistema: `0.3s cubic-bezier(0.4, 0, 0.2, 1)` al cambiar de posición.
- **FR-004**: Los labels DEBEN mantenerse legibles y no superponerse con el texto del campo en ningún estado (vacío, con foco, con valor).
- **FR-005**: Los iconos de información (ℹ️) en Filtros Avanzados DEBEN mostrar tooltips al hacer hover.
- **FR-006**: Los iconos de información en modales DEBEN mostrar tooltips al hacer hover.
- **FR-007**: Los tooltips DEBEN cerrarse automáticamente al mover el mouse fuera del icono.
- **FR-008**: El comportamiento de floating labels y tooltips DEBEN ser consistentes en todos los módulos listados: Personas, Propiedades, Contratos, Liquidaciones, Liquidación Asesores, Recaudos, Desocupaciones, Incidentes, Seguros, Recibos Públicos, Saldos a Favor, Usuarios, IPC/Incrementos, Reportes.
- **FR-009**: Los floating labels DEBEN funcionar correctamente en campos con valores prellenados.
- **FR-010**: Los tooltips DEBEN ser accesibles con atributos ARIA básicos (`role="tooltip"`, `aria-describedby`) y funcionar en dispositivos táctiles (mostrar al tocar, ocultar al tocar fuera).
- **FR-011**: El contenido textual de los tooltips DEBEN provenir de un archivo de constantes centralizado para facilitar mantenimiento y traducción.
- **FR-012**: Los floating labels en campos con errores de validación DEBEN permanecer en posición elevada, cambiar a color de error y mostrar el mensaje de error debajo del campo.

### Key Entities

- **Campo de Formulario**: Elemento de entrada de datos que requiere un label descriptivo. Puede ser Input, Select, Combobox o DatePicker.
- **Floating Label**: Label que cambia su posición de interior del campo a exterior cuando el campo recibe foco o tiene contenido.
- **Tooltip**: Elemento emergente que muestra información contextual al pasar el mouse sobre un icono de información.
- **Filtros Avanzados**: Sección expandible que contiene campos de filtrado para refinar la búsqueda de registros.
- **Modal**: Ventana emergente que contiene formularios de entrada de datos (ej. creación, edición).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% de los campos en Filtros Avanzados de todos los módulos muestran floating labels funcionales sin superposiciones.
- **SC-002**: 100% de los campos en todos los modales muestran floating labels funcionales sin superposiciones.
- **SC-003**: 100% de los iconos de información en Filtros Avanzados muestran tooltips al hacer hover.
- **SC-004**: 100% de los iconos de información en modales muestran tooltips al hacer hover.
- **SC-005**: El comportamiento visual es idéntico entre todos los módulos (sin diferencias de animación, color o posición).
- **SC-006**: No existen superposiciones de texto entre labels y contenido de campos en ningún estado interactivo.
- **SC-007**: Los usuarios pueden identificar todos los campos de formulario sin necesidad de hacer clic en ellos para descubrir su función.

## Assumptions

- El sistema de diseño actual (Claude/Anthropic Design System) define los colores y estilos para floating labels y tooltips que deben ser respetados.
- Los módulos listados por el usuario son los únicos que requieren validación en esta iteración.
- La implementación actual tiene componentes base de floating labels y tooltips que necesitan corrección, no creación desde cero.
- Los tooltips deben usar el sistema de z-index definido en `styles.py` (Z_TOOLTIP=1100). Para tooltips dentro de modales, el z-index debe ser mayor al del modal (Z_MODAL + 50) para garantizar visibilidad.
- Los floating labels deben seguir la paleta de colores del sistema: Textos en Anthropic Near Black (#141413) para labels activos, Olive Gray (#5e5d59) para labels inactivos.
- Las transiciones deben usar el timing estándar del sistema: `all 0.3s cubic-bezier(0.4, 0, 0.2, 1)`.
- El archivo `styles.py` contiene los estilos base (`BASE_STYLE`) que gobernan el comportamiento de pointer-events y z-index para superposiciones.
- El contenido textual de los tooltips debe almacenarse en un archivo de constantes centralizado (ej. `tooltips_text.py`) para facilitar mantenimiento y futuras traducciones.
