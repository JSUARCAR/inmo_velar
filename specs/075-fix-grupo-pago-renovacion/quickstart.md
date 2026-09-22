# Quickstart: Validación de la feature 075

**Feature**: Grupo de pago correcto y atómico en la renovación de contratos
**Objetivo**: demostrar de extremo a extremo que el grupo/día de pago se recalcula, persiste y audita de forma correcta y atómica.

## Prerrequisitos

- Entorno Python con `requirements.txt` instalado (`pip install -r requirements.txt`).
- `DATABASE_URL` apuntando a una base PostgreSQL **de pruebas** (los tests de integración se omiten sin ella).
- Ejecutar desde la raíz del repositorio.

## 1. Validación unitaria (sin base de datos)

```bash
python -m pytest tests/unit/test_grupo_pago_reglas.py tests/unit/test_renovacion_grupo_pago.py tests/unit/test_arriendo_repo_grupo_pago.py -v
```

**Resultado esperado**: verde. Cubre tramos V2 (bordes 7/8, 17/18, 27/28, 31, 1), recálculo en renovación de arriendo y mandato, herencia del período del arriendo por el mandato, mismo tramo sin degradación y mapeo de `GRUPO_OPERATIVO`.

## 2. Validación de integración (base de datos de pruebas)

```bash
python -m pytest tests/integration/test_renovacion_grupo_pago_atomico.py tests/integration/test_auditoria_grupos_pago.py -v
```

**Resultado esperado**: verde. Escenarios:
1. Renovar un arriendo crea historial y persiste `GRUPO_OPERATIVO`/`FECHA_PAGO` del nuevo período; el mandato activo de la misma propiedad queda alineado.
2. Renovar un mandato persiste su grupo/día con base en el período renovado, en una única transacción.
3. Fallo inducido tras actualizar el contrato → rollback total (sin renovación, sin cambios de grupo) y reintento exitoso sin duplicados.
4. Auditoría en solo lectura reporta discrepancias y, tras remediar, cero discrepancias.

## 3. Auditoría/remediación operativa (dry-run → commit)

```bash
python scripts/remediacion/remediar_grupos_pago_v4.py
python scripts/remediacion/remediar_grupos_pago_v4.py --commit
python scripts/remediacion/remediar_grupos_pago_v4.py   # verificación post: 0 discrepancias
```

**Resultado esperado**:
- Primera corrida: reporte por consola y CSV en `outputs/auditoria_grupos_pago_v4_<timestamp>.csv` con `fecha_efectiva`, grupo/día actual y esperado por contrato activo inconsistente.
- `--commit`: aplica en una única transacción; el reporte marca `Actualizado` y `Omitida` para filas modificadas concurrentemente (compare-and-set), que quedan para revisión o nueva corrida.
- Tercera corrida: `Discrepancias encontradas: 0` (idempotencia).

## 4. Validación en UI (runtime)

```bash
reflex run --env dev
```

1. Abrir **Contratos** y localizar un contrato ACTIVO próximo a vencer.
2. Ejecutar **Renovar** y confirmar en el modal.
3. Verificar: el badge de grupo y el día de pago corresponden al nuevo período; el mandato asociado muestra el mismo tramo de grupo (día 10/20/30).
4. Consultar **Liquidaciones de Propietarios** y **Recaudos**: los filtros por ciclo operativo/día de pago ubican los registros bajo el grupo correcto.
5. Forzar un error de renovación (p. ej. canon fuera de rango): el usuario ve un mensaje operativo y el contrato conserva sus valores previos.

## 5. Regresión

```bash
python scripts/check_syntax.py
python -m pytest tests/unit tests/integration -q
python -m pytest tests/unit/test_renovacion_ipc.py tests/unit/test_renovacion_fechas_limite.py tests/unit/test_renovacion_idempotencia.py tests/unit/test_renovacion_cache_fr012.py tests/unit/test_arriendo_sincronizacion.py -q
```

**Resultado esperado**: `check_syntax` OK y 100% de las pruebas que pasaban antes siguen pasando (SC-004).

## 6. Higiene de datos TEST (condición obligatoria)

- Los tests de integración crean datos con marcadores únicos (`TEST-...`, UUID) y los eliminan en su limpieza (`fixture`/`teardown` por IDs registrados).
- Verificación final de ausencia de residuos (todos los conteos deben ser **0**):

```sql
-- Propiedades y personas de prueba
SELECT COUNT(*) FROM PROPIEDADES WHERE MATRICULA_INMOBILIARIA LIKE 'TEST-%';
SELECT COUNT(*) FROM PERSONAS WHERE NUMERO_DOCUMENTO LIKE 'DOC-T%' OR NUMERO_DOCUMENTO LIKE 'TEST-%';

-- Contratos de prueba y sus derivados
SELECT COUNT(*) FROM CONTRATOS_ARRENDAMIENTOS ca
 JOIN PROPIEDADES p ON p.ID_PROPIEDAD = ca.ID_PROPIEDAD
 WHERE p.MATRICULA_INMOBILIARIA LIKE 'TEST-%';

SELECT COUNT(*) FROM CONTRATOS_MANDATOS cm
 JOIN PROPIEDADES p ON p.ID_PROPIEDAD = cm.ID_PROPIEDAD
 WHERE p.MATRICULA_INMOBILIARIA LIKE 'TEST-%';

SELECT COUNT(*) FROM RENOVACIONES_CONTRATOS r
 WHERE r.ID_CONTRATO_A IN (
         SELECT ca.ID_CONTRATO_A FROM CONTRATOS_ARRENDAMIENTOS ca
         JOIN PROPIEDADES p ON p.ID_PROPIEDAD = ca.ID_PROPIEDAD
         WHERE p.MATRICULA_INMOBILIARIA LIKE 'TEST-%')
    OR r.ID_CONTRATO_M IN (
         SELECT cm.ID_CONTRATO_M FROM CONTRATOS_MANDATOS cm
         JOIN PROPIEDADES p ON p.ID_PROPIEDAD = cm.ID_PROPIEDAD
         WHERE p.MATRICULA_INMOBILIARIA LIKE 'TEST-%');
```

El test `tests/integration/test_auditoria_grupos_pago.py` incluye además el bloque automático de verificación de huérfanos (contratos, propiedades, liquidaciones, recaudos, renovaciones y personas TEST) y falla si algún conteo es distinto de cero.

## 7. Seguimiento post-release (SC-006)

A los 30 días de operación, verificar que no existan contratos ACTIVOS con grupo inválido (resultado esperado: **0** en ambas consultas):

```sql
SELECT COUNT(*) FROM CONTRATOS_ARRENDAMIENTOS
 WHERE ESTADO_CONTRATO_A = 'ACTIVO'
   AND (GRUPO_OPERATIVO IS NULL OR GRUPO_OPERATIVO NOT IN (1, 2, 3));

SELECT COUNT(*) FROM CONTRATOS_MANDATOS
 WHERE ESTADO_CONTRATO_M = 'ACTIVO'
   AND (GRUPO_OPERATIVO IS NULL OR GRUPO_OPERATIVO NOT IN (1, 2, 3));
```

## Referencias

- Reglas y decisiones: [research.md](./research.md), [data-model.md](./data-model.md)
- Contratos de interfaces: [contracts/](./contracts/)
