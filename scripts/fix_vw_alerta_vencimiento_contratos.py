import sqlite3
import sys
import os

# Get correct database path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB_PATH = os.path.join(BASE_DIR, "DB_Inmo_Velar.db")

def fix_view():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        print("=== Actualizando VW_ALERTA_VENCIMIENTO_CONTRATOS ===")
        
        # Check if CONTRATOS_MANDATOS table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='CONTRATOS_MANDATOS';")
        mandatos_exists = cursor.fetchone() is not None
        print(f"Tabla CONTRATOS_MANDATOS existe: {mandatos_exists}")
        
        # Drop existing view
        cursor.execute("DROP VIEW IF EXISTS VW_ALERTA_VENCIMIENTO_CONTRATOS;")
        print("[OK] Vista anterior eliminada")
        
        # Create new view
        if mandatos_exists:
            # Full view with both contract types
            sql = """
                CREATE VIEW VW_ALERTA_VENCIMIENTO_CONTRATOS AS
                -- Contratos de Arrendamiento
                SELECT 
                    'Arrendamiento' AS TIPO_CONTRATO,
                    ca.ID_CONTRATO_A AS ID_CONTRATO,
                    ca.ID_PROPIEDAD,
                    p.DIRECCION_PROPIEDAD AS DIRECCION,
                    arr_p.NOMBRE_COMPLETO AS INQUILINO_PROPIETARIO,
                    ca.FECHA_FIN_CONTRATO_A AS FECHA_FIN,
                    CAST((julianday(ca.FECHA_FIN_CONTRATO_A) - julianday('now')) AS INTEGER) AS DIAS_RESTANTES
                FROM CONTRATOS_ARRENDAMIENTOS ca
                JOIN PROPIEDADES p ON ca.ID_PROPIEDAD = p.ID_PROPIEDAD
                JOIN ARRENDATARIOS arr ON ca.ID_ARRENDATARIO = arr.ID_ARRENDATARIO
                JOIN PERSONAS arr_p ON arr.ID_PERSONA = arr_p.ID_PERSONA
                WHERE ca.ESTADO_CONTRATO_A = 'Activo'
                AND ca.FECHA_FIN_CONTRATO_A <= date('now', '+90 days')
                
                UNION ALL
                
                -- Contratos de Mandato
                SELECT 
                    'Mandato' AS TIPO_CONTRATO,
                    cm.ID_CONTRATO_M AS ID_CONTRATO,
                    cm.ID_PROPIEDAD,
                    p.DIRECCION_PROPIEDAD AS DIRECCION,
                    prop_p.NOMBRE_COMPLETO AS INQUILINO_PROPIETARIO,
                    cm.FECHA_FIN_CONTRATO_M AS FECHA_FIN,
                    CAST((julianday(cm.FECHA_FIN_CONTRATO_M) - julianday('now')) AS INTEGER) AS DIAS_RESTANTES
                FROM CONTRATOS_MANDATOS cm
                JOIN PROPIEDADES p ON cm.ID_PROPIEDAD = p.ID_PROPIEDAD
                JOIN PROPIETARIOS prop ON cm.ID_PROPIETARIO = prop.ID_PROPIETARIO
                JOIN PERSONAS prop_p ON prop.ID_PERSONA = prop_p.ID_PERSONA
                WHERE cm.ESTADO_CONTRATO_M = 'Activo'
                AND cm.FECHA_FIN_CONTRATO_M <= date('now', '+90 days')
                
                ORDER BY DIAS_RESTANTES ASC;
            """
            print("[INFO] Creando vista con ambos tipos de contratos...")
        else:
            # View with only arrendamiento contracts
            sql = """
                CREATE VIEW VW_ALERTA_VENCIMIENTO_CONTRATOS AS
                -- Solo Contratos de Arrendamiento (CONTRATOS_MANDATOS no existe)
                SELECT 
                    'Arrendamiento' AS TIPO_CONTRATO,
                    ca.ID_CONTRATO_A AS ID_CONTRATO,
                    ca.ID_PROPIEDAD,
                    p.DIRECCION_PROPIEDAD AS DIRECCION,
                    arr_p.NOMBRE_COMPLETO AS INQUILINO_PROPIETARIO,
                    ca.FECHA_FIN_CONTRATO_A AS FECHA_FIN,
                    CAST((julianday(ca.FECHA_FIN_CONTRATO_A) - julianday('now')) AS INTEGER) AS DIAS_RESTANTES
                FROM CONTRATOS_ARRENDAMIENTOS ca
                JOIN PROPIEDADES p ON ca.ID_PROPIEDAD = p.ID_PROPIEDAD
                JOIN ARRENDATARIOS arr ON ca.ID_ARRENDATARIO = arr.ID_ARRENDATARIO
                JOIN PERSONAS arr_p ON arr.ID_PERSONA = arr_p.ID_PERSONA
                WHERE ca.ESTADO_CONTRATO_A = 'Activo'
                AND ca.FECHA_FIN_CONTRATO_A <= date('now', '+90 days')
                
                ORDER BY DIAS_RESTANTES ASC;
            """
            print("[WARN] CONTRATOS_MANDATOS no existe. Creando vista solo con arrendamientos...")
        
        cursor.execute(sql)
        print("[OK] Nueva vista creada")
        
        conn.commit()
        print("[OK] Cambios guardados exitosamente")
        
        # Verificar datos
        print("\n=== Verificando contenido de la vista ===")
        cursor.execute("SELECT * FROM VW_ALERTA_VENCIMIENTO_CONTRATOS;")
        results = cursor.fetchall()
        print(f"Total contratos en vista: {len(results)}\n")
        
        if results:
            print("Contratos encontrados:")
            for row in results:
                tipo = row[0]
                direccion = row[3]
                nombre = row[4]
                fecha_fin = row[5]
                dias = row[6]
                if dias < 0:
                    urgencia = f"[VENCIDO] dias={dias}"
                else:
                    urgencia = f"[VENCE EN {dias} DIAS]"
                print(f"  {urgencia} - {tipo}: {direccion} ({nombre}) - Fecha fin: {fecha_fin}")
        else:
            print("  (No hay contratos proximos a vencer en 90 dias)")
        
        print("\n[OK] Migracion completada exitosamente")
        return True
        
    except Exception as e:
        conn.rollback()
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    success = fix_view()
    sys.exit(0 if success else 1)
