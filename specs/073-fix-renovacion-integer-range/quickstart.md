# Quickstart: validar el fix de renovación `integer out of range`

**Feature**: `073-fix-renovacion-integer-range`

Guía de validación end-to-end. Detalles de entidades y reglas:
`data-model.md`; contrato de comportamiento: `contracts/propagacion-canon.md`.
Implementación y suites completas pertenecen a `tasks.md` / fase de
implementación. **Nunca contra producción**: usar BD de prueba o staging.

## Prerrequisitos

- `DATABASE_URL` apuntando a BD de prueba; dependencias instaladas.
- Suites en verde antes del cambio:
  `pytest tests/unit/test_renovacion_ipc.py tests/integration/test_renovacion_flujo_completo.py -q`

## Escenario 1 — Reproducción SQL (solo lectura, 1 min)

```sql
-- Antes del fix: falla con integer out of range
SELECT CAST(2300000 * comision_porcentaje / 10000.0 AS INTEGER)
FROM liquidaciones LIMIT 1;
-- Con el fix (cómputo intermedio 64 bits): retorna 230000
SELECT CAST(2300000::BIGINT * comision_porcentaje / 10000 AS INTEGER)
FROM liquidaciones LIMIT 1;
```

Esperado: la primera forma falla, la segunda retorna el valor exacto.

## Escenario 2 — Propagación límite (datos desechables)

1. Crear contrato de prueba ACTIVO con canon 2.300.000, comisión 1000 y
   duración 12, más una liquidación futura.
2. Ejecutar la renovación y verificar: sin errores; `comision_monto` =
   230.000; auditoría con 1 fila.
3. Repetir con canon 10.000.000 × comisión 1500 → `comision_monto` =
   1.500.000 sin errores.

## Escenario 3 — Caso índice (staging)

Renovar el contrato de CR 6 CL 03-40 CS 54, CJT LA ALQUERIA; verificar
historial (anterior 2.300.000, nuevo = 2.300.000 + IPC), vigencia extendida,
`verificar_propagacion_canon` con cero inconsistencias.

## Escenario 4 — No regresión

```bash
pytest tests/unit/test_renovacion_ipc.py tests/unit/test_renovacion_idempotencia.py tests/integration/test_renovacion_flujo_completo.py tests/integration/test_renovacion_atomicidad.py tests/integration/test_renovacion_consecutiva.py tests/integration/test_renovacion_concurrencia.py tests/integration/test_renovacion_errores.py tests/integration/test_canon_propiedad_renovacion.py -q
```

Esperado: 100% de las pruebas que pasaban antes siguen pasando.
