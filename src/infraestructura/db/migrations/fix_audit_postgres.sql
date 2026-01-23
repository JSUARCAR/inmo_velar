-- Función genérica de auditoría para PostgreSQL
CREATE OR REPLACE FUNCTION func_auditoria_cambios()
RETURNS TRIGGER AS $$
DECLARE
    v_old_data JSONB;
    v_new_data JSONB;
    v_campo TEXT;
    v_old_val TEXT;
    v_new_val TEXT;
    v_usuario TEXT;
BEGIN
    -- Determinar usuario responsable
    IF (TG_OP = 'DELETE') THEN
        v_usuario := OLD.updated_by; -- O quien sea que podamos rastrear, difícil en DELETE físico sin session var
        -- Si es soft delete, será un UPDATE
    ELSE
        -- En UPDATE/INSERT confiamos en que la app setea updated_by/created_by
        IF TG_OP = 'INSERT' THEN
            v_usuario := NEW.created_by;
        ELSE
            v_usuario := NEW.updated_by;
        END IF;
    END IF;

    -- Fallback si usuario es nulo
    IF v_usuario IS NULL THEN
        v_usuario := 'SISTEMA_DB';
    END IF;

    IF (TG_OP = 'UPDATE') THEN
        v_old_data := to_jsonb(OLD);
        v_new_data := to_jsonb(NEW);
        
        -- Iterar sobre columnas para detectar cambios
        -- Nota: Esto es genérico. Para replicar la lógica específica de campos de triggers_auditoria.py,
        -- podríamos ser más específicos, pero una función genérica es más robusta.
        -- Sin embargo, los triggers originales solo monitoreaban campos ESPECÍFICOS.
        -- Para mantener consistencia con la lógica original, podemos hacer IFs específicos o auditar TODO.
        -- "Expert Level" sugiere auditar todo lo relevante.
        
        FOR v_campo, v_new_val IN SELECT * FROM jsonb_each_text(v_new_data)
        LOOP
            v_old_val := v_old_data->>v_campo;
            
            -- Si el valor cambió (y no es updated_at/updated_by que siempre cambian)
            IF v_old_val IS DISTINCT FROM v_new_val 
               AND v_campo NOT IN ('updated_at', 'updated_by', 'ultimo_acceso') THEN
                
                INSERT INTO AUDITORIA_CAMBIOS (
                    TABLA, ID_REGISTRO, TIPO_OPERACION, 
                    CAMPO_MODIFICADO, VALOR_ANTERIOR, VALOR_NUEVO, 
                    USUARIO, FECHA_CAMBIO
                ) VALUES (
                    TG_TABLE_NAME::TEXT,
                    (CASE 
                        WHEN TG_TABLE_NAME = 'propiedades' THEN OLD.id_propiedad
                        WHEN TG_TABLE_NAME = 'usuarios' THEN OLD.id_usuario
                        WHEN TG_TABLE_NAME = 'personas' THEN OLD.id_persona
                        WHEN TG_TABLE_NAME = 'contratos_arrendamientos' THEN OLD.id_contrato_a
                        ELSE -1 END),
                    TG_OP,
                    v_campo,
                    v_old_val,
                    v_new_val,
                    v_usuario,
                    NOW()::varchar -- La entidad espera string
                );
            END IF;
        END LOOP;
        
        RETURN NEW;
        
    ELSIF (TG_OP = 'INSERT') THEN
        -- Auditar inserción completa? Normalmente solo update se pide explícitamente auditar campos.
        -- Pero podemos registrar "Registro Creado"
        INSERT INTO AUDITORIA_CAMBIOS (
            TABLA, ID_REGISTRO, TIPO_OPERACION, 
            CAMPO_MODIFICADO, VALOR_ANTERIOR, VALOR_NUEVO, 
            USUARIO, FECHA_CAMBIO
        ) VALUES (
            TG_TABLE_NAME::TEXT,
            (CASE 
                WHEN TG_TABLE_NAME = 'propiedades' THEN NEW.id_propiedad
                WHEN TG_TABLE_NAME = 'usuarios' THEN NEW.id_usuario
                WHEN TG_TABLE_NAME = 'personas' THEN NEW.id_persona
                WHEN TG_TABLE_NAME = 'contratos_arrendamientos' THEN NEW.id_contrato_a
                ELSE -1 END),
            TG_OP,
            'ALL',
            NULL,
            '(Registro Creado)',
            v_usuario,
            NOW()::varchar
        );
        RETURN NEW;
    END IF;

    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- Crear Triggers

-- 1. USUARIOS
DROP TRIGGER IF EXISTS trg_audit_usuarios ON USUARIOS;
CREATE TRIGGER trg_audit_usuarios
AFTER INSERT OR UPDATE ON USUARIOS
FOR EACH ROW EXECUTE FUNCTION func_auditoria_cambios();

-- 2. PERSONAS
DROP TRIGGER IF EXISTS trg_audit_personas ON PERSONAS;
CREATE TRIGGER trg_audit_personas
AFTER INSERT OR UPDATE ON PERSONAS
FOR EACH ROW EXECUTE FUNCTION func_auditoria_cambios();

-- 3. PROPIEDADES
DROP TRIGGER IF EXISTS trg_audit_propiedades ON PROPIEDADES;
CREATE TRIGGER trg_audit_propiedades
AFTER INSERT OR UPDATE ON PROPIEDADES
FOR EACH ROW EXECUTE FUNCTION func_auditoria_cambios();

-- 4. CONTRATOS_ARRENDAMIENTOS
DROP TRIGGER IF EXISTS trg_audit_contratos ON CONTRATOS_ARRENDAMIENTOS;
CREATE TRIGGER trg_audit_contratos
AFTER INSERT OR UPDATE ON CONTRATOS_ARRENDAMIENTOS
FOR EACH ROW EXECUTE FUNCTION func_auditoria_cambios();
