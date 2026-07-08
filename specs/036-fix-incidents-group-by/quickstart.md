# Quickstart: Validación de Corrección GROUP BY

**Date**: 2026-07-08
**Feature**: 036-fix-incidents-group-by

## Prerrequisitos

- PostgreSQL accesible (producción o staging)
- Python 3.11+ con dependencias instaladas
- Acceso al repositorio del proyecto

## Escenarios de Validación

### EV-001: Carga del Módulo Incidentes (Functional)

**Objetivo**: Verificar que el módulo carga sin errores de GROUP BY.

**Pasos**:
1. Navegar a la aplicación web
2. Login con credenciales válidas
3. Navegar al módulo Incidentes
4. Verificar que la lista de incidentes se muestra correctamente

**Resultado esperado**: La lista carga sin errores. Se muestran incidentes con sus cotizaciones asociadas.

**Comando de verificación SQL**:
```sql
-- Ejecutar directamente en PostgreSQL para validar la consulta
EXPLAIN ANALYZE
SELECT I.*, 
    COALESCE(cot.cotizaciones, '[]'::json) AS COTIZACIONES_JSON,
    pp.plan_pago AS PLAN_PAGO_JSON
FROM INCIDENTES I
LEFT JOIN LATERAL (
    SELECT JSON_AGG(
        JSON_BUILD_OBJECT(
            'id_cotizacion', C.ID_COTIZACION,
            'id_proveedor', C.ID_PROVEEDOR,
            'valor_total', C.VALOR_TOTAL,
            'estado', C.ESTADO_COTIZACION
        ) ORDER BY C.FECHA_COTIZACION DESC
    ) as cotizaciones
    FROM COTIZACIONES C 
    WHERE C.ID_INCIDENTE = I.ID_INCIDENTE
) cot ON TRUE
LEFT JOIN LATERAL (
    SELECT JSON_BUILD_OBJECT(
        'id_plan_pago', PPI.ID_PLAN_PAGO,
        'num_cuotas', PPI.NUM_CUOTAS,
        'valor_cuota', PPI.VALOR_CUOTA,
        'total_plan', PPI.TOTAL_PLAN,
        'estado', PPI.ESTADO
    ) as plan_pago
    FROM PLAN_PAGO_INCIDENTE PPI 
    WHERE PPI.ID_INCIDENTE = I.ID_INCIDENTE 
      AND PPI.ESTADO = 'Activo' 
    LIMIT 1
) pp ON TRUE
WHERE 1=1
-- SIN GROUP BY
ORDER BY I.FECHA_INCIDENTE DESC
LIMIT 100;
```

**Criterio de éxito**: La consulta retorna resultados sin errores. `EXPLAIN ANALYZE` muestra Index Scan en INCIDENTES.

---

### EV-002: Incidentes con Múltiples Cotizaciones (Data Integrity)

**Objetivo**: Verificar que no hay duplicación de registros.

**Pasos**:
1. Identificar un incidente con múltiples cotizaciones (≥ 3)
2. Cargar el módulo y localizar ese incidente
3. Verificar que aparece una sola vez en la lista
4. Verificar que todas sus cotizaciones se muestran en el JSON

**Comando de verificación SQL**:
```sql
-- Contar cotizaciones por incidente
SELECT I.ID_INCIDENTE, COUNT(C.ID_COTIZACION) as num_cotizaciones
FROM INCIDENTES I
LEFT JOIN COTIZACIONES C ON I.ID_INCIDENTE = C.ID_INCIDENTE
GROUP BY I.ID_INCIDENTE
HAVING COUNT(C.ID_COTIZACION) > 1
ORDER BY num_cotizaciones DESC
LIMIT 5;
```

**Criterio de éxito**: El incidente aparece exactamente una vez. El JSON contiene todas las cotizaciones.

---

### EV-003: Incidentes sin Cotizaciones (Edge Case)

**Objetivo**: Verificar manejo correcto de array vacío.

**Pasos**:
1. Identificar un incidente sin cotizaciones asociadas
2. Cargar el módulo y localizar ese incidente
3. Verificar que el campo cotizaciones muestra `[]` (array vacío)

**Comando de verificación SQL**:
```sql
-- Incidentes sin cotizaciones
SELECT I.ID_INCIDENTE, COUNT(C.ID_COTIZACION) as num_cotizaciones
FROM INCIDENTES I
LEFT JOIN COTIZACIONES C ON I.ID_INCIDENTE = C.ID_INCIDENTE
WHERE C.ID_COTIZACION IS NULL
LIMIT 5;
```

**Criterio de éxito**: El incidente aparece con `cotizaciones: []`, no `null` o dato faltante.

---

### EV-004: Rendimiento (Performance)

**Objetivo**: Verificar que la consulta cumple el objetivo de < 3 segundos.

**Pasos**:
1. Ejecutar `EXPLAIN ANALYZE` en la consulta completa
2. Verificar el tiempo total de ejecución
3. Verificar que no hay Sequential Scans en tablas grandes

**Comando**:
```sql
EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)
SELECT ...
FROM INCIDENTES I
LEFT JOIN LATERAL ... cot ON TRUE
LEFT JOIN LATERAL ... pp ON TRUE
WHERE 1=1
ORDER BY I.FECHA_INCIDENTE DESC;
```

**Criterio de éxito**:
- Tiempo total < 3000ms
- Seq Scan en INCIDENTES: NO (debe ser Index Scan)
- Seq Scan en COTIZACIONES: Puede existir si no hay índice en ID_INCIDENTE

---

### EV-005: Regresión en Liquidaciones (Regression)

**Objetivo**: Verificar que el módulo de Liquidaciones no se afecta.

**Pasos**:
1. Navegar al módulo Liquidaciones
2. Verificar que la lista carga correctamente
3. Verificar que los datos de incidentes se muestran bien

**Criterio de éxito**: Liquidaciones funciona sin errores.

---

### EV-006: Regresión en Reportes (Regression)

**Objetivo**: Verificar que los reportes no se afectan.

**Pasos**:
1. Generar un reporte que incluya datos de incidentes
2. Verificar que los datos son correctos

**Criterio de éxito**: Los reportes generan correctamente.

## Comandos de Ejecución

```bash
# 1. Ejecutar tests existentes
python -m pytest tests/ -v

# 2. Verificar sintaxis del código
python -m ruff check src/infraestructura/persistencia/repositorio_incidentes_postgres.py
python -m mypy src/infraestructura/persistencia/repositorio_incidentes_postgres.py

# 3. Ejecutar servidor en modo debug
reflex run --env dev

# 4. Ejecutar validación SQL directa
psql -U <usuario> -d <base_datos> -f specs/036-fix-incidents-group-by/validacion.sql
```
