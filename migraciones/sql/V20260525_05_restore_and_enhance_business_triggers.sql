-- Migration: V20260525_05_restore_and_enhance_business_triggers.sql
-- Restaura y mejora los triggers de negocio para garantizar integridad a nivel de base de datos.
-- Ejecución requerida tras eliminación previa para robustecer la sincronización.

-- ==========================================
-- 1. Trigger de Disponibilidad (Ocupada / Libre)
-- ==========================================
CREATE OR REPLACE FUNCTION fn_actualizar_disponibilidad_arrendamiento()
RETURNS TRIGGER AS $$
BEGIN
    -- Ocupada (Transición hacia ACTIVO)
    IF (TG_OP = 'INSERT' AND NEW.ESTADO_CONTRATO_A = 'ACTIVO') OR
       (TG_OP = 'UPDATE' AND OLD.ESTADO_CONTRATO_A != 'ACTIVO' AND NEW.ESTADO_CONTRATO_A = 'ACTIVO') THEN
        UPDATE PROPIEDADES
        SET DISPONIBILIDAD_PROPIEDAD = FALSE,
            UPDATED_AT = CURRENT_TIMESTAMP,
            UPDATED_BY = NEW.UPDATED_BY
        WHERE ID_PROPIEDAD = NEW.ID_PROPIEDAD;
    END IF;

    -- Libre (Transición desde ACTIVO a FINALIZADO/CANCELADO)
    IF (TG_OP = 'UPDATE' AND OLD.ESTADO_CONTRATO_A = 'ACTIVO' AND NEW.ESTADO_CONTRATO_A IN ('FINALIZADO', 'CANCELADO')) THEN
        UPDATE PROPIEDADES
        SET DISPONIBILIDAD_PROPIEDAD = TRUE,
            UPDATED_AT = CURRENT_TIMESTAMP,
            UPDATED_BY = NEW.UPDATED_BY
        WHERE ID_PROPIEDAD = NEW.ID_PROPIEDAD;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_actualizar_disponibilidad_arrendamiento ON CONTRATOS_ARRENDAMIENTOS;
CREATE TRIGGER trg_actualizar_disponibilidad_arrendamiento
AFTER INSERT OR UPDATE OF ESTADO_CONTRATO_A ON CONTRATOS_ARRENDAMIENTOS
FOR EACH ROW
EXECUTE FUNCTION fn_actualizar_disponibilidad_arrendamiento();


-- ==========================================
-- 2. Trigger de Sincronización de Canon (Propiedad y Mandato)
-- ==========================================
CREATE OR REPLACE FUNCTION fn_sync_canon_arrendamiento()
RETURNS TRIGGER AS $$
BEGIN
    -- Si es INSERT o hubo cambio de canon (UPDATE) y el estado es ACTIVO
    IF (TG_OP = 'INSERT' AND NEW.ESTADO_CONTRATO_A = 'ACTIVO') OR 
       (TG_OP = 'UPDATE' AND OLD.CANON_ARRENDAMIENTO IS DISTINCT FROM NEW.CANON_ARRENDAMIENTO AND NEW.ESTADO_CONTRATO_A = 'ACTIVO') THEN
        
        -- Sincronizar Propiedad
        UPDATE PROPIEDADES
        SET CANON_ARRENDAMIENTO_ESTIMADO = NEW.CANON_ARRENDAMIENTO,
            UPDATED_AT = CURRENT_TIMESTAMP,
            UPDATED_BY = NEW.UPDATED_BY
        WHERE ID_PROPIEDAD = NEW.ID_PROPIEDAD;

        -- Sincronizar Mandato
        UPDATE CONTRATOS_MANDATOS
        SET CANON_MANDATO = NEW.CANON_ARRENDAMIENTO,
            UPDATED_AT = CURRENT_TIMESTAMP,
            UPDATED_BY = NEW.UPDATED_BY
        WHERE ID_PROPIEDAD = NEW.ID_PROPIEDAD
          AND ESTADO_CONTRATO_M = 'ACTIVO';
          
        -- Log si es UPDATE
        IF (TG_OP = 'UPDATE') THEN
            INSERT INTO IPC_INCREMENT_HISTORY (
                ID_CONTRATO_A, FECHA_APLICACION, PORCENTAJE_IPC, CANON_ANTERIOR, CANON_NUEVO, OBSERVACIONES, CREATED_BY
            ) VALUES (
                NEW.ID_CONTRATO_A, CURRENT_DATE, 0.00, OLD.CANON_ARRENDAMIENTO, NEW.CANON_ARRENDAMIENTO,
                'Sincronización automática vía Trigger desde actualización de contrato', NEW.UPDATED_BY
            );
        END IF;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_sync_canon_arrendamiento ON CONTRATOS_ARRENDAMIENTOS;
CREATE TRIGGER trg_sync_canon_arrendamiento
AFTER INSERT OR UPDATE OF CANON_ARRENDAMIENTO, ESTADO_CONTRATO_A ON CONTRATOS_ARRENDAMIENTOS
FOR EACH ROW
EXECUTE FUNCTION fn_sync_canon_arrendamiento();


-- ==========================================
-- 3. Trigger de Sincronización de Fechas y Duración hacia el Mandato
-- ==========================================
CREATE OR REPLACE FUNCTION fn_sync_fechas_mandato()
RETURNS TRIGGER AS $$
DECLARE
    v_dia_inicio INT;
    v_grupo INT;
    v_fecha_pago VARCHAR;
BEGIN
    -- Si es INSERT o hubo cambio en fechas/duración (UPDATE) y el estado es ACTIVO
    IF (TG_OP = 'INSERT' AND NEW.ESTADO_CONTRATO_A = 'ACTIVO') OR
       (TG_OP = 'UPDATE' AND (OLD.FECHA_INICIO_CONTRATO_A IS DISTINCT FROM NEW.FECHA_INICIO_CONTRATO_A OR 
                              OLD.FECHA_FIN_CONTRATO_A IS DISTINCT FROM NEW.FECHA_FIN_CONTRATO_A OR
                              OLD.DURACION_CONTRATO_A IS DISTINCT FROM NEW.DURACION_CONTRATO_A) 
                     AND NEW.ESTADO_CONTRATO_A = 'ACTIVO') THEN
        
        -- Calcular el grupo y día de pago basado en el nuevo esquema de la calculadora de contratos
        v_dia_inicio := EXTRACT(DAY FROM CAST(NEW.FECHA_INICIO_CONTRATO_A AS DATE));
        IF v_dia_inicio BETWEEN 1 AND 10 THEN
            v_grupo := 1;
            v_fecha_pago := '10';
        ELSIF v_dia_inicio BETWEEN 11 AND 20 THEN
            v_grupo := 2;
            v_fecha_pago := '20';
        ELSE
            v_grupo := 3;
            v_fecha_pago := '-1';
        END IF;

        UPDATE CONTRATOS_MANDATOS
        SET FECHA_INICIO_CONTRATO_M = NEW.FECHA_INICIO_CONTRATO_A,
            FECHA_FIN_CONTRATO_M = NEW.FECHA_FIN_CONTRATO_A,
            DURACION_CONTRATO_M = NEW.DURACION_CONTRATO_A,
            GRUPO_OPERATIVO = v_grupo,
            FECHA_PAGO = v_fecha_pago,
            UPDATED_AT = CURRENT_TIMESTAMP,
            UPDATED_BY = NEW.UPDATED_BY
        WHERE ID_PROPIEDAD = NEW.ID_PROPIEDAD
          AND ESTADO_CONTRATO_M = 'ACTIVO';
          
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_sync_fechas_mandato ON CONTRATOS_ARRENDAMIENTOS;
CREATE TRIGGER trg_sync_fechas_mandato
AFTER INSERT OR UPDATE OF FECHA_INICIO_CONTRATO_A, FECHA_FIN_CONTRATO_A, DURACION_CONTRATO_A, ESTADO_CONTRATO_A ON CONTRATOS_ARRENDAMIENTOS
FOR EACH ROW
EXECUTE FUNCTION fn_sync_fechas_mandato();
