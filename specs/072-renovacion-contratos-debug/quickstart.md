# Quickstart Validation Guide

**Feature**: 072-renovacion-contratos-debug
**Referencias**: [contracts/servicio-renovacion.md](contracts/servicio-renovacion.md) · [data-model.md](data-model.md) · [spec.md](spec.md)

## Prerrequisitos

- PostgreSQL con esquema de `CONTRATOS_ARRENDAMIENTOS`, `CONTRATOS_MANDATOS`, `RENOVACIONES_CONTRATOS`, `LIQUIDACIONES`, `RECAUDOS`, `AUDITORIA_PROPAGACION_CANON`, `PROPIEDADES`, `IPC` y `IDEMPOTENCY_KEYS` (respaldando el decorador `@idempotent`, FR-011).
- App Reflex corriendo (`reflex init` / `reflex run`) o tests de aplicación.
- Pytest para la suite de automatización.

## Setup

```bash
# Crear BD de test
DATABASE_URL=postgres://localhost/inmobiliaria_test python -c "from src.infraestructura.persistencia import conexion; ..."

# Correr pruebas del feature y regresión
pytest tests/unit tests/integration -k "renovacion or liquidaciones or recaudos or contrato"  # SC-001 + SC-003
```

## Escenarios de Validación End-to-End (SC-001)

### E1: Renovación normal con duración >= 12 meses y IPC vigente
1. Crear contrato arriendo con `duracion_contrato_a = 12`, `fecha_fin_contrato_a` = hoy + N días, y un valor en `IPC` vigente.
2. En la UI, abrir el contrato y click **Renovar**.
3. **Resultado esperado**: renovación exitosa; `canon_nuevo = canon_anterior * (1 + IPC/100)`; log en `RENOVACIONES_CONTRATOS` con `fecha_inicio_renovacion = día siguiente al fin original`.

### E2: Duración < 12 meses → 0% de incremento
1. Crear contrato con `duracion_contrato_a = 6` (menos de 12) aunque exista IPC.
2. Renovar.
3. **Resultado esperado**: `porcentaje_incremento = 0`; `canon_nuevo = canon_anterior` (sin cambios).

### E3: Sin valor IPC registrado → 0% de incremento
1. Crear contrato >= 12 meses pero **sin** valor en `IPC` para la fecha de renovación.
2. Renovar.
3. **Resultado esperado**: `porcentaje_incremento = 0`; no falla por IPC ausente.

### E4: Renovación consecutiva
1. Renovar un contrato dos veces seguidas.
2. **Resultado esperado**: la segunda renovación parte del canon de la primera; dos filas válidas en `RENOVACIONES_CONTRATOS` (sin dobles por idempotencia en un mismo intento).

### E5: Fechas límite (31-Dic y 28-Feb en año bisiesto)
1. Contrato con `fecha_fin_contrato_a = 2026-12-31` → `fecha_inicio_renovacion` debe ser `2027-01-01`.
2. Contrato con `fecha_fin_contrato_a = 2028-02-28` (bisiesto) → `fecha_inicio_renovacion = 2028-02-29` y `fecha_fin_renovacion` = +N meses sobre la última fecha del mes destino.
3. **Resultado esperado**: `sumar_meses` maneja bordes; fechas válidas, jamás `""`.

### E6: Sin recaudos/liquidaciones futuros
1. Contrato sin filas futuras en `LIQUIDACIONES`/`RECAUDOS`.
2. Renovar.
3. **Resultado esperado**: renovación exitosa; propagación no actualiza nada; transacción sin error.

### E7: Sin mandato activo
1. Contrato sin `CONTRATOS_MANDATOS` activo asociado.
2. Renovar.
3. **Resultado esperado**: la renovación continúa sin error; se puede renunciar a la sincronización del mandato (FR-009).

## Escenarios de Regresión (SC-003)

Correr la suite existente al 100% y exigir verde:

```bash
# Liquidaciones, Recaudos y Creación/Edición de Contratos
pytest tests/unit tests/integration tests/contract
```

## Escenarios Específicos del Bug (FR-007)

### E8: Recaudos/liquidaciones con fecha vacía
1. Insertar `RECAUDOS` con `fecha_pago = ''` y `LIQUIDACIONES` con `fecha_generacion = ''` para un contrato.
2. Renovar.
3. **Resultado esperado**: **sin** error de PostgreSQL (`invalid input syntax for type date`); las filas con fecha vacía se ignoran en la propagación (`NULLIF`); el resto se actualiza.

### E9: Verificación del log de renovación (FR-005)
1. Consultar `RENOVACIONES_CONTRATOS` tras una renovación.
2. **Resultado esperado**: `fecha_inicio_renovacion` NO es vacío; es el día siguiente al `fecha_fin_original` (bordes manejados).

### E10: Auditoría de propagación (FR-002)
1. Tras renovar con liquidaciones/recaudos futuros actualizados.
2. Consultar `AUDITORIA_PROPAGACION_CANON`.
3. **Resultado esperado**: una fila SOLO por cada fila realmente modificada (tabla_afectada, registro_id, canon_anterior, canon_nuevo, fecha_actualizacion, usuario_sistema); si `canon_nuevo == canon_anterior` (0%) o no hay filas futuras → 0 registros de auditoría. Verificación de integridad con las queries del contrato 063 (Q1–Q6) alineadas al cast seguro `NULLIF(campo,'')::date >= date_trunc('month', ...)`.

### E11: Atomicidad e idempotencia de reintento (SC-001, FR-011)

1. Renovar un contrato con un fallo inducido a mitad de transacción (ej. tras actualizar el contrato y antes de propagar).
2. Reintentar la misma operación (doble clic / reintento de red con la misma `idempotency_key`).
3. **Resultado esperado**: la BD queda SIN estado parcial (rollback completo: sin log, sin filas propagadas, sin auditoría a medias); el reintento completa exitosamente y NO duplica renovaciones (validable contra `IDEMPOTENCY_KEYS`).

### E12: Concurrencia y caché (CHK032, FR-012)

1. Ejecutar dos renovaciones concurrentes (o una renovación concurrente con escrituras de `RECAUDOS`/`LIQUIDACIONES`).
2. **Resultado esperado**: la transacción única de propagación no genera deadlocks ni timeouts de PostgreSQL (supuesto CHK032 validado).
3. Tras el commit exitoso, verificar que la UI muestra el nuevo canon (caché invalidada en `cache_estado_cartera`); si la invalidación falla, la transacción NO se revierte y se acepta data obsoleta temporal (FR-012).

## Verificación de integridad post-renovación

```sql
-- LIQUIDACIONES futuras consistentes con el canon del contrato
SELECT COUNT(*) FROM LIQUIDACIONES l
JOIN CONTRATOS_MANDATOS cm ON l.id_contrato_m = cm.id_contrato_m
WHERE cm.id_contrato_a = :id AND l.canon_bruto != :nuevo_canon
  AND NULLIF(l.fecha_generacion,'')::date >= date_trunc('month', :fecha_renovacion::date);
-- Esperado: 0

-- RECAUDOS futuros consistentes
SELECT COUNT(*) FROM RECAUDOS r
WHERE r.id_contrato_a = :id AND r.valor_total != :nuevo_canon
  AND NULLIF(r.fecha_pago,'')::date >= date_trunc('month', :fecha_renovacion::date);
-- Esperado: 0
```