# Feature Specification: Agregar Columna PROPIEDAD a Tabla de Recaudos

**Feature Branch**: `050-agregar-columna-propiedad`

**Created**: 2026-07-11

**Status**: Draft

**Input**: User description: "Corregir tabla de recaudos que omite la columna PROPIEDAD por error"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Visualizar columna PROPIEDAD en tabla de recaudos (Priority: P1)

Como usuario del sistema de inmobiliaria, necesito ver la columna PROPIEDAD en la tabla de recaudos para identificar a qué propiedad corresponde cada registro de recaudo.

**Why this priority**: La columna PROPIEDAD es esencial para la identificación y gestión de recaudos por propiedad. Sin ella, los usuarios no pueden distinguir a qué inmueble corresponde cada pago.

**Independent Test**: Puede probarse completamente navegando a la vista de recaudos y verificando que la columna PROPIEDAD aparece en la tabla con los datos correctos de cada propiedad.

**Acceptance Scenarios**:

1. **Given** que el usuario accede a la vista de recaudos, **When** se carga la tabla, **Then** la columna PROPIEDAD debe estar visible entre CICLO OPERATIVO y CANON
2. **Given** que existen registros de recaudos, **When** se visualiza la tabla, **Then** cada fila debe mostrar el nombre o identificador de la propiedad correspondiente
3. **Given** que el usuario aplica filtros, **When** se filtra por propiedad, **Then** la columna debe mostrar solo las propiedades que coinciden con el filtro

---

### User Story 2 - Ordenar por columna PROPIEDAD (Priority: P2)

Como usuario, necesito poder ordenar la tabla de recaudos por la columna PROPIEDAD para agrupar visualmente los recaudos de la misma propiedad.

**Why this priority**: Facilita la organización y búsqueda de recaudos cuando se gestionan múltiples propiedades.

**Independent Test**: Puede probarse haciendo clic en el encabezado de la columna PROPIEDAD y verificando que la tabla se ordena alfabéticamente por propiedad.

**Acceptance Scenarios**:

1. **Given** que la tabla muestra recaudos de múltiples propiedades, **When** el usuario hace clic en el encabezado PROPIEDAD, **Then** la tabla se ordena alfabéticamente por nombre de propiedad
2. **Given** que la tabla ya está ordenada por PROPIEDAD, **When** el usuario hace clic nuevamente, **Then** el orden se invierte (descendente)

---

### User Story 3 - Filtrar por PROPIEDAD (Priority: P3)

Como usuario, necesito poder filtrar la tabla de recaudos por una propiedad específica para ver solo los recaudos de ese inmueble.

**Why this priority**: Permite un análisis enfocado cuando se necesita revisar el historial de una propiedad específica.

**Independent Test**: Puede probarse aplicando un filtro en la columna PROPIEDAD y verificando que solo se muestran los recaudos de la propiedad seleccionada.

**Acceptance Scenarios**:

1. **Given** que existen recaudos de múltiples propiedades, **When** el usuario selecciona una propiedad en el filtro, **Then** solo se muestran los recaudos de esa propiedad
2. **Given** que se aplica un filtro de propiedad, **When** el usuario limpia el filtro, **Then** se muestran todos los recaudos nuevamente

---

### Edge Cases

- ¿Qué sucede cuando una propiedad no tiene nombre registrado? Se debe mostrar un identificador alternativo (ID de propiedad) o "Sin nombre"
- ¿Qué pasa si la tabla tiene registros sin propiedad asociada? Se debe mostrar un indicador visual de registro incompleto
- ¿Cómo se maneja la búsqueda en la columna cuando hay propiedades con nombres similares? La búsqueda debe ser parcial (contiene)

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: La tabla de recaudos DEBE mostrar la columna PROPIEDAD como columna visible por defecto
- **FR-002**: La columna PROPIEDAD DEBE ubicarse después de CICLO OPERATIVO y antes de CANON en el orden de columnas
- **FR-003**: El sistema DEBE mostrar la dirección de la propiedad (campo `direccion`) asociada a cada registro de recaudo a través del campo `propiedad_id`
- **FR-004**: La columna DEBE ser ordenable (ascendente/descendente) al hacer clic en el encabezado
- **FR-005**: El sistema DEBE permitir filtrar la tabla por propiedad específica
- **FR-006**: Cuando una propiedad no tiene nombre, el sistema DEBE mostrar su ID o "Sin nombre"
- **FR-007**: La columna DEBE ser responsiva y adaptarse al tamaño de pantalla
- **FR-008**: El sistema DEBE mantener el estado de orden y filtros de la columna PROPIEDAD al recargar la página

### Key Entities

- **Propiedad**: Representa un inmueble del portafolio de la inmobiliaria. Atributos clave: ID, dirección (usada como nombre visible), propietario
- **Recaudo**: Registro de pago asociado a una propiedad y un período. Relación: cada recaudo tiene un campo `propiedad_id` directo que referencia a la propiedad

## Clarifications

### Session 2026-07-11

- Q: ¿Cómo se relaciona un recaudo con su propiedad? → A: Campo `propiedad_id` directo en la tabla de recaudos. El nombre de la propiedad mostrado es la dirección de la propiedad.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: La columna PROPIEDAD es visible al 100% de los usuarios al acceder a la vista de recaudos
- **SC-002**: El tiempo de carga de la tabla no aumenta más de 50ms al agregar la columna
- **SC-003**: Los usuarios pueden identificar la propiedad de cada recaudo en menos de 2 segundos
- **SC-004**: La funcionalidad de orden y filtro de la columna funciona correctamente en el 100% de los casos de prueba
- **SC-005**: La tabla mantiene la legibilidad en dispositivos móviles (columna PROPIEDAD se adapta o se oculta en pantallas pequeñas)

## Assumptions

- La información de propiedad ya existe en el modelo de datos (modelo Propiedad o tabla relacional)
- Cada registro de recaudo tiene una relación válida con una propiedad existente
- El sistema actual ya soporta columnas ordenables y filtrables en la tabla de recaudos
- El diseño de la interfaz seguirá el patrón establecido para las demás columnas de la tabla
- La columna PROPIEDAD debe ser visible por defecto (no oculta)
- No se requieren permisos adicionales para ver la información de propiedad en recaudos
