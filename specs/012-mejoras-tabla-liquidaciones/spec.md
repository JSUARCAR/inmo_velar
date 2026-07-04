# Feature Specification: Mejoras en Tabla de Liquidaciones

**Feature Branch**: `[###-mejoras-tabla-liquidaciones]`

**Created**: 2026-07-04

**Status**: Draft

**Input**: User description: "Quiero realizar las siguientes mejoras en la tabla de Liquidaciones: Ordenamiento de columnas: todas las columnas de la tabla, excepto la columna Acciones, deben permitir ordenar los registros tanto de forma ascendente (menor a mayor) como descendente (mayor a menor). Nuevo filtro: en la sección de Filtros avanzados, agregar un filtro correspondiente al Ciclo Operativo. Corrección de espaciado y distribución: ajustar el diseño de la sección de Filtros avanzados para respetar adecuadamente los espacios y márgenes entre los componentes, ya que actualmente se evidencian botones superpuestos y problemas de alineación. Mejora de UI/UX: reorganizar el orden en que se muestran los filtros y acciones dentro de la interfaz, siguiendo una distribución más lógica y consistente que mejore la experiencia de usuario. Objetivo: mejorar la usabilidad de la tabla de Liquidaciones, facilitando la búsqueda y organización de la información, corrigiendo problemas visuales en los filtros avanzados y optimizando la disposición de los elementos en la interfaz."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Ordenamiento de Columnas (Priority: P1)

Como usuario, quiero poder ordenar la tabla de Liquidaciones por cualquiera de sus columnas (excepto Acciones) tanto de forma ascendente como descendente, para poder organizar y encontrar rápidamente la información que necesito según distintos criterios.

**Why this priority**: Es fundamental para la usabilidad y búsqueda de registros cuando existen muchos datos.

**Independent Test**: Can be fully tested by clicking on table headers to verify that the rows reorder correctly in ascending and descending order.

**Acceptance Scenarios**:

1. **Given** la tabla de Liquidaciones cargada con datos, **When** el usuario hace clic en el encabezado de una columna (ej. Monto), **Then** los registros se ordenan de forma ascendente según esa columna.
2. **Given** la tabla ordenada de forma ascendente por una columna, **When** el usuario hace clic nuevamente en el mismo encabezado, **Then** los registros se ordenan de forma descendente.
3. **Given** la tabla de Liquidaciones, **When** el usuario observa la columna "Acciones", **Then** nota que no tiene la opción (ni icono) de ordenamiento.

---

### User Story 2 - Filtro por Ciclo Operativo (Priority: P1)

Como usuario, quiero poder filtrar los registros de la tabla de Liquidaciones por su "Ciclo Operativo" desde la sección de Filtros avanzados, para poder aislar liquidaciones pertenecientes a un periodo o ciclo específico.

**Why this priority**: Mejora directamente la capacidad de búsqueda de la información en escenarios del día a día.

**Independent Test**: Can be fully tested by applying the specific "Ciclo Operativo" filter and verifying that only matching rows appear.

**Acceptance Scenarios**:

1. **Given** la sección de Filtros avanzados abierta, **When** el usuario selecciona un "Ciclo Operativo" específico y aplica, **Then** la tabla solo muestra las liquidaciones correspondientes a ese ciclo.

---

### User Story 3 - Corrección Visual y Reorganización UI/UX de Filtros (Priority: P2)

Como usuario, quiero que la sección de Filtros avanzados tenga un diseño ordenado, sin botones superpuestos, y con una distribución lógica y consistente, para que la experiencia de uso sea fluida y profesional.

**Why this priority**: Soluciona bugs visuales actuales (superposición) y mejora la percepción de calidad del producto, pero la funcionalidad core sigue operativa.

**Independent Test**: Can be fully tested by opening the advanced filters and visually verifying that all components have proper spacing, alignment, and logical flow.

**Acceptance Scenarios**:

1. **Given** la vista de la tabla de Liquidaciones, **When** el usuario abre la sección de Filtros avanzados, **Then** visualiza todos los controles (inputs, dropdowns, botones) con espaciados correctos y sin ninguna superposición.
2. **Given** la vista de Filtros avanzados, **When** el usuario inspecciona la disposición de elementos, **Then** observa que los filtros y acciones están agrupados y ordenados de manera lógica.

---

### Edge Cases

- What happens when el usuario combina el nuevo filtro "Ciclo Operativo" con otros filtros existentes? (Deben funcionar como un "AND" lógico).
- How does system handle el ordenamiento ascendente/descendente cuando hay campos nulos (vacíos) en la columna seleccionada? (Generalmente los nulos se agrupan al final o al inicio).
- What happens when la ventana del navegador se redimensiona (responsive)? (La nueva disposición de filtros no debe romperse ni volver a superponerse en pantallas pequeñas).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST permitir ordenamiento ascendente y descendente en todas las columnas de la tabla de Liquidaciones, exceptuando la columna "Acciones".
- **FR-002**: System MUST incluir un campo de selección/búsqueda para "Ciclo Operativo" dentro del panel o sección de Filtros avanzados.
- **FR-003**: System MUST combinar correctamente el filtro de "Ciclo Operativo" con cualquier otro filtro avanzado previamente aplicado.
- **FR-004**: System MUST renderizar la sección de Filtros avanzados aplicando márgenes, padding y alineación correcta (sin superposición de componentes).
- **FR-005**: System MUST presentar la interfaz de Filtros de manera reorganizada (flujo lógico de lectura y acciones) mejorando la experiencia de usuario.

### Key Entities *(include if feature involves data)*

- **Liquidacion**: Representa el registro principal en la tabla (con sus montos, fechas, estados, etc.).
- **Ciclo Operativo**: Representa la entidad o atributo por la que se filtrará.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% de las columnas de datos (excluyendo "Acciones") permiten clics en su encabezado para alternar el orden ASC/DESC, reflejándose en la UI sin errores.
- **SC-002**: El filtro de "Ciclo Operativo" se encuentra disponible y filtra los registros correctamente.
- **SC-003**: El panel de filtros no presenta superposición de elementos en resoluciones de pantalla estándar de escritorio y laptop.
- **SC-004**: La revisión de diseño (Visual Review) aprueba la nueva distribución y espaciado de los elementos de filtro y botones de acción.

## Assumptions

- Se asume que el backend/base de datos ya tiene expuesto o guardado el campo "Ciclo Operativo" asociado a las Liquidaciones, por lo que el cambio se enfoca en que el frontend o la capa de presentación consuma/filtre este campo.
- Se asume que el ordenamiento de columnas es soportado por el componente de tabla (Reflex) actual o que se cuenta con un mecanismo estándar en la app para aplicarlo en el backend o en el estado de frontend.
- Se asume que el rediseño de los filtros se regirá por el Sistema de Diseño del proyecto (CLAUDE DESIGN SYSTEM) respetando los márgenes, colores y fuentes allí definidos.
