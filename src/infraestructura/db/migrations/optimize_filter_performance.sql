-- Feature: Optimización de rendimiento de filtros avanzados
-- Date: 2026-07-08
-- Description: Add composite indexes to optimize filter queries across 7 modules
-- Impact: Reduces query execution time for filtered searches

-- =============================================================================
-- LIQUIDACIONES: Optimizar consultas filtradas por contrato y período
-- =============================================================================
-- Uso: Filtros de liquidaciones por ID_CONTRATO_M y PERIODO
-- Beneficio: Elimina full table scans en consultas con filtros de contrato
CREATE INDEX IF NOT EXISTS idx_liquidaciones_contrato_periodo 
ON LIQUIDACIONES (ID_CONTRATO_M, PERIODO, eliminada);

-- =============================================================================
-- RECAUDO_CONCEPTOS: Optimizar JOINs y filtros por período
-- =============================================================================
-- Uso: JOINs频繁 entre RECAUDOS y RECAUDO_CONCEPTOS por ID_RECAUDO y PERIODO
-- Beneficio: Acelera consultas de recaudos y liquidaciones
CREATE INDEX IF NOT EXISTS idx_recaudo_conceptos_recaudo_periodo 
ON RECAUDO_CONCEPTOS (ID_RECAUDO, PERIODO);

-- =============================================================================
-- CONTRATOS_MANDATOS: Optimizar filtro sin_contrato
-- =============================================================================
-- Uso: Filtro "sin contratos activos" en módulo de personas
-- Beneficio: Acelera subconsultas NOT EXISTS/LEFT JOIN para personas sin contratos
CREATE INDEX IF NOT EXISTS idx_contratos_mandatos_propietario_estado 
ON CONTRATOS_MANDATOS (ID_PROPIETARIO, ESTADO_CONTRATO_M);

-- =============================================================================
-- CONTRATOS_ARRENDAMIENTOS: Optimizar filtro sin_contrato
-- =============================================================================
-- Uso: Filtro "sin contratos activos" en módulo de personas
-- Beneficio: Acelera subconsultas NOT EXISTS/LEFT JOIN para personas sin contratos
CREATE INDEX IF NOT EXISTS idx_contratos_arrendamientos_propietario_estado 
ON CONTRATOS_ARRENDAMIENTOS (ID_PROPIETARIO, ESTADO_CONTRATO_A);

-- =============================================================================
-- DOCUMENTOS: Optimizar búsqueda de imágenes por entidad
-- =============================================================================
-- Uso: Búsqueda de imagen principal en módulo de propiedades
-- Beneficio: Acelera subconsulta correlacionada de DOCUMENTOS
-- Nota: Índice parcial solo para registros de imagen (MIME_TYPE LIKE 'image/%')
CREATE INDEX IF NOT EXISTS idx_documentos_entidad_imagen 
ON DOCUMENTOS (ENTIDAD_TIPO, ENTIDAD_ID, ES_VIGENTE) 
WHERE MIME_TYPE LIKE 'image/%';

-- =============================================================================
-- INCIDENTES: Optimizar filtros por prioridad y estado
-- =============================================================================
-- Uso: Filtros de incidentes por PRIORIDAD y ESTADO_INCIDENTE
-- Beneficio: Acelera consultas filtradas en módulo de incidentes
CREATE INDEX IF NOT EXISTS idx_incidentes_prioridad_estado 
ON INCIDENTES (PRIORIDAD, ESTADO_INCIDENTE, FECHA_CREACION);

-- =============================================================================
-- RECAUDOS: Optimizar filtros por estado y fecha
-- =============================================================================
-- Uso: Filtros de recaudos por ESTADO_RECAUDO y FECHA_RECAUDO
-- Beneficio: Acelera consultas filtradas en módulo de recaudos
CREATE INDEX IF NOT EXISTS idx_recaudos_estado_fecha 
ON RECAUDOS (ESTADO_RECAUDO, FECHA_RECAUDO);

-- =============================================================================
-- Verificación de índices creados
-- =============================================================================
SELECT 
    indexname,
    tablename,
    indexdef
FROM pg_indexes 
WHERE tablename IN (
    'LIQUIDACIONES', 
    'RECAUDO_CONCEPTOS', 
    'CONTRATOS_MANDATOS', 
    'CONTRATOS_ARRENDAMIENTOS',
    'DOCUMENTOS',
    'INCIDENTES',
    'RECAUDOS'
)
AND indexname LIKE 'idx_%'
ORDER BY tablename, indexname;
