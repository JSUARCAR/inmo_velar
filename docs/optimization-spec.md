# Especificación de Optimización de Filtros Avanzados

## Contexto

Los filtros avanzados de 7 módulos (Personas, Propiedades, Contratos, Liquidaciones, Liquidación de Asesores, Recaudos, Incidentes) presentan problemas de rendimiento que causan bloqueos perceptibles en la UI. El objetivo es lograr resultados **prácticamente instantáneos** sin bloqueo perceptible de la interfaz.

**Volumen actual:** < 10,000 registros por tabla
**Stack:** Reflex (Python) + PostgreSQL
**Restricciones:** Sin restricciones de downtime para migraciones

---

## Problemas Identificados (Priorizados)

### P0: Consultas N+1 (Mayor Impacto)

| Módulo | Ubicación | Problema | Impacto |
|--------|-----------|----------|---------|
| Personas | `servicio_personas.py:116-122, 170-176` | 5 consultas por persona para roles | 125+ consultas/página |
| Liquidaciones | `repositorio_liquidacion_postgres.py:1013-1087` | 2 consultas por grupo (estado liquidación + estado recaudo) | 50+ consultas/página |
| Recaudos | `repositorio_recaudo.py:707-750` | 1 consulta por recaudo para conceptos | 50+ consultas/período |

### P1: Subconsultas Correlacionadas

| Módulo | Ubicación | Problema |
|--------|-----------|----------|
| Propiedades | `repositorio_propiedad_postgres.py:148-157` | Subconsulta DOCUMENTOS por fila |
| Liquidaciones | `repositorio_liquidacion_postgres.py:1568-1574` | Subconsulta ESTADO_RECAUDO correlacionada |
| Incidentes | `repositorio_incidentes_postgres.py:247-265` | JSON_AGG + PLAN_PAGO subconsultas por fila |

### P2: Índices Faltantes

| Tabla | Índice | Propósito |
|-------|--------|-----------|
| LIQUIDACIONES | `(ID_CONTRATO_M, PERIODO, eliminada)` | Consultas filtradas por contrato y período |
| RECAUDO_CONCEPTOS | `(ID_RECAUDO, PERIODO)` | JOINs y filtros por período |
| CONTRATOS_MANDATOS | `(ID_PROPIETARIO, ESTADO_CONTRATO_M)` | Filtro sin_contrato |
| CONTRATOS_ARRENDAMIENTOS | `(ID_PROPIETARIO, ESTADO_CONTRATO_A)` | Filtro sin_contrato |
| DOCUMENTOS | `(ENTIDAD_TIPO, ENTIDAD_ID, ES_VIGENTE)` | Búsqueda de imágenes por entidad |

### P3: Problemas Estructurales

| Problema | Ubicación |
|----------|-----------|
| `sin_contrato` usa 5 subconsultas NOT EXISTS | `repositorio_persona_postgres.py:137-151` |
| `obtener_costos_reparaciones_periodo` carga todos los incidentes | `servicio_incidentes.py:356-374` |
| Contratos sin paginación en listas | `servicio_contratos.py:320-356, 510-546` |
| Duplicación de lógica obtener_todos/contar_todos | `repositorio_persona_postgres.py:77, 181` |

---

## Soluciones Propuestas

### Fase 1: Corregir Consultas N+1

#### 1.1 Personas — Roles con UNION ALL

**Archivo:** `src/infraestructura/persistencia/repositorio_persona_postgres.py`

**Antes (N+1):**
```python
# Después de obtener la página de personas
for persona in personas:
    roles = self._obtener_datos_roles_persona(persona.id_persona)  # 5 queries
```

**Después (1 consulta):**
```python
# Construir una sola consulta que obtenga todos los roles de una vez
query_roles = """
    SELECT 'PROPIETARIO' as ROL, ID_PERSONA, ... FROM PROPIETARIOS WHERE ID_PERSONA = ANY($1)
    UNION ALL
    'ARRENDATARIO', ID_PERSONA, ... FROM ARRENDATARIOS WHERE ID_PERSONA = ANY($1)
    UNION ALL
    'CODEUDOR', ID_PERSONA, ... FROM CODEUDORES WHERE ID_PERSONA = ANY($1)
    UNION ALL
    'ASESOR', ID_PERSONA, ... FROM ASESORES WHERE ID_PERSONA = ANY($1)
    UNION ALL
    'PROVEEDOR', ID_PERSONA, ... FROM PROVEEDORES WHERE ID_PERSONA = ANY($1)
"""
# $1 = array de IDs de personas de la página actual
```

**Resultado:** 125+ consultas → 2 consultas por página

#### 1.2 Liquidaciones — Estados en la Consulta Principal

**Archivo:** `src/infraestructura/persistencia/repositorio_liquidacion_postgres.py`

**Antes (N+1):**
```python
# Línea 1013-1087: Para cada grupo, 2 consultas adicionales
for grupo in grupos:
    estado_liq = query_estado_liquidacion(grupo)  # Query 1
    estado_rec = query_estado_recaudo(grupo)       # Query 2 (4 niveles de subconsulta)
```

**Después (consultas integradas):**
```sql
-- Consulta principal con estados integrados via JOINs
SELECT 
    p.ID_PROPIETARIO,
    l.PERIODO,
    SUM(l.VALOR) as TOTAL,
    -- Estado de liquidación integrado
    CASE 
        WHEN SUM(l.VALOR) = SUM(COALESCE(r.VALOR, 0)) THEN 'PAGADO'
        ELSE 'PENDIENTE'
    END as ESTADO_LIQUIDACION,
    -- Estado de recaudo integrado
    (SELECT rrec.ESTADO_RECAUDO 
     FROM RECAUDOS rrec 
     JOIN RECAUDO_CONCEPTOS rconc ON rconc.ID_RECAUDO = rrec.ID_RECAUDO
     WHERE rconc.ID_CONTRATO_M = l.ID_CONTRATO_M 
       AND rconc.PERIODO = l.PERIODO
     LIMIT 1) as ESTADO_RECAUDO
FROM LIQUIDACIONES l
JOIN PROPIETARIOS p ON p.ID_PROPIETARIO = l.ID_PROPIETARIO
LEFT JOIN RECAUDOS r ON r.ID_CONTRATO_M = l.ID_CONTRATO_M AND r.PERIODO = l.PERIODO
WHERE l.eliminada = FALSE
GROUP BY p.ID_PROPIETARIO, l.PERIODO, l.ID_CONTRATO_M
```

**Resultado:** 50+ consultas → 1-2 consultas por página

#### 1.3 Recaudos — Concepts en Lote

**Archivo:** `src/infraestructura/persistencia/repositorio_recaudo.py`

**Antes (N+1):**
```python
# Línea 707-750
for recaudo in recaudos:
    conceptos = self._obtener_conceptos(recaudo.id_recaudo)  # 1 query por recaudo
```

**Después (batch fetch):**
```python
# Una sola consulta para todos los conceptos de la página
ids_recaudos = [r.id_recaudo for r in recaudos]
query_conceptos = """
    SELECT * FROM RECAUDO_CONCEPTOS 
    WHERE ID_RECAUDO = ANY($1)
    ORDER BY PERIODO
"""
conceptos_map = defaultdict(list)
for c in conceptos:
    conceptos_map[c.id_recaudo].append(c)
```

**Resultado:** 50+ consultas → 1 consulta por página

---

### Fase 2: Índices Faltantes

**Archivo:** `src/infraestructura/persistencia/migraciones/XXXX_optimize_filters.sql`

```sql
-- Migración: Optimización de índices para filtros avanzados
-- Fecha: 2026-07-08
-- Propósito: Acelerar consultas filtradas en módulos principales

-- Liquidaciones: Consultas filtradas por contrato y período
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_liquidaciones_contrato_periodo 
ON LIQUIDACIONES (ID_CONTRATO_M, PERIODO, eliminada);

-- Recaudos de conceptos: JOINs y filtros por período
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_recaudo_conceptos_recaudo_periodo 
ON RECAUDO_CONCEPTOS (ID_RECAUDO, PERIODO);

-- Contratos de mandatos: Filtro sin_contrato
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_contratos_mandatos_propietario_estado 
ON CONTRATOS_MANDATOS (ID_PROPIETARIO, ESTADO_CONTRATO_M);

-- Contratos de arrendamiento: Filtro sin_contrato
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_contratos_arrendamientos_propietario_estado 
ON CONTRATOS_ARRENDAMIENTOS (ID_PROPIETARIO, ESTADO_CONTRATO_A);

-- Documentos: Búsqueda de imágenes por entidad
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_documentos_entidad_imagen 
ON DOCUMENTOS (ENTIDAD_TIPO, ENTIDAD_ID, ES_VIGENTE) 
WHERE MIME_TYPE LIKE 'image/%';

-- Incidentes: Filtros por prioridad y estado
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_incidentes_prioridad_estado 
ON INCIDENTES (PRIORIDAD, ESTADO_INCIDENTE, FECHA_CREACION);

-- Recaudos: Filtros por estado y fecha
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_recaudos_estado_fecha 
ON RECAUDOS (ESTADO_RECAUDO, FECHA_RECAUDO);
```

---

### Fase 3: Subconsultas Correlacionadas

#### 3.1 Propiedades — Imagen con LEFT JOIN LATERAL

**Archivo:** `src/infraestructura/persistencia/repositorio_propiedad_postgres.py`

**Antes (subconsulta por fila):**
```sql
SELECT p.*,
    (SELECT ID FROM DOCUMENTOS d 
     WHERE d.ENTIDAD_TIPO = 'PROPIEDAD' 
     AND d.ENTIDAD_ID = CAST(p.ID_PROPIEDAD AS TEXT) 
     AND d.MIME_TYPE LIKE 'image/%%' 
     AND d.ES_VIGENTE = '1' 
     ORDER BY d.ID ASC LIMIT 1) as IMAGEN_PRINCIPAL_ID
FROM PROPIEDADES p
```

**Después (LEFT JOIN LATERAL):**
```sql
SELECT p.*, img.ID as IMAGEN_PRINCIPAL_ID
FROM PROPIEDADES p
LEFT JOIN LATERAL (
    SELECT d.ID 
    FROM DOCUMENTOS d 
    WHERE d.ENTIDAD_TIPO = 'PROPIEDAD' 
      AND d.ENTIDAD_ID = CAST(p.ID_PROPIEDAD AS TEXT) 
      AND d.MIME_TYPE LIKE 'image/%%' 
      AND d.ES_VIGENTE = '1' 
    ORDER BY d.ID ASC 
    LIMIT 1
) img ON TRUE
```

**Nota:** LEFT JOIN LATERAL es más limpio y permite que PostgreSQL optimice mejor la ejecución.

#### 3.2 Liquidaciones — Estado RECAUDO con JOIN

**Archivo:** `src/infraestructura/persistencia/repositorio_liquidacion_postgres.py`

**Antes (subconsulta correlacionada):**
```sql
(SELECT rrec_sub.ESTADO_RECAUDO
 FROM RECAUDOS rrec_sub
 JOIN RECAUDO_CONCEPTOS rconc_sub ON rconc_sub.ID_RECAUDO = rrec_sub.ID_RECAUDO
 JOIN CONTRATOS_ARRENDAMIENTOS ca_sub ON ca_sub.ID_CONTRATO_A = rrec_sub.ID_CONTRATO_A
 WHERE ca_sub.ID_PROPIEDAD = p.ID_PROPIEDAD
   AND rconc_sub.PERIODO = l.PERIODO
 LIMIT 1) AS ESTADO_RECAUDO
```

**Después (JOIN directo):**
```sql
LEFT JOIN RECAUDOS rrec ON rrec.ID_CONTRATO_A = ca.ID_CONTRATO_A
LEFT JOIN RECAUDO_CONCEPTOS rconc ON rconc.ID_RECAUDO = rrec.ID_RECAUDO
    AND rconc.PERIODO = l.PERIODO
```

#### 3.3 Incidentes — JSON_AGG con LEFT JOIN LATERAL

**Archivo:** `src/infraestructura/persistencia/repositorio_incidentes_postgres.py`

**Antes (2 subconsultas por fila):**
```sql
(JSON_AGG(JSON_BUILD_OBJECT(...)) 
 FROM COTIZACIONES C 
 WHERE C.ID_INCIDENTE = I.ID_INCIDENTE) as COTIZACIONES,
(JSON_BUILD_OBJECT(...) 
 FROM PLAN_PAGO_INCIDENTE PPI 
 WHERE PPI.ID_INCIDENTE = I.ID_INCIDENTE 
 LIMIT 1) as PLAN_PAGO
```

**Después (LEFT JOIN LATERAL + agregación):**
```sql
LEFT JOIN LATERAL (
    SELECT JSON_AGG(JSON_BUILD_OBJECT(...)) as cotizaciones
    FROM COTIZACIONES C 
    WHERE C.ID_INCIDENTE = I.ID_INCIDENTE
) cot ON TRUE
LEFT JOIN LATERAL (
    SELECT JSON_BUILD_OBJECT(...) as plan_pago
    FROM PLAN_PAGO_INCIDENTE PPI 
    WHERE PPI.ID_INCIDENTE = I.ID_INCIDENTE 
    LIMIT 1
) pp ON TRUE
```

---

### Fase 4: Limpieza Estructural

#### 4.1 Filtro sin_contrato — LEFT JOIN + IS NULL

**Archivo:** `src/infraestructura/persistencia/repositorio_persona_postgres.py`

**Antes (5 NOT EXISTS):**
```sql
WHERE 
    NOT EXISTS (SELECT 1 FROM CONTRATOS_MANDATOS cm WHERE cm.ID_PROPIETARIO = p.ID_PERSONA AND cm.ESTADO_CONTRATO_M = 'ACTIVO')
    AND NOT EXISTS (SELECT 1 FROM CONTRATOS_ARRENDAMIENTOS ca WHERE ca.ID_PROPIETARIO = p.ID_PERSONA AND ca.ESTADO_CONTRATO_A = 'ACTIVO')
    AND NOT EXISTS (SELECT 1 FROM CODEUDORES c WHERE c.ID_PERSONA = p.ID_PERSONA AND EXISTS (SELECT 1 FROM CONTRATOS_ARRENDAMIENTOS ca2 WHERE ca2.ID_CODEUDOR = c.ID_CODEUDOR AND ca2.ESTADO_CONTRATO_A = 'ACTIVO'))
    AND NOT EXISTS (SELECT 1 FROM ASESORES a WHERE a.ID_PERSONA = p.ID_PERSONA AND EXISTS (SELECT 1 FROM CONTRATOS_ARRENDAMIENTOS ca3 WHERE ca3.ID_ASESOR = a.ID_ASESOR AND ca3.ESTADO_CONTRATO_A = 'ACTIVO'))
    AND NOT EXISTS (SELECT 1 FROM PROVEEDORES pr WHERE pr.ID_PERSONA = p.ID_PERSONA AND EXISTS (SELECT 1 FROM CONTRATOS_MANDATOS cm2 WHERE cm2.ID_PROVEEDOR = pr.ID_PROVEEDOR AND cm2.ESTADO_CONTRATO_M = 'ACTIVO'))
```

**Después (LEFT JOIN + IS NULL):**
```sql
LEFT JOIN CONTRATOS_MANDATOS cm ON cm.ID_PROPIETARIO = p.ID_PERSONA AND cm.ESTADO_CONTRATO_M = 'ACTIVO'
LEFT JOIN CONTRATOS_ARRENDAMIENTOS ca ON ca.ID_PROPIETARIO = p.ID_PERSONA AND ca.ESTADO_CONTRATO_A = 'ACTIVO'
LEFT JOIN CODEUDORES c ON c.ID_PERSONA = p.ID_PERSONA
LEFT JOIN CONTRATOS_ARRENDAMIENTOS ca2 ON ca2.ID_CODEUDOR = c.ID_CODEUDOR AND ca2.ESTADO_CONTRATO_A = 'ACTIVO'
LEFT JOIN ASESORES a ON a.ID_PERSONA = p.ID_PERSONA
LEFT JOIN CONTRATOS_ARRENDAMIENTOS ca3 ON ca3.ID_ASESOR = a.ID_ASESOR AND ca3.ESTADO_CONTRATO_A = 'ACTIVO'
LEFT JOIN PROVEEDORES pr ON pr.ID_PERSONA = p.ID_PERSONA
LEFT JOIN CONTRATOS_MANDATOS cm2 ON cm2.ID_PROVEEDOR = pr.ID_PROVEEDOR AND cm2.ESTADO_CONTRATO_M = 'ACTIVO'
WHERE cm.ID_PROPIETARIO IS NULL 
  AND ca.ID_PROPIETARIO IS NULL 
  AND ca2.ID_CODEUDOR IS NULL 
  AND ca3.ID_ASESOR IS NULL 
  AND cm2.ID_PROVEEDOR IS NULL
```

#### 4.2 obtener_costos_reparaciones_periodo — SQL SUM()

**Archivo:** `src/aplicacion/servicios/servicio_incidentes.py`

**Antes (carga todos los incidentes):**
```python
def obtener_costos_reparaciones_periodo(self, id_propiedad: int, fecha_inicio: date, fecha_fin: date) -> Decimal:
    incidentes = self.repo_incidentes.listar()  # CARGA TODOS
    total = Decimal('0')
    for inc in incidentes:
        if inc.id_propiedad == id_propiedad:  # Filtra en Python
            if fecha_inicio <= inc.fecha_creacion.date() <= fecha_fin:
                total += inc.costo_reparacion or Decimal('0')
    return total
```

**Después (SQL SUM):**
```python
def obtener_costos_reparaciones_periodo(self, id_propiedad: int, fecha_inicio: date, fecha_fin: date) -> Decimal:
    query = """
        SELECT COALESCE(SUM(COSTO_REPARACION), 0) as TOTAL
        FROM INCIDENTES
        WHERE ID_PROPIEDAD = $1
          AND FECHA_CREACION::DATE BETWEEN $2 AND $3
          AND eliminada = FALSE
    """
    result = self.db.execute_query(query, [id_propiedad, fecha_inicio, fecha_fin])
    return Decimal(str(result[0]['TOTAL']))
```

#### 4.3 Contratos — Añadir Paginación

**Archivos:** `src/aplicacion/servicios/servicio_contratos.py`

Agregar parámetros `limit` y `offset` a `listar_mandatos()` y `listar_arrendamientos()`.

#### 4.4 Deduplicación de Consultas Personas

**Archivo:** `src/infraestructura/persistencia/repositorio_persona_postgres.py`

Refactorizar `obtener_todos()` y `contar_todos()` para usar un método privado `_construir_where_filtros()` compartido.

---

## Impacto Esperado

| Fase | Consultas Eliminadas | Impacto |
|------|---------------------|---------|
| Fase 1 (N+1) | ~175+ consultas/página | **Alto** — Elimina bloqueos perceptibles |
| Fase 2 (Índices) | Reducción de tiempo de ejecución | **Medio** — Consultas más rápidas |
| Fase 3 (Subconsultas) | ~75 subconsultas/página | **Medio-Alto** — Mejora en consultas complejas |
| Fase 4 (Estructural) | Reducción de complejidad | **Bajo-Medio** — Mantenibilidad |

---

## Orden de Implementación

1. **Migración de índices** (Fase 2) — Cambios de BD primero
2. **N+1 Personas** (Fase 1.1) — Mayor impacto
3. **N+1 Liquidaciones** (Fase 1.2) — Segundo mayor impacto
4. **N+1 Recaudos** (Fase 1.3) — Tercer mayor impacto
5. **Subconsultas Propiedades** (Fase 3.1)
6. **Subconsultas Liquidaciones** (Fase 3.2)
7. **Subconsultas Incidentes** (Fase 3.3)
8. **Filtro sin_contrato** (Fase 4.1)
9. **obtener_costos_reparaciones_periodo** (Fase 4.2)
10. **Paginación Contratos** (Fase 4.3)
11. **Deduplicación Personas** (Fase 4.4)

---

## Verificación

Para cada fase, ejecutar:
1. **Pruebas unitarias** existentes (si las hay)
2. **Pruebas de integración** de filtros
3. **Benchmark manual** antes/después con `EXPLAIN ANALYZE`
4. **Verificación visual** en la UI (carga de datos, filtros, paginación)

---

## Riesgos

| Riesgo | Mitigación |
|--------|------------|
| LEFT JOIN LATERAL requiere PostgreSQL 9.3+ | Verificar versión en Railway (ya es 9.3+) |
| Migración de índices puede fallar | Usar IF NOT EXISTS, probar en staging |
| Cambios en consultas pueden alterar resultados | Pruebas comparativas antes/después |
| Refactorización puede introducir regresiones | Cobertura de pruebas existentes |

---

## Aprobación

Este diseño debe ser revisado y aprobado antes de proceder con la implementación.

**Pendiente de aprobación del usuario.**
