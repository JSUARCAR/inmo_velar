# Feature Specification: filtro-pago-incidentes

**Feature Branch**: `030-filtro-pago-incidentes`

**Created**: 2026-07-06

**Status**: Draft

**Input**: User description: "Quiero que realices un proceso de ingeniería inversa de nivel Senior/Principal sobre el módulo Incidentes, con el objetivo de ampliar la funcionalidad de la sección Filtros Avanzados. Es necesario incorporar un nuevo filtro denominado Estado de Pago del Incidente..."

## Clarifications

### Session 2026-07-06
- Q: ¿Cómo se determinan los estados de pago a mostrar en el ComboBox de filtros? → A: Se deducen dinámicamente según el estado de las liquidaciones asociadas.
- Q: ¿Cuál es el comportamiento cuando el filtro de pago no tiene selección? → A: No filtrar por estado de pago (comportamiento implícito al estar vacío el ComboBox).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Filtrar Incidentes por Estado de Pago (Priority: P1)

Como usuario del módulo de Incidentes, quiero poder filtrar los registros utilizando el "Estado de Pago del Incidente" en la sección de Filtros Avanzados, para poder consultar rápidamente los incidentes según su situación financiera.

**Why this priority**: Es la funcionalidad core solicitada, permite a los usuarios segmentar la información de incidentes basada en su estado de pago, lo que es crucial para la gestión y seguimiento.

**Independent Test**: Can be fully tested by abriendo el módulo de Incidentes, seleccionando un estado de pago en los Filtros Avanzados y verificando que la tabla se actualice con los registros correctos.

**Acceptance Scenarios**:

1. **Given** que estoy en el módulo de Incidentes, **When** abro los Filtros Avanzados, **Then** veo un nuevo ComboBox etiquetado "Estado de Pago del Incidente".
2. **Given** el ComboBox "Estado de Pago del Incidente", **When** lo despliego, **Then** veo las opciones dinámicas cargadas según las reglas de negocio.
3. **Given** que selecciono un estado de pago, **When** aplico los filtros, **Then** la tabla de incidentes muestra únicamente los registros que coinciden con dicho estado.

---

### User Story 2 - Combinar Filtro de Pago con Otros Filtros (Priority: P2)

Como usuario del módulo de Incidentes, quiero poder combinar el filtro "Estado de Pago del Incidente" con otros filtros avanzados (como ciclo, fecha, tipo), para realizar búsquedas granulares y precisas.

**Why this priority**: Asegura la integración del nuevo filtro con el ecosistema de búsqueda existente, multiplicando el valor de la funcionalidad.

**Independent Test**: Can be fully tested by aplicando el nuevo filtro junto con otro existente y verificando que los resultados cumplan ambas condiciones (operador AND).

**Acceptance Scenarios**:

1. **Given** que aplico el filtro "Estado de Pago del Incidente" y el filtro "Ciclo", **When** se ejecuta la búsqueda, **Then** los resultados en la tabla deben cumplir ambas condiciones simultáneamente.
2. **Given** que aplico múltiples filtros, **When** navego por la paginación o aplico un ordenamiento, **Then** los filtros se mantienen y los resultados son consistentes en todas las páginas.

### Edge Cases

- What happens when no hay incidentes que coincidan con el estado de pago seleccionado? (Debe mostrar un mensaje de "No hay resultados" o tabla vacía amigable).
- What happens when los estados de pago en la base de datos cambian o se agregan nuevos? (El ComboBox debe reflejar las nuevas opciones dinámicamente sin requerir cambios en el código frontend).
- What happens when el ComboBox está vacío o se limpia la selección? (El sistema vuelve al comportamiento por defecto de no filtrar por estado de pago, mostrando todos los incidentes independientemente de su estado financiero).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST renderizar un ComboBox en la UI de Filtros Avanzados de Incidentes con la etiqueta "Estado de Pago del Incidente".
- **FR-002**: System MUST poblar el ComboBox dinámicamente obteniendo los estados de pago posibles desde el backend/base de datos o reglas de negocio centralizadas.
- **FR-003**: System MUST integrar el nuevo criterio de búsqueda en el servicio backend que consulta los incidentes, realizando el filtrado directamente en PostgreSQL (no en memoria en el frontend).
- **FR-004**: System MUST mantener el estado del filtro seleccionado durante la navegación, paginación y ordenamiento de la tabla.
- **FR-005**: System MUST respetar el diseño visual, el comportamiento y los estándares de UI/UX (floating labels, tooltips si aplican) usados en el resto de los filtros avanzados.

### Key Entities *(include if feature involves data)*

- **Incidente**: Entidad principal que será consultada y filtrada.
- **EstadoPago**: Representación de los posibles estados que alimentarán el ComboBox, derivados dinámicamente del estado de las liquidaciones asociadas al incidente.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can filtrar la tabla de incidentes por estado de pago obteniendo resultados en menos de 1 segundo (rendimiento backend).
- **SC-002**: 100% de los resultados mostrados al aplicar el filtro corresponden exactamente al estado de pago seleccionado en la base de datos (precisión de datos).
- **SC-003**: El nuevo ComboBox de filtro renderiza visualmente consistente con los demás filtros (mismo tamaño, tipografía, paddings y comportamiento de floating labels).

## Assumptions

- El estado de pago no se guarda directamente como un campo en `Incidente`, sino que se calcula o extrae a partir del estado de las `Liquidaciones` asociadas en PostgreSQL.
- El sistema de paginación y ordenamiento actual es robusto y puede aceptar un nuevo parámetro de búsqueda sin requerir refactorización profunda.
