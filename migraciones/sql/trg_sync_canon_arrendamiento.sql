-- Function to sync canon values across Property and Mandate when a Lease canon is updated
-- Part of Elite Protocol - Inmobiliaria Velar

CREATE OR REPLACE FUNCTION fn_sync_canon_arrendamiento()
RETURNS TRIGGER AS $$
BEGIN
    -- Only act if the canon has changed and the lease is active
    IF (OLD.CANON_ARRENDAMIENTO IS DISTINCT FROM NEW.CANON_ARRENDAMIENTO AND NEW.ESTADO_CONTRATO_A = 'Activo') THEN
        
        -- 1. Sync Estimated Lease Canon in PROPIEDADES
        UPDATE PROPIEDADES
        SET CANON_ARRENDAMIENTO_ESTIMADO = NEW.CANON_ARRENDAMIENTO,
            UPDATED_AT = CURRENT_TIMESTAMP,
            UPDATED_BY = NEW.UPDATED_BY
        WHERE ID_PROPIEDAD = NEW.ID_PROPIEDAD;

        -- 2. Sync Mandate Canon in active CONTRATOS_MANDATOS
        UPDATE CONTRATOS_MANDATOS
        SET CANON_MANDATO = NEW.CANON_ARRENDAMIENTO,
            UPDATED_AT = CURRENT_TIMESTAMP,
            UPDATED_BY = NEW.UPDATED_BY
        WHERE ID_PROPIEDAD = NEW.ID_PROPIEDAD
          AND ESTADO_CONTRATO_M = 'Activo';

        -- 3. Log into IPC_INCREMENT_HISTORY for audit purposes
        INSERT INTO IPC_INCREMENT_HISTORY (
            ID_CONTRATO_A,
            FECHA_APLICACION,
            PORCENTAJE_IPC,
            CANON_ANTERIOR,
            CANON_NUEVO,
            OBSERVACIONES,
            CREATED_BY
        ) VALUES (
            NEW.ID_CONTRATO_A,
            CURRENT_DATE,
            0.00, -- 0 because it's a manual adjustment or cascading sync
            OLD.CANON_ARRENDAMIENTO,
            NEW.CANON_ARRENDAMIENTO,
            'Sincronización automática vía Trigger desde actualización de contrato',
            NEW.UPDATED_BY
        );
        
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Drop trigger if exists to ensure idempotency
DROP TRIGGER IF EXISTS trg_sync_canon_arrendamiento ON CONTRATOS_ARRENDAMIENTOS;

-- Create the trigger
CREATE TRIGGER trg_sync_canon_arrendamiento
AFTER UPDATE OF CANON_ARRENDAMIENTO ON CONTRATOS_ARRENDAMIENTOS
FOR EACH ROW
EXECUTE FUNCTION fn_sync_canon_arrendamiento();
