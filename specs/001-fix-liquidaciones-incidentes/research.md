# Research: Corrección de Selección de Incidentes en Liquidaciones

**Date**: 2026-07-06

## Problema Identificado

### Root Cause Analysis

El bug principal se encuentra en el método `open_seleccion_incidentes_modal` en `liquidaciones_state.py` (líneas 1933-2049).

**Consulta SQL Actual (INCORRECTA):**
```sql
SELECT i.ID_INCIDENTE, i.DESCRIPCION_INCIDENTE, i.COSTO_INCIDENTE,
       i.ESTADO, i.ESTADO_PAGO,
       p.DIRECCION_PROPIEDAD as PROPIEDAD,
       per.NOMBRE_COMPLETO as PROPIETARIO
FROM INCIDENTES i
LEFT JOIN PROPIEDADES p ON i.ID_PROPIEDAD = p.ID_PROPIEDAD
LEFT JOIN CONTRATOS_MANDATOS cm ON (
    i.ID_CONTRATO_M = cm.ID_CONTRATO_M
    OR (i.ID_CONTRATO_M IS NULL AND i.ID_PROPIEDAD = cm.ID_PROPIEDAD AND cm.ESTADO_CONTRATO_M = 'ACTIVO')
)
LEFT JOIN PROPIETARIOS prop ON cm.ID_PROPIETARIO = prop.ID_PROPIETARIO
LEFT JOIN PERSONAS per ON prop.ID_PERSONA = per.ID_PERSONA
WHERE i.ESTADO IN ('Aprobado', 'En Reparacion', 'Finalizado')
  AND i.ESTADO_PAGO != 'Pagado'
ORDER BY i.ID_INCIDENTE DESC
```

**Problema**: La consulta NO filtra por `ID_PROPIEDAD` de la liquidación. Retorna TODOS los incidentes elegibles del sistema.

### Consulta Corregida (PROPUESTA)

```sql
SELECT i.ID_INCIDENTE, i.DESCRIPCION_INCIDENTE, i.COSTO_INCIDENTE,
       i.ESTADO, i.ESTADO_PAGO,
       p.DIRECCION_PROPIEDAD as PROPIEDAD,
       per.NOMBRE_COMPLETO as PROPIETARIO
FROM INCIDENTES i
LEFT JOIN PROPIEDADES p ON i.ID_PROPIEDAD = p.ID_PROPIEDAD
LEFT JOIN CONTRATOS_MANDATOS cm ON (
    i.ID_CONTRATO_M = cm.ID_CONTRATO_M
    OR (i.ID_CONTRATO_M IS NULL AND i.ID_PROPIEDAD = cm.ID_PROPIEDAD AND cm.ESTADO_CONTRATO_M = 'ACTIVO')
)
LEFT JOIN PROPIETARIOS prop ON cm.ID_PROPIETARIO = prop.ID_PROPIETARIO
LEFT JOIN PERSONAS per ON prop.ID_PERSONA = per.ID_PERSONA
WHERE i.ESTADO IN ('Aprobado', 'En Reparacion', 'Finalizado')
  AND i.ESTADO_PAGO != 'Pagado'
  AND i.ID_PROPIEDAD = %s  -- FILTRO POR PROPIEDAD DE LA LIQUIDACIÓN
ORDER BY i.ID_INCIDENTE DESC
```

## Decisiones de Investigación

### D1: Obtención de ID_PROPIEDAD desde la Liquidación

**Decisión**: Obtener el `ID_PROPIEDAD` a través del `ID_CONTRATO_M` almacenado en la liquidación.

**Rationale**: La liquidación tiene un campo `id_contrato_m` que referencia el contrato de mandato. El contrato tiene el `ID_PROPIEDAD`. Esta es la forma más directa y confiable.

**Alternativas Consideradas**:
1. Almacenar `ID_PROPIEDAD` directamente en la liquidación (requiere migración)
2. Usar una subquery para obtener la propiedad desde el contrato (más complejo)
3. **Elegido**: JOIN con CONTRATOS_MANDATOS para obtener ID_PROPIEDAD

### D2: Manejo de Datos en Formulario de Edición

**Decisión**: El campo `valor_incidentes` ya se carga correctamente en `open_edit_modal` (línea 630). El problema es que el usuario no puede ver los incidentes asociados, solo el valor total.

**Rationale**: El valor total de incidentes ya se carga. Para mostrar el detalle de incidentes, se necesitaría una función adicional que liste los incidentes asociados.

**Alternativas Consideradas**:
1. Agregar un campo de solo lectura que muestre los IDs de incidentes asociados
2. Mostrar un contador de incidentes asociados
3. **Elegido**: Mantener el valor actual y agregar funcionalidad futura si se requiere

### D3: Estrategia de Edición Concurrente

**Decisión**: Implementar "Última escritura con notificación" según especificación.

**Rationale**: Estrategia simple que balancea usabilidad con integridad de datos.

**Alternativas Consideradas**:
1. Bloqueo pesimista (complicado de implementar en Reflex)
2. Merge automático (complejo y propenso a errores)
3. **Elegido**: Última escritura con notificación

## Hallazgos Adicionales

### E1: El campo Observaciones SÍ se carga

En `open_edit_modal` (línea 629):
```python
"observaciones": str(liquidacion.get("observaciones", "")),
```

El campo `observaciones` ya se carga correctamente desde la base de datos.

### E2: El campo Incidentes muestra valor total

En `open_edit_modal` (línea 630):
```python
"valor_incidentes": str(liquidacion.get("valor_incidentes", 0)),
```

El campo `valor_incidentes` muestra el valor total, no el detalle de incidentes.

### E3: Relación 1:N confirmada

La tabla `INCIDENTE_LIQUIDACION` almacena la relación entre incidentes y liquidaciones, confirmando la cardinalidad 1:N (una liquidación puede tener múltiples incidentes).

## Resumen de Cambios Requeridos

| Archivo | Cambio | Prioridad |
|---------|--------|-----------|
| `liquidaciones_state.py` | Agregar filtro `ID_PROPIEDAD` a consulta SQL | Crítico |
| `liquidaciones_state.py` | Obtener `ID_PROPIEDAD` desde contrato | Crítico |
| `liquidacion_edit_form.py` | Verificar carga de campos existentes | Medio |
| `modal_seleccion_incidentes.py` | Sin cambios requeridos | Bajo |