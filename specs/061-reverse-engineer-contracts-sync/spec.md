# Feature Specification: Ingeniería Inversa - Sincronización Contratos, Liquidaciones y Recaudos

**Feature Branch**: `061-reverse-engineer-contracts-sync`

**Created**: 2026-07-22

**Status**: Draft

**Input**: User description: "Realizar ingeniería inversa sobre los módulos de Contratos, Liquidaciones de Propietarios y Recaudos para validar la correcta ejecución e integración de las reglas de negocio entre estos componentes."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Validación de Cascada de Renovación (Priority: P1)

Como auditor del sistema, necesito verificar que cuando se renueva un contrato de arrendamiento y se modifica el canon, el sistema actualice correctamente el Canon de Mandato y el Canon Estimado de la Propiedad, para garantizar la integridad de datos entre módulos.

**Why this priority**: Es el punto crítico del flujo de negocio. Si la cascada falla, los datos financieros serán inconsistentes.

**Independent Test**: Puede probarse ejecutando una renovación de contrato y verificando que los valores en las tablas CONTRATOS_MANDATOS y PROPIEDADES se actualicen correctamente.

**Acceptance Scenarios**:

1. **Given** un contrato de arrendamiento activo con canon = 1.000.000 y su mandato asociado, **When** se renueva el contrato con un nuevo canon = 1.100.000 (incremento IPC), **Then** el mandato asociado debe tener canon_mandato = 1.100.000 y la propiedad debe tener canon_arrendamiento_estimado = 1.100.000.
2. **Given** un contrato de arrendamiento activo, **When** se renueva el contrato, **Then** se crea un registro en RENOVACIONES_CONTRATOS con el canon_anterior, canon_nuevo y porcentaje_incremento correctos.
3. **Given** un contrato de arrendamiento activo con fecha_fin = 2026-12-31, **When** se renueva con duración de 12 meses, **Then** la nueva fecha_fin debe ser 2027-12-31 y el mandato debe sincronizarse con la misma fecha.

---

### User Story 2 - Preservación de Registros Históricos (Priority: P1)

Como auditor del sistema, necesito verificar que las liquidaciones y recaudos generados ANTES de una renovación conserven intactos sus valores originales, para garantizar la trazabilidad financiera.

**Why this priority**: La integridad de datos históricos es crítica para auditorías y reportes financieros.

**Independent Test**: Puede probarse verificando que una liquidación generada con el canon anterior no se modifique después de una renovación.

**Acceptance Scenarios**:

1. **Given** una liquidación generada en período 2026-06 con canon_bruto = 1.000.000, **When** se renueva el contrato en julio 2026 con canon = 1.100.000, **Then** la liquidación del período 2026-06 debe mantener canon_bruto = 1.000.000.
2. **Given** un recaudo generado en período 2026-06 con valor_total = 1.000.000, **When** se renueva el contrato en julio 2026, **Then** el recaudo del período 2026-06 debe mantener valor_total = 1.000.000.
3. **Given** liquidaciones y recaudos en múltiples períodos históricos, **When** se ejecuta una renovación, **Then** Ningún registro histórico debe ser modificado.

---

### User Story 3 - Generación con Canon Actualizado (Priority: P2)

Como administrador del sistema, necesito que las liquidaciones y recaudos generados DESPUÉS de una renovación utilicen el nuevo canon, para reflejar las condiciones contractuales vigentes.

**Why this priority**: Asegura que los nuevos documentos financieros sean correctos.

**Independent Test**: Puede probarse generando liquidaciones y recaudos después de una renovación y verificando que usen el nuevo canon.

**Acceptance Scenarios**:

1. **Given** un contrato renovado con canon_nuevo = 1.100.000, **When** se genera la liquidación del período 2026-08, **Then** el canon_bruto de la liquidación debe ser 1.100.000.
2. **Given** un contrato renovado con canon_nuevo = 1.100.000, **When** se genera el recaudo del período 2026-08, **Then** el valor_total del recaudo debe ser 1.100.000.
3. **Given** un contrato renovado, **When** se generan liquidaciones y recaudos para múltiples períodos futuros, **Then** Todos deben usar el canon_nuevo.

---

### User Story 4 - Consistencia entre Módulos (Priority: P2)

Como auditor del sistema, necesito verificar que no existan discrepancias de datos entre los módulos de Contratos, Liquidaciones y Recaudos, para garantizar la coherencia integral del sistema.

**Why this priority**: La inconsistencia entre módulos puede generar errores financieros difíciles de detectar.

**Independent Test**: Puede probarse ejecutando consultas cruzadas entre módulos y verificando que los valores coincidan.

**Acceptance Scenarios**:

1. **Given** un contrato activo con su mandato y propiedad asociada, **When** se consultan los valores de canon en los tres módulos, **Then** Todos deben mostrar el mismo valor actualizado.
2. **Given** liquidaciones generadas para un período, **When** se comparan con el canon del mandato vigente para ese período, **Then** Las liquidaciones futuras deben coincidir con el mandato.
3. **Given** recaudos generados para un período, **When** se comparan con el canon del arrendamiento vigente para ese período, **Then** Los recaudos futuros deben coincidir con el arrendamiento.

---

### User Story 5 - Ausencia de Actualizaciones Retroactivas (Priority: P2)

Como auditor del sistema, necesito verificar que no existan procesos, consultas o sincronizaciones que apliquen actualizaciones de forma retroactiva sobre información histórica, para garantizar la integridad de datos.

**Why this priority**: Las actualizaciones retroactivas pueden corromper datos financieros históricos.

**Independent Test**: Puede probarse buscando en el código procesos que modifiquen liquidaciones o recaudos existentes después de su creación.

**Acceptance Scenarios**:

1. **Given** el código fuente del sistema, **When** se analizan todos los procesos de actualización, **Then** No debe existir ningún proceso que modifique el canon_bruto de liquidaciones ya generadas.
2. **Given** el código fuente del sistema, **When** se analizan todos los procesos de actualización, **Then** No debe existir ningún proceso que modifique el valor_total de recaudos ya generados.
3. **Given** scripts de migración o recálculo, **When** se ejecutan sobre la base de datos, **Then** No deben alterar registros de liquidaciones o recaudos históricos.

---

### User Story 6 - Respeto de Fecha de Vigencia (Priority: P3)

Como administrador del sistema, necesito que la fecha de vigencia de la renovación sea respetada en todos los procesos que dependan del canon, para asegurar que los cambios se apliquen solo desde el período correcto.

**Why this priority**: La fecha de vigencia determina desde cuándo aplican los nuevos valores.

**Independent Test**: Puede probarse verificando que liquidaciones generadas antes de la fecha de vigencia mantengan valores anteriores.

**Acceptance Scenarios**:

1. **Given** una renovación ejecutada el 2026-07-15, **When** se generan liquidaciones para períodos 2026-06 y 2026-08, **Then** El período 2026-06 debe usar el canon anterior y el 2026-08 debe usar el canon nuevo.
2. **Given** una renovación con fecha de vigencia específica, **When** se consultan liquidaciones y recaudos, **Then** Todos los registros deben respetar la fecha de vigencia establecida.

---

### Edge Cases

- ¿Qué sucede si se renueva un contrato que no tiene mandato asociado?
- ¿Qué sucede si se intenta generar una liquidación para un período ya existente?
- ¿Qué sucede si un recaudo está en estado "Aplicado" y se intenta modificar su valor?
- ¿Qué sucede si se ejecutan múltiples renovaciones en el mismo período?
- ¿Qué sucede si el repositorio de mandato es None durante la cascada?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El sistema MUST registrar cada renovación en RENOVACIONES_CONTRATOS con canon_anterior, canon_nuevo, porcentaje_incremento y motivo.
- **FR-002**: El sistema MUST actualizar el canon_mandato del contrato de mandato activo asociado a la propiedad cuando se renueva el arrendamiento.
- **FR-003**: El sistema MUST actualizar el canon_arrendamiento_estimado de la propiedad cuando se renueva el arrendamiento.
- **FR-004**: El sistema MUST sincronizar la fecha_fin del mandato con la nueva fecha_fin del arrendamiento durante la renovación.
- **FR-005**: Las liquidaciones generadas MUST persistir el valor de canon_bruto al momento de su creación.
- **FR-006**: Los recaudos generados MUST persistir el valor de valor_total al momento de su creación.
- **FR-007**: El sistema MUST generar liquidaciones usando el canon_mandato vigente al momento de la generación.
- **FR-008**: El sistema MUST generar recaudos usando el canon_arrendamiento del contrato activo al momento de la generación.
- **FR-009**: No MUST existir procesos que modifiquen retroactivamente el canon_bruto de liquidaciones ya generadas.
- **FR-010**: No MUST existir procesos que modifiquen retroactivamente el valor_total de recaudos ya generados.
- **FR-011**: La cascada de sincronización MUST ser transaccional (todo o nada).
- **FR-012**: El sistema MUST registrar cada cambio en AUDITORIA_CAMBIOS para trazabilidad.
- **FR-013**: La fecha de vigencia de la renovación MUST ser respetada por todos los procesos dependientes.
- **FR-014**: El sistema MUST invalidar la caché de propiedades después de una renovación.
- **FR-015**: El sistema MUST calcular correctamente el incremento IPC cuando la duración del contrato es >= 12 meses.

### Key Entities

- **ContratoArrendamiento**: Acuerdo de alquiler entre Inmobiliaria y Arrendatario. Campo clave: `canon_arrendamiento`.
- **ContratoMandato**: Acuerdo entre Propietario e Inmobiliaria para administrar una propiedad. Campo clave: `canon_mandato`.
- **Propiedad**: Inmueble administrado. Campo clave: `canon_arrendamiento_estimado`.
- **RenovacionContrato**: Registro histórico de renovaciones. Campos: `canon_anterior`, `canon_nuevo`, `fecha_renovacion`.
- **Liquidacion**: Estado de cuenta mensual del propietario. Campo clave: `canon_bruto` (persistido al crear).
- **Recaudo**: Pago recibido del inquilino. Campo clave: `valor_total` (persistido al crear).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% de las renovaciones de contrato propagan correctamente el canon a Mandato y Propiedad.
- **SC-002**: 0% de registros históricos de liquidaciones son modificados después de una renovación.
- **SC-003**: 0% de registros históricos de recaudos son modificados después de una renovación.
- **SC-004**: 100% de liquidaciones futuras usan el canon actualizado después de una renovación.
- **SC-005**: 100% de recaudos futuros usan el canon actualizado después de una renovación.
- **SC-006**: 0% de discrepancias de datos entre módulos Contratos, Liquidaciones y Recaudos.
- **SC-007**: 0% de procesos que apliquen actualizaciones retroactivas sobre datos históricos.
- **SC-008**: 100% de las renovaciones registran historial completo en RENOVACIONES_CONTRATOS.

## Assumptions

- Los contratos de arrendamiento y mandato están correctamente relacionados por ID_PROPIEDAD.
- La base de datos PostgreSQL está operativa y contiene datos de prueba representativos.
- Los repositorios están correctamente implementados y conectados a la base de datos.
- El sistema de caché invalida correctamente las entradas afectadas por renovaciones.
- Los scripts de migración no alteran datos de liquidaciones o recaudos existentes.
- La lógica de cálculo de IPC está correctamente implementada en CalculadoraContratos.

## Aclaraciones

### A1 - Formato del Entregable
**Decisión**: Script repeatable que genera informe de texto estructurado con pass/fail por criterio de éxito.
**Justificación**: Permite ejecución periódica post-cambio de código y diagnóstico rápido de inconsistencias.

### A2 - Fuente de Datos para Validación
**Decisión**: Datos de prueba controlados en entorno de staging.
**Justificación**: Permite controlar escenarios exactos y reproducir resultados. Datos de producción son impredecibles.

### A3 - Estrategia de Remediación
**Decisión**: Registrar hallazgos en el informe con recomendaciones específicas (valores esperados vs encontrados), sin modificar código.
**Justificación**: La corrección inmediata puede introducir cambios no deseados sin una revisión completa.

### A4 - Definición de "Retroactivo"
**Decisión**: Cualquier modificación de un registro después de su creación inicial constituye una actualización retroactiva, independientemente del estado del registro.
**Justificación**: Definición más restrictiva y segura para protección de datos financieros históricos.

### A5 - Frecuencia de Ejecución
**Decisión**: Script repeatable ejecutable después de cada cambio de código.
**Justificación**: Permite detectar regresiones tempranas y mantener integridad continua.
