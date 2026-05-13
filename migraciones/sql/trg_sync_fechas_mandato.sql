-- Function to sync dates from Lease to Mandate
-- Part of Elite Protocol - Inmobiliaria Velar

CREATE OR REPLACE FUNCTION fn_sync_fechas_mandato()
RETURNS TRIGGER AS $$
BEGIN
    -- Only act if the lease is active
    IF (NEW.ESTADO_CONTRATO_A = 'Activo') THEN
        
        -- Sync Mandate dates in active CONTRATOS_MANDATOS for the same property
        UPDATE CONTRATOS_MANDATOS
        SET FECHA_INICIO_CONTRATO_M = NEW.FECHA_INICIO_CONTRATO_A,
            FECHA_FIN_CONTRATO_M = NEW.FECHA_FIN_CONTRATO_A,
            UPDATED_AT = CURRENT_TIMESTAMP,
            UPDATED_BY = NEW.UPDATED_BY
        WHERE ID_PROPIEDAD = NEW.ID_PROPIEDAD
          AND ESTADO_CONTRATO_M = 'Activo';
        
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Drop trigger if exists to ensure idempotency
DROP TRIGGER IF EXISTS trg_sync_fechas_mandato ON CONTRATOS_ARRENDAMIENTOS;

-- Create the trigger to fire on INSERT and UPDATE of relevant date fields
CREATE TRIGGER trg_sync_fechas_mandato
AFTER INSERT OR UPDATE OF FECHA_INICIO_CONTRATO_A, FECHA_FIN_CONTRATO_A ON CONTRATOS_ARRENDAMIENTOS
FOR EACH ROW
EXECUTE FUNCTION fn_sync_fechas_mandato();
