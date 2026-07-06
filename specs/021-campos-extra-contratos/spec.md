# Feature Specification: campos-extra-contratos

**Feature Branch**: `[021-campos-extra-contratos]`

**Created**: 2026-07-05

**Status**: Draft

**Input**: User description: "/speckit-specify Quiero que realices un proceso de ingeniería inversa de nivel Senior/Principal sobre el módulo Contratos, con el objetivo de comprender su arquitectura funcional, la estructura de la base de datos, la lógica de negocio y los componentes de la interfaz antes de implementar las siguientes mejoras... [truncated for length]"

## Clarifications

### Session 2026-07-05

- Q: Restricción de dominios para el video → A: Aceptar cualquier URL bien formada (http/https) sin restringir el dominio.
- Q: Estado vacío de asesores → A: Mostrar mensaje informativo en el selector, pero permitir guardar el contrato sin responsable (campo opcional).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Video de recibo en contratos (Priority: P1)

Como usuario del sistema (asesor o administrador), quiero registrar la URL del video de recibo del inmueble en el contrato (Mandato o Arrendamiento) para mantener el respaldo audiovisual centralizado.

**Why this priority**: Es el requerimiento 1 y fundamental para el control del estado del inmueble.

**Independent Test**: Se puede probar creando o editando un contrato de Arrendamiento o Mandato, llenando el campo del enlace y verificando que se persista en la base de datos.

**Acceptance Scenarios**:

1. **Given** el formulario de creación de un contrato (Mandato o Arrendamiento), **When** se ingresa una URL en el nuevo campo "Enlace de video", **Then** el valor se guarda correctamente al finalizar la creación.
2. **Given** un contrato existente, **When** abro el modal de edición, **Then** el campo de enlace muestra el valor guardado previamente y permite modificarlo.

---

### User Story 2 - Responsable del depósito en Mandato (Priority: P1)

Como usuario administrador, quiero asignar un "responsable del depósito" desde una lista de asesores activos al crear un Contrato de Mandato, para tener trazabilidad de quién custodia dichos fondos.

**Why this priority**: Es el requerimiento 2 y de alto impacto para la trazabilidad y la responsabilidad financiera.

**Independent Test**: Se puede probar verificando que en el modal de Contrato de Mandato exista el ComboBox, este liste los asesores y se pueda seleccionar uno, guardándose la selección en la base de datos.

**Acceptance Scenarios**:

1. **Given** el formulario de Contrato de Mandato, **When** abro el selector de "Responsable del depósito", **Then** se me muestra una lista obtenida dinámicamente de los asesores activos del sistema.
2. **Given** el formulario de Contrato de Mandato, **When** selecciono un asesor y guardo el contrato, **Then** la asignación queda guardada en la base de datos y asociada a ese contrato.
3. **Given** un Contrato de Mandato con un responsable asignado, **When** se edita el contrato, **Then** el asesor previamente seleccionado aparece correctamente cargado en el ComboBox.

### Edge Cases

- ¿Qué sucede si el enlace proporcionado supera el límite de longitud estándar (ej. 255 caracteres)? El sistema debe manejar URLs largas o aplicar validación de tamaño.
- ¿Qué sucede si un asesor que era responsable de un depósito es posteriormente desactivado en el sistema? Su histórico debe mantenerse intacto y visible al visualizar/editar el contrato.
- ¿El campo de enlace de video es obligatorio o opcional? Asumiremos que es opcional para evitar bloquear contratos si aún no tienen video.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El sistema DEBE permitir el ingreso de una URL (cadena de texto) para almacenar el enlace de video del recibo del inmueble, validando únicamente que sea una URL bien formada (http/https) sin restricciones de dominio.
- **FR-002**: El campo de "Enlace de video" DEBE estar presente en la UI (creación y edición) tanto para Contratos de Mandato como para Contratos de Arrendamiento.
- **FR-003**: El sistema DEBE permitir la selección de un "Responsable del depósito" exclusivamente en la interfaz de Contratos de Mandato. Este campo será opcional; si no hay asesores activos, se mostrará un mensaje informativo en el selector pero no se bloqueará el guardado del contrato.
- **FR-004**: El selector de responsable del depósito DEBE listar a los asesores/usuarios activos en el sistema consultados desde la base de datos.
- **FR-005**: El sistema DEBE almacenar estos dos nuevos campos de manera persistente en PostgreSQL, respetando el modelo de datos y las relaciones foráneas (en el caso del responsable del depósito).

### Key Entities *(include if feature involves data)*

- **ContratoMandato**: Entidad que se enriquecerá con los campos `enlace_video` (opcional) y `responsable_deposito_id` (opcional, llave foránea hacia asesor/usuario).
- **ContratoArrendamiento**: Entidad que se enriquecerá con el campo `enlace_video` (opcional).
- **Asesor / Usuario**: Entidad que provee los valores para la selección en el campo de "Responsable del depósito".

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Los contratos nuevos y editados guardan consistentemente los nuevos campos sin errores de base de datos ni validación (0 errores reportados al realizar la acción).
- **SC-002**: El tiempo de carga de los modales y el ComboBox de asesores se mantiene por debajo de 1 segundo (sin degradación por la nueva consulta dinámica).
- **SC-003**: 100% de persistencia correcta entre el Frontend (Reflex) y Backend (PostgreSQL) para los campos modificados en todos los ciclos de vida del contrato (crear, ver, editar).

## Assumptions

- Se asume que el enlace del video será opcional, por lo cual los contratos existentes no fallarán por no tenerlo.
- Se asume que el "responsable del depósito" corresponde a la misma tabla de usuarios o asesores que el sistema ya maneja para otras asignaciones y que también será un campo opcional para no romper registros anteriores.
