# Feature Specification: fix-filtro-ciclo-ui

**Feature Branch**: `feature/013-fix-filtro-ciclo-ui`

**Created**: 2026-07-04

**Status**: Clarified

**Input**: User description: "Valida el siguiente error que se presenta cuando realizo un filtro por ciclo operativo: Error al cargar liquidaciones: column prop.grupo_operativo does not exist LINE 7: WHERE l.eliminada = FALSE AND prop.GRUPO_OPERATIVO... ^", adicionl evidencio que hay elementos en la sección de filtros avanzados que estan sobrepuestos sin respetar espacio entre ellos. @[image.png]"

## Clarifications

### Session 2026-07-04

- Q: El error indica que `prop.grupo_operativo` no existe. ¿A qué se debe esto principalmente en el contexto de la base de datos de Liquidaciones? → A: El alias utilizado en la consulta principal es distinto (ej. `p.grupo_operativo` en lugar de `prop.grupo_operativo`).
- Q: Al solucionar el problema de superposición de la sección de filtros avanzados en resoluciones más pequeñas (móviles/tabletas pequeñas), ¿cuál es el comportamiento preferido para los elementos cuando se reacomodan (wrap)? → A: Un filtro por fila (ancho 100%) para aprovechar el espacio vertical y evitar agrupaciones apretadas.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Filtro por Ciclo Operativo Exitoso (Priority: P1)

Como usuario administrativo, quiero poder filtrar la tabla de liquidaciones por ciclo operativo sin que ocurra un error de base de datos, para poder encontrar rápidamente la información que necesito según el grupo o ciclo.

**Why this priority**: Es la funcionalidad principal afectada por el bug, impidiendo al usuario ver los datos filtrados correctamente.

**Independent Test**: Se puede probar independientemente seleccionando una opción en el filtro "Ciclo Operativo" en la interfaz de liquidaciones y verificando que la tabla se actualice con los resultados sin mostrar mensajes de error.

**Acceptance Scenarios**:

1. **Given** la vista de la tabla de liquidaciones con el panel de filtros avanzados, **When** el usuario selecciona un ciclo operativo del menú desplegable, **Then** el sistema retorna y muestra únicamente las liquidaciones que pertenecen a los contratos/propiedades con ese ciclo operativo, sin lanzar errores de base de datos.
2. **Given** un filtro de ciclo operativo previamente seleccionado, **When** el usuario limpia el filtro (selecciona "Todos" o vacío), **Then** la tabla muestra todas las liquidaciones sin importar su ciclo.

---

### User Story 2 - Interfaz de Filtros Avanzados Responsiva (Priority: P2)

Como usuario del sistema, quiero ver todos los filtros y botones de acciones en la tabla de liquidaciones con una separación adecuada, sin que se superpongan entre ellos, incluso en pantallas de diferentes tamaños (responsividad), para tener una experiencia de usuario clara y cómoda.

**Why this priority**: Afecta directamente la usabilidad (UI/UX) y la calidad percibida de la aplicación.

**Independent Test**: Se puede probar visualizando la pantalla en distintas resoluciones o tamaños de ventana, y verificando que ningún elemento (input, botón, texto) se superponga sobre otro.

**Acceptance Scenarios**:

1. **Given** la página de liquidaciones abierta en un monitor estándar (escritorio), **When** el usuario observa el área de filtros avanzados, **Then** todos los campos de búsqueda, desplegables y botones tienen el margen y espaciado correcto, sin chocar visualmente ni superponerse.
2. **Given** la página de liquidaciones abierta en una pantalla pequeña o en una ventana redimensionada, **When** los filtros no caben en una sola fila, **Then** los elementos se reacomodan (wrap) en varias líneas manteniendo los espacios y márgenes proporcionales, sin superposición.

### Edge Cases

- ¿Qué pasa si la consulta filtrada no devuelve ningún resultado? El sistema debe mostrar el estado vacío habitual sin errores.
- ¿Qué pasa en resoluciones de pantalla extremadamente pequeñas (e.g. móvil)? Los filtros deben colapsarse a 1 por fila (ancho 100%) con márgenes verticales entre sí.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El sistema MUST ejecutar correctamente la consulta SQL filtrando por ciclo operativo, referenciando correctamente la columna mediante el alias correcto de la tabla de propiedades (`p.GRUPO_OPERATIVO` en lugar de `prop.GRUPO_OPERATIVO`).
- **FR-002**: Los elementos de la UI en la barra de herramientas de filtros MUST colapsar a un filtro por fila (ancho 100%) en resoluciones móviles, y utilizar `wrap` y márgenes adecuadamente definidas para que no se traslapen en resoluciones intermedias.
- **FR-003**: El sistema MUST mantener los estándares de diseño neumórfico del sistema de diseño (Claude Design System).

### Key Entities *(include if feature involves data)*

- **Liquidacion**: Representa el registro de liquidación que debe ser devuelto correctamente.
- **Propiedad**: Entidad a la cual está ligada la liquidación y la cual contiene realmente el atributo de ciclo (grupo operativo).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Los usuarios pueden filtrar por Ciclo Operativo con una tasa de error del 0%.
- **SC-002**: La interfaz de filtros no presenta superposición de elementos en resoluciones probadas desde pantallas móviles (320px ancho) hasta monitores 4K.
- **SC-003**: El tiempo de respuesta de la base de datos al filtrar se mantiene bajo (< 2 segundos).

## Assumptions

- Se mantendrá el enfoque Clean Architecture y el Reflex UI.
