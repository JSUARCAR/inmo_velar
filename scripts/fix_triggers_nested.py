import sqlite3

DB_PATH = "DB_Inmo_Velar.db"

def fix_triggers():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("Corrigiendo triggers de disponibilidad...")
    
    try:
        # 1. Drop existing triggers
        cursor.execute("DROP TRIGGER IF EXISTS TRG_ACTUALIZAR_DISPONIBILIDAD_OCUPADA")
        cursor.execute("DROP TRIGGER IF EXISTS TRG_ACTUALIZAR_DISPONIBILIDAD_LIBRE")
        
        # 2. Recreate TRG_ACTUALIZAR_DISPONIBILIDAD_OCUPADA
        # Ahora actualiza UPDATED_BY usando el CREATED_BY del contrato (quien hizo la operacion)
        trg_ocupada = """
        CREATE TRIGGER TRG_ACTUALIZAR_DISPONIBILIDAD_OCUPADA
        AFTER INSERT ON CONTRATOS_ARRENDAMIENTOS
        WHEN NEW.ESTADO_CONTRATO_A = 'Activo'
        BEGIN
            UPDATE PROPIEDADES 
            SET DISPONIBILIDAD_PROPIEDAD = 0,
                UPDATED_BY = NEW.CREATED_BY,
                UPDATED_AT = datetime('now', 'localtime')
            WHERE ID_PROPIEDAD = NEW.ID_PROPIEDAD;
        END
        """
        cursor.execute(trg_ocupada)
        
        # 3. Recreate TRG_ACTUALIZAR_DISPONIBILIDAD_LIBRE
        # Ahora actualiza UPDATED_BY usando el UPDATED_BY del contrato (quien finalizó/canceló)
        trg_libre = """
        CREATE TRIGGER TRG_ACTUALIZAR_DISPONIBILIDAD_LIBRE
        AFTER UPDATE ON CONTRATOS_ARRENDAMIENTOS
        WHEN NEW.ESTADO_CONTRATO_A IN ('Finalizado', 'Cancelado') 
        AND OLD.ESTADO_CONTRATO_A = 'Activo'
        BEGIN
            UPDATE PROPIEDADES 
            SET DISPONIBILIDAD_PROPIEDAD = 1,
                UPDATED_BY = NEW.UPDATED_BY,
                UPDATED_AT = datetime('now', 'localtime')
            WHERE ID_PROPIEDAD = NEW.ID_PROPIEDAD;
        END
        """
        cursor.execute(trg_libre)
        
        conn.commit()
        print("Triggers corregidos exitosamente.")
        
    except Exception as e:
        conn.rollback()
        print(f"Error corrigiendo triggers: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    fix_triggers()
