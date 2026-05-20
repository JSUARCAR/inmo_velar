-- Script para eliminar triggers de negocio redundantes
-- Delegamos la sincronización en cascada a la capa de aplicación (Python)
-- Protocolo Élite - Inmobiliaria Velar

DROP TRIGGER IF EXISTS trg_sync_canon_arrendamiento ON CONTRATOS_ARRENDAMIENTOS;
DROP TRIGGER IF EXISTS trg_sync_fechas_mandato ON CONTRATOS_ARRENDAMIENTOS;

-- Opcional: Eliminar las funciones si ya no se usan en otros triggers
-- DROP FUNCTION IF EXISTS fn_sync_canon_arrendamiento();
-- DROP FUNCTION IF EXISTS fn_sync_fechas_mandato();

-- Nota: Los triggers de auditoría (TRG_AUDITORIA_*) permanecen activos.
