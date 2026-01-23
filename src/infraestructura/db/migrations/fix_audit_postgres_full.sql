-- ============================================================================
-- COMPREHENSIVE AUDIT SYSTEM FOR POSTGRESQL
-- Tracks INSERT, UPDATE, DELETE on ALL tables
-- ============================================================================

-- Drop existing function to recreate
DROP FUNCTION IF EXISTS func_auditoria_cambios() CASCADE;

-- Enhanced audit function with dynamic PK detection
CREATE OR REPLACE FUNCTION func_auditoria_cambios()
RETURNS TRIGGER AS $$
DECLARE
    v_old_data JSONB;
    v_new_data JSONB;
    v_campo TEXT;
    v_old_val TEXT;
    v_new_val TEXT;
    v_usuario TEXT;
    v_id_registro BIGINT;
    v_pk_column TEXT;
BEGIN
    -- Determine PK column dynamically based on table name
    -- This uses a simple pattern: id_{table_name} or id_{table_name_singular}
    SELECT column_name INTO v_pk_column
    FROM information_schema.columns
    WHERE table_name = TG_TABLE_NAME
    AND column_name LIKE 'id_%'
    ORDER BY ordinal_position
    LIMIT 1;
    
    -- If no PK found, use -1 as fallback
    IF v_pk_column IS NULL THEN
        v_id_registro := -1;
    ELSE
        -- Extract ID value dynamically using jsonb
        IF TG_OP = 'DELETE' THEN
            v_id_registro := (to_jsonb(OLD)->>v_pk_column)::BIGINT;
        ELSE
            v_id_registro := (to_jsonb(NEW)->>v_pk_column)::BIGINT;
        END IF;
    END IF;

    -- Determine responsible user
    IF TG_OP = 'DELETE' THEN
        v_usuario := COALESCE(OLD.updated_by, OLD.created_by, 'SISTEMA_DB');
    ELSIF TG_OP = 'INSERT' THEN
        v_usuario := COALESCE(NEW.created_by, 'SISTEMA_DB');
    ELSE -- UPDATE
        v_usuario := COALESCE(NEW.updated_by, NEW.created_by, 'SISTEMA_DB');
    END IF;

    -- Handle different operations
    IF TG_OP = 'DELETE' THEN
        -- Log deletion
        INSERT INTO auditoria_cambios (
            tabla, id_registro, tipo_operacion,
            campo_modificado, valor_anterior, valor_nuevo,
            usuario, fecha_cambio
        ) VALUES (
            TG_TABLE_NAME,
            v_id_registro,
            'DELETE',
            'ALL',
            '(Registro Eliminado)',
            NULL,
            v_usuario,
            NOW()::VARCHAR
        );
        
        RETURN OLD;
        
    ELSIF TG_OP = 'INSERT' THEN
        -- Log creation
        INSERT INTO auditoria_cambios (
            tabla, id_registro, tipo_operacion,
            campo_modificado, valor_anterior, valor_nuevo,
            usuario, fecha_cambio
        ) VALUES (
            TG_TABLE_NAME,
            v_id_registro,
            'INSERT',
            'ALL',
            NULL,
            '(Registro Creado)',
            v_usuario,
            NOW()::VARCHAR
        );
        
        RETURN NEW;
        
    ELSIF TG_OP = 'UPDATE' THEN
        v_old_data := to_jsonb(OLD);
        v_new_data := to_jsonb(NEW);
        
        -- Log each changed field
        FOR v_campo, v_new_val IN SELECT * FROM jsonb_each_text(v_new_data)
        LOOP
            v_old_val := v_old_data->>v_campo;
            
            -- Only log if value changed and not a metadata field
            IF v_old_val IS DISTINCT FROM v_new_val 
               AND v_campo NOT IN ('updated_at', 'updated_by', 'ultimo_acceso', 'fecha_modificacion')
               AND v_campo != v_pk_column -- Don't log PK changes
            THEN
                INSERT INTO auditoria_cambios (
                    tabla, id_registro, tipo_operacion,
                    campo_modificado, valor_anterior, valor_nuevo,
                    usuario, fecha_cambio
                ) VALUES (
                    TG_TABLE_NAME,
                    v_id_registro,
                    'UPDATE',
                    v_campo,
                    v_old_val,
                    v_new_val,
                    v_usuario,
                    NOW()::VARCHAR
                );
            END IF;
        END LOOP;
        
        RETURN NEW;
    END IF;

    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- CREATE TRIGGERS FOR ALL TABLES  
-- ============================================================================

-- Core entities
CREATE TRIGGER trg_audit_usuarios AFTER INSERT OR UPDATE OR DELETE ON usuarios FOR EACH ROW EXECUTE FUNCTION func_auditoria_cambios();
CREATE TRIGGER trg_audit_personas AFTER INSERT OR UPDATE OR DELETE ON personas FOR EACH ROW EXECUTE FUNCTION func_auditoria_cambios();
CREATE TRIGGER trg_audit_propiedades AFTER INSERT OR UPDATE OR DELETE ON propiedades FOR EACH ROW EXECUTE FUNCTION func_auditoria_cambios();

-- Contracts
CREATE TRIGGER trg_audit_contratos_arrendamientos AFTER INSERT OR UPDATE OR DELETE ON contratos_arrendamientos FOR EACH ROW EXECUTE FUNCTION func_auditoria_cambios();
CREATE TRIGGER trg_audit_contratos_mandatos AFTER INSERT OR UPDATE OR DELETE ON contratos_mandatos FOR EACH ROW EXECUTE FUNCTION func_auditoria_cambios();

-- Financial
CREATE TRIGGER trg_audit_recaudos AFTER INSERT OR UPDATE OR DELETE ON recaudos FOR EACH ROW EXECUTE FUNCTION func_auditoria_cambios();
CREATE TRIGGER trg_audit_liquidaciones AFTER INSERT OR UPDATE OR DELETE ON liquidaciones FOR EACH ROW EXECUTE FUNCTION func_auditoria_cambios();
CREATE TRIGGER trg_audit_liquidaciones_asesores AFTER INSERT OR UPDATE OR DELETE ON liquidaciones_asesores FOR EACH ROW EXECUTE FUNCTION func_auditoria_cambios();
CREATE TRIGGER trg_audit_liquidaciones_propietarios AFTER INSERT OR UPDATE OR DELETE ON liquidaciones_propietarios FOR EACH ROW EXECUTE FUNCTION func_auditoria_cambios();
CREATE TRIGGER trg_audit_descuentos_asesores AFTER INSERT OR UPDATE OR DELETE ON descuentos_asesores FOR EACH ROW EXECUTE FUNCTION func_auditoria_cambios();
CREATE TRIGGER trg_audit_bonificaciones_asesores AFTER INSERT OR UPDATE OR DELETE ON bonificaciones_asesores FOR EACH ROW EXECUTE FUNCTION func_auditoria_cambios();
CREATE TRIGGER trg_audit_saldos_favor AFTER INSERT OR UPDATE OR DELETE ON saldos_favor FOR EACH ROW EXECUTE FUNCTION func_auditoria_cambios();
CREATE TRIGGER trg_audit_recibos_publicos AFTER INSERT OR UPDATE OR DELETE ON recibos_publicos FOR EACH ROW EXECUTE FUNCTION func_auditoria_cambios();

-- Operations
CREATE TRIGGER trg_audit_incidentes AFTER INSERT OR UPDATE OR DELETE ON incidentes FOR EACH ROW EXECUTE FUNCTION func_auditoria_cambios();
CREATE TRIGGER trg_audit_historial_incidentes AFTER INSERT OR UPDATE OR DELETE ON historial_incidentes FOR EACH ROW EXECUTE FUNCTION func_auditoria_cambios();
CREATE TRIGGER trg_audit_ordenes_trabajo AFTER INSERT OR UPDATE OR DELETE ON ordenes_trabajo FOR EACH ROW EXECUTE FUNCTION func_auditoria_cambios();
CREATE TRIGGER trg_audit_desocupaciones AFTER INSERT OR UPDATE OR DELETE ON desocupaciones FOR EACH ROW EXECUTE FUNCTION func_auditoria_cambios();

-- Insurance
CREATE TRIGGER trg_audit_polizas AFTER INSERT OR UPDATE OR DELETE ON polizas FOR EACH ROW EXECUTE FUNCTION func_auditoria_cambios();

-- System
CREATE TRIGGER trg_audit_ipc AFTER INSERT OR UPDATE OR DELETE ON ipc FOR EACH ROW EXECUTE FUNCTION func_auditoria_cambios();
CREATE TRIGGER trg_audit_parametros_sistema AFTER INSERT OR UPDATE OR DELETE ON parametros_sistema FOR EACH ROW EXECUTE FUNCTION func_auditoria_cambios();
CREATE TRIGGER trg_audit_alertas AFTER INSERT OR UPDATE OR DELETE ON alertas FOR EACH ROW EXECUTE FUNCTION func_auditoria_cambios();

-- Catalog tables
CREATE TRIGGER trg_audit_municipios AFTER INSERT OR UPDATE OR DELETE ON municipios FOR EACH ROW EXECUTE FUNCTION func_auditoria_cambios();
CREATE TRIGGER trg_audit_departamentos AFTER INSERT OR UPDATE OR DELETE ON departamentos FOR EACH ROW EXECUTE FUNCTION func_auditoria_cambios();

-- ============================================================================
-- Audit triggers created successfully for all tables
