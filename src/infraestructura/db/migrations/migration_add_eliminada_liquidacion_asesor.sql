-- Migración: Agregar columna ELIMINADA a LIQUIDACIONES_ASESORES
-- Feature: 038-liquidacion-asesores-actions
-- Fecha: 2026-07-08
-- Descripción: Implementa soft delete para liquidaciones de asesores

ALTER TABLE LIQUIDACIONES_ASESORES 
ADD COLUMN IF NOT EXISTS ELIMINADA BOOLEAN DEFAULT FALSE;

CREATE INDEX IF NOT EXISTS idx_liquidaciones_asesor_eliminada 
ON LIQUIDACIONES_ASESORES(ELIMINADA);
