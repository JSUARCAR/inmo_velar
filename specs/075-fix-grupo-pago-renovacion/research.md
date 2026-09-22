# Research: Grupo de pago correcto y atómico en la renovación de contratos

**Feature**: 075-fix-grupo-pago-renovacion | **Date**: 2026-09-21

Resuelve las decisiones técnicas del plan. No quedan `NEEDS CLARIFICATION`: las ambigüedades de negocio fueron resueltas en el spec (sesiones de clarificación 2026-09-21).

---

## R1. Regla única de grupo y día de pago (dominio)

**Decisión**: Centralizar en `CalculadoraContratos`:
- `calcular_grupo_operativo(fecha) -> int`: tramos V2 — día 28-7 → 1; 8-17 → 2; 18-27 → 3.
- `calcular_dia_pago_por_tipo(fecha, tipo) -> int`: mandato → 10/20/30 según grupo; arrendamiento → día exacto de la fecha.
- `calcular_ciclo_pago_mandato(fecha)` se conserva como fachada que delega en `calcular_grupo_operativo` + `calcular_dia_pago_mandato` (compatibilidad de firmas existentes).
- Constantes nombradas para los límites de tramo (sin "magic numbers"): `DIA_INICIO_GRUPO_1_MIN=28`, `DIA_INICIO_GRUPO_2_MIN=8`, etc.

**Rationale**: elimina la contradicción actual entre creación de arriendo (`día ≤10 → G1`, `≤20 → G2`, resto `G3`), edición de arriendo (regla V2 de mandato) y renovación (ninguna). Único punto de verdad, dominio puro y 100% testeable.

**Alternativas consideradas**:
- Mantener reglas por ruta y solo corregir la renovación: rechazada; perpetúa la inconsistencia histórica (FR-003 exige unificar).
- Implementar la regla en SQL dentro del script: rechazada por la feature 067 (SQL no debe contener lógica de negocio).

---

## R2. Fecha efectiva del período vigente y herencia del mandato

**Decisión**: `fecha_efectiva` por contrato:
1. Si el contrato tiene renovaciones: `FECHA_INICIO_RENOVACION` de la renovación más reciente (`ORDER BY FECHA_RENOVACION DESC, ID_RENOVACION DESC LIMIT 1`).
2. Si no tiene renovaciones propias y es un **mandato** cuya propiedad tiene un arrendamiento ACTIVO con renovaciones: hereda la fecha efectiva del arrendamiento (la renovación más reciente del arriendo). Esto materializa FR-005 (el mandato adopta el período renovado del arriendo).
3. En cualquier otro caso: fecha de inicio original del contrato.

**Rationale**: sin la herencia del punto 2, el resultado runtime de FR-005 (mandato sincronizado al período del arriendo renovado) sería marcado como inconsistente por la propia auditoría (que vería al mandato sin historial y lo compararía contra su fecha de inicio original). La regla queda determinística y simétrica entre runtime y auditoría.

**Alternativas consideradas**:
- Registrar una renovación de mandato artificial al renovar el arriendo: rechazada; falsea el historial de renovaciones del mandato.
- Modificar `FECHA_INICIO_CONTRATO_M` para reflejar el nuevo período: rechazada; altera el dato histórico del contrato (FR-010 prohíbe tocar historia).
- Auditar cada contrato solo contra sus propias renovaciones: rechazada; contradice FR-005 y generaría remediaciones que revierten la sincronización.

---

## R3. Atomicidad de la renovación de mandato

**Decisión**: Extraer `_ejecutar_renovacion_mandato` y envolver `renovar_mandato` en `with db.transaccion():`, con el mismo patrón de `renovar_arrendamiento` (`servicio_contrato_arrendamiento.py:406-419`). La invalidación de caché `cache_estado_cartera` se ejecuta **después** del commit (fuera del bloque), conforme FR-012.

**Hallazgo de causa raíz**: `ServicioContratoMandato.renovar_mandato` (`servicio_contrato_mandato.py:252-317`) hoy no abre transacción explícita. Con `psycopg2` (`autocommit=False`) y el wrapper de conexión (`database.py:111-121`), solo `RepositorioRenovacionPostgres.crear` hace `conn.commit()`; las actualizaciones de mandato/propiedad quedan fuera de un commit atómico y pueden perderse o mezclarse con la siguiente operación de la misma conexión.

**Alternativas consideradas**:
- Confiar en los `commit()` internos de cada repositorio: rechazada; viola FR-008 (todo o nada).
- Usar una transacción por repositorio: rechazada; no garantiza rollback conjunto.

---

## R4. Fidelidad de persistencia del grupo en arrendamientos

**Decisión**: Añadir el mapeo de `GRUPO_OPERATIVO` en `RepositorioContratoArrendamientoPostgres._row_to_entity` (`repositorio_contrato_arrendamiento_postgres.py:442-521`): `grupo_operativo=gv("GRUPO_OPERATIVO") or 0`. Sin cambios de esquema.

**Rationale**: `actualizar()` escribe `GRUPO_OPERATIVO = contrato.grupo_operativo` (líneas 396/420); al no mapearse en la lectura, toda renovación/edición persistía `0`. Es la causa directa del "grupo que no corresponde".

**Alternativas consideradas**:
- Cambiar el `UPDATE` para no escribir el grupo: rechazada; impediría persistir el recálculo legítimo y dejaría el campo ingobernable.
- Leer el grupo en un query aparte dentro del servicio: rechazada; duplica acceso a datos y no corrige la pérdida en otras rutas de edición.

---

## R5. Auditoría y remediación de contratos activos

**Decisión**: Script `scripts/remediacion/remediar_grupos_pago_v4.py`:
- **Por defecto solo-lectura**; con `--commit` aplica cambios. Precedente: `scripts/migrar_ciclo_operativo_v3.py` y feature 067.
- Una **sola transacción** para toda la remediación (`with db_manager.transaccion()`), rollback total ante cualquier error.
- Extracción masiva: contratos ACTIVOS de `CONTRATOS_MANDATOS` y `CONTRATOS_ARRENDAMIENTOS` + última renovación por contrato (subconsulta `DISTINCT ON`/`LATERAL` con `ORDER BY FECHA_RENOVACION DESC, ID_RENOVACION DESC`) + renovaciones del arriendo activo por propiedad (para la herencia R2).
- Cálculo esperado en Python con `CalculadoraContratos` (nunca en SQL).
- Reporte por consola y CSV en `outputs/` con: tipo, id, fecha efectiva usada, grupo actual, día actual, grupo esperado, día esperado, acción.
- Fechas TEXT tratadas con `NULLIF(campo,'')::date` (precedente 072 FR-007) para evitar errores de cast.
- Solo actualiza filas con discrepancia real; única sentencia `UPDATE` por tabla por lote de ids.
- Con `--commit`, cada actualización usa **compare-and-set** sobre los valores leídos (`WHERE id = X AND GRUPO_OPERATIVO = leído AND FECHA_PAGO = leído`): las filas modificadas durante la remediación (p. ej. por una renovación concurrente) se omiten y se reportan, sin bloquear la operación normal (sesión de clarificación 2026-09-21).

**Rationale**: FR-009/FR-010 y la decisión de clarificación (operador autorizado, sin remediación automática en despliegue). Idempotente: re-ejecutar en dry-run reporta cero discrepancias.

**Alternativas consideradas**:
- Migración automática al desplegar: rechazada por decisión de clarificación (riesgo operativo).
- Botón en UI: rechazada; la UI no es el canal elegido y añadiría RBAC/estado no previstos.
- Un script por tipo de contrato: rechazada; duplica lógica y multiplica la superficie de error.
- Bloqueo pesimista de filas (`SELECT ... FOR UPDATE`) durante la remediación: rechazada; bloquearía las renovaciones en curso durante toda la transacción. El compare-and-set protege sin bloquear.

---

## R6. Idempotencia, mensaje operativo y caché

**Decisión**:
- Se conserva el decorador `@idempotent(key_prefix=..., ttl_hours=24)` (`src/aplicacion/decorators/idempotent.py`), respaldado por `IDEMPOTENCY_KEYS` (estrategia `DatabaseIdempotencyStrategy`, TTL real 24 h en `registrar`).
- La UI (`contratos_state.execute_renewal`, líneas 1102-1123) ya captura `ValorFueraDeRangoError`, `ValueError` y `Exception`; se alinea el mensaje de rollback al texto operativo del spec ("no se aplicó ningún cambio; es seguro reintentar") para fallos transaccionales, sin exponer errores crudos del motor.
- Invalidación de caché post-commit tolerante: `_invalidar_cache_estado_cartera` ya no falla la operación; en arriendo se mantiene fuera de la transacción (`servicio_contrato_arrendamiento.py:418`).

**Alternativas consideradas**:
- Idempotencia en memoria: rechazada; no cubre reintentos entre sesiones/instancias (FR-008).
- Revertir la transacción si falla la caché: rechazada; contradice el commit ya confirmado (FR-012).

---

## R7. Consulta determinista de la última renovación

**Decisión**: La última renovación se resuelve dentro de la **extracción masiva del script** con una consulta SQL única (subconsulta por contrato `ORDER BY FECHA_RENOVACION DESC, ID_RENOVACION DESC LIMIT 1`, o `DISTINCT ON`/`LATERAL` según convenga). No se añade método por contrato al repositorio.

**Rationale**: FR-001 exige "mayor `fecha_renovacion`, desempate por mayor ID". Resolverlo en bloque evita N+1 (el plan compromete una pasada SQL + cálculo en memoria) y evita un método sin consumidor en runtime: la renovación conoce su nueva fecha efectiva localmente (`fecha_fin_original + 1`) y la auditoría es el único consumidor del historial.

**Alternativas consideradas**:
- `RepositorioRenovacion.obtener_ultima_por_contrato` + uso por contrato: rechazada por N+1 y por introducir API sin consumidor (constitución §12/§15, código como pasivo).
- Calcular la "más reciente" en Python tras un `SELECT` sin orden: rechazada; el orden debe ser determinista en SQL con desempate explícito.

---

## R8. Estrategia de pruebas y datos TEST

**Decisión**:
- **Unitarias** (sin I/O): `tests/unit/test_grupo_pago_reglas.py` (tramos y bordes 7/8, 17/18, 27/28, 1, 31; unificación arriendo/mandato), `tests/unit/test_renovacion_grupo_pago.py` (mocks: recálculo en renovación de arriendo, sync de mandato, mandato sin renovaciones propias hereda período, mismo tramo no degrada, transacción usada en mandato), `tests/unit/test_arriendo_repo_grupo_pago.py` (mapeo `_row_to_entity`).
- **Integración** (guarda `DATABASE_URL`): `tests/integration/test_renovacion_grupo_pago_atomico.py` (persistencia grupo/día tras renovar, rollback inducido sin estado parcial, idempotencia), `tests/integration/test_auditoria_grupos_pago.py` (auditoría cero discrepancias tras remediación).
- **Datos TEST**: UUID en matrícula/documento (patrón existente `tests/integration/test_renovacion_flujo_completo.py`), limpieza por `teardown`/fixture que elimina contratos, renovaciones, liquidaciones/recaudos y personas creadas. Verificación final de ausencia de huérfanos (FR-013/SC-005).
- **Regresión**: suite existente de Contratos/Liquidaciones/Recaudos + `scripts/check_syntax.py`, `mypy`, `ruff`, `black`.

**Alternativas consideradas**:
- Solo pruebas manuales por UI: rechazada; la feature exige rollback e idempotencia verificables de forma objetiva.
- Dejar la limpieza de TEST a un script externo: rechazada; el spec exige que no quede información de prueba.

---

## R9. Unificación de la creación de arrendamientos

**Decisión**: `_ejecutar_creacion_arrendamiento` (`servicio_contrato_arrendamiento.py:106-114`) pasa a calcular el grupo con `calcular_grupo_operativo(fecha_inicio)` (tramos V2) y el día de pago con `calcular_dia_pago_arrendamiento` (día exacto). La edición (`_ejecutar_actualizacion_arrendamiento:212-222`) se refactoriza al mismo par de funciones.

**Rationale**: FR-003 exige que creación, edición y renovación compartan la regla; evita que una creación nueva nazca con un grupo distinto al que la auditoría espera.

**Alternativas consideradas**:
- Conservar los tramos de creación (`≤10/≤20/resto`): rechazada por decisión de clarificación (tramos V2 + día exacto).

---

## R10. Alineación del trigger `fn_sync_fechas_mandato` con la regla V2

**Decisión**: Actualizar el cuerpo de `fn_sync_fechas_mandato` (trigger `trg_sync_fechas_mandato` sobre `CONTRATOS_ARRENDAMIENTOS`) a los tramos V2 (28-7 → G1/10, 8-17 → G2/20, 18-27 → G3/30) mediante `CREATE OR REPLACE FUNCTION`, sin cambios de esquema ni downtime.

**Hallazgo (causa raíz de la recurrencia)**: el trigger implementaba la regla obsoleta V1 (1-10 → G1/10, 11-20 → G2/20, resto → G3/'-1') y reescribía `GRUPO_OPERATIVO`/`FECHA_PAGO` del mandato activo en cada INSERT de arriendo ACTIVO y en cada UPDATE de sus fechas/duración. Era la ruta de ejecución no contemplada por la feature 067: cada creación de arriendo o cambio de fechas corrompía el mandato con la regla vieja (evidencia: mandatos con día `-1`, valor que solo produce este trigger; el test de auditoría falló inicialmente porque su propio INSERT disparó el trigger). Los otros dos triggers (`trg_sync_canon_arrendamiento`, `trg_actualizar_disponibilidad_arrendamiento`) no tocan el grupo y se conservan intactos.

**Rationale**: la capa de servicios ya sincroniza correctamente, pero la creación de arriendos y las ediciones directas dependen del trigger como red de seguridad; con la regla V1 revertía los valores remediados (p. ej. día 30 → '-1') e invalidaba SC-002/SC-006.

**Alternativas consideradas**:
- Eliminar el trigger y dejar solo la sincronización del servicio: rechazada; la creación de arriendos no sincroniza el mandato en la capa de servicios y se perdería la red de seguridad para rutas directas.
- No migrar y documentar el riesgo: rechazada; la primera creación o cambio de fechas posterior reintroduciría el defecto.

---

## Dependencias y supuestos operativos

- **PostgreSQL de pruebas**: los tests de integración requieren `DATABASE_URL` apuntando a una base segura; sin ella se omiten (`pytest.skip`). La remediación real se ejecuta primero en dry-run (FR-010).
- **Tabla `IDEMPOTENCY_KEYS`** existente en producción (feature 072).
- **Tabla `RENOVACIONES_CONTRATOS`**: columnas `FECHA_RENOVACION`, `FECHA_INICIO_RENOVACION`, `ID_RENOVACION` (usadas por el criterio R2/R7).
- **Sin script `update-agent-context`** disponible en `.specify/scripts/powershell/`; el contexto de agentes se mantiene actualizado vía `AGENTS.md` del repositorio.
