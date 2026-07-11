# Quickstart Validation: Corrección del Estado Recaudo

**Fecha**: 2026-07-11
**Feature**: specs/043-fix-estado-recaudo

## Prerrequisitos

- PostgreSQL corriendo con datos de prueba
- Aplicación Reflex en modo desarrollo (`reflex run --env dev`)
- Acceso a la UI de liquidaciones

## Escenarios de Validación

### CP-001: Liquidación sin Recaudo

**Preparación**:
```sql
-- Verificar que NO existan recaudos para el período de prueba
SELECT * FROM RECAUDO_CONCEPTOS rc
JOIN RECAUDOS r ON rc.ID_RECAUDO = r.ID_RECAUDO
WHERE rc.PERIODO = '2026-05' AND r.ESTADO_RECAUDO != 'Reversado';
-- Debe retornar 0 filas
```

**Pasos**:
1. Navegar a Liquidaciones
2. Filtrar por período mayo 2026
3. Observar columna "Estado Recaudo"

**Resultado esperado**: Badge gris con texto "Sin Recaudo"

---

### CP-002: Liquidación con Recaudo Reversado Único

**Preparación**:
```sql
-- Verificar que solo exista un recaudo reversado para el período
SELECT r.ESTADO_RECAUDO, COUNT(*)
FROM RECAUDOS r
JOIN RECAUDO_CONCEPTOS rc ON rc.ID_RECAUDO = r.ID_RECAUDO
WHERE rc.PERIODO = '2026-06'
GROUP BY r.ESTADO_RECAUDO;
-- Debe mostrar: Reversado: 1
```

**Pasos**:
1. Navegar a Liquidaciones
2. Filtrar por período junio 2026
3. Observar columna "Estado Recaudo"

**Resultado esperado**: Badge rojo con texto "Reversado"

---

### CP-003: Recaudo Reversado + Nuevo Válido

**Preparación**:
```sql
-- Verificar: 1 reversado + 1 pendiente/aplicado para el mismo período
SELECT r.ESTADO_RECAUDO, COUNT(*)
FROM RECAUDOS r
JOIN RECAUDO_CONCEPTOS rc ON rc.ID_RECAUDO = r.ID_RECAUDO
WHERE rc.PERIODO = '2026-07'
GROUP BY r.ESTADO_RECAUDO;
-- Debe mostrar: Reversado: 1, Pendiente: 1 (o Aplicado: 1)
```

**Pasos**:
1. Navegar a Liquidaciones
2. Filtrar por período julio 2026
3. Observar columna "Estado Recaudo"

**Resultado esperado**: Badge amarillo (Pendiente) o verde (Aplicado), **NO** rojo (Reversado)

---

### CP-004: Múltiples Recaudos Válidos

**Preparación**:
```sql
-- Verificar: 2+ recaudos no-reversados para el mismo período
SELECT r.ESTADO_RECAUDO, r.FECHA_PAGO
FROM RECAUDOS r
JOIN RECAUDO_CONCEPTOS rc ON rc.ID_RECAUDO = r.ID_RECAUDO
WHERE rc.PERIODO = '2026-08' AND r.ESTADO_RECAUDO != 'Reversado'
ORDER BY r.FECHA_PAGO DESC;
-- Debe mostrar 2+ filas, la primera es el vigente
```

**Pasos**:
1. Navegar a Liquidaciones
2. Filtrar por período agosto 2026
3. Observar columna "Estado Recaudo"

**Resultado esperado**: Badge del estado del recaudo **más reciente** (según FECHA_PAGO)

---

### CP-005: Recaudo de Período Diferente

**Preparación**:
```sql
-- Verificar: recaudo existe pero para OTRO período
SELECT * FROM RECAUDO_CONCEPTOS rc
WHERE rc.PERIODO = '2026-10'; -- período diferente al de la liquidación
```

**Pasos**:
1. Navegar a Liquidaciones
2. Filtrar por período septiembre 2026
3. Observar columna "Estado Recaudo"

**Resultado esperado**: Badge gris con texto "Sin Recaudo" (ignora recaudo de octubre)

---

### CP-006: Consistencia UI vs PostgreSQL

**Pasos**:
1. Ejecutar query manual en PostgreSQL para obtener estado recaudo de una liquidación
2. Comparar con lo mostrado en la UI
3. Repetir para 5 liquidaciones diferentes

**Resultado esperado**: 100% de coincidencia entre query y UI

---

## Comandos de Verificación Rápida

```sql
-- Contar recaudos por estado para un período específico
SELECT r.ESTADO_RECAUDO, COUNT(*)
FROM RECAUDOS r
JOIN RECAUDO_CONCEPTOS rc ON rc.ID_RECAUDO = r.ID_RECAUDO
WHERE rc.PERIODO = '2026-MM'  -- Reemplazar MM
GROUP BY r.ESTADO_RECAUDO;

-- Verificar el recaudo vigente (más reciente no-reversado)
SELECT r.*
FROM RECAUDOS r
JOIN RECAUDO_CONCEPTOS rc ON rc.ID_RECAUDO = r.ID_RECAUDO
WHERE rc.PERIODO = '2026-MM'  -- Reemplazar MM
  AND r.ESTADO_RECAUDO != 'Reversado'
ORDER BY r.FECHA_PAGO DESC
LIMIT 1;
```

## Criterios de Aprobación

- [ ] CP-001 a CP-006 pasan exitosamente
- [ ] No hay errores en consola del navegador
- [ ] No hay errores en logs de la aplicación
- [ ] Otros módulos (Recaudos, Contratos) funcionan normalmente
