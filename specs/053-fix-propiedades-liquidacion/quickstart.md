# Quickstart: Validación Fix Propiedades a Liquidar

**Date**: 2026-07-13

## Prerequisites

- PostgreSQL corriendo con datos de prueba
- Aplicación Reflex en modo dev (`reflex run --env dev`)
- Asesor CRISTIAN JAMIOY con 46 propiedades activas en BD

## Validación 1: Consulta SQL directa (Backend)

```sql
-- Contar propiedades elegibles para CRISTIAN JAMIOY
SELECT COUNT(DISTINCT ca.ID_CONTRATO_A) as total_elegibles
FROM CONTRATOS_ARRENDAMIENTOS ca
JOIN CONTRATOS_MANDATOS cm ON ca.ID_PROPIEDAD = cm.ID_PROPIEDAD
    AND cm.ESTADO_CONTRATO_M = 'ACTIVO'
JOIN ASESORES a ON cm.ID_ASESOR = a.ID_ASESOR
JOIN PERSONAS per ON a.ID_PERSONA = per.ID_PERSONA
WHERE per.NOMBRE_COMPLETO ILIKE '%CRISTIAN%JAMIOY%'
  AND ca.ESTADO_CONTRATO_A = 'ACTIVO';
```

**Expected**: 46 registros

## Validación 2: Generación de Liquidación Individual

1. Navegar a `/liquidacion-asesores`
2. Hacer clic en "+" (Nueva Liquidación)
3. Seleccionar asesor: CRISTIAN JAMIOY
4. Verificar que la tabla de "Propiedades a Liquidar" muestre 46 propiedades
5. Establecer período: 2026-07
6. Guardar la liquidación
7. Verificar en la grilla que la liquidación aparece con los montos correctos

## Validación 3: Asesor con único contrato

1. Seleccionar un asesor con 1 sola propiedad activa
2. Verificar que se muestra exactamente 1 propiedad
3. Generar liquidación y verificar montos

## Validación 4: Asesor con contratos mixtos

1. Seleccionar un asesor con contratos activos e inactivos
2. Verificar que solo se muestran los activos
3. Contar vs. consulta SQL directa

## Validación 5: Contratos ya liquidados

1. Generar una liquidación para un asesor en un período
2. Intentar generar otra liquidación para el mismo asesor y período
3. Verificar que el sistema muestra error "Ya existe liquidación para este período"
4. Eliminar la primera liquidación
5. Generar nueva liquidación para el mismo período
6. Verificar que los contratos vuelven a estar disponibles

## Validación 6: Consistencia Backend-UI

1. Generar liquidación para CRISTIAN JAMIOY (2026-07)
2. Abrir detalle de la liquidación
3. Contar propiedades mostradas en UI
4. Ejecutar consulta SQL:
```sql
SELECT COUNT(*) FROM LIQUIDACIONES_CONTRATOS lc
JOIN LIQUIDACIONES_ASESORES la ON lc.ID_LIQUIDACION_ASESOR = la.ID_LIQUIDACION_ASESOR
JOIN ASESORES a ON la.ID_ASESOR = a.ID_ASESOR
JOIN PERSONAS per ON a.ID_PERSONA = per.ID_PERSONA
WHERE per.NOMBRE_COMPLETO ILIKE '%CRISTIAN%JAMIOY%'
  AND la.PERIODO_LIQUIDACION = '2026-07'
  AND la.ELIMINADA = FALSE;
```
5. Verificar que los conteos coinciden exactamente

## Validación 7: Generación Masiva

1. Hacer clic en "Generar Liquidaciones Masivas"
2. Establecer período: 2026-07
3. Verificar que todos los asesores con contratos activos reciben liquidaciones
4. Verificar que cada liquidación incluye la cantidad correcta de propiedades

## Checklist de Regresión

- [ ] Liquidaciones de propietarios siguen funcionando correctamente
- [ ] Edición de liquidaciones de asesores funciona (estado Pendiente)
- [ ] Aprobación de liquidaciones funciona
- [ ] Eliminación de liquidaciones funciona (soft delete)
- [ ] Reversión de liquidaciones funciona
- [ ] Descuento de PDF funciona
- [ ] Filtros de búsqueda y paginación funcionan
- [ ] Incidentes asociados a liquidaciones se mantienen
