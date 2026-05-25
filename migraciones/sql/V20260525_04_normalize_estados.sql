-- Migration: V20260525_04_normalize_estados.sql
-- Normaliza los estados existentes a mayúsculas para coincidir con el Enum EstadoContrato.

UPDATE CONTRATOS_ARRENDAMIENTOS 
SET ESTADO_CONTRATO_A = UPPER(ESTADO_CONTRATO_A);

UPDATE CONTRATOS_MANDATOS
SET ESTADO_CONTRATO_M = UPPER(ESTADO_CONTRATO_M);
