-- scripts/migration_007_triggers_valor_incidentes.sql
-- Feature: 003-integracion-incidentes-liquidaciones
-- Date: 2026-07-02

-- Drop old triggers if they exist
DROP TRIGGER IF EXISTS trg_incidente_liq_insert ON INCIDENTE_LIQUIDACION;
DROP TRIGGER IF EXISTS trg_incidente_liq_delete ON INCIDENTE_LIQUIDACION;
DROP TRIGGER IF EXISTS trg_incidente_liq_actualizar_valor_insert ON INCIDENTE_LIQUIDACION;
DROP TRIGGER IF EXISTS trg_incidente_liq_actualizar_valor_delete ON INCIDENTE_LIQUIDACION;

-- Drop old functions if they exist
DROP FUNCTION IF EXISTS recalcular_valor_incidentes();
DROP FUNCTION IF EXISTS fn_actualizar_valor_incidentes_insert();
DROP FUNCTION IF EXISTS fn_actualizar_valor_incidentes_delete();

-- Función para recalcular valor_incidentes
CREATE OR REPLACE FUNCTION recalcular_valor_incidentes()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE LIQUIDACIONES 
    SET valor_incidentes = (
        SELECT COALESCE(SUM(valor_descuento), 0)
        FROM INCIDENTE_LIQUIDACION
        WHERE id_liquidacion = COALESCE(NEW.id_liquidacion, OLD.id_liquidacion)
    )
    WHERE id_liquidacion = COALESCE(NEW.id_liquidacion, OLD.id_liquidacion);
    
    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;

-- Trigger AFTER INSERT
CREATE TRIGGER trg_incidente_liq_insert
AFTER INSERT ON INCIDENTE_LIQUIDACION
FOR EACH ROW
EXECUTE FUNCTION recalcular_valor_incidentes();

-- Trigger AFTER DELETE
CREATE TRIGGER trg_incidente_liq_delete
AFTER DELETE ON INCIDENTE_LIQUIDACION
FOR EACH ROW
EXECUTE FUNCTION recalcular_valor_incidentes();