# Feature Specification: Estandarización de Tooltips en Filtros Avanzados

**Feature Branch**: `[022-tooltips-filtros-avanzados]`

**Created**: 2026-07-05

**Status**: Draft

**Input**: User description: "/speckit-specify Quiero que realices un proceso de ingeniería inversa de nivel Senior/Principal sobre la interfaz de usuario de todos los módulos del sistema, con el objetivo de estandarizar el uso de tooltips en los botones disponibles dentro de la sección de Filtros Avanzados, siguiendo las mejores prácticas de UI/UX, accesibilidad y usabilidad..."

## Clarifications

### Session 2026-07-05
- Q: Estructura gramatical de tooltips → A: Infinitivo (ej. "Limpiar filtros", "Aplicar búsqueda")
- Q: UX Flow / Interacción en Dispositivos Táctiles → A: Deshabilitar en móviles (usar CSS/Props para ocultar en touch) para evitar interferir con las acciones de tap.
- Q: Diseño y Posicionamiento → A: Arriba (Top) del botón, con ajuste automático (collision aware) si no hay espacio.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Estandarización de Tooltips en Filtros (Priority: P1)

Como usuario del sistema,
quiero ver tooltips descriptivos al posicionar el cursor o al dar foco de teclado sobre cualquier botón en la sección de Filtros Avanzados,
para entender claramente qué acción realiza cada botón sin confusión.

**Why this priority**: Es el núcleo del requerimiento y mejora drásticamente la usabilidad, consistencia y accesibilidad de la interfaz en todos los módulos de la aplicación.

**Independent Test**: Can be fully tested by navigating to any module with Advanced Filters, hovering over each button, tabbing through them with the keyboard, and verifying the presence, content, accessibility and consistent styling of the tooltips.

**Acceptance Scenarios**:

1. **Given** el usuario está en cualquier módulo con filtros avanzados (ej. Dashboard, Personas, etc.), **When** pasa el cursor (`hover`) sobre un botón de filtro o de acción en dicha sección, **Then** se muestra un tooltip descriptivo con texto claro y conciso.
2. **Given** el usuario navega exclusivamente con el teclado, **When** el foco (`focus`) recae sobre un botón de la sección Filtros Avanzados, **Then** el tooltip correspondiente se hace visible.

### Edge Cases

- En dispositivos táctiles (móvil/tablet), los tooltips se deben deshabilitar (usando CSS/Props para ocultar en touch) para no interferir con los eventos de tap y mantener limpia la UI.
- Los tooltips se posicionan por defecto en la parte superior (Top) del botón, con ajuste automático de colisiones (collision aware) para reposicionarse si no hay espacio suficiente en pantalla.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST implementar tooltips en todos los botones de la sección de Filtros Avanzados de los módulos: Dashboard, Personas, Propiedades, Contratos, Liquidaciones, Liquidación de Asesores, Recaudos, Desocupaciones, Incidentes, Seguros, Recibos Públicos, Saldos a Favor, Usuarios, Gestión de IPC / Incrementos, Reportes.
- **FR-002**: System MUST asegurar que el texto de cada tooltip describa clara y concisamente la acción del botón asociado, utilizando verbos en infinitivo (ej. "Limpiar filtros", "Aplicar búsqueda").
- **FR-003**: System MUST mostrar los tooltips tanto al pasar el cursor (hover) como al recibir foco por teclado (focus).
- **FR-004**: System MUST mantener un diseño y comportamiento homogéneo a lo largo de todos los módulos, respetando el sistema de diseño de la aplicación y garantizando compatibilidad con la jerarquía visual de Radix UI (usar `Z_TOOLTIP=1100`).
- **FR-005**: System MUST asegurar que el tooltip no interfiera con la interacción del usuario ni bloquee otros elementos (verificar y aplicar correctamente `pointer-events`).
- **FR-006**: System MUST reutilizar componentes existentes para la generación de tooltips si ya están definidos, asegurando la consistencia arquitectónica en todo el código base.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% de los botones dentro de las secciones de "Filtros Avanzados" en los 15 módulos cuentan con tooltips configurados correctamente.
- **SC-002**: 100% de los tooltips pueden ser activados mediante navegación por teclado (focus), garantizando accesibilidad funcional completa.
- **SC-003**: El diseño, ancho máximo, color y estilo de los tooltips es idéntico en todos los módulos, sin variaciones o implementaciones "ad-hoc".

## Assumptions

- Se asume que la base de código actual utiliza el sistema Reflex y que existen directivas nativas (como `rx.tooltip`) o un componente UI propio reutilizable para la presentación de tooltips.
- Se asume que todos los botones de Filtros Avanzados se pueden identificar claramente mediante inspección (ingeniería inversa) en cada uno de los archivos o componentes responsables de dichos módulos.
