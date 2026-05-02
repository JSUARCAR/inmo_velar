-- =============================================================================
-- Migración: Índices compuestos para Reporte Financiero Consolidado
-- Fecha: 2026-05-02
-- Propósito: Optimizar el query obtener_reporte_consolidado (10 JOINs)
--            reduciendo Seq Scans a Index Scans en las tablas más consultadas.
-- Aplicar en: Railway console o via psql sobre la BD de producción
-- Idempotente: Todos usan IF NOT EXISTS
-- =============================================================================

-- 1. Índice para el JOIN principal y ORDER BY del consolidado
--    Query: LEFT JOIN liquidaciones l ON cm.ID_CONTRATO_M = l.ID_CONTRATO_M
--    ORDER: ORDER BY l.FECHA_PAGO DESC NULLS LAST
CREATE INDEX IF NOT EXISTS idx_liquidaciones_contrato_estado_fecha
    ON liquidaciones (ID_CONTRATO_M, ESTADO_LIQUIDACION, FECHA_PAGO DESC NULLS LAST);

-- 2. Índice parcial para la subquery de recaudos aplicados
--    Query: INNER JOIN (SELECT MAX(FECHA_PAGO) FROM RECAUDOS WHERE ESTADO_RECAUDO = 'Aplicado')
--    El índice parcial (WHERE) filtra solo los registros relevantes → menor tamaño, mayor velocidad
CREATE INDEX IF NOT EXISTS idx_recaudos_contrato_fecha_aplicado
    ON RECAUDOS (ID_CONTRATO_A, FECHA_PAGO DESC)
    WHERE ESTADO_RECAUDO = 'Aplicado';

-- 3. Índice para el JOIN de contratos_mandatos por propiedad y asesor
--    Query: FROM CONTRATOS_MANDATOS cm ... WHERE cm.ID_ASESOR = %s
--    Cubre también el filtro de estado del contrato en el WHERE
CREATE INDEX IF NOT EXISTS idx_cm_propiedad_asesor_estado
    ON CONTRATOS_MANDATOS (ID_PROPIEDAD, ID_ASESOR, ESTADO_CONTRATO_M);

-- =============================================================================
-- Verificación post-aplicación:
-- Ejecutar en Railway console para confirmar que los índices fueron creados:
--
--   SELECT indexname, tablename, indexdef
--   FROM pg_indexes
--   WHERE indexname IN (
--     'idx_liquidaciones_contrato_estado_fecha',
--     'idx_recaudos_contrato_fecha_aplicado',
--     'idx_cm_propiedad_asesor_estado'
--   );
--
-- Para verificar que el consolidado usa Index Scan (no Seq Scan):
--   EXPLAIN (ANALYZE, BUFFERS) 
--   SELECT cm.ID_CONTRATO_M FROM CONTRATOS_MANDATOS cm
--   LEFT JOIN liquidaciones l ON cm.ID_CONTRATO_M = l.ID_CONTRATO_M
--   ORDER BY l.FECHA_PAGO DESC NULLS LAST
--   LIMIT 20;
-- =============================================================================
