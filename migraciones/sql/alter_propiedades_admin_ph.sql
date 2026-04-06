-- ============================================================
-- Migración: Agregar campos de Administración PH
-- Fecha: 2026-04-06
-- Tabla: PROPIEDADES
-- ============================================================
BEGIN;

-- Fecha de pago de administración (día del mes: 1-28)
ALTER TABLE PROPIEDADES 
ADD COLUMN IF NOT EXISTS FECHA_PAGO_ADMINISTRACION INTEGER 
    CHECK (FECHA_PAGO_ADMINISTRACION BETWEEN 1 AND 28);

-- Link/URL del portal de pago en línea
ALTER TABLE PROPIEDADES 
ADD COLUMN IF NOT EXISTS LINK_PAGO_ADMINISTRACION TEXT;

-- Valor de cuota extraordinaria ordinaria
ALTER TABLE PROPIEDADES 
ADD COLUMN IF NOT EXISTS CUOTA_EXTRA_ORDINARIA NUMERIC(15,2) DEFAULT 0;

COMMIT;

-- Verificación
-- SELECT column_name, data_type FROM information_schema.columns 
-- WHERE table_name = 'PROPIEDADES' 
--   AND column_name IN ('FECHA_PAGO_ADMINISTRACION', 'LINK_PAGO_ADMINISTRACION', 'CUOTA_EXTRA_ORDINARIA');
