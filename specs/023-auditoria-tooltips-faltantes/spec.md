# Feature Specification: Auditoría de Tooltips Faltantes

**Feature Branch**: `[023-auditoria-tooltips-faltantes]`

**Created**: 2026-07-05

**Status**: Draft

**Input**: User description: "identifico que no todos los botones cuenta con el tooltip, puedes validar queesto por favor"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Identificación y Corrección de Tooltips Faltantes (Priority: P1)

Como usuario del sistema,
quiero que todos los botones de acción sin texto (iconos) y botones relevantes en los diferentes módulos tengan un tooltip descriptivo,
para evitar dudas sobre la función que cumplen y mantener la homogeneidad visual y de experiencia de usuario en todo el sistema.

**Why this priority**: Es esencial para la consistencia y usabilidad de la interfaz, dando continuidad al requerimiento previo de tooltips (Feature 022) y resolviendo casos borde o botones que fueron omitidos inicialmente.

**Independent Test**: Can be fully tested by navigating across the system's modules, interacting (hover/focus) with any button that lacks textual labels or is part of standard actions, and verifying the presence of a correct tooltip.

**Acceptance Scenarios**:

1. **Given** el usuario inspecciona módulos que no fueron cubiertos o botones secundarios (ej. cabeceras de tablas, modales secundarios), **When** interactúa con dichos botones, **Then** se muestra un tooltip utilizando `neuro_tooltip` con el texto en infinitivo apropiado.

### Edge Cases

- Botones en vistas modales o popovers: El tooltip debe seguir mostrando un z-index superior (`Z_TOOLTIP=1100`) para no quedar oculto bajo el modal.
- Botones responsivos que en modo móvil ocultan el texto y muestran solo el ícono.
- Comportamiento en dispositivos móviles (los tooltips deben permanecer desactivados).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST realizar una auditoría visual y a nivel de código de todos los componentes `neuro_button`, `rx.button`, y `rx.icon_button` que no estén envueltos en un componente de tooltip (`neuro_tooltip` o `rx.tooltip`).
- **FR-002**: System MUST inyectar `neuro_tooltip` con una descripción en infinitivo para aquellos botones huérfanos que lo ameriten (especialmente aquellos que solo muestran iconos o se encuentran en contextos ambiguos).
- **FR-003**: System MUST preservar la directiva técnica del requerimiento anterior (ocultar en móviles, `side="top"`, respetar `pointer-events: auto`).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% de los botones basados en íconos sin etiqueta visible en toda la aplicación cuentan con un tooltip descriptivo.
- **SC-002**: No existen botones interactivos silenciosos que confundan al usuario por carecer de descripción textual o tooltip.

## Assumptions

- Se asume que la estructura `neuro_tooltip` actual cumple correctamente su función y solo se requiere expandir su cobertura a botones no abarcados por la estandarización anterior (Feature 022).
- Se asume que la prioridad de revisión está en los botones de ícono (ej. `rx.icon_button`), donde la ausencia de texto hace obligatoria la presencia del tooltip.
