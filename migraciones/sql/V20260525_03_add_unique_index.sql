-- Migration: V20260525_03_add_unique_index.sql
-- Agrega índice único parcial para asegurar 1 contrato activo por propiedad.

DROP INDEX IF EXISTS uq_contrato_activo_por_propiedad;

CREATE UNIQUE INDEX uq_contrato_activo_por_propiedad
ON CONTRATOS_ARRENDAMIENTOS (ID_PROPIEDAD)
WHERE ESTADO_CONTRATO_A = 'Activo';
