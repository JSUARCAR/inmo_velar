# Research: Elegibilidad conjunta Mandato Activo + Arrendamiento Activo

**Date**: 2026-09-22
**Feature**: 076-liquidacion-requiere-arrendamiento

## Resumen del estado actual (ingeniería inversa)

### Generación individual

- `ServicioFinanciero.generar_liquidacion_mensual(id_contrato_m, periodo, datos_adicionales, usuario_sistema)` (`src/aplicacion/servicios/servicio_financiero.py:156`):
  - Valida que el mandato exista (`repo_mandato.obtener_por_id`).
  - Valida no duplicidad por contrato/período.
  - **NO** valida `ESTADO_CONTRATO_M = 'ACTIVO'` ni la existencia de arrendamiento activo.
- El formulario individual carga candidatos con:
  - `query_propiedades` (`liquidaciones_state.py:223`): `INNER JOIN CONTRATOS_MANDATOS cm ... WHERE cm.ESTADO_CONTRATO_M = 'ACTIVO'` — solo filtra mandato ACTIVO.
  - `query_propietarios` (`liquidaciones_state.py:232`): igual filtro por mandato ACTIVO.
  - `load_propiedad_seleccionada` (`liquidaciones_state.py:643`): busca mandato ACTIVO por `cm.ID_PROPIEDAD` y `ESTADO_CONTRATO_M = 'ACTIVO'`, pero no valida arrendamiento.

### Generación masiva

- `ServicioFinanciero.generar_liquidacion_propietario(id_propietario, periodo, ...)` (`servicio_financiero.py:266`):
  - Consulta `SELECT ID_CONTRATO_M FROM CONTRATOS_MANDATOS WHERE ID_PROPIETARIO = %s AND ESTADO_CONTRATO_M = 'ACTIVO'` — ausencia de validación de arrendamiento.
  - Por cada contrato llama a `generar_liquidacion_mensual` y clasifica el resultado en `generadas/omitidas/errores`.
- Handler masivo `generar_liquidacion_masiva` (`liquidaciones_state.py:1084`):
  - `SELECT DISTINCT prop.ID_PROPIETARIO ... INNER JOIN CONTRATOS_MANDATOS cm ... WHERE cm.ESTADO_CONTRATO_M = 'ACTIVO'` — considera propietarios con mandato ACTIVO, sin arrendamiento.

### Piezas reutilizables ya existentes

- `RepositorioContratoArrendamientoPostgres.obtener_activo_por_propiedad(id_propiedad)` (`repositorio_contrato_arrendamiento_postgres.py:90`):
  `SELECT * FROM CONTRATOS_ARRENDAMIENTOS WHERE ID_PROPIEDAD = %s AND ESTADO_CONTRATO_A = 'ACTIVO'` — exactamente la verificación requerida por la combinación 1.
- `EstadoContrato` enum (`src/dominio/constantes/estados_contrato.py`): incluye `ACTIVO`; existe helper `es_activo`.
- `ResultadoGeneracionPropietario` (`src/dominio/entidades/resultado_generacion.py`): Value Object con `generadas / omitidas / errores`. Se requiere extenderlo con `no_elegibles` para reportar exclusiones sin tratarlas como error.
- `limpiar_datos_prueba_pg.py` (`src/scripts/limpiar_datos_prueba_pg.py`): patrón de limpieza quirúrgica por lista de IDs, en una sola transacción con rollback total; **base del nuevo script por bitácora**.
- `Liquidacion.fecha_generacion` (`src/dominio/entidades/liquidacion.py:30`): fecha ISO de generación → base temporal de la auditoría histórica.
- Estados de contrato: `ESTADO_CONTRATO_A`/`ESTADO_CONTRATO_M` con valores `'ACTIVO'` frente a inactivo/finalizado (no se inventan estados).

## Decisiones de diseño

### Decision 1: Dónde reside la regla de elegibilidad

**Decision**: La regla vive en **Dominio + Aplicación**, no en la UI. Se crea un Value Object de dominio `ResultadoElegibilidad(frozen)` con campos `elegible: bool` y `motivo: str` (motivo en lenguaje de negocio), y una excepción de dominio `LiquidacionNoElegibleError(motivo)`. `ServicioFinanciero` es el único orquestador que evalúa la elegibilidad invocando `repo_arriendo.obtener_activo_por_propiedad(id_propiedad)` bajo el contrato de que el mandato esté ACTIVO.

**Rationale**: FR-003 exige que no pueda eludirse por ninguna ruta. Si la validación vive solo en el combobox o en la query de la UI, la llamada directa a `generar_liquidacion_mensual` (usada por `generar_liquidacion_propietario`, individual y cualquier integración futura) seguiría generando liquidaciones inelegibles.

**Funcionamiento**:
1. `generar_liquidacion_mensual`: tras validar existencia del mandato, verifica `contrato.estado_contrato_m` sea `ACTIVO` (vía `es_activo`) y `repo_arriendo.obtener_activo_por_propiedad(contrato.id_propiedad)` retorne un arrendamiento. Si falla → `LiquidacionNoElegibleError(motivo)`.
2. `generar_liquidacion_propietario`: la consulta de contratos se restringe a `ID_PROPIEDAD IN (propiedades con arrendamiento ACTIVO)` y los contratos de la combinación 2–5 se clasifican como `no_elegibles` (no como errores).
3. UI: el formulario y la masiva filtran candidatos de antemano (consulta conjunta) para no ofrecer/u operar sobre inelegibles, y el mensaje de exclusión usa el `motivo` en lenguaje de negocio.

**Alternatives considered**:
- Validar solo en el frontend/combobox: Rechazado (FR-003, eludible por cualquier ruta interna).
- Validar solo en la query de la masiva: Rechazado (las combinaciones 2–5 pasarían en llamadas directas al servicio).
- Reusar `obtener_arrendamiento_ACTIVO` de `ServicioContratos`: Aceptado como alternativa equivalente; se prefiere la inyección directa de `repo_arriendo` en `ServicioFinanciero` (ya existente) para no acoplar servicios.

### Decision 2: Verificación de MISMA propiedad por ID único

**Decision**: La coincidencia mandato/arrendamiento se evalúa **exclusivamente** por el identificador único del inmueble (`ID_PROPIEDAD`). `obtener_activo_por_propiedad(id_propiedad)` filtra por `ID_PROPIEDAD = %s AND ESTADO_CONTRATO_A = 'ACTIVO'`, por lo que un arrendamiento activo en otra propiedad jamas cuenta.

**Rationale**: Clarificación Q5 del spec: no se acepta coincidencia por dirección o nombre (dos inmuebles pueden compartir dirección legal similar). Este método ya garantiza la misma propiedad.

**Alternatives considered**:
- Comparar por `DIRECCION_PROPIEDAD`: Rechazado (Chesterton's Fence + Q5).
- Validar por propietario compartido: Rechazado (mandato y arrendamiento pueden tener partes distintas).

### Decision 3: Arrendamientos múltiples en la misma propiedad

**Decision**: Basta UN arrendamiento ACTIVO en la `ID_PROPIEDAD` del mandato para ser elegible. `obtener_activo_por_propiedad` retorna el primero que cumple (`LIMIT` implícito por `fetchone`), lo cual satisface el edge case del spec (uno activo entre varios finalizados).

**Rationale**: Assumptions del spec: la existencia de arrendamientos finalizados paralelos no deshabilita si existe uno activo.

**Alternatives considered**:
- Exigir que TODOS los arrendamientos estén activos: Rechazado (contradice el spec).

### Decision 4: Consultas de candidatos (UI) — filtro conjunto

**Decision**: Las tres consultas de la UI se refuerzan para exigir arrendamiento ACTIVO en la misma propiedad:
- `query_propiedades` y `query_propietarios` (individual) se reescriben con un `EXISTS`/`INNER JOIN` sobre `CONTRATOS_ARRENDAMIENTOS ca ON ca.ID_PROPIEDAD = cm.ID_PROPIEDAD AND ca.ESTADO_CONTRATO_A = 'ACTIVO'`.
- La masiva (`SELECT DISTINCT prop.ID_PROPIETARIO`) se resta a propietarios con al menos una propiedad cumpliendo la combinación completa.

**Rationale**: FR-005 (formulario solo lista elegibles) y FR-004/FR-006 (masiva excluye inelegibles y no aborta).

**Alternatives considered**:
- Dejar la query y marcar no elegibles al generar: Rechazado por FR-005 (el combobox no debe ofrecerlas).

### Decision 5: Clasificación de no elegibles en la masiva

**Decision**: Se extiende `ResultadoGeneracionPropietario` con el atributo `no_elegibles` (default 0). `generar_liquidacion_propietario` cuenta como `no_elegibles` los mandatos ACTIVO sin arrendamiento activo; la excepción de dominio `LiquidacionNoElegibleError` no se cuenta como error. El handler masivo agrega un cuarto contador y el toast/sumario muestra `generadas / ya existían / no elegibles / con error`.

**Rationale**: FR-006 y SC-007: robustez — la masiva NO aborta por exclusiones; solo reporta omitidas/no elegibles. Alinea con la clasificación de 056 (omitida ≠ error).

**Alternatives considered**:
- Contar no elegibles como errores: Rechazado (confunde al operador y contradice el negocio, donde es un caso esperado).
- Silenciar los no elegibles: Rechazado (SC-006 exige comunicar la causa).

### Decision 6: Auditoría de solo lectura re-generable

**Decision**: Se crea `ServicioAuditoriaElegibilidad` en `src/aplicacion/servicios/` con un método `auditar(periodo=None, fecha_reconstruccion=None)` que:
- Consulta las liquidaciones históricas (+ contrato, propiedad, propietario, `fecha_generacion`, estado vigente de mandato y arrendamiento).
- Para cada liquidación evalúa la combinación **al estado vigente en `fecha_generacion`** (usando `FECHA_INICIO_CONTRATO_M/A` y `FECHA_FIN_CONTRATO_M/A` junto con `ESTADO_CONTRATO_M/A`, no el estado actual).
- Devuelve filas con `periodo, id_liquidacion, direccion_propiedad, propietario, motivo` para las que NO cumplen.
- **No persiste resultados**; registra criterios (fecha de reconstrucción, filtro, período) en un log/bitácora de ejecución para re-generación a demanda.

**Rationale**: FR-007 y SC-004: solo lectura; reconstrucción histórica contra el estado de la fecha de generación (Q2); re-generable con los mismos criterios (Q7); sin copias de resultados.

**Nota técnica**: La reconstrucción histórica exacta requiere interpretar `ESTADO` conocido hoy + rango de fechas del contrato en la fecha de generación. Si las fechas históricas de cambio de estado no están disponibles con precisión en el modelo actual, se documenta el supuesto y la auditoría se basa en el intervalo `[FECHA_INICIO, FECHA_FIN]` contra `fecha_generacion` (Decisión de implementación; ver contrato en `contracts/auditoria-elegibilidad.md`).

**Alternatives considered**:
- Auditar contra el estado actual: Rechazado (Q2).
- Persistir una tabla de resultados de auditoría: Rechazado (Q7: re-generable, sin copias).

### Decision 7: Limpieza TEST dirigida por bitácora

**Decision**: Se replica el enfoque de `limpiar_datos_prueba_pg.py` en un nuevo script `limpiar_datos_test_bitacora_pg.py` que:
- Lee la **bitácora de creación** (archivo `bitacora_test.json` en la carpeta de la feature) con `{entidad: [ids]}`: contratos mandato, contratos arrendamiento, propiedades, liquidaciones, recaudos (y relaciones derivadas).
- Borra en orden FK (recaudos → liquidaciones/incidentes → contratos → propiedades → propietarios arrendatarios/rol → personas), en una sola transacción.
- Es **idempotente**: los IDs inexistentes se ignoran (`DELETE ... IN (ids)` no falla por faltantes); re-ejecutable sin efectos colaterales.
- Ante un error se **detiene en el punto** sin tocar el resto (transacción con rollback total como el script original).
- Soporta `--dry-run` y `--ejecutar`.

**Rationale**: Q1/Q6 y FR-008: limpieza dirigida por bitácora explícita; re-ejecutable/idempotente; detención ante error parcial.

**Alternatives considered**:
- Limpieza por patrón de nombres/estado: Rechazado (contamina datos reales; Q1 exige bitácora).
- Reutilizar únicamente `limpiar_datos_prueba_pg.py` con su `.txt`: Aceptado como referencia de orden FK y transacción, pero se necesita un script propio para bitácora JSON + entrega dirigida por la feature.

### Decision 8: Métricas de rendimiento y volumen (diferidas a este plan por Q4)

**Decision**:
- **Generación masiva**: < 30s para ~100 propietarios con consultas conjuntas (una sola query de candidatos con JOIN + evaluación de elegibilidad por mandato dentro de `generar_liquidacion_propietario`). No se exige paralelismo.
- **Auditoría**: < 60s sobre el volumen histórico actual del sistema (~miles de liquidaciones) con la consulta de auditoría en una sola pasada.
- **Limpieza TEST**: < 10s para la bitácora de la feature (decenas de registros).

**Rationale**: Q4 delegó las metas al plan. Son límites operativos razonables para el volumen actual (~50 propiedades, ~24 periodos). Se miden en la fase de implementación con pruebas e2e.

**Alternatives considered**:
- Definir metas en el spec: Descartado (Q4 lo asignó al plan).

## Validation

### Escenarios de prueba (referencia al quickstart)

1. Matriz 5 combinaciones × 2 rutas = 10 verificaciones (SC-002).
2. Consistencia individual/masiva sobre el mismo conjunto (SC-003).
3. Auditoría marca solo las históricas no elegibles, sin modificar nada (SC-004).
4. Limpieza por bitácora: 0 registros TEST y 0 huérfanos; datos reales intactos; re-ejecución sin efectos (SC-005).
5. Mensajes de exclusión en lenguaje de negocio (SC-006).
6. Masiva robusta ante exclusiones con conteo generadas/omitidas/no elegibles/errores (SC-007).
### Confirmación T002
Se ha verificado que pytest, reflex y psycopg2 están disponibles. epo_arriendo está inyectado en ServicioFinanciero.__init__. El método obtener_activo_por_propiedad existe en src/infraestructura/persistencia/repositorio_contrato_arrendamiento_postgres.py en la línea esperada y no requiere cambios.
