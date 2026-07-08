# Research: Corrección GROUP BY en Módulo Incidentes

**Date**: 2026-07-08
**Feature**: 036-fix-incidents-group-by

## R-001: Causa Raíz del Error GROUP BY

**Decision**: Eliminar la cláusula `GROUP BY` redundante de la consulta `listar_con_filtros`.

**Rationale**: El error se origina en el método `listar_con_filtros` del archivo `src/infraestructura/persistencia/repositorio_incidentes_postgres.py` (línea 398).

**Análisis de la Consulta Defectuosa**:

```sql
-- Línea 247: Columna derivada de LATERAL JOIN
COALESCE(cot.cotizaciones, '[]'::json) AS COTIZACIONES_JSON

-- Línea 250-261: LATERAL JOIN que genera la subconsulta 'cot'
LEFT JOIN LATERAL (
    SELECT JSON_AGG(...) as cotizaciones
    FROM COTIZACIONES C 
    WHERE C.ID_INCIDENTE = I.ID_INCIDENTE
) cot ON TRUE

-- Línea 398: GROUP BY que causa el error
GROUP BY I.ID_INCIDENTE, PER_PROV.ID_PERSONA, PROP.ID_PROPIEDAD, 
         PER_PROP.ID_PERSONA, PER_INQ.ID_PERSONA, PER_HAB.ID_PERSONA
```

**Por qué PostgreSQL falla**: La columna `cot.cotizaciones` proviene de una subconsulta derivada (el resultado del `LEFT JOIN LATERAL`). En SQL estándar, toda columna en el `SELECT` que no está en el `GROUP BY` debe estar en una función de agregación. `COALESCE` NO es una función de agregación — es una función ordinaria. Por lo tanto, PostgreSQL exige que `cot.cotizaciones` esté en el `GROUP BY`.

**Por qué el GROUP BY es innecesario**: Los `LEFT JOIN LATERAL` ya manejan la agregación correctamente. Cada fila de `INCIDENTES` produce exactamente una fila del subquery lateral (el resultado de `JSON_AGG`). No hay duplicación de filas, por lo que el `GROUP BY` es redundante y causante del error.

**Alternatives Considered**:
1. Agregar `cot.cotizaciones` al `GROUP BY` — Rechazado: causaría agrupación incorrecta ya que `cotizaciones` es un JSON complejo, no un valor agrupable.
2. Envolver en `MAX(cot.cotizaciones)` — Rechazado:innecesario y adding overhead.
3. **Eliminar el `GROUP BY`** — Seleccionado: solución limpia, respeta la semántica de `LATERAL JOIN`.

## R-002: Alcance del Fix en la Cadena de Datos

**Decision**: El fix se localiza exclusivamente en la capa de repositorio (`repositorio_incidentes_postgres.py`).

**Rationale**: La consulta SQL defectuosa está en el método `listar_con_filtros` del repositorio. El servicio (`servicio_incidentes.py`) y el estado de Reflex (`incidentes_base.py`) delegan correctamente al repositorio. No se requieren cambios en otras capas.

**Mapeo de la Cadena de Datos**:
```
Reflex State (incidentes_base.py)
  └→ Servicio (servicio_incidentes.py:128-155)
      └→ Repositorio (repositorio_incidentes_postgres.py:217-415) ← FIX AQUÍ
          └→ PostgreSQL (consulta SQL)
```

**Alternatives Considered**:
1. Modificar el servicio para pre-procesar datos — Rechazado: innecesario, el problema es puramente SQL.
2. Cambiar la UI para manejar el error — Rechazado: no aborda la causa raíz.

## R-003: Estrategia de Agregación JSON

**Decision**: Mantener `LEFT JOIN LATERAL` con `JSON_AGG` (ya implementado).

**Rationale**: La consulta ya utiliza la estrategia correcta de `LATERAL JOIN` + `JSON_AGG`. El problema no es la estrategia de agregación sino el `GROUP BY` redundante. No se requiere cambiar la estrategia.

**PostgreSQL LATERAL JOIN Behavior**:
- `LATERAL JOIN` permite que la subconsulta referencie columnas de tablas anteriores en el `FROM`.
- El resultado del `LATERAL` es una tabla derivada que produce exactamente una fila por fila de la tabla externa (cuando hay `JSON_AGG`).
- No necesita `GROUP BY` porque la agregación ya ocurrió dentro del subquery lateral.

**Alternatives Considered**:
1. Subconsulta correlacionada (como en `obtener_por_id`) — Ya funciona en ese método, pero `LATERAL` es más eficiente para listados.
2. CTE (Common Table Expression) — Más legible pero innecesario para este caso.

## R-004: Validación de Rendimiento

**Decision**: Usar `EXPLAIN ANALYZE` para validar el plan de ejecución post-fix.

**Rationale**: La constitución del proyecto requiere evidencia técnica objetiva. `EXPLAIN ANALYZE` proporciona:
- Tiempo real de ejecución
- Plan de ejecución (idx scan vs seq scan)
- Costo estimado vs real

**Validación Esperada**:
```sql
EXPLAIN ANALYZE
SELECT I.*, ... COALESCE(cot.cotizaciones, '[]'::json) AS COTIZACIONES_JSON ...
FROM INCIDENTES I
LEFT JOIN LATERAL (...) cot ON TRUE
...
WHERE 1=1
-- Sin GROUP BY
```

**Métricas Objetivo**:
- Tiempo: < 3 segundos para 1000 registros
- Plan: Index Scan en `INCIDENTES` (PK), no Seq Scan
- Sin duplicación de registros

## R-005: Módulos Dependientes para Regresión

**Decision**: Verificar módulos de Liquidaciones y Reportes.

**Rationale**: Estos módulos consumen datos de incidentes y podrían afectarse si la estructura de datos cambia.

**Módulos a Verificar**:
1. **Liquidaciones** (`servicio_incidente_liquidacion.py`): Usa `obtener_por_id` y `listar_con_filtros` para obtener costos de incidentes.
2. **Reportes**: Genera reportes basados en datos de incidentes.

**Criterio de Regresión**: Si los módulos funcionan correctamente antes y después del fix, no hay regresión.

## R-006: Observabilidad en Producción

**Decision**: Log de errores de consulta + tiempo de ejecución al sistema de logging existente.

**Rationale**: El repositorio ya usa `_log = logging.getLogger("RepositorioIncidentes")`. Se puede agregar logging de errores y tiempo de ejecución sin infraestructura nueva.

**Implementación**:
- Log de errores SQL con `_log.error()`
- Log de tiempo de ejecución con `_log.debug()`
- Sin cambios en configuración de logging existente
