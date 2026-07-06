# Feature Specification: move-responsable-deposito

**Feature Branch**: `[024-move-responsable-deposito]`

**Created**: 2026-07-05

**Status**: Draft

**Input**: User description: "Quiero realizar un cambio de alcance sobre la funcionalidad de Asignación del Responsable del Depósito..."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Eliminar Responsable del Depósito de Mandato (Priority: P1)

Como usuario del sistema, quiero que el campo "Responsable del Depósito" ya no aparezca en el modal de Contrato de Mandato para evitar confusiones y asegurar que el alcance del contrato es el correcto.

**Why this priority**: Es el núcleo del requerimiento de limpieza y corrección de alcance. Evita recolección de datos erróneos.

**Independent Test**: Can be fully tested by abriendo el modal de creación y edición de Contrato de Mandato y verificando la ausencia del campo, sin afectar el resto del proceso.

**Acceptance Scenarios**:

1. **Given** un usuario abriendo el modal de creación de Mandato, **When** navega por las secciones del formulario, **Then** el campo "Responsable del Depósito" no es visible ni requerido.
2. **Given** un usuario editando un Contrato de Mandato existente, **When** guarda los cambios, **Then** el sistema actualiza correctamente sin requerir ni sobrescribir información sobre el responsable de depósito.

---

### User Story 2 - Implementar Responsable del Depósito en Arrendamiento (Priority: P1)

Como usuario del sistema, quiero poder asignar un "Responsable del Depósito" al crear o editar un Contrato de Arrendamiento seleccionándolo de una lista dinámica de asesores activos, para tener control de quién maneja los depósitos.

**Why this priority**: Habilita la funcionalidad requerida en el lugar correcto.

**Independent Test**: Can be fully tested by creando un Contrato de Arrendamiento, seleccionando un asesor y verificando que el dato persista.

**Acceptance Scenarios**:

1. **Given** un usuario en el modal de Contrato de Arrendamiento, **When** abre el ComboBox de "Responsable del Depósito", **Then** se muestra la lista de asesores activos cargada desde la base de datos.
2. **Given** un usuario que selecciona un responsable y guarda el contrato, **When** el contrato se persiste, **Then** el ID del responsable se guarda correctamente en PostgreSQL.
3. **Given** un usuario editando un Contrato de Arrendamiento que ya tiene un responsable, **When** se abre el modal, **Then** el asesor asignado aparece preseleccionado correctamente.

## Clarifications

### Session 2026-07-05
- Q: ¿Qué hacer con los datos existentes del responsable en Contratos de Mandato? → A: Eliminar la columna de CONTRATOS_MANDATOS por completo (los datos actuales se descartan).
- Q: ¿Qué sucede si el responsable de depósito asignado a un contrato pasa a estado inactivo? → A: Mostrar el asesor inactivo en el ComboBox ÚNICAMENTE si es el actualmente asignado a ese contrato, para no perder el contexto histórico.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El sistema DEBE remover el campo "Responsable del Depósito" de la UI y del estado asociado para el Contrato de Mandato.
- **FR-002**: El sistema DEBE remover el almacenamiento o actualización del responsable de depósito en las consultas SQL (y repositorios) para el Contrato de Mandato, y **eliminar la columna `responsable_deposito_id` de la tabla `CONTRATOS_MANDATOS`** en la base de datos (los datos previos se descartan).
- **FR-003**: El sistema DEBE agregar el campo "Responsable del Depósito" (ComboBox) a la UI del Contrato de Arrendamiento.
- **FR-004**: El ComboBox DEBE listar dinámicamente los asesores activos obtenidos desde la base de datos, además de incluir al asesor actualmente asignado (incluso si está inactivo) para conservar el histórico visual al editar.
- **FR-005**: El sistema DEBE permitir que la selección de Responsable del Depósito sea opcional (guardar sin asignar si se desea).
- **FR-006**: El sistema DEBE persistir el identificador del asesor seleccionado en la tabla `CONTRATOS_ARRENDAMIENTOS` en PostgreSQL.
- **FR-007**: El sistema DEBE cargar y pre-seleccionar el responsable del depósito previamente asignado al abrir el modal de edición de un Contrato de Arrendamiento existente.
- **FR-008**: El sistema DEBE asegurar que el detalle de Solo Lectura del Contrato de Arrendamiento muestre el Responsable del Depósito, y removerlo del detalle del Contrato de Mandato.

### Key Entities

- **Contrato de Mandato**: Entidad principal de la que se remueve la relación con Responsable del Depósito.
- **Contrato de Arrendamiento**: Entidad principal a la que se le añade la relación opcional `responsable_deposito_id`.
- **Asesor**: Entidad de referencia que alimenta el listado del ComboBox (estado = activo).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% de los intentos de crear/editar Mandatos son exitosos sin incluir el dato del responsable del depósito.
- **SC-002**: 100% de los intentos de crear/editar Arrendamientos permiten seleccionar un responsable de depósito y este valor sobrevive a recargas de la página y cierres de sesión (persistencia comprobada).
- **SC-003**: 0% de regresiones en las funcionalidades ya existentes (creación, listado y detalle) de ambos tipos de contratos.

### Edge Cases

- **Asesor Inactivo**: Si un Contrato de Arrendamiento tiene asignado un responsable de depósito y este asesor pasa a estar inactivo en el sistema, al abrir el modal de edición, el ComboBox debe mostrar a este asesor como preseleccionado para no perder el dato. Si el usuario decide cambiarlo, solo podrá seleccionar de la lista de asesores activos.

## Assumptions

- Las tablas `CONTRATOS_MANDATOS` y `CONTRATOS_ARRENDAMIENTOS` en PostgreSQL son independientes y será necesario crear una migración SQL para transferir la columna o eliminarla de Mandatos y agregarla a Arrendamientos.
- La opción de responsables de depósito ya existe en el frontend o se puede reutilizar el listado de asesores activos que ya se utiliza para otros campos (como el asesor del contrato).
- No hay datos críticos en producción en la tabla de Mandatos para el campo `responsable_deposito_id` (la columna se eliminará descartando sus datos).
