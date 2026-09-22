# Contrato: Limpieza de Datos TEST por Bitácora

**Feature**: 076-liquidacion-requiere-arrendamiento
**Modulo**: `src/scripts/limpiar_datos_test_bitacora_pg.py`

## Propósito

Eliminación TOTAL de los datos TEST creados durante la validación de esta feature (contratos, propiedades, liquidaciones, recaudos y relaciones derivadas), dirigida por la bitácora de creación (Q1), con limpieza de huérfanas que apuntan exclusivamente a la bitácora (Q3). Re-ejecutable e idempotente (Q6). Los datos reales NO se tocan (FR-008, SC-005).

## Interfaz CLI

```text
python src/scripts/limpiar_datos_test_bitacora_pg.py --dry-run     # defecto: reporta sin borrar
python src/scripts/limpiar_datos_test_bitacora_pg.py --ejecutar    # borra de verdad (transacción)
python src/scripts/limpiar_datos_test_bitacora_pg.py --bitacora specs/076-liquidacion-requiere-arrendamiento/bitacora_test.json
```

Salida: por entidad, conteo de registros a borrar / borrados; huérfanas detectadas; estado `OK` o `ROLLBACK` ante error.

## Bitácora de entrada

Archivo JSON (ver esquema en `data-model.md`) con `{entidad: [ids]}`. Entidades soportadas: `contratos_mandatos`, `contratos_arrendamientos`, `propiedades`, `propietarios`, `arrendatarios`, `personas`, `liquidaciones`, `recaudos`.

## Orden de borrado (FK, igual patrón que `limpiar_datos_prueba_pg.py`)

1. `RECAUDO_CONCEPTOS` → `RECAUDOS` (IDs de bitácora).
2. Datos derivados huérfanos que apuntan SOLO a entidades de la bitácora: `INCIDENTE_LIQUIDACION` → plan/cuotas de incidente (`PLAN_PAGO_INCIDENTE`, `CUOTA_INCIDENTE`, `HISTORIAL_INCIDENTES`) → `INCIDENTES`.
3. `LIQUIDACIONES` (IDs de bitácora) y vínculos con incidencias.
4. `CONTRATOS_ARRENDAMIENTOS` y `CONTRATOS_MANDATOS` (IDs de bitácora).
5. `PROPIEDADES` (IDs de bitácora).
6. Roles: `ARRENDATARIOS` / `PROPIETARIOS` (IDs de bitácora, en el orden correcto de dependencia).
7. `PERSONAS` (IDs de bitácora).

## Idempotencia y recuperación (Q6)

- `DELETE ... WHERE id IN (%s,...)` ignora IDs inexistentes; no lanza por faltantes.
- En `--ejecutar`, TENER transacción única: se elimina en orden; ante CUALQUIER error se ejecuta `ROLLBACK` (nada eliminado) y el script termina con status de error sin tocar el resto; la re-ejecución completa queda segura.
- Puede ejecutarse múltiples veces sin efectos colaterales (SC-005).

## Reglas de seguridad

- Prohibido borrar por patrones de estado/nombre/dirección; solo por IDs de la bitácora (Q1).
- Los datos reales (fuera de la bitácora) no se tocan; verificación posterior por consulta (SC-005).
- Al terminar, se elimina la bitácora de creación (solo ella); si queda bitácora o huérfanas → resultado de error visible para el operador.
- No excepciones genéricas: cada fallo se loguea con la entidad e ID que lo causó.