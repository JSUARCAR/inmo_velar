-- Migration 002: Add valor_incidentes column to LIQUIDACIONES table
-- Feature: 003-integracion-incidentes-liquidaciones
-- Date: 2026-06-30

-- Add valor_incidentes column for tracking incident discounts
-- This represents total discounts applied from incident payments
ALTER TABLE LIQUIDACIONES ADD COLUMN valor_incidentes INTEGER DEFAULT 0;

-- Update existing liquidations to have zero incident value
UPDATE LIQUIDACIONES SET valor_incidentes = 0 WHERE valor_incidentes IS NULL;

-- Add index for filtering by incident value
CREATE INDEX IF NOT EXISTS IDX_LIQUIDACIONES_VALOR_INCIDENTES ON LIQUIDACIONES(valor_incidentes);

-- Note: NETO_A_PAGAR should be recalculated as:
-- NETO_A_PAGAR = TOTAL_INGRESOS - TOTAL_EGRESOS - VALOR_INCIDENTES
-- This will be handled by application layer
