# Feature Specification: fix-prod-diag-bugs

**Feature Branch**: `009-fix-prod-diag-bugs`

**Created**: 2026-07-03

**Status**: Draft

**Input**: User description: "/speckit-specify @specs\\008-playwright-prod-diag\\diagnostico.md"

## Clarifications

### Session 2026-07-03

- Q: Estrategia de Mitigación para Datos Nulos (Modal Liquidaciones) → A: Defensa en Código + Script de Backfill
- Q: Estrategia contra Saturación de Websocket (Tabla Incidentes) → A: Paginación Server-Side (Limit/Offset)

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Estabilidad en la Tabla de Incidentes (Priority: P1)

Como usuario administrador, necesito que la tabla de Incidentes cargue de manera confiable en producción, para poder visualizar los detalles y el plan de pagos de una propiedad específica sin que la conexión se sature o se desconecte.

**Why this priority**: Es el bloqueador principal (timeout de 15s) detectado en el diagnóstico. Si la tabla no carga, ningún flujo subsecuente en Incidentes puede realizarse.

**Independent Test**: Navegar a la vista de Incidentes en producción y verificar que la tabla (`.rt-TableRoot`) renderice con todos los datos sin arrojar errores de desconexión del websocket.

**Acceptance Scenarios**:

1. **Given** un entorno de producción con bases de datos PostgreSQL pobladas, **When** el usuario ingresa al módulo de Incidentes, **Then** la tabla se debe cargar en menos de 5 segundos.
2. **Given** la tabla de incidentes renderizada, **When** el usuario hace clic en el incidente de una propiedad específica (ej. "CONJ CIUDADELA COMFENALCO MZ H CS 29"), **Then** se debe abrir el drawer/modal que muestra la sección de "Plan de Pago" correctamente.

---

### User Story 2 - Apertura Confiable del Modal de Edición de Liquidaciones (Priority: P1)

Como administrador, necesito que al hacer clic en el botón "Editar" de una liquidación, el modal se abra sin fallos silenciosos, para poder gestionar los incidentes vinculados.

**Why this priority**: El modal nunca aparece en producción a pesar de que el evento de clic es procesado. Esto bloquea la gestión de cobros y facturación.

**Independent Test**: Al hacer clic en "Editar" sobre la liquidación de la propiedad "Calle Falsa 123 - Test Renov", el modal "Editar Liquidación" debe ser visible en la interfaz en menos de 2 segundos.

**Acceptance Scenarios**:

1. **Given** el módulo de liquidaciones, **When** el usuario presiona "Editar", **Then** el estado de la aplicación actualiza y despliega el modal en pantalla.
2. **Given** datos inconsistentes en la base de datos de producción (posibles nulos por migraciones incompletas), **When** se intenta cargar la liquidación, **Then** el backend debe procesar los nulos defensivamente y no arrojar una excepción silenciosa que frene el renderizado.

---

### User Story 3 - Eliminación de Liquidaciones sin Bloqueos de UI (Priority: P2)

Como administrador, necesito poder hacer clic en el botón "Eliminar" de una liquidación sin que capas invisibles o modales previos (Radix UI) bloqueen la interacción de mi ratón.

**Why this priority**: Las interacciones físicas quedan bloqueadas por `pointer-events: none` residuales, violando el estándar del `constitution.md`. Es un error crudo de Experiencia de Usuario.

**Independent Test**: Verificar que se puede hacer hover y click en el botón "Eliminar" en cualquier fila, enviando exitosamente el evento HTTP.

**Acceptance Scenarios**:

1. **Given** la tabla de liquidaciones visible, **When** el usuario hace hover o click en el botón "Eliminar", **Then** el evento del ratón es interceptado por el botón y el diálogo de confirmación se despliega inmediatamente.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El sistema MUST implementar paginación del lado del servidor (Limit/Offset) en la tabla de Incidentes, agregando controles de paginación en la UI, para prevenir la saturación de los websockets de Reflex al serializar datos masivos desde PostgreSQL.
- **FR-002**: El sistema MUST manejar de forma segura los valores nulos (None) en los campos de liquidación desde la base de datos (previniendo caídas en la hidratación del modal), y ADEMÁS se debe incluir un script de backfill/saneamiento de datos para normalizar los valores históricos en producción.
- **FR-003**: El sistema MUST implementar un override global en `BASE_STYLE` para inyectar `pointer-events: auto` en los contenedores de `rx.dialog.content` o elementos Radix relevantes, garantizando que ninguna capa bloquee interacciones posteriores de la interfaz.

### Key Entities

- **Incidente**: Entidad principal que debe cargarse sin saturar la red (optimización de serialización).
- **Liquidacion**: Entidad que sufre fallos de carga en modal debido a inconsistencias de datos de producción vs local.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: El script automatizado `test_prod_diag.py` supera las 3 pruebas E2E (Plan de Pago, Seleccionar Incidentes, Acción Eliminar) en el entorno de producción en menos de 30 segundos totales.
- **SC-002**: El log de la consola JS de producción muestra cero incidencias del error `Disconnect websocket on page navigation` asociadas a carga excesiva de estado.
- **SC-003**: El tiempo de renderizado interactivo (Time-to-Interactive) de las tablas de Incidentes y Liquidaciones se mantiene por debajo de 3 segundos en condiciones de red 4G/3G simuladas.

## Assumptions

- Se asume que el problema de `Disconnect websocket` en Incidentes es originado por el tamaño excesivo del payload del estado Reflex y no por limitaciones del balanceador de carga de Railway.
- Se asume que la estructura de datos que rompe el modal de edición involucra campos recientemente migrados de SQLite a PostgreSQL que no fueron normalizados en producción.
- Se asume que el estilo global de Radix (`BASE_STYLE`) está centralizado en un archivo como `styles.py` u homólogo en el ecosistema Reflex actual del proyecto.
