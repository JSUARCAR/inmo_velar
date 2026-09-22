# Feature Specification: Grupo de pago correcto y atómico en la renovación de contratos

**Feature Branch**: `075-fix-grupo-pago-renovacion`

**Created**: 2026-09-21

**Status**: Draft

**Input**: User description: "Ingeniería inversa robusta, profunda y exhaustiva sobre el proceso de renovación de contratos del módulo de Contratos. El cliente reporta nuevamente que al renovar un contrato el grupo de pago correspondiente no se actualiza de forma atómica, con riesgo de que el contrato quede asociado a un grupo que no corresponde con su fecha efectiva de renovación. Se requiere causa raíz, auditoría integral de todos los contratos activos, solución de forma y de fondo, pruebas de regresión y eliminación total de datos de TEST."

## Hallazgo de ingeniería inversa (evidencia verificada en código)

Se trazó el flujo completo de renovación (modal/estado → servicio de arrendamiento → servicio de mandato → repositorios PostgreSQL → base de datos) y se identificaron **tres causas concurrentes**, todas verificadas sobre el código vigente:

1. **La renovación nunca recalcula el grupo de pago ni el día de pago.**
   - `ServicioContratoArrendamiento._ejecutar_renovacion_arrendamiento` (`src/aplicacion/servicios/servicio_contrato_arrendamiento.py:432-527`) actualiza fecha de fin, canon, historial, propiedad, mandato (solo canon y fecha de fin), liquidaciones y recaudos, pero **no toca `grupo_operativo` ni `fecha_pago`** del contrato ni del mandato sincronizado. El período renovado inicia en `fecha_inicio_renovacion = fecha_fin_original + 1 día` (`CalculadoraContratos.calcular_fecha_inicio_renovacion`, `src/dominio/servicios/calculadora_contratos.py:216`), pero el grupo/día de pago almacenados siguen reflejando el inicio del período original.
   - `ServicioContratoMandato.renovar_mandato` (`src/aplicacion/servicios/servicio_contrato_mandato.py:252-317`) extiende la fecha de fin y registra historial, pero tampoco recalcula `grupo_operativo`/`fecha_pago`. En cambio, la **edición** sí lo hace: `actualizar_mandato` recalcula grupo y día cuando cambia `fecha_inicio` (`servicio_contrato_mandato.py:164-174`) y la cascada de `actualizar_arrendamiento` también (`servicio_contrato_arrendamiento.py:294-308`).

2. **La persistencia del arrendamiento pierde el grupo al leer la entidad.**
   - `RepositorioContratoArrendamientoPostgres._row_to_entity` (`src/infraestructura/persistencia/repositorio_contrato_arrendamiento_postgres.py:442-521`) no mapea la columna `GRUPO_OPERATIVO`, por lo que la entidad se materializa con el valor por defecto `0` (`ContratoArrendamiento.grupo_operativo`, `src/dominio/entidades/contrato_arrendamiento.py:39`).
   - Como `actualizar()` escribe `GRUPO_OPERATIVO = contrato.grupo_operativo` (`repositorio_contrato_arrendamiento_postgres.py:396,420`), **cada renovación (y cualquier edición) de un arrendamiento sobrescribe el grupo almacenado con `0`**, dejando el contrato asociado a un grupo inexistente respecto de su período vigente.

3. **La solución anterior (feature 067) cubrió creación, edición y una migración puntual, pero no la ruta de renovación.**
   - La migración `scripts/migrar_ciclo_operativo_v3.py` y `migraciones/run_migration_grupos_pago_v2.py` recalibraron datos existentes; `actualizar_mandato`/`actualizar_arrendamiento` recalculan en edición. La ruta `renovar_arrendamiento`/`renovar_mandato` quedó fuera → **implementación parcial** que explica la reaparición del defecto reportado.
   - Adicionalmente existe **contradicción de reglas por ruta** para arrendamientos: creación usa tramos propios `día ≤ 10 → G1, ≤ 20 → G2, resto → G3` (`servicio_contrato_arrendamiento.py:107-114`), mientras que edición usa la regla V2 de mandato (`calcular_ciclo_pago_mandato`, `servicio_contrato_arrendamiento.py:218-222`).

**Conclusión**: la actualización del grupo de pago no forma parte de la operación de renovación; no se calcula en el momento correcto, no se persiste de forma fiel y no queda cubierta por una regla única y determinística.

## Clarifications

### Session 2026-09-21

- Q: ¿Cuál es la fecha base para determinar el grupo/día de pago tras una renovación? → A: La fecha efectiva del período vigente: inicio del período renovado (`fecha_fin_original + 1 día`, registrado como `fecha_inicio_renovacion` de la renovación más reciente); para contratos sin renovaciones, la fecha de inicio original del contrato.
- Q: ¿La auditoría y remediación de grupo de pago aplica también a arrendamientos o solo a mandatos? → A: Aplica a **mandatos y arrendamientos** activos; cubre la totalidad de contratos activos exigida por el cliente.
- Q: Para arrendamientos, ¿qué regla de grupo rige: la de creación (tramos por día de pago) o la V2 de mandatos usada en edición? → A: Rige la **regla de tramos V2** (28-7 → G1, 8-17 → G2, 18-27 → G3) calculada sobre la fecha efectiva del período, con **día de pago = día exacto** de esa fecha (regla propia de arrendamiento). La regla de creación por tramos queda unificada a V2.
- Q: Al renovar un arrendamiento, ¿el mandato activo adopta el período renovado o conserva su propio cálculo? → A: El mandato activo **adopta el período renovado del arrendamiento como su fecha efectiva** y recalcula `grupo_operativo` y `fecha_pago` con la regla de mandato (28-7 → G1 paga 10; 8-17 → G2 paga 20; 18-27 → G3 paga 30) sobre esa misma fecha, quedando consistente con el arrendamiento.
- Q: ¿Cómo se determina la "renovación más reciente" para la fecha efectiva del período vigente cuando hay varias renovaciones o historial incompleto? → A: La renovación con mayor fecha de ejecución (`fecha_renovacion`) descendente y, en empate, mayor ID. Si no existe historial propio: un **mandato** cuya propiedad tiene un arrendamiento ACTIVO con renovaciones **hereda la fecha efectiva de la renovación más reciente de ese arrendamiento** (coherente con FR-005); en cualquier otro caso, la fecha de inicio original del contrato (aunque `fecha_renovacion_contrato` esté registrada).
- Q: ¿Cómo debe ejecutarse la auditoría y remediación de los contratos activos con grupo incorrecto? → A: Auditoría en **solo lectura** (reporte antes/después sin modificar datos) y remediación mediante **script con bandera `--commit` explícita** en una única transacción; sin ejecución automática durante el despliegue, siguiendo el precedente de la feature 067 y `migrar_ciclo_operativo_v3.py`.
- Q: Cuando una renovación falla y se revierte por completo, ¿qué debe observar el usuario? → A: Un **mensaje operativo** en la misma vista donde inició la renovación: "no se aplicó ningún cambio y es seguro reintentar", en lenguaje no técnico (precedente feature 073 FR-004), sin exponer el error crudo del motor.
- Q: ¿Cómo se cuantifica la ventana de idempotencia de la renovación? → A: Clave de idempotencia **persistente con TTL de 24 horas** (mecanismo de las features 072/073): el reintento dentro de la ventana devuelve el resultado existente sin duplicar; pasado el TTL, un nuevo intento se evalúa como renovación nueva.
- Q: Si la invalidación de caché falla después del commit exitoso de la renovación, ¿qué debe ocurrir? → A: Se **tolera el fallo**: la invalidación no bloquea, no retrasa ni revierte la transacción ya confirmada; se registra advertencia y se acepta dato obsoleto temporal en UI (consistencia eventual), conforme al precedente de la feature 072 FR-012.
- Q: ¿Cómo debe garantizar la remediación que una renovación concurrente no sea sobrescrita con el grupo del período anterior? → A: **Actualización condicionada a los valores leídos (compare-and-set) + reporte**: cada `UPDATE` se condiciona a que los valores leídos sigan vigentes; si la fila cambió durante la remediación, se omite y se reporta como modificada, sin bloquear la operación normal.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Renovación con grupo de pago correcto para el período vigente (Priority: P1)

Como administrador, al renovar un contrato (arrendamiento o mandato) el sistema debe asignar el grupo de pago y el día de pago que corresponden a la fecha efectiva del nuevo período contractual, de modo que el contrato nunca quede asociado a un grupo del período anterior.

**Why this priority**: Es el defecto reportado por el cliente y afecta la operación financiera (ciclos de liquidación y cobro) de cada contrato renovado.

**Independent Test**: Renovar un contrato activo y verificar que su grupo y día de pago coinciden con la regla de negocio aplicada a la fecha efectiva del período renovado, en el contrato y en el mandato sincronizado.

**Acceptance Scenarios**:

1. **Given** un contrato activo con grupo correspondiente a su período actual, **When** se renueva con una fecha efectiva que cambia de tramo de grupo, **Then** el grupo y el día de pago se recalculan y persisten con los valores del nuevo período.
2. **Given** un contrato en el que el nuevo período cae en el mismo tramo de grupo, **When** se renueva, **Then** el grupo se mantiene correcto, sin degradarse ni quedar en cero.
3. **Given** una renovación de arrendamiento, **When** finaliza, **Then** el mandato activo de la misma propiedad adopta la fecha efectiva del período renovado, queda en el mismo tramo de grupo que el arrendamiento y con su día de pago de mandato (10/20/30) correcto, sin desincronización.
4. **Given** un contrato renovado, **When** se consulta desde la UI y desde los módulos que dependen del grupo, **Then** todos muestran el grupo y día de pago correctos y consistentes entre sí.

---

### User Story 2 - Auditoría y remediación integral de contratos activos (Priority: P1)

Como administrador, necesito que todos los contratos activos —no solo los renovados recientemente— sean auditados contra la regla de negocio vigente y que las inconsistencias históricas detectadas sean corregidas atómicamente, para asegurar que cada contrato tenga el grupo de pago que realmente le corresponde.

**Why this priority**: El cliente exige validar la totalidad de contratos activos; hay inconsistencias históricas acumuladas por migraciones, reglas antiguas y el defecto de renovación.

**Independent Test**: Ejecutar la auditoría sobre todos los contratos activos y comprobar que el reporte final muestra cero discrepancias entre la fecha efectiva, el grupo y el día de pago; verificar contratos corregidos antes/después.

**Acceptance Scenarios**:

1. **Given** la totalidad de contratos activos en base de datos, **When** se ejecuta la auditoría, **Then** se genera un reporte con cada contrato inconsistente (identificador, fecha base, grupo actual, día de pago actual, grupo esperado, día esperado).
2. **Given** el reporte de contratos inconsistentes, **When** se aplica la remediación, **Then** los contratos activos quedan alineados con la regla vigente en una única operación transaccional.
3. **Given** contratos finalizados o cancelados, **When** se ejecuta la auditoría/remediación, **Then** su información histórica permanece intacta.
4. **Given** contratos con renovaciones previas, **When** se auditan, **Then** la fecha base usada es la del período vigente (renovación más reciente), no la del primer período.

---

### User Story 3 - Atomicidad y rollback en la renovación (Priority: P2)

Como administrador, si cualquier paso de la renovación falla, el sistema no debe dejar el contrato parcialmente actualizado: o se confirman todos los cambios (incluido el grupo de pago) o no se confirma ninguno.

**Why this priority**: El reporte exige atomicidad; un contrato con fechas nuevas y grupo viejo (o en cero) es un estado corrupto para la operación.

**Independent Test**: Inducir un fallo controlado en un paso posterior al cálculo del grupo, verificar rollback total (sin cambios parciales) y reintentar con éxito sin duplicados.

**Acceptance Scenarios**:

1. **Given** una renovación en curso, **When** falla cualquier paso antes del commit, **Then** contrato, mandato, propiedad, liquidaciones, recaudos, historial y grupo de pago permanecen exactamente como estaban.
2. **Given** una renovación fallida y revertida, **When** se reintenta, **Then** se completa exitosamente sin duplicar historial ni dejar registros intermedios.
3. **Given** dos intentos concurrentes sobre el mismo contrato, **When** ambos se ejecutan, **Then** solo uno persiste y el resultado final es consistente.

---

### User Story 4 - Sin regresiones en módulos dependientes del grupo (Priority: P3)

Como administrador, después de la corrección, los módulos que consumen el grupo de pago (Contratos, Liquidaciones de Propietarios, Recaudos y sus filtros por ciclo operativo) siguen funcionando igual o mejor, sin nuevos defectos.

**Why this priority**: El grupo es transversal a la operación; una corrección local que rompa los consumidores sería peor que el defecto original.

**Independent Test**: Ejecutar las suites de pruebas de los módulos afectados y las validaciones funcionales de filtros por ciclo/día de pago antes/después del cambio.

**Acceptance Scenarios**:

1. **Given** la corrección aplicada, **When** se ejecutan las pruebas existentes de Contratos, Liquidaciones y Recaudos, **Then** el 100% de las pruebas que pasaban antes sigue pasando.
2. **Given** una renovación completada, **When** se filtran liquidaciones y recaudos por ciclo operativo y día de pago, **Then** los registros aparecen bajo el grupo correcto del contrato.

### Edge Cases

- Fecha efectiva en cambio de año (31-dic → 01-ene): el grupo/día de pago deben recalcularse con la fecha del nuevo período, sin errores de fecha. Resultado esperado por regla V2: día 1 → Grupo 1 (mandato paga 10; arrendamiento paga 1).
- Fecha efectiva a fin de febrero en año bisiesto (28-feb → 29-feb) y truncamientos de fin de mes. Resultado esperado por regla V2: día 28 y día 29 → Grupo 1 (mandato paga 10; arrendamiento paga 28/29 respectivamente).
- Renovaciones consecutivas: la base de cálculo es siempre la fecha efectiva del período vigente (última renovación), con encadenamiento correcto.
- Contrato renovado antes de esta corrección: debe quedar auditado y remediado aunque su historial de renovación no refleje el grupo actual.
- Contrato sin renovaciones propias: la fecha base es su fecha de inicio original, salvo el mandato que hereda el período del arrendamiento activo renovado (caso siguiente).
- Contrato con `fecha_renovacion_contrato` registrada pero sin historial de renovaciones: la fecha base es su fecha de inicio original, pues el historial es la única fuente del período vigente.
- Mandato sin renovaciones propias cuya propiedad tiene un arrendamiento ACTIVO con renovaciones: hereda la fecha efectiva de la renovación más reciente del arrendamiento, de modo que el resultado de runtime (FR-005) y la auditoría coinciden.
- Arrendamiento sin mandato activo asociado: la renovación completa igualmente y el contrato conserva el grupo correcto de su propio período.
- Grupo o día de pago vacíos/cero/corruptos en un contrato activo: se considera discrepancia cualquier valor almacenado distinto del esperado (incluye 0, vacío, no numérico o fuera de {1,2,3}); deben ser detectados por la auditoría y corregidos con la regla vigente.
- Contratos finalizados o cancelados: no se auditan ni se modifican.
- Fallo durante la remediación masiva: rollback total, sin correcciones parciales.
- Fallo durante una renovación: el usuario recibe el mensaje operativo "no se aplicó ningún cambio; es seguro reintentar", sin error crudo del motor.
- Fallo de invalidación de caché posterior al commit: no revierte ni bloquea la renovación; se tolera dato obsoleto temporal (consistencia eventual).
- Renovación concurrente durante la remediación: la fila afectada se omite y se reporta como modificada durante la remediación; nunca se sobrescribe con el grupo del período anterior.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El sistema MUST determinar `grupo_operativo` y `fecha_pago` con una única fuente de verdad de dominio a partir de la **fecha efectiva del período contractual vigente**: si el contrato tiene renovaciones, el `fecha_inicio_renovacion` de la renovación más reciente (mayor `fecha_renovacion`, desempate por mayor ID); si no existe historial de renovaciones: un mandato cuya propiedad tenga un arrendamiento ACTIVO con renovaciones hereda el `fecha_inicio_renovacion` de la renovación más reciente de ese arrendamiento (la misma fecha adoptada en FR-005); en cualquier otro caso, su fecha de inicio original. Esta regla aplica a arrendamientos y mandatos.
- **FR-002**: Para mandatos, la regla de grupos MUST ser la vigente V2: inicios del 28 al 7 → Grupo 1 (paga 10); del 8 al 17 → Grupo 2 (paga 20); del 18 al 27 → Grupo 3 (paga 30).
- **FR-003**: Para arrendamientos, el día de pago MUST ser el día exacto de la fecha efectiva del período vigente, y su grupo MUST regirse por la misma regla de tramos V2 aplicada al día de esa fecha (28-7 → G1, 8-17 → G2, 18-27 → G3), unificando la regla de creación con la de edición.
- **FR-004**: Al renovar un contrato, el sistema MUST recalcular y persistir `grupo_operativo` y `fecha_pago` con los valores del nuevo período como parte de **la misma operación** que actualiza fechas, canon, historial, propiedad, mandato, liquidaciones y recaudos.
- **FR-005**: La renovación de un arrendamiento MUST sincronizar en el mandato activo de la misma propiedad las fechas del período renovado y MUST recalcular y persistir su `grupo_operativo` y `fecha_pago` con la regla de mandato (FR-002) sobre la fecha efectiva del período renovado, adoptándola como base. El mandato activo MUST quedar consistente con el arrendamiento renovado (misma fecha efectiva), sin degradar ni desincronizar sus valores.
- **FR-006**: La renovación de un mandato MUST cumplir la regla común de FR-004 (recálculo y persistencia de `grupo_operativo` y `fecha_pago` en la misma operación transaccional), aplicada a la fecha efectiva del período renovado.
- **FR-007**: Ninguna operación de lectura/escritura de contratos MUST perder, sobrescribir con cero o deteriorar el grupo de pago almacenado; el valor persistido MUST ser siempre el calculado por la regla vigente.
- **FR-008**: Toda la renovación (incluida la actualización del grupo de pago) MUST ejecutarse en una única transacción: ante el fallo de cualquier paso, rollback completo sin estados parciales y mensaje operativo en la vista de origen ("no se aplicó ningún cambio; es seguro reintentar", sin errores crudos del motor). Un reintento dentro de la ventana de idempotencia (clave persistente con TTL de 24 horas) MUST devolver el resultado existente sin duplicar historial ni registros intermedios; dos intentos concurrentes MUST producir una única renovación.
- **FR-009**: El sistema MUST auditar en **modo solo lectura** (sin modificar datos) la totalidad de contratos activos (tanto de mandato como de arrendamiento) comparando la fecha efectiva del período vigente contra `grupo_operativo` y `fecha_pago` almacenados con las reglas FR-001 a FR-003, y producir un reporte de discrepancias con: identificador del contrato y su tipo, fecha base usada, grupo actual, día de pago actual, grupo esperado, día de pago esperado.
- **FR-010**: El sistema MUST poder remediar atómicamente todos los contratos activos con discrepancia detectada mediante un script con bandera `--commit` explícita (por defecto modo solo-lectura) que ejecute todos los cambios en una única transacción, alineándolos con la regla vigente, sin modificar contratos finalizados ni cancelados ni alterar historial financiero pasado, y sin ejecutarse automáticamente durante el despliegue. Cada actualización MUST condicionarse a que los valores leídos sigan vigentes (actualización condicionada, compare-and-set): si una fila cambió durante la remediación (p. ej. por una renovación concurrente), MUST omitirse y reportarse como modificada, sin sobrescribir el valor recalculado.
- **FR-011**: Después de una renovación o de la remediación, los módulos dependientes del grupo (Contratos, Liquidaciones de Propietarios, Recaudos y sus filtros por ciclo operativo/día de pago) MUST reflejar el grupo y día de pago correctos de cada contrato.
- **FR-012**: La corrección MUST preservar los comportamientos actuales que ya funcionan (cálculo de fechas, IPC, propagación de canon, idempotencia) sin nuevas regresiones. La invalidación de caché posterior al commit exitoso de la renovación MUST ejecutarse sin bloquear ni revertir la transacción: si falla, se registra advertencia y se tolera consistencia eventual en la UI (precedente feature 072 FR-012).
- **FR-013**: Todo dato creado exclusivamente para pruebas (contratos, propiedades, liquidaciones, recaudos, renovaciones o relaciones derivadas de TEST) MUST eliminarse por completo al finalizar la validación, dejando constancia de la verificación de ausencia de registros huérfanos.

### Key Entities *(include if feature involves data)*

- **Contrato (arrendamiento/mandato)**: Acuerdo con fechas de vigencia, canon y los atributos de operación `grupo_operativo` y `fecha_pago`, que deben corresponder a la fecha efectiva de su período vigente.
- **Renovación de contrato**: Registro histórico de cada prórroga; su `fecha_inicio_renovacion` define el inicio del período renovado y es la fecha base para el grupo/día de pago del nuevo período.
- **Mandato (contrato de mandato)**: Contrato del propietario que comparte propiedad con el arrendamiento y cuyo grupo de pago es la fuente del ciclo operativo en Liquidaciones y Recaudos.
- **Liquidación de propietarios / Recaudo**: Registros financieros cuyo ciclo operativo y día de pago dependen del mandato asociado.
- **Reporte de auditoría de grupos de pago**: Resultado de la comparación entre la fecha efectiva del período vigente y los atributos de pago almacenados, con el detalle de discrepancias y su corrección.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: El 100% de las renovaciones ejecutadas (arrendamiento y mandato, en todos los escenarios de fecha) termina con `grupo_operativo` y `fecha_pago` correspondientes a la fecha efectiva del período renovado, verificado contra la regla de negocio vigente.
- **SC-002**: La auditoría sobre la totalidad de contratos activos reporta **cero discrepancias** entre fecha efectiva, grupo y día de pago después de la remediación y de resolver las filas omitidas por concurrencia (documenta el 100% de las corregidas con sus valores antes/después, incluidas las omitidas reportadas).
- **SC-003**: Ante un fallo inducido en cualquier paso de la renovación, el sistema revierte el 100% de los cambios (incluido el grupo de pago) y al reintentar completa exitosamente sin duplicados.
- **SC-004**: Cero (0) regresiones: el 100% de las pruebas existentes de Contratos, Liquidaciones y Recaudos que pasaban antes de la corrección siguen pasando después.
- **SC-005**: El 100% de los datos de TEST creados para la validación es eliminado, y la verificación final confirma ausencia de contratos, propiedades, liquidaciones, recaudos y relaciones huérfanas de prueba.
- **SC-006**: Transcurridos 30 días de operación, cero reportes nuevos de contratos renovados con grupo de pago incorrecto o en cero (seguimiento operativo del responsable de release; ver quickstart §7).

## Assumptions

- Se asume que la fecha efectiva del período vigente es el inicio del período renovado (`fecha_fin_original + 1 día`) registrado en la renovación más reciente —mayor `fecha_renovacion`, desempate por mayor ID—; para contratos sin historial de renovaciones, la fecha de inicio original del contrato, salvo el mandato que hereda el período del arrendamiento activo renovado de la misma propiedad (FR-001/FR-005, ratificado en la sesión de clarificación 2026-09-21).
- La regla V2 (28-7 → G1/10, 8-17 → G2/20, 18-27 → G3/30) es la fuente oficial para contratos de mandato, conforme a la feature 067; para arrendamientos rige la misma regla de tramos V2 sobre la fecha efectiva, con día de pago exacto (sesión 2026-09-21).
- La auditoría y remediación cubren mandatos y arrendamientos en estado ACTIVO (sesión 2026-09-21).
- En la renovación de un arrendamiento, el mandato activo de la propiedad comparte la fecha efectiva del período renovado y con ella se recalcula su grupo/día de pago con la regla de mandato; no conserva una base independiente mientras el arriendo esté renovado (sesión 2026-09-21).
- La auditoría/remediación se ejecuta por un operador autorizado mediante script: primero en modo solo-lectura para revisar el reporte de discrepancias y luego con `--commit`; no hay remediación automática en el despliegue (sesión 2026-09-21).
- La idempotencia de la renovación se respalda en el almacén persistente de claves del sistema (tabla de idempotencia con TTL de 24 horas, mecanismo vigente de las features 072/073), garantizando el comportamiento entre sesiones e instancias (sesión 2026-09-21).
- PostgreSQL es el único motor de base de datos; no se requiere compatibilidad con SQLite (constitución §1).
- La auditoría y remediación aplican exclusivamente a contratos en estado ACTIVO; los contratos finalizados/cancelados se preservan inmutables (criterio ratificado en la feature 067 y reiterado por el cliente).
- El grupo de pago de Liquidaciones y Recaudos se obtiene del contrato de mandato activo asociado a la propiedad; no se almacena por separado en esos registros.
- No se modifican tipos de columna ni esquemas de base de datos; la corrección es de lógica de cálculo, persistencia fiel y consistencia transaccional.
- La corrección debe funcionar hacia adelante (nuevas renovaciones) y hacia atrás (remediación de activos existentes), sin recálculo de historia financiera cerrada.
- Existen suites de pruebas de Contratos, Liquidaciones y Recaudos en verde antes del cambio (criterio de entrada).
- Los datos de TEST son creados de forma controlada y eliminados por completo al finalizar; la constancia de limpieza queda en el reporte de validación.
- Fuera de alcance: cambiar la regla de negocio de grupos vigente, recalcular liquidaciones o recaudos ya cerrados, y optimizaciones de rendimiento no vinculadas a la atomicidad.
