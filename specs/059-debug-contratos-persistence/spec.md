# Feature Specification: Auditoría y Corrección de Persistencia en Módulo de Contratos

**Feature Branch**: `059-debug-contratos-persistence`

**Created**: 2026-07-21

**Status**: Draft

**Input**: User description: "Debugger Senior exhaustivo de ingeniería inversa sobre el módulo de Contratos (modales Nuevo Contrato de Mandato y Nuevo Contrato de Arrendamiento). Se requiere validar integridad de persistencia de TODOS los campos en Create, Read y Update, eliminando discrepancias entre datos ingresados y datos recuperados."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Persistencia Completa al Crear Contrato de Mandato (Priority: P1)

Un usuario crea un Nuevo Contrato de Mandato llenando TODOS los campos del formulario (información general, datos del inmueble, datos del propietario, datos del arrendatario, información de pago, recepción de inventario, cláusulas, etc.). Al guardar, el sistema muestra mensaje de éxito. Al posteriormente editar el mismo contrato, TODOS los campos deben contener la información que fue ingresada originalmente.

**Why this priority**: Este es el reporte del bug original — campos de Información de Pago y Recepción de Inventario se pierden al editar. Representa la falla primaria que motivó la auditoría.

**Independent Test**: Crear un Contrato de Mandato con todos los campos llenos, guardarlo, luego abrirlo en modo edición y verificar que cada campo contiene el valor original.

**Acceptance Scenarios**:

1. **Given** el formulario de Nuevo Contrato de Mandato está abierto con todos los campos vacíos, **When** el usuario llena todos los campos (incluyendo Información de Pago y Recepción de Inventario) y presiona Guardar, **Then** el sistema muestra mensaje de éxito y el contrato se crea en la base de datos.
2. **Given** un Contrato de Mandato fue creado exitosamente con todos los campos, **When** el usuario abre el contrato en modo edición, **Then** TODOS los campos muestran los valores que fueron ingresados al crearlo.
3. **Given** un Contrato de Mandato fue creado exitosamente, **When** se consulta directamente la base de datos, **Then** los registros en las tablas correspondientes contienen TODOS los valores de todos los campos del formulario.

---

### User Story 2 - Persistencia Completa al Crear Contrato de Arrendamiento (Priority: P1)

Un usuario crea un Nuevo Contrato de Arrendamiento llenando TODOS los campos del formulario. Al guardar, el sistema muestra mensaje de éxito. Al posteriormente editar el mismo contrato, TODOS los campos deben contener la información que fue ingresada originalmente.

**Why this priority**: Mismo tipo de bug que P1 pero en el segundo tipo de contrato. Ambos tipos deben funcionar correctamente.

**Independent Test**: Crear un Contrato de Arrendamiento con todos los campos llenos, guardarlo, luego abrirlo en modo edición y verificar que cada campo contiene el valor original.

**Acceptance Scenarios**:

1. **Given** el formulario de Nuevo Contrato de Arrendamiento está abierto, **When** el usuario llena todos los campos y presiona Guardar, **Then** el sistema muestra mensaje de éxito y el contrato se crea en la base de datos.
2. **Given** un Contrato de Arrendamiento fue creado exitosamente, **When** el usuario abre el contrato en modo edición, **Then** TODOS los campos muestran los valores originales.

---

### User Story 3 - Corrección de Campos Específicos Identificados (Priority: P1)

Los campos de "Información de Pago" y "Recepción de Inventario" en el Contrato de Mandato deben persistirse correctamente y recuperarse al editar. Estos campos fueron identificados como los casos reportados del bug.

**Why this priority**: Son los campos específicamente reportados como fallidos por el usuario.

**Independent Test**: Crear un Contrato de Mandato, llenar solo los campos de Información de Pago y Recepción de Inventario, guardar, y verificar que se recuperan al editar.

**Acceptance Scenarios**:

1. **Given** un Contrato de Mandato con datos en Información de Pago y Recepción de Inventario, **When** se abre en modo edición, **Then** ambos grupos de campos muestran los valores ingresados.
2. **Given** un Contrato de Mandato con datos en Información de Pago y Recepción de Inventario, **When** se consulta la base de datos, **Then** los valores están correctamente almacenados en las columnas/tablas correspondientes.

---

### User Story 4 - Auditoría de Integridad Completa (Priority: P2)

Se realiza una auditoría que mapea cada campo del formulario de ambos tipos de contrato contra la base de datos, verificando que exista una ruta completa de persistencia: componente UI → Estado (State) → DTO/Servicio → Repositorio → Tabla PostgreSQL.

**Why this priority**: Permite identificar TODOS los campos con problemas, no solo los reportados. Espreventiva.

**Independent Test**: Generar un mapeo campo-a-columna para cada formulario y verificar que cada campo tiene una ruta de persistencia completa.

**Acceptance Scenarios**:

1. **Given** la auditoría completada, **When** se revisa el mapeo de campos, **Then** cada campo del formulario tiene una ruta de persistencia documentada y verificada.
2. **Given** la auditoría completada, **When** se identifican campos sin persistencia, **Then** se genera un listado de todos los campos con problemas y su causa raíz.

---

### User Story 5 - Actualización (Update) Correcta (Priority: P2)

Al editar un contrato existente y modificar campos, los cambios deben persistirse correctamente en la base de datos y reflejarse en consultas posteriores.

**Why this priority**: El bug puede afectar tanto Create como Update. Verificar que la operación Update funciona correctamente es crítico.

**Independent Test**: Editar un contrato existente, cambiar varios campos, guardar, y verificar que los cambios se reflejan en la base de datos y al re-abrir el formulario.

**Acceptance Scenarios**:

1. **Given** un contrato existente abierto en modo edición, **When** el usuario modifica campos y presiona Guardar, **Then** los cambios se persisten correctamente en la base de datos.
2. **Given** un contrato fue editado exitosamente, **When** se reabre en modo edición, **Then** todos los campos modificados muestran los nuevos valores.

---

### Edge Cases

- ¿Qué sucede cuando un campo del formulario está vacío al crear y luego se llena al editar? ¿Se persiste correctamente el valor actualizado?
- ¿Qué sucede cuando un contrato tiene campos con valores numéricos, fechas, booleanos y texto libre? ¿Todos los tipos de dato se manejan correctamente?
- ¿Qué sucede cuando se crea un contrato con datos mínimos (solo campos obligatorios) y luego se edita agregando campos opcionales? ¿Los nuevos campos se persisten?
- ¿Qué sucede si hay campos calculados o derivados? ¿Se recalculan correctamente al editar?
- ¿Qué sucede con campos que dependen de selecciones en cascada (ej: tipo de contrato afecta campos disponibles)?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El sistema MUST persistir TODOS los campos del formulario de "Nuevo Contrato de Mandato" en la base de datos al momento de crear el contrato, y corregir retroactivamente contratos existentes con datos incompletos.
- **FR-002**: El sistema MUST persistir TODOS los campos del formulario de "Nuevo Contrato de Arrendamiento" en la base de datos al momento de crear el contrato, y corregir retroactivamente contratos existentes con datos incompletos.
- **FR-003**: El sistema MUST recuperar TODOS los campos almacenados al abrir un contrato en modo edición, sin importar el tipo de contrato.
- **FR-004**: El sistema MUST persistir correctamente los campos de "Información de Pago" al crear o editar un Contrato de Mandato.
- **FR-005**: El sistema MUST persistir correctamente los campos de "Recepción de Inventario" al crear o editar un Contrato de Mandato.
- **FR-006**: El sistema MUST mantener consistencia entre los datos ingresados por el usuario y los datos almacenados en la base de datos (sin pérdida de información).
- **FR-007**: El sistema MUST ejecutar la operación de actualización (UPDATE) correctamente al modificar un contrato existente.
- **FR-008**: El sistema MUST validar que cada campo del formulario tenga una ruta de persistencia completa: UI → State → DTO/Servicio → Repositorio → Base de datos.
- **FR-009**: El sistema MUST ejecutar transacciones de base de datos de forma atómica al guardar contratos (rollback completo si falla cualquier paso).
- **FR-010**: El sistema MUST generar un log de auditoría para cada operación de creación y actualización de contratos.
- **FR-011**: El sistema MUST mapear cada campo del formulario a la columna/tabla correspondiente en la base de datos, sin campos huérfanos.
- **FR-012**: El sistema MUST validar que los tipos de datos en el formulario coincidan con los tipos de datos en la base de datos (fechas como ISO 8601, booleanos explícitos, etc.).

### Key Entities

- **Contrato de Mandato**: Acuerdo entre la inmobiliaria y el propietario para administrar un inmueble. Incluye: datos del contrato, datos del inmueble, datos del propietario, datos del arrendatario, información de pago, recepción de inventario, cláusulas y condiciones.
- **Contrato de Arrendamiento**: Acuerdo entre la inmobiliaria (o propietario) y el arrendatario para alquiler de un inmueble. Incluye: datos del contrato, datos del inmueble, datos del propietario, datos del arrendatario, información de pago, condiciones de arrendamiento.
- **Información de Pago**: Grupo de campos que define métodos, montos, fechas y cuentas bancarias asociadas al pago del contrato.
- **Recepción de Inventario**: Grupo de campos que documenta el inventario entregado al momento de la firma del contrato.
- **Base de datos PostgreSQL**: Almacén persistente donde se guardan todos los datos de contratos.
- **Estado de Reflex (State)**: Capa intermedia en el frontend que gestiona el estado del formulario antes de enviarlo al backend.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% de los campos de ambos formularios (Contrato de Mandato y Contrato de Arrendamiento) se persisten correctamente al crear un nuevo contrato.
- **SC-002**: 100% de los campos de ambos formularios se recuperan correctamente al abrir un contrato en modo edición (nuevos y existentes).
- **SC-003**: 0 campos identificados sin ruta de persistencia completa después de la auditoría.
- **SC-004**: Los campos de "Información de Pago" y "Recepción de Inventario" (reportados como fallidos) se persisten y recuperan correctamente en 100% de los casos de prueba, incluyendo contratos existentes.
- **SC-005**: La operación de actualización (Update) persiste correctamente todos los campos modificados en 100% de los casos de prueba.
- **SC-006**: No existen discrepancias entre los datos ingresados por el usuario y los datos almacenados en la base de datos después de la corrección.
- **SC-007**: Cada campo del formulario tiene documentado su mapeo completo: componente UI → Estado → DTO → Repositorio → Columna en BD.
- **SC-008**: Los contratos existentes con datos incompletos en Información de Pago o Recepción de Inventario son corregidos retroactivamente.

## Clarifications

### Session 2026-07-21

- Q: ¿Corregir ambos tipos de contrato o solo Mandato? → A: Corregir Mandato y Arrendamiento en la misma iteración (comparten infraestructura de persistencia).
- Q: ¿Qué nivel de testing se espera? → A: Tests de integración para flujos de persistencia (Create/Read/Update).
- Q: ¿Documentar el mapeo de persistencia? → A: Documentar el mapeo como referencia técnica en specs/ o docs/.
- Q: ¿Corregir retroactivamente contratos existentes? → A: Sí, la corrección debe cubrir contratos existentes con datos incompletos, nuevos contratos y ediciones.
- Q: ¿Proceder con migraciones SQL si son necesarias? → A: Sí, proceder con migraciones si la auditoría las requiere.

## Assumptions

- La base de datos PostgreSQL está operativa y accesible para pruebas.
- El módulo de Contratos ya existe en el código y está funcional (crea contratos con éxito aparente).
- Los campos de "Información de Pago" y "Recepción de Inventario" están presentes en el formulario UI pero no se persisten correctamente.
- El framework utilisé es Reflex (Python) con estado reactivo y repositorios PostgreSQL.
- La arquitectura sigue Clean Architecture: Dominio → Aplicación → Infraestructura → Presentación.
- No se requieren cambios en la estructura de tablas de la base de datos **salvo que la auditoría identifique columnas faltantes** (en cuyo caso se procede con migraciones SQL).
- Los contratos de Mandato y Arrendamiento son tipos distintos con formularios distintos pero comparten infraestructura de persistencia.
