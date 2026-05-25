-- Migration: V20260525_01_drop_business_triggers.sql
-- Elimina los triggers redundantes de BD, ya que la lógica ahora reside en la capa de aplicación.

DROP TRIGGER IF EXISTS TRG_ACTUALIZAR_DISPONIBILIDAD_OCUPADA ON CONTRATOS_ARRENDAMIENTOS;
DROP TRIGGER IF EXISTS TRG_ACTUALIZAR_DISPONIBILIDAD_LIBRE ON CONTRATOS_ARRENDAMIENTOS;
DROP FUNCTION IF EXISTS trg_actualizar_disponibilidad_ocupada();
DROP FUNCTION IF EXISTS trg_actualizar_disponibilidad_libre();
