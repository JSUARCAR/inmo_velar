# Research: Corrección de Propagación de Canon en Renovaciones

**Date**: 2026-07-22
**Feature**: 063-fix-canon-propagation

## Decision Log

### D1: Módulos objetivo para propagación

**Decision**: Solo Liquidación de Propietarios y Recaudos

**Rationale**: La auditoría 062-audit-renewal-propagation verificó que Mandatos y Propiedades ya se propagan correctamente durante la renovación. El problema está aislado a Liquidaciones y Recaudos.

**Alternatives considered**:
- Incluir Mandatos/Propiedades: Rechazado porque ya funcionan correctamente
- Todos los módulos dependientes: Rechazado porque sería redundante

### D2: Campo a actualizar en LIQUIDACIONES

**Decision**: `canon_bruto`

**Rationale**: El campo `canon_bruto` en la tabla LIQUIDACIONES almacena el valor del canon de arrendamiento para cada período de liquidación. Es el campo que alimenta los cálculos financieros para el propietario.

**Alternatives considered**:
- `valor_total`: Rechazado porque incluye otros conceptos (comisiones, descuentos)
- Todos los campos monetarios: Rechazado porque solo `canon_bruto` corresponde al canon del contrato

### D3: Campo a actualizar en RECAUDOS

**Decision**: `valor_total`

**Rationale**: El campo `valor_total` en la tabla RECAUDOS representa el monto total a cobrar/pagar para el recaudo. Es el valor que se compara con el canon del contrato para verificar consistencia.

**Alternatives considered**:
- `canon_arrendamiento`: Rechazado porque puede no existir en todos los registros
- Ambos campos: Rechazado porque `valor_total` es suficiente para la verificación

### D4: Definición de "registro futuro"

**Decision**: Registros con `fecha_generacion` > fecha_renovacion del contrato

**Rationale**: Esta definición utiliza un criterio temporal claro y no ambiguo. Un registro es "futuro" si fue generado después de la fecha en que se aplicó la renovación del contrato.

**Alternatives considered**:
- Estado "pendiente": Rechazado porque un registro pagado podría haberse generado después de la renovación
- Ambos (fecha + estado): Rechazado porque la fecha es suficiente y más preciso

### D5: Estrategia de recuperación ante fallos

**Decision**: Rollback completo de la transacción

**Rationale**: Si la propagación falla parcialmente, es preferible revertir todos los cambios para mantener la consistencia de datos. Un estado parcial podría causar discrepancias financieras difíciles de diagnosticar.

**Alternatives considered**:
- Logging y continuar: Rechazado porque dejaría registros en estado inconsistente
- Reintentar automáticamente: Rechazado como estrategia primaria (puede ser complementaria)

### D6: Mecanismo de propagación

**Decision**: Integrar en el cascade sync existente de `servicio_contrato_arrendamiento.py`

**Rationale**: El sistema ya tiene un patrón de cascade sync que actualiza Mandatos y Propiedades. Extender este patrón para incluir Liquidaciones y Recaudos es coherente con la arquitectura existente.

**Alternatives considered**:
- Servicio separado de sincronización: Rechazado porque introduciría una nueva capa de complejidad
- Trigger en base de datos: Rechazado porque violaría la Clean Architecture (la lógica debe estar en la capa de Aplicación)

### D7: Criterio de "registros futuros" para Liquidaciones

**Decision**: `LIQUIDACIONES.fecha_generacion::date > fecha_renovacion`

**Rationale**: Las fechas en Liquidaciones son de tipo texto con formato ISO 8601. Se requiere casting a date para comparación precisa.

**Alternatives considered**:
- Comparación de strings: Rechazado porque no es confiable con formato ISO 8601
- Usar `periodo` en lugar de `fecha_generacion`: Rechazado porque `fecha_generacion` es más preciso

### D8: Criterio de "registros futuros" para Recaudos

**Decision**: `RECAUDOS.fecha_pago::date > fecha_renovacion`

**Rationale**: Similar a Liquidaciones, las fechas en Recaudos son de tipo texto y requieren casting.

**Alternatives considered**:
- Comparación de strings: Rechazado por las mismas razones que D7
- Usar estado del recaudo: Rechazado porque la fecha es más precisa

## Research Tasks Completed

1. ✅ Revisar estructura de tabla LIQUIDACIONES (columnas relevantes)
2. ✅ Revisar estructura de tabla RECAUDOS (columnas relevantes)
3. ✅ Analizar cascade sync existente en `servicio_contrato_arrendamiento.py`
4. ✅ Verificar tipos de datos de columnas de fecha
5. ✅ Revisar script de auditoría 062 para patrones de consulta

## Open Questions

- ¿Qué tipos de estados existen en LIQUIDACIONES y RECAUDOS? (pendiente, pagado, anulado, etc.)
- ¿Existen constraints de integridad referencial que puedan afectar las actualizaciones?
- ¿Cuál es el volumen promedio de registros futuros por contrato?
