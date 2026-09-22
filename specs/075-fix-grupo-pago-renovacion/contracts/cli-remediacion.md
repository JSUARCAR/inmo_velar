# Contrato: CLI de auditoría y remediación de grupos de pago

**Componente**: `scripts/remediacion/remediar_grupos_pago_v4.py`
**Tipo**: interfaz de línea de comandos operativa (uso interno, operador autorizado)

## Invocación

```bash
python scripts/remediacion/remediar_grupos_pago_v4.py                 # Solo lectura (default)
python scripts/remediacion/remediar_grupos_pago_v4.py --commit        # Aplica remediación
python scripts/remediacion/remediar_grupos_pago_v4.py --outputs-dir outputs
python scripts/remediacion/remediar_grupos_pago_v4.py --help
```

| Flag | Tipo | Default | Descripción |
|---|---|---|---|
| `--commit` | flag | ausente (solo lectura) | Aplica los cambios en una única transacción |
| `--outputs-dir` | ruta | `outputs/` | Directorio del reporte CSV |
| `--help` | flag | — | Ayuda |

## Precondiciones

- `DATABASE_URL` configurada y accesible (PostgreSQL). Sin ella: error de configuración (exit code 2), no se crea transacción.
- Ejecutable desde la raíz del repositorio (importa `src.*`).

## Comportamiento

1. **Extracción**: contratos ACTIVOS de `CONTRATOS_MANDATOS` y `CONTRATOS_ARRENDAMIENTOS`; última renovación por contrato (`FECHA_RENOVACION DESC, ID_RENOVACION DESC`); renovaciones del arriendo activo por propiedad. Fechas TEXT con `NULLIF(campo,'')::date`.
2. **Cálculo**: `fecha_efectiva` según data-model §4; grupo/día esperados con `CalculadoraContratos` (nunca en SQL).
3. **Reporte**: consola + CSV `outputs/auditoria_grupos_pago_v4_<timestamp>.csv` con las columnas del data-model §7. Siempre se genera, incluso sin discrepancias.
4. **Sin `--commit`**: no ejecuta ninguna escritura; la transacción se revierte/cierra sin cambios.
5. **Con `--commit`**: actualiza únicamente filas con discrepancia real y solo si los valores leídos siguen vigentes (compare-and-set); las filas modificadas durante la remediación (p. ej. por una renovación concurrente) se omiten y se reportan; una sola transacción; commit al final.
6. **Fallo en cualquier punto**: rollback total; mensaje de error a stderr; exit code 1.

## Postcondiciones / garantías

- Idempotente: una segunda corrida en solo lectura reporta cero discrepancias una vez resueltas las filas omitidas por concurrencia (que quedan reportadas para revisión o nueva corrida).
- No toca contratos finalizados ni cancelados (filtro `ESTADO = 'ACTIVO'`).
- No modifica historia financiera, canon, fechas ni renovaciones; solo `GRUPO_OPERATIVO` y `FECHA_PAGO`.
- Las renovaciones concurrentes no se sobrescriben: las filas modificadas durante la remediación se omiten y se reportan.
- `--commit` no se activa automáticamente en despliegues.

## Códigos de salida

| Código | Significado |
|---|---|
| 0 | Ejecución exitosa (con o sin discrepancias) |
| 1 | Error de ejecución (rollback aplicado) |
| 2 | Error de configuración/entorno (sin conexión) |

## Ejemplo de salida (consola)

```text
Modo: SOLO LECTURA
Contratos activos evaluados: 412 (mandatos 260 / arriendos 152)
Discrepancias encontradas: 17
[MANDATO 56] fecha_efectiva=2021-09-20 grupo: 2 -> 3 | día: 20 -> 30
[ARRENDAMIENTO 31] fecha_efectiva=2025-03-01 grupo: 0 -> 1 | día: 0 -> 1
Reporte: outputs/auditoria_grupos_pago_v4_20260921_101530.csv
Sin cambios aplicados (dry-run). Use --commit para remediar.
```
