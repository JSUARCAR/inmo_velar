-- Función genérica de auditoría para PostgreSQL - CORREGIDA
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
BEGIN
    -- Determinar usuario responsable
    IF (TG_OP = 'DELETE') THEN
        v_usuario := OLD.updated_by; 
    ELSE
        IF TG_OP = 'INSERT' THEN
            v_usuario := NEW.created_by;
        ELSE
            v_usuario := NEW.updated_by;
        END IF;
    END IF;

    IF v_usuario IS NULL THEN
        v_usuario := 'SISTEMA_DB';
    END IF;
    
    -- Determinar ID de Registro dinámicamente
    -- Usamos TG_TABLE_NAME para saber qué campo leer, pero debemos extraerlo del record correcto (OLD o NEW)
    IF TG_TABLE_NAME = 'propiedades' THEN
        v_id_registro := Coalesce(NEW.id_propiedad, OLD.id_propiedad);
    ELSIF TG_TABLE_NAME = 'usuarios' THEN
        v_id_registro := Coalesce(NEW.id_usuario, OLD.id_usuario);
    ELSIF TG_TABLE_NAME = 'personas' THEN
        v_id_registro := Coalesce(NEW.id_persona, OLD.id_persona);
    ELSIF TG_TABLE_NAME = 'contratos_arrendamientos' THEN
        v_id_registro := Coalesce(NEW.id_contrato_a, OLD.id_contrato_a);
    ELSE
        v_id_registro := -1;
    END IF;

    IF (TG_OP = 'UPDATE') THEN
        v_old_data := to_jsonb(OLD);
        v_new_data := to_jsonb(NEW);
        
        FOR v_campo, v_new_val IN SELECT * FROM jsonb_each_text(v_new_data)
        LOOP
            v_old_val := v_old_data->>v_campo;
            
            IF v_old_val IS DISTINCT FROM v_new_val 
               AND v_campo NOT IN ('updated_at', 'updated_by', 'ultimo_acceso', 'fecha_modificacion') THEN
                
                INSERT INTO AUDITORIA_CAMBIOS (
                    TABLA, ID_REGISTRO, TIPO_OPERACION, 
                    CAMPO_MODIFICADO, VALOR_ANTERIOR, VALOR_NUEVO, 
                    USUARIO, FECHA_CAMBIO
                ) VALUES (
                    TG_TABLE_NAME::TEXT,
                    v_id_registro,
                    TG_OP,
                    v_campo,
                    v_old_val,
                    v_new_val,
                    v_usuario,
                    NOW()::varchar
                );
            END IF;
        END LOOP;
        
        RETURN NEW;
        
    ELSIF (TG_OP = 'INSERT') THEN
        INSERT INTO AUDITORIA_CAMBIOS (
            TABLA, ID_REGISTRO, TIPO_OPERACION, 
            CAMPO_MODIFICADO, VALOR_ANTERIOR, VALOR_NUEVO, 
            USUARIO, FECHA_CAMBIO
        ) VALUES (
            TG_TABLE_NAME::TEXT,
            v_id_registro,
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
