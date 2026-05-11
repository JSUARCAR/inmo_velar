-- Migration: Optimize Personas Filters
-- Description: Adds indexes on role and contract tables to optimize the 'Sin Contrato' filter which uses NOT EXISTS logic.
-- Author: Gemini CLI
-- Date: 2026-05-10

-- 1. Optimize Contract Lookups (Foreign Keys to Roles)
-- Mandatos
CREATE INDEX IF NOT EXISTS idx_cm_propietario ON CONTRATOS_MANDATOS(ID_PROPIETARIO);
CREATE INDEX IF NOT EXISTS idx_cm_asesor ON CONTRATOS_MANDATOS(ID_ASESOR);

-- Arrendamientos
CREATE INDEX IF NOT EXISTS idx_ca_arrendatario ON CONTRATOS_ARRENDAMIENTOS(ID_ARRENDATARIO);
CREATE INDEX IF NOT EXISTS idx_ca_codeudor ON CONTRATOS_ARRENDAMIENTOS(ID_CODEUDOR);

-- 2. Optimize Role -> Persona Mapping
-- (Ensure ID_PERSONA is indexed in all role tables for fast JOINs)
CREATE INDEX IF NOT EXISTS idx_propietarios_persona ON PROPIETARIOS(ID_PERSONA);
CREATE INDEX IF NOT EXISTS idx_arrendatarios_persona ON ARRENDATARIOS(ID_PERSONA);
CREATE INDEX IF NOT EXISTS idx_asesores_persona ON ASESORES(ID_PERSONA);
CREATE INDEX IF NOT EXISTS idx_codeudores_persona ON CODEUDORES(ID_PERSONA);
CREATE INDEX IF NOT EXISTS idx_proveedores_persona ON PROVEEDORES(ID_PERSONA);

-- 3. Additional optimizations for current PersonasState sorting/filtering
CREATE INDEX IF NOT EXISTS idx_personas_doc_nombre ON PERSONAS(NUMERO_DOCUMENTO, NOMBRE_COMPLETO);
CREATE INDEX IF NOT EXISTS idx_personas_estado ON PERSONAS(ESTADO_REGISTRO);
