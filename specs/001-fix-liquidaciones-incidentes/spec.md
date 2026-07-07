# Feature Specification: Corrección de Selección de Incidentes en Liquidaciones

**Feature Branch**: `001-fix-liquidaciones-incidentes`

**Created**: 2026-07-06

**Status**: Draft

**Input**: User description: "Ingeniería inversa sobre el módulo Liquidaciones, funcionalidad Seleccionar Incidentes. El modal muestra incidentes de otras propiedades en lugar de filtrar por la propiedad de la liquidación. Al editar liquidaciones, los campos Incidentes y Observaciones no cargan valores previamente almacenados."

## Clarifications

### Session 2026-07-06

- Q: ¿Cuál es la cardinalidad de la relación Liquidación-Incidentes? → A: 1:N (una liquidación puede tener múltiples incidentes asociados)
- Q: ¿El modal debe permitir seleccionar múltiples incidentes de una vez o solo uno por vez? → A: Selección múltiple (el usuario puede marcar varios incidentes de una vez)
- Q: ¿Cómo debe manejar el sistema conflictos de edición concurrente? → A: Última escritura con notificación (permitir edición libre pero notificar si hubo cambios desde que se abrió)

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Filtrado Correcto de Incidentes por Propiedad (Priority: P1)

Como usuario del módulo de Liquidaciones, quiero que al hacer clic en "Seleccionar Incidentes" al crear o editar una liquidación, el sistema muestre únicamente los incidentes asociados a la propiedad de esa liquidación, para evitar asociaciones incorrectas entre incidentes y liquidaciones.

**Why this priority**: Es la funcionalidad central del flujo de negocio. Si el filtrado es incorrecto, se pueden vincular incidentes a la liquidación equivocada, generando errores financieros y de registro.

**Independent Test**: Puede probarse completamente accediendo a una liquidación existente con propiedad asociada, haciendo clic en "Seleccionar Incidentes" y verificando que solo aparecen incidentes de esa propiedad específica.

**Acceptance Scenarios**:

1. **Given** una liquidación asociada a la propiedad "Calle Falsa 123", **When** el usuario hace clic en "Seleccionar Incidentes", **Then** el modal muestra únicamente incidentes cuya propiedad sea "Calle Falsa 123"
2. **Given** una liquidación sin incidentes previos asociados, **When** el usuario abre el modal de selección de incidentes, **Then** se muestran los incidentes disponibles para la propiedad de esa liquidación
3. **Given** una liquidación con incidentes ya asociados de otras propiedades (dato inconsistente previo), **When** el usuario consulta los incidentes, **Then** el sistema filtra y muestra solo los correspondientes a la propiedad actual
4. **Given** múltiples incidentes disponibles para una propiedad, **When** el usuario abre el modal, **Then** puede seleccionar varios incidentes de una vez antes de guardar

---

### User Story 2 - Carga de Datos al Editar Liquidación (Priority: P1)

Como usuario editando una liquidación existente, quiero que los campos "Incidentes" y "Observaciones" muestren automáticamente la información previamente almacenada, para poder revisar y modificar los datos sin perder información.

**Why this priority**: Sin la carga correcta de datos existentes, el usuario no puede verificar ni actualizar la información, lo que impide el proceso de edición y puede causar pérdida de datos.

**Independent Test**: Puede probarse accediendo a una liquidación que ya tenga incidentes y observaciones registrados, verificando que los campos muestran los valores guardados.

**Acceptance Scenarios**:

1. **Given** una liquidación con incidentes previamente asociados, **When** el usuario abre el formulario de edición, **Then** el campo "Incidentes" muestra el valor correspondiente a los descuentos registrados (múltiples incidentes)
2. **Given** una liquidación con observaciones previamente guardadas, **When** el usuario accede a la edición, **Then** el campo "Observaciones" carga el texto almacenado en la base de datos
3. **Given** una liquidación editada con nuevos incidentes seleccionados, **When** el usuario guarda los cambios, **Then** la información se persiste correctamente y es recuperable en futuras ediciones
4. **Given** una liquidación con múltiples incidentes seleccionados, **When** el usuario abre el modal de edición, **Then** todos los incidentes previamente seleccionados aparecen marcados

---

### User Story 3 - Consistencia entre Capas del Sistema (Priority: P2)

Como administrador del sistema, quiero que exista consistencia completa entre la información almacenada en la base de datos, la lógica del backend y la interfaz de usuario, para garantizar la integridad de los datos y la confiabilidad del sistema.

**Why this priority**: La inconsistencia entre capas genera errores difíciles de diagnosticar y afecta la confianza del usuario en el sistema.

**Independent Test**: Puede probarse insertando datos directamente en la base de datos y verificando que se reflejan correctamente en la interfaz, y viceversa.

**Acceptance Scenarios**:

1. **Given** un registro en la base de datos con incidentes asociados a una liquidación, **When** el usuario carga la liquidación en la interfaz, **Then** los datos mostrados coinciden exactamente con los almacenados
2. **Given** una actualización realizada desde la interfaz, **When** se consulta la base de datos, **Then** los valores persistidos son los mismos que los enviados desde el frontend
3. **Given** datos inconsistentes previos (incidentes de otras propiedades), **When** se ejecuta una corrección, **Then** el sistema permite limpiar y reasociar correctamente los incidentes

---

### Edge Cases

- ¿Qué sucede si la propiedad de la liquidación no tiene incidentes registrados? El modal debe mostrar un estado vacío con mensaje indicando que no hay incidentes disponibles para esa propiedad.
- ¿Cómo maneja el sistema si el ID de la propiedad no se envía correctamente al backend? Debe retornar un error claro y no mostrar incidentes de otras propiedades.
- ¿Qué ocurre si se produce un error de conexión al cargar los incidentes? El sistema debe mostrar un mensaje de error al usuario y permitir reintentar.
- ¿Cómo se comporta si el usuario intenta guardar una liquidación sin seleccionar incidentes cuando es obligatorio? Debe mostrar validación indicando que la selección es requerida.
- ¿Qué sucede si la liquidación tiene múltiples propiedades asociadas (caso atípico)? El sistema debe manejar este escenario según las reglas de negocio definidas.
- ¿Qué ocurre si dos usuarios intentan editar la misma liquidación simultáneamente? El sistema debe aplicar la estrategia de última escritura con notificación: permitir la edición pero notificar al usuario si hubo cambios desde que abrió el formulario.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El sistema DEBE filtrar los incidentes mostrados en el modal "Seleccionar Incidentes" exclusivamente por el ID de la propiedad asociada a la liquidación que se está creando o editando
- **FR-002**: El sistema DEBE enviar el ID de la propiedad correctamente al backend al solicitar la lista de incidentes
- **FR-003**: El sistema DEBE cargar automáticamente el valor de "Incidentes" (descuentos asociados) al editar una liquidación existente
- **FR-004**: El sistema DEBE cargar automáticamente el valor de "Observaciones" al editar una liquidación existente
- **FR-005**: El sistema DEBE persistir correctamente la selección de incidentes y las observaciones al guardar la liquidación
- **FR-006**: El sistema DEBE mantener consistencia entre los datos almacenados en la base de datos, el backend y la interfaz de usuario
- **FR-007**: El sistema DEBE mostrar mensajes de error claros cuando no se puedan cargar los incidentes
- **FR-008**: El sistema DEBE permitir la edición de liquidaciones sin perder la información previamente registrada
- **FR-009**: El sistema DEBE validar que la propiedad asociada a la liquidación sea válida antes de consultar incidentes
- **FR-010**: El sistema DEBE manejar el caso donde no existan incidentes para la propiedad seleccionada mostrando un estado vacío informativo
- **FR-011**: El sistema DEBE permitir la selección múltiple de incidentes en el modal, permitiendo al usuario marcar varios incidentes de una vez
- **FR-012**: El sistema DEBE aplicar la estrategia de última escritura con notificación para manejar ediciones concurrentes, permitiendo edición libre pero notificando si hubo cambios recientes

### Key Entities

- **Liquidación**: Registro financiero que representa un movimiento o ajuste económico, asociado a una propiedad específica. Contiene campos como ID, propiedad asociada, incidentes vinculados (relación 1:N: una liquidación puede tener múltiples incidentes) y observaciones.
- **Incidente**: Evento o situación que puede generar un descuento o ajuste en una liquidación. Cada incidente está asociado a una propiedad específica y puede vincularse a una o más liquidaciones.
- **Propiedad**: Inmueble o unidad del sistema inmobiliario. Es la entidad que conecta liquidaciones con incidentes, ya que los incidentes se filtran por propiedad.
- **Observaciones**: Campo de texto libre que almacena notas o comentarios adicionales sobre una liquidación específica.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: El 100% de las veces que se abre el modal "Seleccionar Incidentes", se muestran únicamente los incidentes de la propiedad de la liquidación en edición
- **SC-002**: El 100% de las liquidaciones con datos previos cargan correctamente los campos "Incidentes" y "Observaciones" al editar
- **SC-003**: No existen discrepancias entre los datos mostrados en la interfaz y los almacenados en la base de datos después de las correcciones
- **SC-004**: El tiempo de carga del modal de incidentes no supera los 3 segundos bajo condiciones normales de red
- **SC-005**: Los usuarios pueden completar el proceso de edición de liquidación con incidentes sin errores relacionados con filtrado o carga de datos
- **SC-006**: Se eliminan los casos de incidentes mostrados de propiedades incorrectas (0% de incidentes fuera de la propiedad correcta)

## Assumptions

- La estructura de base de datos actual mantiene una relación correcta entre liquidaciones, propiedades e incidentes (la relación existe pero la consulta no la respeta)
- El backend actual tiene los endpoints necesarios para filtrar incidentes por propiedad, pero la consulta no está implementada correctamente
- El frontend actual tiene los componentes necesarios para mostrar incidentes y observaciones, pero no están configurados para cargar datos existentes
- La corrección es un fix de bugs existentes, no una nueva funcionalidad que requiera migraciones de base de datos
- Los permisos de usuario existentes permiten la edición de liquidaciones sin necesidad de cambios en el sistema RBAC
- El sistema de diseño actual (Reflex/Anthropic Design System) se mantiene para las correcciones de UI
- No se requieren cambios en la arquitectura general del sistema, solo correcciones en las consultas y el manejo de estado