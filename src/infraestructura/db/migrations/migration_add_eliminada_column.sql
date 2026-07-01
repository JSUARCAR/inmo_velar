-- Feature: 002-eliminar-liquidacion
-- Date: 2026-06-30
-- Description: Add ELIMINADA column for soft delete of liquidations

-- Add soft delete column
ALTER TABLE LIQUIDACIONES ADD COLUMN ELIMINADA BOOLEAN DEFAULT FALSE;

-- Add index for query performance (most queries filter by ELIMINADA=FALSE)
CREATE INDEX idx_liquidaciones_eliminada ON LIQUIDACIONES(ELIMINADA);

-- Verify
SELECT COLUMN_NAME, DATA_TYPE, COLUMN_DEFAULT
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_NAME = 'LIQUIDACIONES' AND COLUMN_NAME = 'ELIMINADA';
