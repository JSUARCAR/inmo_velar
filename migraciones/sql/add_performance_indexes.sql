-- Migration: Add Performance Indexes
-- Description: Adds missing B-Tree indexes on foreign keys and frequently filtered columns to optimize JOINs and WHERE clauses.

-- 1. Optimize Property History Lookups
CREATE INDEX IF NOT EXISTS idx_contratos_arrendamientos_propiedad ON CONTRATOS_ARRENDAMIENTOS(ID_PROPIEDAD);
CREATE INDEX IF NOT EXISTS idx_contratos_mandatos_propiedad ON CONTRATOS_MANDATOS(ID_PROPIEDAD);

-- 2. Optimize Recaudo Status Checks
-- (Already exists idx_recaudo_contrato, but adding state helps filtering active vs paid)
CREATE INDEX IF NOT EXISTS idx_recaudo_contrato_estado ON RECAUDO_ARRENDAMIENTO(ID_CONTRATO_A, ESTADO_RECAUDO);

-- 3. Optimize Liquidations Joins
CREATE INDEX IF NOT EXISTS idx_liquidaciones_liq_contrato ON LIQUIDACIONES_PROPIETARIOS(ID_CONTRATO_M);

-- 4. Optimize Incident Reporting
CREATE INDEX IF NOT EXISTS idx_incidentes_contrato ON INCIDENTES(ID_CONTRATO_M);
