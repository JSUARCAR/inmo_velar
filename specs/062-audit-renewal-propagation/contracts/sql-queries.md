# SQL Query Contracts: Auditoría de Propagación de Renovaciones

**Feature**: 062-audit-renewal-propagation
**Date**: 2026-07-22
**Status**: Complete

## Overview

All SQL queries are READ-ONLY. No INSERT, UPDATE, or DELETE operations are permitted.

## Query Contracts

### 1. Get Renovations July 2026

**Purpose**: Fetch all contract renovations from July 2026, keeping only the last per contract.

```sql
-- Get last renovation per contract in July 2026
WITH ultimas_renovaciones AS (
    SELECT 
        r.contrato_id,
        MAX(r.fecha_renovacion) as fecha_ultima_renovacion
    FROM RENOVACIONES_CONTRATOS r
    WHERE r.fecha_renovacion >= '2026-07-01'
      AND r.fecha_renovacion < '2026-08-01'
    GROUP BY r.contrato_id
)
SELECT 
    r.*,
    c.codigo as contrato_codigo,
    c.canon_arrendamiento as canon_actual,
    a.nombre as arrendatario_nombre
FROM RENOVACIONES_CONTRATOS r
INNER JOIN ultimas_renovaciones ur 
    ON r.contrato_id = ur.contrato_id 
    AND r.fecha_renovacion = ur.fecha_ultima_renovacion
INNER JOIN CONTRATOS_ARRENDAMIENTOS c 
    ON r.contrato_id = c.id
LEFT JOIN ARRENDATARIOS a 
    ON c.arrendatario_id = a.id
ORDER BY r.fecha_renovacion DESC;
```

**Expected Result**: List of `RenovacionJulio2026` objects

### 2. Get Future Liquidaciones

**Purpose**: Fetch liquidaciones from today forward for a specific contract.

```sql
-- Get liquidaciones from today forward
SELECT 
    l.id,
    l.contrato_id,
    l.canon_bruto,
    l.fecha,
    l.estado
FROM LIQUIDACIONES l
WHERE l.contrato_id = %s
  AND l.fecha >= CURRENT_DATE
  AND l.estado NOT IN ('Cancelada', 'Reversado')
ORDER BY l.fecha ASC;
```

**Expected Result**: List of liquidaciones for comparison

### 3. Get Future Recaudos

**Purpose**: Fetch recaudos from today forward for a specific contract.

```sql
-- Get recaudos from today forward
SELECT 
    r.id,
    r.contrato_id,
    r.valor_total,
    r.fecha,
    r.estado
FROM RECAUDOS r
WHERE r.contrato_id = %s
  AND r.fecha >= CURRENT_DATE
  AND r.estado NOT IN ('Cancelada', 'Reversado')
ORDER BY r.fecha ASC;
```

**Expected Result**: List of recaudos for comparison

### 4. Get Recaudo Conceptos

**Purpose**: Fetch concept details for a specific recaudo.

```sql
-- Get recaudo conceptos
SELECT 
    rc.id,
    rc.recaudo_id,
    rc.concepto,
    rc.valor
FROM RECAUDO_CONCEPTOS rc
WHERE rc.recaudo_id = %s
  AND rc.concepto = 'Canon';
```

**Expected Result**: Canon concept amount for recaudo

### 5. Get Mandato

**Purpose**: Fetch mandato details for a specific contract.

```sql
-- Get mandato for contract
SELECT 
    m.id,
    m.canon_mandato,
    m.propiedad_id
FROM CONTRATOS_MANDATO m
INNER JOIN CONTRATOS_ARRENDAMIENTOS c 
    ON m.id = c.mandato_id
WHERE c.id = %s;
```

**Expected Result**: Mandato details or NULL if no mandato

### 6. Get Propiedad

**Purpose**: Fetch propiedad details for a specific mandato.

```sql
-- Get propiedad for mandato
SELECT 
    p.id,
    p.canon_arrendamiento_estimado
FROM PROPIEDADES p
WHERE p.id = %s;
```

**Expected Result**: Propiedad details or NULL if no propiedad

### 7. Get Historical Liquidaciones

**Purpose**: Fetch liquidaciones before July 2026 for preservation check.

```sql
-- Get historical liquidaciones before July 2026
SELECT 
    l.id,
    l.contrato_id,
    l.canon_bruto,
    l.fecha,
    l.estado
FROM LIQUIDACIONES l
WHERE l.contrato_id = %s
  AND l.fecha < '2026-07-01'
  AND l.estado NOT IN ('Cancelada', 'Reversado')
ORDER BY l.fecha DESC;
```

**Expected Result**: Historical liquidaciones for verification

### 8. Get Historical Recaudos

**Purpose**: Fetch recaudos before July 2026 for preservation check.

```sql
-- Get historical recaudos before July 2026
SELECT 
    r.id,
    r.contrato_id,
    r.valor_total,
    r.fecha,
    r.estado
FROM RECAUDOS r
WHERE r.contrato_id = %s
  AND r.fecha < '2026-07-01'
  AND r.estado NOT IN ('Cancelada', 'Reversado')
ORDER BY r.fecha DESC;
```

**Expected Result**: Historical recaudos for verification

## Query Validation Rules

1. **No Write Operations**: Queries must not contain INSERT, UPDATE, DELETE, DROP, TRUNCATE, ALTER
2. **Parameterized Queries**: Use `%s` placeholders for all user input
3. **Timeout**: Queries must complete within 30 seconds
4. **Connection**: Use `DATABASE_URL` environment variable

## Error Handling

| Error Code | Description | Action |
|------------|-------------|--------|
| 08001 | Connection failure | Log error, return empty result |
| 08006 | Connection lost | Log error, return partial result |
| 42P01 | Table not found | Log error, skip query |
| 42703 | Column not found | Log error, skip query |
| 57014 | Query cancelled | Log error, skip query |

## Performance Constraints

- Total execution time: < 30 seconds
- Individual query timeout: 10 seconds
- Maximum rows per query: 10,000
- Connection pool: Not required (single execution)
