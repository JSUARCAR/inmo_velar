# Feature Specification: renovacion-contratos-debug

**Feature Branch**: `072-renovacion-contratos-debug` (working tree local; rama por crear en push)

**Created**: 2026-09-13

**Status**: Draft

**Input**: User description: "/speckit-specify Quiero que realices un proceso de ingeniería inversa robusta..."

## Clarifications

### Session 2026-09-13
- Q: Do you have the exact error message, traceback, or a description of the UI behavior when the failure occurs, or should the investigation start blindly by reproducing the flow? → A: No exact message; please find it by analyzing the code and reproducing the issue.
- Q: ¿La renovación debe propagar automáticamente el nuevo canon a liquidaciones y recaudos futuros, o solo aplicar a registros generados después? → A: Propagación automática a registros futuros (fecha >= mes de renovación), usando `NULLIF(campo, '')::date` para proteger contra fechas vacías en PostgreSQL.
- Q: ¿Cómo se calcula `fecha_inicio_renovacion` en el registro de historial de renovaciones? → A: `fecha_fin_original + 1 día`. El nuevo período empieza el día posterior al vencimiento original, sin solapamiento ni vacío.
- Q: ¿Qué debe ocurrir si la propagación de canon a recaudos/liquidaciones falla después de actualizar el contrato principal? → A: Transacción atómica única: si cualquier paso falla (contrato, log, propagación, sincronización mandato), se hace rollback completo de toda la operación.
- Q: ¿Cuál es la regla de incremento de canon (IPC) en la renovación y qué ocurre si la duración es < 12 meses o no hay valor IPC registrado? → A: Aplicar IPC solo si `duracion_contrato_a >= 12` meses con el valor IPC vigente; si la duración es menor a 12 meses o no existe valor IPC registrado, el canon no cambia (incremento 0%).
- Q: ¿Qué alcance tienen las "condiciones económicas actualizadas" más allá del canon? → A: A nivel de contrato/propiedad/mandato solo cambia el canon; comisión, IVA, totales y neto a pagar se recalculan automáticamente como campos derivados del nuevo canon en `LIQUIDACIONES` y `RECAUDOS` futuros (no son campos editables del contrato).
- Q: ¿Se deben introducir excepciones de dominio tipadas en el flujo de renovación (en lugar de `ValueError` genérico)? → A: Sí, introducir excepción tipada de dominio (p. ej. `ContratoNoRenovableError`) reemplazando los `ValueError` del flujo de renovación, conforme a la constitución §2.2.
- Q: ¿Qué set de prueba mínimo verifica objetivamente SC-001 ("100% de intentos de renovación se completan exitosamente")? → A: 7 casos: ≥12mo con IPC · <12mo sin IPC · sin valor IPC registrado (0%) · renovación consecutiva · fechas límite (31-Dic y 28-Feb bisiesto) · sin recaudos/liquidaciones futuras · sin mandato activo.
- Q: ¿Qué tests de regresión verifican SC-003 ("cero regresiones en Liquidaciones, Recaudos y Creación/Edición")? → A: Ejecutar el 100% de la suite de tests existente de Liquidaciones, Recaudos y Creación/Edición de Contratos exigiendo verde (0 fallos).
- Q: ¿Debe el spec definir un requisito de invalidación de caché de canon tras la renovación? → A: Sí. Tras un commit exitoso se invalida la caché de canon (claves en `cache_estado_cartera`); la invalidación NO bloquea la transacción; si falla, se tolera data obsoleta temporal (consistencia eventual).
- Q: Si un contrato tiene múltiples mandatos activos, ¿cuál se sincroniza durante la renovación? → A: Se sincroniza el mandato activo más reciente (mayor `id_contrato_m`); si hay varios activos se toma el primero sin error.
- Q: ¿La corrección de cast seguro (NULLIF) aplica también a las consultas de verificación de integridad heredadas del feature 063 (Q5/Q6)? → A: Sí. Las 6 queries del contrato 063 (actualización Q1/Q2, consulta Q3/Q4 y verificación Q5/Q6) se alinean al cast seguro `NULLIF(campo,'')::date >= date_trunc('month', ...)`.
- Q: ¿Debe el spec añadir un criterio de aceptación explícito y medible para la atomicidad (ausencia de estado parcial tras un fallo inducido)? → A: Sí. Se amplía SC-001: tras inducir un fallo en cualquier paso de la renovación, la BD queda sin estado parcial (rollback completo) y al reintentar se completa exitosamente sin duplicados.
- Q: En el caso de incremento 0% (`canon_nuevo == canon_anterior`) o de 0 filas futuras a propagar, ¿qué se registra en la auditoría? → A: La auditoría registra SOLO filas realmente modificadas (valor cambiado); con incremento 0% o 0 filas futuras NO se insertan registros en `AUDITORIA_PROPAGACION_CANON`.
- Q: Retos de checklist CHK031/CHK032 (dependencia del almacén de `@idempotent` y validación de deadlocks de una transacción única), resueltos por análisis de código sin pregunta: → A: `@idempotent` se respalda en la tabla PostgreSQL `IDEMPOTENCY_KEYS` vía `DatabaseIdempotencyStrategy`/`IRepositorioIdempotencia` (idempotencia entre sesiones e instancias), documentado en Assumptions; el supuesto de single-transaction sin deadlocks se valida con un test de concurrencia en la fase de implementación.
- Q: (validación checklist coherencia) ¿Qué es exactamente el "valor IPC vigente" de FR-002? → A: El registro IPC de mayor `ANIO` vía `IRepositorioIPC.obtener_ultimo()` (implementación `repositorio_ipc_postgres.py`: `SELECT * FROM IPC ORDER BY ANIO DESC LIMIT 1`); `valor_ipc` es porcentaje flotante (ej. `5.5` = 5.5%). Si no existe ningún registro IPC → no aplica IPC (incremento 0%).
- Q: (validación checklist coherencia) ¿FR-004/SC-004 (PDF post-renovación) requiere implementación nueva en esta feature? → A: No. La regeneración del PDF se gestiona en la capa de presentación (`pdf_state.py`, que instancia `ServicioContratos` con `RepositorioRenovacion`/`RepositorioIPC` y completa los datos del documento); esta feature entrega los datos corregidos (fechas/canon) y SC-004 se reduce a VERIFICACIÓN de que el PDF generado refleja el canon nuevo y las fechas corregidas. Pendiente solo trazar el test de verificación en `tasks.md`.
- Q: (validación checklist coherencia) ¿FR-010 (`canon_arrendamiento_estimado`) requiere código nuevo? → A: No. Ya se actualiza en ambos flujos existentes: `servicio_contrato_arrendamiento.py:468` (nuevo_canon) y `servicio_contrato_mandato.py:291` (canon_mandato). La feature debe cubrirlo con pruebas de verificación (E-escenario) y trazar el task correspondiente.
- Q: (validación checklist coherencia) ¿FR-005 (validación de rangos de fechas) exige nueva lógica? → A: No; se garantiza por construcción: `fecha_inicio_renovacion = fecha_fin_original + 1 día` y `fecha_fin_renovacion` vía `sumar_meses()`, sin solapamiento posible; FR-005 se conserva como guard tipado/estado del contrato (FR-008) sin lógica adicional en esta feature.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Renovación Normal de Contrato (Priority: P1)

Como administrador del sistema, quiero poder renovar un contrato que está próximo a vencerse para extender su vigencia y actualizar sus condiciones económicas sin que el sistema presente errores.

**Why this priority**: Es el flujo principal (Happy Path) reportado como fallido por el cliente. Es crítico para la continuidad del negocio.

**Independent Test**: Can be fully tested by selecting an active, soon-to-expire contract, triggering the renewal process, and verifying the new dates and canon in the database and UI.

**Acceptance Scenarios**:

1. **Given** un contrato activo próximo a vencer, **When** el usuario ejecuta la acción de renovar, **Then** el sistema actualiza correctamente la fecha de inicio, la fecha de vencimiento y el nuevo período contractual.
2. **Given** un contrato renovado, **When** se verifica la base de datos, **Then** las condiciones económicas (canon) están actualizadas correctamente.
3. **Given** un contrato renovado, **When** el proceso finaliza, **Then** se genera o actualiza correctamente el documento PDF asociado.

---

### User Story 2 - Renovaciones Consecutivas (Priority: P2)

Como administrador del sistema, quiero poder renovar un contrato que ya ha sido renovado en períodos anteriores, manteniendo el historial y asegurando que las fechas se calculen correctamente a partir de la última renovación.

**Why this priority**: Los contratos a largo plazo sufren múltiples renovaciones. Fallar en este escenario corrompe el historial del contrato.

**Independent Test**: Can be fully tested by taking a contract that has a historical record of renewals and renewing it again.

**Acceptance Scenarios**:

1. **Given** un contrato que ya tiene una renovación previa, **When** el usuario ejecuta una nueva renovación, **Then** el sistema calcula el nuevo período a partir de la fecha de vencimiento actual.
2. **Given** un contrato con múltiples renovaciones, **When** se guarda la nueva renovación, **Then** el historial de renovaciones se mantiene íntegro y sin pérdida de datos.

---

### User Story 3 - Renovación con Fechas Límite (Priority: P2)

Como administrador del sistema, quiero que el cálculo de fechas durante la renovación maneje correctamente los casos de fin de mes (ej. 28 de febrero, 31 de diciembre) y años bisiestos.

**Why this priority**: Los errores en el manejo de fechas (Date Math) suelen ser la causa raíz común en fallos de renovación.

**Independent Test**: Can be fully tested by renewing contracts that end on specific edge-case dates (Feb 28, Dec 31, etc).

**Acceptance Scenarios**:

1. **Given** un contrato que vence un 31 de diciembre, **When** se renueva por un año, **Then** la nueva fecha de vencimiento es el 31 de diciembre del año siguiente.
2. **Given** un contrato que vence a fin de febrero en un año bisiesto, **When** se renueva por un año, **Then** el sistema calcula la fecha del año siguiente sin lanzar error de "fecha inválida".

### Edge Cases

- ¿Qué ocurre si un usuario intenta renovar un contrato que ya está cancelado o liquidado?
- ¿Cómo maneja el sistema valores nulos o incompletos en los campos de canon o fechas del contrato original?
- ¿Qué sucede si el nuevo período contractual se solapa con el anterior debido a un error manual del usuario (si se permite edición manual)?
- ¿Qué ocurre si el contrato NO tiene liquidaciones ni recaudos futuros al momento de la renovación? → La renovación se completa con éxito; la propagación de canon es un no-op (0 registros afectados) y NO se insertan registros en `AUDITORIA_PROPAGACION_CANON`.
- ¿Qué ocurre si el nuevo canon es igual al anterior (incremento 0%)? → La propagación no modifica valores y NO se insertan registros de auditoría, ya que la auditoría solo registra filas realmente modificadas (valor cambiado).
- ¿Qué ocurre si una `fecha_pago` de `RECAUDOS` o `fecha_generacion` de `LIQUIDACIONES` es `""` o `NULL` durante la propagación? → La query DEBE convertir el valor vacío a `NULL` con `NULLIF(campo, '')::date` para evitar el error de casting `invalid input syntax for type date`.
- ¿Qué ocurre si NO existe un valor IPC registrado o la duración del contrato es menor a 12 meses? → El canon no cambia (incremento 0%) y la renovación continúa con éxito.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El sistema DEBE procesar la renovación del contrato actualizando la fecha de inicio, la fecha de fin y el período contractual correctamente. En el registro de historial (`RENOVACIONES_CONTRATOS`), `fecha_inicio_renovacion` se calcula como `fecha_fin_original + 1 día` (sin solapamiento). Todos los campos de la entidad `RenovacionContrato` DEBEN ser poblados: `id_contrato_m/a`, `tipo_contrato`, `fecha_inicio_original`, `fecha_fin_original`, `fecha_inicio_renovacion`, `fecha_fin_renovacion`, `canon_anterior`, `canon_nuevo`, `porcentaje_incremento`, `motivo_renovacion`. Este cálculo es idéntico para arrendamientos y mandatos.
- **FR-002**: El sistema DEBE calcular y registrar el nuevo canon según las reglas de negocio de la renovación: el incremento IPC aplica ÚNICAMENTE cuando `duracion_contrato_a >= 12` meses y existe un valor IPC vigente registrado; si la duración es menor a 12 meses o no hay valor IPC registrado, el canon no cambia (incremento 0%). Por "valor IPC vigente" se entiende el registro de mayor `ANIO` vía `IRepositorioIPC.obtener_ultimo()` (`SELECT * FROM IPC ORDER BY ANIO DESC LIMIT 1`); `valor_ipc` es porcentaje flotante (ej. `5.5` = 5.5%). A nivel de contrato/propiedad/mandato solo se actualiza el canon; la comisión, el IVA, los totales y el neto a pagar NO se editan a nivel de contrato, sino que se recalculan automáticamente como campos derivados del nuevo canon en las `LIQUIDACIONES` y `RECAUDOS` futuros. Además, DEBE propagar automáticamente el nuevo canon a `LIQUIDACIONES` futuras (campo `canon_bruto`, donde `fecha_generacion::date >= date_trunc('month', fecha_renovacion::date)`) y a `RECAUDOS` futuros (campo `valor_total`, donde `fecha_pago::date >= date_trunc('month', fecha_renovacion::date)`). Registrar cada cambio propagado en `AUDITORIA_PROPAGACION_CANON` con los campos `contrato_id`, `tabla_afectada`, `registro_id`, `canon_anterior`, `canon_nuevo`, `fecha_actualizacion` y `usuario_sistema`.
- **FR-003**: El sistema DEBE persistir la información actualizada en PostgreSQL garantizando la consistencia transaccional (todo o nada).
- **FR-004**: El sistema DEBE regenerar o actualizar el documento PDF del contrato reflejando los nuevos términos. La regeneración se gestiona en la capa de presentación (`pdf_state.py`, que instancia `ServicioContratos` con `RepositorioRenovacion`/`RepositorioIPC`); esta feature entrega los datos corregidos y SC-004 se cumple como verificación del contenido del PDF generado (sin código nuevo de PDF en la capa de servicios).
- **FR-005**: El sistema DEBE validar los rangos de fechas (ej. fecha de fin > fecha de inicio) y prevenir inconsistencias.
- **FR-006**: El sistema DEBE manejar correctamente contratos que posean historial previo de renovaciones.
- **FR-007**: El sistema DEBE asegurar que la corrección de la renovación NO afecte la creación, edición, ni el cálculo de liquidaciones y recaudos. Las queries de propagación DEBEN usar `NULLIF(campo_fecha, '')::date` para proteger contra cadenas vacías en campos de fecha de PostgreSQL, evitando errores de casting `invalid input syntax for type date`. Este cast seguro DEBE aplicarse de forma consistente a las queries de actualización, consulta y verificación de integridad del contrato 063 (Q1–Q6), usando `NULLIF(campo,'')::date >= date_trunc('month', fecha_renovacion::date)`.
- **FR-008**: El sistema DEBE lanzar excepciones de dominio tipadas (p. ej. `ContratoNoRenovableError`) en lugar de `ValueError` genérico cuando un contrato de arrendamiento o mandato es inexistente o su estado no es `ACTIVO` al intentar renovarlo, conforme a la constitución §2.2.
- **FR-009**: Al renovar un arrendamiento, el sistema DEBE sincronizar `canon_mandato` y `fecha_fin_contrato_m` en el mandato activo asociado a la misma propiedad, tomando el mandato activo más reciente (mayor `id_contrato_m`); si hay varios activos se toma el primero sin error. Si NO existe mandato activo, la renovación continúa con éxito sin sincronizar y sin lanzar error.
- **FR-010**: Tras la renovación, el sistema DEBE actualizar `canon_arrendamiento_estimado` en la propiedad asociada con el canon nuevo (tanto en renovación de arrendamiento como de mandato).
- **FR-011**: El sistema DEBE evitar renovaciones duplicadas accidentales: la renovación de arrendamiento y de mandato deben estar protegidas por el decorador `@idempotent` existente.
- **FR-012**: Tras un commit exitoso de la transacción de renovación, el sistema DEBE invalidar la caché de canon del contrato (claves en `cache_estado_cartera`) para que la UI refleje el nuevo valor. La invalidación NO DEBE bloquear ni retrasar la transacción de BD. Si la invalidación falla tras el commit exitoso, se tolera data obsoleta temporal (consistencia eventual); no se debe abortar ni revertir la transacción.

### Key Entities *(include if feature involves data)*

- **Contrato**: Entidad principal que almacena las fechas, el canon, el estado y la relación con propietario/inquilino.
- **Historial de Renovaciones**: Registro (si existe como entidad separada) que guarda los términos anteriores del contrato.
- **Liquidacion / Recaudo**: Entidades financieras que dependen de las condiciones económicas del contrato.
- **Documento PDF**: Archivo físico o registro que representa el contrato firmado.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: El 100% de los intentos de renovación (normales, consecutivos y límite) se completan exitosamente sin lanzar excepciones o errores en la UI. El set de prueba mínimo que lo verifica son 7 casos: (1) contrato con duración ≥ 12 meses con valor IPC, (2) duración < 12 meses (sin IPC), (3) sin valor IPC registrado (incremento 0%), (4) renovación consecutiva, (5) fechas límite (31-Dic y 28-Feb en año bisiesto), (6) sin recaudos/liquidaciones futuras, (7) sin mandato activo. Además, la atomicidad es verificable: tras inducir un fallo en cualquier paso de la renovación, la BD queda sin estado parcial (rollback completo, sin cambios a mitad de transacción) y al reintentar la operación se completa exitosamente sin renovaciones duplicadas (idempotencia).
- **SC-002**: El 100% de las fechas de vencimiento y nuevos cánones se calculan con precisión matemática según las reglas de negocio.
- **SC-003**: Cero (0) regresiones reportadas en los módulos de Liquidaciones, Recaudos y Creación/Edición de Contratos tras implementar la corrección. Se verifica ejecutando el 100% de la suite de tests existente de esos tres módulos y exigiendo que quede en verde (0 fallos).
- **SC-004**: Los documentos PDF generados post-renovación reflejan los datos correctos en el 100% de los casos de prueba.

## Assumptions

- Se asume que el esquema de base de datos actual en PostgreSQL soporta correctamente los tipos de datos de fechas y valores monetarios.
- El mensaje de error exacto es desconocido; se asume que el error debe ser descubierto mediante el análisis del código y la reproducción del flujo en el entorno de desarrollo/pruebas actual.
- Se asume que no hay reglas de negocio "ocultas" que difieran de la lógica de negocio estándar de renovación de contratos inmobiliarios (incremento anual estándar, prórroga automática).
- PostgreSQL es el ÚNICO motor de base de datos en producción; NO se requiere compatibilidad ni soporte para SQLite en la lógica de negocio o infraestructura nueva (constitución §1).
- La propagación de canon y el bug de casting fueron introducidos por la feature `063-fix-canon-propagation`; esta feature depende de aquella y debe preservar su lógica de propagación.
- Se requiere validar que el schema `RENOVACIONES_CONTRATOS` ya existe en producción con la columna `FECHA_INICIO_RENOVACION TEXT NOT NULL` antes de implementar.
- El cálculo de fechas depende de `CalculadoraContratos.sumar_meses()`, cuyo comportamiento en fechas de borde (28-Feb, 31-Dic, año bisiesto) debe respetarse y cubrirse en pruebas.
- Se declara FUERA del alcance de esta feature el tuning/optimización de performance de la propagación; no se definen metas de latencia ni throughput.
- Se asume que `NULLIF` y `date_trunc` están disponibles en la versión de PostgreSQL de producción (funciones estándar del motor, sin extensiones especiales).
- El decorador `@idempotent` (FR-011) depende de un almacén de respaldo en base de datos: delega en `DatabaseIdempotencyStrategy` y el repositorio `IRepositorioIdempotencia`, que persiste claves/resultados en la tabla PostgreSQL `IDEMPOTENCY_KEYS` (lock atómico, TTL 24h, polling). Por tanto la idempotencia se garantiza entre sesiones e instancias, NO solo en memoria; esta tabla debe existir en producción.
- Supuesto a validar en la fase de tests (criterio de release): la propagación puede ejecutarse en UNA única transacción PostgreSQL sin generar deadlocks frente a procesos concurrentes que escriben `RECAUDOS`/`LIQUIDACIONES`. Se debe cubrir con un test de concurrencia durante la implementación (CHK032).
- "Valor IPC vigente" (FR-002): registro IPC de mayor `ANIO` vía `IRepositorioIPC.obtener_ultimo()` (`ORDER BY ANIO DESC LIMIT 1`); `valor_ipc` es porcentaje flotante (ej. `5.5` = 5.5%). Sin registros → incremento 0%.
- El PDF post-renovación se regenera en la capa de presentación (`pdf_state.py`); esta feature NO introduce código nuevo de PDF. SC-004 = verificación (E-escenario) de que el PDF generado refleja el canon nuevo y las fechas corregidas; el test de verificación debe quedar trazado en `tasks.md`.
- FR-010 (`canon_arrendamiento_estimado`) YA se actualiza en los flujos existentes: arrendamiento (`servicio_contrato_arrendamiento.py:468`) y mandato (`servicio_contrato_mandato.py:291`); la feature debe cubrirlo con pruebas de verificación y trazarlo en `tasks.md`.
