# Feature Specification: playwright-prod-diag

**Feature Branch**: `[008-playwright-prod-diag]`

**Created**: 2026-07-03

**Status**: Draft

**Input**: User description: "Ingeniería inversa, diagnóstico y validación funcional de nivel Senior/Principal sobre los módulos Incidentes y Liquidaciones de Propietarios utilizando Playwright en modo visible (headed)."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Validación del Plan de Pago en Incidentes (Priority: P1)

El sistema debe permitir validar en producción que el flujo de Plan de Pagos en el módulo de Incidentes muestre las cuotas correctas, con el valor asociado a la cotización y un estado consistente con la base de datos, para la propiedad "CONJ CIUDADELA COMFENALCO MZ H CS 29".

**Why this priority**: Asegura la integridad financiera y visual de la aplicación para los propietarios y administradores.

**Independent Test**: Can be fully tested by navigating directly to the Incidentes module, locating the specific property, and inspecting the loaded DOM elements.

**Acceptance Scenarios**:

1. **Given** un usuario autenticado en producción, **When** accede al incidente de la propiedad, **Then** visualiza la sección Plan de Pago con las cuotas generadas correctamente.
2. **Given** que la sección Plan de Pago no carga, **When** se inspecciona la red y consola, **Then** se debe identificar la causa raíz (frontend, backend, base de datos).

---

### User Story 2 - Validación del botón Seleccionar Incidentes (Priority: P1)

El sistema debe permitir diagnosticar el comportamiento del botón "Seleccionar Incidentes" dentro del modal de edición de liquidaciones para la propiedad "Calle Falsa 123 - Test Renov".

**Why this priority**: Existe un reporte de que el botón no renderiza o no funciona en producción a diferencia del entorno local.

**Independent Test**: Can be fully tested by navigating to Liquidaciones, opening the edit modal, and verifying the presence and clickability of the button.

**Acceptance Scenarios**:

1. **Given** el modal de edición abierto, **When** la liquidación es elegible, **Then** el botón "Seleccionar Incidentes" está visible y abre la lista filtrada (sin estado Pagado).
2. **Given** la selección de uno o más incidentes, **When** se confirma, **Then** se actualiza el campo correspondiente.

---

### User Story 3 - Validación de la acción Eliminar (Priority: P1)

Verificar y diagnosticar la funcionalidad de eliminación en el módulo de Liquidaciones para el entorno Sandbox.

**Why this priority**: La acción destructiva falla silenciosamente en producción.

**Independent Test**: Can be fully tested by attempting to delete a liquidation record and capturing the network events and console errors.

**Acceptance Scenarios**:

1. **Given** una liquidación en tabla, **When** se hace clic en Eliminar y se confirma, **Then** la red emite la solicitud correcta y la tabla se actualiza reflejando la eliminación.

---

### User Story 4 - Diagnóstico Comparativo Local vs Producción (Priority: P1)

Realizar un análisis exhaustivo del entorno para documentar las causas de las asimetrías de funcionalidad.

**Why this priority**: Fundamental para garantizar que los despliegues de Railway reflejen 100% las funcionalidades testeadas localmente.

**Independent Test**: Can be fully tested by extracting logs, variables, y network traces del entorno desplegado y comparándolas con el local.

**Acceptance Scenarios**:

1. **Given** los fallos evidenciados, **When** se contrastan configuraciones, migraciones, builds y dependencias, **Then** se documenta la causa raíz exacta y la solución técnica.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: La ejecución de Playwright MUST realizarse en modo visible (`headed=True`).
- **FR-002**: El sistema MUST interactuar con el entorno de producción (`https://extraordinary-joy-production-2fd2.up.railway.app/`).
- **FR-003**: El script MUST autenticarse exitosamente usando credenciales inyectadas o hardcodeadas (solo por protocolo de diagnóstico).
- **FR-004**: El sistema MUST capturar y analizar solicitudes HTTP, respuestas y logs de consola durante cada User Story.
- **FR-005**: El análisis MUST contemplar un chequeo de infraestructura (commits desplegados, caché, CORS, estado de migraciones) para justificar discrepancias con el entorno local.

### Key Entities

- **Incidente**: Entidad base que contiene cotizaciones y genera un plan de pago.
- **Liquidación**: Entidad que agrupa cobros, incluyendo incidentes no pagados, susceptible a edición y eliminación.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Se documenta exitosamente el origen del 100% de los fallos observados (1. Plan de Pago, 2. Seleccionar Incidentes, 3. Eliminar).
- **SC-002**: El informe entregado identifica claramente el componente afectado (Frontend, DB, Backend, Despliegue) de cada discrepancia sin ambigüedades.
- **SC-003**: La solución propuesta minimiza el impacto arquitectónico y mantiene el cumplimiento del protocolo Zero Leak.

## Assumptions

- Se asume que las credenciales provistas tienen los permisos RBAC suficientes para acceder, editar y eliminar en Sandbox dentro del entorno de producción.
- Se asume que el servidor local está disponible o su comportamiento funcional ya es conocido y reproducible como baseline.
- Se asume que Playwright puede evadir o manejar tiempos de espera prolongados derivados de la latencia en Railway.
