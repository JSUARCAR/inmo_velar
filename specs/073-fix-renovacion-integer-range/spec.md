# Feature Specification: Renovación de contratos — error `integer out of range`

**Feature Branch**: `073-fix-renovacion-integer-range`

**Created**: 2026-09-14

**Status**: Draft

**Input**: User description: "Ingeniería inversa robusta sobre el proceso de renovación de contratos (módulo Contratos). Al renovar el contrato de la propiedad CR 6 CL 03-40 CS 54, CJT LA ALQUERIA el sistema falla con `Error: integer out of range`. Se exige solución de forma (desbloquear esa renovación) y de fondo (corregir la causa raíz estructural), con validación y prevención de regresiones en Contratos, Liquidaciones de Propietarios, Recaudos y módulos dependientes."

## Hallazgo de ingeniería inversa (evidencia verificada, no suposición)

Se trazó el flujo completo de renovación de arrendamiento (modal de renovación → estado de contratos → servicio de arrendamientos → repositorios → base de datos) y se reprodujo el error contra la base de datos real con una consulta de solo lectura:

- El contrato afectado es el **N.º 73** (propiedad N.º 20, canon **$2.300.000**, duración **12 meses**, estado ACTIVO, vigencia 2025-10-05 → 2026-10-05). Al tener duración ≥ 12 meses, la renovación entra por la rama con incremento IPC y, después de actualizar contrato, propiedad y mandato, **propaga el canon nuevo a las liquidaciones futuras**.
- La propagación recalcula la comisión con una operación del tipo `canon × porcentaje_comisión / 10000`. En el contrato afectado eso es `2.300.000 × 1000 = 2.300.000.000`, que **supera el máximo del entero de 32 bits (2.147.483.647)**. La multiplicación se evalúa antes de la división, por lo que la base de datos rechaza la operación con `integer out of range` aunque el resultado final (230.000) cabría sin problema.
- Prueba de control: con un canon de 900.000 la misma operación funciona (900.000 × 1000 = 900.000.000). Esto explica por qué otros contratos sí se renuevan y este no: **no es un defecto de fechas, identificadores ni del IPC, es la magnitud del producto canon × comisión**.
- Toda la renovación corre dentro de una única transacción: al fallar la propagación, **se revierte la renovación completa** (no quedan registros parciales; el contrato 73 sigue ACTIVO sin renovar).
- El canon máximo registrado en arrendamientos es **$10.000.000** y la comisión máxima es **1500**, por lo que el problema es estructural y afectará a más contratos (p. ej. 1.500.000 × 1500 también desborda).
- Rastreo de patrones afines: es el **único cálculo en la ruta de renovación** que multiplica dos enteros antes de dividir. Los demás usos (cálculo en memoria del canon nuevo, actualización de mandato/propiedad, recaudos, auditoría en columna numérica) operan dentro de rango.

## Clarifications

### Session 2026-09-14

- Q: ¿La corrección de fondo incluye migración de tipos de columnas o backfill histórico? → A: No; solo cálculo sin desbordamiento + validación previa, sin cambiar tipos de columnas ni recalcular historia.
- Q: ¿Qué contenido debe tener el mensaje operativo ante un valor fuera de rango? → A: Indica el campo y el valor que excede el rango, sin tecnicismos.
- Q: ¿Qué debe pasar si dos operadores renuevan el mismo contrato a la vez? → A: Solo una renovación persiste; el segundo intento recibe el resultado existente sin duplicar.
- Q: ¿Qué regla de redondeo aplica a la comisión e IVA derivados? → A: Truncar al entero (comportamiento actual).
- Q: ¿Qué debe pasar con datos futuros por encima de los máximos observados? → A: Rechazar con el mensaje operativo (campo + valor, sin tecnicismos).
- Revisión checklist renovacion.md (26 ítems, CHK001–CHK026): refinamientos aplicados a FR-001/002/003/004/005/006, FR-011/012 nuevos (encadenamiento y fecha personalizada), entidades, escenarios US1, SC-001, bordes y supuestos; ver reporte de la sesión.
- Q: ¿Cuál es la gate única de validación (umbral operativo vs límite int4)? → A: Máximos operativos primero (rechazo con mensaje); límite int4 como red de seguridad para todo derivado.
- Revisión checklist limites.md (12 ítems, CHK001–CHK012): todos cumplidos con la gate en dos niveles y los refinamientos previos; sin cambios adicionales al spec.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Renovar el contrato de CS 54, La Alquería (Priority: P1)

El operador abre el contrato asociado a CR 6 CL 03-40 CS 54, CJT LA ALQUERIA, solicita la renovación (con la proyección de IPC mostrada en el modal) y la confirma. La renovación completa sin errores: queda registrada en el historial, el contrato extiende su vigencia con el canon incrementado por IPC, y las liquidaciones y recaudos futuros reflejan el canon nuevo.

**Why this priority**: Es el caso reportado por el cliente y hoy bloquea por completo la operación de ese contrato.

**Independent Test**: Renovar únicamente el contrato N.º 73 y comprobar historial, vigencia, canon, liquidaciones y recaudos futuros.

**Acceptance Scenarios**:

1. **Given** el contrato N.º 73 ACTIVO con canon $2.300.000 y vigencia hasta 2026-10-05, **When** el operador confirma su renovación, **Then** la operación termina sin errores y el historial registra canon anterior $2.300.000 y canon nuevo = $2.300.000 + IPC vigente.
2. **Given** la renovación del contrato N.º 73 confirmada, **When** se consultan sus liquidaciones con fecha igual o posterior al mes de renovación, **Then** todas muestran canon bruto igual al canon nuevo y comisión/IVA truncados al entero según ese canon.
3. **Given** la renovación del contrato N.º 73 confirmada, **When** se consultan sus recaudos con fecha igual o posterior al mes de renovación, **Then** el concepto Canon y el total reflejan el canon nuevo.

---

### User Story 2 - Renovar cualquier contrato sin importar la magnitud del canon (Priority: P2)

Cualquier contrato ACTIVO (arriendo o mandato), incluidos los de canon alto (hasta el máximo real del sistema) y comisiones altas, se renueva sin errores de desbordamiento, hoy y en futuras renovaciones consecutivas.

**Why this priority**: Corrige la causa raíz estructural; sin esto, el mismo error reaparecerá con otros contratos.

**Independent Test**: Renovar contratos de prueba con combinaciones límite (canon 10.000.000 × comisión 1500) y renovaciones consecutivas, verificando que ninguna falla por desbordamiento.

**Acceptance Scenarios**:

1. **Given** un contrato ACTIVO con canon y comisión cuyo producto supera 2.147.483.647, **When** se renueva, **Then** la operación completa sin errores y los valores derivados (comisión, IVA, totales) son aritméticamente correctos.
2. **Given** un contrato ya renovado una vez, **When** se permite y ejecuta una segunda renovación consecutiva, **Then** ambas quedan en el historial con valores encadenados correctos (el canon anterior de la segunda es el canon nuevo de la primera).

---

### User Story 3 - Módulos dependientes consistentes y sin regresiones (Priority: P3)

Después de cada renovación, la información queda consistente en Contratos, Liquidaciones de Propietarios, Recaudos, Propiedades (canon estimado) y Mandato sincronizado, y los procesos existentes de esos módulos siguen funcionando como antes.

**Why this priority**: La renovación escribe en varios módulos; un arreglo local que rompa la consistencia sería peor que el error original.

**Independent Test**: Tras renovar, ejecutar las verificaciones de propagación y las suites de Contratos, Liquidaciones y Recaudos.

**Acceptance Scenarios**:

1. **Given** una renovación completada, **When** se verifica la propagación del canon, **Then** el reporte indica cero inconsistencias en liquidaciones y recaudos futuros.
2. **Given** la corrección aplicada, **When** se ejecuta la suite de pruebas de Contratos, Liquidaciones y Recaudos, **Then** el 100% de las pruebas que pasaban antes siguen pasando.

### Edge Cases

- Producto canon × comisión exactamente en el límite (2.147.483.647) y justo por encima: ambos deben resolverse sin error y con el valor truncado exacto al entero.
- Contrato con duración menor a 12 meses (sin IPC): la renovación no aplica incremento y debe seguir funcionando como antes.
- Sin valor de IPC vigente registrado: la renovación completa con 0% de incremento en lugar de fallar.
- Renovación con fecha de fin personalizada desde el modal: se respeta la fecha indicada y el resto del cálculo no cambia.
- Falla previa ya revertida: reintentar la renovación del contrato 73 no duplica registros de historial (la operación es idempotente).
- Liquidaciones o recaudos futuros inexistentes: la renovación completa igualmente (propagación de cero filas).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El sistema MUST permitir completar la renovación del contrato N.º 73 (CR 6 CL 03-40 CS 54, CJT LA ALQUERIA) sin errores, registrando historial, nueva vigencia y canon con IPC aplicado, donde IPC es el último valor vigente registrado; si la duración es menor a 12 meses o no hay IPC vigente, la renovación aplica 0% de incremento y completa igualmente.
- **FR-002**: El cálculo de todos los valores derivados durante la propagación a liquidaciones (comisión, IVA, totales y neto) MUST producir el valor aritméticamente correcto para cualquier combinación de canon y comisión dentro de los rangos reales del sistema (canon hasta $10.000.000, comisión hasta 1500), sin errores de desbordamiento y truncando los resultados al entero en pesos, sin decimales (regla vigente).
- **FR-003**: El sistema MUST validar, antes de persistir, que cada valor numérico derivado de la renovación cabe en el tipo de su columna destino, y rechazar con un mensaje operativo visible en la misma vista donde se inició la renovación, que indique el campo y el valor que excede el rango, en lenguaje no técnico y nunca un error crudo de base de datos, cualquier caso que lo exceda.
- **FR-004**: La renovación MUST mantener su atomicidad: o persisten juntos historial, contrato, propiedad, mandato, liquidaciones y recaudos, o no persiste ninguno; ante un fallo, el sistema informa que no se aplicó ningún cambio y que es seguro reintentar.
- **FR-005**: La renovación MUST seguir siendo idempotente ante reintentos y ante intentos concurrentes sobre el mismo contrato (un reintento tras el fallo revertido no duplica el historial; dos intentos simultáneos producen un único registro y el segundo recibe el resultado existente); el historial permite comprobar que un intento fallido no dejó registros antes de reintentar.
- **FR-006**: El sistema MUST propagar el canon nuevo a liquidaciones futuras (canon bruto, total de ingresos, comisión, IVA, egresos totales y neto) y a recaudos futuros (concepto Canon y total), solo para registros con fecha igual o posterior al mes de renovación; si no existen registros futuros, la renovación completa igualmente sin errores.
- **FR-007**: El sistema MUST sincronizar el mandato activo de la misma propiedad (canon y fecha de fin) y el canon estimado de la propiedad con el canon nuevo del arriendo.
- **FR-008**: El sistema MUST registrar en auditoría cada liquidación y recaudo cuyo canon cambió efectivamente (solo cambios reales).
- **FR-009**: Tras la corrección, las renovaciones de mandato MUST seguir el mismo estándar de no-desbordamiento y validación que las de arrendamiento.
- **FR-010**: El sistema MUST conservar intacta la información histórica (renovaciones anteriores, liquidaciones y recaudos de meses pasados no se modifican).
- **FR-011**: En renovaciones consecutivas del mismo contrato, el canon anterior de cada renovación MUST igualar el canon nuevo de la inmediata anterior (encadenamiento).
- **FR-012**: Cuando el operador indique una fecha de fin personalizada en el modal, la renovación MUST respetarla y el resto del cálculo no cambia.

### Key Entities *(include if feature involves data)*

- **Contrato de arrendamiento**: Contrato sobre un inmueble (canon, duración en meses, fechas de vigencia, estado). El caso índice es el N.º 73 de La Alquería CS 54.
- **Renovación de contrato**: Registro histórico de cada prórroga (vigencias original y renovada, canon anterior/nuevo, porcentaje de incremento almacenado en base 100 —p. ej. 5.2% → 520—, motivo, fecha).
- **Liquidación de propietario**: Cuenta periódica por propiedad (canon bruto, comisión e IVA derivados del canon, ingresos/egresos, neto a pagar). Las futuras se recalculan con el canon nuevo.
- **Recaudo**: Cobro asociado al contrato de arriendo (conceptos incluido Canon, total). Los futuros se actualizan con el canon nuevo.
- **Mandato y propiedad**: El mandato activo de la misma propiedad y el canon estimado de la propiedad se sincronizan con el canon renovado.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: El operador completa la renovación del contrato de CS 54, La Alquería en un solo intento, sin errores, y el historial muestra el canon nuevo correcto según el IPC vigente (verificable contra el historial y la tabla IPC).
- **SC-002**: El 100% de los contratos activos probados (incluidos los de canon hasta $10.000.000 con comisión hasta 1500) se renuevan sin errores de desbordamiento.
- **SC-003**: Después de cada renovación probada, el 100% de las liquidaciones y recaudos futuros del contrato muestran el canon nuevo, y el reporte de propagación indica cero inconsistencias.
- **SC-004**: El 100% de las pruebas existentes de Contratos, Liquidaciones y Recaudos que pasaban antes del cambio siguen pasando después.
- **SC-005**: Transcurridos 30 días de operación, cero reportes nuevos de `integer out of range` en renovaciones.

## Assumptions

- La renovación fallida del contrato 73 fue revertida por completo por la transacción; el contrato sigue ACTIVO sin renovar y es seguro reintentar tras la corrección.
- Gate de validación en dos niveles (sesión 2026-09-14): primero máximos operativos (canon ≤ $10.000.000, comisión ≤ 1500; por encima se rechazan con el mensaje operativo de FR-003 y su soporte requeriría una iniciativa separada); segundo, límite int4 (2.147.483.647) como red de seguridad para todo valor derivado.
- La escala vigente es comisión en base 10000 (1000 = 10%) e IPC en porcentaje directo (5.2 = 5.2%); no se cambia ninguna regla de negocio, solo la capacidad del cálculo.
- La tabla de IPC vuelve a tener valores vigentes; si estuviera vacía, la renovación aplica 0% (comportamiento actual ya contemplado).
- Las suites de pruebas de Contratos, Liquidaciones y Recaudos existen y están en verde antes del cambio (criterio de entrada verificado en T001 de tasks.md).
- Fuera de alcance: migración de tipos de columnas en base de datos y recálculo (backfill) de liquidaciones históricas; la corrección se limita a cálculo sin desbordamiento + validación previa (sesión 2026-09-14).
- Sin objetivos de latencia estrictos: la propagación está acotada a los registros futuros de un único contrato, por lo que no se definen requisitos de rendimiento (exclusión explícita y acotada).
