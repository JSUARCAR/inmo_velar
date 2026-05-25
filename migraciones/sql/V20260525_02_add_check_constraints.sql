-- Migration: V20260525_02_add_check_constraints.sql
-- Agrega check constraint para asegurar que la disponibilidad sea booleana válida.

ALTER TABLE PROPIEDADES
DROP CONSTRAINT IF EXISTS chk_disponibilidad_valida;

ALTER TABLE PROPIEDADES
ADD CONSTRAINT chk_disponibilidad_valida
CHECK (DISPONIBILIDAD_PROPIEDAD IN (FALSE, TRUE));
