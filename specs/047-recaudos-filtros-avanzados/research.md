# Research: Filtros Avanzados Recaudos

**Date**: 2026-07-11

## Decision 1: Fuente de datos para Pago Contrato

**Decision**: El filtro Pago Contrato consulta directamente la columna calculada `COALESCE(NULLIF(ca.FECHA_PAGO, ''), EXTRACT(DAY FROM ca.FECHA_INICIO_CONTRATO_A::DATE)::TEXT)` de `CONTRATOS_ARRENDAMIENTOS`.

**Rationale**: Esta es la misma expresión SQL que alimenta la columna "Pago Contrato" en la tabla principal (repositorio_recaudo.py:587-619). Garantiza consistencia exacta entre la columna y el filtro.

**Alternatives considered**:
- Almacenar el día de pago en una tabla derivada: Rechazado porque introduce redundancia y riesgo de desincronización.
- Calcular en frontend: Rechazado porque la especificación requiere filtrado en backend.

## Decision 2: Multi-select OR para filtros numéricos/categóricos

**Decision**: Implementar multi-select usando `List[str]` en el state y cláusulas `IN (...)` en SQL.

**Rationale**: El patrón actual es single-select con AND. No existe multi-select en ningún módulo. La especificación requiere selección múltiple con OR intra-filtro. La cláusula `IN (...)` es el mecanismo SQL estándar para OR sobre valores discretos.

**Alternatives considered**:
- Múltiples filtros independientes: Rechazado porque complica la UX y el state.
- Array PostgreSQL: Rechazado porque los filtros se construyen como strings en el state de Reflex, no como arrays nativos.

## Decision 3: Fuente de datos para Ciclo Operativo

**Decision**: El filtro Ciclo Operativo consulta `cm.GRUPO_OPERATIVO` desde la subconsulta LATERAL sobre `CONTRATOS_MANDATOS` con `ESTADO_CONTRATO_M = 'ACTIVO'`.

**Rationale**: Esta es la misma lógica que la columna "Ciclo Operativo" existente (feature 045). La fuente oficial es el contrato de mandato activo más reciente de la propiedad.

**Alternatives considered**:
- Consultar directamente LIQUIDACIONES: Rechazado porque la Liquidación de Propietarios puede no existir para todos los recaudos, y el ciclo operativo se resuelve vía el contrato de mandato.
- Duplicar el dato en RECAUDOS: Rechazado porque introduce redundancia y desincronización.

## Decision 4: Carga dinámica de opciones del filtro Ciclo Operativo

**Decision**: Las opciones del filtro se obtienen de una query `SELECT DISTINCT GRUPO_OPERATIVO FROM CONTRATOS_MANDATOS WHERE ESTADO_CONTRATO_M = 'ACTIVO'`.

**Rationale**: Permite que nuevos grupos operativos aparezcan automáticamente sin cambios en el código. Consistente con la especificación FR-006.

**Alternatives considered**:
- Hardcodear ["Grupo 1", "Grupo 2", "Grupo 3", "Grupo 4"]: Rechazado porque la especificación requiere opciones dinámicas.

## Decision 5: Carga dinámica de opciones del filtro Pago Contrato

**Decision**: Las opciones se generan como `["Todos"] + [str(i) for i in range(1, 32)]` (días 1-31).

**Rationale**: El día de pago es un valor numérico entre 1 y 31. Ya existe esta generación en el state actual (`dias_pago_options`). Es una lista finita y acotada que no requiere consulta a base de datos.

**Alternatives considered**:
- Consultar valores distintos existentes en la base: Rechazado porque el filtro debe mostrar todos los días posibles (1-31), no solo los que tienen registros.
