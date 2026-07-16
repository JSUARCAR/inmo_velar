-- migraciones/fix_datos_liquidaciones_afectadas.sql
-- Script de migración para reconstruir contratos y descuentos faltantes
-- NOTA: Tras la investigación, se confirmó que NO existen liquidaciones afectadas por el bug de transacción. 
-- El bug generaba una excepción durante la creación, impidiendo el guardado en lugar de guardarlo parcialmente.
-- Las liquidaciones existentes que mostraban "0" contratos en la UI sufrían del bug del INNER JOIN, no de pérdida de datos.

BEGIN;

-- 1. Identificar liquidaciones sin contratos (0 afectadas reales)
CREATE TEMP TABLE liquidaciones_afectadas AS
SELECT la.ID_LIQUIDACION_ASESOR, la.ID_ASESOR, la.PERIODO_LIQUIDACION
FROM LIQUIDACIONES_ASESORES la
LEFT JOIN LIQUIDACIONES_CONTRATOS lc ON la.ID_LIQUIDACION_ASESOR = lc.ID_LIQUIDACION_ASESOR
WHERE lc.ID_CONTRATO_A IS NULL;

-- (Opcional) Reconstruir si existieran (Query inactiva por ser innecesaria, se deja como referencia)
/*
INSERT INTO LIQUIDACIONES_CONTRATOS (ID_LIQUIDACION_ASESOR, ID_CONTRATO_A, CANON_INCLUIDO, COMISION_PORCENTAJE_CONTRATO, COMISION_MONTO_CONTRATO, CREATED_BY)
SELECT a.ID_LIQUIDACION_ASESOR, ca.ID_CONTRATO_A, ca.CANON_ARRENDAMIENTO, cm.COMISION_PORCENTAJE_CONTRATO_M, 
       (ca.CANON_ARRENDAMIENTO * cm.COMISION_PORCENTAJE_CONTRATO_M / 100), 'system_migration'
FROM liquidaciones_afectadas a
JOIN CONTRATOS_ARRENDAMIENTOS ca ON ca.ID_ASESOR = a.ID_ASESOR AND ca.ESTADO_CONTRATO_A = 'ACTIVO'
LEFT JOIN CONTRATOS_MANDATOS cm ON ca.ID_PROPIEDAD = cm.ID_PROPIEDAD AND cm.ESTADO_CONTRATO_M = 'ACTIVO';
*/

-- 2. Reconstruir descuentos (0 afectados reales)
/*
INSERT INTO DESCUENTOS_ASESORES (ID_LIQUIDACION_ASESOR, TIPO_DESCUENTO, DESCRIPCION_DESCUENTO, VALOR_DESCUENTO, CREATED_BY)
SELECT ... 
*/

COMMIT;
