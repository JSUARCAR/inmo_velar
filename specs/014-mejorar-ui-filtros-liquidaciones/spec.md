# Feature Specification: Mejorar UI Filtros Liquidaciones

**Feature Branch**: `[014-mejorar-ui-filtros-liquidaciones]`

**Created**: 2026-07-04

**Status**: Draft

**Input**: User description: "Quiero que organices en la sección de filtros avanzados del módulo de Liquidaciones de Propietarios, ya que visualmente no se ve bien organizado ni espaciado, valida la imagen para tener contexto"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Organización Visual de Filtros (Priority: P1)

Como usuario administrativo, quiero que la sección de filtros avanzados y acciones de Liquidaciones de Propietarios tenga un espaciado adecuado y una distribución lógica, para poder identificar y utilizar las opciones rápidamente sin confusión visual.

**Why this priority**: La interfaz actual presenta elementos amontonados (como los selectores, el switch "Individual" y los botones de acción) que dificultan la usabilidad y empeoran la experiencia de usuario. Corregirlo es esencial para una interacción fluida y profesional.

**Independent Test**: Can be fully tested by navegando a la página de Liquidaciones de Propietarios y observando la barra superior de filtros y botones de acción en distintos tamaños de pantalla (Desktop y Mobile).

**Acceptance Scenarios**:

1. **Given** que estoy en la vista de Liquidaciones de Propietarios, **When** observo la barra de herramientas principal, **Then** los campos de búsqueda, selectores, switches y botones de acción deben estar separados por un espaciado consistente y alineados correctamente.
2. **Given** que la pantalla cambia de tamaño, **When** redimensiono la ventana, **Then** los filtros deben mantenerse legibles, organizándose fluidamente en un contenedor adaptativo en lugar de solaparse o comprimirse en exceso.

---

### Edge Cases

- What happens when la pantalla es muy estrecha (dispositivos móviles o ventanas pequeñas)? Los controles deberían usar flex wrap o colapsar en filas para mantener su utilidad.
- How does system handle cuando se aplican múltiples filtros que requieren la atención del usuario? La posición de los controles de selección debe ser intuitiva, idealmente agrupada cerca del botón de búsqueda y separada de las acciones globales (como el switch o crear nueva liquidación).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST aplicar un espaciado (gap) uniforme entre todos los controles en la barra de filtros de Liquidaciones (inputs, selects, switch, botones).
- **FR-002**: System MUST agrupar lógicamente los elementos: separar el grupo de búsqueda/filtros del grupo de acciones globales (Switch "Individual", Botón "+ Nueva", Botón de recarga).
- **FR-003**: System MUST evitar que los textos y labels (como el switch "Individual") se superpongan visualmente o se amontonen con los botones y selectores adyacentes.
- **FR-004**: System MUST cumplir con el "Claude Design System" (colores, sombras, estilos limpios) definido en la constitución, evitando sobrecargar de márgenes innecesarios pero manteniendo un "breathing room" claro.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: En pantallas de escritorio (>= 1024px), los elementos de la barra de filtros no se sobreponen ni quedan apretados.
- **SC-002**: El espaciado entre los diferentes componentes (Búsqueda, Selectores, Switch, Botones) es consistente y utiliza las unidades estándar del diseño de Reflex (ej. `spacing="4"` o equivalente).
- **SC-003**: No hay pérdida de funcionalidad: todos los controles interactivos (inputs, switches, dropdowns, botones) son fáciles de clickear (hitbox apropiado) y se renderizan correctamente sin recortarse.

## Assumptions

- No se realizarán cambios a la lógica de filtrado backend ni a los callbacks de estado; el trabajo es exclusivamente sobre las propiedades visuales y de disposición (Layout/CSS/Reflex props).
- La disposición se adaptará usando el sistema de Flexbox de Reflex (`rx.hstack`, `rx.vstack`, `rx.flex` con `wrap="wrap"`) para lograr el responsivo deseado.
