# Contratos: Renovación de Contratos (Debug de casting de fechas)

**Date**: 2026-09-13
**Feature**: 072-renovacion-contratos-debug
**Scope**: Fase 1 - Contratos de interfaz del flujo de renovación

El proyecto es una web service interno (Reflex). La "interfaz externa" es la llamada de la capa de presentación a los servicios de aplicación y las queries SQL (PostgreSQL) que estos ejecutan. Este documento define ambos contratos.

## 1. Contrato de Servicio de Aplicación

### MS1: `renovar_arrendamiento(id_contrato_a, ...)`

- **Ubicación**: `src/aplicacion/servicios/servicio_contrato_arrendamiento.py`
- **Decorador**: `@idempotent(key_prefix="arriendo:renovar")` (existente)
- **Entrada**: `id_contrato_a` (int) + datos opcionales de fecha.
- **Comportamiento**:
  1. Valida que el contrato sea renovable; si no → `ContratoNoRenovableError` (FR-008).
  2. Calcula incremento IPC (`_calcular_incremento_ipc`): aplica solo si `duracion_contrato_a >= 12` meses Y existe valor IPC vigente; si no → 0%.
  3. Actualiza `canon_arrendamiento` del contrato y `canon_arrendamiento_estimado` de la propiedad (FR-010).
  4. Sincroniza el mandato activo MÁS RECIENTE: `canon_mandato`, `fecha_fin_contrato_m` (FR-009); ante múltiples activos se toma el de mayor `id_contrato_m` (primero sin error); si no hay mandato activo, continúa sin error.
  5. Inserta log en `RENOVACIONES_CONTRATOS` con `fecha_inicio_renovacion = fecha_fin_original + 1 día` (helper `CalculadoraContratos.calcular_fecha_inicio_renovacion`, NO `sumar_meses`) (FR-005).
  6. Propaga canon a `LIQUIDACIONES`/`RECAUDOS` futuros y audita (FR-002, `AUDITORIA_PROPAGACION_CANON`).
  7. Invalida la caché de canon (`invalidate_cache` en `cache_estado_cartera`) DESPUÉS del commit exitoso; NO bloquea la transacción; si falla, se tolera data obsoleta temporal (FR-012).
  8. Commit transaccional; en error → ROLLBACK (FR-003).
- **Resultado**: log de renovación creado; canon propagado; estado notificado a la UI.

### MS2: `renovar_mandato(id_contrato_m, ...)`

- **Ubicación**: `src/aplicacion/servicios/servicio_contrato_mandato.py`
- **Decorador**: `@idempotent(key_prefix="mandato:renovar")` — **NUEVO** (FR-011; hoy no existe).
- **Entrada**: `id_contrato_m` (int).
- **Comportamiento**: mismo flujo que MS1 en el lado del mandato (canon_mandato, fechas).
- **Resultado**: mandato actualizado sin duplicar en reintentos.

### MS3: `_calcular_incremento_ipc(contrato, ipc_actual)` (helper testable)

- Regla pura: retorna `valor_ipc` (decremento en %) si `duracion_contrato_a >= 12` y hay IPC; else `0.0`.

## 2. Contrato de Queries SQL (PostgreSQL)

> Hereda y corrige `specs/063-fix-canon-propagation/contracts/sql-queries.md`. Regla: **toda comparación de fecha usa `NULLIF(campo,'')::date`**. El cast seguro también alinea las queries de actualización (Q1/Q2), consulta (Q3/Q4) y verificación de integridad (Q5/Q6) del contrato 063 a `NULLIF(campo,'')::date >= date_trunc('month', ...)` (FR-007).

### S1: Actualizar `canon_bruto` en LIQUIDACIONES futuras

```sql
UPDATE LIQUIDACIONES
SET canon_bruto = %s,
    comision_monto = <derivado del canon_nuevo>,
    iva_comision = <derivado del canon_nuevo>,
    total_ingresos = <derivado del canon_nuevo>,
    total_egresos = <derivado del canon_nuevo>,
    neto_a_pagar = <derivado del canon_nuevo>
WHERE id_contrato_m = (
    SELECT id_contrato_m FROM CONTRATOS_MANDATOS
    WHERE id_contrato_a = %s LIMIT 1
)
AND NULLIF(fecha_generacion, '')::date >= date_trunc('month', %s::date);
```

**Parámetros**: (canon_nuevo, contrato_id, fecha_renovacion)

### S2: Actualizar `valor_total` en RECAUDOS futuros

```sql
UPDATE RECAUDOS
SET valor_total = %s
WHERE id_contrato_a = %s
AND NULLIF(fecha_pago, '')::date >= date_trunc('month', %s::date);
```

**Parámetros**: (canon_nuevo, contrato_id, fecha_renovacion)

### S3: Registrar auditoría por fila actualizada

```sql
INSERT INTO AUDITORIA_PROPAGACION_CANON (
    contrato_id, tabla_afectada, registro_id,
    canon_anterior, canon_nuevo, fecha_actualizacion, usuario_sistema
) VALUES (%s, %s, %s, %s, %s, NOW(), %s);
```

**Parámetros**: (contrato_id, 'LIQUIDACIONES'|'RECAUDOS', registro_id, canon_anterior, canon_nuevo, usuario_sistema)

**Nota**: Insertar SOLO por fila realmente modificada (valor cambiado). Con incremento 0% (`canon_nuevo == canon_anterior`) o 0 filas futuras → sin inserts de auditoría (FR-002, Edge Cases).

### S4: Log de renovación en `RENOVACIONES_CONTRATOS`

```sql
INSERT INTO RENOVACIONES_CONTRATOS (
    id_contrato_m, id_contrato_a, tipo_contrato,
    fecha_inicio_original, fecha_fin_original,
    fecha_inicio_renovacion, fecha_fin_renovacion,
    canon_anterior, canon_nuevo, porcentaje_incremento,
    motivo_renovacion, fecha_renovacion, created_at, created_by
) VALUES (%s, ...);
-- fecha_inicio_renovacion = fecha_fin_original + 1 día (helper calcular_fecha_inicio_renovacion) -- nunca ''
```

## 3. Reglas transversales del contrato

1. Todas las queries usan `%s` como placeholder (PostgreSQL).
2. Comparaciones de fecha SIEMPRE con `NULLIF(campo,'')::date` (fix FR-007); aplica a propagación y a las queries heredadas del contrato 063 (Q1–Q6).
3. Actualización y auditoría en una única transacción atómica; ROLLBACK ante cualquier fallo (FR-003).
4. Orden de propagación: `LIQUIDACIONES` primero, `RECAUDOS` segundo.
5. Fila con fecha vacía → se excluye (NULL no cumple la comparación) sin romper la renovación.
6. La regla de las filas "futuras" usa `>= date_trunc('month', fecha_renovacion)` para incluir el mes de la propia renovación.
7. Al existir múltiples mandatos activos se sincroniza solo el más reciente (mayor `id_contrato_m`) (FR-009).
8. Invalidación de caché tras commit exitoso, NO bloqueante; estado obsoleto temporal tolerado (FR-012).