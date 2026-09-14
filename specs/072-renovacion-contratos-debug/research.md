# Research: Renovación de Contratos (Debug de casting de fechas)

**Date**: 2026-09-13
**Feature**: 072-renovacion-contratos-debug
**Scope**: Fase 0 - Investigación y decisiones de diseño

## Resumen Ejecutivo

La renovación de contratos falla en producción por un `Python` `ValueError` de fecha (fechas vacías `""` casteadas con `""::date` en PostgreSQL) introducido en `063-fix-canon-propagation`. La lección de `sumar_meses` (función única de verdad para bordes de fechas) y el uso de `NULLIF` permiten un fix mínimo, atómico y con cobertura completa.

```python
lesion = fecha_vacia.cast("")  # PostgreSQL: ERROR invalid input syntax for type date
```

## Investigación

### Causa Raíz (Confirmada)

1. En `actualizar_canon_liquidaciones_futuras` y `actualizar_valor_recaudos_futuros` se comparan fechas con `>` y `%s`; las filas con `fecha_generacion`/`fecha_pago` vacíos (`""`) rompen el cast de PostgreSQL al evaluar `'""'::date`.
2. El flujo de renovación construye `RenovacionContrato` sin poblar `fecha_inicio_renovacion` (el dataclass `renovacion_contrato.py:26` y el INSERT del repositorio `repositorio_renovacion_postgres.py:21,34` ya incluyen la columna), por lo que el log `RENOVACIONES_CONTRATOS` se persistía con fecha vacía `""`.
3. `renovar_mandato` no usaba `@idempotent`, a diferencia de `renovar_arrendamiento` (FR-011): reintentos duplican renovaciones.

## Resolución de NEEDS CLARIFICATION (Phase 0)

Todas las clarificaciones de la sesión 2026-09-13 quedaron resueltas en el spec (`spec.md`, sección `Clarifications`). No queda ningún `NEEDS CLARIFICATION` abierto.

| Clarificación | Decisión |
|---------------|----------|
| Aplicación del IPC | Incremento IPC solo si `duracion_contrato_a >= 12` meses Y existe valor IPC vigente registrado; si no → incremento 0% (canon sin cambios). |
| Alcance de condiciones económicas | Solo canon a nivel contrato/propiedad/mandato. Comisión, IVA, totales y neto NO se editan a nivel de contrato: se recalculan como campos derivados del nuevo canon en `LIQUIDACIONES`/`RECAUDOS` futuros. |
| Excepciones tipadas | `ContratoNoRenovableError` (excepción de dominio, constitución §2.2) sustituye `ValueError` en los flujos de renovación (FR-008). |
| Set de tests SC-001 | 7 casos: (1) duración ≥12m con IPC → incremento; (2) duración <12m sin IPC → 0%; (3) sin valor IPC → 0%; (4) renovación consecutiva; (5) bordes 31-Dic y 28-Feb (año bisiesto); (6) sin recaudos/liquidaciones futuros → no rompe; (7) sin mandato activo → continúa sin error. |
| Suite de regresión SC-003 | Debe correr al 100% y quedar verde la suite existente de Liquidaciones, Recaudos y Creación/Edición de Contratos. |
| Invalidación de caché (FR-012) | Tras commit exitoso se invalida la caché de canon; la invalidación NO bloquea la transacción; si falla se tolera data obsoleta temporal (consistencia eventual). |
| Múltiples mandatos activos (FR-009) | Se sincroniza el mandato activo más reciente (mayor `id_contrato_m`); ante varios activos, el primero sin error. |
| Cast seguro en contrato 063 (FR-007) | Las 6 queries heredadas (Q1–Q6: actualización, consulta, verificación de integridad) se alinean a `NULLIF(campo,'')::date >= date_trunc('month', ...)`. |
| Atomicidad medible (SC-001) | Fallo inducido en cualquier paso → rollback completo sin estado parcial; reintento idempotente completa sin duplicados. |
| Auditoría (FR-002) | `AUDITORIA_PROPAGACION_CANON` registra SOLO filas realmente modificadas; incremento 0% o 0 filas futuras → sin registros. |

## Decisions

### D1: Casting seguro de fechas vacías con `NULLIF`

- **Decision**: Reemplazar las comparaciones `campo::date > %s` por `NULLIF(campo,'')::date >= date_trunc('month', %s::date)` (y el equivalente para `LIQUIDACIONES.fecha_generacion`). El cast seguro se aplica de forma consistente a las 6 queries heredadas del contrato 063 (Q1/Q2 actualización, Q3/Q4 consulta, Q5/Q6 verificación de integridad) (FR-007).
- **Rationale**: `NULLIF` es estándar PostgreSQL; convierte `""` en `NULL` y las filas con fecha vacía se excluyen de la propagación (no hay fecha qué actualizar). El `>=` con `date_trunc('month', ...)` cubre la fila del propio mes de renovación.
- **Alternatives considered**: (a) Borrar/regenerar filas con fecha vacía (destructivo); (b) validación en capa de aplicación antes de cada query (fragmenta la lógica y no protege otros callers). Se descartaron.

### D2: Poblar `fecha_inicio_renovacion` en los flujos de renovación

- **Decision**: Poblar siempre `fecha_inicio_renovacion = fecha_fin_original + 1 día` (vía el nuevo helper `CalculadoraContratos.calcular_fecha_inicio_renovacion(fecha_fin_original)` — NO `sumar_meses(.,1)`, que suma meses calendario y rompe el caso E5) en la construcción de `RenovacionContrato` dentro de `renovar_arrendamiento` (`servicio_contrato_arrendamiento.py:443`) y `renovar_mandato` (`servicio_contrato_mandato.py:266`). El dataclass (`renovacion_contrato.py:26`) y el INSERT del repositorio (`repositorio_renovacion_postgres.py:21,34`) ya incluyen el campo; hoy los servicios no lo pasan y se persiste `""`.
- **Rationale**: Evita `corrupted log dates`; `+1 día` es correcto para todo caso límite (31-Dic → 01-Ene, quickstart E5) sin matemática de meses calendario; `sumar_meses` se reserva para `fecha_fin_renovacion` (CHK006).
- **Alternatives considered**: Derivación a nivel de repositorio (oculta la regla de negocio); validación post-insert (corrige el dato tarde).

### D3: Regla IPC (resuelta por clarificación)

- **Decision**: Cálculo del incremento aislado en `_calcular_incremento_ipc(contrato, ipc_actual)`; aplica solo si `duracion_contrato_a >= 12` meses Y existe valor IPC vigente; si no, `0`.
- **Rationale**: Cumple la regla de negocio *y* el caso de test con IPC ausente; centraliza la lógica para prueba unitaria pura.
- **Alternatives considered**: Consulta ad-hoc en el servicio (acopla y no es testeble).

### D4: Alcance económico (resuelta por clarificación)

- **Decision**: La renovación actualiza únicamente `canon_arrendamiento` (contrato), `canon_mandato` (mandato) y `canon_arrendamiento_estimado` (propiedad). Comisión/IVA/totales/neto se computan como derivados del nuevo canon en `LIQUIDACIONES`/`RECAUDOS` futuros.
- **Rationale**: El canon es la única fuente de verdad; los campos derivados se regeneran con el nuevo valor en cada fila futura, sin tocar config de contrato.
- **Alternatives considered**: Recalcular comisión/IPC en contrato (cambia el contenido del contrato y no está solicitado).

### D5: Excepciones tipadas del dominio (FR-008)

- **Decision**: Crear `ContratoNoRenovableError` en `src/dominio/excepciones.py` y lanzarlo en los flujos de renovación (mandato/arrendamiento) en lugar de `ValueError`.
- **Rationale**: Constitución §2.2 — las excepciones deben ser tipadas en el dominio; la UI puede capturarlas y traducirlas.
- **Alternatives considered**: Mantener `ValueError` genérico (viola la constitución y no distingue contexto).

### D6: Idempotencia en ambos flujos (FR-011)

- **Decision**: Decorar `renovar_mandato` con `@idempotent(key_prefix="mandato:renovar")`, espejo de `arriendo:renovar` ya presente en `renovar_arrendamiento`. El decorador delega en `DatabaseIdempotencyStrategy`/`IRepositorioIdempotencia`, respaldado en la tabla PostgreSQL `IDEMPOTENCY_KEYS` (lock atómico + TTL 24h + polling): idempotencia real entre sesiones e instancias (CHK031).
- **Rationale**: Los reintentos por red/timeout no duplican renovaciones; patrón ya existente en el repo; almacén DB-backed ya implementado.
- **Alternatives considered**: Control en la UI (no protege la API); verificación manual de existencias (carrera); almacén en memoria (no protege multi-instancia).

### D7: Auditoría y sincronización (FR-002/FR-009/FR-010)

- **Decision**: Propagar a `LIQUIDACIONES` (`canon_bruto`) y `RECAUDOS` (`valor_total`) con `>= date_trunc('month', %s::date)`, registrar cada cambio en `AUDITORIA_PROPAGACION_CANON` SOLO para filas realmente modificadas (valor cambiado; con 0% o 0 filas futuras no se inserta nada), sincronizar `canon_mandato` y `fecha_fin_contrato_m` del mandato activo más reciente (mayor `id_contrato_m`; ante varios activos, el primero sin error; si no existe, continuar sin error) y actualizar `canon_arrendamiento_estimado` en `PROPIEDADES`.
- **Rationale**: Mantiene consistencia entre contrato, mandato, propiedad y cobranza; los campos de auditoría ya existen (no requiere migración); la auditoría refleja cambios reales.
- **Alternatives considered**: Actualizar solo el contrato (deja mandato/propiedad/recaudos inconsistentes); auditar hasta sin cambios (ruido en auditoría).

### D8: Suite de tests (SC-001 + SC-003)

- **Decision**: Añadir 7 casos de unidad/integración específicos de renovación + criterio de atomicidad medible (fallo inducido en cualquier paso → BD sin estado parcial por rollback completo; reintento completa sin duplicados) + test de concurrencia que valide que la transacción única no genera deadlocks frente a escrituras concurrentes en `RECAUDOS`/`LIQUIDACIONES` (CHK032) + ejecutar al 100% la suite existente de Liquidaciones, Recaudos y Creación/Edición de Contratos como regresión obligatoria.
- **Rationale**: SC-001 fija los criterios de éxito del feature (incluida la no-particialidad); SC-003 garantiza que el fix no rompe funcionalidad adyacente; el supuesto de no-deadlocks se valida con evidencia (CHK032).
- **Alternatives considered**: Solo tests del flujo nuevo (riesgo de regresión en casting); asumir sin evidencia la ausencia de deadlocks (supuesto sin validar).

## Tecnología y buenas prácticas

- **PostgreSQL**: `NULLIF`, `date_trunc('month', ...)`, placeholders `%s`, transacción atómica con `ROLLBACK` (patrón ya presente en `servicio_contrato_arrendamiento.py`).
- **Reflex + psycopg2**: la UI llama a los servicios de aplicación; sin capa REST intermedia (web service Reflex).
- **Pytest**: tests de dominio 100% (constitución §5) y de aplicación >90%.
- **Invalidación de caché (FR-012)**: vía `CacheManager`/`invalidate_cache(namespace)` (`src/infraestructura/cache/cache_manager.py`), sobre las claves de canon del contrato (`cache_estado_cartera`). Tras el commit exitoso, invalidación NO bloqueante; si falla, se tolera data obsoleta temporal (consistencia eventual) y la transacción no se revierte.

## Conclusiones

Fix mínimo y retenido a los flujos de renovación existentes. No hay `NEEDS CLARIFICATION` pendientes; Phase 1 (data-model, contracts, quickstart) puede proceder.