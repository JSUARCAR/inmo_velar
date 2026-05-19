-- Migración para añadir campos de Ciclo de Pago
-- Se añaden grupo_operativo y dia_pago a contratos de arrendamiento y mandato

-- Contratos de Arrendamiento
ALTER TABLE CONTRATOS_ARRENDAMIENTOS ADD COLUMN IF NOT EXISTS grupo_operativo INTEGER DEFAULT 0;
ALTER TABLE CONTRATOS_ARRENDAMIENTOS ADD COLUMN IF NOT EXISTS dia_pago INTEGER;

-- Contratos de Mandato
ALTER TABLE CONTRATOS_MANDATOS ADD COLUMN IF NOT EXISTS grupo_operativo INTEGER DEFAULT 0;
ALTER TABLE CONTRATOS_MANDATOS ADD COLUMN IF NOT EXISTS dia_pago INTEGER;
