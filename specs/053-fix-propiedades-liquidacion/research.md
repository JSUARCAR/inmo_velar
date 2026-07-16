# Research: Fix Propiedades a Liquidar

**Date**: 2026-07-13

## R1: Root Cause Analysis — Consulta obtener_activos_por_asesor()

**Decision**: El problema raíz está en el JOIN entre `CONTRATOS_ARRENDAMIENTOS` y `CONTRATOS_MANDATOS` vía `ID_PROPIEDAD`.

**Rationale**: La consulta actual en `repositorio_contrato_arrendamiento_postgres.py` (líneas 107-133) ejecuta:

```sql
SELECT ca.*, cm.COMISION_PORCENTAJE_CONTRATO_M, cm.ID_CONTRATO_M, ...
FROM CONTRATOS_ARRENDAMIENTOS ca
JOIN CONTRATOS_MANDATOS cm ON ca.ID_PROPIEDAD = cm.ID_PROPIEDAD
JOIN PROPIEDADES p ON ca.ID_PROPIEDAD = p.ID_PROPIEDAD
LEFT JOIN ARRENDATARIOS arr ON ca.ID_ARRENDATARIO = arr.ID_ARRENDATARIO
LEFT JOIN SEGUROS seg ON arr.ID_SEGURO = seg.ID_SEGURO
WHERE cm.ID_ASESOR = {id_asesor}
  AND ca.ESTADO_CONTRATO_A = 'ACTIVO'
  AND cm.ESTADO_CONTRATO_M = 'ACTIVO'
```

**Causas probables de exclusión**:
1. **JOIN INNER entre ca y cm**: Si una propiedad tiene CONTRATO_ARRENDAMIENTO activo pero el CONTRATO_MANDATO asociado no está en estado ACTIVO (o no existe), la propiedad se excluye silenciosamente.
2. **Filtro `cm.ID_ASESOR`**: Si el CONTRATO_MANDATOS tiene un ID_ASESOR diferente o NULL, la propiedad se excluye.
3. **JOIN vía ID_PROPIEDAD**: Si hay múltiples CONTRATOS_MANDATOS para la misma propiedad (históricos), el JOIN puede producir duplicados o excluir registros si el mandato activo no es el que se une primero.
4. **Posible problema de datos**: Si existen propiedades con contrato de arrendamiento activo pero sin contrato mandato activo correspondiente, estas se pierden.

**Alternatives considered**:
- Cambiar a LEFT JOIN: No aplica porque necesitamos el mandato para obtener el porcentaje de comisión y el ID del asesor.
- Agregar subquery: Podría resolver el problema de duplicados si hay múltiples mandatos históricos.
- Filtrar por mandato más reciente: Solución óptima para manejar historial.

## R2: Estructura de la tabla LIQUIDACIONES_CONTRATOS

**Decision**: La tabla `LIQUIDACIONES_CONTRATOS` almacena el desglose por contrato de cada liquidación de asesor.

**Rationale**: Esta tabla es el vínculo entre la liquidación consolidada (`LIQUIDACIONES_ASESORES`) y los contratos individuales. Su existencia confirma que el sistema soporta liquidaciones multi-contrato. El problema no está en el almacenamiento sino en la selección inicial de contratos elegibles.

**Alternatives considered**: N/A — la estructura es correcta, el problema está en la consulta de selección.

## R3: Flujo de generación en el frontend (form_state.py)

**Decision**: El frontend llama directamente al repositorio para obtener contratos activos, duplicando la lógica del servicio.

**Rationale**: En `form_state.py` (líneas 461-525), `fetch_advisor_properties()` llama a `servicio.repo_contrato_arrendamiento.obtener_activos_por_asesor(id_asesor)` directamente, en lugar de pasar por un método del servicio. Esto significa que:
1. La lógica de selección está acoplada al repositorio, no al dominio.
2. Cualquier cambio en la consulta del repositorio afecta automáticamente al frontend.
3. El servicio `generar_liquidacion_multi_contrato()` recibe la lista de contratos ya filtrada — no re-valida.

**Alternatives considered**:
- Mover la lógica de selección al servicio: Mejor separación de responsabilidades pero fuera del alcance de este fix.
- Dejar como está: Aceptable para un fix puntual siempre que la consulta del repositorio sea correcta.

## R4: Regla de reincorporación tras eliminación

**Decision**: Al eliminar una liquidación, los contratos vuelven a ser elegibles.

**Rationale**: La tabla `LIQUIDACIONES_CONTRATOS` tiene una FK a `LIQUIDACIONES_ASESORES`. Si se elimina (soft delete) la liquidación padre, los registros hijos en `LIQUIDACIONES_CONTRATOS` quedan huérfanos lógicamente. La consulta de "ya liquidados" debe filtrar por `ELIMINADA = FALSE` en la liquidación padre para permitir la reincorporación.

**Alternatives considered**: N/A — la lógica actual ya usa soft delete (`ELIMINADA = FALSE`), esto es consistente.

## R5: Estados de contrato y reglas de elegibilidad

**Decision**: Solo contratos con `ESTADO_CONTRATO_A = 'ACTIVO'` y `ESTADO_CONTRATO_M = 'ACTIVO'` son elegibles.

**Rationale**: Los 4 estados de contrato son ACTIVO, FINALIZADO, CANCELADO, LEGAL. Solo ACTIVO califica. La consulta actual ya filtra por esto. El problema no está en el filtro de estado sino en el JOIN.

**Alternatives considered**: N/A — los filtros de estado son correctos.

## R6: Período y duplicados

**Decision**: La restricción UNIQUE en `LIQUIDACIONES_ASESORES(ID_ASESOR, PERIODO_LIQUIDACION)` previene duplicados a nivel de BD.

**Rationale**: El servicio verifica duplicados antes de insertar (`obtener_por_asesor_periodo`). Si la liquidación fue eliminada (soft delete), el registro huérfano en LIQUIDACIONES_CONTRATOS no bloquea la creación de una nueva liquidación para el mismo período + asesor.

**Alternatives considered**: N/A — la lógica de duplicados es correcta.
