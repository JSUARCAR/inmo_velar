# Feature Specification: Fix Payment Status Synchronization Between Liquidaciones and Incidentes

**Feature Branch**: `[033-fix-payment-sync-incidentes]`

**Created**: 2026-07-07

**Status**: Draft

**Input**: User description: "Quiero que realices un proceso de ingeniería inversa de nivel Senior/Principal sobre la integración entre los módulos Liquidaciones e Incidentes, ya que identifiqué una inconsistencia en la sincronización del estado de pago de los incidentes. El Incidente #53 tiene un plan de pago asociado a la Liquidación de Propietario #573. Al revisar el plan de pago del incidente, observo que la cuota asociada a la Liquidación #573 continúa con estado Pendiente y, como consecuencia, la tarjeta del incidente sigue mostrando el Estado de Pago: Pendiente. Sin embargo, al ingresar al módulo Liquidaciones, verifico que la Liquidación #573 ya se encuentra en estado Pagada. Existe, por tanto, una inconsistencia entre ambos módulos, ya que el cambio de estado de la liquidación no se está reflejando en el plan de pago del incidente ni en el estado de pago mostrado en la tarjeta del incidente."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Payment Status Sync After Liquidación Payment (Priority: P1)

Como usuario del sistema, necesito que cuando una Liquidación de Propietario asociada a un incidente cambie a estado "Pagada", el estado de pago del incidente se actualice automáticamente en tiempo real, para mantener la consistencia de la información financiera entre ambos módulos.

**Why this priority**: Este es el problema principal reportado. Si la sincronización no funciona, la información financiera está desactualizada, lo que puede llevar a errores en la toma de decisiones y pagos duplicados.

**Independent Test**: Puede ser probado creando una liquidación asociada a un incidente con plan de pago, marcándola como pagada, y verificando que el estado del incidente se actualice correctamente.

**Acceptance Scenarios**:

1. **Given** un incidente con plan de pago activo y una cuota asociada a una liquidación en estado "Aprobada", **When** se marca la liquidación como "Pagada", **Then** la cuota del plan de pago debe cambiar su estado de "Pendiente" a "Pagada".
2. **Given** un incidente con plan de pago activo y una cuota asociada a una liquidación en estado "Aprobada", **When** se marca la liquidación como "Pagada", **Then** el estado de pago del incidente debe actualizarse automáticamente a "Pagado" si todas sus cuotas están pagadas.
3. **Given** un incidente con plan de pago activo y múltiples cuotas asociadas a diferentes liquidaciones, **When** una de las liquidaciones se marca como "Pagada", **Then** el estado de pago del incidente debe actualizarse a "Parcialmente Pagado" si no todas las cuotas están pagadas.

---

### User Story 2 - Payment Status Display Consistency (Priority: P1)

Como usuario del sistema, necesito que la tarjeta del incidente muestre inmediatamente el estado de pago correcto después de que una liquidación asociada sea marcada como pagada, sin necesidad de recargar la página o realizar otra acción.

**Why this priority**: La experiencia de usuario se ve afectada directamente cuando la información mostrada no coincide con la información real en la base de datos.

**Independent Test**: Puede ser probado marcando una liquidación como pagada y verificando que la tarjeta del incidente actualice su badge de estado de pago sin recarga manual.

**Acceptance Scenarios**:

1. **Given** un incidente con estado de pago "Pendiente", **When** se marca una liquidación asociada como "Pagada", **Then** la tarjeta del incidente debe mostrar inmediatamente el nuevo estado de pago.
2. **Given** un incidente con estado de pago "Parcialmente Pagado", **When** se marca la última liquidación asociada como "Pagada", **Then** la tarjeta del incidente debe mostrar "Pagado".

---

### User Story 3 - Bulk Payment Status Sync (Priority: P2)

Como gestor financiero, necesito que cuando se realice un pago masivo de liquidaciones (múltiples liquidaciones de un propietario), el estado de pago de todos los incidentes afectados se actualice correctamente.

**Why this priority**: El pago masivo es una funcionalidad importante para la eficiencia operativa, y la falta de sincronización en este flujo puede causar inconsistencias en múltiples incidentes simultáneamente.

**Independent Test**: Puede ser probado seleccionando múltiples liquidaciones de un propietario y marcándolas como pagadas en bloque, verificando que todos los incidentes asociados actualicen su estado.

**Acceptance Scenarios**:

1. **Given** un propietario con múltiples liquidaciones asociadas a diferentes incidentes, **When** se realiza un pago masivo de todas las liquidaciones, **Then** todos los incidentes asociados deben actualizar su estado de pago correctamente.

---

### User Story 4 - Payment Reversal Status Sync (Priority: P2)

Como usuario del sistema, necesito que cuando se revierta el pago de una liquidación, el estado de pago del incidente asociado se recalcule correctamente, manteniendo la consistencia de la información.

**Why this priority**: La reversión de pagos es una operación que debe mantener la integridad de los datos entre módulos.

**Independent Test**: Puede ser probado revirtiendo el pago de una liquidación y verificando que el incidente asociado actualice su estado de pago.

**Acceptance Scenarios**:

1. **Given** un incidente con estado de pago "Pagado" (todas las cuotas pagadas), **When** se revierte el pago de una de las liquidaciones asociadas, **Then** el estado del incidente debe cambiar a "Parcialmente Pagado" o "Pendiente" según corresponda.
2. **Given** un incidente con estado de pago "Parcialmente Pagado", **When** se revierte el pago de la única liquidación pagada, **Then** el estado del incidente debe cambiar a "Pendiente".

---

### Edge Cases

- ¿Qué sucede cuando un incidente tiene múltiples cuotas asociadas a la misma liquidación?
- ¿Cómo maneja el sistema una liquidación que se cancela después de haber sido marcada como pagada?
- ¿Qué ocurre si hay un error de base de datos durante la actualización del estado de pago del incidente?
- ¿Cómo se comporta el sistema si se intenta marcar como pagada una liquidación que no tiene incidentes asociados?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST actualizar el estado de la cuota del plan de pago de "Asociada" a "Pagada" cuando la liquidación asociada cambie a estado "Pagada".
- **FR-002**: System MUST recalcular el estado de pago del incidente después de cada cambio de estado de una liquidación asociada.
- **FR-003**: System MUST actualizar el estado de pago del incidente a "Pagado" cuando todas sus cuotas estén pagadas.
- **FR-004**: System MUST actualizar el estado de pago del incidente a "Parcialmente Pagado" cuando algunas de sus cuotas estén pagadas.
- **FR-005**: System MUST actualizar el estado de pago del incidente a "Pendiente" cuando ninguna de sus cuotas esté pagada.
- **FR-006**: System MUST persistir los cambios de estado en la base de datos de manera atómica (transacción).
- **FR-007**: System MUST reflejar inmediatamente los cambios de estado en la interfaz de usuario sin necesidad de recarga manual.
- **FR-008**: System MUST manejar errores de sincronización sin afectar el proceso de pago principal.
- **FR-009**: System MUST sincronizar el estado de pago durante pagos masivos de liquidaciones.
- **FR-010**: System MUST sincronizar el estado de pago durante reversiones de pagos.

### Key Entities *(include if feature involves data)*

- **Incidente**: Entidad que representa un problema reportado. Contiene el campo `estado_pago` que refleja el estado general de pago del incidente.
- **PlanPagoIncidente**: Entidad que representa el plan de pago asociado a un incidente. Contiene el estado del plan y las cuotas.
- **CuotaIncidente**: Entidad que representa una cuota individual del plan de pago. Contiene `estado_pago` (Pendiente, Asociada, Pagada) y `id_liquidacion` (referencia a la liquidación asociada).
- **Liquidacion**: Entidad que representa la liquidación mensual de un propietario. Contiene `estado_liquidacion` (En Proceso, Aprobada, Pagada, Cancelada).
- **IncidenteLiquidacion**: Entidad de relación que vincula incidentes con liquidaciones.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% de las liquidaciones marcadas como "Pagada" actualizan correctamente el estado de pago de todos los incidentes asociados.
- **SC-002**: El estado de pago del incidente se refleja en la interfaz de usuario en menos de 2 segundos después del cambio de estado de la liquidación.
- **SC-003**: 100% de las reversiones de pago actualizan correctamente el estado de pago de los incidentes asociados.
- **SC-004**: Los pagos masivos sincronizan correctamente el estado de pago de todos los incidentes afectados.
- **SC-005**: No se pierden actualizaciones de estado debido a errores de sincronización (tolerancia a fallos).

## Assumptions

- Se asume que el esquema de base de datos actual ya cuenta con las tablas necesarias (CUOTA_INCIDENTE, PLAN_PAGO_INCIDENTE, INCIDENTE_LIQUIDACION) y sus relaciones correctas.
- Se asume que la lógica de negocio para los estados de pago (Pendiente, Parcialmente Pagado, Pagado) ya está definida y es correcta.
- Se asume que la interfaz de usuario ya tiene los componentes necesarios para mostrar el estado de pago y que solo necesitan actualizarse con los datos correctos.
- Se asume que el problema actual está en la capa de servicio/state y no en la base de datos o consultas SQL.
