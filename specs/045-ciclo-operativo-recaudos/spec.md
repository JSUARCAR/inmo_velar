# Feature Specification: Ciclo Operativo en Módulo Recaudos

**Feature Branch**: `045-ciclo-operativo-recaudos`

**Created**: 2026-07-11

**Status**: Draft

**Input**: User description: "Incorporar una nueva columna denominada Ciclo Operativo en la tabla principal del módulo Recaudos, cuyo valor se obtenga de la Liquidación de Propietarios asociada a cada recaudo."

## Clarifications

### Session 2026-07-11

- Q: ¿Cómo se resuelve cuál contrato de mandato es el "vigente" cuando hay múltiples? → A: Contrato con estado "Activo" y fecha de inicio más reciente dentro del periodo del recaudo.

## User Scenarios & Testing

### User Story 1 - Visualización del Ciclo Operativo en la tabla de Recaudos (Priority: P1)

Como usuario del módulo Recaudos, deseo ver una columna adicional llamada "Ciclo Operativo" en la tabla principal, para identificar rápidamente a qué grupo operativo pertenece cada recaudo sin necesidad de navegar a la liquidación asociada.

**Why this priority**: Es el objetivo principal de la feature. Sin esta columna, el usuario debe abrir cada liquidación individualmente para conocer el ciclo operativo, lo cual es ineficiente y propenso a errores.

**Independent Test**: Puede probarse completamente abriendo el módulo Recaudos y verificando que la columna aparece con valores correctos. Se entrega valor inmediato al usuario.

**Acceptance Scenarios**:

1. **Given** que existen recaudos con liquidaciones asociadas, **When** el usuario abre la tabla principal del módulo Recaudos, **Then** se muestra la columna "Ciclo Operativo" ubicada inmediatamente después de la columna "Pago Contrato".
2. **Given** un recaudo asociado a una propiedad con grupo operativo 1, **When** el usuario visualiza la fila correspondiente, **Then** la columna Ciclo Operativo muestra "Grupo 1".
3. **Given** un recaudo asociado a una propiedad con grupo operativo 3, **When** el usuario visualiza la fila correspondiente, **Then** la columna Ciclo Operativo muestra "Grupo 3".
4. **Given** que la propiedad BRR BOSQUES DE PINARES MZ 4 CS 144 PI 1 tiene grupo operativo 1, **When** el usuario visualiza el recaudo de dicha propiedad, **Then** la columna Ciclo Operativo muestra "Grupo 1" de forma exacta.

---

### User Story 2 - Comportamiento ante recaudos sin liquidación asociada (Priority: P2)

Como usuario del módulo Recaudos, deseo que la columna Ciclo Operativo maneje correctamente los casos donde un recaudo no tiene una liquidación de propietarios asociada, para mantener la integridad visual de la información.

**Why this priority**: Es un caso edge crítico que afecta la integridad de la información mostrada. Sin este manejo, la UI podría mostrar datos inconsistentes o errores.

**Independent Test**: Puede probarse creando o identificando un recaudo sin liquidación asociada y verificando que la columna muestra un valor apropiado (vacío, guion, o "N/A") sin errores visuales.

**Acceptance Scenarios**:

1. **Given** un recaudo que no tiene liquidación de propietarios asociada, **When** el usuario visualiza la tabla de Recaudos, **Then** la columna Ciclo Operativo muestra un valor indicativo de ausencia de datos (guion o "N/A") sin errores.
2. **Given** un recaudo sin liquidación asociada, **When** el usuario interactúa con la tabla (ordenar, filtrar, paginar), **Then** el comportamiento de la tabla no se ve afectado por la ausencia del ciclo operativo.

---

### User Story 3 - Consistencia del dato en diferentes vistas (Priority: P3)

Como usuario, deseo que el ciclo operativo mostrado en la tabla de Recaudos sea idéntico al registrado en la Liquidación de Propietarios correspondiente, para garantizar que la información sea confiable y coherente.

**Why this priority**: Garantiza la integridad de la información entre módulos, esencial para la confianza del usuario en el sistema.

**Independent Test**: Puede probarse comparando visualmente el ciclo operativo en la tabla de Recaudos con el ciclo operativo de la liquidación de propietarios correspondiente para una propiedad dada.

**Acceptance Scenarios**:

1. **Given** un recaudo con liquidación asociada, **When** el usuario compara el ciclo operativo en la tabla de Recaudos con el de la liquidación correspondiente, **Then** ambos valores son idénticos.
2. **Given** que se actualiza el grupo operativo de un contrato de mandato, **When** el usuario recarga la tabla de Recaudos, **Then** la columna Ciclo Operativo refleja el valor actualizado de forma inmediata.

---

### Edge Cases

- ¿Qué sucede cuando un recaudo tiene múltiples conceptos y solo algunos están asociados a liquidaciones? Se espera que el ciclo operativo provenga de la liquidación del contrato de mandato vinculado a la misma propiedad, no de los conceptos individuales.
- ¿Qué sucede cuando una propiedad tiene contratos de mandato activos con diferentes grupos operativos? El sistema debe seleccionar el contrato con estado "Activo" y fecha de inicio más reciente dentro del periodo del recaudo, y mostrar su grupo operativo.
- ¿Qué sucede cuando el contrato de mandato asociado ha sido eliminado lógicamente (soft delete)? Se debe mostrar un indicador de datos no disponibles.
- ¿Qué sucede con recaudos históricos cuyo contrato de mandato ya no existe? Se debe mostrar un valor de ausencia de datos sin afectar la visualización.

## Requirements

### Functional Requirements

- **FR-001**: La tabla principal del módulo Recaudos DEBE incorporar una nueva columna denominada "Ciclo Operativo".
- **FR-002**: La columna Ciclo Operativo DEBE ubicarse inmediatamente después de la columna "Pago Contrato" en la tabla.
- **FR-003**: El valor mostrado en la columna Ciclo Operativo DEBE provenir exclusivamente del campo `GRUPO_OPERATIVO` de la tabla `CONTRATOS_MANDATOS`, accedido a través de la relación entre el recaudo y la liquidación de propietarios.
- **FR-004**: El sistema DEBE resolver la relación entre Recaudos y Liquidaciones de Propietarios mediante la cadena: Recaudo → Contrato de Arrendamiento → Propiedad → Contrato de Mandato → Grupo Operativo.
- **FR-005**: El valor del ciclo operativo DEBE formatearse como "Grupo N" donde N corresponde al número del grupo operativo (1, 2, 3, 4, 5, etc.).
- **FR-006**: Cuando un recaudo no tenga una liquidación de propietarios asociada, la columna DEBE mostrar un guion ("-") o indicador visual equivalente de ausencia de datos.
- **FR-007**: El ciclo operativo DEBE mantenerse consistente y sincronizado entre la base de datos PostgreSQL, el backend y la interfaz de usuario, sin caché que pueda generar desfase.
- **FR-008**: La incorporación de esta columna NO DEBE afectar el rendimiento de carga de la tabla de Recaudos (tiempo de respuesta percibido).
- **FR-009**: La columna DEBE ser visible tanto en la vista de lista principal como en cualquier exportación de datos del módulo.
- **FR-010**: El ciclo operativo mostrado DEBE corresponder al contrato de mandato vigente para el periodo del recaudo, no a un valor estático o calculado de forma independiente. Cuando existen múltiples contratos de mandato para una propiedad, se debe seleccionar el contrato con estado "Activo" y fecha de inicio más reciente dentro del periodo del recaudo.

### Key Entities

- **Recaudo**: Registro de pago recibido de un arrendatario. Vinculado a un Contrato de Arrendamiento (ID_CONTRATO_A). Contiene un período de referencia a través de sus conceptos (RECAUDO_CONCEPTOS.PERIODO).
- **Liquidación de Propietarios**: Cálculo mensual de lo que se debe pagar al propietario. Vinculada a un Contrato de Mandato (ID_CONTRATO_M). Contiene período (PERIODO), estado, montos desglosados.
- **Contrato de Mandato**: Contrato entre la inmobiliaria y el propietario. Contiene el campo `GRUPO_OPERATIVO` que define el ciclo operativo (Grupo 1, Grupo 2, etc.).
- **Contrato de Arrendamiento**: Contrato entre la inmobiliaria y el arrendatario. Vinculado a una Propiedad.
- **Propiedad**: Entidad central que conecta ambos tipos de contrato. Un Contrato de Arrendamiento y un Contrato de Mandato pueden coexistir para la misma propiedad.
- **Ciclo Operativo**: Valor derivado del campo `GRUPO_OPERATIVO` del Contrato de Mandato. Representa el grupo operativo al que pertenece la propiedad/liquidación. No es una entidad independiente ni un campo almacenado en Recaudos.

## Success Criteria

### Measurable Outcomes

- **SC-001**: La columna Ciclo Operativo aparece correctamente en el 100% de los recaudos que tienen una liquidación de propietarios asociada.
- **SC-002**: El valor mostrado en la columna Ciclo Operativo coincide al 100% con el registrado en la Liquidación de Propietarios correspondiente para todos los recaudos verificados.
- **SC-003**: El tiempo de carga de la tabla de Recaudos no se incrementa más de un 10% con respecto al tiempo base (sin la columna adicional).
- **SC-004**: El caso de validación de la propiedad BRR BOSQUES DE PINARES MZ 4 CS 144 PI 1 muestra "Grupo 1" de forma correcta y consistente.
- **SC-005**: Los recaudos sin liquidación asociada muestran un indicador de ausencia de datos sin errores visuales ni funcionales.
- **SC-006**: No se introducen regresiones funcionales en el módulo Recaudos (filtros, ordenamiento, paginación, CRUD de recaudos operan normalmente).
- **SC-007**: La integridad referencial se mantiene entre PostgreSQL, el backend y la interfaz de usuario para todos los escenarios probados.

## Assumptions

- El campo `GRUPO_OPERATIVO` en la tabla `CONTRATOS_MANDATOS` contiene valores numéricos enteros (1, 2, 3, 4, 5) que representan los grupos operativos del sistema.
- La relación entre Recaudos y Liquidaciones de Propietarios se establece a través de la cadena: Recaudo → Contrato de Arrendamiento → Propiedad → Contrato de Mandato → Grupo Operativo.
- Cada propiedad puede tener múltiples contratos de mandato. Para resolver cuál es "vigente", se selecciona el contrato con estado "Activo" y fecha de inicio más reciente dentro del periodo del recaudo.
- Los valores del ciclo operativo son exclusivamente numéricos (1-5) y se formatean como "Grupo N" para la visualización en la UI.
- La existencia de RECAUDO_CONCEPTOS.PERIODO permite correlacionar el recaudo con la liquidación del mismo periodo para el contrato de mandato correspondiente.
- El módulo de Recaudos ya cuenta con una infraestructura funcional de paginación, filtrado y ordenamiento que debe mantenerse operativa tras el cambio.
- No se requiere crear ni modificar tablas en la base de datos; el campo `GRUPO_OPERATIVO` ya existe en `CONTRATOS_MANDATOS`.
- El cambio es puramente de visualización en la tabla de Recaudos; no se requiere modificar la lógica de negocio de creación, edición o eliminación de recaudos.
