# Research: Corrección del Estado Recaudo

**Fecha**: 2026-07-11
**Feature**: specs/043-fix-estado-recaudo

## Descubrimientos

### 1. Mapeo de Estados (Decisión)

**Decisión**: Usar los estados reales del sistema: `Pendiente`, `Aplicado`, `Reversado`, `Vencido`

**Razón**: El enum `EstadoRecaudo` en `src/dominio/constantes/recaudo.py` define exactamente estos 4 valores. La spec original mencionaba "Pagado" y "En proceso" que no existen en el sistema.

**Alternativas consideradas**:
- Agregar nuevos estados al enum → Rechazado: fuera del alcance (bug fix, no feature)
- Mapear estados de la spec a estados reales → Rechazado: confuso y propenso a errores

**Mapeo resultado**:
| Spec (original) | Sistema real |
|-----------------|--------------|
| Sin recaudo | Sin Recaudo (default Python) |
| Pendiente | Pendiente |
| Pagado | Aplicado |
| Reversado | Reversado |
| En proceso | Vencido |

### 2. Causa Raíz de Inconsistencias (Decisión)

**Decisión**: Corregir las subqueries SQL para:
1. Filtrar recaudos con estado `Reversado`
2. Ordenar por `FECHA_PAGO DESC` (más reciente primero)
3. Aplicar `LIMIT 1` después del filtro y orden

**Razón**: El `LIMIT 1` sin `ORDER BY` y sin filtro de estado es la causa raíz. El recaudo retornado puede ser:
- De otro período (falta filtro estricto)
- Reversado (falta filtro de estado)
- El más antiguo en lugar del más reciente (falta ORDER BY)

**Alternativas consideradas**:
- Agregar campo `vigente` boolean → Rechazado: requiere migración de BD
- Usar `MAX(fecha_pago)` en subquery → Rechazado: menos eficiente que ORDER BY + LIMIT 1
- Mover lógica a Python (post-query) → Rechazado: ineficiente para tablas grandes

### 3. Archivos Afectados (Decisión)

**Decisión**: Modificar 3 archivos principales:

| Archivo | Cambio |
|---------|--------|
| `repositorio_liquidacion_postgres.py` | Corregir subquery en `listar_paginado()` y `_obtener_estados_recaudo_por_grupos()` |
| `repositorio_recaudo.py` | Verificar consistencia en `obtener_estado_pago_actual()` |
| `liquidaciones_state.py` | Ajustar mapeo de estados si es necesario |

**Razón**: La lógica de cálculo del estado recaudo está concentrada en el repositorio de liquidaciones.

**Alternativas consideradas**:
- Crear servicio dedicado → Rechazado: over-engineering para un fix
- Modificar solo la UI → Rechazado: no resuelve la causa raíz

### 4. Estrategia de Pruebas (Decisión)

**Decisión**: Pruebas de regresión manual + verificación de queries

**Razón**: El proyecto no tiene suite de tests automatizados para esta funcionalidad específica.

**Plan**:
1. Verificar queries SQL directamente en PostgreSQL
2. Probar los 6 escenarios de la spec en la UI
3. Confirmar que otros módulos no se afectan

## Resumen de Cambios

### Cambio 1: Subquery Individual (`listar_paginado`)

**Antes**:
```sql
(SELECT rrec_sub.ESTADO_RECAUDO
 FROM RECAUDOS rrec_sub
 JOIN RECAUDO_CONCEPTOS rconc_sub ON rconc_sub.ID_RECAUDO = rrec_sub.ID_RECAUDO
 JOIN CONTRATOS_ARRENDAMIENTOS ca_sub ON ca_sub.ID_CONTRATO_A = rrec_sub.ID_CONTRATO_A
 WHERE ca_sub.ID_PROPIEDAD = p.ID_PROPIEDAD
   AND rconc_sub.PERIODO = l.PERIODO
 LIMIT 1) AS ESTADO_RECAUDO
```

**Después**:
```sql
(SELECT rrec_sub.ESTADO_RECAUDO
 FROM RECAUDOS rrec_sub
 JOIN RECAUDO_CONCEPTOS rconc_sub ON rconc_sub.ID_RECAUDO = rrec_sub.ID_RECAUDO
 JOIN CONTRATOS_ARRENDAMIENTOS ca_sub ON ca_sub.ID_CONTRATO_A = rrec_sub.ID_CONTRATO_A
 WHERE ca_sub.ID_PROPIEDAD = p.ID_PROPIEDAD
   AND rconc_sub.PERIODO = l.PERIODO
   AND rrec_sub.ESTADO_RECAUDO != 'Reversado'
 ORDER BY rrec_sub.FECHA_PAGO DESC
 LIMIT 1) AS ESTADO_RECAUDO
```

### Cambio 2: Batch Query (`_obtener_estados_recaudo_por_grupos`)

Mismo patrón: agregar filtro `!= 'Reversado'` y `ORDER BY FECHA_PAGO DESC` en la subquery batch.

### Cambio 3: Python Default

Mantener `"Sin Recaudo"` como default cuando la subquery retorna NULL (ya implementado correctamente).
