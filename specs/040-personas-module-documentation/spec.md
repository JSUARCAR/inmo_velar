# Feature Specification: Manual de Usuario - Módulo Personas

**Feature Branch**: `040-personas-module-documentation`

**Created**: 2026-07-08

**Status**: Draft

**Input**: User description: "Actuar como Arquitecto de Documentación Técnica para completar y enriquecer el archivo personas.md con un manual de usuario empresarial completo, incluyendo capturas de pantalla y documentación funcional detallada."

## Clarifications

### Session 2026-07-08
- Q: ¿Cuál es el alcance de la documentación del manual? → A: Solo funcionalidades visibles en la UI actual (tabla, filtros, CRUD, exportación)
- Q: ¿Se debe documentar la navegación entre módulos? → A: No, solo el módulo Personas de forma independiente
- Q: ¿Se incluye configuración de permisos/RBAC? → A: Solo descripción de qué acciones requiere qué rol, no configuración técnica
- Q: ¿Cuántas capturas de pantalla se incluirán? → A: Moderado (8-10): vista general, filtros, tabla, cards, crear wizard, detalles, paginación, exportar
- Q: ¿En qué idioma se documentará el manual? → A: Solo español (consistente con la constitución del proyecto)
- Q: ¿Cómo se versionará el manual? → A: Versionado por fecha en encabezado (ej: "Actualizado: 2026-07-08")
- Q: ¿Quién es responsable del mantenimiento del manual? → A: Desarrolladores del módulo (actualizan al hacer cambios)

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Consulta y Gestión de Personas (Priority: P1)

Como administrador del sistema de Inmobiliaria Velar, necesito acceder al módulo de Personas para gestionar propietarios, arrendatarios, asesores, codeudores y proveedores de forma centralizada, visualizando KPIs, aplicando filtros y realizando operaciones CRUD.

**Why this priority**: Es la funcionalidad core del módulo. Sin ella, no existe valor en la documentación.

**Independent Test**: Puede probarse accediendo a `/personas`, verificando que se muestra la tabla de personas con KPIs y que los filtros funcionan correctamente.

**Acceptance Scenarios**:

1. **Given** que el usuario tiene permisos de acceso, **When** ingresa al módulo Personas, **Then** se muestra la tabla de personas con KPIs por rol (Propietarios, Arrendatarios, Asesores, Codeudores, Proveedores).
2. **Given** que existen personas registradas, **When** el usuario aplica un filtro por rol, **Then** la tabla se actualiza mostrando solo personas con ese rol.
3. **Given** que el usuario necesita buscar una persona específica, **When** ingresa texto en la barra de búsqueda y presiona Enter, **Then** se filtran los resultados por nombre o documento.

---

### User Story 2 - Creación de Nueva Persona (Priority: P1)

Como administrador, necesito crear nuevas personas en el sistema mediante un formulario guiado con wizard de múltiples pasos, asignando roles específicos y validando los datos ingresados.

**Why this priority**: La creación de personas es una operación fundamental para el funcionamiento del sistema inmobiliario.

**Independent Test**: Puede probarse haciendo clic en "Nueva Persona", completando el wizard de 3 pasos y verificando que el registro se crea correctamente.

**Acceptance Scenarios**:

1. **Given** que el usuario tiene permisos de creación, **When** hace clic en "Nueva Persona", **Then** se abre un modal con wizard de 3 pasos.
2. **Given** que se completa el paso 1 (datos básicos), **When** se avanzan al paso 2, **Then** se puede seleccionar uno o múltiples roles.
3. **Given** que se completa el wizard, **When** se envía el formulario, **Then** el sistema crea la persona y la muestra en la tabla.

---

### User Story 3 - Visualización de Detalles y Auditoría (Priority: P2)

Como auditor, necesito ver los detalles completos de una persona incluyendo su historial de cambios y roles asociados, para mantener trazabilidad de las operaciones.

**Why this priority**: La auditoría es importante pero no bloquea la operación básica del módulo.

**Independent Test**: Puede probarse haciendo clic en el icono de ojo (ver detalles) en cualquier fila de la tabla.

**Acceptance Scenarios**:

1. **Given** que el usuario selecciona ver detalles de una persona, **When** se abre el modal de detalles, **Then** se muestra información completa incluyendo roles, datos de contacto y fechas.
2. **Given** que existe historial de cambios, **When** se consulta el log de auditoría, **Then** se muestran las acciones realizadas con fechas y usuarios.

---

### User Story 4 - Exportación de Datos (Priority: P2)

Como gerente, necesito exportar los datos filtrados de personas a formato Excel/CSV para análisis externo y reportes gerenciales.

**Why this priority**: La exportación facilita el análisis de datos fuera del sistema pero no es crítica para la operación diaria.

**Independent Test**: Puede probarse aplicando filtros y haciendo clic en el botón de exportar, verificando que se descarga un archivo CSV válido.

**Acceptance Scenarios**:

1. **Given** que el usuario tiene filtros aplicados, **When** hace clic en exportar, **Then** se descarga un archivo CSV con los datos filtrados.
2. **Given** que no hay personas que cumplan los filtros, **When** se intenta exportar, **Then** se muestra un mensaje informativo.

---

### Edge Cases

- ¿Qué sucede cuando un usuario sin permisos intenta eliminar una persona? → El botón de eliminar no se muestra.
- ¿Cómo maneja el sistema una persona que tiene contratos activos y se intenta desactivar? → Se muestra advertencia o se bloquea la operación.
- ¿Qué ocurre si se intenta crear una persona con un documento que ya existe? → El sistema muestra error de duplicidad.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El sistema MUST mostrar una tabla paginada de personas con columnas: Nombre, Documento, Contacto, Fecha Creación, Roles, Estado y Acciones.
- **FR-002**: El sistema MUST calcular y mostrar KPIs por rol (Propietarios, Arrendatarios, Asesores, Codeudores, Proveedores) con conteos de activos e inactivos.
- **FR-003**: El sistema MUST permitir filtrar por rol (Todos, Propietario, Arrendatario, Codeudor, Asesor, Proveedor).
- **FR-004**: El sistema MUST permitir buscar por nombre o número de documento con búsqueda en tiempo real.
- **FR-005**: El sistema MUST permitir filtrar por rango de fechas de creación.
- **FR-006**: El sistema MUST permitir alternar la visualización de personas inactivas.
- **FR-007**: El sistema MUST permitir filtrar personas sin contrato asociado.
- **FR-008**: El sistema MUST soportar dos modos de vista: Tabla y Cards.
- **FR-009**: El sistema MUST permitir ordenar por columnas (Nombre, Documento, Fecha Creación, Estado).
- **FR-010**: El sistema MUST implementar paginación con navegación Anterior/Siguiente.
- **FR-011**: El sistema MUST permitir crear personas mediante un wizard de 3 pasos con validación en cada paso.
- **FR-012**: El sistema MUST permitir asignar múltiples roles a una persona (Propietario, Arrendatario, Asesor, Codeudor, Proveedor).
- **FR-013**: El sistema MUST permitir editar personas existentes.
- **FR-014**: El sistema MUST permitir desactivar/reactivar personas (soft delete).
- **FR-015**: El sistema MUST mostrar detalles completos de una persona en un modal dedicado.
- **FR-016**: El sistema MUST registrar auditoría de todas las operaciones (crear, editar, cambiar estado).
- **FR-017**: El sistema MUST exportar datos filtrados a formato CSV.
- **FR-018**: El sistema MUST aplicar control de acceso basado en roles (RBAC) para acciones de crear, editar y eliminar.

### Key Entities

- **Persona**: Entidad central que representa una persona física o jurídica en el sistema. Atributos: ID, nombre, tipo documento, número documento, teléfono, correo, dirección, fecha creación, estado.
- **Rol**: Clasificación de la persona dentro del ecosistema inmobiliario. Tipos: Propietario, Arrendatario, Asesor, Codeudor, Proveedor. Una persona puede tener múltiples roles.
- **KPI**: Indicadores clave de rendimiento que muestran conteos por rol (activos/inactivos).
- **Auditoría**: Registro de todas las operaciones realizadas sobre las personas para trazabilidad.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: El usuario puede visualizar la lista completa de personas en menos de 3 segundos después de acceder al módulo.
- **SC-002**: El usuario puede encontrar una persona específica usando los filtros en menos de 30 segundos.
- **SC-003**: El usuario puede crear una nueva persona completa en menos de 2 minutos usando el wizard.
- **SC-004**: El 100% de las operaciones CRUD generan registros de auditoría.
- **SC-005**: Los KPIs se actualizan en tiempo real al cambiar filtros.
- **SC-006**: La exportación CSV contiene todos los campos visibles en la tabla.
- **SC-007**: El manual documenta el 100% de las funcionalidades visibles en la interfaz.

## Out of Scope

- Flujos de navegación entre módulos (ej: Persona → Contrato)
- Configuración técnica de permisos o RBAC
- Guías de troubleshooting avanzado
- Documentación de APIs o endpoints
- Mantenimiento de base de datos

## Assumptions

- Los usuarios tienen conocimientos básicos de uso de sistemas web.
- Los usuarios tienen permisos según su rol (Operador, Administrador, Auditor).
- La conexión a internet es estable durante la operación.
- El sistema de autenticación está funcionando correctamente.
- Los datos de prueba están disponibles para documentar flujos.
- Las credenciales proporcionadas (jsuarcar/velarjoan2026) son válidas para acceso de prueba.
