-- Migration 001: Add estado_pago column to INCIDENTES table
-- Feature: 003-integracion-incidentes-liquidaciones
-- Date: 2026-06-30

-- Add estado_pago column for tracking payment status
-- Values: 'Pendiente', 'Parcialmente Pagado', 'Pagado'
ALTER TABLE INCIDENTES ADD COLUMN estado_pago TEXT DEFAULT 'Pendiente';

-- Update existing incidents to have correct initial status
-- Incidents without active payment plans should be 'Pendiente'
UPDATE INCIDENTES SET estado_pago = 'Pendiente' WHERE estado_pago IS NULL;

-- Add index for filtering by payment status
CREATE INDEX IF NOT EXISTS IDX_INCIDENTES_ESTADO_PAGO ON INCIDENTES(estado_pago);

-- Add composite index for common queries (status + payment status)
CREATE INDEX IF NOT EXISTS IDX_INCIDENTES_ESTADO_PAGO_ESTADO ON INCIDENTES(estado, estado_pago);
