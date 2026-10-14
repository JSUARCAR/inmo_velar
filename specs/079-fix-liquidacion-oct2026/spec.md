# Feature Specification: Liquidación Propietarios Octubre 2026 Invisible

**Feature Branch**: `079-fix-liquidacion-oct2026`

**Created**: 2026-10-14

**Status**: Draft

**Input**: User description: "Ingeniería inversa — Liquidación de Propietarios: el cliente reporta que realizó la liquidación correspondiente al período de octubre de 2026; sin embargo, la liquidación generada no se está mostrando en la tabla del módulo. Investigar causa raíz en Frontend/Backend/DB, validar flujos individual y masivo, corregir origen, probar y limpiar datos TEST."

## Clarifications

### Session 2026-10-14

- Q: Ejecuciones masivas concurrentes del mismo período por dos administradores, ¿comportamiento esperado? → A: Permitidas; la segunda cuenta duplicados como omitidas (idempotente, sin lock).
- Q: ¿Qué cubre el margen del 5% en SC-001 (95% persistidos)? → A: Solo errores transitorios reintentables (timeout/lock); omitidas y no_elegibles excluidas del cálculo.
- Q: Semántica de filtro por período individual (LIKE) vs agrupada (=), ¿unificar o preservar? → A: Preservar sin cambios (LIKE individual, = agrupada).
- Q: ¿Quién puede disparar la generación masiva? → A: Cualquier usuario con permiso CREAR en Liquidaciones.
- Q: Tiempo límite para la generación masiva de 64 contratos, ¿límite explícito? → A: Sin límite explícito; background async con toast al finalizar.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Generar liquidación masiva octubre 2026 y verla en tabla (Priority: P1)

Como usuario con permiso CREAR en Liquidaciones, genero la liquidación masiva para el período 2026-10 desde la vista agrupada y la veo inmediatamente en la tabla agrupada/individual.

**Why this priority**: Es el caso reportado. Sin esto el módulo es inutilizable para el cierre mensual.

**Independent Test**: Generar masiva para un período TEST (ej. 2099-12) con 3 propietarios conocidos, verificar que el toast reporta generadas>0, que la tabla recarga y que el filtro de período queda en el período generado.

**Acceptance Scenarios**:

1. **Given** existen 64 contratos elegibles sin liquidación para 2026-10, **When** ejecuto generación masiva para 2026-10, **Then** se persisten N liquidaciones con PERIODO='2026-10' y eliminada=FALSE y la tabla las muestra sin recarga manual.
2. **Given** ya existe liquidación para un contrato en 2026-10, **When** re-ejecuto masiva, **Then** ese contrato cuenta como omitida, no duplica (UNIQUE ID_CONTRATO_M+PERIODO) y no lanza error.

---

### User Story 2 - Generar liquidación individual y verla inmediatamente (Priority: P1)

Como administrador, creo una liquidación individual por propiedad para 2026-10 y la veo en la tabla sin cambiar filtros manualmente.

**Why this priority**: Flujo alternativo que debe seguir funcionando y sirve como comparador para detectar lógica duplicada.

**Independent Test**: Crear individual para contrato elegible en período TEST, verificar persistencia y aparición en tabla individual y agrupada.

**Acceptance Scenarios**:

1. **Given** contrato elegible sin liquidación en período TEST, **When** guardo individual, **Then** se crea con estado 'En Proceso' y aparece en ambas vistas al filtrar por ese período.

---

### User Story 3 - Consultar liquidaciones por período con filtros y paginación (Priority: P2)

Como administrador, filtro por período 2026-10, 2026-09 y anteriores, navego páginas y el total coincide con la BD.

**Why this priority**: Garantiza que el problema no es solo de generación sino de recuperación/visualización.

**Independent Test**: Filtrar por 2026-09 (60 registros conocidos) y por período TEST, comparar total UI vs COUNT(*) en BD.

**Acceptance Scenarios**:

1. **Given** hay 60 liquidaciones en 2026-09, **When** filtro período=2026-09, **Then** total=60 y paginación 25+25+10 funciona.
2. **Given** filtro en 2026-09 y genero masiva para 2026-10, **When** termina la generación, **Then** el filtro cambia automáticamente a 2026-10 y muestra las nuevas.

---

### Edge Cases

- ¿Qué pasa cuando un contrato ACTIVO no tiene arriendo activo? Se cuenta como no_elegible con detalle "sin contrato de arrendamiento activo", no bloquea al resto.
- ¿Cómo maneja el sistema el doble clic / reintento de masiva para el mismo período? Segunda ejecución debe reportar omitidas, no duplicar.
- ¿Qué pasa si la BD es PostgreSQL (prod, claves en MAYÚSCULAS) vs SQLite (dev, claves mixtas)? El acceso a `tiene_arriendo` debe funcionar en ambas.
- ¿Qué pasa si el usuario cambia de vista durante la generación masiva en background? La recarga debe ocurrir de todos modos.
- ¿Qué pasa si no hay propietarios elegibles? Debe mostrar error "No se encontraron propietarios..." y no dejar loading infinito.
- ¿Qué pasa si dos administradores ejecutan la masiva del mismo período a la vez? Ambas ejecuciones están permitidas; la restricción UNIQUE (ID_CONTRATO_M+PERIODO) serializa de facto y la segunda cuenta duplicados como omitidas, sin lock global. Una carrera simultánea exacta sobre el mismo contrato+período cuenta como error transitorio reintentable.
- Regla de estado consolidado: si alguna liquidación está En Proceso → En Proceso; si todas Aprobada → Aprobada; ídem Pagada/Cancelada; mezcla → Mixto. El filtro Estado ofrece Todos/En Proceso/Aprobada/Pagada/Cancelada.
- ¿Período futuro vs pasado? Sin distinción: cualquier YYYY-MM es generable, incluido el mes en curso.
- ¿Filtro sin resultados o página exacta? Total 0 muestra tabla vacía con total 0; total exactamente 25 muestra una página llena sin "Siguiente".

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El sistema MUST generar liquidaciones por propietario para un período dado iterando sus contratos de mandato activos y creando una liquidación por contrato elegible. Término canónico: "masiva" = generación por propietario para todos los propietarios (sinónimo de "bulk" en UI).
- **FR-002**: El sistema MUST clasificar como no_elegible (sin persistir) los contratos sin arrendamiento activo, con motivo auditable.
- **FR-003**: El sistema MUST contar como omitida (sin error) la liquidación ya existente para el par contrato+período.
- **FR-004**: El sistema MUST persistir liquidaciones con PERIODO exacto 'YYYY-MM' y estado inicial 'En Proceso', sin trim implícito (el input type="month" no produce espacios).
- **FR-005**: El sistema MUST recuperar liquidaciones por período exacto en vista agrupada y por coincidencia de período en vista individual, excluyendo eliminadas (diferencia preservada intencionalmente, sin unificar).
- **FR-006**: Tras generación masiva, el sistema MUST sincronizar el filtro de período con el período generado, resetear a página 1 y recargar la tabla en ambas vistas.
- **FR-007**: El sistema MUST soportar cursores dict con claves en MAYÚSCULAS (PostgreSQL) y minúsculas (SQLite) sin KeyError.
- **FR-008**: El sistema MUST reportar al usuario el resumen "generadas / ya existían / no elegibles / con error" con los primeros motivos, sin ocultar errores como éxito.
- **FR-009**: El sistema MUST mantener intactas las reglas de negocio (comisión, IVA, gastos, estados En Proceso→Aprobada→Pagada→Cancelada) y la integridad referencial.
- **FR-010**: Los datos creados exclusivamente para TEST (períodos 2099-*) MUST ser eliminados físicamente al finalizar, verificando COUNT(*)=0.

### Key Entities

- **Liquidación**: Representa el estado de cuenta mensual por contrato de mandato; atributos clave: ID_CONTRATO_M, PERIODO (YYYY-MM), estado, canon, comisiones, egresos, neto, eliminada.
- **Contrato de mandato / arrendamiento**: Determinan elegibilidad; solo mandatos ACTIVO con arriendo ACTIVO en la misma propiedad generan.
- **ResultadoGeneracionPropietario**: Agregado generadas/omitidas/errores/no_elegibles + detalles; usado por masiva para el toast y diagnóstico.
- **Generación Masiva**: Término canónico que designa la ejecución masiva por lote (`generar_liquidacion_masiva` en frontend / botón "users" en vista agrupada), la cual itera todos los propietarios con contratos de mandato activos para generar las liquidaciones del período seleccionado.
- **Filtro de período / vista**: Estado del frontend (filter_periodo, vista_agrupada, current_page) que determina qué registros se consultan y muestran.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Al generar masiva para un período sin liquidaciones, al menos el 95% de los contratos elegibles sin liquidación previa resultan persistidos y visibles en la tabla sin recarga manual; el margen del 5% cubre exclusivamente errores transitorios reintentables (timeout/lock) y excluye omitidas y no_elegibles del cálculo.
- **SC-002**: La consulta por período 2026-09 devuelve 60 registros en menos de 5 segundos y la paginación muestra 25 por página sin duplicados ni faltantes.
- **SC-003**: El 100% de las generaciones por propietario en el entorno de persistencia de producción completan con éxito y sin errores de acceso a campos ni incompatibilidades de datos en pruebas con 3 o más propietarios.
- **SC-004**: Tras la limpieza, cero registros con PERIODO LIKE '2099%' permanecen en la base de datos (verificado por COUNT(*)=0).
- **SC-005**: Los 8 tests unitarios/de dominio existentes siguen pasando sin regresiones.

## Assumptions

- Los 64 contratos elegibles detectados el 2026-10-14 representan el universo para octubre 2026; no se crean contratos nuevos durante la prueba.
- La base de producción es PostgreSQL en Railway (DATABASE_URL); SQLite solo se usa en dev/test y preserva el alias en minúsculas.
- Persistencia nativa PostgreSQL según constitución §2.3: tipos estrictos (booleanos explícitos, fechas ISO 8601) y cero dependencias nuevas de SQLite; los nombres de clases del diagnóstico viven en research/código, no en criterios de aceptación.
- El usuario genera la masiva desde la vista agrupada (único punto de entrada del botón "users"), pero la tabla debe refrescarse en ambas vistas.
- No se regenera octubre 2026 en producción hasta desplegar el fix; la validación se hace con períodos TEST 2099-* que luego se borran.
- El formato de período es siempre YYYY-MM proveniente de input type="month"; no se aceptan otros formatos.
- La generación masiva corre en background async sin límite explícito de duración; la UI muestra estado de carga y toast resumen al finalizar.
