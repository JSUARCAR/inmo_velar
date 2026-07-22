# SQL Queries Contract: Corrección de Propagación de Canon en Renovaciones

**Date**: 2026-07-22
**Feature**: 063-fix-canon-propagation

## Queries de Actualización

### Q1: Actualizar canon_bruto en LIQUIDACIONES futuras

```sql
UPDATE LIQUIDACIONES
SET canon_bruto = %s
WHERE id_contrato_m = (
    SELECT id_contrato_m FROM CONTRATOS_MANDATOS
    WHERE id_contrato_a = %s LIMIT 1
)
AND fecha_generacion::date > %s;
```

**Parámetros**: (canon_nuevo, contrato_id, fecha_renovacion)
**Retorna**: Número de registros actualizados

### Q2: Actualizar valor_total en RECAUDOS futuros

```sql
UPDATE RECAUDOS
SET valor_total = %s
WHERE id_contrato_a = %s
AND fecha_pago::date > %s;
```

**Parámetros**: (canon_nuevo, contrato_id, fecha_renovacion)
**Retorna**: Número de registros actualizados

## Queries de Consulta

### Q3: Obtener liquidaciones futuras de un contrato

```sql
SELECT
    l.id_liquidacion,
    l.id_contrato_m,
    l.canon_bruto,
    l.fecha_generacion
FROM LIQUIDACIONES l
WHERE l.id_contrato_m = (
    SELECT id_contrato_m FROM CONTRATOS_MANDATOS
    WHERE id_contrato_a = %s LIMIT 1
)
AND l.fecha_generacion::date > %s
ORDER BY l.fecha_generacion;
```

**Parámetros**: (contrato_id, fecha_renovacion)
**Retorna**: Lista de liquidaciones futuras

### Q4: Obtener recaudos futuros de un contrato

```sql
SELECT
    r.id_recaudo,
    r.id_contrato_a,
    r.valor_total,
    r.fecha_pago
FROM RECAUDOS r
WHERE r.id_contrato_a = %s
AND r.fecha_pago::date > %s
ORDER BY r.fecha_pago;
```

**Parámetros**: (contrato_id, fecha_renovacion)
**Retorna**: Lista de recaudos futuros

## Queries de Verificación

### Q5: Verificar integridad de liquidaciones

```sql
SELECT
    l.id_liquidacion,
    l.canon_bruto,
    c.canon_arrendamiento
FROM LIQUIDACIONES l
JOIN CONTRATOS_MANDATOS cm ON l.id_contrato_m = cm.id_contrato_m
JOIN CONTRATOS_ARRENDAMIENTOS c ON cm.id_contrato_a = c.id_contrato_a
WHERE c.id_contrato_a = %s
AND l.canon_bruto != c.canon_arrendamiento
AND l.fecha_generacion::date > %s;
```

**Parámetros**: (contrato_id, fecha_renovacion)
**Retorna**: Lista de inconsistencias

### Q6: Verificar integridad de recaudos

```sql
SELECT
    r.id_recaudo,
    r.valor_total,
    c.canon_arrendamiento
FROM RECAUDOS r
JOIN CONTRATOS_ARRENDAMIENTOS c ON r.id_contrato_a = c.id_contrato_a
WHERE c.id_contrato_a = %s
AND r.valor_total != c.canon_arrendamiento
AND r.fecha_pago::date > %s;
```

**Parámetros**: (contrato_id, fecha_renovacion)
**Retorna**: Lista de inconsistencias

## Queries de Auditoría

### Q7: Registrar actualización en log de auditoría

```sql
INSERT INTO AUDITORIA_PROPAGACION_CANON (
    contrato_id,
    tabla_afectada,
    registro_id,
    canon_anterior,
    canon_nuevo,
    fecha_actualizacion,
    usuario_sistema
) VALUES (%s, %s, %s, %s, %s, NOW(), %s);
```

**Parámetros**: (contrato_id, tabla, registro_id, canon_anterior, canon_nuevo, usuario)
**Retorna**: ID del registro de auditoría

## Notas de Implementación

1. Todas las queries usan `%s` como placeholder (PostgreSQL)
2. Las comparaciones de fecha usan `::date` para casting explícito
3. Las queries de actualización deben ejecutarse en una transacción atómica
4. El orden de actualización es: LIQUIDACIONES primero, RECAUDOS segundo
5. Si alguna query falla, se ejecuta ROLLBACK completo
